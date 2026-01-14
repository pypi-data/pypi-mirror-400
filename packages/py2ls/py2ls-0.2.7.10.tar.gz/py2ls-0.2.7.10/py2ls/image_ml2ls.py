r"""
Ultimate Image Machine Learning Master Function (Optimized)
Author: DeepSeek AI
Date: 2025-05-30
Version: 2.0

新增功能:
1. 模型导出与导入 (pickle/joblib)
2. 完整的预测报告生成 (HTML格式)
3. 预测结果可视化增强
4. 支持从保存的模型直接预测
5. 更完善的配置管理


# usage: 250601
from py2ls.ips import listdir
import re

f = listdir("/Users/macjianfeng/Desktop/img_datasets/", "folder", verbose=True)


train_images = [
    *listdir(f["path"][0], "tif")["path"].tolist(),
    *listdir(f["path"][1], "tif")["path"].tolist(),
]


labels = [re.findall(r"\d+x", i)[0] for i in train_images]

# 初始化主函数
mlearner = ImageMLearner()
# 加载图像
images, filtered_labels = mlearner.load_images(train_images, labels)

# 自动模型比较
comparison_results = mlearner.auto_compare_models()
# 保存最佳模型
mlearner.save_model(mlearner.best_model, "models/best_model.joblib")
dir_test = "/Users/macjianfeng/Desktop/20250515_CDX2_LiCl_7d/HNT-34/50µM/"
f = listdir(dir_test, "tif", verbose=True)

# 使用最佳模型进行预测
test_images = f.path.tolist()

predictions = mlearner.predict(test_images, output_dir="reports")
print("Predictions:", predictions)

"""

"""
-------------------------------------------------------------------------------
This file provides a complete machine learning pipeline for image analysis with:

    Core Functionality:
        Image loading and preprocessing
        Feature extraction (HOG, LBP, CNN, etc.)
        Model training and evaluation (many classifiers/regressors)
        Model comparison and selection
        Prediction and reporting

    Key Components:
        Multiple feature extraction methods
        Wide range of ML models (traditional and deep learning)
        Model evaluation and visualization
        Report generation (HTML/Markdown)

    Use Cases:
        When you need end-to-end image classification/regression
        When you want to compare multiple models automatically
        When you need feature extraction from images
        When you want detailed reports and visualizations
        When you need GPU acceleration support

    You need a complete ML pipeline from images to predictions
    You want to compare multiple ML models automatically
    You need different feature extraction methods
    You want detailed evaluation metrics and visualizations
    You need HTML/Markdown reports of your analysis
    You want to leverage both traditional ML and deep learning
-------------------------------------------------------------------------------
"""


usage_str="""
-------------如果要使用tensorflow的话, 一定要最先调用--------
    import tensorflow as tf
    print("Eager execution enabled:", tf.executing_eagerly())
    tf.config.set_visible_devices([], "GPU")
-------------如果要使用tensorflow的话, 一定要最先调用--------
"""
print(usage_str)
from .ips import has_gpu #set_computing_device 
from .ImageLoader import ImageLoader
import os
import json
import yaml
import pickle
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
from functools import partial
from collections import defaultdict
from typing import Union, Dict, List, Tuple, Optional, Callable, Any
from IPython.display import HTML, display
from tqdm import tqdm
import gc
import logging

# 图像处理库
import cv2
from skimage import io, color, exposure
from skimage import transform, feature, filters, morphology, segmentation
from PIL import Image
# 机器学习库
from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    confusion_matrix,
    mean_squared_error,
    r2_score,
    classification_report,
)

# 分类模型 
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    ExtraTreesClassifier,
    ExtraTreesRegressor,
    HistGradientBoostingRegressor,
    BaggingClassifier,
    BaggingRegressor,
    AdaBoostClassifier,
    AdaBoostRegressor,
)
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor,StackingClassifier,StackingRegressor
from sklearn.svm import SVC 

from sklearn.linear_model import (
    LogisticRegression,ElasticNet,ElasticNetCV,
    LinearRegression,Lasso,RidgeClassifierCV,Perceptron,SGDClassifier,
    RidgeCV,Ridge,TheilSenRegressor,HuberRegressor,PoissonRegressor,Lars, LassoLars, BayesianRidge,
    GammaRegressor, TweedieRegressor, LassoCV, LassoLarsCV, LarsCV,
    OrthogonalMatchingPursuit, OrthogonalMatchingPursuitCV, PassiveAggressiveRegressor
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
import xgboost as xgb 
from sklearn.naive_bayes import GaussianNB,BernoulliNB
from sklearn.discriminant_analysis import (
    LinearDiscriminantAnalysis,
    QuadraticDiscriminantAnalysis,
)
from sklearn.naive_bayes import GaussianNB, BernoulliNB
import lightgbm as lgb
import catboost as cb
from sklearn.neural_network import MLPClassifier, MLPRegressor
# 回归模型
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    AdaBoostRegressor,
    ExtraTreesRegressor,
)

from sklearn.linear_model import (
    LassoCV,
    LogisticRegression,
    LinearRegression,
    Lasso,
    Ridge,
    ElasticNet,
)
# 深度学习特征提取
# try:
#     from tensorflow.keras.utils import to_categorical

# except Exception as e:
#     print("Error importing tensorflow.keras.utils or sklearn.utils.class_weight:", e)
    
# try:
    
#     from tensorflow.keras.applications import (
#         VGG16,
#         VGG19,
#         ResNet50,
#         InceptionV3,
#         MobileNet,
#         DenseNet121,
#         EfficientNetB0,
#     )
#     from tensorflow.keras.models import Model
#     from tensorflow.keras.preprocessing import image
#     from tensorflow.keras.applications.imagenet_utils import preprocess_input

#     DL_ENABLED = True
# except ImportError:
#     DL_ENABLED = False
# Conditional imports for deep learning
DL_ENABLED = False
try:
    import tensorflow as tf
    from sklearn.utils.class_weight import compute_class_weight
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    from tensorflow.keras.utils import to_categorical
    from tensorflow.keras.applications import (
        VGG16, VGG19, ResNet50, InceptionV3, 
        MobileNet, DenseNet121, EfficientNetB0
    )
    from tensorflow.keras.models import Model
    from tensorflow.keras.preprocessing import image
    from tensorflow.keras.applications.imagenet_utils import preprocess_input
    from tensorflow.keras.callbacks import (
        EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
    )
    from concurrent.futures import ThreadPoolExecutor
    from tensorflow.keras.mixed_precision import set_global_policy
    from tensorflow.keras.optimizers import Adam
    DL_ENABLED = True
except ImportError:
    pass
#====check gpu available====
# set_computing_device()
# Global configuration

