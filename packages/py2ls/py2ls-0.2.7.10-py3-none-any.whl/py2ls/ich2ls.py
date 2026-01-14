 #  用来处理ich图像的初级工具包

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Union, Tuple, List, Dict, Optional
from PIL import Image
from skimage import (filters, morphology, measure, color, 
                     segmentation, exposure, util)
from skimage.filters import threshold_multiotsu
from scipy import ndimage as ndi
import warnings
from .ips import color2rgb
# Suppress specific warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

def open_img(
    img_path: str, 
    convert: str = "gray", 
    plot: bool = False,
    figsize: Tuple[int, int] = (10, 5)
) -> Tuple[Image.Image, np.ndarray]:
    """
    Enhanced image loading with better conversion options and visualization
    
    Args:
        img_path: Path to image file
        convert: Conversion mode ('gray', 'rgb', 'hed', 'hsv')
        plot: Whether to show comparison plot
        figsize: Size of comparison plot
        
    Returns:
        Tuple of (PIL Image, numpy array)
    """
    # Load image with validation
    try:
        img = Image.open(img_path)
    except Exception as e:
        raise ValueError(f"Failed to load image: {str(e)}")
    
    # Enhanced conversion options
    if convert.lower() in ["gray", "grey"]:
        img_array = np.array(img.convert("L"))
    elif convert.lower() == "rgb":
        img_array = np.array(img.convert("RGB"))
    elif convert.lower() == "hed":
        img_array = color.rgb2hed(np.array(img.convert("RGB")))
    elif convert.lower() == "hsv":
        img_array = color.rgb2hsv(np.array(img.convert("RGB")))
    else:
        img_array = np.array(img)
    
    # Visualization
    if plot:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        ax1.imshow(img)
        ax1.set_title("Original Image")
        ax1.axis('off')
        
        ax2.imshow(img_array, cmap='gray' if convert.lower() in ["gray", "grey"] else None)
        ax2.set_title(f"Converted ({convert.upper()})")
        ax2.axis('off')
        plt.tight_layout()
        plt.show()
    
    return img, img_array


def clean_img(
    img: np.ndarray,
    methods: Union[str, List[str]] = "all",
    obj_min: int = 50,
    hole_min: int = 50,
    threshold_range: Optional[Tuple[float, float]] = None,
    plot: bool = False,
    cmap: str = "gray",
    figsize: Tuple[int, int] = (8, 8),
    **kwargs
) -> np.ndarray:
    """
    Advanced image cleaning with multiple processing methods
    
    Args:
        img: Input image array
        methods: Processing methods ('threshold', 'objects', 'holes', 'all')
        obj_min: Minimum object size (pixels)
        hole_min: Minimum hole size (pixels)
        threshold_range: Manual threshold range [min, max]
        plot: Whether to show result
        cmap: Colormap for plotting
        figsize: Figure size for plotting
        
    Returns:
        Cleaned binary image
    """
    # Process methods argument
    if isinstance(methods, str):
        methods = ["threshold", "objects", "holes"] if methods == "all" else [methods]
    
    img_clean = img.copy()
    
    # Apply thresholding
    if any(m in methods for m in ["threshold", "thr", "otsu"]):
        if threshold_range:
            # Manual threshold range
            img_clean = np.logical_and(img >= threshold_range[0], img <= threshold_range[1])
        else:
            try:
                # Try multi-Otsu first for better thresholding
                thresholds = threshold_multiotsu(img)
                img_clean = img > thresholds[0]
            except ValueError:
                # Fallback to regular Otsu
                thr = filters.threshold_otsu(img)
                img_clean = img > thr
    
    # Morphological operations
    if any(m in methods for m in ["objects", "obj"]):
        img_clean = morphology.remove_small_objects(img_clean, min_size=obj_min)
    
    if any(m in methods for m in ["holes", "hole"]):
        img_clean = morphology.remove_small_holes(img_clean, area_threshold=hole_min)
    
    # Optional additional processing
    if kwargs.get("denoise", False):
        img_clean = filters.median(img_clean)
    
    if kwargs.get("close", False):
        img_clean = morphology.binary_closing(img_clean)
    
    # Visualization
    if plot:
        plt.figure(figsize=figsize)
        plt.imshow(img_clean, cmap=cmap)
        plt.title("Cleaned Image")
        plt.axis('off')
        plt.show()
    
    return img_clean


def segment_img(
    img: np.ndarray,
    method: str = "watershed",
    min_size: int = 50,
    plot: bool = False,
    cmap: str = "jet",
    connectivity: int = 1,
    output: str = "segmentation",
    **kwargs
) -> Union[np.ndarray, Dict[str, np.ndarray]]:
    """
    Advanced image segmentation with multiple algorithms
    
    Args:
        img: Input image
        method: Segmentation method ('watershed', 'edge', 'threshold')
        min_size: Minimum region size
        plot: Whether to show results
        cmap: Colormap for visualization
        connectivity: Pixel connectivity for watershed
        output: Output type ('segmentation', 'all', 'edges', 'markers')
        
    Returns:
        Segmented image or dictionary of intermediate results
    """
    results = {}
    
    if method.lower() in ["watershed", "region", "watershed"]:
        # Enhanced watershed segmentation
        elevation_map = filters.sobel(img)
        
        # Adaptive marker generation
        if kwargs.get("adaptive_markers", True):
            # Use histogram peaks for better marker placement
            hist, bins = np.histogram(img, bins=256)
            peaks = np.argsort(hist)[-2:]  # Get two highest peaks
            markers = np.zeros_like(img)
            markers[img < bins[peaks[0]]] = 1
            markers[img > bins[peaks[1]]] = 2
        else:
            # Simple threshold-based markers
            markers = np.zeros_like(img)
            markers[img < np.percentile(img, 25)] = 1
            markers[img > np.percentile(img, 75)] = 2
        
        # Apply watershed
        segmentation_result = segmentation.watershed(
            elevation_map, 
            markers=markers, 
            connectivity=connectivity
        )
        
        # Clean up small regions
        segmentation_result = morphology.remove_small_objects(
            segmentation_result, 
            min_size=min_size
        )
        
        results = {
            "elevation": elevation_map,
            "markers": markers,
            "segmentation": segmentation_result
        }
        
    elif method.lower() in ["edge", "edges"]:
        # Edge-based segmentation
        edges = filters.sobel(img) > 0.1
        filled = ndi.binary_fill_holes(edges)
        segmentation_result = morphology.remove_small_objects(filled, min_size=min_size)
        
        results = {
            "edges": edges,
            "filled": filled,
            "segmentation": segmentation_result
        }
    
    elif method.lower() in ["threshold", "thr"]:
        # Threshold-based segmentation
        if "threshold_range" in kwargs:
            low, high = kwargs["threshold_range"]
            segmentation_result = np.logical_and(img >= low, img <= high)
        else:
            try:
                thresholds = threshold_multiotsu(img)
                segmentation_result = np.digitize(img, bins=thresholds)
            except ValueError:
                threshold = filters.threshold_otsu(img)
                segmentation_result = img > threshold
        
        results = {
            "segmentation": segmentation_result
        }
    
    # Visualization
    if plot:
        n_results = len(results)
        fig, axes = plt.subplots(1, n_results + 1, figsize=((n_results + 1) * 5, 5))
        
        axes[0].imshow(img, cmap='gray')
        axes[0].set_title("Original")
        axes[0].axis('off')
        
        for i, (name, result) in enumerate(results.items(), 1):
            axes[i].imshow(result, cmap=cmap)
            axes[i].set_title(name.capitalize())
            axes[i].axis('off')
        
        plt.tight_layout()
        plt.show()
    
    # Return requested output
    if output == "all":
        return results
    elif output in results:
        return results[output]
    else:
        return results["segmentation"]


def label_img(
    img: np.ndarray,
    plot: bool = False,
    cmap: str = "nipy_spectral",
    min_size: int = 20,
    **kwargs
) -> np.ndarray:
    """
    Enhanced connected component labeling
    
    Args:
        img: Binary input image
        plot: Whether to visualize results
        cmap: Colormap for labels
        min_size: Minimum region size
        
    Returns:
        Labeled image
    """
    # Clean image first
    img_clean = clean_img(
        img,
        methods=["objects", "holes"],
        obj_min=min_size,
        hole_min=min_size
    )
    
    # Label connected components
    labels = measure.label(img_clean)
    
    # Visualization
    if plot:
        plt.figure(figsize=(10, 5))
        plt.imshow(labels, cmap=cmap)
        plt.title("Labeled Regions")
        plt.colorbar()
        plt.axis('off')
        plt.show()
    
    return labels


