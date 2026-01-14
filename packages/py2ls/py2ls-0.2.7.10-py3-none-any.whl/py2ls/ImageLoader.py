# 250604_204034:
import os
import numpy as np
import pandas as pd
import cv2
import hashlib
import warnings
import functools
from typing import Union, Optional, Dict, Tuple, List
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from tqdm import tqdm
from PIL import Image, UnidentifiedImageError
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import to_categorical 
import logging

"""
-------------------------------------------------------------------------------
Image Preprocessing
    This file provides a comprehensive image preprocessing pipeline with the following key features:
    
Core Functionality:
    Image loading and processing (resizing, normalization, CLAHE enhancement)
    Parallel processing using ThreadPoolExecutor/ProcessPoolExecutor
    Chunk-based processing for memory efficiency
    Caching mechanism to store processed images

Key Components:
    _apply_clahe(): Contrast Limited Adaptive Histogram Equalization
    _process_single_image(): Handles individual image processing
    ImageLoader class: Main preprocessing pipeline

Use Cases:
    When you need to preprocess large image datasets efficiently
    When memory management is important (chunk-based processing)
    When you want to cache preprocessed images for future use
    When you need parallel processing for faster preprocessing

You only need image preprocessing without ML
You're working with very large datasets that need chunking
You want to cache preprocessed images for future use
You need efficient parallel processing of images
Your focus is on image enhancement/normalization
-------------------------------------------------------------------------------
"""
def _apply_clahe(
    img: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: Tuple[int, int] = (8, 8),
) -> np.ndarray:
    """Apply Contrast Limited Adaptive Histogram Equalization (CLAHE).
    
    Input image should be uint8 or float32 scaled 0-1.
    Returns uint8 image after CLAHE.
    """
    if img.dtype != np.uint8:
        img = (img * 255).astype(np.uint8)

    if len(img.shape) == 2 or (len(img.shape) == 3 and img.shape[2] == 1):
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        return clahe.apply(img)
    else:
        lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        l = clahe.apply(l)
        lab = cv2.merge((l, a, b))
        return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

def _process_single_image(
    path: str, target_size: Tuple[int, int], grayscale: bool, scaler: str
) -> Optional[np.ndarray]:
    """Process a single image file with error handling."""
    try:
        with Image.open(path) as img:
            if grayscale:
                img = img.convert("L")
            else:
                img = img.convert("RGB")

            img = img.resize(target_size[::-1])  # PIL uses (width, height)
            img_array = np.array(img)

            if scaler == "normalize":
                img_array = img_array.astype(np.float32) / 255.0
            elif scaler == "standardize":
                img_array = img_array.astype(np.float32)
                mean, std = img_array.mean(), img_array.std()
                img_array = (img_array - mean) / std if std > 0 else (img_array - mean)
            elif scaler == "clahe":
                img_array = _apply_clahe(img_array).astype(np.float32) / 255.0

            return img_array
    except (OSError, UnidentifiedImageError, ValueError, TypeError) as e:
        logging.warning(f"Failed to process image {path}: {e}")
        return None


