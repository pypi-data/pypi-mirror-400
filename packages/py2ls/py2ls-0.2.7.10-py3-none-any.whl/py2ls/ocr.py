import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from py2ls.ips import (
    strcmp,
    detect_angle,
    str2words, 
    isa
)
from PIL import Image 
import logging
from typing import Union, List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum, auto
import warnings
# Suppress unnecessary warnings
warnings.filterwarnings('ignore')

"""
    Enhanced Optical Character Recognition (OCR) Package
"""

class OCREngine(Enum):
    EASYOCR = auto()
    PADDLEOCR = auto()
    PYTHON_TESSERACT = auto()
    DDDDOCR = auto()
    ZEROX = auto()

@dataclass
class OCRResult:
    text: str
    confidence: float
    bbox: Optional[List[Tuple[int, int]]] = None
    language: Optional[str] = None
    engine: Optional[str] = None

    def __str__(self):
        return f"Text: {self.text} (Confidence: {self.confidence:.2f})"

@dataclass
class OCRConfig:
    languages: List[str] = None
    engine: OCREngine = OCREngine.PADDLEOCR
    threshold: float = 0.1 
    decoder: str = "wordbeamsearch"
    preprocess: Dict = None
    postprocess: Dict = None
    visualization: Dict = None

    def __post_init__(self):
        if self.languages is None:
            self.languages = ["en"]
        if self.preprocess is None:
            self.preprocess = {
                "grayscale": True,
                "threshold": True,
                "rotate": "auto"
            }
        if self.postprocess is None:
            self.postprocess = {
                "spell_check": True,
                "clean": True
            }
        if self.visualization is None:
            self.visualization = {
                "show": True,
                "box_color": (0, 255, 0),
                "text_color": (116, 173, 233),
                "font_size": 8
            }

# Valid language codes
lang_valid = {
    "easyocr": {
        "english": "en",
        "thai": "th",
        "chinese_traditional": "ch_tra",
        "chinese": "ch_sim",
        "japanese": "ja",
        "korean": "ko",
        "tamil": "ta",
        "telugu": "te",
        "kannada": "kn",
        "german": "de",
    },
    "paddleocr": {
        "chinese": "ch",
        "chinese_traditional": "chinese_cht",
        "english": "en",
        "french": "fr",
        "german": "de",
        "korean": "korean",
        "japanese": "japan",
        "russian": "ru",
        "italian": "it",
        "portuguese": "pt",
        "spanish": "es",
        "polish": "pl",
        "dutch": "nl",
        "arabic": "ar",
        "vietnamese": "vi",
        "tamil": "ta",
        "turkish": "tr",
    },
    "pytesseract": {
        "afrikaans": "afr",
        "amharic": "amh",
        "arabic": "ara",
        "assamese": "asm",
        "azerbaijani": "aze",
        "azerbaijani_cyrillic": "aze_cyrl",
        "belarusian": "bel",
        "bengali": "ben",
        "tibetan": "bod",
        "bosnian": "bos",
        "breton": "bre",
        "bulgarian": "bul",
        "catalan": "cat",
        "cebuano": "ceb",
        "czech": "ces",
        "chinese": "chi_sim",
        "chinese_vertical": "chi_sim_vert",
        "chinese_traditional": "chi_tra",
        "chinese_traditional_vertical": "chi_tra_vert",
        "cherokee": "chr",
        "corsican": "cos",
        "welsh": "cym",
        "danish": "dan",
        "danish_fraktur": "dan_frak",
        "german": "deu",
        "german_fraktur": "deu_frak",
        "german_latf": "deu_latf",
        "dhivehi": "div",
        "dzongkha": "dzo",
        "greek": "ell",
        "english": "eng",
        "middle_english": "enm",
        "esperanto": "epo",
        "math_equations": "equ",
        "estonian": "est",
        "basque": "eus",
        "faroese": "fao",
        "persian": "fas",
        "filipino": "fil",
        "finnish": "fin",
        "french": "fra",
        "middle_french": "frm",
        "frisian": "fry",
        "scottish_gaelic": "gla",
        "irish": "gle",
        "galician": "glg",
        "ancient_greek": "grc",
        "gujarati": "guj",
        "haitian_creole": "hat",
        "hebrew": "heb",
        "hindi": "hin",
        "croatian": "hrv",
        "hungarian": "hun",
        "armenian": "hye",
        "inuktitut": "iku",
        "indonesian": "ind",
        "icelandic": "isl",
        "italian": "ita",
        "old_italian": "ita_old",
        "javanese": "jav",
        "japanese": "jpn",
        "japanese_vertical": "jpn_vert",
        "kannada": "kan",
        "georgian": "kat",
        "old_georgian": "kat_old",
        "kazakh": "kaz",
        "khmer": "khm",
        "kyrgyz": "kir",
        "kurdish_kurmanji": "kmr",
        "korean": "kor",
        "korean_vertical": "kor_vert",
        "lao": "lao",
        "latin": "lat",
        "latvian": "lav",
        "lithuanian": "lit",
        "luxembourgish": "ltz",
        "malayalam": "mal",
        "marathi": "mar",
        "macedonian": "mkd",
        "maltese": "mlt",
        "mongolian": "mon",
        "maori": "mri",
        "malay": "msa",
        "burmese": "mya",
        "nepali": "nep",
        "dutch": "nld",
        "norwegian": "nor",
        "occitan": "oci",
        "oriya": "ori",
        "script_detection": "osd",
        "punjabi": "pan",
        "polish": "pol",
        "portuguese": "por",
    },
}