def img_process(
    img: Union[str, np.ndarray],
    convert: str = "gray",
    clean_methods: Union[str, List[str]] = "all",
    clean_params: Optional[Dict] = None,
    segment_method: str = "watershed",
    segment_params: Optional[Dict] = None,
    label_params: Optional[Dict] = None,
    plot: bool = True,
    figsize: Tuple[int, int] = (15, 10),
    return_all: bool = False
) -> Dict[str, Union[np.ndarray, pd.DataFrame]]:
    """
    Complete image processing pipeline with enhanced functionality
    
    Args:
        img: Input image path or array
        convert: Color conversion mode
        clean_methods: Cleaning methods
        clean_params: Parameters for cleaning
        segment_method: Segmentation method
        segment_params: Parameters for segmentation
        label_params: Parameters for labeling
        plot: Whether to show processing steps
        figsize: Figure size for plots
        return_all: Whether to return all intermediate results
        
    Returns:
        Dictionary containing processed images and region properties
    """
    # Initialize parameters
    clean_params = clean_params or {}
    segment_params = segment_params or {}
    label_params = label_params or {}
    
    # Load image if path is provided
    if isinstance(img, str):
        pil_img, img_array = open_img(img, convert=convert, plot=plot)
    else:
        pil_img = None
        img_array = img
    
    # Normalize image
    img_norm = exposure.rescale_intensity(img_array)
    
    # Clean image
    img_clean = clean_img(
        img_norm,
        methods=clean_methods,
        plot=plot,
        **clean_params
    )
    
    # Segment image
    seg_results = segment_img(
        img_clean,
        method=segment_method,
        plot=plot,
        **segment_params
    )
    
    # Get segmentation result (handle case where multiple outputs are returned)
    if isinstance(seg_results, dict):
        img_seg = seg_results["segmentation"]
    else:
        img_seg = seg_results
    
    # Label image
    img_label = label_img(
        img_seg,
        plot=plot,
        **label_params
    )
    
    # Calculate region properties
    regions = measure.regionprops(img_label, intensity_image=img_norm)
    
    # Create DataFrame of properties
    props_list = [
        'area', 'bbox', 'centroid', 'convex_area', 'eccentricity',
        'equivalent_diameter', 'euler_number', 'extent', 'filled_area',
        'label', 'major_axis_length', 'max_intensity', 'mean_intensity',
        'min_intensity', 'minor_axis_length', 'orientation', 'perimeter',
        'solidity', 'weighted_centroid'
    ]
    
    region_table = measure.regionprops_table(
        img_label,
        intensity_image=img_norm,
        properties=props_list
    )
    df_regions = pd.DataFrame(region_table)
    
    # Prepare output
    output = {
        "original": pil_img if pil_img is not None else img_array,
        "array": img_array,
        "normalized": img_norm,
        "cleaned": img_clean,
        "segmentation": img_seg,
        "labeled": img_label,
        "regions": regions,
        "df_regions": df_regions
    }
    
    # Add intermediate results if requested
    if return_all and isinstance(seg_results, dict):
        output.update(seg_results)
    
    # Visualization of final results
    if plot:
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        titles = ["Original", "Normalized", "Cleaned", "Segmentation", "Labeled", "Overlay"]
        
        # Handle different image types
        display_images = [
            output["original"] if pil_img is not None else output["array"],
            output["normalized"],
            output["cleaned"],
            output["segmentation"],
            output["labeled"],
            color.label2rgb(output["labeled"], image=output["normalized"], alpha=0.3)
        ]
        
        for ax, title, disp_img in zip(axes.flatten(), titles, display_images):
            ax.imshow(disp_img, cmap='gray' if title != "Labeled" else 'nipy_spectral')
            ax.set_title(title)
            ax.axis('off')
        
        plt.tight_layout()
        plt.show()
    
    return output


# Helper functions for common operations
def overlay_labels(
    image: np.ndarray,
    labels: np.ndarray,
    alpha: float = 0.3,
    plot: bool = False
) -> np.ndarray:
    """
    Create overlay of labels on original image
    
    Args:
        image: Original image
        labels: Label array
        alpha: Transparency for overlay
        plot: Whether to show result
        
    Returns:
        Overlay image
    """
    overlay = color.label2rgb(labels, image=image, alpha=alpha)
    if plot:
        plt.figure(figsize=(10, 5))
        plt.imshow(overlay)
        plt.axis('off')
        plt.show()
    return overlay


def extract_region_features(
    label_image: np.ndarray,
    intensity_image: np.ndarray,
    features: List[str] = None
) -> pd.DataFrame:
    """
    Extract specific features from labeled regions
    
    Args:
        label_image: Labeled image
        intensity_image: Intensity image for measurements
        features: List of features to extract
        
    Returns:
        DataFrame of region features
    """
    default_features = [
        'area', 'bbox', 'centroid', 'convex_area', 'eccentricity',
        'equivalent_diameter', 'euler_number', 'extent', 'filled_area',
        'label', 'major_axis_length', 'max_intensity', 'mean_intensity',
        'min_intensity', 'minor_axis_length', 'orientation', 'perimeter',
        'solidity', 'weighted_centroid'
    ]
    
    features = features or default_features
    props = measure.regionprops_table(label_image, intensity_image, properties=features)
    return pd.DataFrame(props)



# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from scipy.stats import pearsonr
# from PIL import Image
# from skimage import filters, morphology, measure, color

# #  用来处理ich图像的初级工具包


# def open_img(dir_img, convert="gray", plot=False):
#     # Step 1: Load the image
#     image = Image.open(dir_img)

#     if convert == "gray" or convert == "grey":
#         gray_image = image.convert("L")
#         image_array = np.array(gray_image)
#     else:
#         image_array = np.array(image)
#     if plot:
#         _, axs = plt.subplots(1, 2)
#         axs[0].imshow(image)
#         axs[1].imshow(image_array)
#         axs[0].set_title("img_raw")
#         axs[1].set_title(f"img_{convert}")
#     return image, image_array


# from skimage import filters, morphology


# def clean_img(
#     img,
#     method=["threshold_otsu", "objects", "holes"],
#     obj_min=50,
#     hole_min=50,
#     filter=None,
#     plot=False,
#     cmap="grey",
# ):
#     if isinstance(method, str):
#         if method == "all":
#             method = ["threshold_otsu", "objects", "holes"]
#         else:
#             method = [method]
#     if any("thr" in met or "ot" in met for met in method) and filter is None:
#         thr_otsu = filters.threshold_otsu(img)
#         img_update = img > thr_otsu
#     if any("obj" in met for met in method):
#         img_update = morphology.remove_small_objects(img_update, min_size=obj_min)
#     if any("hol" in met for met in method):
#         img_update = morphology.remove_small_holes(img_update, area_threshold=hole_min)
#     if ("thr" in met for met in method) and filter:  # threshold
#         mask = (img >= filter[0]) & (img <= filter[1])
#         img_update = np.where(mask, img, 0)

#     if plot:
#         plt.imshow(img_update, cmap=cmap)
#     return img_update


# from skimage import filters, segmentation


# def segment_img(
#     img,
#     filter=[30, 150],
#     plot=False,
#     mode="reflect",  # 'reflect' or 'constant'
#     method="region",  # 'region' or 'edge', 'threshold'
#     area_min=50,
#     cmap="jet",
#     connectivity=1,
#     output="segmentation",
# ):
#     if "reg" in method:  # region method
#         # 1. find an elevation map using the Sobel gradient of the image
#         elevation_map = filters.sobel(img, mode=mode)
#         # 2. find markers of the background and the coins based on the extreme parts of the histogram of gray values.
#         markers = np.zeros_like(img)
#         # Apply filtering based on provided filter values
#         if filter is not None:
#             markers[img < filter[0]] = 1
#             markers[img > filter[1]] = 2
#         else:
#             # If no filter is provided, set markers across the whole range of the image
#             markers[img == img.min()] = 1
#             markers[img == img.max()] = 2
#         # 3. watershed transform to fill regions of the elevation map starting from the markers
#         img_segmentation = segmentation.watershed(
#             elevation_map, markers=markers, connectivity=connectivity
#         )
#         if plot:
#             _, axs = plt.subplots(2, 2)
#             for i, ax in enumerate(axs.flatten().tolist()):
#                 if i == 0:
#                     ax.imshow(img)
#                     ax.set_title("image")
#                 elif i == 1:
#                     ax.imshow(elevation_map, cmap=cmap)
#                     ax.set_title("elevation map")
#                 elif i == 2:
#                     ax.imshow(markers, cmap=cmap)
#                     ax.set_title("markers")
#                 elif i == 3:
#                     ax.imshow(img_segmentation, cmap=cmap)
#                     ax.set_title("segmentation")
#                 ax.set_axis_off()
#         if "el" in output:
#             return elevation_map
#         elif "mar" in output:
#             return markers
#         elif "seg" in output:
#             return img_segmentation
#         else:
#             return img_segmentation
#     elif "ed" in method:  # edge
#         edges = cal_edges(img)
#         fills = fill_holes(edges)
#         img_segmentation = remove_holes(fills, area_min)
#         if plot:
#             _, axs = plt.subplots(2, 2)
#             for i, ax in enumerate(axs.flatten().tolist()):
#                 if i == 0:
#                     ax.imshow(img)
#                     ax.set_title("image")
#                 elif i == 1:
#                     ax.imshow(edges, cmap=cmap)
#                     ax.set_title("edges map")
#                 elif i == 2:
#                     ax.imshow(fills, cmap=cmap)
#                     ax.set_title("fills")
#                 elif i == 3:
#                     ax.imshow(img_segmentation, cmap=cmap)
#                     ax.set_title("segmentation")
#                 ax.set_axis_off()
#         if "seg" in output:
#             return img_segmentation
#         elif "ed" in output:
#             return edges
#         elif "fill" in output:
#             return fills
#         else:
#             return img_segmentation
#     elif "thr" in method:  # threshold
#         if filter:
#             mask = (img >= filter[0]) & (img <= filter[1])
#             img_threshold = np.where(mask, img, 0)
#             if plot:
#                 plt.imshow(img_threshold, cmap=cmap)
#             return img_threshold
#         else:
#             return None


# from skimage import measure


# def label_img(img, plot=False):
#     img_label = measure.label(img)
#     if plot:
#         plt.imshow(img_label)
#     return img_label