class ImageLoader:
    """
    A scalable image preprocessing pipeline that can handle datasets of any size
    with efficient memory usage and parallel processing capabilities.

    # Usage:
    preprocessor = ImageLoader(
        target_size=(32, 32),
        chunk_size=2001,  # Process 5,000 images at a time
        cache_dir="./big_dataset_cache",
        backend="threading",
        n_jobs=8, 
        grayscale=True,
    )

    # This will process in chunks and cache results
    result_train = preprocessor.process(
        df_train,
        x_col="path",
        y_col="Label",
        output="df",
        cache=True,
    )
    result_test = preprocessor.process(
        df_train,
        x_col="path",
        y_col="Label",
        output="df",
        cache=True,
    )
    """

    def __init__(
        self,
        target_size: Tuple[int, int] = (128, 128),
        grayscale: bool = False,
        scaler: str = "normalize",
        n_jobs: int = min(8, os.cpu_count()),
        cache_dir: str = "./preprocessing_cache",
        chunk_size: int = 1000,
        backend: str = "threading",
        verbose: bool = True,
    ):
        """
        Initialize the preprocessor with processing parameters.

        Args:
            target_size: Target dimensions (height, width) for resizing
            grayscale: Convert to grayscale if True
            scaler: Preprocessing method ('normalize', 'standardize', 'clahe', 'raw')
            n_jobs: Number of parallel workers
            cache_dir: Directory for caching processed data
            chunk_size: Number of images to process at once
            backend: Parallel processing backend ('threading' or 'multiprocessing')
            verbose: Print progress information
        """
        self.target_size = target_size
        self.grayscale = grayscale
        self.scaler = scaler
        self.n_jobs = min(n_jobs, os.cpu_count() or 1)
        self.cache_dir = cache_dir
        self.chunk_size = chunk_size
        self.backend = backend
        self.verbose = verbose
        str_usage="""
        preprocessor = ImageLoader(
            target_size=(32, 32),
            chunk_size=2001,  # Process 5,000 images at a time
            cache_dir="./big_dataset_cache",
            backend="threading",
            n_jobs=8,
            grayscale=True,
        )

        # This will process in chunks and cache results
        result_train = preprocessor.process(
            df_train,
            x_col="path",
            y_col="Label",
            output="df",
            cache=True,
        )
        result_test = preprocessor.process(
            df_test,
            x_col="path",
            y_col="Label",
            output="df",
            cache=True,
        )
        # Sample the same 1000 rows from the training set
        sampled_train = result_train.sample(100)

        x_train = sampled_train.drop(columns=["label"])
        y_train = sampled_train["label"]

        # Sample 1000 rows from the test set, and align
        sampled_test = result_test.sample(100)

        x_true = sampled_test.drop(columns=["label"])
        y_true = sampled_test["label"]

        # Run prediction
        res_pred_stack = ml2ls.predict(
            x_train=x_train,
            y_train=y_train,
            x_true=x_true,
            y_true=y_true,
            # cls="light",  # or "light", etc.
            voting=False,
        )
        """
        if self.verbose:
            print(str_usage)
        # Create cache directory if needed
        os.makedirs(self.cache_dir, exist_ok=True)

    def _parallel_process(self, paths: List[str]) -> np.ndarray:
        """
        Process images in parallel using the configured backend.

        Args:
            paths: List of image paths to process

        Returns:
            Stacked array of processed images
        """
        # Create a partial function with fixed parameters
        worker = functools.partial(
            _process_single_image,
            target_size=self.target_size,
            grayscale=self.grayscale,
            scaler=self.scaler,
        )

        if self.backend == "threading":
            with ThreadPoolExecutor(max_workers=self.n_jobs) as pool:
                futures = [pool.submit(worker, path) for path in paths]
                results = []
                for future in tqdm(
                    as_completed(futures), total=len(futures), disable=not self.verbose
                ):
                    try:
                        result = future.result()
                        if result is not None:
                            results.append(result)
                    except Exception as e:
                        if self.verbose:
                            warnings.warn(f"Image processing failed: {str(e)}")
        else:
            # Use smaller chunks for multiprocessing to reduce overhead
            chunk_size = max(1, len(paths) // (self.n_jobs * 2))
            with ProcessPoolExecutor(max_workers=self.n_jobs) as pool:
                futures = []
                for i in range(0, len(paths), chunk_size):
                    chunk = paths[i : i + chunk_size]
                    futures.append(pool.submit(self._process_chunk, chunk))

                results = []
                for future in tqdm(
                    as_completed(futures), total=len(futures), disable=not self.verbose
                ):
                    try:
                        chunk_results = future.result()
                        results.extend(chunk_results)
                    except Exception as e:
                        if self.verbose:
                            warnings.warn(f"Chunk processing failed: {str(e)}")

        # Filter out failed images
        valid_results = [res for res in results if res is not None]
        if valid_results:
            # Handle different image dimensions
            try:
                return np.stack(valid_results)
            except ValueError as e:
                if "must have the same shape" in str(e):
                    # Handle variable channel issue
                    return np.array(valid_results, dtype=object)
                raise
        return np.array([])

    def _process_chunk(self, paths: List[str]) -> List[np.ndarray]:
        """Process a chunk of images (used for multiprocessing)."""
        results = []
        for path in paths:
            try:
                img = _process_single_image(
                    path, self.target_size, self.grayscale, self.scaler
                )
                if img is not None:
                    results.append(img)
            except Exception:
                continue
        return results

    def _get_cache_filename(self, data_hash: str) -> str:
        """
        Generate a unique cache filename based on processing parameters.

        Args:
            data_hash: Hash of the input data

        Returns:
            Full path to cache file
        """
        params = {
            "target_size": self.target_size,
            "grayscale": self.grayscale,
            "scaler": self.scaler,
            "chunk_size": self.chunk_size,
        }
        param_hash = hashlib.md5(str(params).encode()).hexdigest()
        return os.path.join(self.cache_dir, f"img_cache_{data_hash}_{param_hash}.npz")

    @staticmethod
    def _load_from_cache(cache_file: str) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Load processed data from cache.

        Args:
            cache_file: Path to cache file

        Returns:
            Tuple of (images, labels) or None if cache is invalid
        """
        try:
            with np.load(cache_file) as data:
                return data["images"], data["labels"]
        except Exception:
            return None

    @staticmethod
    def _save_to_cache(cache_file: str, images: np.ndarray, labels: np.ndarray):
        """
        Save processed data to cache.

        Args:
            cache_file: Path to cache file
            images: Processed images array
            labels: Corresponding labels array
        """
        np.savez_compressed(cache_file, images=images, labels=labels)

    def _process_labels(
        self,
        data: pd.DataFrame,
        y_col: Optional[str],
        encoder: str,
        label_encoder: Optional[LabelEncoder] = None,
    ) -> Optional[np.ndarray]:
        """
        Process and encode labels according to specified method.

        Args:
            data: Input DataFrame
            y_col: Name of column containing labels
            encoder: Encoding method ('label', 'onehot', 'binary', None)
            label_encoder: Pre-fitted LabelEncoder (optional)

        Returns:
            Array of processed labels or None
        """
        if y_col is None or encoder is None:
            return None

        labels = data[y_col].values

        if encoder == "binary":
            unique_labels = np.unique(labels)
            if len(unique_labels) != 2:
                raise ValueError("Binary encoding requires exactly 2 classes")
            return (labels == unique_labels[0]).astype(int)
        elif encoder == "onehot":
            if label_encoder is None:
                label_encoder = LabelEncoder()
                labels = label_encoder.fit_transform(labels)
            else:
                labels = label_encoder.transform(labels)
            return to_categorical(labels)
        elif encoder == "label":
            if label_encoder is None:
                label_encoder = LabelEncoder()
                labels = label_encoder.fit_transform(labels)
            else:
                labels = label_encoder.transform(labels)
            return labels

        return labels

    def _format_output(
        self, images: np.ndarray, labels: Optional[np.ndarray], output: str
    ) -> Union[ImageDataGenerator, Tuple[np.ndarray, np.ndarray], pd.DataFrame]:
        """
        Format the processed data according to requested output type.

        Args:
            images: Processed images array
            labels: Processed labels array
            output: Requested output type ('generator', 'array', 'dataframe')

        Returns:
            Processed data in requested format
        """
        if output == "generator":
            # Create a memory-efficient generator
            def generator():
                for i in range(0, len(images), self.chunk_size):
                    batch_images = images[i : i + self.chunk_size]
                    batch_labels = (
                        labels[i : i + self.chunk_size] if labels is not None else None
                    )
                    yield (
                        (batch_images, batch_labels)
                        if batch_labels is not None
                        else batch_images
                    )

            return generator()
        elif output == "array":
            return (images, labels) if labels is not None else images
        else:  # dataframe
            # Handle variable image dimensions
            if images.dtype == object:
                # Convert to uniform array
                images = np.array([img for img in images], dtype=np.float32)
            if len(images) == 0:
                warnings.warn("No images to process; returning empty DataFrame.")
                return pd.DataFrame()
            # Ensure image dimensions are known
            if images.ndim == 4:
                n, h, w, c = images.shape
            elif images.ndim == 3:
                n, h, w = images.shape
                c = 1
                images = images.reshape(n, h, w, c)
            else:
                print(f"image type: {type(images)}")
                print(f"image shape: {images.shape}")
                print(f"image dtype: {images.dtype}")
                raise ValueError(f"Unexpected image shape: {images.shape}")

            # Flatten image data
            images_flat = images.reshape(len(images), -1)

            # Create column names based on channels
            if c == 3:
                col_names = (
                    [f"pixel_{i}_r" for i in range(h * w)] +
                    [f"pixel_{i}_g" for i in range(h * w)] +
                    [f"pixel_{i}_b" for i in range(h * w)]
                )
            elif c == 1:
                col_names = [f"pixel_{i}" for i in range(h * w)]
            else:
                # fallback
                col_names = [f"pixel_{i}" for i in range(images_flat.shape[1])]

            # Create DataFrame
            df = pd.DataFrame(images_flat, columns=col_names)

            # Append labels if present
            if labels is not None:
                df["label"] = labels
            print(f"dataframe shape: {df.shape}")
            return df 

    def process(
        self,
        data: pd.DataFrame,
        x_col: str,
        y_col: Optional[str] = None,
        encoder: str = "label",
        label_encoder: Optional[LabelEncoder] = None,
        output: str = "dataframe",
        cache: bool = True,
        max_samples: Optional[int] = None,
        **kwargs,
    ) -> Union[ImageDataGenerator, Tuple[np.ndarray, np.ndarray], pd.DataFrame]:
        """
        Main processing method that handles the entire pipeline.

        Args:
            data: Input DataFrame containing image paths and labels
            x_col: Name of column containing image paths
            y_col: Name of column containing labels (optional)
            encoder: Label encoding method ('label', 'onehot', 'binary', None)
            label_encoder: Pre-fitted LabelEncoder (optional)
            output: Requested output format ('generator', 'array', 'dataframe')
            cache: Whether to use disk caching
            max_samples: Maximum number of samples to process
            kwargs: Additional arguments for processing

        Returns:
            Processed data in requested format
        """
        # Validate inputs
        if x_col not in data.columns:
            raise ValueError(f"Column '{x_col}' not found in DataFrame")

        if y_col is not None and y_col not in data.columns:
            raise ValueError(f"Column '{y_col}' not found in DataFrame")

        # Limit samples if requested
        if max_samples is not None:
            data = data.iloc[:max_samples]

        # Generate data hash for caching
        data_hash = hashlib.md5(pd.util.hash_pandas_object(data).values).hexdigest()
        cache_file = self._get_cache_filename(data_hash) if cache else None

        # Try loading from cache
        if cache and cache_file and os.path.exists(cache_file):
            if self.verbose:
                print("Loading from cache...")
            cached_data = self._load_from_cache(cache_file)
            if cached_data is not None:
                images, labels = cached_data
                return self._format_output(images, labels, output)

        # Process labels first
        labels = self._process_labels(data, y_col, encoder, label_encoder)

        # Process images in chunks if dataset is large
        total_images = len(data)
        use_chunking = total_images > self.chunk_size * 2

        if use_chunking and self.verbose:
            print(f"Processing {total_images} images in chunks of {self.chunk_size}...")

        # Process all images at once if not chunking
        if not use_chunking:
            images = self._parallel_process(data[x_col].values)
        else:
            # Process images chunk by chunk
            images = []
            for i in tqdm(
                range(0, total_images, self.chunk_size), disable=not self.verbose
            ):
                chunk_paths = data[x_col].iloc[i : i + self.chunk_size].values
                chunk_images = self._parallel_process(chunk_paths)
                if len(chunk_images) > 0:
                    images.append(chunk_images)

            # Handle empty chunks
            if images:
                try:
                    images = np.concatenate(images)
                except ValueError:
                    # Handle case with no images processed
                    images = np.array([])
            else:
                images = np.array([])

        # Align labels with successfully processed images
        if labels is not None and len(images) > 0:
            labels = labels[: len(images)]

        # Save to cache if requested
        if cache and cache_file and len(images) > 0:
            self._save_to_cache(cache_file, images, labels)

        return self._format_output(images, labels, output)


def create_augmentation_generator(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    target_size: Tuple[int, int] = (224, 224),
    batch_size: int = 32,
    class_mode: str = "raw",
    augment_params: Optional[Dict] = None,
    grayscale: bool = False,
    shuffle: bool = True,
    seed: Optional[int] = None,
) -> ImageDataGenerator:
    """
    Create an augmented image data generator for training.

    Args:
        data: Input DataFrame
        x_col: Column with image paths
        y_col: Column with labels
        target_size: Target image dimensions
        batch_size: Images per batch
        class_mode: Type of label output
        augment_params: Dictionary of augmentation parameters
        grayscale: Convert to grayscale
        shuffle: Shuffle the data
        seed: Random seed

    Returns:
        Configured ImageDataGenerator
    """
    default_augment = {
        "rotation_range": 20,
        "width_shift_range": 0.1,
        "height_shift_range": 0.1,
        "shear_range": 0.1,
        "zoom_range": 0.1,
        "horizontal_flip": True,
        "vertical_flip": False,
        "brightness_range": [0.9, 1.1],
        "fill_mode": "reflect",
    }

    if augment_params:
        default_augment.update(augment_params)

    datagen = ImageDataGenerator(**default_augment)

    return datagen.flow_from_dataframe(
        dataframe=data,
        x_col=x_col,
        y_col=y_col,
        target_size=target_size,
        color_mode="grayscale" if grayscale else "rgb",
        class_mode=class_mode,
        batch_size=batch_size,
        shuffle=shuffle,
        seed=seed,
    )