class OCRProcessor:
    def __init__(self, config: OCRConfig = None):
        self.config = config if config else OCRConfig()
        self._initialize_engine()
        
    def _initialize_engine(self):
        """Initialize the selected OCR engine"""
        engine_map = {
            OCREngine.EASYOCR: "easyocr",
            OCREngine.PADDLEOCR: "paddleocr",
            OCREngine.PYTHON_TESSERACT: "pytesseract",
            OCREngine.DDDDOCR: "ddddocr",
            OCREngine.ZEROX: "zerox"
        }
        self.engine_name = engine_map.get(self.config.engine, "paddleocr")
        
    def process_image(self, image_path: Union[str, np.ndarray]) -> List[OCRResult]:
        """Main method to process an image and return OCR results"""
        try:
            # Load and preprocess image
            image = self._load_image(image_path)
            processed_image = self._preprocess_image(image)
            
            # Perform OCR
            results = self._perform_ocr(processed_image)
            
            # Post-process results
            final_results = self._postprocess_results(results)
            
            # Visualize if needed
            if self.config.visualization.get('show', True):
                self._visualize_results(image, final_results)
                
            return final_results
            
        except Exception as e:
            logging.error(f"Error processing image: {str(e)}")
            raise
            
    def _load_image(self, image_path: Union[str, np.ndarray]) -> np.ndarray:
        """Load image from path or numpy array"""
        if isinstance(image_path, str):
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from path: {image_path}")
        elif isinstance(image_path, np.ndarray):
            image = image_path
        else:
            raise ValueError("Input must be either image path or numpy array")
            
        return image
        
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Apply preprocessing steps to the image"""
        return preprocess_img(image, **self.config.preprocess)
        
    def _perform_ocr(self, image: np.ndarray) -> List[OCRResult]:
        """Perform OCR using the selected engine"""
        engine_methods = {
            OCREngine.EASYOCR: self._easyocr_recognize,
            OCREngine.PADDLEOCR: self._paddleocr_recognize,
            OCREngine.PYTHON_TESSERACT: self._pytesseract_recognize,
            OCREngine.DDDDOCR: self._ddddocr_recognize,
            OCREngine.ZEROX: self._zerox_recognize
        }
        
        method = engine_methods.get(self.config.engine)
        if not method:
            raise ValueError(f"Unsupported OCR engine: {self.config.engine}")
            
        return method(image)
        
    def _postprocess_results(self, results: List[OCRResult]) -> List[OCRResult]:
        """Apply post-processing to OCR results"""
        if not self.config.postprocess:
            return results
            
        for result in results:
            if self.config.postprocess.get('spell_check', False):
                result.text = str2words(result.text)
            if self.config.postprocess.get('clean', False):
                result.text = self._clean_text(result.text)
                
        return results
        
    def _visualize_results(self, image: np.ndarray, results: List[OCRResult]):
        """Visualize OCR results on the original image"""
        vis_config = self.config.visualization
        fig, ax = plt.subplots(figsize=(10, 10))
        
        for result in results:
            if result.confidence >= self.config.threshold and result.bbox:
                top_left = tuple(map(int, result.bbox[0]))
                bottom_right = tuple(map(int, result.bbox[2]))
                
                # Draw bounding box
                image = cv2.rectangle(
                    image, 
                    top_left, 
                    bottom_right, 
                    vis_config['box_color'], 
                    2
                )
                
                # Add text
                image = add_text_pil(
                    image,
                    result.text,
                    top_left,
                    font_size=vis_config['font_size'] * 6,
                    color=vis_config['text_color'],
                    bg_color=(133, 203, 245, 100)
                )
        
        # Display the image
        ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        ax.axis("off")
        plt.show()
        
    # Engine-specific recognition methods
    def _easyocr_recognize(self, image: np.ndarray) -> List[OCRResult]:
        """Recognize text using EasyOCR"""
        import easyocr
        
        lang = lang_auto_detect(self.config.languages, "easyocr")
        reader = easyocr.Reader(lang, gpu=self.config.use_gpu)
        detections = reader.readtext(image, decoder=self.config.decoder)
        
        return [
            OCRResult(
                text=text,
                confidence=score,
                bbox=bbox,
                engine="easyocr"
            ) for bbox, text, score in detections
        ]
        
    def _paddleocr_recognize(self, image: np.ndarray) -> List[OCRResult]:
        """Recognize text using PaddleOCR"""
        from paddleocr import PaddleOCR
        
        lang = lang_auto_detect(self.config.languages, "paddleocr")
        ocr = PaddleOCR(
            use_angle_cls=True,
            lang=lang[0],  # PaddleOCR supports one language at a time 
        )
        result = ocr.ocr(image, cls=True)
        
        ocr_results = []
        if result and result[0]:
            for line in result[0]:
                if line:
                    bbox, (text, score) = line
                    ocr_results.append(
                        OCRResult(
                            text=text,
                            confidence=score,
                            bbox=bbox,
                            engine="paddleocr"
                        )
                    )
                    
        return ocr_results
        
    def _pytesseract_recognize(self, image: np.ndarray) -> List[OCRResult]:
        """Recognize text using pytesseract"""
        import pytesseract
        
        lang = lang_auto_detect(self.config.languages, "pytesseract")
        data = pytesseract.image_to_data(
            image,
            lang="+".join(lang),
            output_type=pytesseract.Output.DICT
        )
        
        ocr_results = []
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 0:  # Filter out empty results
                ocr_results.append(
                    OCRResult(
                        text=data['text'][i],
                        confidence=float(data['conf'][i])/100,
                        bbox=(
                            (data['left'][i], data['top'][i]),
                            (data['left'][i] + data['width'][i], data['top'][i]),
                            (data['left'][i] + data['width'][i], data['top'][i] + data['height'][i]),
                            (data['left'][i], data['top'][i] + data['height'][i])
                        ),
                        engine="pytesseract"
                    )
                )
                
        return ocr_results
        
    def _ddddocr_recognize(self, image: np.ndarray) -> List[OCRResult]:
        """Recognize text using ddddocr"""
        import ddddocr
        
        ocr = ddddocr.DdddOcr(det=False, ocr=True)
        image_bytes = convert_image_to_bytes(image)
        text = ocr.classification(image_bytes)
        
        return [
            OCRResult(
                text=text,
                confidence=1.0,  # ddddocr doesn't provide confidence scores
                engine="ddddocr"
            )
        ]
        
    def _zerox_recognize(self, image: np.ndarray) -> List[OCRResult]:
        """Recognize text using pyzerox"""
        from pyzerox import zerox
        
        results = zerox(image)
        return [
            OCRResult(
                text=text,
                confidence=score,
                bbox=bbox,
                engine="zerox"
            ) for bbox, text, score in results
        ]
        
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean text by removing special characters and extra spaces"""
        import re
        text = re.sub(r'[^\w\s]', '', text)
        text = ' '.join(text.split())
        return text

def lang_auto_detect(
    lang: Union[str, List[str]],
    model: str = "easyocr",  # "easyocr" or "pytesseract"
) -> List[str]:
    """Automatically detect and validate language codes for the specified OCR model."""
    models = ["easyocr", "paddleocr", "pytesseract"]
    model = strcmp(model, models)[0]
    res_lang = []
    
    if isinstance(lang, str):
        lang = [lang]
        
    for i in lang:
        res_lang.append(lang_valid[model][strcmp(i, list(lang_valid[model].keys()))[0]])
        
    return res_lang

def determine_src_points(image: np.ndarray) -> np.ndarray:
    """Determine source points for perspective correction."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area and pick the largest one
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    src_points = None

    for contour in contours:
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) == 4:  # We need a quadrilateral
            src_points = np.array(approx, dtype="float32")
            break

    if src_points is not None:
        # Order points in a specific order (top-left, top-right, bottom-right, bottom-left)
        src_points = src_points.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        s = src_points.sum(axis=1)
        diff = np.diff(src_points, axis=1)
        rect[0] = src_points[np.argmin(s)]
        rect[2] = src_points[np.argmax(s)]
        rect[1] = src_points[np.argmin(diff)]
        rect[3] = src_points[np.argmax(diff)]
        src_points = rect
    else:
        # If no rectangle is detected, fallback to a default or user-defined points
        height, width = image.shape[:2]
        src_points = np.array(
            [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
            dtype="float32",
        )
    return src_points

def get_default_camera_matrix(image_shape: Tuple[int, int]) -> Tuple[np.ndarray, np.ndarray]:
    """Generate a default camera matrix for undistortion."""
    height, width = image_shape[:2]
    focal_length = width
    center = (width / 2, height / 2)
    camera_matrix = np.array(
        [[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]],
        dtype="float32",
    )
    dist_coeffs = np.zeros((4, 1))  # Assuming no distortion
    return camera_matrix, dist_coeffs

def correct_perspective(image: np.ndarray, src_points: np.ndarray) -> np.ndarray:
    """Correct perspective distortion in an image."""
    # Define the destination points for the perspective transform
    width, height = 1000, 1000  # Adjust size as needed
    dst_points = np.array(
        [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
        dtype="float32",
    )

    # Calculate the perspective transform matrix
    M = cv2.getPerspectiveTransform(src_points, dst_points)
    # Apply the perspective transform
    corrected_image = cv2.warpPerspective(image, M, (width, height))
    return corrected_image

def detect_text_orientation(image: np.ndarray) -> float:
    """Detect the orientation angle of text in an image."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    if lines is None:
        return 0

    angles = []
    for rho, theta in lines[:, 0]:
        angle = theta * 180 / np.pi
        if angle > 90:
            angle -= 180
        angles.append(angle)

    median_angle = np.median(angles)
    return median_angle