# def img_process(img, **kwargs):
#     convert = "gray"
#     method_clean_img = ["threshold_otsu", "objects", "holes"]
#     obj_min_clean_img = 50
#     hole_min_clean_img = 50
#     plot = True
#     for k, v in kwargs.items():
#         if "convert" in k.lower():
#             convert = v
#         if "met" in k.lower() and any(
#             ["clean" in k.lower(), "rem" in k.lower(), "rm" in k.lower()]
#         ):
#             method_clean_img = v
#         if "obj" in k.lower() and any(
#             ["clean" in k.lower(), "rem" in k.lower(), "rm" in k.lower()]
#         ):
#             obj_min_clean_img = v
#         if "hol" in k.lower() and any(
#             ["clean" in k.lower(), "rem" in k.lower(), "rm" in k.lower()]
#         ):
#             hole_min_clean_img = v
#         if "plot" in k.lower():
#             plot = v

#     if isinstance(img, str):
#         image, image_array = open_img(img, convert=convert)
#         normalized_image = image_array / 255.0
#     else:
#         cleaned_image = img
#         image_array = cleaned_image
#         normalized_image = cleaned_image
#         image = cleaned_image

#     # Remove small objects and fill small holes
#     cleaned_image = clean_img(
#         img=image_array,
#         method=method_clean_img,
#         obj_min=obj_min_clean_img,
#         hole_min=hole_min_clean_img,
#         plot=False,
#     )
#     # Label the regions
#     label_image = label_img(cleaned_image)
#     overlay_image = overlay_imgs(label_image, image=image_array)
#     regions = measure.regionprops(label_image, intensity_image=image_array)
#     region_props = measure.regionprops_table(
#         label_image, intensity_image=image_array, properties=props_list
#     )
#     df_regions = pd.DataFrame(region_props)
#     # Pack the results into a single output variable (dictionary)
#     output = {
#         "img": image,
#         "img_array": image_array,
#         "img_scale": normalized_image,
#         "img_clean": cleaned_image,
#         "img_label": label_image,
#         "img_overlay": overlay_image,
#         "regions": regions,
#         "df_regions": df_regions,
#     }
#     if plot:
#         imgs = []
#         [imgs.append(i) for i in list(output.keys()) if "img" in i]
#         for img_ in imgs:
#             plt.figure()
#             plt.imshow(output[img_])
#             plt.title(img_)
#     return output


# # def img_preprocess(dir_img, subtract_background=True, size_obj=50, size_hole=50,**kwargs):
# #     """
# #     Processes an image by performing thresholding, morphological operations,
# #     and region labeling.

# #     Parameters:
# #     - dir_img: Path to the image file.
# #     - size_obj: Minimum size of objects to keep (default: 50).
# #     - size_hole: Maximum size of holes to fill (default: 50).

# #     Returns:
# #     - output: Dictionary containing the overlay image, threshold value, and regions.
# #     """
# #     props_list = [
# #         "area",  # Number of pixels in the region. Useful for determining the size of regions.
# #         "area_bbox",
# #         "area_convex",
# #         "area_filled",
# #         "axis_major_length",  # Lengths of the major and minor axes of the ellipse that fits the region. Useful for understanding the shape's elongation and orientation.
# #         "axis_minor_length",
# #         "bbox",  # Bounding box coordinates (min_row, min_col, max_row, max_col). Useful for spatial localization of regions.
# #         "centroid",  # Center of mass coordinates (centroid-0, centroid-1). Helps locate the center of each region.
# #         "centroid_local",
# #         "centroid_weighted",
# #         "centroid_weighted_local",
# #         "coords",
# #         "eccentricity",  # Measure of how elongated the region is. Values range from 0 (circular) to 1 (line). Useful for assessing the shape of regions.
# #         "equivalent_diameter_area",  # Diameter of a circle with the same area as the region. Provides a simple measure of size.
# #         "euler_number",
# #         "extent",  # Ratio of the region's area to the area of its bounding box. Indicates how much of the bounding box is filled by the region.
# #         "feret_diameter_max",  # Maximum diameter of the region, providing another measure of size.
# #         "image",
# #         "image_convex",
# #         "image_filled",
# #         "image_intensity",
# #         "inertia_tensor",  # ensor describing the distribution of mass in the region, useful for more advanced shape analysis.
# #         "inertia_tensor_eigvals",
# #         "intensity_max",  # Maximum intensity value within the region. Helps identify regions with high-intensity features.
# #         "intensity_mean",  # Average intensity value within the region. Useful for distinguishing between regions based on their brightness.
# #         "intensity_min",  # Minimum intensity value within the region. Useful for regions with varying intensity.
# #         "intensity_std",
# #         "label",  # Unique identifier for each region.
# #         "moments",
# #         "moments_central",
# #         "moments_hu",  # Hu moments are a set of seven invariant features that describe the shape of the region. Useful for shape recognition and classification.
# #         "moments_normalized",
# #         "moments_weighted",
# #         "moments_weighted_central",
# #         "moments_weighted_hu",
# #         "moments_weighted_normalized",
# #         "orientation",  # ngle of the major axis of the ellipse that fits the region. Useful for determining the orientation of elongated regions.
# #         "perimeter",  # Length of the boundary of the region. Useful for shape analysis.
# #         "perimeter_crofton",
# #         "slice",
# #         "solidity",  # Ratio of the area of the region to the area of its convex hull. Indicates how solid or compact a region is.
# #     ]
# #     if isinstance(dir_img, str):
# #         # Step 1: Load the image
# #         image = Image.open(dir_img)

# #         # Step 2: Convert the image to grayscale and normalize
# #         gray_image = image.convert("L")
# #         image_array = np.array(gray_image)
# #         normalized_image = image_array / 255.0
# #     else:
# #         cleaned_image = dir_img
# #         image_array = cleaned_image
# #         normalized_image = cleaned_image
# #         image = cleaned_image
# #         binary_image = cleaned_image
# #         thr_val = None
# #     if subtract_background:
# #         # Step 3: Apply thresholding to segment the image
# #         thr_val = filters.threshold_otsu(image_array)
# #         print(f"Threshold value is: {thr_val}")

# #         # Apply thresholds and generate binary images
# #         binary_image = image_array > thr_val

# #         # Step 4: Perform morphological operations to clean the image
# #         # Remove small objects and fill small holes
# #         cleaned_image_rm_min_obj = morphology.remove_small_objects(
# #             binary_image, min_size=size_obj
# #         )
# #         cleaned_image = morphology.remove_small_holes(
# #             cleaned_image_rm_min_obj, area_threshold=size_hole
# #         )

# #     # Label the regions
# #     label_image = label_img(cleaned_image)

# #     # Optional: Overlay labels on the original image
# #     overlay_image = color.label2rgb(label_image, image_array)
# #     regions = measure.regionprops(label_image, intensity_image=image_array)
# #     region_props = measure.regionprops_table(
# #         label_image, intensity_image=image_array, properties=props_list
# #     )
# #     df_regions = pd.DataFrame(region_props)
# #     # Pack the results into a single output variable (dictionary)
# #     output = {
# #         "img": image,
# #         "img_array": image_array,
# #         "img_scale": normalized_image,
# #         "img_binary": binary_image,
# #         "img_clean": cleaned_image,
# #         "img_label": label_image,
# #         "img_overlay": overlay_image,
# #         "thr_val": thr_val,
# #         "regions": regions,
# #         "df_regions": df_regions,
# #     }

# #     return output


def cal_pearson(img1, img2):
    """Compute Pearson correlation coefficient between two images."""
    img1_flat = img1.flatten()
    img2_flat = img2.flatten()
    r, p = pearsonr(img1_flat, img2_flat)
    return r, p


def cal_manders(img1, img2):
    """Compute Manders' overlap coefficient between two binary images."""
    img1_binary = img1 > filters.threshold_otsu(img1)
    img2_binary = img2 > filters.threshold_otsu(img2)
    overlap_coef = np.sum(img1_binary & img2_binary) / np.sum(img1_binary)
    return overlap_coef


def overlay_imgs(
    *imgs,
    image=None,
    colors=None,
    alpha=0.3,
    bg_label=0,
    bg_color=(0, 0, 0),
    image_alpha=1,
    kind="overlay",
    saturation=0,
    channel_axis=-1,
):
    # Ensure all input images have the same shape
    print(
        f'\nusage:\nich2ls.overlay_imgs(res_b["img_binary"], res_r["img_binary"], bg_label=0)'
    )
    shapes = [img.shape for img in imgs]
    if not all(shape == shapes[0] for shape in shapes):
        raise ValueError("All input images must have the same shape")

    # If no image is provided, use the first input image as the base
    if image is None:
        image = imgs[0]

    # Combine the images into a label, with unique multipliers for each image
    label = sum((img.astype(np.uint) * (i + 1) for i, img in enumerate(imgs)))

    # Create the overlay image
    overlay_image = color.label2rgb(
        label,
        image=image,
        bg_label=bg_label,
        colors=colors,
        alpha=alpha,
        bg_color=bg_color,
        image_alpha=image_alpha,
        saturation=saturation,
        kind=kind,
        channel_axis=channel_axis,  # Corrected from saturation to channel_axis
    )

    return overlay_image


from skimage import exposure


# Comparing edge-based and region-based segmentation
def draw_hist(img, ax=None, **kwargs):
    """
    _, axs = plt.subplots(1, 2)
    draw_hist(image, c="r", ax=axs[1], lw=2, ls=":")
    """
    print(f"img type: {type(img)}")
    if not isinstance(img, np.ndarray):
        img = np.array(img)
    hist, hist_centers = exposure.histogram(img)
    if ax is None:
        ax = plt.gca()
    ax.plot(hist_centers, hist, **kwargs)


