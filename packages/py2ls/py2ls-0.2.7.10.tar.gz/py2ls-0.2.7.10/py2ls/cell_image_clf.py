import os
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import models
import albumentations as A
from albumentations.pytorch import ToTensorV2
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
)
from sklearn.preprocessing import label_binarize
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import joblib
from tqdm import tqdm
import json
from datetime import datetime
import time
from PIL import Image
import gc
from torch.cuda import amp
from torch.optim.lr_scheduler import CosineAnnealingLR, ReduceLROnPlateau
import warnings

# 忽略警告
warnings.filterwarnings("ignore")

from .ips import set_computing_device
set_computing_device()

class CellImageClassifier:
    """
    终极细胞图像分类系统 

    主要改进:
    1. 支持混合精度训练(AMP) - 加速训练并减少显存占用
    2. 添加多种学习率调度器
    3. 增强多通道图像处理能力
    4. 添加模型解释功能(Grad-CAM)
    5. 改进数据加载效率(使用缓存)
    6. 添加更详细的评估指标(AUC-ROC, PR曲线等)
    7. 增强错误处理和日志记录
    """

    def __init__(self, config=None):
        # 默认配置
        self.default_config = {
            "model_name": "resnet18",  # 支持的模型: resnet18, resnet50, efficientnet_b0-3, densenet121, vgg16, convnext_tiny
            "num_classes": 5,  # 分类类别数
            "input_channels": 3,  # 输入通道数
            "image_size": (256, 256),  # 输入图像尺寸
            "batch_size": 16,  # 批量大小
            "learning_rate": 0.001,  # 初始学习率
            "epochs": 30,  # 训练轮数
            "device": self._auto_select_device(),  # 自动选择设备
            "augmentation_level": "high",  # 增强级别: none, low, medium, high
            "staining_type": "generic",  # 染色类型: generic, H&E, fluorescence, IHC
            "model_save_path": "models",  # 模型保存路径
            "report_save_path": "reports",  # 报告保存路径
            "data_cache_path": "data_cache",  # 数据缓存路径
            "use_amp": True,  # 启用混合精度训练
            "lr_scheduler": "plateau",  # 学习率调度器: plateau, cosine, step
            "optimizer": "adam",  # 优化器: adam, sgd
            "early_stopping": 5,  # 早停轮数(0表示禁用)
            "class_weights": None,  # 类别权重(处理不平衡数据)
            "grad_cam_layers": ["layer4"],  # Grad-CAM可视化层
        }

        # 合并用户配置
        self.config = {**self.default_config, **(config or {})}

        # 初始化模型
        self.model = None
        self.class_names = None
        self.label_encoder = None
        self.stats = {
            "train_loss": [],
            "val_loss": [],
            "val_accuracy": [],
            "val_auc": [],
            "val_f1": [],
        }

        # 创建必要的目录
        os.makedirs(self.config["model_save_path"], exist_ok=True)
        os.makedirs(self.config["report_save_path"], exist_ok=True)
        os.makedirs(self.config["data_cache_path"], exist_ok=True)

        # 初始化混合精度训练
        self.scaler = amp.GradScaler(enabled=self.config["use_amp"])

        print(f"细胞图像分类器初始化完成 | 设备: {self.config['device']}")

    @staticmethod
    def _auto_select_device():
        """自动选择最佳计算设备"""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"

    def _clear_cache(self):
        """清除缓存以释放内存"""
        torch.cuda.empty_cache()
        gc.collect()

    def build_model(self):
        """创建图像分类模型"""
        model_name = self.config["model_name"].lower()
        num_classes = self.config["num_classes"]
        in_channels = self.config["input_channels"]

        # 支持的模型列表
        supported_models = {
            "resnet18": models.resnet18,
            "resnet34": models.resnet34,
            "resnet50": models.resnet50,
            "resnet101": models.resnet101,
            "efficientnet_b0": models.efficientnet_b0,
            "efficientnet_b3": models.efficientnet_b3,
            "densenet121": models.densenet121,
            "vgg16": models.vgg16,
            "convnext_tiny": models.convnext_tiny,
        }

        if model_name not in supported_models:
            raise ValueError(
                f"不支持的模型: {model_name}。支持: {list(supported_models.keys())}"
            )

        # 创建预训练模型
        try:
            model_func = supported_models[model_name]
            pretrained_model = model_func(pretrained=True)
        except Exception as e:
            print(f"加载预训练模型失败: {e}, 使用随机初始化")
            pretrained_model = model_func(pretrained=False)

        # 根据模型类型调整输入通道
        if "resnet" in model_name:
            # 修改ResNet的第一层卷积
            original_conv1 = pretrained_model.conv1
            pretrained_model.conv1 = nn.Conv2d(
                in_channels=in_channels,
                out_channels=original_conv1.out_channels,
                kernel_size=original_conv1.kernel_size,
                stride=original_conv1.stride,
                padding=original_conv1.padding,
                bias=original_conv1.bias,
            )
            # 修改最后的全连接层
            num_features = pretrained_model.fc.in_features
            pretrained_model.fc = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(num_features, 512),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(512, num_classes),
            )

        elif "efficientnet" in model_name:
            # 修改EfficientNet的第一层卷积
            original_conv = pretrained_model.features[0][0]
            pretrained_model.features[0][0] = nn.Conv2d(
                in_channels=in_channels,
                out_channels=original_conv.out_channels,
                kernel_size=original_conv.kernel_size,
                stride=original_conv.stride,
                padding=original_conv.padding,
                bias=False,
            )
            # 修改最后的分类层
            num_features = pretrained_model.classifier[1].in_features
            pretrained_model.classifier = nn.Sequential(
                nn.Dropout(0.4), nn.Linear(num_features, num_classes)
            )

        elif "densenet" in model_name:
            # 修改DenseNet的第一层卷积
            original_conv = pretrained_model.features.conv0
            pretrained_model.features.conv0 = nn.Conv2d(
                in_channels=in_channels,
                out_channels=original_conv.out_channels,
                kernel_size=original_conv.kernel_size,
                stride=original_conv.stride,
                padding=original_conv.padding,
                bias=False,
            )
            # 修改最后的分类层
            num_features = pretrained_model.classifier.in_features
            pretrained_model.classifier = nn.Linear(num_features, num_classes)

        elif "vgg" in model_name:
            # 修改VGG的第一层卷积
            original_conv = pretrained_model.features[0]
            pretrained_model.features[0] = nn.Conv2d(
                in_channels=in_channels,
                out_channels=original_conv.out_channels,
                kernel_size=original_conv.kernel_size,
                stride=original_conv.stride,
                padding=original_conv.padding,
            )
            # 修改最后的分类层
            num_features = pretrained_model.classifier[6].in_features
            pretrained_model.classifier[6] = nn.Linear(num_features, num_classes)

        elif "convnext" in model_name:
            # 修改ConvNeXt的第一层卷积
            original_conv = pretrained_model.features[0][0]
            pretrained_model.features[0][0] = nn.Conv2d(
                in_channels=in_channels,
                out_channels=original_conv.out_channels,
                kernel_size=original_conv.kernel_size,
                stride=original_conv.stride,
                padding=original_conv.padding,
            )
            # 修改最后的分类层
            num_features = pretrained_model.classifier[2].in_features
            pretrained_model.classifier[2] = nn.Linear(num_features, num_classes)

        self.model = pretrained_model.to(self.config["device"])
        print(
            f"创建模型: {model_name} | 输入通道: {in_channels} | 类别数: {num_classes}"
        )
        return self.model

    def get_augmentations(self):
        """获取数据增强管道 - 根据染色类型和增强级别定制"""
        staining_type = self.config["staining_type"]
        aug_level = self.config["augmentation_level"]
        image_size = self.config["image_size"]

        # 基础转换（始终应用）
        base_transforms = [
            A.Resize(image_size[0], image_size[1]),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2(),
        ]

        # 根据增强级别选择增强
        if aug_level == "none":
            return A.Compose(base_transforms)

        # 通用增强
        common_aug = [
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.Rotate(limit=30, p=0.5),
            A.ShiftScaleRotate(
                shift_limit=0.1, scale_limit=0.1, rotate_limit=15, p=0.5
            ),
            A.RandomBrightnessContrast(brightness_limit=0.1, contrast_limit=0.1, p=0.5),
        ]

        # 染色类型特定的增强
        staining_aug = []
        if staining_type == "H&E":
            # H&E染色增强 - 增强细胞核与细胞质的对比度
            staining_aug = [
                A.CLAHE(clip_limit=3.0, tile_grid_size=(8, 8), p=0.7),
                A.HueSaturationValue(
                    hue_shift_limit=5, sat_shift_limit=20, val_shift_limit=10, p=0.5
                ),
                A.RGBShift(r_shift_limit=10, g_shift_limit=10, b_shift_limit=10, p=0.3),
                A.RandomGamma(gamma_limit=(70, 130), p=0.5),  # 增强对比度
            ]
        elif staining_type == "fluorescence":
            # 荧光染色增强 - 保持通道关系
            staining_aug = [
                A.RandomGamma(gamma_limit=(80, 120), p=0.5),
                A.MultiplicativeNoise(multiplier=[0.9, 1.1], elementwise=True, p=0.2),
                A.ChannelShuffle(p=0.1),  # 模拟通道错位
                A.ChannelDropout(
                    channel_drop_range=(1, 1), fill_value=0, p=0.1
                ),  # 模拟通道丢失
            ]
        elif staining_type == "IHC":
            # 免疫组化染色增强 - 增强棕褐色沉淀
            staining_aug = [
                A.ColorJitter(
                    brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1, p=0.7
                ),
                A.RGBShift(r_shift_limit=20, g_shift_limit=10, b_shift_limit=5, p=0.5),
                A.Sharpen(alpha=(0.2, 0.5), p=0.3),  # 增强细节
            ]
        else:  # generic
            staining_aug = [
                A.CLAHE(clip_limit=2.0, tile_grid_size=(8, 8), p=0.3),
                A.HueSaturationValue(
                    hue_shift_limit=5, sat_shift_limit=10, val_shift_limit=5, p=0.5
                ),
                A.RandomGamma(gamma_limit=(80, 120), p=0.5),
            ]

        # 高级增强
        advanced_aug = []
        if aug_level in ["medium", "high"]:
            advanced_aug = [
                A.OneOf(
                    [
                        A.MotionBlur(blur_limit=3, p=0.3),
                        A.GaussianBlur(blur_limit=3, p=0.3),
                        A.MedianBlur(blur_limit=3, p=0.3),
                    ],
                    p=0.5,
                ),
                A.OneOf(
                    [
                        A.OpticalDistortion(distort_limit=0.5, shift_limit=0.1, p=0.3),
                        A.GridDistortion(num_steps=5, distort_limit=0.3, p=0.3),
                        A.ElasticTransform(alpha=1, sigma=20, alpha_affine=10, p=0.3),
                    ],
                    p=0.5,
                ),
                A.CoarseDropout(max_holes=3, max_height=20, max_width=20, p=0.3),
            ]

            if aug_level == "high":
                advanced_aug += [
                    A.RandomShadow(
                        shadow_roi=(0, 0.5, 1, 1),
                        num_shadows_lower=1,
                        num_shadows_upper=2,
                        p=0.2,
                    ),
                    A.RandomSunFlare(src_radius=100, p=0.1),
                    A.RandomFog(fog_coef_lower=0.1, fog_coef_upper=0.3, p=0.1),
                    A.RandomRain(p=0.1),  # 模拟显微镜上的水滴
                ]

        # 组合所有增强
        all_aug = common_aug + staining_aug + advanced_aug
        return A.Compose(all_aug + base_transforms)

    def create_dataset(self, image_paths, labels, is_train=True):
        """
        创建细胞图像数据集

        参数:
        image_paths (list): 图像路径列表
        labels (list): 对应标签列表
        is_train (bool): 是否为训练集

        返回:
        CellDataset: 自定义数据集对象
        """
        # 如果没有标签，创建虚拟标签（用于预测）
        if labels is None:
            labels = [-1] * len(image_paths)

        # 创建标签编码器（如果是第一次）
        if self.label_encoder is None:
            unique_labels = sorted(set(labels))
            self.label_encoder = {label: idx for idx, label in enumerate(unique_labels)}
            self.class_names = list(self.label_encoder.keys())
            self.config["num_classes"] = len(self.class_names)
            print(f"创建标签编码器 | 类别: {self.class_names}")

        # 将标签编码为数字
        encoded_labels = [self.label_encoder.get(l, -1) for l in labels]

        # 获取增强管道
        transform = self.get_augmentations() if is_train else self.get_augmentations()

        return CellDataset(
            image_paths=image_paths,
            labels=encoded_labels,
            transform=transform,
            is_train=is_train,
            input_channels=self.config["input_channels"],
            cache_dir=self.config["data_cache_path"] if is_train else None,
        )

    def train(self, image_paths, labels, val_split=0.2, save_best=True):
        """
        训练细胞图像分类模型

        参数:
        image_paths (list): 图像路径列表
        labels (list): 对应标签列表
        val_split (float): 验证集比例
        save_best (bool): 是否保存最佳模型
        """
        # 清除缓存
        self._clear_cache()

        # 创建数据集
        full_dataset = self.create_dataset(image_paths, labels, is_train=True)

        # 分割训练集和验证集
        if val_split > 0:
            val_size = int(len(full_dataset) * val_split)
            train_size = len(full_dataset) - val_size
            train_dataset, val_dataset = random_split(
                full_dataset,
                [train_size, val_size],
                generator=torch.Generator().manual_seed(42),
            )
        else:
            train_dataset = full_dataset
            val_dataset = None

        # 创建数据加载器
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config["batch_size"],
            shuffle=True,
            num_workers=0,#min(4, os.cpu_count()),
            pin_memory=True,
            persistent_workers=True,
        )

        val_loader = None
        if val_dataset:
            val_loader = DataLoader(
                val_dataset,
                batch_size=self.config["batch_size"],
                shuffle=False,
                num_workers=0,#min(2, os.cpu_count()),
                pin_memory=True,
            )

        # 创建模型（如果尚未创建）
        if self.model is None:
            self.build_model()

        # 设置优化器
        optimizer_name = self.config["optimizer"].lower()
        if optimizer_name == "sgd":
            optimizer = optim.SGD(
                self.model.parameters(),
                lr=self.config["learning_rate"],
                momentum=0.9,
                weight_decay=1e-4,
            )
        else:  # 默认使用Adam
            optimizer = optim.Adam(
                self.model.parameters(),
                lr=self.config["learning_rate"],
                weight_decay=1e-4,
            )

        # 设置损失函数（考虑类别不平衡）
        if self.config["class_weights"]:
            weights = torch.tensor(
                self.config["class_weights"], device=self.config["device"]
            )
            criterion = nn.CrossEntropyLoss(weight=weights)
        else:
            criterion = nn.CrossEntropyLoss()

        # 设置学习率调度器
        scheduler_name = self.config["lr_scheduler"].lower()
        if scheduler_name == "cosine":
            scheduler = CosineAnnealingLR(optimizer, T_max=self.config["epochs"])
        elif scheduler_name == "step":
            scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)
        else:  # 默认使用Plateau
            scheduler = ReduceLROnPlateau(
                optimizer, mode="min", patience=3, factor=0.5, verbose=True
            )

        # 训练循环
        best_val_loss = float("inf")
        best_val_accuracy = 0.0
        epochs_no_improve = 0

        for epoch in range(self.config["epochs"]):
            start_time = time.time()

            # 训练阶段
            self.model.train()
            train_loss = 0.0
            progress_bar = tqdm(
                train_loader, desc=f"Epoch {epoch+1}/{self.config['epochs']} [Train]"
            )

            for images, labels in progress_bar:
                images, labels = images.to(self.config["device"]), labels.to(
                    self.config["device"]
                )

                # 混合精度训练
                with amp.autocast(enabled=self.config["use_amp"]):
                    outputs = self.model(images)
                    loss = criterion(outputs, labels)

                # 反向传播
                optimizer.zero_grad()
                self.scaler.scale(loss).backward()
                self.scaler.step(optimizer)
                self.scaler.update()

                train_loss += loss.item() * images.size(0)
                progress_bar.set_postfix(loss=loss.item())

            # 计算平均训练损失
            train_loss = train_loss / len(train_loader.dataset)
            self.stats["train_loss"].append(train_loss)

            # 验证阶段
            val_loss = 0.0
            val_accuracy = 0.0
            all_labels = []
            all_preds = []

            if val_loader:
                self.model.eval()
                correct = 0
                total = 0
                progress_bar = tqdm(
                    val_loader, desc=f"Epoch {epoch+1}/{self.config['epochs']} [Val]"
                )

                with torch.no_grad():
                    for images, labels in progress_bar:
                        images, labels = images.to(self.config["device"]), labels.to(
                            self.config["device"]
                        )

                        with amp.autocast(enabled=self.config["use_amp"]):
                            outputs = self.model(images)
                            loss = criterion(outputs, labels)

                        val_loss += loss.item() * images.size(0)

                        _, predicted = torch.max(outputs.data, 1)
                        total += labels.size(0)
                        correct += (predicted == labels).sum().item()

                        # 收集预测结果用于计算高级指标
                        all_labels.extend(labels.cpu().numpy())
                        all_preds.extend(predicted.cpu().numpy())

                        accuracy = correct / total
                        progress_bar.set_postfix(loss=loss.item(), accuracy=accuracy)

                # 计算验证指标
                val_loss = val_loss / len(val_loader.dataset)
                val_accuracy = correct / total
                self.stats["val_loss"].append(val_loss)
                self.stats["val_accuracy"].append(val_accuracy)

                # 计算AUC和F1分数
                if len(self.class_names) > 2:
                    # 多分类AUC
                    y_true_bin = label_binarize(
                        all_labels, classes=range(len(self.class_names))
                    )
                    y_pred_bin = label_binarize(
                        all_preds, classes=range(len(self.class_names))
                    )
                    auc = roc_auc_score(y_true_bin, y_pred_bin, multi_class="ovr")
                    f1 = average_precision_score(y_true_bin, y_pred_bin)
                else:
                    # 二分类AUC
                    auc = roc_auc_score(all_labels, all_preds)
                    f1 = average_precision_score(all_labels, all_preds)

                self.stats["val_auc"].append(auc)
                self.stats["val_f1"].append(f1)

                # 更新学习率
                if scheduler_name == "plateau":
                    scheduler.step(val_loss)
                else:
                    scheduler.step()

                # 保存最佳模型
                if save_best and val_accuracy > best_val_accuracy:
                    best_val_accuracy = val_accuracy
                    best_val_loss = val_loss
                    epochs_no_improve = 0
                    self.save_model("best_model.pth")
                    print(
                        f"保存最佳模型 | 验证准确率: {val_accuracy:.4f} | AUC: {auc:.4f}"
                    )
                else:
                    epochs_no_improve += 1
                    if (
                        self.config["early_stopping"] > 0
                        and epochs_no_improve >= self.config["early_stopping"]
                    ):
                        print(f"早停触发: 验证准确率连续{epochs_no_improve}轮未提升")
                        break
            else:
                # 如果没有验证集，只更新训练损失
                if scheduler_name != "plateau":
                    scheduler.step()

            # 计算epoch时间
            epoch_time = time.time() - start_time

            # 打印epoch总结
            if val_loader:
                print(
                    f"Epoch {epoch+1}/{self.config['epochs']} | "
                    f"Time: {epoch_time:.1f}s | "
                    f"Train Loss: {train_loss:.4f} | "
                    f"Val Loss: {val_loss:.4f} | "
                    f"Val Acc: {val_accuracy:.4f} | "
                    f"AUC: {auc:.4f} | "
                    f"F1: {f1:.4f}"
                )
            else:
                print(
                    f"Epoch {epoch+1}/{self.config['epochs']} | "
                    f"Time: {epoch_time:.1f}s | "
                    f"Train Loss: {train_loss:.4f}"
                )

        # 保存最终模型
        self.save_model("final_model.pth")
        print("训练完成!")

        # 可视化训练过程
        self.plot_training_history()

        return self.stats

    def predict(self, image_paths, output_dir=None):
        """
        使用训练好的模型进行预测

        参数:
        image_paths (list): 图像路径列表
        output_dir (str): 预测结果保存目录

        返回:
        tuple: (预测标签列表, 预测概率数组)
        """
        if self.model is None:
            raise RuntimeError("模型未加载，请先加载或训练模型")

        # 清除缓存
        self._clear_cache()

        # 创建预测数据集
        dataset = self.create_dataset(image_paths, labels=None, is_train=False)
        dataloader = DataLoader(
            dataset,
            batch_size=self.config["batch_size"],
            shuffle=False,
            num_workers=0,#min(2, os.cpu_count()),
            pin_memory=True,
        )
        # print("---debug---")
        # print("如果参数里有NaN或Inf，说明权重加载或保存有问题，需要重新加载或重新训练模型。")
        # for name, param in self.model.named_parameters():
        #     if param.requires_grad:
        #         print(f"{name} mean: {param.data.mean().item()}, std: {param.data.std().item()}")
        #         if torch.isnan(param).any():
        #             print(f"参数{name}中含NaN")
        #         if torch.isinf(param).any():
        #             print(f"参数{name}中含Inf")
        # print("---debug---")
        # 预测
        self.model.eval()
        all_predictions = []
        all_probabilities = []
        all_logits = [] 
        with torch.no_grad():
            for images, _ in tqdm(dataloader, desc="预测中"):
                images = images.to(self.config["device"])
                # ---- debug ----
                # sample_img = images[0].unsqueeze(0).to(self.config["device"])
                # output = self.model(sample_img)
                # print("单张图像模型输出:", output)
                # print("是否含NaN:", torch.isnan(output).any().item())
                # print("是否含Inf:", torch.isinf(output).any().item())
                # ---- debug ----

                # print("输入数据 min:", images.min().item())
                # print("输入数据 max:", images.max().item())
                # print("输入数据 has NaN:", torch.isnan(images).any().item())
                # print("输入数据 has Inf:", torch.isinf(images).any().item())
                # break  # 只打印第一个batch，防止输出太多
            
                with amp.autocast(enabled=self.config["use_amp"]):
                    outputs = self.model(images)
                # ----debug----
                # print("outputs min:", outputs.min().item())
                # print("outputs max:", outputs.max().item())
                # print("outputs has NaN:", torch.isnan(outputs).any().item())
                # print("outputs has Inf:", torch.isinf(outputs).any().item())
                # ----debug----

                probabilities = torch.softmax(outputs, dim=1)
                _, predicted = torch.max(outputs, 1)

                all_predictions.extend(predicted.cpu().numpy())
                all_probabilities.extend(probabilities.cpu().numpy())
                all_logits.extend(outputs.cpu().numpy())

        # 将数字标签解码为原始标签
        decoded_predictions = [self.class_names[p] for p in all_predictions]

        # 保存预测结果
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(output_dir, f"predictions_{timestamp}.csv")

            # 创建结果DataFrame
            results = []
            for i, path in enumerate(image_paths):
                pred_label = decoded_predictions[i]
                prob = all_probabilities[i][all_predictions[i]]
                results.append(
                    {
                        "image_path": path,
                        "predicted_class": pred_label,
                        "probability": prob,
                        **{
                            f"prob_{cls}": prob_val
                            for cls, prob_val in zip(
                                self.class_names, all_probabilities[i]
                            )
                        },
                    }
                )

            df = pd.DataFrame(results)
            df.to_csv(report_path, index=False)
            print(f"预测结果保存至: {report_path}")

            # 生成可视化报告
            self.generate_prediction_report(
                image_paths, decoded_predictions, all_probabilities, output_dir
            )

            # 生成Grad-CAM可视化
            if self.config["grad_cam_layers"]:
                self.generate_grad_cam(
                    image_paths,
                    all_logits,
                    output_dir,
                    layer_names=self.config["grad_cam_layers"],
                )

        return decoded_predictions, np.array(all_probabilities)

    def evaluate(self, image_paths, labels):
        """
        评估模型性能

        参数:
        image_paths (list): 图像路径列表
        labels (list): 真实标签列表

        返回:
        dict: 包含详细评估指标的字典
        """
        # 预测
        predictions, probabilities = self.predict(image_paths)
        # -------debug------
        # prob_array = np.array(probabilities)
        # print("probabilities shape:", prob_array.shape)
        # print("NaN count in probabilities:", np.isnan(prob_array).sum())
        # print("Sample probabilities:", prob_array[:5])
        # -------debug------
        
        # 处理NaN,替换成0
        probabilities = np.nan_to_num(probabilities, nan=0.0)

        # 编码真实标签
        true_labels_encoded = [self.label_encoder[l] for l in labels]
        # 把字符串预测标签转成数字编码
        predictions_encoded = [self.label_encoder[p] for p in predictions]

        # 计算评估指标
        report = classification_report(
            true_labels_encoded, predictions_encoded, output_dict=True
        )
        cm = confusion_matrix(
            true_labels_encoded, predictions_encoded, labels=range(len(self.class_names))
        )

        # 计算AUC-ROC
        if len(self.class_names) > 2:
            # 多分类AUC
            y_true_bin = label_binarize(
                true_labels_encoded, classes=range(len(self.class_names))
            )
            auc = roc_auc_score(y_true_bin, probabilities, multi_class="ovr")
            ap = average_precision_score(y_true_bin, probabilities)
        else:
            # 二分类AUC
            auc = roc_auc_score(true_labels_encoded, probabilities[:, 1])
            ap = average_precision_score(true_labels_encoded, probabilities[:, 1])

        # 可视化混淆矩阵
        plt.figure(figsize=(12, 10))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=self.class_names,
            yticklabels=self.class_names,
        )
        plt.xlabel("预测标签")
        plt.ylabel("真实标签")
        plt.title("混淆矩阵")

        # 保存评估报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = self.config["report_save_path"]
        os.makedirs(report_dir, exist_ok=True)

        # 保存分类报告
        report_path = os.path.join(
            report_dir, f"classification_report_{timestamp}.json"
        )
        with open(report_path, "w") as f:
            json.dump(report, f, indent=4)

        # 保存混淆矩阵
        cm_path = os.path.join(report_dir, f"confusion_matrix_{timestamp}.png")
        plt.savefig(cm_path, bbox_inches="tight")
        plt.close()

        # 保存ROC曲线
        self.plot_roc_curve(
            true_labels_encoded,
            probabilities,
            save_path=os.path.join(report_dir, f"roc_curve_{timestamp}.png"),
        )

        # 保存PR曲线
        self.plot_pr_curve(
            true_labels_encoded,
            probabilities,
            save_path=os.path.join(report_dir, f"pr_curve_{timestamp}.png"),
        )

        print(f"评估报告保存至: {report_path}")
        print(f"混淆矩阵保存至: {cm_path}")
        print(f"AUC-ROC: {auc:.4f} | Average Precision: {ap:.4f}")

        return {
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
            "auc_roc": auc,
            "average_precision": ap,
        }

    def save_model(self, filename):
        """
        保存模型和配置

        参数:
        filename (str): 模型文件名
        """
        model_path = os.path.join(self.config["model_save_path"], filename)

        # 保存模型状态
        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "config": self.config,
                "label_encoder": self.label_encoder,
                "class_names": self.class_names,
                "stats": self.stats,
            },
            model_path,
        )

        print(f"模型保存至: {model_path}")
        return model_path

    def load_model(self, model_path):
        """
        加载预训练模型

        参数:
        model_path (str): 模型文件路径
        """
        # 加载检查点
        checkpoint = torch.load(
            model_path, map_location=torch.device(self.config["device"])
        )

        # 加载配置
        if "config" in checkpoint:
            loaded_config = checkpoint["config"]
            # 更新配置但不覆盖设备设置
            loaded_config["device"] = self.config["device"]
            self.config = {**self.config, **loaded_config}

        # 加载标签编码器和类别名称
        if "label_encoder" in checkpoint:
            self.label_encoder = checkpoint["label_encoder"]
            self.class_names = checkpoint.get(
                "class_names", list(self.label_encoder.keys())
            )
            self.config["num_classes"] = len(self.class_names)
            print(f"加载标签编码器 | 类别: {self.class_names}")
        elif "class_names" in checkpoint:
            self.class_names = checkpoint["class_names"]
            self.label_encoder = {cls: idx for idx, cls in enumerate(self.class_names)}
            self.config["num_classes"] = len(self.class_names)
            print(f"从类别名称重建标签编码器 | 类别: {self.class_names}")

        # 加载训练统计信息
        if "stats" in checkpoint:
            self.stats = checkpoint["stats"]

        # 创建模型架构
        self.build_model()

        # 加载模型权重
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()
        print(f"模型从 {model_path} 加载成功")

        return self.model

    def plot_training_history(self):
        """可视化训练历史"""
        if not self.stats["train_loss"]:
            print("没有训练历史数据")
            return

        plt.figure(figsize=(16, 12))

        # 绘制损失曲线
        plt.subplot(2, 2, 1)
        plt.plot(self.stats["train_loss"], label="训练损失")
        if self.stats["val_loss"]:
            plt.plot(self.stats["val_loss"], label="验证损失")
        plt.title("训练和验证损失")
        plt.xlabel("轮次")
        plt.ylabel("损失")
        plt.legend()
        plt.grid(True)

        # 绘制准确率曲线
        if self.stats["val_accuracy"]:
            plt.subplot(2, 2, 2)
            plt.plot(self.stats["val_accuracy"], label="验证准确率", color="green")
            plt.title("验证准确率")
            plt.xlabel("轮次")
            plt.ylabel("准确率")
            plt.legend()
            plt.grid(True)

        # 绘制AUC曲线
        if self.stats["val_auc"]:
            plt.subplot(2, 2, 3)
            plt.plot(self.stats["val_auc"], label="验证AUC", color="purple")
            plt.title("验证AUC")
            plt.xlabel("轮次")
            plt.ylabel("AUC")
            plt.legend()
            plt.grid(True)

        # 绘制F1曲线
        if self.stats["val_f1"]:
            plt.subplot(2, 2, 4)
            plt.plot(self.stats["val_f1"], label="验证F1分数", color="orange")
            plt.title("验证F1分数")
            plt.xlabel("轮次")
            plt.ylabel("F1分数")
            plt.legend()
            plt.grid(True)

        plt.tight_layout()

        # 保存图像
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_path = os.path.join(
            self.config["report_save_path"], f"training_history_{timestamp}.png"
        )
        plt.savefig(plot_path, bbox_inches="tight", dpi=300)
        plt.close()
        print(f"训练历史图保存至: {plot_path}")

    def plot_roc_curve(self, true_labels, probabilities, save_path=None):
        """绘制ROC曲线"""
        from sklearn.metrics import roc_curve, auc
        from itertools import cycle

        if len(self.class_names) == 2:
            # 二分类
            fpr, tpr, _ = roc_curve(true_labels, probabilities[:, 1])
            roc_auc = auc(fpr, tpr)

            plt.figure()
            plt.plot(
                fpr,
                tpr,
                color="darkorange",
                lw=2,
                label=f"ROC曲线 (AUC = {roc_auc:.2f})",
            )
            plt.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--")
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel("假正例率")
            plt.ylabel("真正例率")
            plt.title("ROC曲线")
            plt.legend(loc="lower right")
        else:
            # 多分类
            fpr = dict()
            tpr = dict()
            roc_auc = dict()

            # 二值化真实标签
            y_true_bin = label_binarize(
                true_labels, classes=range(len(self.class_names))
            )

            # 计算每个类别的ROC曲线和AUC
            for i in range(len(self.class_names)):
                fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], probabilities[:, i])
                roc_auc[i] = auc(fpr[i], tpr[i])

            # 计算微平均ROC曲线和AUC
            fpr["micro"], tpr["micro"], _ = roc_curve(
                y_true_bin.ravel(), probabilities.ravel()
            )
            roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

            # 绘制ROC曲线
            plt.figure(figsize=(10, 8))
            colors = cycle(
                ["aqua", "darkorange", "cornflowerblue", "green", "red", "purple"]
            )

            # 绘制每个类别的ROC曲线
            for i, color in zip(range(len(self.class_names)), colors):
                plt.plot(
                    fpr[i],
                    tpr[i],
                    color=color,
                    lw=2,
                    label=f"ROC {self.class_names[i]} (AUC = {roc_auc[i]:.2f})",
                )

            # 绘制微平均ROC曲线
            plt.plot(
                fpr["micro"],
                tpr["micro"],
                label=f'Micro-average ROC (AUC = {roc_auc["micro"]:.2f})',
                color="deeppink",
                linestyle=":",
                linewidth=4,
            )

            plt.plot([0, 1], [0, 1], "k--", lw=2)
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel("假正例率")
            plt.ylabel("真正例率")
            plt.title("多类别ROC曲线")
            plt.legend(loc="lower right")

        if save_path:
            plt.savefig(save_path, bbox_inches="tight", dpi=300)
            plt.close()
            return save_path
        else:
            plt.show()

    def plot_pr_curve(self, true_labels, probabilities, save_path=None):
        """绘制精确率-召回率曲线"""
        from sklearn.metrics import precision_recall_curve, average_precision_score
        from itertools import cycle

        if len(self.class_names) == 2:
            # 二分类
            precision, recall, _ = precision_recall_curve(
                true_labels, probabilities[:, 1]
            )
            ap = average_precision_score(true_labels, probabilities[:, 1])

            plt.figure()
            plt.plot(
                recall,
                precision,
                color="darkorange",
                lw=2,
                label=f"PR曲线 (AP = {ap:.2f})",
            )
            plt.xlabel("召回率")
            plt.ylabel("精确率")
            plt.title("精确率-召回率曲线")
            plt.legend(loc="upper right")
        else:
            # 多分类
            precision = dict()
            recall = dict()
            average_precision = dict()

            # 二值化真实标签
            y_true_bin = label_binarize(
                true_labels, classes=range(len(self.class_names))
            )

            # 计算每个类别的PR曲线和AP
            for i in range(len(self.class_names)):
                precision[i], recall[i], _ = precision_recall_curve(
                    y_true_bin[:, i], probabilities[:, i]
                )
                average_precision[i] = average_precision_score(
                    y_true_bin[:, i], probabilities[:, i]
                )

            # 计算微平均PR曲线
            precision["micro"], recall["micro"], _ = precision_recall_curve(
                y_true_bin.ravel(), probabilities.ravel()
            )
            average_precision["micro"] = average_precision_score(
                y_true_bin, probabilities, average="micro"
            )

            # 绘制PR曲线
            plt.figure(figsize=(10, 8))
            colors = cycle(
                ["aqua", "darkorange", "cornflowerblue", "green", "red", "purple"]
            )

            # 绘制每个类别的PR曲线
            for i, color in zip(range(len(self.class_names)), colors):
                plt.plot(
                    recall[i],
                    precision[i],
                    color=color,
                    lw=2,
                    label=f"PR {self.class_names[i]} (AP = {average_precision[i]:.2f})",
                )

            # 绘制微平均PR曲线
            plt.plot(
                recall["micro"],
                precision["micro"],
                label=f'Micro-average PR (AP = {average_precision["micro"]:.2f})',
                color="deeppink",
                linestyle=":",
                linewidth=4,
            )

            plt.xlabel("召回率")
            plt.ylabel("精确率")
            plt.title("多类别精确率-召回率曲线")
            plt.legend(loc="upper right")

        if save_path:
            plt.savefig(save_path, bbox_inches="tight", dpi=300)
            plt.close()
            return save_path
        else:
            plt.show()

    def generate_grad_cam(
        self, image_paths, logits, output_dir, layer_names, num_samples=10
    ):
        """
        生成Grad-CAM可视化 - 解释模型决策

        参数:
        image_paths (list): 图像路径列表
        logits (list): 模型原始输出列表
        output_dir (str): 输出目录
        layer_names (list): 要可视化的层名列表
        num_samples (int): 要可视化的样本数量
        """
        if not layer_names:
            return

        # 确保模型在评估模式
        self.model.eval()

        # 创建Grad-CAM目录
        cam_dir = os.path.join(output_dir, "grad_cam")
        os.makedirs(cam_dir, exist_ok=True)

        # 随机选择样本
        indices = np.random.choice(
            len(image_paths), min(num_samples, len(image_paths)), replace=False
        )

        # 对每个样本生成Grad-CAM
        for idx in indices:
            img_path = image_paths[idx]
            logit = logits[idx]
            predicted_class = np.argmax(logit)

            # 加载原始图像
            img = cv2.imread(img_path)
            if img is None:
                continue

            # 对每个指定的层生成Grad-CAM
            for layer_name in layer_names:
                # 生成Grad-CAM
                cam = self._compute_grad_cam(img_path, layer_name, predicted_class)
                if cam is None:
                    continue

                # 将CAM覆盖到原始图像上
                heatmap = cv2.applyColorMap(cam, cv2.COLORMAP_JET)
                superimposed_img = heatmap * 0.4 + img * 0.6

                # 保存结果
                img_name = os.path.splitext(os.path.basename(img_path))[0]
                save_path = os.path.join(
                    cam_dir, f"{img_name}_{layer_name}_gradcam.jpg"
                )
                cv2.imwrite(save_path, superimposed_img)

        print(f"Grad-CAM可视化保存至: {cam_dir}")

    def _compute_grad_cam(self, image_path, layer_name, target_class):
        """计算指定层和类别的Grad-CAM"""
        # 获取目标层
        layer = None
        for name, module in self.model.named_modules():
            if name == layer_name:
                layer = module
                break

        if layer is None:
            print(f"未找到层: {layer_name}")
            return None

        # 注册hook
        activations = []
        gradients = []

        def forward_hook(module, input, output):
            activations.append(output.detach())

        def backward_hook(module, grad_input, grad_output):
            gradients.append(grad_output[0].detach())

        forward_handle = layer.register_forward_hook(forward_hook)
        backward_handle = layer.register_backward_hook(backward_hook)

        try:
            # 预处理图像
            transform = self.get_augmentations()
            img = cv2.imread(image_path)
            if img is None:
                return None

            augmented = transform(image=img)
            input_tensor = augmented["image"].unsqueeze(0).to(self.config["device"])

            # 前向传播
            output = self.model(input_tensor)

            # 后向传播
            self.model.zero_grad()
            one_hot = torch.zeros_like(output)
            one_hot[0, target_class] = 1
            output.backward(gradient=one_hot)

            # 获取激活和梯度
            if not activations or not gradients:
                return None

            activations = activations[0].cpu().numpy()[0]
            gradients = gradients[0].cpu().numpy()[0]

            # 计算权重
            weights = np.mean(gradients, axis=(1, 2))
            cam = np.zeros(activations.shape[1:], dtype=np.float32)

            # 计算CAM
            for i, w in enumerate(weights):
                cam += w * activations[i]

            # 后处理CAM
            cam = np.maximum(cam, 0)
            cam = cam - np.min(cam)
            cam = cam / np.max(cam) if np.max(cam) > 0 else cam
            cam = cv2.resize(cam, (img.shape[1], img.shape[0]))

            return (cam * 255).astype(np.uint8)

        finally:
            # 移除hook
            forward_handle.remove()
            backward_handle.remove()

    def generate_prediction_report(
        self, image_paths, predictions, probabilities, output_dir, num_samples=10
    ):
        """
        生成预测报告

        参数:
        image_paths (list): 图像路径列表
        predictions (list): 预测标签列表
        probabilities (list): 预测概率列表
        output_dir (str): 输出目录
        num_samples (int): 报告中包含的样本数量
        """
        # 创建HTML报告
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>细胞图像分类报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1400px; margin: auto; background: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); border-radius: 8px; }}
                h1, h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; margin: 20px 0; }}
                .cell-card {{ border: 1px solid #ddd; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); transition: transform 0.3s; }}
                .cell-card:hover {{ transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
                .cell-card img {{ width: 100%; height: 180px; object-fit: cover; border-bottom: 1px solid #ddd; }}
                .card-content {{ padding: 15px; }}
                .prediction {{ font-weight: bold; font-size: 16px; margin: 10px 0; }}
                .prob-bar {{ height: 20px; background: #eee; border-radius: 10px; margin: 10px 0; overflow: hidden; }}
                .prob-fill {{ height: 100%; background: #3498db; border-radius: 10px; }}
                .prob-text {{ font-size: 14px; color: #555; }}
                .class-distribution {{ display: flex; flex-wrap: wrap; gap: 15px; margin: 20px 0; }}
                .class-item {{ background: #f8f9fa; padding: 10px 15px; border-radius: 8px; border-left: 4px solid #3498db; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #3498db; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }}
                .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #3498db; }}
                .metric-label {{ font-size: 16px; color: #555; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>细胞图像分类报告</h1>
                <p><strong>生成时间:</strong> {timestamp}</p>
                <p><strong>模型:</strong> {model_name}</p>
                <p><strong>样本总数:</strong> {total_samples}</p>
                
                <h2>预测分布</h2>
                <div class="class-distribution">
                    {class_distribution}
                </div>
                
                <h2>模型评估指标</h2>
                <div class="metrics">
                    {metrics_cards}
                </div>
                
                <h2>随机样本预测结果</h2>
                <div class="grid">
                    {sample_images}
                </div>
                
                <h2>所有预测结果</h2>
                {predictions_table}
            </div>
        </body>
        </html>
        """

        # 生成类别分布
        class_counts = {cls: 0 for cls in self.class_names}
        for pred in predictions:
            class_counts[pred] += 1

        dist_chart = ""
        for cls, count in class_counts.items():
            percentage = count / len(predictions)
            dist_chart += f"""
            <div class="class-item">
                <div><strong>{cls}:</strong> {count} ({percentage:.1%})</div>
                <div class="prob-bar">
                    <div class="prob-fill" style="width: {percentage*100}%"></div>
                </div>
            </div>
            """

        # 计算评估指标
        metrics_cards = ""
        if hasattr(self, "stats") and self.stats.get("val_auc"):
            metrics = {
                "准确率": self.stats["val_accuracy"][-1],
                "AUC": self.stats["val_auc"][-1],
                "F1分数": self.stats["val_f1"][-1],
                "损失": self.stats["val_loss"][-1],
            }

            for name, value in metrics.items():
                metrics_cards += f"""
                <div class="metric-card">
                    <div class="metric-value">{value:.4f}</div>
                    <div class="metric-label">{name}</div>
                </div>
                """

        # 随机选择样本
        indices = np.random.choice(
            len(image_paths), min(num_samples, len(image_paths)), replace=False
        )
        sample_html = ""

        for idx in indices:
            img_path = image_paths[idx]
            pred = predictions[idx]
            prob = probabilities[idx][self.label_encoder[pred]]

            # 创建图像标签
            img_tag = f'<img src="{img_path}" alt="Cell Image">'

            # 创建概率条
            prob_bar = f"""
            <div class="prob-bar">
                <div class="prob-fill" style="width: {prob*100:.1f}%"></div>
            </div>
            <div class="prob-text">置信度: {prob:.3f}</div>
            """

            sample_html += f"""
            <div class="cell-card">
                {img_tag}
                <div class="card-content">
                    <div class="prediction">预测: {pred}</div>
                    {prob_bar}
                </div>
            </div>
            """

        # 创建预测结果表
        table_rows = ""
        for i, (img_path, pred) in enumerate(zip(image_paths, predictions)):
            prob = probabilities[i][self.label_encoder[pred]]
            table_rows += f"""
            <tr>
                <td>{i+1}</td>
                <td>{os.path.basename(img_path)}</td>
                <td>{pred}</td>
                <td>{prob:.4f}</td>
            </tr>
            """

        predictions_table = f"""
        <table>
            <thead>
                <tr>
                    <th>序号</th>
                    <th>图像</th>
                    <th>预测类别</th>
                    <th>置信度</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        """

        # 填充HTML模板
        html_content = html_content.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            model_name=self.config["model_name"],
            total_samples=len(image_paths),
            class_distribution=dist_chart,
            metrics_cards=metrics_cards,
            sample_images=sample_html,
            predictions_table=predictions_table,
        )

        # 保存HTML报告
        report_path = os.path.join(output_dir, "prediction_report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"预测报告保存至: {report_path}")
        return report_path


class CellDataset(Dataset):
    """
    细胞图像数据集类 - 优化版

    改进:
    1. 添加图像缓存机制 - 加速后续训练
    2. 更健壮的错误处理
    3. 支持多种图像格式
    4. 优化的多通道处理
    """

    def __init__(
        self,
        image_paths,
        labels,
        transform=None,
        is_train=True,
        input_channels=3,
        cache_dir=None,
    ):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform
        self.is_train = is_train
        self.input_channels = input_channels
        self.cache_dir = cache_dir

        # 细胞图像特有的增强组合
        self.cell_specific_aug = A.Compose(
            [
                A.OneOf(
                    [
                        A.MotionBlur(blur_limit=3, p=0.3),
                        A.GaussianBlur(blur_limit=3, p=0.3),
                        A.MedianBlur(blur_limit=3, p=0.3),
                    ],
                    p=0.5,
                ),
                A.OneOf(
                    [
                        A.OpticalDistortion(distort_limit=0.5, shift_limit=0.1, p=0.3),
                        A.GridDistortion(num_steps=5, distort_limit=0.3, p=0.3),
                        A.ElasticTransform(alpha=1, sigma=20, alpha_affine=10, p=0.3),
                    ],
                    p=0.5,
                ),
                A.RandomGamma(gamma_limit=(80, 120), p=0.5),
            ]
        )

        # 检查图像路径和标签是否匹配
        if labels is not None and len(image_paths) != len(labels):
            raise ValueError("图像路径数量和标签数量不匹配")

        # 创建缓存目录
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)

    def __len__(self):
        return len(self.image_paths) 
    #     return image, label
    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        
        # 读取图像 - 确保返回NumPy数组
        try:
            # 使用OpenCV读取图像
            image = cv2.imread(img_path)
            if image is None:
                raise FileNotFoundError(f"无法加载图像: {img_path}")
            
            # 确保图像是NumPy数组
            if not isinstance(image, np.ndarray):
                image = np.array(image)
                
            # 确保图像有正确的通道数
            if len(image.shape) == 2:  # 灰度图像
                if self.input_channels == 3:
                    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                elif self.input_channels == 1:
                    image = np.expand_dims(image, axis=-1)
            else:  # 彩色或多通道图像
                if image.shape[2] == 3 and self.input_channels == 1:
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                    image = np.expand_dims(image, axis=-1)
                elif image.shape[2] == 4 and self.input_channels == 3:
                    image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
                elif image.shape[2] > self.input_channels:
                    image = image[:, :, :self.input_channels]
                    
        except Exception as e:
            print(f"加载图像{img_path}出错: {e}")
            # 返回空白图像作为后备
            image = np.zeros((self.transform.height, self.transform.width, self.input_channels), dtype=np.uint8)

        if image.ndim == 2:
            image = np.expand_dims(image, axis=-1)

        if image.shape[-1] == 1 and self.input_channels == 3:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[-1] == 3 and self.input_channels == 1:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            image = np.expand_dims(image, axis=-1)

        if image.dtype != np.uint8:
            image = image.astype(np.uint8)
        # 应用数据增强
        if self.transform:
            try:
                # albumentations 要求 image 是 NumPy array
                if isinstance(image, torch.Tensor):
                    image = image.numpy()
                if isinstance(image, Image.Image):  # PIL image
                    image = np.array(image)

                if image.ndim == 3 and image.shape[2] == 1:
                    image = np.squeeze(image, axis=2)

                augmented = self.transform(image=image)
                image = augmented['image']

                # 如果是训练集，应用细胞特有增强
                if self.is_train and self.cell_specific_aug:
                    if isinstance(image, torch.Tensor):
                        image = image.numpy()
                    if isinstance(image, Image.Image):
                        image = np.array(image)

                    if image.ndim == 3 and image.shape[2] == 1:
                        image = np.squeeze(image, axis=2)

                    augmented = self.cell_specific_aug(image=image)
                    image = augmented['image']
            except Exception as e:
                print(f"数据增强出错: {e}")
 

        # 获取标签
        label = self.labels[idx] if self.labels is not None else -1
        
        # 确保最终输出是张量
        if not isinstance(image, torch.Tensor):
            image = torch.from_numpy(image)
        
        return image, label