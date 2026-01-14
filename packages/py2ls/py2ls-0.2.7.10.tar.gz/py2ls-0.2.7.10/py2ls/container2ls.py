"""
通用容器调度器 (Universal Container Scheduler)
=============================================

一个企业级的、生产就绪的命令执行框架，支持本地执行、容器化执行（Docker/Apptainer）
以及HPC集群调度（SLURM/PBS/Torque）。提供完整的作业管理、监控、重试和资源管理功能。

核心特性：  
多后端支持：Local, Docker, Apptainer, SLURM, PBS
完整的作业管理：提交、执行、监控、取消
智能重试机制：指数退避、条件重试
资源管理：CPU、内存、GPU等资源请求和限制
优先级队列：支持作业优先级调度
超时监控：自动检测和取消超时作业
结果缓存：避免重复执行相同命令
持久化存储：SQLite数据库存储作业和结果
插件系统：可扩展的插件架构
健康检查：全面的系统健康监控
指标收集：性能指标和统计信息
命令行接口：完整的CLI支持
设计原则：
---------
- **统一接口**: 所有后端使用相同的API
- **配置驱动**: 通过配置类管理复杂参数
- **类型安全**: 完整的类型注解
- **可观测性**: 内置监控和日志
- **可扩展性**: 插件架构，易于扩展新功能

快速开始：
---------
```python
from universal_scheduler import ContainerScheduler, Backend, ResourceRequest

# 创建调度器实例
scheduler = ContainerScheduler()

# 运行简单命令
result = scheduler.run("echo 'Hello, World!'", backend=Backend.LOCAL)

# 使用Docker容器
result = scheduler.run(
    cmd="python -c 'import numpy; print(numpy.__version__)'",
    backend=Backend.DOCKER,
    image="python:3.9-slim",
    mounts={"/data": "/data"}
)

# 提交SLURM作业
result = scheduler.run(
    cmd="python train_model.py",
    backend=Backend.SLURM,
    resource=ResourceRequest(cpus=8, memory_gb=32, gpus=1),
    job_name="model_training"
)

# 文件结构建议：
universal_scheduler/
├── __init__.py          # 主模块
├── scheduler.py         # 主调度器类
├── models.py           # 数据模型（ResourceRequest, JobResult等）
├── plugins.py          # 插件系统
├── storage.py          # 存储和缓存
├── monitors.py         # 监控和指标
├── backends.py         # 后端实现
├── cli.py             # 命令行接口
├── config/
│   └── default.yaml   # 默认配置
└── examples/          # 示例代码

"""

import subprocess
import shlex
import time
import logging
import os
import signal
import sys
import tempfile
import json
import hashlib
import pickle
import sqlite3
import uuid
import socket
import threading
import inspect
import asyncio
import heapq
import random
import multiprocessing as mp
from pathlib import Path
from typing import Dict, List, Optional, Union, Callable, Any, Tuple, Set, Type
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, Future, ProcessPoolExecutor
from abc import ABC, abstractmethod
from functools import wraps, lru_cache
from contextlib import contextmanager
import warnings

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    warnings.warn("PyYAML not installed, YAML config support disabled")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    warnings.warn("psutil not installed, resource monitoring limited")

# ============================================================================
# 核心枚举和数据类型
# ============================================================================

class Backend(Enum):
    """支持的执行后端"""
    LOCAL = "local"
    DOCKER = "docker"
    APPTAINER = "apptainer"
    SLURM = "slurm"
    PBS = "pbs"
    KUBERNETES = "kubernetes"
    AWS_BATCH = "aws_batch"
    AZURE_BATCH = "azure_batch"

class JobPriority(Enum):
    """作业优先级"""
    LOWEST = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3
    HIGHEST = 4
    CRITICAL = 5

class JobStatus(Enum):
    """作业状态"""
    CREATED = "created"
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    SUSPENDED = "suspended"
    UNKNOWN = "unknown"

class ResourceType(Enum):
    """资源类型"""
    CPU = "cpu"
    GPU = "gpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    TIME = "time"

# ============================================================================
# 核心数据类
# ============================================================================

@dataclass
class ResourceRequest:
    """
    资源请求配置
    定义作业所需的计算资源，包括CPU、内存、GPU等。
    支持不同后端的资源映射。
    """
    cpus: int = 1
    memory_gb: float = 1.0
    memory_mb: Optional[int] = None
    gpus: int = 0
    gpu_type: Optional[str] = None
    time_minutes: Optional[int] = None
    time_hours: Optional[int] = None
    partition: Optional[str] = None
    queue: Optional[str] = None
    nodes: int = 1
    tasks_per_node: int = 1
    account: Optional[str] = None
    reservation: Optional[str] = None
    qos: Optional[str] = None
    walltime: Optional[str] = None
    exclusive: bool = False
    constraints: Optional[str] = None
    features: Optional[str] = None
    
    def __post_init__(self):
        """后初始化处理，确保内存单位一致"""
        if self.memory_mb is None and self.memory_gb is not None:
            self.memory_mb = int(self.memory_gb * 1024)
        
        # 确保时间单位一致
        if self.time_hours is not None and self.time_minutes is None:
            self.time_minutes = self.time_hours * 60
        elif self.time_minutes is not None and self.time_hours is None:
            self.time_hours = self.time_minutes / 60
    
    @property
    def total_cpus(self) -> int:
        """总CPU核心数"""
        return self.cpus * self.nodes * self.tasks_per_node

    def to_slurm_directives(self) -> Dict[str, str]:
        """转换为SLURM指令"""
        directives = {}
        if self.cpus > 1:
            directives["--cpus-per-task"] = str(self.cpus)
        if self.memory_mb:
            directives["--mem"] = f"{self.memory_mb}M"
        if self.gpus > 0:
            gres = f"gpu:{self.gpus}"
            if self.gpu_type:
                gres = f"gpu:{self.gpu_type}:{self.gpus}"
            directives["--gres"] = gres
        if self.time_minutes:
            directives["--time"] = str(self.time_minutes)
        if self.partition:
            directives["--partition"] = self.partition
        if self.account:
            directives["--account"] = self.account
        if self.qos:
            directives["--qos"] = self.qos
        if self.nodes > 1:
            directives["--nodes"] = str(self.nodes)
        if self.tasks_per_node > 1:
            directives["--ntasks-per-node"] = str(self.tasks_per_node)
        if self.exclusive:
            directives["--exclusive"] = ""
        if self.constraints:
            directives["--constraint"] = self.constraints
        return directives
    
    def to_pbs_directives(self) -> Dict[str, str]:
        """转换为PBS指令"""
        directives = {}
        directives["-l nodes"] = f"{self.nodes}:ppn={self.cpus}"
        if self.memory_mb:
            directives["-l mem"] = f"{self.memory_mb}mb"
        if self.time_hours:
            directives["-l walltime"] = f"{self.time_hours}:00:00"
        if self.queue:
            directives["-q"] = self.queue
        if self.gpus > 0:
            directives["-l gpus"] = str(self.gpus)
            if self.gpu_type:
                directives["-l gputype"] = self.gpu_type
        return directives

@dataclass
class RetryConfig:
    """
    重试策略配置
    定义作业失败时的重试行为，支持指数退避、条件重试等策略。
    """
    max_attempts: int = 1
    delay_seconds: float = 1.0
    backoff_factor: float = 2.0
    max_delay_seconds: float = 300.0
    jitter_seconds: float = 0.0
    retry_on_exit_codes: List[int] = field(default_factory=list)
    retry_on_timeout: bool = True
    retry_on_signal: bool = False
    retry_on_memory_error: bool = True
    retry_on_disk_full: bool = True
    retry_on_network_error: bool = True
    retry_condition: Optional[Callable[['JobResult'], bool]] = None

    def get_delay(self, attempt: int) -> float:
        """计算第attempt次重试的延迟时间"""
        delay = self.delay_seconds * (self.backoff_factor ** (attempt - 1))
        delay = min(delay, self.max_delay_seconds)
        
        # 添加抖动
        if self.jitter_seconds > 0:
            delay += random.uniform(-self.jitter_seconds, self.jitter_seconds)
            delay = max(0, delay)
        
        return delay

    def should_retry(self, result: 'JobResult', attempt: int) -> bool:
        """判断是否需要重试"""
        if attempt >= self.max_attempts:
            return False
        
        # 检查退出码
        if result.exit_code is not None:
            if self.retry_on_exit_codes:
                if result.exit_code in self.retry_on_exit_codes:
                    return True
            elif result.exit_code != 0:
                return True
        
        # 检查超时
        if result.status == JobStatus.TIMEOUT and self.retry_on_timeout:
            return True
        
        # 检查信号
        if result.exit_code is not None and result.exit_code < 0 and self.retry_on_signal:
            return True
        
        # 检查错误信息中的关键词
        error_msg = (result.error_message or "").lower()
        stderr = (result.stderr or "").lower()
        
        if self.retry_on_memory_error and any(
            keyword in error_msg or keyword in stderr 
            for keyword in ["memory", "oom", "out of memory"]
        ):
            return True
        
        if self.retry_on_disk_full and any(
            keyword in error_msg or keyword in stderr
            for keyword in ["disk full", "no space", "quota exceeded"]
        ):
            return True
        
        if self.retry_on_network_error and any(
            keyword in error_msg or keyword in stderr
            for keyword in ["network", "connection", "timeout", "refused"]
        ):
            return True
        
        # 自定义条件
        if self.retry_condition and self.retry_condition(result):
            return True
        
        return False

@dataclass
class ExecutionConfig:
    """
    执行配置
    定义命令执行的详细配置，包括工作目录、环境变量、挂载点等。
    """
    workdir: Optional[Path] = None
    env: Dict[str, str] = field(default_factory=dict)
    mounts: Dict[Path, Path] = field(default_factory=dict)
    shell: str = "/bin/bash"
    clean_temp: bool = True
    capture_output: bool = True
    stdout: Optional[Path] = None
    stderr: Optional[Path] = None
    stdin: Optional[str] = None
    timeout: Optional[int] = None
    check: bool = False
    silent: bool = False
    user: Optional[str] = None
    group: Optional[str] = None
    network_mode: Optional[str] = None
    security_opts: Optional[List[str]] = None
    ulimits: Optional[Dict[str, Tuple[int, int]]] = None
    tmpfs: Optional[Dict[str, str]] = None
    read_only: bool = False
    detach: bool = False

    def __post_init__(self):
        """确保路径是绝对路径"""
        if self.workdir is not None:
            self.workdir = Path(self.workdir).resolve()
        if self.stdout is not None:
            self.stdout = Path(self.stdout).resolve()
        if self.stderr is not None:
            self.stderr = Path(self.stderr).resolve()
        
        # 转换挂载路径
        mounts = {}
        for host_path, container_path in self.mounts.items():
            mounts[Path(host_path).resolve()] = Path(container_path)
        self.mounts = mounts