from skimage import feature


# delineate the contours of the coins using edge-based segmentation
def cal_edges(img, plot=False, cmap=plt.cm.gray):
    edges = feature.canny(img)
    if plot:
        plt.imshow(edges, cmap=cmap)
    return edges


from scipy import ndimage as ndi


# These contours are then filled using mathematical morphology.
def fill_holes(img, plot=False):
    img_fill_holes = ndi.binary_fill_holes(img)
    if plot:
        plt.imshow(img_fill_holes, cmap=plt.cm.gray)
    return img_fill_holes


from skimage import morphology


def remove_holes(img, size=50, plot=False):
    img_rm_holes = morphology.remove_small_objects(img, size)
    if plot:
        plt.imshow(img_rm_holes, cmap=plt.cm.gray)
    return img_rm_holes


import matplotlib.patches as mpatches
from skimage import measure, color


def draw_bbox(
    img,
    df=None,
    img_label=None,
    img_label2rgb=None,
    show=True,  # plot the image
    bg_alpha=1,  # the alpha of the bg image
    area_min=1,
    area_max=None,
    fill=False,
    edgecolor="red",
    linewidth=2,
    ax=None,
    **kwargs,
):
    """
    ich2ls.draw_bbox(
    res["img_label"], fill=False, color="r", lw=1, edgecolor="w", alpha=0.4)
    """
    if ax is None:
        ax = plt.gca()
    try:
        if img_label is None:
            img_label = measure.label(img)
    except Exception as e:
        print(e)
        img_label=img
    if isinstance(show, bool):
        if show:
            try:
                if img_label2rgb is None:
                    img_label2rgb = color.label2rgb(img_label, image=img, bg_label=0)
                ax.imshow(img_label2rgb, alpha=bg_alpha)
            except Exception as e:
                print(e)
                ax.imshow(img_label, alpha=bg_alpha)
    elif isinstance(show, str):
        if "raw" in show:
            ax.imshow(img, alpha=bg_alpha)
        elif "label" in show:
            ax.imshow(img_label, alpha=bg_alpha)
        elif "rgb" in show:
            if img_label2rgb is None:
                img_label2rgb = color.label2rgb(img_label, image=img, bg_label=0)
            ax.imshow(img_label2rgb, alpha=bg_alpha)
        elif "no" in show.lower():
            pass
    num = 0
    if df is None:
        for region in measure.regionprops(img_label):
            # take regions with large enough areas
            if area_max is None:
                area_max = np.inf
            if area_min <= region.area <= area_max:
                minr, minc, maxr, maxc = region.bbox
                rect = mpatches.Rectangle(
                    (minc, minr),
                    maxc - minc,
                    maxr - minr,
                    fill=fill,
                    edgecolor=edgecolor,
                    linewidth=linewidth,
                    **kwargs,
                )
                ax.add_patch(rect)
                num += 1
    else:
        # Iterate over each row in the DataFrame and draw the bounding boxes
        for _, row in df.iterrows():
            minr = row["bbox-0"]
            minc = row["bbox-1"]
            maxr = row["bbox-2"]
            maxc = row["bbox-3"]

            # Optionally filter by area if needed
            area = (maxr - minr) * (maxc - minc)
            if area >= area_min:
                rect = mpatches.Rectangle(
                    (minc, minr),
                    maxc - minc,
                    maxr - minr,
                    fill=fill,
                    edgecolor=edgecolor,
                    linewidth=linewidth,
                    **kwargs,
                )
                ax.add_patch(rect)
                num += 1
    return num


props_list = [
    "area",  # Number of pixels in the region. Useful for determining the size of regions.
    "area_bbox",
    "area_convex",
    "area_filled",
    "axis_major_length",  # Lengths of the major and minor axes of the ellipse that fits the region. Useful for understanding the shape's elongation and orientation.
    "axis_minor_length",
    "bbox",  # Bounding box coordinates (min_row, min_col, max_row, max_col). Useful for spatial localization of regions.
    "centroid",  # Center of mass coordinates (centroid-0, centroid-1). Helps locate the center of each region.
    "centroid_local",
    "centroid_weighted",
    "centroid_weighted_local",
    "coords",
    "eccentricity",  # Measure of how elongated the region is. Values range from 0 (circular) to 1 (line). Useful for assessing the shape of regions.
    "equivalent_diameter_area",  # Diameter of a circle with the same area as the region. Provides a simple measure of size.
    "euler_number",
    "extent",  # Ratio of the region's area to the area of its bounding box. Indicates how much of the bounding box is filled by the region.
    "feret_diameter_max",  # Maximum diameter of the region, providing another measure of size.
    "image",
    "image_convex",
    "image_filled",
    "image_intensity",
    "inertia_tensor",  # ensor describing the distribution of mass in the region, useful for more advanced shape analysis.
    "inertia_tensor_eigvals",
    "intensity_max",  # Maximum intensity value within the region. Helps identify regions with high-intensity features.
    "intensity_mean",  # Average intensity value within the region. Useful for distinguishing between regions based on their brightness.
    "intensity_min",  # Minimum intensity value within the region. Useful for regions with varying intensity.
    "intensity_std",
    "label",  # Unique identifier for each region.
    "moments",
    "moments_central",
    "moments_hu",  # Hu moments are a set of seven invariant features that describe the shape of the region. Useful for shape recognition and classification.
    "moments_normalized",
    "moments_weighted",
    "moments_weighted_central",
    "moments_weighted_hu",
    "moments_weighted_normalized",
    "orientation",  # ngle of the major axis of the ellipse that fits the region. Useful for determining the orientation of elongated regions.
    "perimeter",  # Length of the boundary of the region. Useful for shape analysis.
    "perimeter_crofton",
    "slice",
    "solidity",  # Ratio of the area of the region to the area of its convex hull. Indicates how solid or compact a region is.
] 

from skimage.util import img_as_ubyte

def remove_high_intensity_artifacts(img, threshold=200, replace_value=255, min_size=1):
    """
    Remove high-intensity artifacts from image.

    Parameters:
    - img: Input image (2D or 3D numpy array)
    - threshold: Intensity threshold (typically 230-255)
    - replace_value: Value or color to replace artifacts with
    - min_size: Minimum artifact size to remove (in pixels)

    Returns:
    - cleaned: Image with artifacts removed/replaced
    """
    # Replace NaNs with 0 before type conversion
    if np.isnan(img).any():
        img = np.nan_to_num(img, nan=0)

    try:
        img = img_as_ubyte(img)
    except Exception as e:
        print(f"Failed to use img_as_ubyte: {e}")

    if img.ndim not in [2, 3]:
        raise ValueError("Input image must be 2D (grayscale) or 3D (RGB).")

    # Create mask for high-intensity regions
    mask = np.any(img > threshold, axis=-1) if img.ndim == 3 else img > threshold
    mask = morphology.remove_small_objects(mask, min_size=min_size)
    mask = morphology.binary_opening(mask, morphology.disk(3))

    cleaned = img.copy()

    if img.ndim == 3:
        for c in range(3):
            channel = cleaned[:, :, c]
            valid = ~mask
            if np.any(valid):
                background_val = np.median(channel[valid])
            else:
                background_val = 0
            channel[mask] = background_val
            cleaned[:, :, c] = channel
    else:
        valid = ~mask
        if np.any(valid):
            cleaned[mask] = np.median(cleaned[valid])
        else:
            cleaned[mask] = replace_value

    return cleaned

from PIL import Image
import numpy as np
from skimage.restoration import rolling_ball
from skimage import morphology, filters
from skimage.util import img_as_ubyte
from skimage import img_as_float
from scipy.ndimage import median_filter
from skimage.morphology import disk

# Default method-specific config
METHOD_CONFIG = {
    'rolling_ball': {'radius': 30},
    'gaussian_sub': {'sigma': 10},
    'median': {'size': 20},
    'tophat': {'radius': 15},
}

# Thresholding defaults
DEFAULT_THRESHOLD = {
    'otsu': True,   # could be expanded later for other methods
}

def clean_background(
    img,
    method='rolling_ball',
    thr=None,              # custom threshold value, None = use method (e.g., 'otsu')
    **kwargs               # extra config like radius=30, sigma=5, etc.
):
    """
    Preprocess an image with background subtraction and thresholding.

    Parameters:
    - img (str | PIL.Image.Image | np.ndarray): Input image.
    - method (str): Background subtraction method.
    - thr (float or None): Threshold value. If None, use default method (e.g., 'otsu').
    - kwargs: Method-specific overrides like radius=30, sigma=5, etc.

    Returns:
    - cleaned (ndarray): Binary preprocessed image (uint8).
    """

    # Step 1: Load and normalize input image
    if isinstance(img, str):
        img_pil = Image.open(img).convert('L')
    elif isinstance(img, Image.Image):
        img_pil = img.convert('L')
    elif isinstance(img, np.ndarray):
        img_pil = Image.fromarray(img).convert('L') if img.ndim == 3 else Image.fromarray(img.astype(np.uint8))
    else:
        raise TypeError("Input must be a file path (str), PIL.Image, or numpy.ndarray")

    img_gray = np.array(img_pil)
    img_float = img_as_float(img_gray)

    # Step 2: Load defaults and override with kwargs
    config = METHOD_CONFIG.get(method)
    if config is None:
        raise ValueError(f"Unknown method: {method}")
    config = config.copy()
    config.update({k: v for k, v in kwargs.items() if v is not None})  # override if provided

    # Step 3: Apply background subtraction
    if method == 'rolling_ball':
        img_bg_removed = rolling_ball(img_float, radius=config['radius'])
    elif method == 'gaussian_sub':
        img_bg_removed = img_float - filters.gaussian(img_float, sigma=config['sigma'])
    elif method == 'median':
        img_bg_removed = img_float - median_filter(img_float, size=config['size'])
    elif method == 'tophat':
        selem = disk(config['radius'])
        img_bg_removed = morphology.white_tophat(img_gray, selem=selem)
        img_bg_removed = img_as_float(img_bg_removed)
    else:
        raise ValueError(f"Unsupported method: {method}")

    # # Step 4: Thresholding
    # if thr is None:
    #     # use Otsu
    #     thr_val = filters.threshold_otsu(img_bg_removed)
    # else:
    #     thr_val = thr

    # binary = img_bg_removed > thr_val

    # # Step 5: Morphological cleanup
    # cleaned = morphology.remove_small_objects(binary, min_size=100)
    # cleaned = morphology.remove_small_holes(cleaned, area_threshold=100)

    return img_as_ubyte(img_bg_removed)
 