DEFAULT_CONFIG = {
    "preprocessing": {
        "resize": (128, 128),
        "remove_background": True,
        "denoise": "median",
        "normalize": True,
        "hist_equalize": False,
        "chunk_size": 100,
        "augmentation": {
            "rotation_range": 10,
            "width_shift_range": 0.1,
            "height_shift_range": 0.1,
            "shear_range": 0.05,
            "zoom_range": 0.1,
            "horizontal_flip": True
        }
    },
    "feature_extraction": {
        "method": "hog",
        "cnn_model": "resnet50" if DL_ENABLED else None,
        "hog_params": {"orientations": 8, "pixels_per_cell": (16, 16), "cells_per_block": (1, 1)},
        "lbp_params": {"P": 8, "R": 1, "method": "uniform"}
    },
    "cnn": {
        "conv_layers": [(16, 3, 1), (32, 3, 1)],
        "dense_layers": [32],
        "use_batchnorm": True,
        "use_dropout": False,
        "dropout_rate": 0.2,
        "pooling": "max",
        "learning_rate": 0.001,
        "optimizer": "adam"
    },
    "model": {"name": "cnn", "params": {}},
    "auto_comparison": True,
    "test_size": 0.2,
    "random_state": 1,
    "n_cpu": max(os.cpu_count() - 2, 4),
    "visualization": {
        "enable": True,
        "confusion_matrix": True,
        "feature_space": True,
        "sample_images": 2,
        "cmap": "viridis"
    },
    "report": {"format": "html", "include_visuals": True}
} 
def build_cnn_model(
    input_shape: tuple,
    num_classes: int,
    *,
    # Architecture configuration
    conv_layers: list = None,
    dense_layers: list = None,
    use_batchnorm: bool = True,
    use_dropout: bool = False,
    dropout_rate: float = 0.2,
    pooling: str = "max",
    # Training configuration
    learning_rate: float = 0.001,
    optimizer: str = "adam",
    # Logging/utility
    verbose: bool = True,
    logger: logging.Logger = None
) -> tf.keras.Model:
    """
    Flexible CNN builder with customizable architecture.
    
    Args:
        input_shape: Tuple (height, width, channels) or (height, width)
        num_classes: Number of output classes
        conv_layers: List of tuples (filters, kernel_size, stride) for conv layers
                     Default: [(16, 3, 1), (32, 3, 1)]
        dense_layers: List of units for dense layers. Default: [32]
        use_batchnorm: Whether to use batch normalization
        use_dropout: Whether to use dropout
        dropout_rate: Dropout rate if use_dropout=True
        pooling: "max" or "avg" pooling
        learning_rate: Learning rate for optimizer
        optimizer: "adam", "sgd", or "rmsprop"
        verbose: Whether to print model info
        logger: Custom logger instance
        
    Returns:
        Compiled Keras model
    """
    # Initialize logging
    logger = logger or logging.getLogger("cnn_builder")
    if verbose and not logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    
    start_time = time.time()
    
    # Validate and normalize input shape
    if len(input_shape) == 2:
        input_shape = (*input_shape, 1)
    elif len(input_shape) != 3:
        raise ValueError("input_shape must be (h,w) or (h,w,c)")
    
    # Set default architecture if not provided
    conv_layers = conv_layers or [(16, 3, 1), (32, 3, 1)]
    dense_layers = dense_layers or [32]
    
    # Configure output layer
    if num_classes == 1:  # Regression
        final_config = {"units": 1, "activation": "linear", "loss": "mse", "metrics": ["mae"]}
    elif num_classes == 2:  # Binary classification
        final_config = {"units": 1, "activation": "sigmoid", "loss": "binary_crossentropy", "metrics": ["accuracy"]}
    else:  # Multi-class
        final_config = {"units": num_classes, "activation": "softmax", "loss": "sparse_categorical_crossentropy", "metrics": ["accuracy"]}
    
    # Build model
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.InputLayer(input_shape=input_shape))
    
    # Add convolutional blocks
    for i, (filters, kernel_size, stride) in enumerate(conv_layers):
        model.add(tf.keras.layers.Conv2D(
            filters=filters,
            kernel_size=kernel_size,
            strides=stride,
            padding="same",
            name=f"conv_{i}"
        ))
        
        if use_batchnorm:
            model.add(tf.keras.layers.BatchNormalization(name=f"bn_{i}"))
        
        model.add(tf.keras.layers.ReLU(name=f"relu_{i}"))
        
        # Add pooling every other conv layer
        if i % 2 == 1:
            if pooling == "max":
                model.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2), name=f"pool_{i}"))
            else:
                model.add(tf.keras.layers.AveragePooling2D(pool_size=(2, 2), name=f"pool_{i}"))
        
        if use_dropout:
            model.add(tf.keras.layers.Dropout(dropout_rate, name=f"dropout_{i}"))
    
    # Transition to dense layers
    model.add(tf.keras.layers.Flatten())
    
    # Add dense layers
    for i, units in enumerate(dense_layers):
        model.add(tf.keras.layers.Dense(units, activation="relu", name=f"dense_{i}"))
        if use_batchnorm:
            model.add(tf.keras.layers.BatchNormalization(name=f"bn_dense_{i}"))
        if use_dropout:
            model.add(tf.keras.layers.Dropout(dropout_rate, name=f"dropout_dense_{i}"))
    
    # Output layer
    model.add(tf.keras.layers.Dense(
        units=final_config["units"],
        activation=final_config["activation"],
        name="output"
    ))
    
    # Configure optimizer
    optimizers = {
        "adam": tf.keras.optimizers.Adam(learning_rate=learning_rate),
        "sgd": tf.keras.optimizers.SGD(learning_rate=learning_rate, momentum=0.9),
        "rmsprop": tf.keras.optimizers.RMSprop(learning_rate=learning_rate)
    }
    
    # Compile model
    model.compile(
        optimizer=optimizers.get(optimizer, optimizers["adam"]),
        loss=final_config["loss"],
        metrics=final_config["metrics"]
    )
    
    # Logging
    if verbose:
        logger.info(f"Built CNN with:")
        logger.info(f"- {len(conv_layers)} conv layers")
        logger.info(f"- {len(dense_layers)} dense layers")
        logger.info(f"- BatchNorm: {use_batchnorm}")
        logger.info(f"- Dropout: {use_dropout} ({dropout_rate if use_dropout else 'N/A'})")
        logger.info(f"- Optimizer: {optimizer} (lr={learning_rate})")
        logger.info(f"Model built in {time.time()-start_time:.2f}s\n")
        model.summary(print_fn=logger.info)
    
    return model