def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """Rotate an image by a given angle."""
    center = (image.shape[1] // 2, image.shape[0] // 2)
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(
        image, rot_mat, (image.shape[1], image.shape[0]), flags=cv2.INTER_LINEAR
    )
    return rotated_image

def correct_skew(image: np.ndarray) -> np.ndarray:
    """Correct skew in an image using contour detection."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    coords = np.column_stack(np.where(gray > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return rotated

def undistort_image(image: np.ndarray, camera_matrix: np.ndarray, dist_coeffs: np.ndarray) -> np.ndarray:
    """Undistort an image using camera calibration parameters."""
    return cv2.undistort(image, camera_matrix, dist_coeffs)

def add_text_pil(
    image: np.ndarray,
    text: str,
    position: Tuple[int, int],
    cvt_cmp: bool = True,
    font_size: int = 12,
    color: Tuple[int, int, int] = (0, 0, 0),
    bg_color: Tuple[int, int, int, int] = (133, 203, 245, 100),
) -> np.ndarray:
    """Add text to an image using PIL for better Unicode support."""
    from PIL import Image, ImageDraw, ImageFont
    
    # Convert the image to PIL format
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).convert("RGBA")
    overlay = Image.new("RGBA", pil_image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        font = ImageFont.truetype(
            "/System/Library/Fonts/Supplemental/Songti.ttc", font_size
        )
    except IOError:
        font = ImageFont.load_default()

    # Calculate text size using textbbox
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Draw background rectangle
    x, y = position
    offset = int(0.1 * text_height)
    adjusted_position = (position[0], position[1] - text_height - offset)

    background_rect = [
        adjusted_position[0],
        adjusted_position[1],
        x + text_width,
        y + text_height,
    ]
    draw.rectangle(background_rect, fill=bg_color)
    
    # Add text to the image
    draw.text(adjusted_position, text, font=font, fill=color)
    
    # Combine images
    if pil_image.mode != "RGBA":
        pil_image = pil_image.convert("RGBA")
    if overlay.mode != "RGBA":
        overlay = overlay.convert("RGBA")
    combined = Image.alpha_composite(pil_image, overlay)
    
    # Convert back to OpenCV format
    return cv2.cvtColor(np.array(combined), cv2.COLOR_RGBA2BGR)

def preprocess_img(
    image: Union[str, np.ndarray],
    grayscale: bool = True,
    threshold: bool = True,
    threshold_method: str = "adaptive",
    rotate: Union[str, float] = "auto",
    skew: bool = False,
    blur: bool = False,
    blur_ksize: Tuple[int, int] = (5, 5),
    morph: bool = True,
    morph_op: str = "open",
    morph_kernel_size: Tuple[int, int] = (3, 3),
    enhance_contrast: bool = True,
    clahe_clip: float = 2.0,
    clahe_grid_size: Tuple[int, int] = (8, 8),
    edge_detection: bool = False,
) -> np.ndarray:
    """
    Preprocess an image for OCR to improve recognition accuracy.
    
    Parameters:
        image: Input image (path, numpy array, or PIL image)
        grayscale: Convert to grayscale
        threshold: Apply thresholding
        threshold_method: 'global' or 'adaptive' thresholding
        rotate: 'auto' to auto-detect angle, or float for manual rotation
        skew: Correct skew
        blur: Apply Gaussian blur
        blur_ksize: Kernel size for blur
        morph: Apply morphological operations
        morph_op: Type of operation ('open', 'close', 'dilate', 'erode')
        morph_kernel_size: Kernel size for morphological operations
        enhance_contrast: Apply CLAHE contrast enhancement
        clahe_clip: Clip limit for CLAHE
        clahe_grid_size: Grid size for CLAHE
        edge_detection: Apply Canny edge detection
        
    Returns:
        Preprocessed image as numpy array
    """
    import PIL.PngImagePlugin
    
    # Convert different input types to numpy array
    if isinstance(image, (PIL.PngImagePlugin.PngImageFile, Image.Image)):
        image = np.array(image)
    if isinstance(image, str):
        image = cv2.imread(image)
    if not isinstance(image, np.ndarray):
        image = np.array(image)
        
    try:
        if image.shape[1] == 4:  # Check if it has an alpha channel
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    except:
        pass

    # Rotate image
    if rotate == "auto":
        angle = detect_angle(image, by="fft")
        img_preprocessed = rotate_image(image, angle)
    elif isinstance(rotate, (int, float)):
        img_preprocessed = rotate_image(image, rotate)
    else:
        img_preprocessed = image

    # Correct skew
    if skew:
        img_preprocessed = correct_skew(img_preprocessed)

    # Convert to grayscale
    if grayscale:
        img_preprocessed = cv2.cvtColor(img_preprocessed, cv2.COLOR_BGR2GRAY)

    # Thresholding
    if threshold:
        if threshold_method == "adaptive":
            img_preprocessed = cv2.adaptiveThreshold(
                img_preprocessed,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2,
            )
        elif threshold_method == "global":
            _, img_preprocessed = cv2.threshold(
                img_preprocessed, 127, 255, cv2.THRESH_BINARY
            )

    # Denoise by Gaussian Blur
    if blur:
        img_preprocessed = cv2.GaussianBlur(img_preprocessed, blur_ksize, 0)

    # Morphological operations
    if morph:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, morph_kernel_size)
        if morph_op == "close":
            img_preprocessed = cv2.morphologyEx(
                img_preprocessed, cv2.MORPH_CLOSE, kernel
            )
        elif morph_op == "open":
            img_preprocessed = cv2.morphologyEx(
                img_preprocessed, cv2.MORPH_OPEN, kernel
            )
        elif morph_op == "dilate":
            img_preprocessed = cv2.dilate(img_preprocessed, kernel)
        elif morph_op == "erode":
            img_preprocessed = cv2.erode(img_preprocessed, kernel)

    # Contrast enhancement
    if enhance_contrast:
        clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=clahe_grid_size)
        img_preprocessed = clahe.apply(img_preprocessed)

    # Edge detection
    if edge_detection:
        img_preprocessed = cv2.Canny(img_preprocessed, 100, 200)

    return img_preprocessed

def convert_image_to_bytes(image: Union[np.ndarray, Image.Image]) -> bytes:
    """Convert a CV2 or numpy image to bytes for OCR engines that require it."""
    import io
    from PIL import Image
    
    # Convert OpenCV image (numpy array) to PIL image
    if isinstance(image, np.ndarray):
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
    # Save PIL image to a byte stream
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def text_postprocess(
    text: Union[str, List[str]],
    spell_check: bool = True,
    clean: bool = True,
    filter: Dict = None,
    pattern: str = None,
    merge: bool = True,
) -> Union[str, List[str]]:
    """
    Post-process OCR results to improve text quality.
    
    Parameters:
        text: Input text or list of texts
        spell_check: Apply spell checking
        clean: Remove special characters
        filter: Dictionary with filtering options (e.g., min_length)
        pattern: Regex pattern to match
        merge: Merge fragments into single string
        
    Returns:
        Processed text or list of texts
    """
    import re
    from spellchecker import SpellChecker
    
    if filter is None:
        filter = {"min_length": 2}
        
    if isinstance(text, str):
        text = [text]

    def correct_spelling(text_list: List[str]) -> List[str]:
        spell = SpellChecker()
        return [spell.correction(word) if spell.correction(word) else word for word in text_list]

    def clean_text(text_list: List[str]) -> List[str]:
        return [re.sub(r"[^\w\s]", "", t) for t in text_list]

    def filter_text(text_list: List[str], min_length: int = 2) -> List[str]:
        return [t for t in text_list if len(t) >= min_length]

    def extract_patterns(text_list: List[str], pattern: str) -> List[str]:
        compiled_pattern = re.compile(pattern)
        return [t for t in text_list if compiled_pattern.search(t)]

    def merge_fragments(text_list: List[str]) -> str:
        return " ".join(text_list)

    results = text
    if spell_check:
        results = correct_spelling(results)
    if clean:
        results = clean_text(results)
    if filter:
        results = filter_text(results, min_length=filter.get("min_length", 2))
    if pattern:
        results = extract_patterns(results, pattern)
    if merge and isinstance(results, list):
        results = merge_fragments(results)

    return results

def save_ocr_results(results: List[OCRResult], dir_save: str):
    fname, output = os.path.splitext(dir_save)
    if output == "txt":
        with open(dir_save, "w", encoding="utf-8") as f:
            for r in results:
                f.write(r.text + "\n")
    
    elif output == "csv":
        import pandas as pd
        df = pd.DataFrame([r.__dict__ for r in results])
        df.to_csv(dir_save, index=False)

    elif output == "xlsx":
        import pandas as pd
        df = pd.DataFrame([r.__dict__ for r in results])
        df.to_excel(dir_save, index=False)

    elif output == "json":
        import json
        with open(dir_save, "w", encoding="utf-8") as f:
            json.dump([r.__dict__ for r in results], f, indent=4)

    elif output == "docx":
        from docx import Document
        doc = Document()
        for r in results:
            doc.add_paragraph(r.text)
        doc.save(dir_save)

def get_text(
    image: Union[str, np.ndarray],
    dir_save:str=None,
    lang: Union[str, List[str]] = ["ch_sim", "en"],
    model: str = "paddleocr",
    thr: float = 0.1,
    gpu: bool = True,
    decoder: str = "wordbeamsearch",
    output: str = "txt",
    preprocess: Dict = None,
    postprocess: Union[bool, Dict] = False,
    show: bool = True,
    ax = None,
    cmap = cv2.COLOR_BGR2RGB,
    font = cv2.FONT_HERSHEY_SIMPLEX,
    fontsize: int = 8,
    figsize: List[int] = [10, 10],
    box_color: Tuple[int, int, int] = (0, 255, 0),
    fontcolor: Tuple[int, int, int] = (116, 173, 233),
    bg_color: Tuple[int, int, int, int] = (133, 203, 245, 100),
    usage: bool = False,
    **kwargs,
) -> Union[List[OCRResult], np.ndarray, Tuple[np.ndarray, List[OCRResult]]]:
    """
    Extract text from an image using specified OCR engine.
    
    This is a convenience wrapper around the OCRProcessor class for backward compatibility.
    For new code, consider using the OCRProcessor class directly.
    """
    # Backward compatibility wrapper
    if usage:
        print("""
        Example usage:
        image_path = 'car_plate.jpg'
        results = get_text(
            image_path,
            lang=["en"],
            gpu=False,
            output="text",
            preprocess={
                "grayscale": True,
                "threshold": True,
                "threshold_method": 'adaptive',
                "blur": True,
                "blur_ksize": (5, 5),
                "morph": True,
                "morph_op": 'close',
                "morph_kernel_size": (3, 3),
                "enhance_contrast": True,
                "clahe_clip": 2.0,
                "clahe_grid_size": (8, 8),
                "edge_detection": False
            }
        )""")
        return

    # Create config from parameters
    engine_map = {
        "easyocr": OCREngine.EASYOCR,
        "paddleocr": OCREngine.PADDLEOCR,
        "pytesseract": OCREngine.PYTHON_TESSERACT,
        "ddddocr": OCREngine.DDDDOCR,
        "zerox": OCREngine.ZEROX
    }
    
    config = OCRConfig(
        languages=lang if isinstance(lang, list) else [lang],
        engine=engine_map.get(model.lower(), OCREngine.PADDLEOCR),
        threshold=thr, 
        decoder=decoder,
        preprocess=preprocess if preprocess else {},
        postprocess=postprocess if isinstance(postprocess, dict) else {"spell_check": postprocess},
        visualization={
            "show": show,
            "box_color": box_color,
            "text_color": fontcolor,
            "font_size": fontsize
        }
    )
    
    # Process image
    processor = OCRProcessor(config)
    results = processor.process_image(image)
    
    # Format output based on requested type
    if dir_save is None:
        if output == "all":
            return results
        elif "text" in output.lower():
            return [r.text for r in results]
        elif "score" in output.lower() or "prob" in output.lower():
            return [r.confidence for r in results]
        elif "box" in output.lower():
            return [r.bbox for r in results if r.bbox]
    else: 
        save_ocr_results(results, dir_save)
        if show:
            print(f"OCR results saved to: {dir_save}")
            return dir_save 

def get_table(
    image: Union[str, np.ndarray],
    dir_save: str = "table_result.xlsx",
    output: str = None,  # 'excel' or 'df'
    layout: bool = True,
    show_log: bool = True,
    use_gpu: bool = False,
):
    """
    Recognize and extract tables using PaddleOCR's PPStructure.

    Parameters:
        image (str | np.ndarray): Path to image or numpy array
        dir_save (str): Path to save Excel output (if output='excel')
        output (str): 'excel' to save as .xlsx, 'df' or 'dataframe' to return pandas DataFrames
        layout (bool): Whether to detect layout blocks
        show_log (bool): Show PaddleOCR logs
        use_gpu (bool): Whether to use GPU for inference

    Returns:
        List of dictionaries (if output='excel') or List of pandas DataFrames (if output='df')
    """
    from paddleocr import PPStructure, save_structure_res
    import cv2
    

    if isinstance(image, str):
        img = cv2.imread(image)
        img_name = os.path.splitext(os.path.basename(image))[0]
    else:
        img = image
        img_name = "table_result"

    table_engine = PPStructure(layout=layout, show_log=show_log, use_gpu=use_gpu)
    result = table_engine(img)
    if output is None:
        output="excel"
    if output.lower() in ["df", "dataframe"]:
        # Convert all table blocks into pandas DataFrames
        dfs = []
        for block in result:
            if block["type"] == "table" and "res" in block:
                table_data = block["res"]["html"]
                try:
                    # Read HTML into DataFrame
                    df = pd.read_html(table_data)[0]
                    dfs.append(df)
                except Exception as e:
                    print(f"[Warning] Could not parse table block: {e}")
        return dfs

    else:
        # Save to Excel file
        save_structure_res(result, os.path.dirname(dir_save), img_name)
        print(
            f"[Info] Table saved to: {os.path.join(os.path.dirname(dir_save), img_name + '.xlsx')}"
        )
        return result
def draw_box(
    image,
    detections=None,
    thr=0.25,
    cmap=cv2.COLOR_BGR2RGB,
    box_color=(0, 255, 0),  # draw_box
    fontcolor=(0, 0, 255),  # draw_box
    fontsize=8,
    show=True,
    ax=None,
    **kwargs,
):

    if ax is None:
        ax = plt.gca()
    if isinstance(image, str):
        image = cv2.imread(image)
    if detections is None:
        detections = get_text(image=image, show=0, output="all", **kwargs)

    for bbox, text, score in detections:
        if score > thr:
            top_left = tuple(map(int, bbox[0]))
            bottom_right = tuple(map(int, bbox[2]))
            image = cv2.rectangle(image, top_left, bottom_right, box_color, 2) 
            image = add_text_pil(
                image, text, top_left, cvt_cmp=cvt_cmp,font_size=fontsize *6, color=fontcolor
            )

    img_cmp = cv2.cvtColor(image, cmap)
    if show:
        ax.imshow(img_cmp)
        ax.axis("off")
        # plt.show()
    return img_cmp

    
#! ===========OCR Backup 250529===========

# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# from py2ls.ips import (
#     strcmp,
#     detect_angle,
#     str2words, 
#     isa
# )
# import logging

# """
#     Optical Character Recognition (OCR)
# """

# # Valid language codes
# lang_valid = {
#     "easyocr": {
#         "english": "en",
#         "thai": "th",
#         "chinese_traditional": "ch_tra",
#         "chinese": "ch_sim",
#         "japanese": "ja",
#         "korean": "ko",
#         "tamil": "ta",
#         "telugu": "te",
#         "kannada": "kn",
#         "german": "de",
#     },
#     "paddleocr": {
#         "chinese": "ch",
#         "chinese_traditional": "chinese_cht",
#         "english": "en",
#         "french": "fr",
#         "german": "de",
#         "korean": "korean",
#         "japanese": "japan",
#         "russian": "ru",
#         "italian": "it",
#         "portuguese": "pt",
#         "spanish": "es",
#         "polish": "pl",
#         "dutch": "nl",
#         "arabic": "ar",
#         "vietnamese": "vi",
#         "tamil": "ta",
#         "turkish": "tr",
#     },
#     "pytesseract": {
#         "afrikaans": "afr",
#         "amharic": "amh",
#         "arabic": "ara",
#         "assamese": "asm",
#         "azerbaijani": "aze",
#         "azerbaijani_cyrillic": "aze_cyrl",
#         "belarusian": "bel",
#         "bengali": "ben",
#         "tibetan": "bod",
#         "bosnian": "bos",
#         "breton": "bre",
#         "bulgarian": "bul",
#         "catalan": "cat",
#         "cebuano": "ceb",
#         "czech": "ces",
#         "chinese": "chi_sim",
#         "chinese_vertical": "chi_sim_vert",
#         "chinese_traditional": "chi_tra",
#         "chinese_traditional_vertical": "chi_tra_vert",
#         "cherokee": "chr",
#         "corsican": "cos",
#         "welsh": "cym",
#         "danish": "dan",
#         "danish_fraktur": "dan_frak",
#         "german": "deu",
#         "german_fraktur": "deu_frak",
#         "german_latf": "deu_latf",
#         "dhivehi": "div",
#         "dzongkha": "dzo",
#         "greek": "ell",
#         "english": "eng",
#         "middle_english": "enm",
#         "esperanto": "epo",
#         "math_equations": "equ",
#         "estonian": "est",
#         "basque": "eus",
#         "faroese": "fao",
#         "persian": "fas",
#         "filipino": "fil",
#         "finnish": "fin",
#         "french": "fra",
#         "middle_french": "frm",
#         "frisian": "fry",
#         "scottish_gaelic": "gla",
#         "irish": "gle",
#         "galician": "glg",
#         "ancient_greek": "grc",
#         "gujarati": "guj",
#         "haitian_creole": "hat",
#         "hebrew": "heb",
#         "hindi": "hin",
#         "croatian": "hrv",
#         "hungarian": "hun",
#         "armenian": "hye",
#         "inuktitut": "iku",
#         "indonesian": "ind",
#         "icelandic": "isl",
#         "italian": "ita",
#         "old_italian": "ita_old",
#         "javanese": "jav",
#         "japanese": "jpn",
#         "japanese_vertical": "jpn_vert",
#         "kannada": "kan",
#         "georgian": "kat",
#         "old_georgian": "kat_old",
#         "kazakh": "kaz",
#         "khmer": "khm",
#         "kyrgyz": "kir",
#         "kurdish_kurmanji": "kmr",
#         "korean": "kor",
#         "korean_vertical": "kor_vert",
#         "lao": "lao",
#         "latin": "lat",
#         "latvian": "lav",
#         "lithuanian": "lit",
#         "luxembourgish": "ltz",
#         "malayalam": "mal",
#         "marathi": "mar",
#         "macedonian": "mkd",
#         "maltese": "mlt",
#         "mongolian": "mon",
#         "maori": "mri",
#         "malay": "msa",
#         "burmese": "mya",
#         "nepali": "nep",
#         "dutch": "nld",
#         "norwegian": "nor",
#         "occitan": "oci",
#         "oriya": "ori",
#         "script_detection": "osd",
#         "punjabi": "pan",
#         "polish": "pol",
#         "portuguese": "por",
#     },
# }


# def lang_auto_detect(
#     lang,
#     model="easyocr",  # "easyocr" or "pytesseract"
# ):
#     models = ["easyocr", "paddleocr", "pytesseract"]
#     model = strcmp(model, models)[0]
#     res_lang = []
#     if isinstance(lang, str):
#         lang = [lang]
#     for i in lang:
#         res_lang.append(lang_valid[model][strcmp(i, list(lang_valid[model].keys()))[0]])
#     return res_lang


# def determine_src_points(image):
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
#     contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     # Sort contours by area and pick the largest one
#     contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
#     src_points = None

#     for contour in contours:
#         epsilon = 0.02 * cv2.arcLength(contour, True)
#         approx = cv2.approxPolyDP(contour, epsilon, True)
#         if len(approx) == 4:  # We need a quadrilateral
#             src_points = np.array(approx, dtype="float32")
#             break

#     if src_points is not None:
#         # Order points in a specific order (top-left, top-right, bottom-right, bottom-left)
#         src_points = src_points.reshape(4, 2)
#         rect = np.zeros((4, 2), dtype="float32")
#         s = src_points.sum(axis=1)
#         diff = np.diff(src_points, axis=1)
#         rect[0] = src_points[np.argmin(s)]
#         rect[2] = src_points[np.argmax(s)]
#         rect[1] = src_points[np.argmin(diff)]
#         rect[3] = src_points[np.argmax(diff)]
#         src_points = rect
#     else:
#         # If no rectangle is detected, fallback to a default or user-defined points
#         height, width = image.shape[:2]
#         src_points = np.array(
#             [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
#             dtype="float32",
#         )
#     return src_points


# def get_default_camera_matrix(image_shape):
#     height, width = image_shape[:2]
#     focal_length = width
#     center = (width / 2, height / 2)
#     camera_matrix = np.array(
#         [[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]],
#         dtype="float32",
#     )
#     dist_coeffs = np.zeros((4, 1))  # Assuming no distortion
#     return camera_matrix, dist_coeffs


# def correct_perspective(image, src_points):
#     # Define the destination points for the perspective transform
#     width, height = 1000, 1000  # Adjust size as needed
#     dst_points = np.array(
#         [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
#         dtype="float32",
#     )

#     # Calculate the perspective transform matrix
#     M = cv2.getPerspectiveTransform(src_points, dst_points)
#     # Apply the perspective transform
#     corrected_image = cv2.warpPerspective(image, M, (width, height))
#     return corrected_image


# def detect_text_orientation(image):
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     edges = cv2.Canny(gray, 50, 150, apertureSize=3)
#     lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

#     if lines is None:
#         return 0

#     angles = []
#     for rho, theta in lines[:, 0]:
#         angle = theta * 180 / np.pi
#         if angle > 90:
#             angle -= 180
#         angles.append(angle)

#     median_angle = np.median(angles)
#     return median_angle


# def rotate_image(image, angle):
#     center = (image.shape[1] // 2, image.shape[0] // 2)
#     rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
#     rotated_image = cv2.warpAffine(
#         image, rot_mat, (image.shape[1], image.shape[0]), flags=cv2.INTER_LINEAR
#     )
#     return rotated_image


# def correct_skew(image):
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     coords = np.column_stack(np.where(gray > 0))
#     angle = cv2.minAreaRect(coords)[-1]
#     if angle < -45:
#         angle = -(90 + angle)
#     else:
#         angle = -angle
#     (h, w) = image.shape[:2]
#     center = (w // 2, h // 2)
#     M = cv2.getRotationMatrix2D(center, angle, 1.0)
#     rotated = cv2.warpAffine(
#         image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
#     )
#     return rotated


# def undistort_image(image, camera_matrix, dist_coeffs):
#     return cv2.undistort(image, camera_matrix, dist_coeffs)


# def add_text_pil(
#     image,
#     text,
#     position,
#     cvt_cmp=True,
#     font_size=12,
#     color=(0, 0, 0),
#     bg_color=(133, 203, 245, 100),
# ):
#     from PIL import Image, ImageDraw, ImageFont
#     # Convert the image to PIL format
#     pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).convert("RGBA")
#     # Define the font (make sure to use a font that supports Chinese characters)
#     overlay = Image.new("RGBA", pil_image.size, (255, 255, 255, 0))
#     # Create a drawing context
#     draw = ImageDraw.Draw(overlay)

#     try:
#         font = ImageFont.truetype(
#             "/System/Library/Fonts/Supplemental/Songti.ttc", font_size
#         )
#     except IOError:
#         font = ImageFont.load_default()

#     # cal top_left position
#     # Measure text size using textbbox
#     text_bbox = draw.textbbox((0, 0), text, font=font)
#     # # 或者只画 text, # Calculate text size
#     # text_width, text_height = draw.textsize(text, font=font)
#     text_width = text_bbox[2] - text_bbox[0]
#     text_height = text_bbox[3] - text_bbox[1]

#     # Draw background rectangle
#     x, y = position
#     # Calculate 5% of the text height for upward adjustment
#     offset = int(
#         0.1 * text_height
#     )  # 这就不再上移动了; # int(0.5 * text_height)  # 上移动 50%

#     # Adjust position to match OpenCV's bottom-left alignment
#     adjusted_position = (position[0], position[1] - text_height - offset)

#     background_rect = [
#         adjusted_position[0],
#         adjusted_position[1],
#         x + text_width,
#         y + text_height,
#     ]
#     draw.rectangle(background_rect, fill=bg_color)
#     # Add text to the image
#     draw.text(adjusted_position, text, font=font, fill=color)
#     # Ensure both images are in RGBA mode for alpha compositing
#     if pil_image.mode != "RGBA":
#         pil_image = pil_image.convert("RGBA")
#     if overlay.mode != "RGBA":
#         overlay = overlay.convert("RGBA")
#     combined = Image.alpha_composite(pil_image, overlay)
#     # Convert the image back to OpenCV format
#     image = cv2.cvtColor(np.array(combined), cv2.COLOR_RGBA2BGR) #if cvt_cmp else np.array(combined)
#     return image


# def preprocess_img(
#     image,
#     grayscale=True,
#     threshold=True,
#     threshold_method="adaptive",
#     rotate="auto",
#     skew=False,
#     blur=False,#True,
#     blur_ksize=(5, 5),
#     morph=True,
#     morph_op="open",
#     morph_kernel_size=(3, 3),
#     enhance_contrast=True,
#     clahe_clip=2.0,
#     clahe_grid_size=(8, 8),
#     edge_detection=False,
# ):
#     """
#     预处理步骤:

#     转换为灰度图像: 如果 grayscale 为 True，将图像转换为灰度图像。
#     二值化处理: 根据 threshold 和 threshold_method 参数，对图像进行二值化处理。
#     降噪处理: 使用高斯模糊对图像进行降噪。
#     形态学处理: 根据 morph_op 参数选择不同的形态学操作（开运算、闭运算、膨胀、腐蚀），用于去除噪声或填补孔洞。
#     对比度增强: 使用 CLAHE 技术增强图像对比度。
#     边缘检测: 如果 edge_detection 为 True，使用 Canny 边缘检测算法。

#     预处理图像以提高 OCR 识别准确性。
#     参数:
#     image: 输入的图像路径或图像数据。
#     grayscale: 是否将图像转换为灰度图像。
#     threshold: 是否对图像进行二值化处理。
#     threshold_method: 二值化方法，可以是 'global' 或 'adaptive'。
#     denoise: 是否对图像进行降噪处理。
#     blur_ksize: 高斯模糊的核大小。
#     morph: 是否进行形态学处理。
#     morph_op: 形态学操作的类型，包括 'open'（开运算）、'close'（闭运算）、'dilate'（膨胀）、'erode'（腐蚀）。
#     morph_kernel_size: 形态学操作的内核大小。
#     enhance_contrast: 是否增强图像对比度。
#     clahe_clip: CLAHE（对比度受限的自适应直方图均衡）的剪裁限制。
#     clahe_grid_size: CLAHE 的网格大小。
#     edge_detection: 是否进行边缘检测。
#     """
#     import PIL.PngImagePlugin
#     if isinstance(image, PIL.PngImagePlugin.PngImageFile):
#         image = np.array(image)
#     if isinstance(image, str):
#         image = cv2.imread(image)
#     if not isinstance(image, np.ndarray):
#         image = np.array(image)
        
#     try:
#         if image.shape[1] == 4:  # Check if it has an alpha channel
#             # Drop the alpha channel (if needed), or handle it as required
#             image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
#         else:
#             # Convert RGB to BGR for OpenCV compatibility
#             image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
#     except:
#         pass

#     # Rotate image
#     if rotate == "auto":
#         angle = detect_angle(image, by="fft")
#         img_preprocessed = rotate_image(image, angle)
#     else:
#         img_preprocessed = image

#     # Correct skew
#     if skew:
#         img_preprocessed = correct_skew(image)

#     # Convert to grayscale
#     if grayscale:
#         img_preprocessed = cv2.cvtColor(img_preprocessed, cv2.COLOR_BGR2GRAY)

#     # Thresholding
#     if threshold:
#         if threshold_method == "adaptive":
#             image = cv2.adaptiveThreshold(
#                 img_preprocessed,
#                 255,
#                 cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#                 cv2.THRESH_BINARY,
#                 11,
#                 2,
#             )
#         elif threshold_method == "global":
#             _, img_preprocessed = cv2.threshold(
#                 img_preprocessed, 127, 255, cv2.THRESH_BINARY
#             )

#     # Denoise by Gaussian Blur
#     if blur:
#         img_preprocessed = cv2.GaussianBlur(img_preprocessed, blur_ksize, 0)

#     # 形态学处理
#     if morph:
#         kernel = cv2.getStructuringElement(cv2.MORPH_RECT, morph_kernel_size)
#         if morph_op == "close":  # 闭运算
#             # 目的： 闭运算用于填补前景物体中的小孔或间隙，同时保留其形状和大小。
#             # 工作原理： 闭运算先进行膨胀，然后进行腐蚀。膨胀步骤填补小孔或间隙，腐蚀步骤恢复较大物体的形状。
#             # 效果：
#             # 填补前景物体中的小孔和间隙。
#             # 平滑较大物体的边缘。
#             # 示例用途： 填补物体中的小孔或间隙。
#             img_preprocessed = cv2.morphologyEx(
#                 img_preprocessed, cv2.MORPH_CLOSE, kernel
#             )
#         elif morph_op == "open":  # 开运算
#             # 目的： 开运算用于去除背景中的小物体或噪声，同时保留较大物体的形状和大小。
#             # 工作原理： 开运算先进行腐蚀，然后进行膨胀。腐蚀步骤去除小规模的噪声，膨胀步骤恢复剩余物体的大小。
#             # 效果：
#             # 去除前景中的小物体。
#             # 平滑较大物体的轮廓。
#             # 示例用途： 去除小噪声或伪影，同时保持较大物体完整。
#             img_preprocessed = cv2.morphologyEx(
#                 img_preprocessed, cv2.MORPH_OPEN, kernel
#             )
#         elif morph_op == "dilate":  # 膨胀
#             # 目的： 膨胀操作在物体边界上添加像素。它可以用来填补物体中的小孔或连接相邻的物体。
#             # 工作原理： 内核在图像上移动，每个位置上的像素值被设置为内核覆盖区域中的最大值。
#             # 效果：
#             # 物体变大。
#             # 填补物体中的小孔或间隙。
#             # 示例用途： 填补物体中的小孔或连接断裂的物体部分。
#             img_preprocessed = cv2.dilate(img_preprocessed, kernel)
#         elif morph_op == "erode":  # 腐蚀
#             # 目的： 腐蚀操作用于去除物体边界上的像素。它可以用来去除小规模的噪声，并将靠近的物体分开。
#             # 工作原理： 内核（结构元素）在图像上移动，每个位置上的像素值被设置为内核覆盖区域中的最小值。
#             # 效果：
#             # 物体变小。
#             # 去除图像中的小白点（在白色前景/黑色背景的图像中）。
#             # 示例用途： 去除二值图像中的小噪声或分离相互接触的物体
#             img_preprocessed = cv2.erode(img_preprocessed, kernel)

#     # 对比度增强
#     if enhance_contrast:
#         clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=clahe_grid_size)
#         img_preprocessed = clahe.apply(img_preprocessed)

#     # 边缘检测
#     if edge_detection:
#         img_preprocessed = cv2.Canny(img_preprocessed, 100, 200)

#     return img_preprocessed

# def convert_image_to_bytes(image):
#     """
#     Convert a CV2 or numpy image to bytes for ddddocr.
#     """
#     import io
#     # Convert OpenCV image (numpy array) to PIL image
#     if isinstance(image, np.ndarray):
#         image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#     # Save PIL image to a byte stream
#     img_byte_arr = io.BytesIO()
#     image.save(img_byte_arr, format='PNG')
#     return img_byte_arr.getvalue()

# def text_postprocess(
#     text,
#     spell_check=True,
#     clean=True,
#     filter=dict(min_length=2),
#     pattern=None,
#     merge=True,
# ):
#     import re
#     from spellchecker import SpellChecker

#     def correct_spelling(text_list):
#         spell = SpellChecker()
#         corrected_text = [spell.candidates(word) for word in text_list]
#         return corrected_text

#     def clean_text(text_list):
#         cleaned_text = [re.sub(r"[^\w\s]", "", text) for text in text_list]
#         return cleaned_text

#     def filter_text(text_list, min_length=2):
#         filtered_text = [text for text in text_list if len(text) >= min_length]
#         return filtered_text

#     def extract_patterns(text_list, pattern):
#         pattern = re.compile(pattern)
#         matched_text = [text for text in text_list if pattern.search(text)]
#         return matched_text

#     def merge_fragments(text_list):
#         merged_text = " ".join(text_list)
#         return merged_text

#     results = text
#     if spell_check:
#         # results = correct_spelling(results)
#         results=str2words(results)
#     if clean:
#         results = clean_text(results)
#     if filter:
#         results = filter_text(
#             results, min_length=postprocess["filter"].get("min_length", 2)
#         )
#     if pattern:
#         results = extract_patterns(results, postprocess["pattern"])
#     if merge:
#         results = merge_fragments(results)


# # https://www.jaided.ai/easyocr/documentation/
# # extract text from an image with EasyOCR
# def get_text(
#     image,
#     lang=["ch_sim", "en"],
#     model="paddleocr",  # "pytesseract","paddleocr","easyocr"
#     thr=0.1, 
#     gpu=True,
#     decoder="wordbeamsearch",  #'greedy', 'beamsearch' and 'wordbeamsearch'(hightly accurate)
#     output="txt",
#     preprocess=None,
#     postprocess=False,# do not check spell
#     show=True,
#     ax=None,
#     cmap=cv2.COLOR_BGR2RGB,  # draw_box
#     font=cv2.FONT_HERSHEY_SIMPLEX,# draw_box
#     fontsize=8,# draw_box
#     figsize=[10,10],
#     box_color = (0, 255, 0), # draw_box
#     fontcolor = (116,173,233), # draw_box
#     bg_color=(133, 203, 245, 100),# draw_box
#     usage=False,
#     **kwargs,
# ):
#     """
#         image: 输入的图像路径或图像数据。
#         lang: OCR 语言列表。
#         thr: 置信度阈值，低于此阈值的检测结果将被过滤。
#         gpu: 是否使用 GPU。
#         output: 输出类型，可以是 'all'（返回所有检测结果）、'text'（返回文本）、'score'（返回置信度分数）、'box'（返回边界框）。
#         preprocess: 预处理参数字典，传递给 preprocess_img 函数。
#         show: 是否显示结果图像。
#         ax: 用于显示图像的 Matplotlib 子图。
#         cmap: 用于显示图像的颜色映射。
#         box_color: 边界框的颜色。
#         fontcolor: 文本的颜色。
#         kwargs: 传递给 EasyOCR readtext 函数的其他参数。 
#     """
#     from PIL import Image
#     if usage:
#         print(
#             """
#         image_path = 'car_plate.jpg'  # 替换为你的图像路径
#         results = get_text(
#             image_path,
#             lang=["en"],
#             gpu=False,
#             output="text",
#             preprocess={
#                 "grayscale": True,
#                 "threshold": True,
#                 "threshold_method": 'adaptive',
#                 "blur": True,
#                 "blur_ksize": (5, 5),
#                 "morph": True,
#                 "morph_op": 'close',
#                 "morph_kernel_size": (3, 3),
#                 "enhance_contrast": True,
#                 "clahe_clip": 2.0,
#                 "clahe_grid_size": (8, 8),
#                 "edge_detection": False
#             },
#             adjust_contrast=0.7
#         )""")

#     models = ["easyocr", "paddleocr", "pytesseract","ddddocr","zerox"]
#     model = strcmp(model, models)[0]
#     lang = lang_auto_detect(lang, model)
#     cvt_cmp=True
#     if isinstance(image, str) and isa(image,'file'):
#         image = cv2.imread(image)
#     elif isa(image,'image'):
#         cvt_cmp=False
#         image = np.array(image)
#     else:
#         raise ValueError(f"not support image with {type(image)} type")

#     # Ensure lang is always a list
#     if isinstance(lang, str):
#         lang = [lang]

#     # ! preprocessing img
#     if preprocess is None:
#         preprocess = {}
#     image_process = preprocess_img(image, **preprocess)
#     plt.figure(figsize=figsize) if show else None
#     # plt.subplot(131)
#     # plt.imshow(cv2.cvtColor(image, cmap))  if cvt_cmp else plt.imshow(image)
#     # plt.subplot(132)
#     # plt.imshow(image_process)
#     # plt.subplot(133)
#     if "easy" in model.lower():
#         import easyocr
#         print(f"detecting language(s):{lang}")
#         # Perform OCR on the image
#         reader = easyocr.Reader(lang, gpu=gpu)
#         detections = reader.readtext(image_process, decoder=decoder, **kwargs)

#         text_corr = []
#         for _, text, _ in detections:
#             text_corr.append(text_postprocess(text) if postprocess else text)

#         if show:
#             if ax is None:
#                 ax = plt.gca()
#             for i, (bbox, text, score) in enumerate(detections):
#                 if score > thr:
#                     top_left = tuple(map(int, bbox[0]))
#                     bottom_right = tuple(map(int, bbox[2]))
#                     image = cv2.rectangle(image, top_left, bottom_right, box_color, 2) 
#                     image = add_text_pil(
#                         image,
#                         text_corr[i],
#                         top_left,
#                         cvt_cmp=cvt_cmp,
#                         font_size=fontsize *6,
#                         color=fontcolor,
#                     )
#             try:
#                 img_cmp = cv2.cvtColor(image, cmap) if cvt_cmp else image
#             except:
#                 img_cmp=image
                
#             ax.imshow(img_cmp) if cvt_cmp else ax.imshow(image)
#             ax.axis("off")

#             if output == "all":
#                 return ax, detections
#             elif "t" in output.lower() and "x" in output.lower():
#                 text = [text_ for _, text_, score_ in detections if score_ >= thr]
#                 if postprocess:
#                     return ax, text
#                 else:
#                     return text_corr
#             elif "score" in output.lower() or "prob" in output.lower():
#                 scores = [score_ for _, _, score_ in detections]
#                 return ax, scores
#             elif "box" in output.lower():
#                 bboxes = [bbox_ for bbox_, _, score_ in detections if score_ >= thr]
#                 return ax, bboxes
#             else:
#                 return ax, detections
#         else:
#             if output == "all":
#                 return detections
#             elif "t" in output.lower() and "x" in output.lower():
#                 text = [text_ for _, text_, score_ in detections if score_ >= thr]
#                 return text
#             elif "score" in output.lower() or "prob" in output.lower():
#                 scores = [score_ for _, _, score_ in detections]
#                 return scores
#             elif "box" in output.lower():
#                 bboxes = [bbox_ for bbox_, _, score_ in detections if score_ >= thr]
#                 return bboxes
#             else:
#                 return detections
#     elif "pad" in model.lower():
#         from paddleocr import PaddleOCR
#         logging.getLogger("ppocr").setLevel(logging.ERROR)
        
#         lang=strcmp(lang, ['ch','en','french','german','korean','japan'])[0]
#         ocr = PaddleOCR(
#             use_angle_cls=True,
#             cls=True,
#             lang=lang
#         )  # PaddleOCR supports only one language at a time
#         cls=kwargs.pop('cls',True)
#         result = ocr.ocr(image_process,cls=cls, **kwargs)
#         detections = []
#         if result[0] is not None:
#             for line in result[0]:
#                 bbox, (text, score) = line
#                 text = str2words(text) if postprocess else text # check spell
#                 detections.append((bbox, text, score))

#         if show:
#             if ax is None:
#                 ax = plt.gca()
#             for bbox, text, score in detections:
#                 if score > thr:
#                     top_left = tuple(map(int, bbox[0]))
#                     bottom_left = tuple(
#                         map(int, bbox[1])
#                     )  # Bottom-left for more accurate placement
#                     bottom_right = tuple(map(int, bbox[2]))
#                     image = cv2.rectangle(image, top_left, bottom_right, box_color, 2)
#                     image = add_text_pil(
#                         image,
#                         text,
#                         top_left,
#                         cvt_cmp=cvt_cmp,
#                         font_size=fontsize *6,
#                         color=fontcolor,
#                         bg_color=bg_color,
#                     )
#             try:
#                 img_cmp = cv2.cvtColor(image, cmap) if cvt_cmp else image
#             except:
#                 img_cmp = image

#             ax.imshow(img_cmp)
#             ax.axis("off")
#             if output == "all":
#                 return ax, detections
#             elif "t" in output.lower() and "x" in output.lower():
#                 text = [text_ for _, text_, score_ in detections if score_ >= thr]
#                 return ax, text
#             elif "score" in output.lower() or "prob" in output.lower():
#                 scores = [score_ for _, _, score_ in detections]
#                 return ax, scores
#             elif "box" in output.lower():
#                 bboxes = [bbox_ for bbox_, _, score_ in detections if score_ >= thr]
#                 return ax, bboxes
#             else:
#                 return ax, detections
#         else:
#             if output == "all":
#                 return detections
#             elif "t" in output.lower() and "x" in output.lower():
#                 text = [text_ for _, text_, score_ in detections if score_ >= thr]
#                 return text
#             elif "score" in output.lower() or "prob" in output.lower():
#                 scores = [score_ for _, _, score_ in detections]
#                 return scores
#             elif "box" in output.lower():
#                 bboxes = [bbox_ for bbox_, _, score_ in detections if score_ >= thr]
#                 return bboxes
#             else:
#                 return detections
#     elif "ddddocr" in  model.lower():
#         import ddddocr 
        
#         ocr = ddddocr.DdddOcr(det=False, ocr=True)
#         image_bytes = convert_image_to_bytes(image_process)

#         results = ocr.classification(image_bytes)  # Text extraction

#         # Optional: Perform detection for bounding boxes
#         detections = []
#         if kwargs.get("det", False):
#             det_ocr = ddddocr.DdddOcr(det=True)
#             det_results = det_ocr.detect(image_bytes)
#             for box in det_results:
#                 top_left = (box[0], box[1])
#                 bottom_right = (box[2], box[3])
#                 detections.append((top_left, bottom_right))

#         if postprocess is None:
#             postprocess = dict(
#                 spell_check=True,
#                 clean=True,
#                 filter=dict(min_length=2),
#                 pattern=None,
#                 merge=True,
#             )
#             text_corr = []
#             [
#                 text_corr.extend(text_postprocess(text, **postprocess))
#                 for _, text, _ in detections
#             ]
#         # Visualization
#         if show:
#             if ax is None:
#                 ax = plt.gca()
#             image_vis = image.copy()
#             if detections:
#                 for top_left, bottom_right in detections:
#                     cv2.rectangle(image_vis, top_left, bottom_right, box_color, 2)
#             image_vis = cv2.cvtColor(image_vis, cmap)
#             ax.imshow(image_vis)
#             ax.axis("off")
#         return detections

#     elif "zerox" in model.lower():
#         from pyzerox import zerox
#         result = zerox(image_process)
#         detections = [(bbox, text, score) for bbox, text, score in result]
#         # Postprocess and visualize
#         if postprocess is None:
#             postprocess = dict(
#                 spell_check=True,
#                 clean=True,
#                 filter=dict(min_length=2),
#                 pattern=None,
#                 merge=True,
#             )
#         text_corr = [text_postprocess(text, **postprocess) for _, text, _ in detections]
        
#         # Display results if 'show' is True
#         if show:
#             if ax is None:
#                 ax = plt.gca()
#             for bbox, text, score in detections:
#                 if score > thr:
#                     top_left = tuple(map(int, bbox[0]))
#                     bottom_right = tuple(map(int, bbox[2]))
#                     image = cv2.rectangle(image, top_left, bottom_right, box_color, 2)
#                     image = add_text_pil(image, text, top_left, cvt_cmp=cvt_cmp,font_size=fontsize *6, color=fontcolor, bg_color=bg_color)
#             ax.imshow(image)
#             ax.axis("off")

#         # Return result based on 'output' type
#         if output == "all":
#             return ax, detections
#         elif "t" in output.lower() and "x" in output.lower():
#             text = [text_ for _, text_, score_ in detections if score_ >= thr]
#             return ax, text
#         elif "score" in output.lower() or "prob" in output.lower():
#             scores = [score_ for _, _, score_ in detections]
#             return ax, scores
#         elif "box" in output.lower():
#             bboxes = [bbox_ for bbox_, _, score_ in detections if score_ >= thr]
#             return ax, bboxes
#         else:
#             return detections
#     else:  # "pytesseract"
#         import pytesseract
#         if ax is None:
#             ax = plt.gca()
#         text = pytesseract.image_to_string(image_process, lang="+".join(lang), **kwargs)
#         bboxes = pytesseract.image_to_boxes(image_process, **kwargs)
#         if show:
#             # Image dimensions
#             h, w, _ = image.shape

#             for line in bboxes.splitlines():
#                 parts = line.split()
#                 if len(parts) == 6:
#                     char, left, bottom, right, top, _ = parts
#                     left, bottom, right, top = map(int, [left, bottom, right, top])

#                     # Convert Tesseract coordinates (bottom-left and top-right) to (top-left and bottom-right)
#                     top_left = (left, h - top)
#                     bottom_right = (right, h - bottom)

#                     # Draw the bounding box
#                     image = cv2.rectangle(image, top_left, bottom_right, box_color, 2)
#                     image = add_text_pil(
#                         image,
#                         char,
#                         left,
#                         cvt_cmp=cvt_cmp,
#                         font_size=fontsize *6,
#                         color=fontcolor,
#                     )
#             img_cmp = cv2.cvtColor(image, cmap)
#             ax.imshow(img_cmp)
#             ax.axis("off")
#             if output == "all":
#                 # Get verbose data including boxes, confidences, line and page numbers
#                 detections = pytesseract.image_to_data(image_process)
#                 return ax, detections
#             elif "t" in output.lower() and "x" in output.lower():
#                 return ax, text
#             elif "box" in output.lower():
#                 return ax, bboxes
#             else:
#                 # Get information about orientation and script detection
#                 return pytesseract.image_to_osd(image_process, **kwargs)
#         else:
#             if output == "all":
#                 # Get verbose data including boxes, confidences, line and page numbers
#                 detections = pytesseract.image_to_data(image_process, **kwargs)
#                 return detections
#             elif "t" in output.lower() and "x" in output.lower():
#                 return text
#             elif "box" in output.lower():
#                 return bboxes
#             else:
#                 # Get information about orientation and script detection
#                 return pytesseract.image_to_osd(image_process, **kwargs)


# def draw_box(
#     image,
#     detections=None,
#     thr=0.25,
#     cmap=cv2.COLOR_BGR2RGB,
#     box_color=(0, 255, 0),  # draw_box
#     fontcolor=(0, 0, 255),  # draw_box
#     fontsize=8,
#     show=True,
#     ax=None,
#     **kwargs,
# ):

#     if ax is None:
#         ax = plt.gca()
#     if isinstance(image, str):
#         image = cv2.imread(image)
#     if detections is None:
#         detections = get_text(image=image, show=0, output="all", **kwargs)

#     for bbox, text, score in detections:
#         if score > thr:
#             top_left = tuple(map(int, bbox[0]))
#             bottom_right = tuple(map(int, bbox[2]))
#             image = cv2.rectangle(image, top_left, bottom_right, box_color, 2) 
#             image = add_text_pil(
#                 image, text, top_left, cvt_cmp=cvt_cmp,font_size=fontsize *6, color=fontcolor
#             )

#     img_cmp = cv2.cvtColor(image, cmap)
#     if show:
#         ax.imshow(img_cmp)
#         ax.axis("off")
#         # plt.show()
#     return img_cmp