@dataclass
class JobResult:
    """
    作业执行结果
    封装作业的执行结果，包括状态、退出码、输出、时间统计等。
    """
    job_id: str
    status: JobStatus
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    attempts: int = 0
    error_message: Optional[str] = None
    backend: Optional[str] = None
    command: Optional[str] = None
    resource_usage: Optional[Dict[str, Any]] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    parent_job_id: Optional[str] = None

    def success(self) -> bool:
        """作业是否成功完成"""
        return self.status == JobStatus.COMPLETED and (self.exit_code == 0 or self.exit_code is None)

    def failed(self) -> bool:
        """作业是否失败"""
        return self.status in {JobStatus.FAILED, JobStatus.TIMEOUT}

    def running(self) -> bool:
        """作业是否正在运行"""
        return self.status == JobStatus.RUNNING

    def cancelled(self) -> bool:
        """作业是否被取消"""
        return self.status == JobStatus.CANCELLED

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于序列化"""
        data = asdict(self)
        data['status'] = self.status.value
        return data

    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_json(cls, json_str: str) -> 'JobResult':
        """从JSON字符串创建JobResult"""
        data = json.loads(json_str)
        data['status'] = JobStatus(data['status'])
        if data['start_time']:
            data['start_time'] = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        if data['end_time']:
            data['end_time'] = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        return cls(**data)

@dataclass
class JobDependency:
    """
    作业依赖关系
    定义作业之间的依赖关系，支持复杂的工作流。
    """
    job_id: str
    condition: Optional[Callable[[JobResult], bool]] = None
    timeout: Optional[float] = None
    propagate_status: bool = True

@dataclass
class JobDefinition:
    """
    作业定义
    完整定义作业的所有属性和配置。
    """
    cmd: str
    backend: Backend = Backend.LOCAL
    image: Optional[str] = None
    config: ExecutionConfig = field(default_factory=ExecutionConfig)
    resource: ResourceRequest = field(default_factory=ResourceRequest)
    retry: RetryConfig = field(default_factory=RetryConfig)
    job_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority: JobPriority = JobPriority.NORMAL
    dependencies: List[JobDependency] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    callback: Optional[Callable[[JobResult], Any]] = None
    result_handler: Optional[Callable[[JobResult], JobResult]] = None

    def __post_init__(self):
        if self.job_id is None:
            self.job_id = f"job_{uuid.uuid4().hex[:8]}"
        if self.name is None:
            self.name = self.job_id

# ============================================================================
# 配置管理
# ============================================================================

@dataclass
class SchedulerConfig:
    """
    调度器配置
    完整的调度器配置，支持从YAML文件加载和保存。
    """
    default_backend: Backend = Backend.LOCAL
    default_image: Optional[str] = None
    max_concurrent: int = 4
    database_url: Optional[str] = None
    cache_dir: Optional[Path] = None
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    enable_priority_queue: bool = False
    enable_timeout_monitor: bool = True
    health_check_interval: int = 30
    cleanup_interval: int = 300
    web_monitor_enabled: bool = False
    web_monitor_port: int = 8080
    
    # 资源限制
    max_cpu_percent: float = 90.0
    max_memory_percent: float = 90.0
    max_disk_percent: float = 85.0
    
    # 缓存配置
    cache_max_size_mb: int = 1024
    cache_max_age_days: int = 30
    
    # 数据库配置
    db_cleanup_days: int = 90
    db_backup_days: int = 7
    
    def __post_init__(self):
        if self.cache_dir is not None:
            self.cache_dir = Path(self.cache_dir)
        if self.log_file is not None:
            self.log_file = Path(self.log_file)
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> 'SchedulerConfig':
        """从文件加载配置"""
        if not YAML_AVAILABLE:
            return cls()
            
        if config_path is None:
            # 查找默认配置文件位置
            possible_paths = [
                Path("config/scheduler.yaml"),
                Path("scheduler.yaml"),
                Path("~/.universal-scheduler/config.yaml").expanduser(),
                Path("/etc/universal-scheduler/config.yaml")
            ]
            
            for path in possible_paths:
                if path.exists():
                    config_path = path
                    break
        
        if config_path and config_path.exists():
            with open(config_path) as f:
                data = yaml.safe_load(f)
            
            # 转换字符串为枚举
            if "default_backend" in data and isinstance(data["default_backend"], str):
                data["default_backend"] = Backend(data["default_backend"])
            
            return cls(**data)
        
        return cls()  # 返回默认配置
    
    def save(self, config_path: Path):
        """保存配置到文件"""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required to save configuration")
            
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            data = self.to_dict()
            # 转换枚举为字符串以便YAML序列化
            if "default_backend" in data:
                data["default_backend"] = data["default_backend"].value
            yaml.dump(data, f, default_flow_style=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        # 转换枚举
        if isinstance(data["default_backend"], Backend):
            data["default_backend"] = data["default_backend"].value
        # 转换路径
        for key in ["cache_dir", "log_file"]:
            if data[key] is not None:
                data[key] = str(data[key])
        return data
    
    def validate(self) -> List[str]:
        """验证配置，返回错误列表"""
        errors = []
        
        if self.max_concurrent <= 0:
            errors.append("max_concurrent must be positive")
        
        if self.max_cpu_percent <= 0 or self.max_cpu_percent > 100:
            errors.append("max_cpu_percent must be between 0 and 100")
        
        if self.cache_dir and not self.cache_dir.parent.exists():
            errors.append(f"Cache directory parent does not exist: {self.cache_dir.parent}")
        
        return errors

# ============================================================================
# 插件系统
# ============================================================================

class Plugin(ABC):
    """
    插件基类
    扩展调度器功能的插件接口，可以添加监控、日志、缓存等功能。
    """
    
    @abstractmethod
    def on_job_submit(self, job: JobDefinition) -> None:
        """作业提交时调用"""
        pass

    @abstractmethod
    def on_job_start(self, job_id: str) -> None:
        """作业开始时调用"""
        pass

    @abstractmethod
    def on_job_complete(self, result: JobResult) -> None:
        """作业完成时调用"""
        pass

    @abstractmethod
    def on_error(self, error: Exception) -> None:
        """发生错误时调用"""
        pass

class NotificationPlugin(Plugin):
    """发送通知的插件"""
    
    def __init__(self, webhook_url: Optional[str] = None, email: Optional[str] = None):
        self.webhook_url = webhook_url
        self.email = email
        self.notification_count = 0
    
    def on_job_submit(self, job: JobDefinition) -> None:
        self._send_notification(f"Job submitted: {job.name} ({job.job_id})")
    
    def on_job_start(self, job_id: str) -> None:
        self._send_notification(f"Job started: {job_id}")
    
    def on_job_complete(self, result: JobResult) -> None:
        status = "SUCCESS" if result.success() else "FAILED"
        self._send_notification(f"Job completed: {result.job_id} - {status}")
    
    def on_error(self, error: Exception) -> None:
        self._send_notification(f"Error: {str(error)}", level="ERROR")
    
    def _send_notification(self, message: str, level: str = "INFO"):
        """发送通知"""
        self.notification_count += 1
        timestamp = datetime.now().isoformat()
        full_message = f"[{timestamp}] [{level}] {message}"
        
        # 控制台输出
        print(full_message)
        
        # Webhook通知
        if self.webhook_url:
            try:
                import requests
                requests.post(self.webhook_url, json={"message": full_message}, timeout=5)
            except ImportError:
                print("requests module not installed, webhook disabled")
            except Exception as e:
                print(f"Webhook failed: {e}")
        
        # 邮件通知（简化示例）
        if self.email and level == "ERROR":
            print(f"Would send email to {self.email}: {full_message}")

class ResourceLogger(Plugin):
    """资源使用日志插件"""
    
    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file
        self.resource_logs = []
    
    def on_job_submit(self, job: JobDefinition) -> None:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "submit",
            "job_id": job.job_id,
            "name": job.name,
            "resource": {
                "cpus": job.resource.cpus,
                "memory_gb": job.resource.memory_gb,
                "gpus": job.resource.gpus
            }
        }
        self.resource_logs.append(log_entry)
        print(f"[RESOURCE] Job {job.job_id} submitted with resource: {job.resource}")
    
    def on_job_start(self, job_id: str) -> None:
        print(f"[RESOURCE] Job {job_id} started")
    
    def on_job_complete(self, result: JobResult) -> None:
        if result.resource_usage:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": "complete",
                "job_id": result.job_id,
                "resource_usage": result.resource_usage,
                "duration": result.duration
            }
            self.resource_logs.append(log_entry)
            print(f"[RESOURCE] Job {result.job_id} used: {result.resource_usage}")
    
    def on_error(self, error: Exception) -> None:
        print(f"[RESOURCE] Error: {error}")
    
    def save_logs(self):
        """保存资源日志到文件"""
        if self.log_file:
            with open(self.log_file, 'w') as f:
                json.dump(self.resource_logs, f, indent=2, default=str)

# ============================================================================
# 监控和指标收集
# ============================================================================

class MetricsCollector:
    """
    指标收集器
    收集和报告作业执行的各种指标。
    """
    
    def __init__(self):
        self._metrics = {
            "jobs_total": 0,
            "jobs_completed": 0,
            "jobs_failed": 0,
            "jobs_running": 0,
            "total_duration": 0.0,
            "total_cpu_hours": 0.0,
            "total_memory_gb_hours": 0.0,
            "retries_total": 0,
            "backend_stats": {},
            "resource_stats": {},
            "timestamps": []
        }
        self._lock = threading.Lock()

    def record_job_start(self, job: JobDefinition):
        """记录作业开始"""
        with self._lock:
            self._metrics["jobs_total"] += 1
            self._metrics["jobs_running"] += 1
            
            # 记录后端统计
            backend = job.backend.value
            self._metrics["backend_stats"].setdefault(backend, 0)
            self._metrics["backend_stats"][backend] += 1

    def record_job_complete(self, result: JobResult, job: JobDefinition):
        """记录作业完成"""
        with self._lock:
            self._metrics["jobs_running"] -= 1
            
            if result.success():
                self._metrics["jobs_completed"] += 1
            else:
                self._metrics["jobs_failed"] += 1
            
            # 记录时长
            if result.duration:
                self._metrics["total_duration"] += result.duration
                
                # 计算资源使用
                if job.resource:
                    cpu_hours = job.resource.total_cpus * result.duration / 3600
                    self._metrics["total_cpu_hours"] += cpu_hours
                    
                    if job.resource.memory_gb:
                        mem_hours = job.resource.memory_gb * result.duration / 3600
                        self._metrics["total_memory_gb_hours"] += mem_hours
            
            # 记录重试次数
            if result.attempts > 1:
                self._metrics["retries_total"] += (result.attempts - 1)
            
            # 记录时间戳
            self._metrics["timestamps"].append({
                "job_id": result.job_id,
                "start_time": result.start_time.isoformat() if result.start_time else None,
                "end_time": result.end_time.isoformat() if result.end_time else None,
                "status": result.status.value,
                "backend": job.backend.value
            })

    def get_metrics(self) -> Dict[str, Any]:
        """获取所有指标"""
        with self._lock:
            metrics = self._metrics.copy()
        
        # 计算成功率
        if metrics["jobs_total"] > 0:
            metrics["success_rate"] = metrics["jobs_completed"] / metrics["jobs_total"]
        else:
            metrics["success_rate"] = 0.0
        
        # 计算平均时长
        completed = metrics["jobs_completed"] + metrics["jobs_failed"]
        if completed > 0:
            metrics["avg_duration"] = metrics["total_duration"] / completed
        else:
            metrics["avg_duration"] = 0.0
        
        return metrics

    def reset(self):
        """重置指标"""
        with self._lock:
            self._metrics = {
                "jobs_total": 0,
                "jobs_completed": 0,
                "jobs_failed": 0,
                "jobs_running": 0,
                "total_duration": 0.0,
                "total_cpu_hours": 0.0,
                "total_memory_gb_hours": 0.0,
                "retries_total": 0,
                "backend_stats": {},
                "resource_stats": {},
                "timestamps": []
            }

class ResourceMonitor:
    """资源使用监控"""
    def __init__(self):
        self.start_time = datetime.now()
        self.resource_usage = {}
        self._lock = threading.Lock()

    def record_usage(self, job_id: str, usage: Dict[str, Any]):
        """记录资源使用"""
        with self._lock:
            self.resource_usage[job_id] = {
                "timestamp": datetime.now(),
                "usage": usage
            }

    def get_system_usage(self) -> Dict[str, Any]:
        """获取系统资源使用情况"""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not installed"}
        
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_total_gb": memory.total / (1024**3),
                "memory_used_gb": memory.used / (1024**3),
                "memory_percent": memory.percent,
                "disk_total_gb": disk.total / (1024**3),
                "disk_used_gb": disk.used / (1024**3),
                "disk_percent": disk.percent,
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
            }
        except Exception as e:
            return {"error": str(e)}

    def get_job_usage(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取作业资源使用"""
        with self._lock:
            return self.resource_usage.get(job_id)

# ============================================================================
# 存储和缓存
# ============================================================================

class JobStore:
    """
    作业存储
    持久化存储作业定义和结果，支持查询和历史记录。
    """
    
    def __init__(self, db_path: Union[str, Path] = "jobs.db"):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            # 作业表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    cmd TEXT,
                    backend TEXT,
                    image TEXT,
                    config_json TEXT,
                    resource_json TEXT,
                    retry_json TEXT,
                    priority INTEGER,
                    tags_json TEXT,
                    metadata_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 结果表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS job_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT,
                    attempt INTEGER,
                    status TEXT,
                    exit_code INTEGER,
                    stdout TEXT,
                    stderr TEXT,
                    error_message TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration REAL,
                    resource_usage_json TEXT,
                    metrics_json TEXT,
                    tags_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES jobs (job_id)
                )
            """)
            
            # 索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_job_results_job_id ON job_results (job_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_job_results_status ON job_results (status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_job_results_start_time ON job_results (start_time)")
            
            conn.commit()

    def save_job(self, job: JobDefinition):
        """保存作业定义"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO jobs 
                (job_id, name, description, cmd, backend, image, config_json, 
                resource_json, retry_json, priority, tags_json, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.job_id,
                job.name,
                job.description,
                job.cmd,
                job.backend.value,
                job.image,
                json.dumps(asdict(job.config)),
                json.dumps(asdict(job.resource)),
                json.dumps(asdict(job.retry)),
                job.priority.value,
                json.dumps(job.tags),
                json.dumps(job.metadata)
            ))
            conn.commit()

    def save_result(self, result: JobResult):
        """保存作业结果"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO job_results 
                (job_id, attempt, status, exit_code, stdout, stderr, error_message,
                start_time, end_time, duration, resource_usage_json, metrics_json, tags_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.job_id,
                result.attempts,
                result.status.value,
                result.exit_code,
                result.stdout,
                result.stderr,
                result.error_message,
                result.start_time.isoformat() if result.start_time else None,
                result.end_time.isoformat() if result.end_time else None,
                result.duration,
                json.dumps(result.resource_usage) if result.resource_usage else None,
                json.dumps(result.metrics),
                json.dumps(result.tags)
            ))
            conn.commit()

    def get_job(self, job_id: str) -> Optional[JobDefinition]:
        """获取作业定义"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM jobs WHERE job_id = ?
            """, (job_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # 重建作业定义
            try:
                config_data = json.loads(row[6])
                resource_data = json.loads(row[7])
                retry_data = json.loads(row[8])
                tags = json.loads(row[10])
                metadata = json.loads(row[11])
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for job {job_id}: {e}")
                return None
            
            job = JobDefinition(
                job_id=row[0],
                name=row[1],
                description=row[2],
                cmd=row[3],
                backend=Backend(row[4]),
                image=row[5],
                config=ExecutionConfig(**config_data),
                resource=ResourceRequest(**resource_data),
                retry=RetryConfig(**retry_data),
                priority=JobPriority(row[9]),
                tags=tags,
                metadata=metadata
            )
            
            return job

    def get_job_history(self, job_id: str) -> List[JobResult]:
        """获取作业历史结果"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM job_results 
                WHERE job_id = ? 
                ORDER BY attempt
            """, (job_id,))
            
            results = []
            for row in cursor.fetchall():
                try:
                    result = JobResult(
                        job_id=row[1],
                        status=JobStatus(row[3]),
                        exit_code=row[4],
                        stdout=row[5],
                        stderr=row[6],
                        error_message=row[7],
                        start_time=datetime.fromisoformat(row[8].replace('Z', '+00:00')) if row[8] else None,
                        end_time=datetime.fromisoformat(row[9].replace('Z', '+00:00')) if row[9] else None,
                        duration=row[10],
                        attempts=row[2],
                        resource_usage=json.loads(row[11]) if row[11] else None,
                        metrics=json.loads(row[12]) if row[12] else {},
                        tags=json.loads(row[13]) if row[13] else {}
                    )
                    results.append(result)
                except Exception as e:
                    print(f"Error loading result for job {job_id}: {e}")
            
            return results

    def search_jobs(
        self,
        status: Optional[JobStatus] = None,
        backend: Optional[Backend] = None,
        tags: Optional[Dict[str, str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[JobDefinition]:
        """搜索作业"""
        query = "SELECT job_id FROM jobs WHERE 1=1"
        params = []
        
        if status:
            # 需要连接结果表
            query += " AND job_id IN (SELECT DISTINCT job_id FROM job_results WHERE status = ?)"
            params.append(status.value)
        
        if backend:
            query += " AND backend = ?"
            params.append(backend.value)
        
        if tags:
            for key, value in tags.items():
                query += f" AND json_extract(tags_json, '$.{key}') = ?"
                params.append(value)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            job_ids = [row[0] for row in cursor.fetchall()]
            
            jobs = []
            for job_id in job_ids:
                job = self.get_job(job_id)
                if job:
                    jobs.append(job)
            
            return jobs

    def cleanup_old_jobs(self, days: int = 30):
        """清理旧作业"""
        cutoff = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            # 删除旧结果
            conn.execute("""
                DELETE FROM job_results 
                WHERE job_id IN (
                    SELECT job_id FROM jobs 
                    WHERE created_at < ?
                )
            """, (cutoff.isoformat(),))
            
            # 删除旧作业
            conn.execute("""
                DELETE FROM jobs WHERE created_at < ?
            """, (cutoff.isoformat(),))
            
            conn.commit()

class ResultCache:
    """
    结果缓存
    缓存作业结果，支持结果复用和增量计算。
    """
    
    def __init__(self, cache_dir: Union[str, Path] = ".job_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = self.cache_dir / "index.json"
        self._index = self._load_index()
        self._lock = threading.Lock()

    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        """加载索引"""
        if self._index_file.exists():
            try:
                with open(self._index_file) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_index(self):
        """保存索引"""
        with open(self._index_file, 'w') as f:
            json.dump(self._index, f, indent=2)

    def compute_key(
        self,
        cmd: str,
        backend: Backend = Backend.LOCAL,
        image: Optional[str] = None,
        mounts: Optional[Dict[Path, Path]] = None,
        workdir: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        resource: Optional[ResourceRequest] = None
    ) -> str:
        """
        计算缓存键
        基于命令和配置生成唯一的缓存键，相同配置返回相同键。
        """
        import hashlib
        
        components = {
            "cmd": cmd,
            "backend": backend.value,
            "image": image or "",
            "mounts": json.dumps(sorted((str(k), str(v)) for k, v in (mounts or {}).items())),
            "workdir": str(workdir) if workdir else "",
            "env": json.dumps(sorted((k, v) for k, v in (env or {}).items())),
            "resource": json.dumps(asdict(resource)) if resource else ""
        }
        
        content = json.dumps(components, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def set(self, key: str, result: JobResult, ttl_seconds: int = 86400):
        """
        设置缓存
        """
        with self._lock:
            # 保存结果
            cache_file = self.cache_dir / f"{key}.pkl"
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(result, f)
                
                # 更新索引
                self._index[key] = {
                    "created": datetime.now().isoformat(),
                    "expires": (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat(),
                    "size": cache_file.stat().st_size,
                    "job_id": result.job_id,
                    "status": result.status.value
                }
                self._save_index()
            except Exception as e:
                print(f"Error saving cache: {e}")

    def get(self, key: str) -> Optional[JobResult]:
        """获取缓存结果"""
        with self._lock:
            if not self.has(key):
                return None
            
            cache_file = self.cache_dir / f"{key}.pkl"
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                # 缓存损坏，删除
                self.delete(key)
                return None

    def has(self, key: str) -> bool:
        """检查缓存是否存在且有效"""
        with self._lock:
            if key not in self._index:
                return False
            
            entry = self._index[key]
            expires = datetime.fromisoformat(entry["expires"])
            
            if datetime.now() > expires:
                self.delete(key)
                return False
            
            cache_file = self.cache_dir / f"{key}.pkl"
            return cache_file.exists()

    def delete(self, key: str):
        """删除缓存"""
        with self._lock:
            if key in self._index:
                cache_file = self.cache_dir / f"{key}.pkl"
                if cache_file.exists():
                    cache_file.unlink()
                del self._index[key]
                self._save_index()

    def cleanup(self, max_size_mb: int = 1024, max_age_days: int = 30):
        """清理缓存"""
        with self._lock:
            now = datetime.now()
            total_size_mb = 0
            
            # 收集需要删除的键
            to_delete = []
            
            for key, entry in list(self._index.items()):
                cache_file = self.cache_dir / f"{key}.pkl"
                
                # 检查过期
                expires = datetime.fromisoformat(entry["expires"])
                created = datetime.fromisoformat(entry["created"])
                
                if now > expires:
                    to_delete.append(key)
                elif (now - created).days > max_age_days:
                    to_delete.append(key)
                elif cache_file.exists():
                    total_size_mb += entry["size"] / (1024 * 1024)
                    if total_size_mb > max_size_mb:
                        to_delete.append(key)
            
            # 删除
            for key in to_delete:
                self.delete(key)
            
            # 按创建时间排序，删除最旧的
            if total_size_mb > max_size_mb:
                sorted_keys = sorted(
                    self._index.keys(),
                    key=lambda k: datetime.fromisoformat(self._index[k]["created"])
                )
                while total_size_mb > max_size_mb and sorted_keys:
                    key = sorted_keys.pop(0)
                    if key in self._index:
                        total_size_mb -= self._index[key]["size"] / (1024 * 1024)
                        self.delete(key)

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._lock:
            total_size = 0
            count = 0
            status_counts = {}
            
            for entry in self._index.values():
                total_size += entry["size"]
                count += 1
                status = entry["status"]
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                "count": count,
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "status_counts": status_counts
            }

# ============================================================================
# 队列和监控
# ============================================================================

class PriorityJobQueue:
    """优先作业队列"""
    def __init__(self):
        self._queue = []
        self._lock = threading.Lock()
        self._stats = {
            "jobs_pushed": 0,
            "jobs_popped": 0,
            "max_size": 0
        }
    
    def push(self, job: JobDefinition):
        with self._lock:
            heapq.heappush(self._queue, (-job.priority.value, time.time(), job.job_id, job))
            self._stats["jobs_pushed"] += 1
            self._stats["max_size"] = max(self._stats["max_size"], len(self._queue))
    
    def pop(self) -> Optional[JobDefinition]:
        with self._lock:
            if self._queue:
                _, _, job_id, job = heapq.heappop(self._queue)
                self._stats["jobs_popped"] += 1
                return job
        return None
    
    def peek(self) -> Optional[JobDefinition]:
        """查看队列中的下一个作业但不移除"""
        with self._lock:
            if self._queue:
                _, _, _, job = self._queue[0]
                return job
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        with self._lock:
            stats = self._stats.copy()
            stats["current_size"] = len(self._queue)
            stats["avg_wait_time"] = self._calculate_avg_wait_time()
            return stats
    
    def _calculate_avg_wait_time(self) -> float:
        """计算平均等待时间"""
        if not self._queue:
            return 0.0
        
        now = time.time()
        total_wait = 0.0
        count = 0
        
        for _, enqueue_time, _, _ in self._queue:
            total_wait += (now - enqueue_time)
            count += 1
        
        return total_wait / count if count > 0 else 0.0
    
    def get_queue_snapshot(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取队列快照"""
        with self._lock:
            snapshot = []
            # 复制并排序队列
            sorted_queue = sorted(self._queue, key=lambda x: (-x[0], x[1]))
            for priority_neg, enqueue_time, job_id, job in sorted_queue[:limit]:
                snapshot.append({
                    "job_id": job_id,
                    "name": job.name,
                    "priority": JobPriority(-priority_neg).name,
                    "enqueued_at": datetime.fromtimestamp(enqueue_time).isoformat(),
                    "wait_time_seconds": time.time() - enqueue_time,
                    "backend": job.backend.value,
                    "cmd_preview": job.cmd[:100] + ("..." if len(job.cmd) > 100 else "")
                })
            return snapshot