#! ============增强版的图像分析工具===============
# 支持多种染色方法并自动判断是否需要反转通道。该工具可以处理HED、RGB、荧光等多种染色方式，并支持多通道联合分析。
# 多通道联合分析：可以分析两个染色通道的共定位情况，如DAB阳性细胞核
# 自动通道反转：根据染色类型自动决定是否需要反转通道值
# 标准化输出：所有结果都包含统一的测量指标，便于比较
# 灵活的可视化：支持叠加显示和单独显示各通道结果

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import pandas as pd 
from skimage import morphology,measure,color,filters
from sklearn import cluster
from scipy.ndimage import median_filter
from skimage import exposure
import matplotlib.colors as mcolors
from skimage.color import rgb2hsv
class StainDetector:
    """
    多功能染色分析工具，支持多种染色方法

    支持的染色方法:
    - HED染色: 核染色(Hematoxylin), 伊红(Eosin), DAB
    - RGB染色: 常规RGB通道分析
    - 荧光染色: FITC(绿), TRITC(红), DAPI(蓝), Cy5(远红)
    - 特殊染色: Masson(胶原纤维), PAS(糖原), Silver(神经纤维)
    """
    ARTIFACT_STRATEGIES = {
            'median': lambda orig, mask: median_filter(orig, size=(5,5,1)),
            'inpaint': lambda orig, mask: cv2.inpaint(orig, mask.astype(np.uint8), 3, cv2.INPAINT_TELEA),
            'background': lambda orig, mask: np.where(mask[...,None], np.percentile(orig, 25, axis=(0,1)), orig),
            'blur': lambda orig, mask: np.where(mask[...,None], filters.gaussian(orig, sigma=2), orig)
        }
    # 染色方法配置字典
    STAIN_CONFIG = {
        # HED染色
        "hematoxylin": {
            "method": "hed",
            "channel": 0,
            "invert": True,
            "color": "hematoxylin",  # Special name for custom cmap
            "alpha": 0.5,
            "cmap": None,  # Will be created dynamically
        },
        "nuclei": {
            "method": "hed",
            "channel": 0,
            "invert": True,
            "color": "hematoxylin",  # Special name for custom cmap
            "alpha": 0.5,
            "cmap": None,  # Will be created dynamically
        },
        "purple": {
            "method": "hed",
            "channel": 0,
            "invert": True,
            "color": "hematoxylin",  # Special name for custom cmap
            "alpha": 0.5,
            "cmap": None,  # Will be created dynamically
        },
        "h": {
            "method": "hed",
            "channel": 0,
            "invert": True,
            "color": "hematoxylin",  # Special name for custom cmap
            "alpha": 0.5,
            "cmap": None,  # Will be created dynamically
        },
        "eosin": {
            "method": "hed",
            "channel": 1,
            "invert": False,
            "color": "eosin",  # Special name for custom cmap
            "alpha": 0.45,  # Slightly more visible than H
            "cmap": None,
        },
        "cytoplasm": {
            "method": "hed",
            "channel": 1,
            "invert": False,
            "color": "eosin",  # Special name for custom cmap
            "alpha": 0.45,  # Slightly more visible than H
            "cmap": None,
        },
        "pink": {
            "method": "hed",
            "channel": 1,
            "invert": False,
            "color": "eosin",  # Special name for custom cmap
            "alpha": 0.45,  # Slightly more visible than H
            "cmap": None,
        },
        "e": {
            "method": "hed",
            "channel": 1,
            "invert": False,
            "color": "eosin",  # Special name for custom cmap
            "alpha": 0.45,  # Slightly more visible than H
            "cmap": None,
        },
        "dab": {
            "method": "hed",
            "channel": 2,
            "invert": True,
            "color": "dab",
            "alpha": 0.4,
            "cmap": None,
        },
        # RGB单通道
        "red": {"method": "rgb", "channel": "R", "invert": False, "color": "red"},
        "green": {"method": "rgb", "channel": "G", "invert": False, "color": "green"},
        "blue": {"method": "rgb", "channel": "B", "invert": False, "color": "blue"},
        # 荧光染色
        "dapi": {
            "method": "rgb",
            "channel": "B",
            "invert": True,
            "color": "dapi",
            "alpha": 0.5,
            "cmap": None,
        },
        "fitc": {
            "method": "rgb",
            "channel": "G",
            "invert": False,
            "color": "fitc",
            "alpha": 0.6,
            "cmap": None,
        },
        "tritc": {"method": "rgb", "channel": "R", "invert": False, "color": "red"},
        "cy5": {"method": "hsv", "channel": 0, "invert": True, "color": "magenta"},
        # 特殊染色
        "masson": {"method": "rgb", "channel": "B", "invert": False, "color": "blue"},
        "pas": {"method": "rgb", "channel": "R", "invert": False, "color": "magenta"},
        "silver": {"method": "rgb", "channel": "G", "invert": True, "color": "black"},
    }

    def __init__(self, image_path):
        """初始化分析器，加载图像"""
        self.results = {}
        self._init_custom_colormaps() 
        if isinstance(image_path,str):
            self.image_path = image_path
            self.image_rgb = np.array(Image.open(image_path).convert("RGB"))
        else:
            self.image_path=None
            self.image_rgb=image_path 
        # Precompute HSV for color-based analysis
        self.image_hsv = rgb2hsv(self.image_rgb / 255.0)  # Normalized HSV

    def extract_channel(self, stain_type, channel='rgb'):
        """
        根据染色类型提取对应通道，支持自定义通道或自动检测
        
        参数:
            stain_type: 染色类型名称 (必须存在于STAIN_CONFIG中)
            channel: 可选，可覆盖默认通道设置:
                - 对于HED: 0,1,2
                - 对于RGB: 'R','G','B'
                - 对于HSV: 0,1,2
        """
        config = self.STAIN_CONFIG[stain_type.lower()]
        method = config["method"]
        
        # 优先使用自定义通道
        if channel is not None:
            if method == "rgb" and isinstance(channel, int):
                channel = ['R','G','B'][channel]
            config = config.copy()  # 避免修改原始配置
            config["channel"] = channel
        
        if method == "hed":
            stains = color.rgb2hed(self.image_rgb)
            channel = stains[:, :, config["channel"]]
        elif method == "rgb":
            idx = {"R": 0, "G": 1, "B": 2}[str(config["channel"]).upper()]
            channel = self.image_rgb[:, :, idx]
        elif method == "hsv":
            hsv = color.rgb2hsv(self.image_rgb)
            channel = hsv[:, :, config["channel"]]
        
        return channel, config

    def detect_primary_channel(self, method="hed"):
        """
        自动检测图像中信号最强的通道
        
        参数:
            method: 检测模式 ('hed', 'rgb', 或 'hsv')
        返回:
            通道索引 (对于HED/HSV为0-2，对于RGB为'R'/'G'/'B')
        """
        if method == "hed":
            stains = color.rgb2hed(self.image_rgb)
            channel_means = [np.mean(stains[:,:,i]) for i in range(3)]
            return np.argmax(channel_means)
        elif method == "rgb":
            channel_means = [np.mean(self.image_rgb[:,:,i]) for i in range(3)]
            return ['R','G','B'][np.argmax(channel_means)]
        elif method == "hsv":
            hsv = color.rgb2hsv(self.image_rgb)
            channel_means = [np.mean(hsv[:,:,i]) for i in range(3)]
            return np.argmax(channel_means)
        else:
            raise ValueError("Method must be 'hed', 'rgb', or 'hsv'")
    
    def process(self, 
                stain_type, 
                sigma=1.0, 
                min_size=50, 
                hole_size=100, 
                channel=None,     
                subtract_background=False,
                use_local_threshold=False, 
                apply_remove_high_intensity_artifacts=False,
                block_size=35, #use_local_threshold
                contrast=False,
                contrast_method="clahe",
                clip_limit=0.01,# only for clahe method
                stretch_range=(2,98),# only for stretch method
                ):
        """
        处理特定染色通道

        参数:
            stain_type: 染色类型 (如 'dab', 'hematoxylin', 'fitc'等)
            sigma: 高斯模糊半径
            min_size: 最小区域像素大小

        返回:
            binary_mask, labeled_image, dataframe
        增强版处理函数，支持自定义通道
        
        参数:
            channel: 可覆盖STAIN_CONFIG中的通道设置
        """
        # 自动检测通道（如果未提供且配置允许）
        if channel is None and self.STAIN_CONFIG[stain_type.lower()].get("auto_detect", True):
            method = self.STAIN_CONFIG[stain_type.lower()]["method"]
            channel = self.detect_primary_channel(method)
            print(f"Auto-detected primary channel for {stain_type}: {channel}")
        
        channel, config = self.extract_channel(stain_type, channel)  
        # Optional contrast enhancement 
        if contrast: 
            channel = self.enhance_contrast(channel, method=contrast_method,clip_limit=clip_limit,stretch_range=stretch_range) 
            print("increase contrast")

        processed = -channel if config["invert"] else channel
        if subtract_background:
            processed=clean_background(processed)
        if sigma:
            processed = filters.gaussian(processed, sigma=sigma)
        if apply_remove_high_intensity_artifacts:
            processed=remove_high_intensity_artifacts(processed, threshold=250, replace_value=255, min_size=20)
        processed = (processed - processed.min()) / (processed.max() - processed.min())
        # blurred = blurred[~np.isnan(blurred)] 
        if np.isnan(processed).any():
            processed = np.nan_to_num(processed, nan=0)
        # --- 阈值处理部分 ---
        if use_local_threshold:
            threshold = filters.threshold_local(processed, block_size) 
        else:
            threshold = filters.threshold_otsu(processed)  
        binary_mask = processed > threshold 

        # Remove small objects and fill holes
        cleaned_mask = morphology.remove_small_objects(binary_mask, min_size=min_size)
        try:
            cleaned_mask = morphology.remove_small_holes(cleaned_mask, area_threshold=hole_size)
            cleaned_mask = morphology.binary_closing(cleaned_mask, morphology.disk(2))
        except Exception as e:
            print(f"cannot fill the holes but only removed small objects, error: {e}")

        labeled = morphology.label(cleaned_mask)

        # 提取区域属性
        props = measure.regionprops_table(
            labeled,
            intensity_image=channel,# use the original image instead of processed,
            properties=[
                "area",
                "mean_intensity",
                "eccentricity",
                "solidity",
                "bbox",
                "centroid",
                "label"
            ],
        )
        df = pd.DataFrame(props)
        df["stain_type"] = stain_type

        # 存储结果
        self.results[stain_type] = {
            "mask": cleaned_mask,
            "labeled": labeled,
            "df": df,
            "color": config["color"],
        }

        return cleaned_mask, labeled, df

    

    def enhance_contrast(self, channel_array, method='clahe', clip_limit=0.5,stretch_range=(2,98)):
        """
        Enhance contrast for a specific channel.

        Parameters:
            channel_array: 2D numpy array of the selected channel.
            method: 'clahe' (default), or 'stretch'
            clip_limit: Only for CLAHE, controls contrast enhancement strength.

        Returns:
            contrast_enhanced_channel: 2D numpy array after enhancement
        """
        if method == 'clahe':
            # Apply CLAHE (adaptive histogram equalization)
            enhanced = exposure.equalize_adapthist(channel_array, clip_limit=clip_limit)
        elif method == 'stretch':
            # Contrast stretching
            
            lo, hi = stretch_range
            lo = max(0, min(lo, 100))
            hi = max(0, min(hi, 100))
            p2, p98 = np.percentile(channel_array, (lo,hi))
            enhanced = exposure.rescale_intensity(channel_array, in_range=(p2, p98))
        else:
            raise ValueError("Unsupported method. Use 'clahe' or 'stretch'.")

        return enhanced
    
    def remove_artifacts(self, 
                        intensity_range=(230, 255), 
                        strategy='median',
                        min_artifact_size=1,
                        opening_radius=3,
                        dilation_radius=2):
        """
        Remove high-intensity artifacts from the image using specified strategy
        
        Parameters:
        - intensity_range: Tuple (min, max) intensity values to consider as artifacts
        - strategy: Artifact replacement strategy (median/inpaint/background/blur)
        - min_artifact_size: Minimum contiguous artifact area to remove (pixels)
        - opening_radius: Morphological opening disk radius for mask cleaning
        - dilation_radius: Morphological dilation disk radius for mask expansion
        """
        # # Create base artifact mask
        try:
            if isinstance(self.image_rgb,np.array):
                self.image_rgb=np.array(self.image_rgb)
        except:
            pass
        mask = np.any((self.image_rgb >= intensity_range[0]) & 
                    (self.image_rgb <= intensity_range[1]), axis=2)
        
        # Refine artifact mask
        mask = morphology.binary_opening(mask, morphology.disk(opening_radius))
        mask = morphology.remove_small_objects(mask, min_artifact_size)
        mask = morphology.binary_dilation(mask, morphology.disk(dilation_radius))
        
        # Apply selected replacement strategy
        if strategy in self.ARTIFACT_STRATEGIES:
            cleaned = self.image_rgb.copy()
            replacement = self.ARTIFACT_STRATEGIES[strategy](self.image_rgb, mask)
            cleaned[mask] = replacement[mask]
            self.image_rgb = cleaned
        else:
            raise ValueError(f"Invalid strategy: {strategy}. Choose from {list(self.ARTIFACT_STRATEGIES.keys())}")

        return mask

    # [Keep existing methods unchanged]
    
    def enhanced_process(self, 
                        stain_type,
                        artifact_params=None,
                        **process_kwargs):
        """
        Enhanced processing with optional artifact removal
        
        Parameters:
        - artifact_params: Dict of parameters for remove_artifacts()
                           None skips artifact removal
        - process_kwargs: Arguments for original process() method
        """
        if artifact_params:
            self.remove_artifacts(**artifact_params)
            
        return self.process(stain_type, **process_kwargs)
    def estimate_n_cells(self, stain_type=None, eps=50, min_samples=3, verbose=False, ax=None):
        """
        Estimate the number of distinct cells by clustering nearby nuclei regions.
        
        Parameters:
        - stain_type: Which stain to analyze (defaults to first processed stain)
        - eps: Maximum distance between points in the same cluster (in pixels)
        - min_samples: Minimum points to form a dense region
        - verbose: Whether to print debug information
        - ax: Matplotlib axis to plot the clusters (optional)
        
        Returns:
        - n_cells: Estimated number of distinct cells
        - df: DataFrame with added 'cluster_id' column (-1 means noise)
        """
        if stain_type is None:
            stain_type = next(iter(self.results.keys()))
            print(f"'stain_type' not provided, using the first processed stain: {stain_type}")
        
        # Get the dataframe for this stain
        df = self.results[stain_type.lower()]["df"].copy()
        
        # Skip if no regions detected
        if len(df) == 0:
            if verbose:
                print("No regions detected - returning 0 cells")
            return 0, df
        
        # Extract centroid coordinates
        X = df[["centroid-1", "centroid-0"]].values  # Using (x,y) format
        
        # Apply DBSCAN clustering
        clustering = cluster.DBSCAN(eps=eps, min_samples=min_samples).fit(X)
        df["cluster_id"] = clustering.labels_
        
        # Count clusters (ignoring noise points labeled -1)
        unique_clusters = set(clustering.labels_)
        n_cells = len(unique_clusters) - (1 if -1 in unique_clusters else 0)
        
        if verbose:
            print(f"Estimated number of cells after clustering: {n_cells}")
        
            # Visualization if requested
            if ax is not None:
                ax.scatter(
                    X[:, 0],  # x coordinates
                    X[:, 1],  # y coordinates
                    c=df["cluster_id"],
                    cmap="tab20",
                    s=30,
                    alpha=0.7
                )
                ax.set_title(f"{stain_type} clusters (n={n_cells})")
                ax.invert_yaxis()  # Match image coordinates
                ax.set_aspect('equal')
            
            # Store results back in the detector
            self.results[stain_type.lower()]["df"] = df
            self.results[stain_type.lower()]["n_cells"] = n_cells
             
        return n_cells, df

 
    def count_cells(self, stain_type=None, area_min=20, area_max=2000, min_solidity=0.3):
        """
        Count cells based on filtered nuclei properties.
        """ 
        if stain_type is None:
            stain_type  = list(self.results.keys())[0]
            print(f"'stain_type' not provided, using the first processed stain: {stain_type}")
        df = self.results[stain_type.lower()]["df"].copy()

        # Filter likely nuclei
        filtered = df[
            (df["area"] >= area_min) &
            (df["area"] <= area_max) &
            (df["solidity"] >= min_solidity)
        ].copy()
        self.count_cells_filtered = filtered
        count = len(filtered)
        print(f"Detected {count} cells in stain '{stain_type}'")
        return count

    def calculate_stain_area_ratio(
        self, stain1=None, stain2=None, verbose=True
    ):
        """
        Calculate area ratio between two stains with proper unit handling

        Args:
            stain1: First stain (default: hematoxylin/nuclear)
            stain2: Second stain (default: eosin/cytoplasm)
            verbose: Print formatted results

        Returns:
            Dictionary containing:
            - stain1_area: Area in pixels
            - stain2_area: Area in pixels
            - ratio: stain1/stain2
            - stain1: Name of first stain
            - stain2: Name of second stain
            - unit: Always 'pixels' (px²)
        """
        # Get results if not already processed
        if stain1 is None:
            stain1  = list(self.results.keys())[0]
            print(f"'stain1' not provided, using the first processed stain: {stain1}")
        if stain2 is None:
            stain2  = list(self.results.keys())[1]
            print(f"'stain2' not provided, using the first processed stain: {stain2}") 
        df1 = self.results[stain1.lower()]["df"]
        df2 = self.results[stain2.lower()]["df"]

        # Calculate areas
        area1 = df1["area"].sum()
        area2 = df2["area"].sum()

        # Handle edge cases
        if area2 == 0:
            ratio = float("inf") if area1 > 0 else 0.0
        else:
            ratio = area1 / area2

        # Build results
        result = {
            "stain1_area": area1,
            "stain2_area": area2,
            "ratio": ratio,
            "stain1": stain1,
            "stain2": stain2,
            "unit": "pixels",  
        }

        if verbose:
            print(
                f"\nStain Analysis Ratio ({stain1}/{stain2}):\n"
                f"- {stain1} area: {area1:,} px\n"
                f"- {stain2} area: {area2:,} px\n"
                f"- Ratio: {ratio:.4f}"
            )

        return result

    def analyze_dual_stain(self, stain1, stain2, min_size=50):
        """
        双染色联合分析 (如DAB和核染色)

        返回:
            co_localized_mask, co_localized_df
        """
        # 确保两个染色已处理
        if stain1 not in self.results:
            self.process(stain1)
        if stain2 not in self.results:
            self.process(stain2)

        # 获取两个染色的标记图像
        label1 = self.results[stain1]["labeled"]
        label2 = self.results[stain2]["labeled"]

        # 创建共定位掩模
        co_localized = (label1 > 0) & (label2 > 0)
        co_localized = morphology.remove_small_objects(co_localized, min_size=min_size)
        co_labeled = measure.label(co_localized)

        # 提取共定位区域属性
        props = measure.regionprops_table(co_labeled, properties=["area", "bbox", "centroid"])
        df = pd.DataFrame(props)
        df["stain_pair"] = f"{stain1}_{stain2}"

        return co_localized, co_labeled, df

    def _init_custom_colormaps(self):
        """Initialize custom colormaps for specific stains"""
        # Hematoxylin (desaturated purple)
        hema_colors = [
            (0, 0, 0),
            (0.4, 0.2, 0.6),
            (0.8, 0.6, 0.9),
        ]  # Dark purple to light purple
        self.STAIN_CONFIG["hematoxylin"]["cmap"] = LinearSegmentedColormap.from_list(
            "hema", hema_colors
        )

        # Eosin (pinkish-red)
        eosin_colors = [
            (0, 0, 0),
            (0.9, 0.3, 0.4),
            (1, 0.9, 0.9),
        ]  # Dark red to light pink
        self.STAIN_CONFIG["eosin"]["cmap"] = LinearSegmentedColormap.from_list(
            "eosin", eosin_colors
        )

        # DAB (brown)
        dab_colors = [
            (0, 0, 0),
            (0.6, 0.4, 0.2),
            (0.9, 0.8, 0.6),
        ]  # Dark brown to light brown
        self.STAIN_CONFIG["dab"]["cmap"] = LinearSegmentedColormap.from_list(
            "dab", dab_colors
        )

        # DAPI (vivid blue)
        dapi_colors = [(0, 0, 0), (0.1, 0.1, 0.8), (0.6, 0.8, 1)]
        self.STAIN_CONFIG["dapi"]["cmap"] = LinearSegmentedColormap.from_list(
            "dapi", dapi_colors
        )

        # FITC (vivid green)
        fitc_colors = [(0, 0, 0), (0.1, 0.8, 0.1), (0.8, 1, 0.8)]
        self.STAIN_CONFIG["fitc"]["cmap"] = LinearSegmentedColormap.from_list(
            "fitc", fitc_colors
        )

    def _get_colormap(self, stain_type):
        """Get colormap optimized for specific stain types"""
        config = self.STAIN_CONFIG.get(stain_type.lower(), {})

        if config.get("cmap"):
            return config["cmap"]

        # Default colormaps for non-special stains
        cmaps = {
            "red": "Reds",
            "green": "Greens",
            "blue": "Blues",
            "purple": "Purples",
            "pink": "RdPu",
            "brown": "YlOrBr",
            "magenta": "magma",
            "black": "binary",
        }
        return cmaps.get(config.get("color", "").lower(), "viridis")

    def plot(self, stains=None, figsize=(8, 8), alpha=None, n_col=2):
        """Enhanced visualization with stain-specific settings"""
        if stains is None:
            stains = list(self.results.keys())

        n = len(stains) + 1  # Original + stains
        cols = min(n, n_col)
        rows = (n + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=figsize)
        axes = axes.ravel() if rows > 1 else axes

        # Original image
        axes[0].imshow(self.image_rgb)
        axes[0].set_title("raw")
        axes[0].axis("off")

        # Process each stain
        for i, stain in enumerate(stains, 1): 
            if stain.lower() not in self.results:
                continue
            config = self.STAIN_CONFIG.get(stain.lower(), {})
            stain_alpha = alpha if alpha is not None else config.get("alpha", 0.4)

            axes[i].imshow(self.image_rgb)
            axes[i].imshow(
                self.results[stain]["mask"],
                alpha=stain_alpha,
                cmap=self._get_colormap(stain),
                vmin=0,
                vmax=1,
            )
            axes[i].set_title(f"{stain.capitalize()}")
            axes[i].axis("off")
        # Hide unused axes
        for j in range(i + 1, len(axes)):
            axes[j].axis("off")
        # plt.tight_layout()
    def plot_counts(self, stain_type=None, show_labels=True,show_area=True, figsize=(10, 10),fontsize=9, label_color='yellow', alpha=0.4):
        """
        Display overlay of segmentation on original image with cell label counts.
        """ 
        if stain_type is None:
            # stain_type  = list(self.results.keys())[0]
            stain_type = next(iter(self.results.keys()))
            print(f"'stain_type' not provided, using the first processed stain: {stain_type}")
        # Ensure we have filtered cells
        if not hasattr(self, 'count_cells_filtered'):
            print("Running cell counting first...")
            self.count_cells(stain_type)
        label_image = self.results[stain_type.lower()]["labeled"]
        # df = self.results[stain_type]["df"]
        # df=self.count_cells_filtered

        overlay = color.label2rgb(label_image, image=self.image_rgb, bg_label=0, alpha=0.4)

        fig, axs = plt.subplots(2,1,figsize=figsize)
        axs[0].imshow(self.image_rgb)
        axs[0].set_title(f"raw image")

        axs[1].imshow(overlay)
        axs[1].set_title(f"Area - {stain_type.capitalize()}")

        if show_labels:
            idx=1
            for _, row in self.count_cells_filtered.iterrows():
                y, x = row["centroid-0"], row["centroid-1"]
                if show_area:
                    axs[0].text(x, y, f"{idx}", fontsize=fontsize, color=label_color, ha='center')
                    axs[1].text(x, y, f"{idx}:{str(int(row["area"]))}", fontsize=fontsize, color=label_color, ha='center')
                else:
                    axs[0].text(x, y, f"{idx}", fontsize=fontsize, color=label_color, ha='center')
                    axs[1].text(x, y, f"{idx}", fontsize=fontsize, color=label_color, ha='center')
                idx+=1
                axs[0].axis("off")
                axs[1].axis("off")
        plt.tight_layout()
    def output(self, prefix="analysis"):
        """
        保存所有结果到CSV文件并返回DataFrames
        参数:
            prefix: 保存文件的前缀
        返回:
            dict: 包含两个键:
                - 'combined': 所有结果的合并DataFrame
                - 'individual': 包含各染色单独结果的字典
        """
        all_dfs = []
        individual_dfs = {}

        for stain, data in self.results.items():
            df = data["df"].copy()
            df["stain_type"] = stain  # 确保每个DF都有染色类型列
            all_dfs.append(df)
            individual_dfs[stain] = df

        # 创建返回字典
        result_dict = {
            "combined": (
                pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
            ),
            "individual": individual_dfs,
        }
        return result_dict
 
    @staticmethod
    def dual_color(image, 
                color1=["#8A4EC3", "#7E44C1"], 
                color2=["#A6A3D2", "#B891D0"], 
                bg_v_thresh=0.9, 
                h_delta=0.04, 
                s_delta=0.2, 
                v_delta=0.2,
                allow_overlap=True,
                channel_mode='rgb',channels=None):
        """
        Enhanced dual color analysis supporting multiple images/channels.
        """
        def process_single_image(img, color_group, is_second=False, existing_mask=None,
                allow_overlap=True,):
            # Convert to appropriate color space
            if channel_mode.lower() == 'hed':
                img_conv = color.rgb2hed(img)
                img_processed = np.stack([img_conv[:,:,0], img_conv[:,:,1], 
                                    img_conv[:,:,2]], axis=-1)
            else:
                img_processed = color.rgb2hsv(img)
            
            mask = np.zeros(img_processed.shape[:2], dtype=bool)
            for hex_color in color_group:
                try:
                    rgb_color = mcolors.to_rgb(hex_color)
                    hsv_color = mcolors.rgb_to_hsv(rgb_color)
                    
                    bounds = {
                        "h_min": max(0, hsv_color[0] - h_delta),
                        "h_max": min(1, hsv_color[0] + h_delta),
                        "s_min": max(0, hsv_color[1] - s_delta),
                        "s_max": min(1, hsv_color[1] + s_delta),
                        "v_min": max(0, hsv_color[2] - v_delta),
                        "v_max": min(1, hsv_color[2] + v_delta),
                    }
                    
                    H, S, V = img_processed[:,:,0], img_processed[:,:,1], img_processed[:,:,2]
                    tissue_mask = V < bg_v_thresh
                    new_mask = (
                        (H >= bounds["h_min"]) & (H <= bounds["h_max"]) &
                        (S >= bounds["s_min"]) & (S <= bounds["s_max"]) &
                        (V >= bounds["v_min"]) & (V <= bounds["v_max"]) &
                        tissue_mask
                    )
                    
                    if is_second and not allow_overlap and existing_mask is not None:
                        new_mask = new_mask & ~existing_mask
                    mask = mask | new_mask
                    
                except ValueError as e:
                    print(f"Warning: Could not process color {hex_color}: {str(e)}")
                    continue
                    
            return mask
        # Always use full RGB image for detection
        if isinstance(image, list):
            # If list provided, use first image as RGB source
            img_rgb = image[0] if image[0].ndim == 3 else np.stack([image[0]]*3, axis=-1)
        else:
            img_rgb = image if image.ndim == 3 else np.stack([image]*3, axis=-1)
        # # Handle input images
        # if not isinstance(image, list):
        #     # Single image case
        #     img1 = img2 = image
        # else:
        #     # Multi-image/channel case
        #     img1, img2 = image[0], image[1]
        
        # # Ensure proper dimensionality
        # if img1.ndim == 2:
        #     img1 = np.stack([img1]*3, axis=-1)
        # if img2.ndim == 2:
        #     img2 = np.stack([img2]*3, axis=-1)
        
        # Process stains
        mask1 = process_single_image(img_rgb, color1)
        mask2 = process_single_image(img_rgb, color2, is_second=True, existing_mask=mask1,allow_overlap=allow_overlap)
        if channels is not None:
            if len(channels) != 2:
                raise ValueError("channels must be a list of two channel indices")
            
            # Create channel-specific masks
            mask1 = mask1 & (img_rgb[..., channels[0]] > 0)
            mask2 = mask2 & (img_rgb[..., channels[1]] > 0) 
        # Calculate statistics
        area1, area2 = np.sum(mask1), np.sum(mask2)
        total_area = area1 + area2
        ratio1 = area1 / total_area if total_area > 0 else 0
        ratio2 = area2 / total_area if total_area > 0 else 0
        
        # Prepare visualization image
        vis_img = img_rgb
        
        return {
            "stain1_mask": mask1,
            "stain2_mask": mask2,
            "stain1_area": area1,
            "stain2_area": area2,
            "ratio_stain1": ratio1,
            "ratio_stain2": ratio2,
            "co_local_mask": mask1 & mask2,
            "image": vis_img / 255.0,
            "params": {
                "color1": color1,
                "color2": color2,
                "bg_v_thresh": bg_v_thresh,
                "h_delta": h_delta,
                "s_delta": s_delta,
                "v_delta": v_delta,
                "channel_mode": channel_mode
            }
        }
    def apply_dual_color(self, color1=["#8A4EC3", "#7E44C1"], color2=["#A6A3D2", "#B891D0"], 
                        bg_v_thresh=0.9, h_delta=0.04, s_delta=0.2, v_delta=0.2,allow_overlap=True, channels:list=None,channel_mode='rgb'):
        """
        Instance method wrapper for the static dual_color
        """ 
        if channels is not None:
            if len(channels) != 2:
                raise ValueError("channels must be a list of two channel indices") 

            channel1 = self.image_rgb[..., channels[0]]
            channel2 = self.image_rgb[..., channels[1]]
            
            # Convert single channels to 3-channel by replicating
            if channel1.ndim == 2:
                channel1 = np.stack([channel1]*3, axis=-1)
            if channel2.ndim == 2:
                channel2 = np.stack([channel2]*3, axis=-1)
            result = self.dual_color([channel1, channel2],  
                                color1=color1, 
                                color2=color2,
                                bg_v_thresh=bg_v_thresh,
                                h_delta=h_delta,
                                s_delta=s_delta,
                                v_delta=v_delta,
                                allow_overlap=allow_overlap,
                                channel_mode=channel_mode)
        else:
            result = self.dual_color(self.image_rgb,
                                color1=color1,
                                color2=color2,
                                bg_v_thresh=bg_v_thresh,
                                h_delta=h_delta,
                                s_delta=s_delta,
                                v_delta=v_delta,
                                allow_overlap=allow_overlap,
                                channel_mode=channel_mode) 
        result["image"] = self.image_rgb / 255.0  # Ensure image is available for plotting
        self.results["dual_color"] = result
        return result
    def plot_dual_color(self, figsize=(12, 8), stain1_name="Stain 1", stain2_name="Stain 2",mask_cmaps=("gray", "gray"),paint1="purple",paint2="pink",show_colocal=False):
        """
        Visualize dual color analysis results
        
        Parameters:
            figsize: Tuple (width, height) of figure size
            stain1_name: Label for first stain
            stain2_name: Label for second stain
            
        Returns:
            numpy.ndarray: Array of matplotlib Axes objects (2x2 grid)
        """
        if "dual_color" not in self.results:
            self.dual_color()
            
        res = self.results["dual_color"]
        if show_colocal:
            fig, axes = plt.subplots(3, 2, figsize=figsize)
        else:
            fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.ravel()
        
        # Raw image
        axes[0].imshow(res["image"])
        axes[0].set_title("Raw Image")
        axes[0].axis("off")
        
        # First stain mask
        axes[1].imshow(res["stain1_mask"], cmap=mask_cmaps[0])
        axes[1].set_title(stain1_name)
        axes[1].axis("off")
        
        # Second stain mask
        axes[2].imshow(res["stain2_mask"], cmap=mask_cmaps[1])
        axes[2].set_title(stain2_name)
        axes[2].axis("off")
        if show_colocal:
            # Co-local
            colocal = np.zeros_like(res["image"]) 
            c1,c2=color2rgb(paint1),color2rgb(paint2)
            co_color=(np.mean([c1[0],c2[0]],axis=0),np.mean([c1[1],c2[1]],axis=0),np.mean([c1[2],c2[2]],axis=0))
            co_color = tuple(np.mean([color1, color2], axis=0)) 

            colocal[ res["stain1_mask"]&res["stain2_mask"]] = co_color
            axes[4].imshow(colocal)
            axes[4].set_title("Colocal")
            axes[4].axis("off") 
        # Overlay
        overlay = np.zeros_like(res["image"])
        overlay[res["stain1_mask"]] = color2rgb(paint1)  # purple
        overlay[res["stain2_mask"]] = color2rgb(paint2)  # pink
        axes[3].imshow(overlay)
        axes[3].set_title("Overlay")
        axes[3].axis("off") 
        return axes
    def preview(self, channels=None, method='rgb', figsize=(12, 8), cmap='viridis',return_fig=False):
        """
        Quick preview of image channels to assess composition before analysis.

        Summary Table: Which Method to Use?

        Image Type	Best Method	When to Use	Example Use Case
        Fluorescence (DAPI/FITC/TRITC)	'rgb'	If channels are cleanly separated (e.g., DAPI in blue, FITC in green).	Immunofluorescence (IF) with clear channel separation.
        Fluorescence (Overlap)	'hsv'	If signals overlap (e.g., FITC + TRITC mixing).	Colocalization analysis.
        Brightfield (H&E Stains)	'hed'	Hematoxylin (nuclei) + Eosin (cytoplasm).	Histopathology (tissue analysis).
        Brightfield (IHC, DAB)	'hed'	DAB (brown) detection in IHC.

        Parameters:
        - channels: List of channels to preview. Options depend on method:
            - For 'rgb': ['R','G','B'] or [0,1,2]
            - For 'hed': [0,1,2] (H,E,D)
            - For 'hsv': [0,1,2] (H,S,V)
        - method: Decomposition method ('rgb', 'hed', or 'hsv')
        - figsize: Figure size
        - cmap: Colormap for single channel display
        
        Returns:
        - Matplotlib figure
        """
        if channels is None:
            channels = [0, 1, 2] if method != 'rgb' else ['R', 'G', 'B']
        
        # Convert image based on method
        if method.lower() == 'hed':
            img = color.rgb2hed(self.image_rgb)
            channel_names = ['Hematoxylin', 'Eosin', 'DAB']
        elif method.lower() == 'hsv':
            img = color.rgb2hsv(self.image_rgb)
            channel_names = ['Hue', 'Saturation', 'Value']
        else:  # default to RGB
            img = self.image_rgb
            channel_names = ['Red', 'Green', 'Blue']
            method = 'rgb'  # ensure consistent behavior
        
        fig, axes = plt.subplots(1, len(channels)+1, figsize=figsize)
        
        # Show original image
        axes[0].imshow(self.image_rgb)
        axes[0].set_title('Original')
        axes[0].axis('off')
        
        # Show each requested channel
        for i, channel in enumerate(channels, 1):
            if method == 'rgb':
                if isinstance(channel, int):
                    channel_idx = channel
                    channel_name = channel_names[channel_idx]
                else:
                    channel_map = {'R':0, 'G':1, 'B':2}
                    channel_idx = channel_map[channel.upper()]
                    channel_name = channel_names[channel_idx]
                channel_img = img[:, :, channel_idx]
            else:
                channel_idx = channel if isinstance(channel, int) else int(channel)
                channel_img = img[:, :, channel_idx]
                channel_name = channel_names[channel_idx]
            
            axes[i].imshow(channel_img, cmap=cmap)
            axes[i].set_title(f'{channel_name} Channel')
            axes[i].axis('off')
        if return_fig:
            return fig
        plt.tight_layout()
        plt.show()