class ImageMLearner:
    """
    通用图像机器学习主函数 (优化版)

    参数:
    cfg (Union[dict, str]): 配置字典或配置文件路径 (JSON/YAML)
    verbose (bool): 是否显示详细输出
    """

    def __init__(self, cfg: Union[dict, str] = None, verbose: bool = True):
        self.verbose = verbose
        self.dl_enabled = DL_ENABLED
        self.cfg = self._load_cfg(cfg)
        self.models = {}
        self.feature_extractors = {}
        self.preprocessors = {}
        self.chunk_size = self.cfg["preprocessing"].get("chunk_size", 128)
        self.n_cpu=self.cfg.get("n_cpu", max(os.cpu_count(), 8))
        self._register_default_components()

        # 状态跟踪
        self.images, self.image_input, self.labels = [], [], []
        self.X_train, self.y_train = None, None
        self.X_test, self.y_test = None, None
        self.features = None
        self.model_performance = {}
        self.best_model = None
        self.label_encoder = None
        self.task_type = None
        self.class_names = None
        
        # Hardware optimization
        self.has_gpu = has_gpu(verbose=self.verbose)
        self.cfg_hash = hash(json.dumps(self.cfg["preprocessing"], sort_keys=True))

        if self.has_gpu and DL_ENABLED:
            self._configure_gpu()

        # Initialize ImageLoader
        self.image_loader = ImageLoader(
            target_size=self.cfg["preprocessing"].get("resize", (128, 128)),
            grayscale=self.cfg["preprocessing"].get("to_grayscale", True),
            n_jobs=self.cfg.get("n_cpu", max(os.cpu_count() - 2, 4)),
            verbose=verbose,
            scaler="normalize" if self.cfg["preprocessing"].get("normalize", True) else "raw",
            chunk_size=self.cfg["preprocessing"].get("chunk_size", 100)
        )
        # 初始化CNN模型缓存
        self._cnn_models = {} 
        if cfg is not None: 
            self.clear_cache()
        # If DL is disabled but config requests CNN, fall back to HOG
        if not self.dl_enabled and self.cfg["feature_extraction"].get("method") == "cnn":
            self.cfg["feature_extraction"]["method"] = "hog"
            if self.verbose:
                print("CNN requested but DL not available. Falling back to HOG.")
        if self.verbose:
            print(f"init: ImageMLearner initialized with cfg: {self.cfg}")
    def _configure_gpu(self):
        """Configure GPU settings for optimal performance"""
        try:
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                set_global_policy('mixed_float16')
                if self.verbose:
                    print("GPU configured with mixed precision")
        except Exception as e:
            print(f"Error configuring GPU: {str(e)}")
    def _load_cfg(self, cfg: Union[dict, str]) -> dict:
        """加载配置文件"""
        default_cfg = {
            "preprocessing": {
                "resize": (128, 128),
                "remove_background": True,
                "denoise": "median",
                "normalize": True,
                "hist_equalize": False,
                "chunk_size": 100,
            },
            "feature_extraction": {
                "method": "hog",
                "cnn_model": "resnet50" if self.dl_enabled else None,
                "hog_params": {
                    "orientations": 8,
                    "pixels_per_cell": (16, 16),
                    "cells_per_block": (1, 1),
                },
                "lbp_params": {"P": 8, "R": 1, "method": "uniform"},
            },
            "model": {"name": "random_forest", "params": {}},
            "auto_comparison": True,
            "test_size": 0.2,
            "random_state": 1,
            "n_cpu":max(os.cpu_count(), 8),
            "visualization": {
                "enable": True,
                "confusion_matrix": True,
                "feature_space": True,
                "sample_images": 2,
                "cmap": "viridis",
            },
            "report": {"format": "html", "include_visuals": True},  # html/md
        }

        if cfg is None:
            return default_cfg

        if isinstance(cfg, str):
            if cfg.endswith(".json"):
                with open(cfg, "r") as f:
                    cfg = json.load(f)
            elif cfg.endswith((".yaml", ".yml")):
                with open(cfg, "r") as f:
                    cfg = yaml.safe_load(f)
            else:
                raise ValueError("Unsupported cfg file format. Use JSON or YAML.")

        # 深度合并配置  
        def deep_merge(target, source):
            for key, value in source.items():
                if (key in target) and isinstance(target[key], dict) and isinstance(value, dict):
                    deep_merge(target[key], value)
                else:
                    target[key] = value
            return target
        
        config = DEFAULT_CONFIG.copy()
        return deep_merge(config, cfg)
    def _register_default_components(self):
        """注册默认预处理、特征提取和模型"""
        # 注册预处理方法
        self.register_preprocessor("grabcut", self._grabcut_background_removal)
        self.register_preprocessor("kmeans", self._kmeans_background_removal)
        self.register_preprocessor("morphology", self._morphology_background_removal)

        # 注册特征提取方法
        self.register_feature_extractor("pixels", self._extract_raw_pixels)
        self.register_feature_extractor("hog", self._extract_hog)
        self.register_feature_extractor("lbp", self._extract_lbp)
        self.register_feature_extractor("color_hist", self._extract_color_histogram)

        # if self.dl_enabled:
        #     self.register_feature_extractor("cnn", self._extract_cnn_features)

        # 注册模型
        models = {
            # 分类模型
            "logistic_regression": LogisticRegression,
            "svm": SVC,
            "knn": KNeighborsClassifier,
            "decision_tree": DecisionTreeClassifier,
            "random_forest": RandomForestClassifier,
            "gradient_boosting": GradientBoostingClassifier,
            "ada_boost": AdaBoostClassifier,
            "naive_bayes": GaussianNB,
            "lda": LinearDiscriminantAnalysis,
            "qda": QuadraticDiscriminantAnalysis,
            "extra_trees": ExtraTreesClassifier,
            # added
            "lasso_logistic": LogisticRegression(penalty='l1', solver='saga'),
            "ridge_classifier": RidgeClassifierCV(),
            "elastic_net_cls": ElasticNet(),
            "xgb": xgb.XGBClassifier(), #if XGB_ENABLED else None,
            "lightgbm": lgb.LGBMClassifier(), #if LGBM_ENABLED else None,
            "catboost": cb.CatBoostClassifier(verbose=0), #if CATBOOST_ENABLED else None,
            "bagging": BaggingClassifier(),
            "mlp": MLPClassifier(max_iter=500),
            "quadratic_discriminant": QuadraticDiscriminantAnalysis(),
            "bernoulli_nb": BernoulliNB(),
            "sgd": SGDClassifier(),
            # 回归模型
            "linear_regression": LinearRegression,
            "ridge": Ridge,
            "lasso": Lasso,
            "elastic_net": ElasticNet,
            "svr": SVR,
            "knn_regressor": KNeighborsRegressor,
            "decision_tree_reg": DecisionTreeRegressor,
            "random_forest_reg": RandomForestRegressor,
            "gradient_boosting_reg": GradientBoostingRegressor,
            "ada_boost_reg": AdaBoostRegressor,
            "extra_trees_reg": ExtraTreesRegressor,
            "cnn":self._build_cnn_model,
            # added
            "lasso_cv": LassoCV(),
            "elastic_net_cv": ElasticNetCV(),
            "xgb_reg": xgb.XGBRegressor(), #if XGB_ENABLED else None,
            "lightgbm_reg": lgb.LGBMRegressor(), #if LGBM_ENABLED else None,
            "catboost_reg": cb.CatBoostRegressor(verbose=0), #if CATBOOST_ENABLED else None,
            "bagging_reg": BaggingRegressor(),
            "mlp_reg": MLPRegressor(max_iter=500),
            "theil_sen": TheilSenRegressor(),
            "huber": HuberRegressor(),
            "poisson": PoissonRegressor(),
        }

        for name, model in models.items():
            self.register_model(name, model)

    def register_preprocessor(self, name: str, func: Callable):
        """注册新的预处理方法"""
        self.preprocessors[name] = func
        # if self.verbose:
        #     print(f"Registered preprocessor: {name}")

    def register_feature_extractor(self, name: str, func: Callable):
        """注册新的特征提取方法"""
        self.feature_extractors[name] = func
        # if self.verbose:
        #     print(f"Registered feature extractor: {name}")

    def register_model(self, name: str, model_class: BaseEstimator):
        """注册新的机器学习模型"""
        self.models[name] = model_class
        # if self.verbose:
        #     print(f"Registered model: {name}")

    def load_images(self, image_paths: List[str], labels: List = None):
        """
        加载图像数据集

        参数:
        image_paths: Can be:
            - List of file paths (e.g., ["img1.jpg", "img2.png"])
            - NumPy array of shape (n_samples, height, width[, channels])
            - List of NumPy arrays (each shape: (height, width[, channels]))
        labels: 对应的标签列表 (可选)
        """
        self._reset_state()
        if self.verbose:
            print(f"Loading {len(image_paths)} images...") 
        # return images, filtered_labels
        # Case 1: Input is already arrays
        if not isinstance(image_paths[0], str):
            self.images = list(image_paths)
            self.image_input = None
            if labels is not None:
                self._process_labels(labels)
            return self.images, self.labels
        
        # Case 2: Input is file paths - use ImageLoader
        df = pd.DataFrame({"path": image_paths})
        if labels is not None:
            df["label"] = labels
            
        # Process images using ImageLoader
        result = self.image_loader.process(
            data=df,
            x_col="path",
            y_col="label" if labels is not None else None,
            encoder="label" if labels is not None else None,
            output="array"
        )
        
        if labels is not None:
            images, processed_labels = result
            self.labels = processed_labels
        else:
            images = result
            
        self.images = list(images)
        self.image_input = image_paths
        
        # Detect task type and process labels
        if labels is not None:
            self._process_labels(labels)
            
        if self.verbose:
            print(f"Loaded {len(self.images)} images, {len(self.labels) if labels is not None else 0} labels")
            
        return self.images, self.labels if labels is not None else None


    def _process_labels(self, labels: List):
        """Internal method to process labels and detect task type"""
        labels = np.array(labels).flatten()
        
        # Detect task type
        unique_labels = set(labels)
        if all(isinstance(label, (int, float)) for label in labels):
            self.task_type = "regression"
            if self.verbose:
                print("Detected regression task")
        else:
            self.task_type = "classification"
            self.class_names = sorted(unique_labels)
            self.label_encoder = LabelEncoder()
            self.labels = self.label_encoder.fit_transform(labels)
            if self.verbose:
                print(f"Detected classification task with {len(unique_labels)} classes")
    def preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """应用配置的预处理步骤到单个图像"""
        cfg = self.cfg["preprocessing"]

        # Convert to 3-channel BGR if needed
        # if img.ndim == 2:  # Grayscale
        #     img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        # elif img.ndim == 3 and img.shape[2] == 4:  # RGBA
        #     img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        # elif img.ndim == 3 and img.shape[2] == 3:  # RGB
        #     img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

        # Ensure uint8 (0-255) for OpenCV operations
        if img.dtype != np.uint8:
            img = (img * 255).astype(np.uint8) if img.max() <= 1.0 else img.astype(np.uint8)
            # or: img = img.astype(np.uint8)  # If already [0,255]

        # 调整大小 # Resize with OpenCV for performance
        if cfg.get("resize") and img.shape[:2] != cfg["resize"]:
            img = cv2.resize(img, tuple(cfg["resize"][::-1]), interpolation=cv2.INTER_AREA)

        # 去背景 
        if cfg.get("remove_background"):
            method = cfg.get("bg_method", "grabcut")
            if method in self.preprocessors:
                img = self.preprocessors[method](img)
        # 转换为灰度（如果需要） 
        if cfg.get("to_grayscale", True) and img.ndim == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # 降噪
        denoise_method = cfg.get("denoise")
        if denoise_method:
            if denoise_method == "median":
                img = cv2.medianBlur(img, 3)
            elif denoise_method == "gaussian":
                img = cv2.GaussianBlur(img, (5, 5), 0)
            elif denoise_method == "bilateral":
                img = cv2.bilateralFilter(img, 9, 75, 75)

        # 直方图均衡化
        if cfg.get("hist_equalize", False):
            if img.ndim == 3:
                img_yuv = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
                img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
                img = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2RGB)
            else:
                img = exposure.equalize_hist(img)

        # 标准化
        if cfg.get("normalize", True):
            img = img.astype(np.float32) / 255.0

        return img

    def _grabcut_background_removal(self, img: np.ndarray) -> np.ndarray:
        """使用GrabCut算法去除背景"""
        mask = np.zeros(img.shape[:2], np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)

        # 定义ROI（整个图像）
        h, w = img.shape[:2]
        margin=10
        rect = (
            max(0, margin),
            max(0, margin),
            max(1, w - 2 * margin),
            max(1, h - 2 * margin)
        )

        cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)

        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
        result = img * mask2[:, :, np.newaxis]

        # 清除边界
        result = segmentation.clear_border(result)

        return result

    def _kmeans_background_removal(self, img: np.ndarray) -> np.ndarray:
        """使用K-means聚类去除背景"""
        if img.ndim == 3:
            Z = img.reshape((-1, 3))
        else:
            Z = img.reshape((-1, 1))

        Z = np.float32(Z)

        # K-means参数
        K = 2
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, label, center = cv2.kmeans(
            Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
        )

        # 找到背景（假设背景是最大的簇）
        counts = np.bincount(label.flatten())
        bg_label = np.argmax(counts)

        # 创建掩码
        mask = np.uint8(label == bg_label)
        mask = mask.reshape(img.shape[:2])

        # 形态学操作清理掩码
        mask = morphology.binary_erosion(mask, morphology.disk(5))
        mask = morphology.binary_dilation(mask, morphology.disk(5))

        # 应用掩码
        if img.ndim == 3:
            result = img.copy()
            result[mask == 1] = 0
        else:
            result = img * (1 - mask)

        return result

    def _morphology_background_removal(self, img: np.ndarray) -> np.ndarray:
        """使用形态学操作去除背景"""
        if img.ndim == 3:
            gray = color.rgb2gray(img)
        else:
            gray = img

        # 阈值处理
        thresh = gray > 0.5

        # 形态学操作
        cleaned = morphology.binary_erosion(thresh, morphology.disk(5))
        cleaned = morphology.binary_dilation(cleaned, morphology.disk(5))

        # 应用掩码
        if img.ndim == 3:
            result = img.copy()
            result[~cleaned] = 0
        else:
            result = img * cleaned

        return result

    def extract_features(self, images: List[np.ndarray] = None) -> np.ndarray:
        """从图像列表中提取特征"""
        import concurrent.futures
        if images is None:
            images = self.images

        if not images:
            raise ValueError("No images available for feature extraction")

        method = self.cfg["feature_extraction"]["method"]
        extractor = self.feature_extractors.get(method)

        if not extractor:
            raise ValueError(f"Unsupported feature extraction method: {method}")

        if self.verbose:
            print(f"Extracting features using {method} method...")
        # Use cached features if available
        cache_file = f"features_cache_{self.cfg_hash}.npy"
        if os.path.exists(cache_file):
            if self.verbose:
                print("Loading features from cache")
            self.features = np.load(cache_file, allow_pickle=True)
            return self.features
        start_time = time.time()
        # Use cached preprocessing if available
        preprocessed_images = self._cache_preprocessed(images)
        
        # Process features
        with ThreadPoolExecutor(max_workers=self.n_cpu) as executor:
            features = list(tqdm(
                executor.map(extractor, preprocessed_images),
                total=len(images),
                desc="Extracting features",
                disable=not self.verbose
            )) 
        self.features = np.array(features)
        # Save to cache
        np.save(cache_file, self.features)

        if self.verbose:
            print(f"Features extracted in {time.time()-start_time:.2f}s")
            print(f"Feature matrix shape: {self.features.shape}")

        return self.features

    def _cache_preprocessed(self, images):
        """Cache preprocessed images to disk for faster subsequent runs"""
        import concurrent.futures
        cache_file = f"preprocessed_cache_{self.cfg_hash}.npy"
        if os.path.exists(cache_file):
            if self.verbose:
                print("Loading preprocessed images from cache")
            return np.load(cache_file, allow_pickle=True)
        
        if self.verbose:
            print(f"Preprocessing {len(images)} images...")
        start_time = time.time()
        processed = []
        
        # Process in chunks
        for i in tqdm(range(0, len(images), self.chunk_size),
                         desc="Preprocessing",
                         disable=not self.verbose):
            chunk = images[i:i+self.chunk_size]
            with ThreadPoolExecutor(max_workers=self.n_cpu) as executor:
                processed_chunk = list(executor.map(self.preprocess_image, chunk))
            processed.extend(processed_chunk)
        
        # Save to cache
        np.save(cache_file, processed)
        
        if self.verbose:
            print(f"Preprocessed in {time.time()-start_time:.2f}s")
        
        return processed
 
    def clear_cache(self, pattern: str = "*.npy") -> int:
        """Clear cached files with pattern matching"""
        import glob
        deleted = 0
        for f in glob.glob(pattern):
            try:
                os.remove(f)
                deleted += 1
                if self.verbose:
                    print(f"Removed {f}")
            except Exception as e:
                if self.verbose:
                    print(f"Failed to remove {f}: {str(e)}")
        return deleted

    def _extract_raw_pixels(self, img: np.ndarray) -> np.ndarray:
        """提取原始像素特征"""
        return img.flatten()
    def _reset_state(self):
        """Reset internal state to free memory"""
        self.features = None
        self.X_train, self.y_train = None, None
        self.X_test, self.y_test = None, None
        self.clear_cache("preprocessed_cache_*.npy")
        self.clear_cache("features_cache_*.npy")
        self.clear_cache("cnn_preprocessed_*.npy")
        gc.collect()
        
        if DL_ENABLED:
            tf.keras.backend.clear_session()
    def _extract_hog(self, img: np.ndarray) -> np.ndarray:
        """提取HOG特征"""
        params = self.cfg["feature_extraction"]["hog_params"]

        if img.ndim == 3:
            img = color.rgb2gray(img)

        return feature.hog(
            img,
            orientations=params["orientations"],
            pixels_per_cell=params["pixels_per_cell"],
            cells_per_block=params["cells_per_block"],
            feature_vector=True,
        )

    def _extract_lbp(self, img: np.ndarray) -> np.ndarray:
        """提取LBP特征"""
        params = self.cfg["feature_extraction"]["lbp_params"]

        if img.ndim == 3:
            img = color.rgb2gray(img)

        lbp = feature.local_binary_pattern(
            img, P=params["P"], R=params["R"], method=params["method"]
        )

        # 计算直方图
        n_bins = int(lbp.max() + 1)
        hist, _ = np.histogram(lbp, bins=n_bins, density=True)

        return hist

    def _extract_color_histogram(self, img: np.ndarray) -> np.ndarray:
        """提取颜色直方图特征"""
        if img.ndim == 2:  # 灰度图像
            hist = cv2.calcHist([img], [0], None, [256], [0, 256])
            return hist.flatten()

        # 彩色图像
        channels = cv2.split(img)
        hist_features = []

        for i, channel in enumerate(channels):
            hist = cv2.calcHist([channel], [0], None, [256], [0, 256])
            hist_features.extend(hist.flatten())

        return np.array(hist_features)

    def _extract_cnn_features(self, img: np.ndarray) -> np.ndarray:
        """使用预训练CNN提取特征"""
        if not self.dl_enabled:
            raise ImportError("Deep learning libraries not available")
        model_name = self.cfg["feature_extraction"]["cnn_model"].lower()
        models = {
            "vgg16": VGG16,
            "vgg19": VGG19,
            "resnet50": ResNet50,
            "inceptionv3": InceptionV3,
            "mobilenet": MobileNet,
            "densenet121": DenseNet121,
            "efficientnetb0": EfficientNetB0,
        }

        if model_name not in models:
            raise ValueError(f"Unsupported CNN model: {model_name}")

        # 加载模型
        if model_name not in self._cnn_models:
            base_model = models[model_name](
                weights="imagenet", include_top=False, pooling="avg"
            )
            self._cnn_models[model_name] = Model(
                inputs=base_model.input, outputs=base_model.output
            )

        model = self._cnn_models[model_name]

        # 预处理图像
        if img.ndim == 2:
            img = np.stack((img,) * 3, axis=-1)

        img = transform.resize(img, (224, 224))
        img = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)

        # 提取特征
        features = model.predict(img)
        return features.flatten()
 

    def preprocess_image_for_cnn(self, img: np.ndarray) -> np.ndarray:
        """
        Ultimate optimized CNN preprocessing:
        - Minimal operations
        - Vectorized normalization
        - Efficient resizing
        - Memory-friendly processing
        """
        target_size = self.cfg["preprocessing"].get("resize", (32, 32))
        
        # Convert PIL Image if needed
        if isinstance(img, Image.Image):
            img = np.array(img)
            
        if img.ndim == 2:  # Grayscale
            img = np.stack((img,)*3, axis=-1)  # Convert to 3-channel
        elif img.shape[2] == 4:  # RGBA
            img = img[..., :3]  # Remove alpha
        # Ensure we have 3 channels
        if img.shape[2] == 1:
            img = np.concatenate([img]*3, axis=-1)
        # Handle different channel cases 
        if img.ndim == 2:  # Grayscale to RGB
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.ndim == 3 and img.shape[2] == 4:  # RGBA
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        elif img.ndim == 3 and img.shape[2] == 3:  # BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Efficient resizing - use OpenCV for fastest performance
        if img.shape[:2] != target_size:
            img = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
        
        # Resize
        if img.shape[:2] != target_size:
            img = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
        
        # Normalization
        img = img.astype(np.float32) / 255.0
        return img
    def _build_cnn_model(self, input_shape=None, num_classes=None):
        """Build CNN model with proper instance access"""
        if input_shape is None:
            input_shape = self.cfg["preprocessing"]["resize"]
        
        if num_classes is None:
            if hasattr(self, 'labels') and self.labels is not None:
                num_classes = len(np.unique(self.labels)) if self.task_type == "classification" else 1
            else:
                num_classes = 2  # Default fallback
        
        return build_cnn_model(
            input_shape=input_shape,
            num_classes=num_classes,
            **self.cfg["cnn"]
        )
 
    def _train_cnn_model(self, model_builder: Callable, params: dict):
        """Optimized CNN training pipeline with fixes for hanging issue"""
        if not self.dl_enabled:
            raise ImportError("Deep learning libraries not available")
        
        tf.config.optimizer.set_jit(True)  # Enable XLA compilation
        tf.keras.backend.clear_session()  # Clean any previous models
        # Configure GPU settings
        if self.has_gpu:
            set_global_policy('mixed_float16')
        
        # Preprocessing
        target_size = self.cfg["preprocessing"].get("resize", (224, 224))
        X = self._preprocess_for_cnn(self.images,target_size)
        y = np.array(self.labels).flatten()
        
        # Debug: Check data shapes and types
        if self.verbose:
            print(f"X shape: {X.shape}, dtype: {X.dtype}")
            print(f"y shape: {y.shape}, dtype: {y.dtype}")
            print(f"Unique labels: {np.unique(y)}")
        
        # Split dataset
        stratify = y if self.task_type == "classification" else None
        X_train, X_val, y_train, y_val = train_test_split(
            X, y,
            test_size=self.cfg["test_size"],
            random_state=self.cfg["random_state"],
            stratify=stratify
        )
        
        # Fix: Ensure data types match
        X_train = X_train.astype(np.float32)
        X_val = X_val.astype(np.float32)
        
        # Data augmentation
        datagen = self._create_datagen(params)
        
        # Build model
        input_shape = X.shape[1:]
        num_classes = len(np.unique(y)) if self.task_type == "classification" else 1
        model = model_builder(input_shape, num_classes)
        
        # # Debug: Print model summary
        # if self.verbose:
        #     model.summary()
        
        # Training configuration
        batch_size = params.get('batch_size', 32)
        # FIX: Use explicit DataGenerator instead of direct arrays
        train_datagen = ImageDataGenerator()
        val_datagen = ImageDataGenerator()
        
        train_generator = train_datagen.flow(
            X_train, y_train,
            batch_size=batch_size,
            shuffle=True
        )
        
        val_generator = val_datagen.flow(
            X_val, y_val,
            batch_size=batch_size,
            shuffle=False
        )
        # Calculate steps
        steps_per_epoch = max(1, len(X_train) // batch_size)
        validation_steps = max(1, len(X_val) // batch_size)
        
        # Callbacks
        callbacks = self._create_callbacks(params)
    
        # FIX: Add explicit print before training
        if self.verbose:
            print(f"\nStarting training with:")
            print(f"  Train samples: {len(X_train)}")
            print(f"  Validation samples: {len(X_val)}")
            print(f"  Batch size: {batch_size}")
            print(f"  Steps per epoch: {steps_per_epoch}")
            print(f"  Validation steps: {validation_steps}")
            print("Compiling model...")
        
        # FIX: Test model with a single batch
        try:
            if self.verbose:
                print("Testing with one batch...")
            test_batch = next(train_generator)
            model.predict(test_batch[0], verbose=0)
            if self.verbose:
                print("1st batch test successful")
        except Exception as e:
            print(f"❌ Error in single batch test: {str(e)}")
            raise
        # Train model
        start_time = time.time()
        
        # FIX: Use explicit generators
        history = model.fit(
            train_generator,
            steps_per_epoch=steps_per_epoch,
            epochs=params.get('epochs', 50),
            validation_data=val_generator,
            validation_steps=validation_steps,
            callbacks=callbacks,
            verbose=1 if self.verbose else 0  # Use 1 for per-batch updates
        )
        
        # Collect metrics
        train_time = time.time() - start_time
        best_epoch = np.argmin(history.history['val_loss']) + 1
        metrics = {
            'train_time': train_time,
            'best_epoch': best_epoch,
            'val_loss': history.history['val_loss'][best_epoch-1],
            'best_val_loss': min(history.history['val_loss'])
        }
        
        if self.task_type == 'classification':
            metrics['val_accuracy'] = history.history['val_accuracy'][best_epoch-1]
            metrics['best_val_accuracy'] = max(history.history['val_accuracy'])
        
        # Save results
        self.model_performance["cnn"] = {
            "model": model,
            "metrics": metrics,
            "history": history.history,
            "params": params
        }
        self._update_best_model(model, metrics)
        # Cleanup
        tf.keras.backend.clear_session()
        gc.collect()
        
        if self.verbose:
            print(f"Training completed in {train_time:.2f}s")
            print(f"Best validation accuracy: {metrics.get('best_val_accuracy', metrics['best_val_loss']):.4f}")
        
        return model, metrics
 

    def _create_datagen(self, params: dict):
        """Create data generator with augmentation"""
        use_augmentation = params.get('use_augmentation', False)
        
        # Fix: Only apply augmentation if explicitly enabled
        if use_augmentation:
            aug_cfg = self.cfg["preprocessing"].get("augmentation", {})
            datagen = ImageDataGenerator(
                rotation_range=aug_cfg.get("rotation_range", 10),
                width_shift_range=aug_cfg.get("width_shift_range", 0.1),
                height_shift_range=aug_cfg.get("height_shift_range", 0.1),
                shear_range=aug_cfg.get("shear_range", 0.05),
                zoom_range=aug_cfg.get("zoom_range", 0.1),
                horizontal_flip=aug_cfg.get("horizontal_flip", True),
                fill_mode='reflect'
            )
        else:
            # Fix: Use simple generator without augmentation
            datagen = ImageDataGenerator()
        
        return datagen
    def _preprocess_for_cnn(self, images, target_size: Tuple[int, int]) -> np.ndarray:
        """Efficient CNN preprocessing with parallel processing"""
        cache_file = f"cnn_preprocessed_{self.cfg_hash}.npy"
        
        if os.path.exists(cache_file):
            if self.verbose:
                print("Loading CNN preprocessed images from cache")
            return np.load(cache_file)
        
        if self.verbose:
            print("Preprocessing images for CNN...")
        
        start_time = time.time()
        processed = []
        
        # Process in chunks
        for i in range(0, len(images), self.chunk_size):
            chunk = images[i:i+self.chunk_size]
            with ThreadPoolExecutor(max_workers=self.n_cpu) as executor:
                processed_chunk = list(executor.map(
                    partial(self._preprocess_single_cnn, target_size=target_size),
                    chunk
                ))
            processed.extend(processed_chunk)
        
        processed = np.array(processed)
        
        # FIX: Ensure proper shape (samples, height, width, channels)
        if processed.ndim == 3:
            # Add channel dimension for grayscale
            processed = np.expand_dims(processed, axis=-1)
        
        np.save(cache_file, processed)
        
        if self.verbose:
            print(f"Preprocessed in {time.time()-start_time:.2f}s")
            print(f"Processed shape: {processed.shape}")
        
        return processed
 
 
    def _preprocess_single_cnn(self, img: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """Optimized single image preprocessing for CNN"""
        # Convert to 3-channel if needed
        if img.ndim == 2:
            img = np.stack((img,)*3, axis=-1)
        elif img.shape[2] == 4:
            img = img[..., :3]
        # Handle channel conversions
        if img.ndim == 3:
            if img.shape[2] == 3:  # RGB to BGR if needed
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            elif img.shape[2] == 1:  # Grayscale to "RGB"
                img = np.concatenate([img]*3, axis=-1)
        # Resize with OpenCV
        if img.shape[:2] != target_size:
            img = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
        
        # Convert to float and normalize
        img = img.astype(np.float32) / 255.0
        
        # Fix: Return grayscale if needed
        if self.cfg["preprocessing"].get("to_grayscale", True):
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            img = np.expand_dims(img, axis=-1)
        
        return img

    def _create_callbacks(self, params: dict) -> List[tf.keras.callbacks.Callback]:
        """Create training callbacks"""
        return [
            EarlyStopping(
                patience=params.get('patience', 8),
                monitor='val_accuracy' if self.task_type == "classification" else 'val_loss',
                restore_best_weights=True,
                verbose=1 if self.verbose else 0
            ),
            ModelCheckpoint(
                'best_model.keras',
                save_best_only=True,
                monitor='val_accuracy' if self.task_type == "classification" else 'val_loss',
                mode='max' if self.task_type == "classification" else 'min'
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,
                min_lr=1e-6,
                verbose=1 if self.verbose else 0
            )
        ]

    def train_model(self, model_name: str = None, params: dict = None):
        """训练指定的模型"""
        if model_name is None:
            model_name=self.cfg["model"]["name"]
        if model_name != "cnn" and self.features is None:
            self.extract_features()
        print(f"Training model: {model_name}")
        if self.labels is None:
            raise ValueError("Labels are required for training")
        # 特殊处理需要自定义训练流程的模型
        if model_name in ["xgb", "lightgbm", "catboost"]:
            # 设置GPU加速（如果可用）
            if self.has_gpu:
                params.update({"tree_method": "gpu_hist", "gpu_id": 0})
            
            # 设置类别权重（针对不平衡数据）
            if self.task_type == "classification":
                class_weights = compute_class_weight('balanced', classes=np.unique(self.y_train), y=self.y_train)
                params["class_weight"] = dict(zip(np.unique(self.y_train), class_weights))
        
        # 获取模型配置
        model_cfg = self.cfg["model"]
        model_name = model_name or model_cfg["name"]
        params = params or model_cfg.get("params", {})

        if model_name not in self.models:
            raise ValueError(f"Unsupported model: {model_name}")

        # 特殊处理CNN模型
        if model_name == "cnn":
            if not self.dl_enabled:
                raise ImportError("Deep learning libraries not available")
            return self._train_cnn_model(self.models[model_name], params or {})

        # 划分训练测试集
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.features,
            self.labels,
            test_size=self.cfg["test_size"],
            random_state=self.cfg["random_state"],
            stratify=self.labels,
        )
        print("划分训练测试集")

        # 过滤不支持的参数
        model_class = self.models[model_name]
        
        supported_params = model_class().get_params().keys()
        filtered_params = {k: v for k, v in params.items() if k in supported_params}

        if len(filtered_params) != len(params) and self.verbose:
            removed_params = set(params.keys()) - set(filtered_params.keys())
            print(f"Removed unsupported params for {model_name}: {removed_params}")
        # 创建模型
        model = model_class(**filtered_params)

        print("创建模型")
        if self.verbose:
            print(f"🤖 Training {model_name} model...")
            print(f"📐 Parameters: {params}")

        # 训练模型
        start_time = time.time()
        model.fit(self.X_train, self.y_train)
        train_time = time.time() - start_time

        print(" 训练模型")
        # 评估模型
        metrics = self.evaluate_model(model)
        print(" 评估模型")
        # 保存结果
        self.model_performance[model_name] = {
            "model": model,
            "metrics": metrics,
            "train_time": train_time,
            "params": params,
        }
        print(" 保存结果")
        # 更新最佳模型
        self._update_best_model(model, metrics)

        if self.verbose:
            print(f"Model trained in {train_time:.2f}s")
            print("Performance metrics:")
            for k, v in metrics.items():
                print(f"  {k}: {v:.4f}")

        return model, metrics

    def auto_compare_models(
        self, model_names: List[str] = None, params_list: List[dict] = None
    ):
        """自动比较多个模型并排名"""
        if model_names is None:
            # 根据任务类型选择默认模型 
            if self.task_type == "classification":
                model_names = [
                    "random_forest", "svm", "knn", "gradient_boosting", "logistic_regression",
                    "xgb", "lightgbm", "catboost", "extra_trees", "mlp", "bagging"
                ]
                params_list = [
                    {"n_estimators": 100},  # RF
                    {"C": 1.0, "kernel": "rbf"},  # SVM
                    {"n_neighbors": 5},  # KNN
                    {"n_estimators": 100},  # GBM
                    {"C": 1.0, "penalty": "l2"},  # Logistic
                    {"n_estimators": 100},  # XGBoost
                    {"n_estimators": 100},  # LightGBM
                    {"iterations": 100},    # CatBoost
                    {"n_estimators": 100},  # Extra Trees
                    {"hidden_layer_sizes": (64,)},  # MLP
                    {"n_estimators": 50}    # Bagging
                ]
            else:  # regression
                model_names = [
                    "random_forest_reg", "svr", "knn_regressor", "gradient_boosting_reg", "linear_regression",
                    "xgb_reg", "lightgbm_reg", "catboost_reg", "extra_trees_reg", "mlp_reg", "bagging_reg"
                ]
                params_list = [
                    {"n_estimators": 100},  # RF Reg
                    {"C": 1.0, "kernel": "rbf"},  # SVR
                    {"n_neighbors": 5},  # KNN Reg
                    {"n_estimators": 100},  # GBM Reg
                    {},  # Linear Regression
                    {"n_estimators": 100},  # XGBoost Reg
                    {"n_estimators": 100},  # LightGBM Reg
                    {"iterations": 100},    # CatBoost Reg
                    {"n_estimators": 100},  # Extra Trees Reg
                    {"hidden_layer_sizes": (64,)},  # MLP Reg
                    {"n_estimators": 50}    # Bagging Reg
                ]
        # 分类的话, 必须要>=2个分类
        if self.task_type == "classification":
            unique_classes = np.unique(self.labels)
            if len(unique_classes) < 2:
                raise ValueError(
                    "Classification requires ≥2 classes. Your data has only one class."
                )
        if params_list is None:
            params_list = [{}] * len(model_names)

        if len(model_names) != len(params_list):
            raise ValueError("model_names and params_list must have the same length")

        if self.verbose:
            print(f"Comparing {len(model_names)} models...")

        # 训练并评估所有模型
        results = []
        for name, params in zip(model_names, params_list):
            try:
                _, metrics = self.train_model(name, params)
                results.append({"model": name, "params": params, **metrics})
            except Exception as e:
                print(f"Error training {name}: {str(e)}")

        # 创建结果DataFrame
        results_df = pd.DataFrame(results)

        # 根据任务类型选择排序指标
        if self.task_type == "classification":
            sort_by = "accuracy"
        else:
            sort_by = "r2"

        # 排序结果
        results_df = results_df.sort_values(by=sort_by, ascending=False)

        # 保存最佳模型
        best_model_name = results_df.iloc[0]["model"]
        self.best_model = self.model_performance[best_model_name]["model"]

        if self.verbose:
            print("\n🏆 Model Comparison Results:")
            print(results_df[["model", sort_by]])
            print(f"\n🥇 Best model: {best_model_name}")

        return results_df

    def _update_best_model(self, model, metrics):
        """Helper to update the best model reference"""
        if self.best_model is None:
            self.best_model = model
        else:
            current_metric = self._get_primary_metric(self.best_model)
            new_metric = self._get_primary_metric(model, metrics)

            if new_metric > current_metric:
                self.best_model = model

    def _get_primary_metric(self, model, metrics=None):
        """Get the appropriate primary metric for comparison"""
        if metrics is None:
            metrics = self.evaluate_model(model=model)

        return metrics.get(
            "accuracy" if self.task_type == "classification" else "r2", 0
        )

    def evaluate_model(self, model: BaseEstimator = None) -> dict:
        """评估模型性能"""
        if model is None:
            if self.best_model is None:
                raise ValueError("No model available for evaluation")
            model = self.best_model

        # 计算指标
        metrics = {}
        try:
            # 预测
            y_pred = model.predict(self.X_test)
            print("try to predict it again")
            if self.task_type == "classification":
                metrics["accuracy"] = accuracy_score(self.y_test, y_pred)
                metrics["f1_weighted"] = f1_score(self.y_test, y_pred, average="weighted")
                if self.verbose:
                    print("\nClassification Report:")
                    print(
                        classification_report(
                            self.y_test, y_pred, target_names=self.class_names
                        )
                    )
                    # 可视化混淆矩阵
                    if (
                        self.cfg["visualization"]["enable"]
                        and self.cfg["visualization"]["confusion_matrix"]
                    ):
                        self.plot_confusion_matrix(self.y_test, y_pred)
            else:
                metrics["mse"] = mean_squared_error(self.y_test, y_pred)
                metrics["mae"] = mean_absolute_error(self.y_test, y_pred)
                metrics["r2"] = r2_score(self.y_test, y_pred)
        except Exception as e:
            print(f"Error evaluating model: {str(e)}")
        return metrics

    def _reset_prediction_state(self):
        """Reset internal state before new prediction"""
        # Clear feature cache
        self.features = None
        self.clear_cache()
        # Clear CNN-specific cache
        if hasattr(self, 'preprocessed_images'):
            del self.preprocessed_images
        # Clear image cache
        self.images = []
        self.image_input = []
        # Clear train/test splits
        if hasattr(self, 'X_train'): self.X_train = None
        if hasattr(self, 'X_test'): self.X_test = None
        if hasattr(self, 'y_train'): self.y_train = None
        if hasattr(self, 'y_test'): self.y_test = None

    def predict(
        self,
        image_paths: List[str],
        model: BaseEstimator = None,
        output_dir: str = None,
    ) -> np.ndarray:
        """预测新图像的标签并生成报告"""
        self._reset_prediction_state()
        if model is None:
            if self.best_model is None:
                raise ValueError("No model available for prediction")
            model = self.best_model
        image_paths = list(image_paths)
        # 加载并预处理图像
        images, _ = self.load_images(image_paths)

        # Check if model is a CNN (Sequential/Functional API with Conv layers)
        is_cnn = any(isinstance(layer, (tf.keras.layers.Conv2D, tf.keras.layers.Convolution2D)) 
                    for layer in model.layers)
        if is_cnn:
            print("Using direct CNN prediction")  # Debug
            target_size = self.cfg["preprocessing"].get("resize", (32, 32))
            images = self._preprocess_for_cnn(images,target_size=target_size)  # Must return (N,H,W,C)
            predictions = model.predict(images)
        else:
            features = self.extract_features(images) 
            predictions = model.predict(features)
        self.clear_cache()
        self.predictions=predictions
        # 解码分类标签
    #     if self.task_type == "classification" and self.label_encoder:
    #         predictions = self.label_encoder.inverse_transform(predictions)
    # # Handle predictions based on model type
        if self.task_type == "classification":
            if predictions.ndim > 1 and predictions.shape[1] > 1:
                # Multi-class: convert probabilities to class indices
                predictions = np.argmax(predictions, axis=1)
            else:
                # Binary classification: threshold at 0.5
                predictions = (predictions > 0.5).astype(int)
            
            # Only inverse transform if label_encoder exists
            if hasattr(self, 'label_encoder') and self.label_encoder:
                try:
                    predictions = self.label_encoder.inverse_transform(predictions)
                except ValueError as e:
                    print(f"Label transform warning: {e}")
                    print("Returning numeric predictions instead")
        # 可视化预测结果
        if self.cfg["visualization"]["enable"]:
            self.visualize_predictions(images, predictions, image_paths)

        # 生成预测报告
        if output_dir:
            self.generate_prediction_report(image_paths, predictions, output_dir) 

        return predictions

    def save_model(self, model: BaseEstimator, file_path: str, format: str = "joblib"):
        """
        保存训练好的模型

        参数:
        model: 要保存的模型对象
        file_path: 保存路径
        format: 保存格式 ('joblib' 或 'pickle')
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if format == "joblib":
            joblib.dump(model, file_path)
        elif format == "pickle":
            with open(file_path, "wb") as f:
                pickle.dump(model, f)
        else:
            raise ValueError("Unsupported format. Use 'joblib' or 'pickle'")

        if self.verbose:
            print(f"Model saved to {file_path}")

    def load_model(self, file_path: str, format: str = "joblib") -> BaseEstimator:
        """
        加载保存的模型

        参数:
        file_path: 模型文件路径
        format: 文件格式 ('joblib' 或 'pickle')

        返回:
        加载的模型对象
        """
        if format == "joblib":
            model = joblib.load(file_path)
        elif format == "pickle":
            with open(file_path, "rb") as f:
                model = pickle.load(f)
        else:
            raise ValueError("Unsupported format. Use 'joblib' or 'pickle'")

        if self.best_model is None:
            self.best_model = model
            print(f"the best model is loaded: {model}")
        if self.verbose:
            print(f"Model loaded from {file_path}")

        return model

    def visualize_predictions(
        self, images: List[np.ndarray], predictions: List, paths: List[str] = None
    ):
        """可视化预测结果"""
        n_samples = min(self.cfg["visualization"]["sample_images"], len(images))

        plt.figure(figsize=(15, 8))
        for i in range(n_samples):
            plt.subplot(2, (n_samples + 1) // 2, i + 1)

            if images[i].ndim == 2:
                plt.imshow(images[i], cmap="gray")
            else:
                plt.imshow(images[i])

            title = f"Pred: {predictions[i]}"
            if paths and isinstance(paths[i], str) and paths[i]:
                title += f"\n{os.path.basename(paths[i])}"

            plt.title(title, fontsize=10)
            plt.axis("off")

        plt.tight_layout()

        # 保存可视化结果
        if self.cfg["report"].get("include_visuals", True):
            vis_path = os.path.join("reports", "prediction_visuals.png")
            os.makedirs(os.path.dirname(vis_path), exist_ok=True)
            plt.savefig(vis_path, dpi=150, bbox_inches="tight")

        plt.show()

    def plot_confusion_matrix(self, y_true, y_pred):
        """绘制混淆矩阵"""
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=self.class_names,
            yticklabels=self.class_names,
        )
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.title("Confusion Matrix")

        # 保存可视化结果
        if self.cfg["report"].get("include_visuals", True):
            cm_path = os.path.join("reports", "confusion_matrix.png")
            os.makedirs(os.path.dirname(cm_path), exist_ok=True)
            plt.savefig(cm_path, dpi=150, bbox_inches="tight")

        plt.show()

    def visualize_feature_space(self):
        """可视化特征空间"""
        if self.features is None:
            raise ValueError("No features available for visualization")
        if self.verbose:
            print(f"features dimensions: {self.features.shape[1]}")
        # 降维
        if self.features.shape[1] > 2:
            if self.verbose:
                print(
                    "Reducing feature dimensions for visualization...\n\t第一步:PCA;\n\t第二步:t-SNE to 2D)"
                )
            # 使用PCA进行初步降维, n_components=50
            pca = PCA(n_components=50)
            features_reduced = pca.fit_transform(self.features)

            # 使用t-SNE进一步降维到2D
            tsne = TSNE(n_components=2, random_state=self.cfg["random_state"])
            features_2d = tsne.fit_transform(features_reduced)
        else:
            features_2d = self.features

        # 绘制特征空间
        plt.figure(figsize=(12, 8))

        if self.labels is not None:
            scatter = plt.scatter(
                features_2d[:, 0],
                features_2d[:, 1],
                c=self.labels,
                cmap=self.cfg["visualization"]["cmap"],
                alpha=0.7,
            )

            if self.task_type == "classification":
                plt.legend(*scatter.legend_elements(), title="Classes")
        else:
            plt.scatter(features_2d[:, 0], features_2d[:, 1], alpha=0.7)

        plt.title("Feature Space Visualization")
        plt.xlabel("Dimension 1")
        plt.ylabel("Dimension 2")

        # 保存可视化结果
        if self.cfg["report"].get("include_visuals", True):
            fs_path = os.path.join("reports", "feature_space.pdf")
            os.makedirs(os.path.dirname(fs_path), exist_ok=True)
            plt.savefig(fs_path, dpi=150, bbox_inches="tight")

        plt.show()

    def generate_report(self, output_path: str = "reports/training_report.html"):
        """生成训练报告"""
        report_type = "html" if output_path.endswith(".html") else "md"

        if report_type == "html":
            report = self._generate_html_report()
            with open(output_path, "w") as f:
                f.write(report)
        else:
            report = self._generate_markdown_report()
            with open(output_path, "w") as f:
                f.write(report)

        if self.verbose:
            print(f"Report generated at {output_path}")

        return report

    def generate_prediction_report(
        self, image_paths: List[str], predictions: List, output_dir: str = "reports"
    ):
        """生成预测报告"""
        os.makedirs(output_dir, exist_ok=True)
        report_path = os.path.join(output_dir, "prediction_report.html")

        # 创建报告内容
        report = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Model Training Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2 {{ color: #2c3e50; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .summary {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
                .section {{ margin-bottom: 30px; }}
                img {{ max-width: 100%; height: auto; }}
            </style>
        </head>
        <body>
                    <h1>Image Prediction Report</h1>
            <p>Generated on: {date}</p>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Total Predictions:</strong> {count}</p>
                <p><strong>Model Used:</strong> {model_name}</p>
                <p><strong>Task Type:</strong> {task_type}</p>
            </div>
            
            <h2>Prediction Details</h2>
            <table>
                <tr>
                    <th>Image</th>
                    <th>Filename</th>
                    <th>Prediction</th>
                </tr>
                {rows}
            </table>
        </body>
        </html> 
        """

        # 生成表格行
        rows = ""
        for path, pred in zip(image_paths, predictions):
            try:
                img_tag = f'<img src="{path}" alt="{os.path.basename(path)}">'
                rows += f"<tr><td>{img_tag}</td><td>{os.path.basename(path)}</td><td>{pred}</td></tr>"
            except Exception as e:
                print(e)
                break

        # 填充报告
        report = report.format(
            date=time.strftime("%Y-%m-%d %H:%M:%S"),
            count=len(image_paths),
            model_name=(
                self.best_model.__class__.__name__ if self.best_model else "Unknown"
            ),
            task_type=self.task_type.capitalize(),
            rows=rows,
        )

        # 保存报告
        with open(report_path, "w") as f:
            f.write(report)

        if self.verbose:
            print(f"Prediction report generated at {report_path}")

        return report

    def _generate_html_report(self) -> str:
        """生成HTML格式的训练报告"""
        report = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Model Training Report</title>
            <style>
                body {{font-family: Arial; margin: 20px; }}
                h1, h2 {{ color: #2c3e50; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .summary {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
                .section {{ margin-bottom: 30px; }}
                img {{ max-width: 100%; height: auto; }}
            </style>
        </head>
        <body>
            <h1>Image Machine Learning Training Report</h1>
            <p>Generated on: {{date}}</p>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Task Type:</strong> {task_type}</p>
                <p><strong>Number of Images:</strong> {num_images}</p>
                <p><strong>Feature Extraction Method:</strong> {feat_method}</p>
                <p><strong>Best Model:</strong> {best_model} (Accuracy/R2: {best_metric:.4f})</p>
            </div>
            
            <div class="section">
                <h2>Model Performance Comparison</h2>
                {model_table}
            </div>
            
            <div class="section">
                <h2>cfguration</h2>
                <pre>{cfg}</pre>
            </div>
            
            <div class="section">
                <h2>Visualizations</h2>
                {visualizations}
            </div>
        </body>
        </html>
        """

        # 生成模型性能表
        if self.model_performance:
            model_table = """
            <table>
                <tr>
                    <th>Model</th>
                    <th>Accuracy/R2</th>
                    <th>F1/MSE</th>
                    <th>Training Time (s)</th>
                </tr>
                {rows}
            </table>
            """

            rows = ""
            for name, perf in self.model_performance.items():
                metrics = perf["metrics"]
                if self.task_type == "classification":
                    row = f"<tr><td>{name}</td><td>{metrics['accuracy']:.4f}</td><td>{metrics['f1_weighted']:.4f}</td><td>{perf['train_time']:.2f}</td></tr>"
                else:
                    row = f"<tr><td>{name}</td><td>{metrics['r2']:.4f}</td><td>{metrics['mse']:.4f}</td><td>{perf['train_time']:.2f}</td></tr>"
                rows += row

            model_table = model_table.format(rows=rows)
        else:
            model_table = "<p>No models trained yet.</p>"

        # 生成可视化部分
        visualizations = ""
        if self.cfg["report"].get("include_visuals", True):
            # 特征空间可视化
            fs_path = os.path.join("reports", "feature_space.png")
            if os.path.exists(fs_path):
                visualizations += (
                    f'<h3>Feature Space</h3><img src="{fs_path}" alt="Feature Space">'
                )

            # 混淆矩阵
            if self.task_type == "classification":
                cm_path = os.path.join("reports", "confusion_matrix.png")
                if os.path.exists(cm_path):
                    visualizations += f'<h3>Confusion Matrix</h3><img src="{cm_path}" alt="Confusion Matrix">'

        # 填充报告
        best_metric = self.evaluate_model(self.best_model).get(
            "accuracy" if self.task_type == "classification" else "r2", 0
        )

        report = report.format(
            date=time.strftime("%Y-%m-%d %H:%M:%S"),
            task_type=self.task_type.capitalize(),
            num_images=len(self.images),
            feat_method=self.cfg["feature_extraction"]["method"],
            best_model=self.best_model.__class__.__name__ if self.best_model else "N/A",
            best_metric=best_metric,
            model_table=model_table,
            cfg=json.dumps(self.cfg, indent=2),
            visualizations=visualizations,
        )

        return report

    def _generate_markdown_report(self) -> str:
        """生成Markdown格式的训练报告"""
        report = "# Image Machine Learning Training Report\n\n"
        report += f"**Generated on**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # 摘要部分
        best_metric = self.evaluate_model(self.best_model).get(
            "accuracy" if self.task_type == "classification" else "r2", 0
        )

        report += "## Summary\n"
        report += f"- **Task Type**: {self.task_type.capitalize()}\n"
        report += f"- **Number of Images**: {len(self.images)}\n"

        if self.task_type == "classification":
            report += f"- **Number of Classes**: {len(self.class_names)}\n"

        report += f"- **Feature Extraction Method**: {self.cfg['feature_extraction']['method']}\n"
        report += f"- **Best Model**: {self.best_model.__class__.__name__ if self.best_model else 'N/A'} (Accuracy/R2: {best_metric:.4f})\n\n"

        # 模型性能比较
        if self.model_performance:
            report += "## Model Performance Comparison\n\n"
            report += "| Model | Accuracy/R2 | F1/MSE | Training Time (s) |\n"
            report += "|-------|-------------|--------|-------------------|\n"

            for name, perf in self.model_performance.items():
                metrics = perf["metrics"]
                if self.task_type == "classification":
                    report += f"| {name} | {metrics['accuracy']:.4f} | {metrics['f1_weighted']:.4f} | {perf['train_time']:.2f} |\n"
                else:
                    report += f"| {name} | {metrics['r2']:.4f} | {metrics['mse']:.4f} | {perf['train_time']:.2f} |\n"
        else:
            report += "No models trained yet.\n\n"

        # 配置信息
        report += "\n## cfguration\n```json\n"
        report += json.dumps(self.cfg, indent=2)
        report += "\n```\n\n"

        # 可视化
        if self.cfg["report"].get("include_visuals", True):
            report += "## Visualizations\n"

            # 特征空间可视化
            fs_path = os.path.join("reports", "feature_space.png")
            if os.path.exists(fs_path):
                report += f"### Feature Space\n![]({fs_path})\n\n"

            # 混淆矩阵
            if self.task_type == "classification":
                cm_path = os.path.join("reports", "confusion_matrix.png")
                if os.path.exists(cm_path):
                    report += f"### Confusion Matrix\n![]({cm_path})\n\n"

        return report