class TimeoutMonitor:
    """作业超时监控"""
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self._monitored_jobs = {}
        self._lock = threading.Lock()
        self._stats = {
            "jobs_timed_out": 0,
            "preemptive_cancellations": 0
        }
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
    
    def add_job(self, job_id: str, timeout_seconds: Optional[float] = None):
        """添加要监控的作业"""
        if timeout_seconds is None or timeout_seconds <= 0:
            return
        
        with self._lock:
            self._monitored_jobs[job_id] = {
                "start_time": time.time(),
                "timeout": timeout_seconds,
                "warned": False
            }
    
    def remove_job(self, job_id: str):
        """移除监控的作业"""
        with self._lock:
            if job_id in self._monitored_jobs:
                job_info = self._monitored_jobs[job_id]
                if job_info.get("warned", False):
                    self._stats["preemptive_cancellations"] += 1
                del self._monitored_jobs[job_id]
    
    def _monitor_loop(self):
        """监控循环"""
        while True:
            try:
                now = time.time()
                jobs_to_cancel = []
                
                with self._lock:
                    for job_id, job_info in list(self._monitored_jobs.items()):
                        elapsed = now - job_info["start_time"]
                        timeout = job_info["timeout"]
                        
                        # 提前警告（80%超时）
                        if not job_info["warned"] and elapsed > timeout * 0.8:
                            self._warn_about_timeout(job_id, elapsed, timeout)
                            job_info["warned"] = True
                        
                        # 超时取消
                        if elapsed > timeout:
                            jobs_to_cancel.append(job_id)
                            self._stats["jobs_timed_out"] += 1
                
                # 在锁外取消作业
                for job_id in jobs_to_cancel:
                    self.scheduler.logger.warning(f"[{job_id}] Job timeout, cancelling")
                    self.scheduler.cancel(job_id)
                    self.remove_job(job_id)
                
                time.sleep(1)
                
            except Exception as e:
                self.scheduler.logger.error(f"Timeout monitor error: {e}")
                time.sleep(5)
    
    def _warn_about_timeout(self, job_id: str, elapsed: float, timeout: float):
        """超时警告"""
        self.scheduler.logger.warning(
            f"[{job_id}] Job is approaching timeout: "
            f"{elapsed:.1f}/{timeout:.1f} seconds ({elapsed/timeout:.1%})"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取监控统计"""
        with self._lock:
            stats = self._stats.copy()
            stats["currently_monitored"] = len(self._monitored_jobs)
            return stats

# ============================================================================
# 主调度器类
# ============================================================================

class ContainerScheduler:
    """
    通用容器调度器
    企业级的命令执行框架，支持多种后端、资源管理、重试机制、监控等。
    """
    
    def __init__(
        self,
        default_backend: Backend = Backend.LOCAL,
        default_image: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        max_concurrent: int = 4,
        metrics_collector: Optional[MetricsCollector] = None,
        job_store: Optional[JobStore] = None,
        result_cache: Optional[ResultCache] = None,
        plugins: Optional[List[Plugin]] = None,
        enable_web_monitor: bool = False,
        web_port: int = 8080,
        config: Optional[SchedulerConfig] = None,
        enable_priority_queue: bool = False,
        enable_timeout_monitor: bool = True,
    ):
        """
        初始化调度器
        
        Args:
            default_backend: 默认执行后端
            default_image: 默认容器镜像
            logger: 日志记录器
            max_concurrent: 最大并发作业数
            metrics_collector: 指标收集器
            job_store: 作业存储
            result_cache: 结果缓存
            plugins: 插件列表
            enable_web_monitor: 是否启用Web监控
            web_port: Web监控端口
            config: 调度器配置
            enable_priority_queue: 是否启用优先级队列
            enable_timeout_monitor: 是否启用超时监控
        """
        # 配置
        self.config = config or SchedulerConfig(
            default_backend=default_backend,
            max_concurrent=max_concurrent
        )
        self.default_backend = self.config.default_backend
        self.default_image = default_image
        self.max_concurrent = self.config.max_concurrent
        
        # 日志
        if logger is None:
            logger = logging.getLogger(__name__)
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.setLevel(getattr(logging, self.config.log_level))
        self.logger = logger
        
        # 核心组件
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.job_store = job_store
        self.result_cache = result_cache
        self.plugins = plugins or []
        self.resource_monitor = ResourceMonitor()
        
        # 队列系统
        self._priority_queue = None
        if enable_priority_queue:
            self._priority_queue = PriorityJobQueue()
            self._queue_thread = threading.Thread(
                target=self._process_queue_loop,
                daemon=True
            )
            self._queue_thread.start()
        
        # 超时监控
        self._timeout_monitor = None
        if enable_timeout_monitor:
            self._timeout_monitor = TimeoutMonitor(self)
        
        # 执行器和状态管理
        self._executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self._futures: Dict[str, Future] = {}
        self._results: Dict[str, JobResult] = {}
        self._job_definitions: Dict[str, JobDefinition] = {}
        self._lock = threading.RLock()
        
        # 信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # 清理线程
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True
        )
        self._cleanup_thread.start()
        
        # 健康检查线程
        self._health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self._health_check_thread.start()
        
        self.logger.info(f"Scheduler initialized with backend={self.default_backend}, max_concurrent={self.max_concurrent}")

    def _signal_handler(self, signum, frame):
        """处理中断信号"""
        self.logger.warning(f"Received signal {signum}, shutting down...")
        self.shutdown()

    def _cleanup_loop(self):
        """清理循环"""
        while True:
            time.sleep(self.config.cleanup_interval)
            try:
                self._cleanup_stale_jobs()
                if self.result_cache:
                    self.result_cache.cleanup(
                        max_size_mb=self.config.cache_max_size_mb,
                        max_age_days=self.config.cache_max_age_days
                    )
                if self.job_store:
                    self.job_store.cleanup_old_jobs(days=self.config.db_cleanup_days)
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")

    def _health_check_loop(self):
        """健康检查循环"""
        while True:
            try:
                time.sleep(self.config.health_check_interval)
                health = self.health_check()
                if health["status"] != "healthy":
                    self.logger.warning(f"Health check failed: {health}")
            except Exception as e:
                self.logger.error(f"Health check error: {e}")

    def _cleanup_stale_jobs(self):
        """清理过时的作业"""
        with self._lock:
            stale_time = datetime.now() - timedelta(hours=24)
            stale_jobs = []
            
            for job_id, future in list(self._futures.items()):
                if future.done():
                    stale_jobs.append(job_id)
            
            for job_id in stale_jobs:
                if job_id in self._futures:
                    del self._futures[job_id]

    def _process_queue_loop(self):
        """处理优先级队列的循环"""
        while True:
            try:
                if self._priority_queue:
                    job = self._priority_queue.pop()
                    if job:
                        # 检查是否有足够的资源
                        if self._has_enough_resources(job):
                            self.submit(job, wait=False)
                        else:
                            # 放回队列稍后重试
                            time.sleep(5)
                            self._priority_queue.push(job)
                
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Queue processing error: {e}")
                time.sleep(1)

    def _has_enough_resources(self, job: JobDefinition) -> bool:
        """检查是否有足够资源运行作业"""
        try:
            if not PSUTIL_AVAILABLE:
                return True
            
            # 获取系统资源
            system_usage = self.resource_monitor.get_system_usage()
            
            if "error" in system_usage:
                return True
            
            # 检查CPU
            if "cpu_percent" in system_usage:
                if system_usage["cpu_percent"] > self.config.max_cpu_percent:
                    self.logger.debug(f"CPU usage too high: {system_usage['cpu_percent']}%")
                    return False
            
            # 检查内存
            if job.resource.memory_gb:
                available_memory_gb = (system_usage.get("memory_total_gb", 0) - 
                                     system_usage.get("memory_used_gb", 0))
                if available_memory_gb < job.resource.memory_gb:
                    self.logger.debug(f"Insufficient memory: {available_memory_gb:.1f}GB available, {job.resource.memory_gb:.1f}GB required")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Resource check error: {e}")
            return True

    def _build_command(
        self,
        job: JobDefinition
    ) -> Tuple[List[str], Optional[Path]]:
        """
        构建执行命令
        
        Args:
            job: 作业定义
            
        Returns:
            (命令部分列表, 临时脚本路径)
        """
        backend = job.backend
        cmd = job.cmd
        image = job.image or self.default_image
        config = job.config
        resource = job.resource
        
        if backend == Backend.LOCAL:
            return [config.shell, "-c", cmd], None
        
        elif backend == Backend.DOCKER:
            if not image:
                raise ValueError("Docker backend requires image")
            
            parts = ["docker", "run", "--rm", "-i"]
            
            # 挂载卷
            for host_path, container_path in config.mounts.items():
                parts += ["-v", f"{host_path}:{container_path}"]
            
            # 工作目录
            if config.workdir:
                parts += ["-w", str(config.workdir)]
            
            # 环境变量
            for key, value in config.env.items():
                parts += ["-e", f"{key}={shlex.quote(str(value))}"]
            
            # 用户
            if config.user:
                parts += ["-u", config.user]
            
            # 网络
            if config.network_mode:
                parts += ["--network", config.network_mode]
            
            # 安全选项
            if config.security_opts:
                for opt in config.security_opts:
                    parts += ["--security-opt", opt]
            
            # 资源限制
            if resource:
                parts += ["--cpus", str(resource.cpus)]
                if resource.memory_mb:
                    parts += ["--memory", f"{resource.memory_mb}m"]
            
            parts.append(image)
            parts += [config.shell, "-c", cmd]
            
            return parts, None
        
        elif backend == Backend.APPTAINER:
            if not image:
                raise ValueError("Apptainer backend requires image")
            
            parts = ["apptainer", "exec", "--containall"]
            
            # 挂载卷
            for host_path, container_path in config.mounts.items():
                parts += ["--bind", f"{host_path}:{container_path}"]
            
            # 工作目录
            if config.workdir:
                parts += ["--pwd", str(config.workdir)]
            
            # 环境变量
            for key, value in config.env.items():
                parts += ["--env", f"{key}={shlex.quote(str(value))}"]
            
            # 确保镜像存在
            image_path = Path(image)
            if not image_path.exists():
                self.logger.info(f"Pulling image: {image}")
                pull_cmd = ["apptainer", "pull", "--force", str(image_path), f"docker://{image}"]
                subprocess.run(pull_cmd, check=False, capture_output=True)
            
            parts.append(str(image_path))
            parts += [config.shell, "-c", cmd]
            
            return parts, None
        
        elif backend == Backend.SLURM:
            # 创建SLURM脚本
            return self._build_slurm_script(job)
        
        elif backend == Backend.PBS:
            # 创建PBS脚本
            return self._build_pbs_script(job)
        
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def _build_slurm_script(self, job: JobDefinition) -> Tuple[List[str], Path]:
        """构建SLURM脚本"""
        # 创建临时目录
        temp_dir = Path(tempfile.mkdtemp(prefix="slurm_"))
        script_path = temp_dir / f"{job.job_id}.sh"
        
        # 构建脚本内容
        script_lines = ["#!/bin/bash"]
        
        # SLURM指令
        directives = job.resource.to_slurm_directives()
        for key, value in directives.items():
            if value:
                script_lines.append(f"#SBATCH {key}={value}")
            else:
                script_lines.append(f"#SBATCH {key}")
        
        # 输出文件
        if job.config.stdout:
            script_lines.append(f"#SBATCH --output={job.config.stdout}")
        if job.config.stderr:
            script_lines.append(f"#SBATCH --error={job.config.stderr}")
        
        script_lines.append("")
        
        # 环境变量
        for key, value in job.config.env.items():
            script_lines.append(f"export {key}={shlex.quote(str(value))}")
        
        script_lines.append("")
        
        # 容器命令
        if job.image:
            container_cmd = ["apptainer", "exec"]
            for host_path, container_path in job.config.mounts.items():
                container_cmd += ["--bind", f"{host_path}:{container_path}"]
            if job.config.workdir:
                container_cmd += ["--pwd", str(job.config.workdir)]
            container_cmd.append(job.image)
            container_cmd += [job.config.shell, "-c", shlex.quote(job.cmd)]
            script_lines.append(" ".join(container_cmd))
        else:
            if job.config.workdir:
                script_lines.append(f"cd {job.config.workdir}")
            script_lines.append(job.cmd)
        
        # 写入文件
        script_path.write_text("\n".join(script_lines))
        script_path.chmod(0o755)
        
        return ["sbatch", "--parsable", str(script_path)], script_path

    def _build_pbs_script(self, job: JobDefinition) -> Tuple[List[str], Path]:
        """构建PBS脚本"""
        temp_dir = Path(tempfile.mkdtemp(prefix="pbs_"))
        script_path = temp_dir / f"{job.job_id}.pbs"
        
        script_lines = ["#!/bin/bash"]
        
        # PBS指令
        directives = job.resource.to_pbs_directives()
        for key, value in directives.items():
            script_lines.append(f"#PBS {key} {value}")
        
        # 输出文件
        if job.config.stdout:
            script_lines.append(f"#PBS -o {job.config.stdout}")
        if job.config.stderr:
            script_lines.append(f"#PBS -e {job.config.stderr}")
        
        script_lines.append("")
        
        # 环境变量
        for key, value in job.config.env.items():
            script_lines.append(f"export {key}={shlex.quote(str(value))}")
        
        script_lines.append("")
        script_lines.append("cd $PBS_O_WORKDIR")
        
        if job.config.workdir:
            script_lines.append(f"cd {job.config.workdir}")
        
        script_lines.append("")
        
        # 容器命令
        if job.image:
            container_cmd = ["apptainer", "exec"]
            for host_path, container_path in job.config.mounts.items():
                container_cmd += ["--bind", f"{host_path}:{container_path}"]
            container_cmd.append(job.image)
            container_cmd += [job.config.shell, "-c", shlex.quote(job.cmd)]
            script_lines.append(" ".join(container_cmd))
        else:
            script_lines.append(job.cmd)
        
        # 写入文件
        script_path.write_text("\n".join(script_lines))
        script_path.chmod(0o755)
        
        return ["qsub", str(script_path)], script_path

    def _execute_job(
        self,
        job: JobDefinition,
        use_cache: bool = True
    ) -> JobResult:
        """
        执行单个作业
        
        Args:
            job: 作业定义
            use_cache: 是否使用缓存
            
        Returns:
            作业结果
        """
        job_id = job.job_id
        
        # 触发插件事件
        for plugin in self.plugins:
            try:
                plugin.on_job_submit(job)
            except Exception as e:
                self.logger.error(f"Plugin on_job_submit error: {e}")
        
        # 指标收集
        self.metrics_collector.record_job_start(job)
        
        # 检查缓存
        if use_cache and self.result_cache:
            cache_key = self.result_cache.compute_key(
                cmd=job.cmd,
                backend=job.backend,
                image=job.image,
                mounts=job.config.mounts,
                workdir=job.config.workdir,
                env=job.config.env,
                resource=job.resource
            )
            
            if self.result_cache.has(cache_key):
                cached_result = self.result_cache.get(cache_key)
                if cached_result:
                    self.logger.info(f"[{job_id}] Using cached result")
                    
                    # 更新作业ID
                    cached_result.job_id = job_id
                    cached_result.attempts = 1
                    
                    # 触发完成事件
                    for plugin in self.plugins:
                        try:
                            plugin.on_job_complete(cached_result)
                        except Exception as e:
                            self.logger.error(f"Plugin on_job_complete error: {e}")
                    
                    self.metrics_collector.record_job_complete(cached_result, job)
                    
                    # 保存到存储
                    if self.job_store:
                        self.job_store.save_job(job)
                        self.job_store.save_result(cached_result)
                    
                    return cached_result
        
        # 构建命令
        cmd_parts, script_path = self._build_command(job)
        
        result = JobResult(
            job_id=job_id,
            status=JobStatus.RUNNING,
            backend=job.backend.value,
            command=job.cmd,
            tags=job.tags.copy()
        )
        
        result.start_time = datetime.now()
        
        try:
            # 触发开始事件
            for plugin in self.plugins:
                try:
                    plugin.on_job_start(job_id)
                except Exception as e:
                    self.logger.error(f"Plugin on_job_start error: {e}")
            
            # 添加超时监控
            if self._timeout_monitor and job.config.timeout:
                self._timeout_monitor.add_job(job_id, job.config.timeout)
            
            self.logger.info(f"[{job_id}] Starting job: {job.name}")
            if not job.config.silent:
                self.logger.info(f"[{job_id}] Command: {' '.join(cmd_parts)}")
            
            # 准备输出
            stdout_dest = None
            stderr_dest = None
            stdout_file = None
            stderr_file = None
            
            if job.config.capture_output:
                stdout_dest = subprocess.PIPE
                stderr_dest = subprocess.PIPE
            elif job.config.stdout:
                stdout_file = open(job.config.stdout, 'w')
                stdout_dest = stdout_file
            elif job.config.stderr:
                stderr_file = open(job.config.stderr, 'w')
                stderr_dest = stderr_file
            
            # 执行命令
            stdin_input = job.config.stdin.encode() if job.config.stdin else None
            
            process = subprocess.run(
                cmd_parts,
                shell=False,
                check=False,  # 我们手动检查退出码
                timeout=job.config.timeout,
                stdout=stdout_dest,
                stderr=stderr_dest,
                stdin=subprocess.PIPE if job.config.stdin else None,
                text=not job.config.stdin,  # 如果stdin是二进制，text=False
                cwd=job.config.workdir,
                input=stdin_input
            )
            
            # 收集输出
            if job.config.capture_output:
                result.stdout = process.stdout
                result.stderr = process.stderr
                if result.stdout and len(result.stdout) > 10000:  # 限制输出大小
                    result.stdout = result.stdout[:10000] + "... [truncated]"
                if result.stderr and len(result.stderr) > 10000:
                    result.stderr = result.stderr[:10000] + "... [truncated]"
            
            result.exit_code = process.returncode
            
            if process.returncode == 0:
                result.status = JobStatus.COMPLETED
            else:
                result.status = JobStatus.FAILED
                result.error_message = f"Command failed with exit code {process.returncode}"
                
        except subprocess.TimeoutExpired:
            result.status = JobStatus.TIMEOUT
            result.error_message = f"Command timed out after {job.config.timeout} seconds"
        except subprocess.CalledProcessError as e:
            result.status = JobStatus.FAILED
            result.exit_code = e.returncode
            result.error_message = str(e)
            if e.stdout:
                result.stdout = e.stdout
            if e.stderr:
                result.stderr = e.stderr
        except FileNotFoundError as e:
            result.status = JobStatus.FAILED
            result.error_message = f"Command not found: {e}"
        except PermissionError as e:
            result.status = JobStatus.FAILED
            result.error_message = f"Permission denied: {e}"
        except Exception as e:
            result.status = JobStatus.FAILED
            result.error_message = f"Unexpected error: {e}"
        
        finally:
            # 关闭文件
            if stdout_file:
                stdout_file.close()
            if stderr_file:
                stderr_file.close()
            
            # 移除超时监控
            if self._timeout_monitor:
                self._timeout_monitor.remove_job(job_id)
            
            result.end_time = datetime.now()
            if result.start_time and result.end_time:
                result.duration = (result.end_time - result.start_time).total_seconds()
            
            # 清理临时脚本
            if script_path and job.config.clean_temp:
                try:
                    script_path.unlink()
                    script_path.parent.rmdir()
                except Exception as e:
                    self.logger.warning(f"[{job_id}] Failed to clean temp files: {e}")
        
        # 结果处理
        if job.result_handler:
            try:
                result = job.result_handler(result)
            except Exception as e:
                self.logger.error(f"[{job_id}] Result handler failed: {e}")
        
        # 触发完成事件
        for plugin in self.plugins:
            try:
                plugin.on_job_complete(result)
            except Exception as e:
                self.logger.error(f"Plugin on_job_complete error: {e}")
        
        # 指标收集
        self.metrics_collector.record_job_complete(result, job)
        
        # 保存结果
        if self.job_store:
            self.job_store.save_job(job)
            self.job_store.save_result(result)
        
        # 缓存结果
        if use_cache and self.result_cache and result.success():
            cache_key = self.result_cache.compute_key(
                cmd=job.cmd,
                backend=job.backend,
                image=job.image,
                mounts=job.config.mounts,
                workdir=job.config.workdir,
                env=job.config.env,
                resource=job.resource
            )
            self.result_cache.set(cache_key, result)
        
        # 回调函数
        if job.callback:
            try:
                job.callback(result)
            except Exception as e:
                self.logger.error(f"[{job_id}] Callback failed: {e}")
        
        self.logger.info(f"[{job_id}] Job completed with status: {result.status.value}")
        
        # 存储结果
        with self._lock:
            self._results[job_id] = result
        
        return result

    def submit(self, job: JobDefinition, wait: bool = True) -> Union[JobResult, Future]:
        """
        提交作业
        
        Args:
            job: 作业定义
            wait: 是否等待作业完成
            
        Returns:
            如果wait=True返回JobResult，否则返回Future
        """
        # 保存作业定义
        with self._lock:
            self._job_definitions[job.job_id] = job
        
        # 提交到线程池
        future = self._executor.submit(self._execute_job, job)
        
        with self._lock:
            self._futures[job.job_id] = future
        
        if wait:
            try:
                return future.result()
            except Exception as e:
                self.logger.error(f"[{job.job_id}] Job execution failed: {e}")
                result = JobResult(
                    job_id=job.job_id,
                    status=JobStatus.FAILED,
                    error_message=str(e)
                )
                return result
        else:
            return future

    def run(
        self,
        cmd: str,
        backend: Union[Backend, str] = None,
        image: str = None,
        mounts: Dict[Union[str, Path], Union[str, Path]] = None,
        workdir: Union[str, Path] = None,
        env: Dict[str, str] = None,
        dry_run: bool = False,
        resource: Union[ResourceRequest, Dict[str, Any]] = None,
        retry: Union[RetryConfig, Dict[str, Any]] = None,
        config: Union[ExecutionConfig, Dict[str, Any]] = None,
        job_id: str = None,
        wait: bool = True,
        name: str = None,
        description: str = None,
        tags: Dict[str, str] = None,
        priority: Union[JobPriority, int] = JobPriority.NORMAL,
        use_cache: bool = True
    ) -> Union[JobResult, Future]:
        """
        运行命令（简化接口）
        
        Args:
            cmd: 要执行的命令
            backend: 执行后端，默认使用调度器默认后端
            image: 容器镜像
            mounts: 挂载映射 {主机路径: 容器路径}
            workdir: 工作目录
            env: 环境变量
            dry_run: 只打印命令不执行
            resource: 资源请求配置或字典
            retry: 重试配置或字典
            config: 执行配置或字典
            job_id: 作业ID，自动生成如果未提供
            wait: 是否等待作业完成
            name: 作业名称
            description: 作业描述
            tags: 作业标签
            priority: 作业优先级
            use_cache: 是否使用结果缓存
            
        Returns:
            如果wait=True返回JobResult，否则返回Future
        """
        # 参数转换
        if backend is None:
            backend = self.default_backend
        elif isinstance(backend, str):
            backend = Backend(backend)
        
        if isinstance(resource, dict):
            resource = ResourceRequest(**resource)
        elif resource is None:
            resource = ResourceRequest()
        
        if isinstance(retry, dict):
            retry = RetryConfig(**retry)
        elif retry is None:
            retry = RetryConfig()
        
        if isinstance(config, dict):
            config = ExecutionConfig(**config)
        elif config is None:
            config = ExecutionConfig()
        
        # 挂载转换
        mounts_dict = {}
        if mounts:
            for host_path, container_path in mounts.items():
                mounts_dict[Path(host_path)] = Path(container_path)
        
        # 工作目录转换
        if workdir:
            config.workdir = Path(workdir)
        
        # 环境变量
        if env:
            config.env.update(env)
        
        # 挂载点
        if mounts_dict:
            config.mounts.update(mounts_dict)
        
        # 优先级转换
        if isinstance(priority, int):
            priority = JobPriority(priority)
        
        # 创建作业定义
        job = JobDefinition(
            cmd=cmd,
            backend=backend,
            image=image,
            config=config,
            resource=resource,
            retry=retry,
            job_id=job_id,
            name=name,
            description=description,
            priority=priority,
            tags=tags or {}
        )
        
        # 干运行
        if dry_run:
            cmd_parts, _ = self._build_command(job)
            self.logger.info(f"[DRY RUN] Command: {' '.join(cmd_parts)}")
            
            result = JobResult(
                job_id=job.job_id,
                status=JobStatus.COMPLETED,
                command=cmd
            )
            return result
        
        # 提交作业
        return self.submit(job, wait=wait)

    def enqueue(self, job: JobDefinition) -> str:
        """
        将作业加入优先级队列（而不是立即执行）
        
        Args:
            job: 作业定义
            
        Returns:
            作业ID
        """
        if not self._priority_queue:
            raise RuntimeError("Priority queue is not enabled")
        
        # 保存作业定义
        with self._lock:
            self._job_definitions[job.job_id] = job
        
        # 加入优先级队列
        self._priority_queue.push(job)
        
        self.logger.info(f"[{job.job_id}] Job enqueued with priority {job.priority}")
        
        return job.job_id

    def run_many(
        self,
        commands: List[Union[str, Dict[str, Any]]],
        backend: Backend = None,
        max_workers: int = None,
        progress_callback: Callable[[int, int], None] = None,
        stop_on_error: bool = False,
        use_cache: bool = True
    ) -> List[JobResult]:
        """
        批量运行多个命令
        
        Args:
            commands: 命令列表，可以是字符串或配置字典
            backend: 执行后端，覆盖单个命令的后端设置
            max_workers: 最大工作线程数，默认使用调度器设置
            progress_callback: 进度回调函数 (completed, total)
            stop_on_error: 遇到错误是否停止
            use_cache: 是否使用结果缓存
            
        Returns:
            作业结果列表
        """
        if max_workers is None:
            max_workers = self.max_concurrent
        
        # 转换命令为作业定义
        jobs = []
        for i, cmd_spec in enumerate(commands):
            if isinstance(cmd_spec, JobDefinition):
                # 已经是JobDefinition对象
                job = cmd_spec
                # 确保有作业ID
                if not job.job_id:
                    job.job_id = f"batch_{i}_{uuid.uuid4().hex[:4]}"
            elif isinstance(cmd_spec, str):
                # 简单字符串命令
                job = JobDefinition(
                    cmd=cmd_spec,
                    backend=backend or self.default_backend,
                    name=f"batch_{i}",
                    job_id=f"batch_{i}_{uuid.uuid4().hex[:4]}"
                )
            else:
                # 配置字典
                cmd_spec = cmd_spec.copy()
                
                # 提取命令
                cmd = cmd_spec.pop("cmd")
                
                # 处理后端
                if backend is not None and "backend" not in cmd_spec:
                    cmd_spec["backend"] = backend
                
                # 创建作业定义
                try:
                    job = JobDefinition(cmd=cmd, **cmd_spec)
                except TypeError as e:
                    self.logger.error(f"Error creating job from spec {cmd_spec}: {e}")
                    continue
                
                # 如果没有作业ID，生成一个
                if not job.job_id:
                    job.job_id = f"batch_{i}_{uuid.uuid4().hex[:4]}"
                
                # 如果没有名称，使用作业ID
                if not job.name:
                    job.name = job.job_id
            
            jobs.append(job)
        
        total = len(jobs)
        results = []
        completed = 0
        
        # 使用执行器并行运行
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for job in jobs:
                future = executor.submit(self._execute_job, job, use_cache)
                futures.append((job.job_id, future))
            
            for job_id, future in futures:
                try:
                    result = future.result()
                    results.append(result)
                    
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total)
                    
                    # 检查是否需要停止
                    if stop_on_error and result.failed():
                        self.logger.warning(f"Stopping batch due to failed job: {job_id}")
                        break
                        
                except Exception as e:
                    self.logger.error(f"Job {job_id} failed with exception: {e}")
                    
                    error_result = JobResult(
                        job_id=job_id,
                        status=JobStatus.FAILED,
                        error_message=str(e)
                    )
                    results.append(error_result)
                    
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total)
                    
                    if stop_on_error:
                        break
        
        return results

    def cancel(self, job_id: str):
        """取消作业"""
        with self._lock:
            if job_id in self._futures:
                future = self._futures[job_id]
                future.cancel()
                
                # 更新结果
                if job_id in self._results:
                    self._results[job_id].status = JobStatus.CANCELLED
                
                self.logger.info(f"[{job_id}] Job cancelled")
            else:
                self.logger.warning(f"[{job_id}] Job not found or already completed")

    def cancel_all(self):
        """取消所有作业"""
        with self._lock:
            for job_id in list(self._futures.keys()):
                self.cancel(job_id)

    def wait_all(self, timeout: float = None) -> List[JobResult]:
        """等待所有作业完成"""
        results = []
        with self._lock:
            futures = list(self._futures.items())
        
        for job_id, future in futures:
            try:
                result = future.result(timeout=timeout)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error waiting for job {job_id}: {e}")
        
        return results

    def get_job(self, job_id: str) -> Optional[JobDefinition]:
        """获取作业定义"""
        with self._lock:
            return self._job_definitions.get(job_id)

    def get_result(self, job_id: str) -> Optional[JobResult]:
        """获取作业结果"""
        # 首先检查内存中的结果
        with self._lock:
            if job_id in self._results:
                return self._results[job_id]
        
        # 然后检查存储
        if self.job_store:
            history = self.job_store.get_job_history(job_id)
            if history:
                return history[-1]  # 返回最新结果
        
        return None

    def get_status(self, job_id: str) -> Optional[JobStatus]:
        """获取作业状态"""
        result = self.get_result(job_id)
        if result:
            return result.status
        
        # 检查是否在运行
        with self._lock:
            if job_id in self._futures and not self._futures[job_id].done():
                return JobStatus.RUNNING
        
        return None

    def health_check(self) -> Dict[str, Any]:
        """检查调度器健康状况"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # 检查执行器
        health_status["components"]["executor"] = {
            "running": not self._executor._shutdown,
            "active_threads": threading.active_count(),
            "max_workers": self.max_concurrent
        }
        
        # 检查后端可用性
        backend_health = {}
        for backend in [Backend.LOCAL, Backend.DOCKER, Backend.APPTAINER, Backend.SLURM, Backend.PBS]:
            backend_health[backend.value] = self._check_backend_health(backend)
        
        health_status["components"]["backends"] = backend_health
        
        # 检查系统资源
        try:
            system_usage = self.resource_monitor.get_system_usage()
            if "error" in system_usage:
                health_status["components"]["system"] = {"error": system_usage["error"]}
            else:
                health_status["components"]["system"] = {
                    "cpu_percent": system_usage["cpu_percent"],
                    "memory_percent": system_usage["memory_percent"],
                    "disk_percent": system_usage["disk_percent"],
                    "status": "healthy" if system_usage["cpu_percent"] < 95 and 
                                      system_usage["memory_percent"] < 95 else "warning"
                }
        except Exception as e:
            health_status["components"]["system"] = {"error": str(e)}
        
        # 检查存储
        if self.job_store:
            try:
                with sqlite3.connect(self.job_store.db_path) as conn:
                    conn.execute("SELECT 1")
                health_status["components"]["storage"] = {"status": "healthy"}
            except Exception as e:
                health_status["components"]["storage"] = {"error": str(e), "status": "unhealthy"}
                health_status["status"] = "degraded"
        
        # 检查缓存
        if self.result_cache:
            try:
                stats = self.result_cache.get_stats()
                health_status["components"]["cache"] = {
                    "status": "healthy",
                    "count": stats["count"],
                    "size_mb": stats["total_size_mb"]
                }
            except Exception as e:
                health_status["components"]["cache"] = {"error": str(e), "status": "unhealthy"}
                health_status["status"] = "degraded"
        
        # 如果任何组件不健康，更新整体状态
        for component, status in health_status["components"].items():
            if status.get("status") == "unhealthy":
                health_status["status"] = "unhealthy"
                break
            elif status.get("status") == "warning":
                health_status["status"] = "degraded"
        
        return health_status

    def _check_backend_health(self, backend: Backend) -> Dict[str, Any]:
        """检查后端健康状态"""
        try:
            if backend == Backend.LOCAL:
                return {"available": True, "status": "healthy"}
            
            elif backend == Backend.DOCKER:
                result = subprocess.run(
                    ["docker", "info"],
                    capture_output=True,
                    text=True
                )
                return {
                    "available": result.returncode == 0,
                    "status": "healthy" if result.returncode == 0 else "unhealthy"
                }
            
            elif backend == Backend.APPTAINER:
                result = subprocess.run(
                    ["apptainer", "version"],
                    capture_output=True,
                    text=True
                )
                return {
                    "available": result.returncode == 0,
                    "status": "healthy" if result.returncode == 0 else "unhealthy"
                }
            
            elif backend == Backend.SLURM:
                result = subprocess.run(
                    ["sinfo", "--version"],
                    capture_output=True,
                    text=True
                )
                return {
                    "available": result.returncode == 0,
                    "status": "healthy" if result.returncode == 0 else "unhealthy"
                }
            
            elif backend == Backend.PBS:
                result = subprocess.run(
                    ["qstat", "--version"],
                    capture_output=True,
                    text=True
                )
                return {
                    "available": result.returncode == 0,
                    "status": "healthy" if result.returncode == 0 else "unhealthy"
                }
            
            return {"available": False, "status": "unknown"}
            
        except Exception as e:
            return {"available": False, "status": "error", "error": str(e)}

    def get_metrics(self) -> Dict[str, Any]:
        """获取调度器指标"""
        metrics = self.metrics_collector.get_metrics()
        
        # 添加当前状态
        with self._lock:
            current = {
                "jobs_total": len(self._job_definitions),
                "jobs_pending": len([f for f in self._futures.values() if not f.done()]),
                "jobs_running": len([f for f in self._futures.values() if not f.done()]),
                "jobs_completed": len(self._results),
                "backends_available": [b.value for b in Backend]
            }
        
        metrics["current"] = current
        
        # 添加缓存统计
        if self.result_cache:
            metrics["cache"] = self.result_cache.get_stats()
        
        # 添加队列统计
        if self._priority_queue:
            metrics["queue"] = self._priority_queue.get_stats()
        
        # 添加超时监控统计
        if self._timeout_monitor:
            metrics["timeout_monitor"] = self._timeout_monitor.get_stats()
        
        return metrics

    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        if not self._priority_queue:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "stats": self._priority_queue.get_stats(),
            "snapshot": self._priority_queue.get_queue_snapshot()
        }

    def shutdown(self, wait: bool = True, cancel_jobs: bool = True):
        """
        关闭调度器
        
        Args:
            wait: 是否等待正在进行的作业完成
            cancel_jobs: 是否取消正在运行的作业
        """
        self.logger.info("Shutting down scheduler...")
        
        if cancel_jobs:
            self.cancel_all()
        
        self._executor.shutdown(wait=wait)
        
        # 保存插件数据
        for plugin in self.plugins:
            if isinstance(plugin, ResourceLogger):
                plugin.save_logs()
        
        self.logger.info("Scheduler shut down")

    def __del__(self):
        """析构函数"""
        try:
            self.shutdown(wait=False, cancel_jobs=True)
        except:
            pass
    def run_workflow(
        self,
        workflow: List[Dict[str, Any]],
        max_workers: int = None,
        stop_on_error: bool = True,
        name: str = "workflow"
    ) -> Dict[str, JobResult]:
        """
        运行工作流（带依赖关系的作业）
        
        Args:
            workflow: 工作流定义列表，每个元素包含命令和依赖关系
            max_workers: 最大工作线程数
            stop_on_error: 遇到错误是否停止整个工作流
            name: 工作流名称
            
        Returns:
            作业ID到结果的映射
            
        Examples:
            >>> # 简单线性工作流
            >>> workflow = [
            ...     {"cmd": "download_data.sh", "job_id": "download"},
            ...     {"cmd": "process_data.py", "job_id": "process",
            ...      "dependencies": ["download"]},
            ...     {"cmd": "analyze.py", "job_id": "analyze",
            ...      "dependencies": ["process"]}
            ... ]
            >>> results = scheduler.run_workflow(workflow)
            
            >>> # 并行工作流
            >>> workflow = [
            ...     {"cmd": "preprocess.py --input data1.csv", "job_id": "preprocess1"},
            ...     {"cmd": "preprocess.py --input data2.csv", "job_id": "preprocess2"},
            ...     {"cmd": "merge_results.py", "job_id": "merge",
            ...      "dependencies": ["preprocess1", "preprocess2"]}
            ... ]
            >>> results = scheduler.run_workflow(
            ...     workflow,
            ...     max_workers=2,
            ...     name="data_pipeline"
            ... )
        """
        if max_workers is None:
            max_workers = self.max_concurrent
        
        self.logger.info(f"Starting workflow: {name} with {len(workflow)} jobs")
        
        # 创建工作流作业
        jobs = {}
        job_dependencies = {}
        
        for spec in workflow:
            spec = spec.copy()
            
            # 提取作业ID
            job_id = spec.pop("job_id", str(uuid.uuid4().hex[:8]))
            
            # 提取依赖
            dependencies = spec.pop("dependencies", [])
            job_dependencies[job_id] = dependencies
            
            # 创建作业定义
            cmd = spec.pop("cmd")
            # 处理其他参数
            backend = spec.pop("backend", None)
            if isinstance(backend, str):
                backend = Backend(backend)
            elif backend is None:
                backend = self.default_backend
            resource = spec.pop("resource", None)
            retry = spec.pop("retry", None)
            config = spec.pop("config", None)
            
            # 创建配置对象
            if isinstance(resource, dict):
                resource = ResourceRequest(**resource)
            elif resource is None:
                resource = ResourceRequest()
            
            if isinstance(retry, dict):
                retry = RetryConfig(**retry)
            elif retry is None:
                retry = RetryConfig()
            
            if isinstance(config, dict):
                config = ExecutionConfig(**config)
            elif config is None:
                config = ExecutionConfig()
            
            # 后端转换
            if isinstance(backend, str):
                backend = Backend(backend)
            elif backend is None:
                backend = self.default_backend
            
            # 创建作业定义
            job = JobDefinition(
                cmd=cmd,
                backend=backend,
                config=config,
                resource=resource,
                retry=retry,
                job_id=job_id,
                **spec  # 其他参数如name, tags等
            )
            jobs[job_id] = job
        
        # 结果存储
        results = {}
        completed = set()
        failed = set()
        
        # 工作流执行循环
        while len(results) < len(jobs):
            # 找到可以执行的作业（依赖都已满足）
            ready_jobs = []
            
            for job_id, job in jobs.items():
                if job_id in results:
                    continue  # 已经完成
                
                # 检查依赖
                dependencies = job_dependencies.get(job_id, [])
                can_run = True
                
                for dep_id in dependencies:
                    if dep_id not in results:
                        can_run = False
                        break
                    elif results[dep_id].failed():
                        can_run = False
                        break
                
                if can_run:
                    ready_jobs.append(job)
            
            if not ready_jobs:
                # 没有可运行的作业，可能是有循环依赖或依赖失败
                if stop_on_error and failed:
                    self.logger.warning(f"Workflow {name} stopped due to failed dependencies")
                    break
                else:
                    # 检查是否有作业因为循环依赖而无法运行
                    time.sleep(1)
                    continue
            
            # 执行就绪的作业
            batch_results = self.run_many(
                ready_jobs,
                max_workers=min(max_workers, len(ready_jobs)),
                stop_on_error=stop_on_error,
                use_cache=False  # 工作流作业通常不使用缓存
            )
            
            # 更新结果
            for result in batch_results:
                results[result.job_id] = result
                
                if result.success():
                    completed.add(result.job_id)
                else:
                    failed.add(result.job_id)
                    
                    if stop_on_error:
                        self.logger.warning(f"Workflow job failed: {result.job_id}")
            
            # 进度日志
            self.logger.info(
                f"Workflow {name} progress: {len(results)}/{len(jobs)} "
                f"(completed: {len(completed)}, failed: {len(failed)})"
            )
        
        self.logger.info(f"Workflow {name} completed")
        return results
# ============================================================================
# 简化接口函数
# ============================================================================

def run_command(
    cmd: str,
    backend: str = "local",
    image: str = None,
    mounts: Dict[str, str] = None,
    workdir: str = None,
    env: Dict[str, str] = None,
    dry_run: bool = False,
    resource: Dict[str, Any] = None,
    retry: Dict[str, Any] = None,
    **kwargs
) -> JobResult:
    """
    简化接口函数 - 保持与原始版本兼容
    
    Args:
        cmd: 要执行的命令
        backend: local | docker | apptainer | slurm | pbs
        image: 容器镜像
        mounts: 挂载映射
        workdir: 工作目录
        env: 环境变量
        dry_run: 只打印不执行
        resource: 资源请求配置
        retry: 重试配置
        
    Returns:
        作业结果
    """
    # 转换参数
    mounts_dict = None
    if mounts:
        mounts_dict = {Path(k): Path(v) for k, v in mounts.items()}
    
    workdir_path = Path(workdir) if workdir else None
    
    # 创建调度器实例
    scheduler = ContainerScheduler()
    
    # 资源请求
    resource_obj = None
    if resource:
        resource_obj = ResourceRequest(**resource)
    
    # 重试配置
    retry_obj = None
    if retry:
        retry_obj = RetryConfig(**retry)
    
    # 执行配置
    config_kwargs = {}
    for key in ["timeout", "stdout", "stderr", "capture_output", "check", "silent"]:
        if key in kwargs:
            config_kwargs[key] = kwargs[key]
    
    config = ExecutionConfig(
        workdir=workdir_path,
        env=env or {},
        mounts=mounts_dict or {},
        **config_kwargs
    )
    
    # 运行命令
    return scheduler.run(
        cmd=cmd,
        backend=backend,
        image=image,
        config=config,
        resource=resource_obj,
        retry=retry_obj,
        dry_run=dry_run
    )

# ============================================================================
# 命令行接口
# ============================================================================

def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Universal Container Scheduler CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "echo Hello World"
  %(prog)s "python script.py" --backend docker --image python:3.9
  %(prog)s --health
  %(prog)s --stats
  %(prog)s "long_job.sh" --queue --priority high
        """
    )
    
    # 主要模式
    parser.add_argument("command", nargs="?", help="Command to execute")
    parser.add_argument("--config", help="Configuration file path")
    
    # 执行参数
    parser.add_argument("--backend", default="local", 
                       choices=["local", "docker", "apptainer", "slurm", "pbs"],
                       help="Execution backend")
    parser.add_argument("--image", help="Container image")
    parser.add_argument("--workdir", help="Working directory")
    parser.add_argument("--mount", action="append", 
                       help="Mount mapping (host:container)")
    parser.add_argument("--env", action="append", 
                       help="Environment variable (KEY=VALUE)")
    parser.add_argument("--cpus", type=int, default=1, help="CPU cores")
    parser.add_argument("--memory", type=float, help="Memory in GB")
    parser.add_argument("--timeout", type=int, help="Timeout in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    parser.add_argument("--output", help="Output file")
    parser.add_argument("--error", help="Error file")
    parser.add_argument("--retry", type=int, default=1, help="Max retry attempts")
    
    # 队列和调度
    parser.add_argument("--queue", action="store_true", help="Add job to queue instead of immediate execution")
    parser.add_argument("--priority", default="normal", 
                       choices=["lowest", "low", "normal", "high", "highest", "critical"],
                       help="Job priority")
    
    # 监控和管理
    parser.add_argument("--health", action="store_true", help="Check scheduler health")
    parser.add_argument("--stats", action="store_true", help="Show scheduler statistics")
    parser.add_argument("--list-jobs", action="store_true", help="List all jobs")
    parser.add_argument("--queue-status", action="store_true", help="Show queue status")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()

    # 设置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    # 加载配置
    config = None
    if args.config:
        config = SchedulerConfig.load(Path(args.config))
    
    # 创建调度器
    scheduler = ContainerScheduler(
        config=config,
        enable_priority_queue=True if args.queue else False,
        enable_timeout_monitor=True
    )
    
    try:
        # 处理不同模式
        if args.health:
            # 健康检查模式
            health = scheduler.health_check()
            print(json.dumps(health, indent=2, default=str))
            sys.exit(0 if health["status"] == "healthy" else 1)
        
        elif args.stats:
            # 统计模式
            metrics = scheduler.get_metrics()
            print(json.dumps(metrics, indent=2, default=str))
            sys.exit(0)
        
        elif args.queue_status:
            # 队列状态
            queue_status = scheduler.get_queue_status()
            print(json.dumps(queue_status, indent=2, default=str))
            sys.exit(0)
        
        elif args.list_jobs:
            # 列出作业
            if scheduler.job_store:
                jobs = scheduler.job_store.search_jobs(limit=100)
                for job in jobs:
                    result = scheduler.get_result(job.job_id)
                    status = result.status.value if result else "unknown"
                    print(f"{job.job_id}: {job.name} ({job.backend.value}) - {status}")
            else:
                print("Job store not enabled")
            sys.exit(0)
        
        elif args.command:
            # 执行命令模式
            # 解析挂载
            mounts = {}
            if args.mount:
                for mount in args.mount:
                    if ":" in mount:
                        host, container = mount.split(":", 1)
                        mounts[host] = container
            
            # 解析环境变量
            env = {}
            if args.env:
                for env_var in args.env:
                    if "=" in env_var:
                        key, value = env_var.split("=", 1)
                        env[key] = value
            
            # 资源配置
            resource = {}
            if args.cpus > 1:
                resource["cpus"] = args.cpus
            if args.memory:
                resource["memory_gb"] = args.memory
            
            # 执行配置
            config_dict = {}
            if args.timeout:
                config_dict["timeout"] = args.timeout
            if args.output:
                config_dict["stdout"] = args.output
            if args.error:
                config_dict["stderr"] = args.error
            
            # 优先级转换
            priority_map = {
                "lowest": JobPriority.LOWEST,
                "low": JobPriority.LOW,
                "normal": JobPriority.NORMAL,
                "high": JobPriority.HIGH,
                "highest": JobPriority.HIGHEST,
                "critical": JobPriority.CRITICAL
            }
            priority = priority_map[args.priority]
            
            if args.queue:
                # 加入队列
                job = JobDefinition(
                    cmd=args.command,
                    backend=Backend(args.backend),
                    image=args.image,
                    config=ExecutionConfig(
                        workdir=Path(args.workdir) if args.workdir else None,
                        env=env,
                        mounts={Path(k): Path(v) for k, v in mounts.items()},
                        **config_dict
                    ),
                    resource=ResourceRequest(**resource),
                    retry=RetryConfig(max_attempts=args.retry),
                    priority=priority,
                    name="cli_job"
                )
                job_id = scheduler.enqueue(job)
                print(f"Job enqueued with ID: {job_id}")
                print(f"Use --queue-status to check queue status")
            else:
                # 立即执行
                result = scheduler.run(
                    cmd=args.command,
                    backend=args.backend,
                    image=args.image,
                    mounts=mounts,
                    workdir=args.workdir,
                    env=env,
                    dry_run=args.dry_run,
                    resource=resource,
                    retry={"max_attempts": args.retry},
                    config=config_dict,
                    priority=priority
                )
                
                # 输出结果
                if result.stdout:
                    print(result.stdout)
                
                if result.stderr:
                    print(result.stderr, file=sys.stderr)
                
                exit_code = result.exit_code or 0
                if result.success():
                    print(f"Command completed successfully in {result.duration:.2f}s")
                else:
                    print(f"Command failed with exit code {exit_code}: {result.error_message}")
                
                sys.exit(exit_code)
        else:
            # 交互模式
            print("Universal Container Scheduler")
            print("No command specified. Available modes:")
            print("  --health      Check scheduler health")
            print("  --stats       Show scheduler statistics")
            print("  --queue       Add job to queue")
            print("  --list-jobs   List all jobs")
            print("  --queue-status Show queue status")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        scheduler.shutdown(wait=False, cancel_jobs=True)
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        scheduler.shutdown(wait=True, cancel_jobs=False)


# ============================================================================
# 使用示例
# ============================================================================

# if __name__ == "__main__":
#     # 示例代码
#     print("Universal Container Scheduler - Example Usage")
#     print("=" * 50)
    
#     # 示例1: 基本使用
#     print("\n1. Basic Usage:")
#     scheduler = ContainerScheduler()
#     result = scheduler.run("echo 'Hello, World!'")
#     print(f"   Result: {result.status.value}, Output: {result.stdout}")
    
#     # 示例2: 使用Docker容器
#     print("\n2. Docker Container Example:")
#     try:
#         result = scheduler.run(
#             cmd="python -c 'import sys; print(f\"Python {sys.version}\")'",
#             backend="docker",
#             image="python:3.9-slim",
#             dry_run=True  # 干运行，不实际执行
#         )
#         print(f"   Dry run completed for Docker command")
#     except Exception as e:
#         print(f"   Docker not available: {e}")
    
#     # 示例3: 带重试的作业
#     print("\n3. Job with Retry:")
#     result = scheduler.run(
#         cmd="echo 'Test with retry' && exit 1",  # 这个命令会失败
#         retry={"max_attempts": 3, "delay_seconds": 1}
#     )
#     print(f"   Final status: {result.status.value}, Attempts: {result.attempts}")
    
#     # 示例4: 批量作业
#     print("\n4. Batch Jobs:")
#     commands = [f"echo 'Job {i}'" for i in range(3)]
#     results = scheduler.run_many(commands, max_workers=2)
#     print(f"   Completed {len(results)} jobs, {sum(1 for r in results if r.success())} successful")
    
#     # 示例5: 健康检查
#     print("\n5. Health Check:")
#     health = scheduler.health_check()
#     print(f"   Status: {health['status']}")
    
#     # 示例6: 指标收集
#     print("\n6. Metrics:")
#     metrics = scheduler.get_metrics()
#     print(f"   Total jobs: {metrics['jobs_total']}")
#     print(f"   Success rate: {metrics.get('success_rate', 0):.1%}")
    
#     # 清理
#     scheduler.shutdown()
    
#     print("\n" + "=" * 50)
#     print("All examples completed!")
#     print("\nTo use the command line interface:")
#     print("  python universal_scheduler.py --help")
#     print("\nExample commands:")
#     print("  python universal_scheduler.py 'echo Hello'")
#     print("  python universal_scheduler.py --health")
#     print("  python universal_scheduler.py --stats")


# ============================================================================
# 高级使用场景示例
# ============================================================================

def example_data_processing_pipeline():
    """
    示例1: 数据处理流水线
    模拟真实的数据处理工作流：下载 -> 预处理 -> 分析 -> 报告
    """
    print("\n" + "="*60)
    print("示例1: 数据处理流水线")
    print("="*60)
    
    # 创建配置化的调度器
    scheduler = ContainerScheduler(
        max_concurrent=4,
        job_store=JobStore("data_pipeline.db"),
        result_cache=ResultCache(".pipeline_cache"),
        plugins=[
            NotificationPlugin(),
            ResourceLogger()
        ],
        enable_priority_queue=True
    )
    
    # 模拟数据文件
    data_files = [
        "sales_2023_q1.csv",
        "sales_2023_q2.csv", 
        "sales_2023_q3.csv",
        "sales_2023_q4.csv"
    ]
    
    try:
        # 阶段1: 并行下载数据（模拟）
        print("\n阶段1: 下载数据文件...")
        download_jobs = []
        for data_file in data_files:
            job = JobDefinition(
                cmd=f"curl -s https://example.com/data/{data_file} -o {data_file}",
                name=f"download_{data_file}",
                resource=ResourceRequest(cpus=1, memory_gb=2),
                retry=RetryConfig(max_attempts=3, delay_seconds=5),
                tags={"stage": "download", "file": data_file}
            )
            download_jobs.append(job)
        
        # 批量提交下载作业
        download_results = scheduler.run_many(
            [{"cmd": f"echo '模拟下载 {f}' && sleep 1" for f in data_files}],
            progress_callback=lambda c, t: print(f"  下载进度: {c}/{t}")
        )
        
        # 阶段2: 数据预处理
        print("\n阶段2: 数据预处理...")
        preprocess_jobs = []
        for data_file in data_files:
            output_file = data_file.replace(".csv", "_processed.parquet")
            job = JobDefinition(
                cmd=f"python preprocess.py --input {data_file} --output {output_file}",
                name=f"preprocess_{data_file}",
                backend=Backend.DOCKER,
                image="python:3.9-data-science",
                mounts={"/data": "/data"},
                config=ExecutionConfig(
                    workdir=Path("/data"),
                    env={"PYTHONPATH": "/data/scripts"}
                ),
                resource=ResourceRequest(cpus=4, memory_gb=8),
                retry=RetryConfig(max_attempts=2),
                tags={"stage": "preprocess", "file": data_file}
            )
            preprocess_jobs.append(job)
            scheduler.enqueue(job)  # 加入队列
        
        # 等待预处理完成
        print("等待预处理作业完成...")
        scheduler.wait_all()
        
        # 阶段3: 聚合分析
        print("\n阶段3: 聚合分析...")
        analysis_job = JobDefinition(
            cmd="python analyze.py --pattern *_processed.parquet --output analysis_results.json",
            name="aggregate_analysis",
            backend=Backend.SLURM,
            resource=ResourceRequest(
                cpus=8,
                memory_gb=32,
                time_hours=2,
                partition="analysis"
            ),
            tags={"stage": "analysis"}
        )
        
        analysis_result = scheduler.submit(analysis_job, wait=True)
        
        # 阶段4: 生成报告
        print("\n阶段4: 生成报告...")
        report_job = JobDefinition(
            cmd="python generate_report.py --input analysis_results.json --output report.html",
            name="generate_report",
            resource=ResourceRequest(cpus=2, memory_gb=4),
            tags={"stage": "report"}
        )
        
        report_result = scheduler.submit(report_job, wait=True)
        
        # 检查最终结果
        if report_result.success():
            print(f"\n✅ 数据处理流水线完成！")
            print(f"   总作业数: {scheduler.metrics_collector.get_metrics()['jobs_total']}")
            print(f"   成功作业: {scheduler.metrics_collector.get_metrics()['jobs_completed']}")
            print(f"   总耗时: {report_result.duration:.1f}s")
        else:
            print(f"\n❌ 数据处理流水线失败！")
            print(f"   错误信息: {report_result.error_message}")
    
    finally:
        scheduler.shutdown()
        print("调度器已关闭")

def example_machine_learning_training():
    """
    示例2: 机器学习模型训练与超参数搜索
    分布式模型训练和超参数优化
    """
    print("\n" + "="*60)
    print("示例2: 机器学习模型训练")
    print("="*60)
    
    scheduler = ContainerScheduler(
        max_concurrent=8,
        job_store=JobStore("ml_training.db"),
        enable_priority_queue=True
    )
    
    # 超参数搜索空间
    hyperparameters = [
        {"model": "resnet50", "lr": 0.001, "batch_size": 32, "epochs": 50},
        {"model": "resnet50", "lr": 0.01, "batch_size": 64, "epochs": 50},
        {"model": "efficientnet", "lr": 0.001, "batch_size": 32, "epochs": 50},
        {"model": "efficientnet", "lr": 0.01, "batch_size": 64, "epochs": 50},
        {"model": "vit", "lr": 0.0005, "batch_size": 16, "epochs": 100},
        {"model": "vit", "lr": 0.005, "batch_size": 32, "epochs": 100},
    ]
    
    try:
        print(f"开始超参数搜索，共 {len(hyperparameters)} 组配置...")
        
        # 为每组超参数创建训练任务
        training_jobs = []
        for i, params in enumerate(hyperparameters):
            params_str = " ".join([f"--{k} {v}" for k, v in params.items()])
            
            job = JobDefinition(
                cmd=f"python train_model.py {params_str} --data /data/imagenet --output /output/model_{i}.pth",
                name=f"train_model_{i}",
                backend=Backend.SLURM,
                image="pytorch/pytorch:latest",
                config=ExecutionConfig(
                    mounts={
                        Path("/datasets/imagenet"): Path("/data"),
                        Path("/models"): Path("/output")
                    }
                ),
                resource=ResourceRequest(
                    cpus=8,
                    memory_gb=32,
                    gpus=2,
                    gpu_type="a100",
                    time_hours=12,
                    partition="gpu",
                    exclusive=True
                ),
                retry=RetryConfig(
                    max_attempts=2,
                    retry_on_memory_error=True,
                    retry_on_network_error=True
                ),
                tags={
                    "task": "hyperparameter_search",
                    "model": params["model"],
                    "config_id": str(i)
                },
                callback=lambda result, i=i: print(f"  配置 {i} 训练完成: {result.status.value}")
            )
            training_jobs.append(job)
        
        # 批量提交训练作业（并行执行）
        print("提交训练作业...")
        training_results = scheduler.run_many(
            training_jobs,
            max_workers=4,  # 最多同时训练4个模型
            progress_callback=lambda c, t: print(f"  训练进度: {c}/{t}")
        )
        
        # 收集最佳模型
        best_model = None
        best_accuracy = 0.0
        
        for result in training_results:
            if result.success() and result.stdout:
                try:
                    # 从输出中解析指标
                    import json
                    metrics = json.loads(result.stdout)
                    accuracy = metrics.get("val_accuracy", 0)
                    
                    if accuracy > best_accuracy:
                        best_accuracy = accuracy
                        best_model = result
                except:
                    pass
        
        if best_model:
            print(f"\n🎉 找到最佳模型!")
            print(f"   配置ID: {best_model.job_id}")
            print(f"   验证准确率: {best_accuracy:.2%}")
            
            # 评估最佳模型
            print("\n评估最佳模型...")
            eval_job = JobDefinition(
                cmd=f"python evaluate_model.py --model /output/{best_model.job_id}.pth --test_data /data/imagenet_test",
                name="evaluate_best_model",
                backend=Backend.SLURM,
                resource=ResourceRequest(
                    cpus=4,
                    memory_gb=16,
                    gpus=1,
                    time_hours=2
                ),
                tags={"task": "evaluation", "best_model": best_model.job_id}
            )
            
            eval_result = scheduler.submit(eval_job, wait=True)
            
            if eval_result.success():
                print("   评估完成!")
                print(f"   测试准确率: {eval_result.stdout}")
    
    finally:
        scheduler.shutdown()
        print("\nML训练完成!")

def example_bioinformatics_workflow():
    """
    示例3: 生物信息学工作流
    DNA测序数据分析流程
    """
    print("\n" + "="*60)
    print("示例3: 生物信息学工作流")
    print("="*60)
    
    scheduler = ContainerScheduler(
        max_concurrent=6,
        default_backend=Backend.SLURM,
        job_store=JobStore("bioinformatics.db"),
        result_cache=ResultCache(".bio_cache")
    )
    
    # 样本列表
    samples = [
        "sample_001", "sample_002", "sample_003", 
        "sample_004", "sample_005", "sample_006"
    ]
    
    try:
        # 工作流定义
        workflow = []
        
        # 1. 质量控制（并行）
        for sample in samples:
            workflow.append({
                "job_id": f"qc_{sample}",
                "cmd": f"fastqc /data/raw/{sample}.fastq.gz -o /data/qc/{sample}",
                "backend": Backend.LOCAL,
                "resource": {"cpus": 2, "memory_gb": 4},
                "tags": {"stage": "quality_control", "sample": sample}
            })
        
        # 2. 序列比对（有依赖关系）
        for sample in samples:
            workflow.append({
                "job_id": f"align_{sample}",
                "cmd": f"bwa mem -t 8 /data/reference/hg38.fasta /data/raw/{sample}.fastq.gz > /data/aligned/{sample}.sam",
                "dependencies": [f"qc_{sample}"],
                "backend": Backend.SLURM,
                "resource": {"cpus": 8, "memory_gb": 16, "time_hours": 4},
                "tags": {"stage": "alignment", "sample": sample}
            })
        
        # 3. 变异检测（批量处理）
        workflow.append({
            "job_id": "variant_calling",
            "cmd": "gatk HaplotypeCaller -R /data/reference/hg38.fasta -I /data/aligned/*.bam -O /data/variants/all_variants.vcf",
            "dependencies": [f"align_{sample}" for sample in samples],
            "backend": Backend.SLURM,
            "resource": {"cpus": 32, "memory_gb": 64, "time_hours": 8, "partition": "large"},
            "tags": {"stage": "variant_calling"}
        })
        
        # 4. 注释分析
        workflow.append({
            "job_id": "annotation",
            "cmd": "annovar /data/variants/all_variants.vcf /data/annotations/ -buildver hg38",
            "dependencies": ["variant_calling"],
            "backend": Backend.LOCAL,
            "resource": {"cpus": 4, "memory_gb": 8},
            "tags": {"stage": "annotation"}
        })
        
        # 5. 生成报告
        workflow.append({
            "job_id": "generate_report",
            "cmd": "python generate_report.py --vcf /data/variants/all_variants.vcf --output /data/report/final_report.html",
            "dependencies": ["annotation"],
            "tags": {"stage": "report"}
        })
        
        print(f"开始生物信息学工作流，共 {len(workflow)} 个步骤...")
        
        # 运行工作流
        results = scheduler.run_workflow(
            workflow=workflow,
            max_workers=3,
            name="bioinformatics_pipeline",
            stop_on_error=True
        )
        
        # 分析结果
        successful = sum(1 for r in results.values() if r.success())
        total = len(results)
        
        print(f"\n工作流完成: {successful}/{total} 个步骤成功")
        
        if successful == total:
            final_result = results["generate_report"]
            print(f"🎉 分析完成! 报告已生成")
            print(f"   总耗时: {sum(r.duration or 0 for r in results.values()):.1f}秒")
            
            # 显示各阶段耗时
            print("\n各阶段耗时:")
            for job_id, result in results.items():
                if result.duration:
                    print(f"   {job_id}: {result.duration:.1f}s")
    
    finally:
        scheduler.shutdown()

def example_cloud_batch_processing():
    """
    示例4: 云批量处理
    模拟AWS Batch或Azure Batch场景
    """
    print("\n" + "="*60)
    print("示例4: 云批量处理")
    print("="*60)
    
    # 模拟云作业调度
    scheduler = ContainerScheduler(
        max_concurrent=20,  # 高并发
        job_store=JobStore("cloud_batch.db"),
        plugins=[
            NotificationPlugin(),
            ResourceLogger("cloud_resources.json")
        ]
    )
    
    # 模拟大量数据处理任务
    tasks = []
    for i in range(100):
        task = {
            "task_id": f"task_{i:03d}",
            "input_file": f"s3://bucket/input/data_{i}.json",
            "output_file": f"s3://bucket/output/processed_{i}.parquet",
            "complexity": random.choice(["simple", "medium", "complex"])
        }
        tasks.append(task)
    
    try:
        print(f"开始处理 {len(tasks)} 个云任务...")
        
        # 根据任务复杂度分配资源
        job_definitions = []
        for task in tasks:
            if task["complexity"] == "simple":
                cpus = 2
                memory_gb = 4
                priority = JobPriority.LOW
            elif task["complexity"] == "medium":
                cpus = 4
                memory_gb = 8
                priority = JobPriority.NORMAL
            else:  # complex
                cpus = 8
                memory_gb = 16
                priority = JobPriority.HIGH
            
            job = JobDefinition(
                cmd=f"python cloud_processor.py --input {task['input_file']} --output {task['output_file']}",
                name=f"cloud_task_{task['task_id']}",
                backend=Backend.DOCKER,
                image="python:3.9-cloud",
                config=ExecutionConfig(
                    env={
                        "AWS_ACCESS_KEY_ID": "xxx",
                        "AWS_SECRET_ACCESS_KEY": "xxx",
                        "AWS_DEFAULT_REGION": "us-east-1"
                    }
                ),
                resource=ResourceRequest(cpus=cpus, memory_gb=memory_gb),
                retry=RetryConfig(
                    max_attempts=3,
                    backoff_factor=2.0,
                    retry_on_network_error=True
                ),
                priority=priority,
                tags={
                    "cloud": "aws",
                    "task_type": "batch_processing",
                    "complexity": task["complexity"],
                    "task_id": task["task_id"]
                },
                callback=lambda r, t=task: print(f"  任务 {t['task_id']} 完成: {r.status.value}")
            )
            job_definitions.append(job)
        
        # 批量提交（模拟云批量作业）
        print("提交任务到云队列...")
        batch_size = 10  # 每批处理10个任务
        all_results = []
        
        for i in range(0, len(job_definitions), batch_size):
            batch = job_definitions[i:i+batch_size]
            print(f"处理批次 {i//batch_size + 1}/{(len(job_definitions)+batch_size-1)//batch_size}...")
            
            batch_results = scheduler.run_many(
                batch,
                max_workers=10,
                progress_callback=lambda c, t: None  # 静默进度
            )
            all_results.extend(batch_results)
            
            # 批次间短暂暂停
            time.sleep(2)
        
        # 统计结果
        successful = sum(1 for r in all_results if r.success())
        failed = len(all_results) - successful
        
        print(f"\n📊 批量处理完成统计:")
        print(f"   总任务数: {len(all_results)}")
        print(f"   成功: {successful}")
        print(f"   失败: {failed}")
        
        if failed > 0:
            print("\n失败任务:")
            for result in all_results:
                if result.failed():
                    print(f"   {result.job_id}: {result.error_message}")
        
        # 显示资源使用情况
        metrics = scheduler.get_metrics()
        print(f"\n💻 资源使用统计:")
        print(f"   CPU小时: {metrics['total_cpu_hours']:.2f}")
        print(f"   内存GB小时: {metrics['total_memory_gb_hours']:.2f}")
        print(f"   平均作业时长: {metrics.get('avg_duration', 0):.1f}s")
    
    finally:
        scheduler.shutdown()

def example_real_time_monitoring():
    """
    示例5: 实时监控和告警系统
    模拟生产环境监控场景
    """
    print("\n" + "="*60)
    print("示例5: 实时监控系统")
    print("="*60)
    
    # 创建带完整监控的调度器
    scheduler = ContainerScheduler(
        max_concurrent=10,
        job_store=JobStore("monitoring.db"),
        plugins=[
            NotificationPlugin(webhook_url="https://hooks.slack.com/services/XXX"),
            ResourceLogger("monitoring_logs.json")
        ],
        enable_timeout_monitor=True,
        enable_priority_queue=True
    )
    
    # 监控任务定义
    monitoring_tasks = [
        {
            "name": "database_health_check",
            "cmd": "python check_database.py --host db-prod --timeout 30",
            "interval": 60,  # 每60秒执行一次
            "timeout": 45,
            "priority": JobPriority.HIGH
        },
        {
            "name": "api_endpoint_check", 
            "cmd": "curl -f https://api.example.com/health",
            "interval": 30,
            "timeout": 10,
            "retry": {"max_attempts": 2}
        },
        {
            "name": "disk_space_check",
            "cmd": "python check_disk.py --path / --threshold 90",
            "interval": 300,
            "priority": JobPriority.NORMAL
        },
        {
            "name": "service_metrics_collect",
            "cmd": "python collect_metrics.py --services web,api,cache,queue",
            "interval": 60,
            "resource": {"cpus": 2, "memory_gb": 4}
        },
        {
            "name": "log_analysis",
            "cmd": "python analyze_logs.py --logfile /var/log/app.log --pattern ERROR",
            "interval": 120,
            "backend": Backend.LOCAL,
            "resource": {"cpus": 4, "memory_gb": 8}
        }
    ]
    
    try:
        print("启动实时监控系统...")
        print(f"监控任务数: {len(monitoring_tasks)}")
        
        # 创建定期执行的任务
        monitor_threads = []
        stop_event = threading.Event()
        
        for task_def in monitoring_tasks:
            def monitor_loop(def_copy=task_def, stop=stop_event):
                """监控循环"""
                task_name = def_copy["name"]
                interval = def_copy["interval"]
                
                print(f"  启动监控: {task_name} (间隔: {interval}s)")
                
                execution_count = 0
                while not stop.is_set():
                    try:
                        # 创建作业定义
                        job = JobDefinition(
                            cmd=def_copy["cmd"],
                            name=f"monitor_{task_name}_{execution_count}",
                            backend=def_copy.get("backend", Backend.LOCAL),
                            config=ExecutionConfig(
                                timeout=def_copy.get("timeout", 30),
                                capture_output=True
                            ),
                            resource=ResourceRequest(**def_copy.get("resource", {"cpus": 1, "memory_gb": 1})),
                            retry=RetryConfig(**def_copy.get("retry", {"max_attempts": 1})),
                            priority=def_copy.get("priority", JobPriority.NORMAL),
                            tags={
                                "monitoring": "true",
                                "task": task_name,
                                "execution": str(execution_count)
                            }
                        )
                        
                        # 提交作业（异步）
                        future = scheduler.submit(job, wait=False)
                        
                        # 记录执行
                        execution_count += 1
                        
                        # 等待间隔时间
                        for _ in range(interval):
                            if stop.is_set():
                                break
                            time.sleep(1)
                            
                    except Exception as e:
                        print(f"监控任务 {task_name} 错误: {e}")
                        time.sleep(interval)
            
            thread = threading.Thread(target=monitor_loop, daemon=True)
            thread.start()
            monitor_threads.append(thread)
        
        # 运行监控一段时间
        print("\n监控系统运行中... (运行30秒演示)")
        print("按 Ctrl+C 停止监控")
        
        # 演示期间显示实时状态
        for i in range(6):  # 运行30秒
            if stop_event.is_set():
                break
                
            time.sleep(5)
            
            # 显示当前状态
            health = scheduler.health_check()
            metrics = scheduler.get_metrics()
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 系统状态:")
            print(f"  健康状态: {health['status']}")
            print(f"  运行作业: {metrics['current']['jobs_running']}")
            print(f"  总作业数: {metrics['jobs_total']}")
            print(f"  成功率: {metrics.get('success_rate', 0):.1%}")
            
            # 如果有失败作业，显示警告
            failed_jobs = []
            if scheduler.job_store:
                failed_jobs = scheduler.job_store.search_jobs(status=JobStatus.FAILED, limit=3)
            
            if failed_jobs:
                print(f"  ⚠️ 最近失败作业:")
                for job in failed_jobs:
                    result = scheduler.get_result(job.job_id)
                    if result:
                        print(f"     {job.name}: {result.error_message}")
        
        # 停止监控
        print("\n停止监控系统...")
        stop_event.set()
        
        # 等待所有监控线程结束
        for thread in monitor_threads:
            thread.join(timeout=5)
        
        # 最终报告
        print("\n📈 监控报告:")
        print("=" * 40)
        
        metrics = scheduler.get_metrics()
        print(f"监控周期: 30秒")
        print(f"执行作业数: {metrics['jobs_total']}")
        print(f"成功作业: {metrics['jobs_completed']}")
        print(f"失败作业: {metrics['jobs_failed']}")
        print(f"成功率: {metrics.get('success_rate', 0):.1%}")
        
        # 显示后端使用情况
        if metrics.get('backend_stats'):
            print("\n后端使用统计:")
            for backend, count in metrics['backend_stats'].items():
                print(f"  {backend}: {count} 次")
    
    except KeyboardInterrupt:
        print("\n监控被用户中断")
    finally:
        scheduler.shutdown()
        print("监控系统已关闭")

def example_custom_workflow_orchestrator():
    """
    示例6: 自定义工作流编排器
    复杂依赖关系和条件执行
    """
    print("\n" + "="*60)
    print("示例6: 自定义工作流编排器")
    print("="*60)
    
    scheduler = ContainerScheduler(
        max_concurrent=8,
        job_store=JobStore("workflow_orchestrator.db"),
        enable_priority_queue=True
    )
    
    # 定义复杂工作流
    workflow_def = {
        "name": "ml_pipeline_with_validation",
        "stages": [
            {
                "id": "data_extraction",
                "description": "从多个源提取数据",
                "parallel_tasks": [
                    {
                        "id": "extract_db",
                        "cmd": "python extract_from_database.py --config db_config.yaml",
                        "resource": {"cpus": 4, "memory_gb": 8}
                    },
                    {
                        "id": "extract_api",
                        "cmd": "python extract_from_api.py --endpoints api_endpoints.json",
                        "resource": {"cpus": 2, "memory_gb": 4}
                    },
                    {
                        "id": "extract_files",
                        "cmd": "python extract_from_files.py --input /data/raw/ --pattern *.csv",
                        "resource": {"cpus": 2, "memory_gb": 4}
                    }
                ]
            },
            {
                "id": "data_validation",
                "description": "数据验证和质量检查",
                "dependencies": ["data_extraction"],
                "cmd": "python validate_data.py --sources extracted/ --output validation_report.json",
                "resource": {"cpus": 4, "memory_gb": 8},
                "condition": lambda r: r.exit_code == 0  # 只有成功才继续
            },
            {
                "id": "feature_engineering",
                "description": "特征工程（并行特征提取）",
                "dependencies": ["data_validation"],
                "parallel_tasks": [
                    {
                        "id": "numeric_features",
                        "cmd": "python extract_numeric_features.py --input validated_data.parquet",
                        "resource": {"cpus": 4, "memory_gb": 8}
                    },
                    {
                        "id": "text_features",
                        "cmd": "python extract_text_features.py --input validated_data.parquet",
                        "resource": {"cpus": 4, "memory_gb": 16}
                    },
                    {
                        "id": "time_features",
                        "cmd": "python extract_time_features.py --input validated_data.parquet",
                        "resource": {"cpus": 2, "memory_gb": 4}
                    }
                ]
            },
            {
                "id": "model_training",
                "description": "模型训练和验证",
                "dependencies": ["feature_engineering"],
                "parallel_tasks": [
                    {
                        "id": "train_xgboost",
                        "cmd": "python train_xgboost.py --features features/ --output models/xgboost.pkl",
                        "resource": {"cpus": 8, "memory_gb": 16}
                    },
                    {
                        "id": "train_nn",
                        "cmd": "python train_neural_network.py --features features/ --output models/nn.h5",
                        "backend": Backend.SLURM,
                        "resource": {"cpus": 8, "memory_gb": 32, "gpus": 1}
                    }
                ]
            },
            {
                "id": "model_evaluation",
                "description": "模型评估和选择",
                "dependencies": ["model_training"],
                "cmd": "python evaluate_models.py --models models/ --test_data test_set.parquet",
                "resource": {"cpus": 4, "memory_gb": 8}
            },
            {
                "id": "deployment_prep",
                "description": "部署准备",
                "dependencies": ["model_evaluation"],
                "cmd": "python prepare_deployment.py --best_model best_model.pkl --output deployment/",
                "resource": {"cpus": 2, "memory_gb": 4}
            }
        ]
    }
    
    try:
        print(f"开始工作流: {workflow_def['name']}")
        print(f"阶段数: {len(workflow_def['stages'])}")
        
        # 跟踪作业ID映射
        job_mapping = {}
        all_results = {}
        
        # 执行每个阶段
        for stage in workflow_def['stages']:
            print(f"\n➤ 阶段: {stage['id']} - {stage['description']}")
            
            # 检查依赖是否满足
            if 'dependencies' in stage:
                deps_satisfied = True
                for dep in stage['dependencies']:
                    if dep not in all_results or not all_results[dep].success():
                        deps_satisfied = False
                        print(f"   等待依赖: {dep}")
                        break
                
                if not deps_satisfied:
                    print(f"   跳过阶段 {stage['id']} (依赖未满足)")
                    continue
            
            # 并行任务
            if 'parallel_tasks' in stage:
                print(f"   并行任务数: {len(stage['parallel_tasks'])}")
                
                # 创建并行作业
                parallel_jobs = []
                for task in stage['parallel_tasks']:
                    job = JobDefinition(
                        cmd=task['cmd'],
                        name=f"{stage['id']}_{task['id']}",
                        backend=task.get('backend', Backend.LOCAL),
                        resource=ResourceRequest(**task.get('resource', {"cpus": 1, "memory_gb": 1})),
                        tags={
                            "workflow": workflow_def['name'],
                            "stage": stage['id'],
                            "task": task['id']
                        }
                    )
                    parallel_jobs.append(job)
                    job_mapping[job.job_id] = f"{stage['id']}.{task['id']}"
                
                # 执行并行任务
                results = scheduler.run_many(
                    parallel_jobs,
                    max_workers=len(parallel_jobs),
                    stop_on_error=True
                )
                
                # 存储结果
                for job, result in zip(parallel_jobs, results):
                    task_id = job_mapping[job.job_id]
                    all_results[task_id] = result
                    print(f"     任务 {task_id}: {result.status.value}")
                
                # 检查是否所有并行任务都成功
                all_success = all(r.success() for r in results)
                if not all_success:
                    print(f"   阶段 {stage['id']} 有任务失败，停止工作流")
                    break
                    
                # 将整个阶段标记为成功
                stage_result = JobResult(
                    job_id=stage['id'],
                    status=JobStatus.COMPLETED if all_success else JobStatus.FAILED
                )
                all_results[stage['id']] = stage_result
            
            # 单一任务
            elif 'cmd' in stage:
                job = JobDefinition(
                    cmd=stage['cmd'],
                    name=stage['id'],
                    resource=ResourceRequest(**stage.get('resource', {"cpus": 1, "memory_gb": 1})),
                    tags={
                        "workflow": workflow_def['name'],
                        "stage": stage['id']
                    }
                )
                
                result = scheduler.submit(job, wait=True)
                all_results[stage['id']] = result
                
                print(f"   结果: {result.status.value}, 耗时: {result.duration:.1f}s")
                
                # 检查条件
                if 'condition' in stage and callable(stage['condition']):
                    if not stage['condition'](result):
                        print(f"   条件不满足，停止工作流")
                        break
        
        # 工作流完成报告
        print("\n" + "="*40)
        print("工作流完成报告")
        print("="*40)
        
        successful_stages = sum(1 for k, v in all_results.items() if '.' not in k and v.success())
        total_stages = sum(1 for k in all_results.keys() if '.' not in k)
        
        print(f"完成阶段: {successful_stages}/{total_stages}")
        print(f"总作业数: {scheduler.metrics_collector.get_metrics()['jobs_total']}")
        
        if successful_stages == total_stages:
            print("✅ 工作流完全成功!")
        else:
            print("⚠️  工作流部分完成")
            
            # 显示失败阶段
            print("\n失败阶段:")
            for stage_id, result in all_results.items():
                if '.' not in stage_id and result.failed():
                    print(f"  {stage_id}: {result.error_message}")
    
    finally:
        scheduler.shutdown()

def example_disaster_recovery_drills():
    """
    示例7: 灾难恢复演练
    模拟系统故障和恢复过程
    """
    print("\n" + "="*60)
    print("示例7: 灾难恢复演练")
    print("="*60)
    
    # 创建具有高可用性特性的调度器
    scheduler = ContainerScheduler(
        max_concurrent=5,
        job_store=JobStore("dr_drill.db"),
        result_cache=ResultCache(".dr_cache"),
        plugins=[
            NotificationPlugin(email="admin@example.com")
        ],
        enable_priority_queue=True,
        enable_timeout_monitor=True
    )
    
    try:
        print("开始灾难恢复演练...")
        
        # 模拟正常操作
        print("\n阶段1: 正常操作")
        normal_operations = [
            "python process_transactions.py --batch-size 1000",
            "python generate_reports.py --date $(date +%Y-%m-%d)",
            "python backup_database.py --incremental",
            "python monitor_services.py --all",
            "python cleanup_logs.py --older-than 7d"
        ]
        
        normal_results = scheduler.run_many(
            normal_operations,
            progress_callback=lambda c, t: print(f"  正常操作进度: {c}/{t}")
        )
        
        # 模拟故障注入
        print("\n阶段2: 故障注入和检测")
        fault_jobs = [
            {
                "name": "simulate_network_partition",
                "cmd": "python simulate_fault.py --type network --duration 30",
                "retry": {"max_attempts": 5, "delay_seconds": 10},
                "tags": {"dr_test": "network_failure"}
            },
            {
                "name": "simulate_disk_failure",
                "cmd": "python simulate_fault.py --type disk --path /data --severity high",
                "priority": JobPriority.HIGH,
                "tags": {"dr_test": "disk_failure"}
            },
            {
                "name": "simulate_service_outage",
                "cmd": "python simulate_fault.py --type service --services db,cache,queue",
                "timeout": 60,
                "tags": {"dr_test": "service_outage"}
            }
        ]
        
        fault_results = scheduler.run_many(
            fault_jobs,
            stop_on_error=True
        )
        
        # 检查系统健康状态
        print("\n阶段3: 系统健康检查")
        health = scheduler.health_check()
        
        if health["status"] != "healthy":
            print(f"⚠️  系统健康状态: {health['status']}")
            print("触发恢复程序...")
            
            # 执行恢复步骤
            recovery_steps = [
                {
                    "step": "1. 故障隔离",
                    "cmd": "python isolate_fault.py --diagnosis fault_report.json",
                    "priority": JobPriority.CRITICAL
                },
                {
                    "step": "2. 启动备用系统",
                    "cmd": "python start_backup_systems.py --components db,cache",
                    "resource": {"cpus": 8, "memory_gb": 16}
                },
                {
                    "step": "3. 数据恢复",
                    "cmd": "python restore_data.py --backup latest --target /data",
                    "timeout": 300,
                    "retry": {"max_attempts": 3}
                },
                {
                    "step": "4. 服务恢复",
                    "cmd": "python restore_services.py --services all --validate",
                    "priority": JobPriority.HIGH
                },
                {
                    "step": "5. 数据同步",
                    "cmd": "python sync_data.py --source backup --target production",
                    "timeout": 600
                }
            ]
            
            print("\n执行恢复步骤:")
            recovery_results = []
            
            for step in recovery_steps:
                print(f"  {step['step']}...")
                
                job = JobDefinition(
                    cmd=step['cmd'],
                    name=f"recovery_{step['step'].split('.')[0]}",
                    priority=step.get('priority', JobPriority.NORMAL),
                    config=ExecutionConfig(
                        timeout=step.get('timeout', 60)
                    ),
                    resource=ResourceRequest(**step.get('resource', {"cpus": 2, "memory_gb": 4})),
                    retry=RetryConfig(**step.get('retry', {"max_attempts": 1})),
                    tags={"dr_test": "recovery", "step": step['step']}
                )
                
                result = scheduler.submit(job, wait=True)
                recovery_results.append(result)
                
                if result.success():
                    print(f"    ✅ 完成")
                else:
                    print(f"    ❌ 失败: {result.error_message}")
            
            # 验证恢复
            print("\n阶段4: 恢复验证")
            verification_jobs = [
                "python verify_system.py --full-check",
                "python verify_data.py --integrity --consistency",
                "python verify_services.py --all --timeout 30",
                "python verify_performance.py --baseline baseline_metrics.json"
            ]
            
            verification_results = scheduler.run_many(verification_jobs)
            
            successful_verifications = sum(1 for r in verification_results if r.success())
            
            if successful_verifications == len(verification_results):
                print("🎉 灾难恢复演练成功完成!")
                print("   所有系统功能正常恢复")
            else:
                print("⚠️  恢复验证部分失败")
                print(f"   成功验证: {successful_verifications}/{len(verification_results)}")
        
        else:
            print("系统仍然健康，故障被自动恢复")
        
        # 生成演练报告
        print("\n📋 灾难恢复演练报告:")
        print("="*40)
        
        metrics = scheduler.get_metrics()
        total_jobs = metrics['jobs_total']
        successful_jobs = metrics['jobs_completed']
        success_rate = metrics.get('success_rate', 0)
        
        print(f"总作业数: {total_jobs}")
        print(f"成功作业: {successful_jobs}")
        print(f"成功率: {success_rate:.1%}")
        print(f"重试次数: {metrics.get('retries_total', 0)}")
        
        # 显示演练耗时
        if scheduler.job_store:
            all_jobs = scheduler.job_store.search_jobs(tags={"dr_test": True})
            total_duration = 0
            for job in all_jobs:
                result = scheduler.get_result(job.job_id)
                if result and result.duration:
                    total_duration += result.duration
            
            print(f"总演练耗时: {total_duration:.1f}秒")
    
    finally:
        scheduler.shutdown()
        print("\n灾难恢复演练完成")

def example_edge_computing_scenario():
    """
    示例8: 边缘计算场景
    分布式边缘节点任务调度
    """
    print("\n" + "="*60)
    print("示例8: 边缘计算场景")
    print("="*60)
    
    # 模拟多个边缘节点
    edge_nodes = [
        {"id": "edge-01", "location": "factory-floor", "cpus": 8, "memory_gb": 16, "gpus": 1},
        {"id": "edge-02", "location": "warehouse", "cpus": 4, "memory_gb": 8, "gpus": 0},
        {"id": "edge-03", "location": "retail-store", "cpus": 2, "memory_gb": 4, "gpus": 0},
        {"id": "edge-04", "location": "field-office", "cpus": 4, "memory_gb": 8, "gpus": 0},
        {"id": "edge-05", "location": "research-lab", "cpus": 16, "memory_gb": 32, "gpus": 2}
    ]
    
    # 创建主调度器
    master_scheduler = ContainerScheduler(
        max_concurrent=10,
        job_store=JobStore("edge_computing.db"),
        plugins=[NotificationPlugin()]
    )
    
    # 为每个边缘节点创建子调度器（模拟）
    edge_schedulers = {}
    
    try:
        print(f"初始化 {len(edge_nodes)} 个边缘节点...")
        
        # 边缘计算任务
        edge_tasks = []
        
        # 1. 实时视频分析
        for camera_id in range(5):
            task = {
                "type": "video_analytics",
                "cmd": f"python analyze_video.py --camera {camera_id} --model person_detection",
                "requirements": {"gpus": 1, "latency": "low"},
                "priority": JobPriority.HIGH
            }
            edge_tasks.append(task)
        
        # 2. 传感器数据处理
        for sensor_group in ["temperature", "humidity", "vibration", "pressure"]:
            task = {
                "type": "sensor_processing",
                "cmd": f"python process_sensors.py --type {sensor_group} --window 60",
                "requirements": {"cpus": 2, "interval": 60},
                "priority": JobPriority.NORMAL
            }
            edge_tasks.append(task)
        
        # 3. 预测性维护
        task = {
            "type": "predictive_maintenance",
            "cmd": "python predictive_maintenance.py --equipment all --horizon 24",
            "requirements": {"cpus": 4, "memory_gb": 8},
            "priority": JobPriority.HIGH
        }
        edge_tasks.append(task)
        
        # 4. 本地AI推理
        for model in ["defect_detection", "quality_inspection", "anomaly_detection"]:
            task = {
                "type": "ai_inference",
                "cmd": f"python run_inference.py --model {model} --input /data/latest",
                "requirements": {"gpus": 1, "memory_gb": 4},
                "priority": JobPriority.CRITICAL
            }
            edge_tasks.append(task)
        
        print(f"总共 {len(edge_tasks)} 个边缘计算任务")
        
        # 任务分发策略
        print("\n任务分发到边缘节点...")
        
        scheduled_tasks = []
        for task in edge_tasks:
            # 选择最适合的边缘节点
            suitable_nodes = []
            for node in edge_nodes:
                suitable = True
                
                # 检查GPU需求
                if task["requirements"].get("gpus", 0) > 0 and node["gpus"] == 0:
                    suitable = False
                
                # 检查CPU需求
                if task["requirements"].get("cpus", 1) > node["cpus"]:
                    suitable = False
                
                # 检查内存需求
                if task["requirements"].get("memory_gb", 1) > node["memory_gb"]:
                    suitable = False
                
                if suitable:
                    suitable_nodes.append(node)
            
            if suitable_nodes:
                # 选择负载最低的节点（简化策略）
                selected_node = suitable_nodes[0]
                
                job = JobDefinition(
                    cmd=task["cmd"],
                    name=f"edge_{task['type']}_{selected_node['id']}",
                    backend=Backend.LOCAL,  # 假设边缘节点使用本地执行
                    resource=ResourceRequest(
                        cpus=task["requirements"].get("cpus", 1),
                        memory_gb=task["requirements"].get("memory_gb", 1),
                        gpus=task["requirements"].get("gpus", 0)
                    ),
                    priority=task["priority"],
                    tags={
                        "edge_computing": "true",
                        "node_id": selected_node["id"],
                        "location": selected_node["location"],
                        "task_type": task["type"],
                        "latency": task["requirements"].get("latency", "normal")
                    }
                )
                
                scheduled_tasks.append(job)
                print(f"  任务 '{task['type']}' 分配到节点 '{selected_node['id']}'")
            else:
                print(f"  ⚠️  任务 '{task['type']}' 无合适节点，调度到云端")
                
                # 调度到云
                cloud_job = JobDefinition(
                    cmd=task["cmd"],
                    name=f"cloud_{task['type']}",
                    backend=Backend.AWS_BATCH,  # 假设使用AWS Batch
                    resource=ResourceRequest(
                        cpus=task["requirements"].get("cpus", 1),
                        memory_gb=task["requirements"].get("memory_gb", 1),
                        gpus=task["requirements"].get("gpus", 0)
                    ),
                    priority=task["priority"],
                    tags={
                        "edge_computing": "true",
                        "node_id": "cloud",
                        "task_type": task["type"]
                    }
                )
                scheduled_tasks.append(cloud_job)
        
        # 执行所有任务
        print(f"\n开始执行 {len(scheduled_tasks)} 个边缘计算任务...")
        
        results = master_scheduler.run_many(
            scheduled_tasks,
            max_workers=5,
            progress_callback=lambda c, t: print(f"  执行进度: {c}/{t}")
        )
        
        # 分析结果
        print("\n📊 边缘计算任务执行统计:")
        
        # 按节点统计
        node_stats = {}
        for job, result in zip(scheduled_tasks, results):
            node_id = job.tags.get("node_id", "unknown")
            if node_id not in node_stats:
                node_stats[node_id] = {"total": 0, "success": 0}
            
            node_stats[node_id]["total"] += 1
            if result.success():
                node_stats[node_id]["success"] += 1
        
        for node_id, stats in node_stats.items():
            success_rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            print(f"  节点 {node_id}: {stats['success']}/{stats['total']} 成功 ({success_rate:.1%})")
        
        # 按任务类型统计
        type_stats = {}
        for job, result in zip(scheduled_tasks, results):
            task_type = job.tags.get("task_type", "unknown")
            if task_type not in type_stats:
                type_stats[task_type] = {"total": 0, "success": 0}
            
            type_stats[task_type]["total"] += 1
            if result.success():
                type_stats[task_type]["success"] += 1
        
        print("\n📈 按任务类型统计:")
        for task_type, stats in type_stats.items():
            success_rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            print(f"  {task_type}: {stats['success']}/{stats['total']} 成功 ({success_rate:.1%})")
        
        # 总体统计
        total_success = sum(1 for r in results if r.success())
        total_tasks = len(results)
        overall_success_rate = total_success / total_tasks if total_tasks > 0 else 0
        
        print(f"\n🎯 总体统计:")
        print(f"  总任务数: {total_tasks}")
        print(f"  成功任务: {total_success}")
        print(f"  成功率: {overall_success_rate:.1%}")
        
        # 计算平均延迟
        successful_results = [r for r in results if r.success() and r.duration]
        if successful_results:
            avg_duration = sum(r.duration for r in successful_results) / len(successful_results)
            print(f"  平均执行时间: {avg_duration:.2f}秒")
            
            # 低延迟任务统计
            low_latency_tasks = [job for job in scheduled_tasks if job.tags.get("latency") == "low"]
            if low_latency_tasks:
                low_latency_durations = []
                for job in low_latency_tasks:
                    result = next((r for r in results if r.job_id == job.job_id), None)
                    if result and result.duration:
                        low_latency_durations.append(result.duration)
                
                if low_latency_durations:
                    avg_low_latency = sum(low_latency_durations) / len(low_latency_durations)
                    print(f"  低延迟任务平均时间: {avg_low_latency:.2f}秒")
    
    finally:
        master_scheduler.shutdown()
        print("\n边缘计算场景模拟完成")

# ============================================================================
# 运行所有示例
# ============================================================================

def run_all_examples():
    """运行所有示例场景"""
    print("通用容器调度器 - 高级使用场景示例")
    print("="*70)
    
    examples = [
        ("数据处理流水线", example_data_processing_pipeline),
        ("机器学习训练", example_machine_learning_training),
        ("生物信息学工作流", example_bioinformatics_workflow),
        ("云批量处理", example_cloud_batch_processing),
        ("实时监控系统", example_real_time_monitoring),
        ("自定义工作流编排", example_custom_workflow_orchestrator),
        ("灾难恢复演练", example_disaster_recovery_drills),
        ("边缘计算场景", example_edge_computing_scenario),
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n示例 {i}: {name}")
        print("-"*40)
        
        try:
            func()
            print(f"✅ {name} 示例完成")
        except KeyboardInterrupt:
            print(f"⏹️  {name} 示例被中断")
            break
        except Exception as e:
            print(f"❌ {name} 示例错误: {e}")
            import traceback
            traceback.print_exc()
        
        # 示例间暂停
        if i < len(examples):
            print("\n" + "="*70)
            input("按 Enter 键继续下一个示例...")
    
    print("\n" + "="*70)
    print("所有示例运行完成！")

def quick_demo():
    """快速演示核心功能"""
    print("快速演示 - 核心功能")
    print("="*50)
    
    # 1. 基本使用
    print("\n1. 基本命令执行:")
    scheduler = ContainerScheduler()
    result = scheduler.run("echo 'Hello from Universal Scheduler!'")
    print(f"   状态: {result.status.value}, 输出: {result.stdout}")
    
    # 2. 批量处理
    print("\n2. 批量作业处理:")
    commands = [f"echo 'Task {i}' && sleep 0.1" for i in range(5)]
    results = scheduler.run_many(commands, max_workers=3)
    print(f"   完成 {len(results)} 个任务, {sum(1 for r in results if r.success())} 个成功")
    
    # 3. 工作流示例
    print("\n3. 简单工作流:")
    workflow = [
        {"cmd": "echo 'Step 1: Data extraction'", "job_id": "step1"},
        {"cmd": "echo 'Step 2: Processing'", "job_id": "step2", "dependencies": ["step1"]},
        {"cmd": "echo 'Step 3: Analysis'", "job_id": "step3", "dependencies": ["step2"]},
    ]
    results = scheduler.run_workflow(workflow)
    print(f"   工作流完成: {len(results)}/{len(workflow)} 步骤成功")
    
    # 4. 健康检查
    print("\n4. 系统健康检查:")
    health = scheduler.health_check()
    print(f"   健康状态: {health['status']}")
    
    # 5. 指标查看
    print("\n5. 性能指标:")
    metrics = scheduler.get_metrics()
    print(f"   总作业数: {metrics['jobs_total']}")
    print(f"   成功率: {metrics.get('success_rate', 0):.1%}")
    
    scheduler.shutdown()
    print("\n✅ 快速演示完成!")

# ============================================================================
# 主入口
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="通用容器调度器示例")
    parser.add_argument("--demo", action="store_true", help="运行快速演示")
    parser.add_argument("--all", action="store_true", help="运行所有示例")
    parser.add_argument("--example", type=int, choices=range(1, 9), 
                       help="运行特定示例 (1-8)")
    
    args = parser.parse_args()
    
    if args.demo:
        quick_demo()
    elif args.all:
        run_all_examples()
    elif args.example:
        examples = [
            example_data_processing_pipeline,
            example_machine_learning_training,
            example_bioinformatics_workflow,
            example_cloud_batch_processing,
            example_real_time_monitoring,
            example_custom_workflow_orchestrator,
            example_disaster_recovery_drills,
            example_edge_computing_scenario,
        ]
        if 1 <= args.example <= len(examples):
            examples[args.example - 1]()
        else:
            print(f"示例编号 {args.example} 无效，可用范围: 1-{len(examples)}")
    else:
        print("通用容器调度器 - 使用示例")
        print("\n用法:")
        print("  python examples.py --demo      # 快速演示")
        print("  python examples.py --all       # 运行所有示例")
        print("  python examples.py --example N # 运行特定示例")
        print("\n示例列表:")
        examples = [
            "1. 数据处理流水线",
            "2. 机器学习训练", 
            "3. 生物信息学工作流",
            "4. 云批量处理",
            "5. 实时监控系统",
            "6. 自定义工作流编排",
            "7. 灾难恢复演练",
            "8. 边缘计算场景",
        ]
        for example in examples:
            print(f"  {example}")