#!/usr/bin/env python3
"""
S3FS Mount Manager - Ultimate Edition
A comprehensive tool for mounting S3 buckets using s3fs with enterprise-grade features.

Features:
1. Automatic credential discovery from multiple sources
2. Smart mount detection and management
3. Fstab persistence management
4. Multiple bucket/profile support
5. Health checks and diagnostics
6. Graceful error handling
7. Configuration presets
8. Performance tuning options
Usage:

from s3fs_manager import S3FSMountManager

# Initialize manager
manager = S3FSMountManager()

# Create configuration
config = manager.create_config(
    bucket_name="my-data-bucket",
    profile="production",
    mount_point="/mnt/s3-data",
    preset="performance"
)

# Mount the bucket
success = manager.mount(config)

# Check health
health = manager.check_mount_health("/mnt/s3-data")
print(f"Mount status: {health.status}")

2. Command Line Interface
# Mount a bucket
python mount2ls.py mount my-bucket --profile production --save-as prod-config

# Show status
python mount2ls.py status

# Add to fstab for boot-time mounting
sudo python mount2ls.py fstab add my-bucket --comment "Production data"

# Monitor mounts
python mount2ls.py monitor start --interval 30

# Unmount
python mount2ls.py unmount /mnt/s3-data
"""

import os
import sys
import json
import shlex
import signal
import logging
import argparse
import configparser
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MountStatus(Enum):
    """Mount status enumeration"""
    NOT_MOUNTED = "not_mounted"
    MOUNTED = "mounted"
    STALE = "stale"
    ERROR = "error"


class CredentialSource(Enum):
    """Credential source enumeration"""
    AWS_PROFILE = "aws_profile"
    ENVIRONMENT = "environment"
    FILE = "file"
    IAM_ROLE = "iam_role"
    ECS_METADATA = "ecs_metadata"


@dataclass
class S3MountConfig:
    """S3 mount configuration dataclass"""
    profile: str = "default"
    bucket_name: str = ""
    mount_point: Path = None
    endpoint_url: str = "https://s3.amazonaws.com"
    region: str = "us-east-1"
    access_key: str = ""
    secret_key: str = ""
    session_token: str = ""
    iam_role: str = ""
    
    # Mount options
    use_cache: bool = True
    cache_location: Path = Path("/tmp/s3fs_cache")
    allow_other: bool = False
    allow_root: bool = False
    uid: Optional[int] = None
    gid: Optional[int] = None
    umask: str = "000"
    retries: int = 5
    connect_timeout: int = 30
    readwrite_timeout: int = 300
    max_stat_cache_size: int = 100000
    stat_cache_expire: int = 900
    enable_noobj_cache: bool = True
    
    # Performance tuning
    parallel_count: int = 5
    multipart_size: int = 512  # MB
    max_upload_threads: int = 5
    ensure_diskfree: int = 10240  # 10GB minimum free space
    
    # Advanced options
    use_path_request_style: bool = False
    sse: bool = False
    sse_kms_key_id: str = ""
    storage_class: str = "STANDARD"
    
    # Health check
    health_check_interval: int = 60  # seconds
    auto_remount: bool = True
    auto_remount_attempts: int = 3
    
    def __post_init__(self):
        if not self.mount_point:
            self.mount_point = Path.home() / self.bucket_name


@dataclass
class MountHealth:
    """Mount health information"""
    status: MountStatus
    mount_time: Optional[datetime] = None
    last_access: Optional[datetime] = None
    read_speed: Optional[float] = None  # MB/s
    write_speed: Optional[float] = None  # MB/s
    latency: Optional[float] = None  # ms
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class S3FSMountManager:
    """
    Ultimate S3FS Mount Manager
    
    A comprehensive tool for mounting S3 buckets with enterprise features:
    - Automatic credential discovery from multiple sources
    - Smart mount detection and management
    - Health monitoring and auto-recovery
    - Performance tuning
    - Configuration presets
    - Multi-bucket support
    
    Example:
        >>> manager = S3FSMountManager()
        >>> config = manager.create_config(
        ...     bucket_name="my-bucket",
        ...     profile="production"
        ... )
        >>> success = manager.mount(config)
        >>> health = manager.check_health(config.mount_point)
    """
    
    # Default configuration presets
    PRESETS = {
        "standard": {
            "retries": 5,
            "parallel_count": 5,
            "max_stat_cache_size": 100000,
        },
        "performance": {
            "parallel_count": 20,
            "multipart_size": 1024,
            "max_upload_threads": 10,
            "max_stat_cache_size": 500000,
        },
        "reliable": {
            "retries": 10,
            "connect_timeout": 60,
            "readwrite_timeout": 600,
            "auto_remount": True,
            "auto_remount_attempts": 5,
        },
        "low_memory": {
            "parallel_count": 2,
            "max_stat_cache_size": 10000,
            "enable_noobj_cache": False,
        },
        "high_latency": {
            "connect_timeout": 120,
            "readwrite_timeout": 900,
            "retries": 15,
            "parallel_count": 3,
        }
    }
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize S3FS Mount Manager
        
        Args:
            config_dir: Directory for storing configuration files
        """
        self.config_dir = config_dir or Path.home() / ".config" / "s3fs-manager"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load saved configurations
        self.saved_configs = self._load_saved_configs()
        
        # Active mounts tracking
        self.active_mounts: Dict[Path, S3MountConfig] = {}
        self.mount_health: Dict[Path, MountHealth] = {}
        
        # Health monitoring thread
        self.monitor_thread = None
        self.monitor_running = False
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"S3FS Mount Manager initialized. Config dir: {self.config_dir}")
    
    def _signal_handler(self, signum, frame):
        """Handle termination signals gracefully"""
        logger.info(f"Received signal {signum}, cleaning up...")
        self.stop_monitoring()
        self.unmount_all()
        sys.exit(0)
    
    def _load_saved_configs(self) -> Dict[str, S3MountConfig]:
        """Load saved configurations from disk"""
        config_file = self.config_dir / "saved_configs.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                configs = {}
                for name, cfg_data in data.items():
                    # Convert mount_point string back to Path
                    if 'mount_point' in cfg_data:
                        cfg_data['mount_point'] = Path(cfg_data['mount_point'])
                    if 'cache_location' in cfg_data:
                        cfg_data['cache_location'] = Path(cfg_data['cache_location'])
                    configs[name] = S3MountConfig(**cfg_data)
                return configs
            except Exception as e:
                logger.error(f"Failed to load saved configs: {e}")
        return {}
    
    def _save_configs(self):
        """Save configurations to disk"""
        config_file = self.config_dir / "saved_configs.json"
        try:
            # Convert Path objects to strings for JSON serialization
            data = {}
            for name, config in self.saved_configs.items():
                cfg_dict = asdict(config)
                cfg_dict['mount_point'] = str(config.mount_point)
                cfg_dict['cache_location'] = str(config.cache_location)
                data[name] = cfg_dict
            
            with open(config_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save configs: {e}")
    
    def discover_credentials(self, profile: str = "default") -> Tuple[str, str, str]:
        """
        Discover AWS credentials from multiple sources
        
        Sources checked in order:
        1. Environment variables
        2. AWS CLI profile
        3. IAM role (EC2/ECS)
        4. Credential file
        
        Args:
            profile: AWS profile name
            
        Returns:
            Tuple of (access_key, secret_key, session_token)
            
        Raises:
            ValueError: If no credentials found
        """
        sources = []
        
        # 1. Environment variables
        access_key = os.environ.get('AWS_ACCESS_KEY_ID') or os.environ.get('AWS_ACCESS_KEY')
        secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY') or os.environ.get('AWS_SECRET_KEY')
        session_token = os.environ.get('AWS_SESSION_TOKEN')
        
        if access_key and secret_key:
            sources.append(CredentialSource.ENVIRONMENT)
            logger.info("Found credentials in environment variables")
            return access_key, secret_key, session_token or ""
        
        # 2. AWS CLI profile
        creds_file = Path.home() / ".aws" / "credentials"
        config_file = Path.home() / ".aws" / "config"
        
        if creds_file.exists():
            try:
                creds = configparser.ConfigParser()
                creds.read(creds_file)
                
                # Check for profile
                profile_name = profile
                if profile != "default" and f"profile {profile}" in creds:
                    profile_name = f"profile {profile}"
                
                if profile_name in creds:
                    access_key = creds[profile_name].get("aws_access_key_id")
                    secret_key = creds[profile_name].get("aws_secret_access_key")
                    session_token = creds[profile_name].get("aws_session_token")
                    
                    if access_key and secret_key:
                        sources.append(CredentialSource.AWS_PROFILE)
                        logger.info(f"Found credentials in AWS profile: {profile}")
                        return access_key, secret_key, session_token or ""
            except Exception as e:
                logger.warning(f"Failed to read AWS credentials file: {e}")
        
        # 3. IAM Role (check metadata service)
        try:
            import requests
            # Try EC2 metadata
            metadata_url = "http://169.254.169.254/latest/meta-data/iam/security-credentials/"
            response = requests.get(metadata_url, timeout=2)
            if response.status_code == 200:
                role_name = response.text.strip()
                role_url = f"{metadata_url}{role_name}"
                role_data = requests.get(role_url, timeout=2).json()
                
                sources.append(CredentialSource.IAM_ROLE)
                logger.info(f"Found IAM role credentials: {role_name}")
                return role_data['AccessKeyId'], role_data['SecretAccessKey'], role_data.get('Token', "")
        except:
            pass
        
        # 4. Check for credential file
        passwd_file = Path.home() / ".passwd-s3fs"
        if passwd_file.exists():
            try:
                with open(passwd_file, 'r') as f:
                    content = f.read().strip()
                    if ':' in content:
                        access_key, secret_key = content.split(':', 1)
                        sources.append(CredentialSource.FILE)
                        logger.info("Found credentials in .passwd-s3fs file")
                        return access_key, secret_key, ""
            except Exception as e:
                logger.warning(f"Failed to read .passwd-s3fs: {e}")
        
        raise ValueError(
            f"No AWS credentials found for profile '{profile}'. "
            "Please configure AWS credentials via:\n"
            "1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)\n"
            "2. AWS CLI: 'aws configure'\n"
            "3. IAM role (if on EC2/ECS)\n"
            "4. Create ~/.passwd-s3fs file"
        )
    
    def discover_endpoint(self, profile: str = "default", region: str = None) -> str:
        """
        Discover S3 endpoint URL
        
        Args:
            profile: AWS profile name
            region: AWS region (overrides profile setting)
            
        Returns:
            Endpoint URL
        """
        # Check config file for custom endpoint
        config_file = Path.home() / ".aws" / "config"
        if config_file.exists():
            try:
                config = configparser.ConfigParser()
                config.read(config_file)
                
                section = profile if profile == "default" else f"profile {profile}"
                if section in config:
                    # Check for endpoint_url in s3 section
                    s3_options = config[section].get("s3", "")
                    for line in s3_options.splitlines():
                        if "endpoint_url" in line:
                            endpoint = line.split("=")[-1].strip()
                            logger.info(f"Found custom endpoint in config: {endpoint}")
                            return endpoint
                    
                    # Get region from config
                    if not region:
                        region = config[section].get("region", "us-east-1")
            except Exception as e:
                logger.warning(f"Failed to read AWS config: {e}")
        
        # Use region to construct endpoint
        if not region:
            region = os.environ.get('AWS_REGION', 'us-east-1')
        
        # Special handling for different regions
        if region.startswith('cn-'):
            return f"https://s3.{region}.amazonaws.com.cn"
        elif region.startswith('us-gov-'):
            return f"https://s3.{region}.amazonaws.com"
        else:
            return f"https://s3.{region}.amazonaws.com"
    
    def create_config(
        self,
        bucket_name: str,
        profile: str = "default",
        mount_point: Optional[Union[str, Path]] = None,
        preset: str = "standard",
        **kwargs
    ) -> S3MountConfig:
        """
        Create S3 mount configuration
        
        Args:
            bucket_name: Name of S3 bucket
            profile: AWS profile name
            mount_point: Local mount directory (default: ~/bucket_name)
            preset: Configuration preset (standard, performance, reliable, etc.)
            **kwargs: Additional configuration overrides
            
        Returns:
            S3MountConfig object
        """
        # Discover credentials
        access_key, secret_key, session_token = self.discover_credentials(profile)
        
        # Discover endpoint
        endpoint_url = self.discover_endpoint(profile, kwargs.get('region'))
        
        # Create mount point path
        if mount_point is None:
            mount_point = Path.home() / bucket_name
        elif isinstance(mount_point, str):
            mount_point = Path(mount_point).expanduser()
        
        # Start with preset configuration
        if preset in self.PRESETS:
            base_config = self.PRESETS[preset].copy()
        else:
            base_config = self.PRESETS["standard"].copy()
        
        # Apply kwargs overrides
        base_config.update(kwargs)
        
        # Create config object
        config = S3MountConfig(
            profile=profile,
            bucket_name=bucket_name,
            mount_point=mount_point,
            endpoint_url=endpoint_url,
            access_key=access_key,
            secret_key=secret_key,
            session_token=session_token,
            **base_config
        )
        
        return config
    
    def save_config(self, name: str, config: S3MountConfig):
        """
        Save configuration for later use
        
        Args:
            name: Configuration name
            config: S3MountConfig object
        """
        self.saved_configs[name] = config
        self._save_configs()
        logger.info(f"Saved configuration: {name}")
    
    def load_config(self, name: str) -> S3MountConfig:
        """
        Load saved configuration
        
        Args:
            name: Configuration name
            
        Returns:
            S3MountConfig object
            
        Raises:
            KeyError: If configuration not found
        """
        if name not in self.saved_configs:
            raise KeyError(f"Configuration '{name}' not found")
        return self.saved_configs[name]
    
    def is_mounted(self, mount_point: Union[str, Path]) -> Tuple[bool, Optional[Dict]]:
        """
        Check if path is mounted with detailed information
        
        Args:
            mount_point: Path to check
            
        Returns:
            Tuple of (is_mounted, mount_info)
        """
        mount_path = Path(mount_point) if isinstance(mount_point, str) else mount_point
        
        # Check with mountpoint command
        try:
            result = subprocess.run(
                ["mountpoint", "-q", str(mount_path)],
                capture_output=True
            )
            is_mountpoint = result.returncode == 0
            
            # Get detailed mount info
            mount_info = None
            if is_mountpoint:
                result = subprocess.run(
                    ["mount"], capture_output=True, text=True
                )
                for line in result.stdout.splitlines():
                    if str(mount_path) in line:
                        mount_info = self._parse_mount_line(line)
                        break
            
            return is_mountpoint, mount_info
        except Exception as e:
            logger.error(f"Failed to check mount status: {e}")
            return False, None
    
    def _parse_mount_line(self, line: str) -> Dict:
        """Parse mount command output line"""
        parts = line.split()
        info = {
            'device': parts[0],
            'mount_point': parts[2],
            'filesystem': parts[4],
            'options': parts[5].strip('()').split(',')
        }
        return info
    
    def check_mount_health(self, mount_point: Union[str, Path]) -> MountHealth:
        """
        Perform comprehensive health check on mount
        
        Args:
            mount_point: Mount point to check
            
        Returns:
            MountHealth object
        """
        mount_path = Path(mount_point) if isinstance(mount_point, str) else mount_point
        is_mounted, mount_info = self.is_mounted(mount_path)
        
        if not is_mounted:
            return MountHealth(status=MountStatus.NOT_MOUNTED)
        
        health = MountHealth(
            status=MountStatus.MOUNTED,
            mount_time=datetime.now()
        )
        
        # Perform I/O test
        try:
            # Read test
            test_file = mount_path / ".health_check_test"
            with open(test_file, 'w') as f:
                f.write("health_check")
            
            start = time.time()
            with open(test_file, 'r') as f:
                content = f.read()
            read_time = time.time() - start
            
            # Cleanup
            test_file.unlink()
            
            # Calculate speeds (simplified)
            if read_time > 0:
                health.read_speed = 0.001 / read_time  # 1KB / time
            
        except Exception as e:
            health.status = MountStatus.ERROR
            health.errors.append(f"I/O test failed: {e}")
        
        # Check for stale mount (no recent access)
        if health.last_access and (datetime.now() - health.last_access).seconds > 300:
            health.warnings.append("Mount appears stale - no recent access")
            health.status = MountStatus.STALE
        
        return health
    
    def _create_passwd_file(self, config: S3MountConfig) -> Path:
        """
        Create s3fs password file
        
        Args:
            config: S3MountConfig object
            
        Returns:
            Path to password file
        """
        passwd_dir = self.config_dir / "credentials"
        passwd_dir.mkdir(exist_ok=True)
        
        passwd_file = passwd_dir / f"{config.profile}_{config.bucket_name}.passwd"
        
        # Write credentials
        with open(passwd_file, 'w') as f:
            if config.session_token:
                f.write(f"{config.access_key}:{config.secret_key}:{config.session_token}\n")
            else:
                f.write(f"{config.access_key}:{config.secret_key}\n")
        
        # Secure permissions
        os.chmod(passwd_file, 0o600)
        
        return passwd_file
    
    def _build_s3fs_command(self, config: S3MountConfig) -> List[str]:
        """
        Build s3fs command with all options
        
        Args:
            config: S3MountConfig object
            
        Returns:
            List of command arguments
        """
        # Create password file
        passwd_file = self._create_passwd_file(config)
        
        # Base command
        cmd = [
            "s3fs",
            config.bucket_name,
            str(config.mount_point),
            "-o", f"passwd_file={passwd_file}",
            "-o", f"url={config.endpoint_url}",
        ]
        
        # Add common options
        options = [
            ("retries", config.retries),
            ("connect_timeout", config.connect_timeout),
            ("readwrite_timeout", config.readwrite_timeout),
            ("parallel_count", config.parallel_count),
            ("multipart_size", config.multipart_size),
            ("max_stat_cache_size", config.max_stat_cache_size),
            ("stat_cache_expire", config.stat_cache_expire),
            ("ensure_diskfree", config.ensure_diskfree),
            ("umask", config.umask),
        ]
        
        for opt, value in options:
            if value is not None:
                cmd.extend(["-o", f"{opt}={value}"])
        
        # Conditional options
        if config.use_cache:
            cmd.extend(["-o", f"use_cache={config.cache_location}"])
        
        if config.allow_other:
            cmd.append("-o")
            cmd.append("allow_other")
        
        if config.allow_root:
            cmd.append("-o")
            cmd.append("allow_root")
        
        if config.uid is not None:
            cmd.extend(["-o", f"uid={config.uid}"])
        
        if config.gid is not None:
            cmd.extend(["-o", f"gid={config.gid}"])
        
        if config.use_path_request_style:
            cmd.append("-o")
            cmd.append("use_path_request_style")
        
        if not config.enable_noobj_cache:
            cmd.append("-o")
            cmd.append("enable_noobj_cache")
        
        if config.sse:
            cmd.append("-o")
            cmd.append("sse")
            if config.sse_kms_key_id:
                cmd.extend(["-o", f"sse_kms_key_id={config.sse_kms_key_id}"])
        
        # Debug logging
        cmd.append("-o")
        cmd.append("dbglevel=info")
        cmd.append("-f")  # Run in foreground
        
        return cmd
    
    def mount(self, config: S3MountConfig, force: bool = False) -> bool:
        """
        Mount S3 bucket with comprehensive error handling
        
        Args:
            config: S3MountConfig object
            force: Force remount if already mounted
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Mounting bucket '{config.bucket_name}' to '{config.mount_point}'")
        
        # Check if already mounted
        is_mounted, mount_info = self.is_mounted(config.mount_point)
        
        if is_mounted:
            if not force:
                logger.warning(f"Mount point '{config.mount_point}' is already mounted")
                return True
            
            logger.info(f"Force unmounting existing mount at '{config.mount_point}'")
            if not self.unmount(config.mount_point):
                logger.error("Failed to unmount existing mount")
                return False
        
        # Create mount point
        try:
            config.mount_point.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created mount point: {config.mount_point}")
        except Exception as e:
            logger.error(f"Failed to create mount point: {e}")
            return False
        
        # Create cache directory if using cache
        if config.use_cache:
            try:
                config.cache_location.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"Failed to create cache directory: {e}")
        
        # Check disk space
        try:
            stat = os.statvfs(config.mount_point)
            free_space = stat.f_bavail * stat.f_frsize / (1024 ** 3)  # GB
            
            if free_space < (config.ensure_diskfree / 1024):
                logger.warning(
                    f"Low disk space: {free_space:.1f}GB free, "
                    f"recommended: {config.ensure_diskfree/1024:.1f}GB"
                )
        except Exception as e:
            logger.warning(f"Could not check disk space: {e}")
        
        # Build and execute mount command
        cmd = self._build_s3fs_command(config)
        logger.debug(f"Executing command: {' '.join(cmd)}")
        
        try:
            # Start s3fs as a subprocess
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Wait for mount to complete (with timeout)
            timeout = 30
            start_time = time.time()
            
            while True:
                # Check if process is still running
                if process.poll() is not None:
                    stderr_output = process.stderr.read()
                    if process.returncode != 0:
                        logger.error(f"s3fs failed with code {process.returncode}: {stderr_output}")
                        return False
                    break
                
                # Check if mount point is now mounted
                is_mounted, _ = self.is_mounted(config.mount_point)
                if is_mounted:
                    logger.info(f"Successfully mounted {config.bucket_name}")
                    break
                
                # Check timeout
                if time.time() - start_time > timeout:
                    logger.error(f"Mount timeout after {timeout} seconds")
                    process.terminate()
                    return False
                
                time.sleep(0.5)
            
            # Track active mount
            self.active_mounts[config.mount_point] = config
            
            # Perform health check
            health = self.check_mount_health(config.mount_point)
            self.mount_health[config.mount_point] = health
            
            logger.info(f"Mount health: {health.status.value}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to mount: {e}")
            return False
    
    def unmount(self, mount_point: Union[str, Path], force: bool = False) -> bool:
        """
        Unmount S3 bucket
        
        Args:
            mount_point: Mount point to unmount
            force: Force unmount if busy
            
        Returns:
            True if successful, False otherwise
        """
        mount_path = Path(mount_point) if isinstance(mount_point, str) else mount_point
        
        logger.info(f"Unmounting {mount_path}")
        
        # Check if mounted
        is_mounted, _ = self.is_mounted(mount_path)
        if not is_mounted:
            logger.info(f"{mount_path} is not mounted")
            return True
        
        # Try fusermount first
        try:
            if force:
                cmd = ["fusermount", "-u", "-z", str(mount_path)]
            else:
                cmd = ["fusermount", "-u", str(mount_path)]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"Successfully unmounted {mount_path}")
                # Remove from active mounts
                self.active_mounts.pop(mount_path, None)
                self.mount_health.pop(mount_path, None)
                return True
            else:
                logger.warning(f"fusermount failed: {result.stderr}")
        except Exception as e:
            logger.warning(f"fusermount error: {e}")
        
        # Try umount if fusermount failed
        try:
            if force:
                cmd = ["umount", "-f", "-l", str(mount_path)]
            else:
                cmd = ["umount", str(mount_path)]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"Successfully unmounted with umount: {mount_path}")
                self.active_mounts.pop(mount_path, None)
                self.mount_health.pop(mount_path, None)
                return True
            else:
                logger.error(f"umount failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"umount error: {e}")
            return False
    
    def unmount_all(self):
        """Unmount all active mounts"""
        logger.info("Unmounting all active mounts")
        for mount_point in list(self.active_mounts.keys()):
            self.unmount(mount_point, force=True)
    
    def update_fstab(self, config: S3MountConfig, comment: str = "") -> bool:
        """
        Add or update entry in /etc/fstab for persistent mount
        
        Args:
            config: S3MountConfig object
            comment: Optional comment for fstab entry
            
        Returns:
            True if successful, False otherwise
        """
        if os.geteuid() != 0:
            logger.error("Root privileges required to update /etc/fstab")
            return False
        
        passwd_file = self._create_passwd_file(config)
        
        # Build fstab options
        options = [
            "_netdev",
            f"passwd_file={passwd_file}",
            f"url={config.endpoint_url}",
            f"retries={config.retries}",
            f"connect_timeout={config.connect_timeout}",
            f"readwrite_timeout={config.readwrite_timeout}",
            f"parallel_count={config.parallel_count}",
            f"umask={config.umask}",
        ]
        
        if config.allow_other:
            options.append("allow_other")
        
        if config.use_path_request_style:
            options.append("use_path_request_style")
        
        if config.use_cache:
            options.append(f"use_cache={config.cache_location}")
        
        options_str = ",".join(options)
        
        # Create fstab entry
        fstab_entry = (
            f"s3fs#{config.bucket_name} {config.mount_point} "
            f"fuse {options_str} 0 0"
        )
        
        if comment:
            fstab_entry = f"# {comment}\n{fstab_entry}"
        
        try:
            # Read existing fstab
            with open("/etc/fstab", "r") as f:
                lines = f.readlines()
            
            # Check if entry already exists
            entry_exists = False
            new_lines = []
            
            for line in lines:
                if f"s3fs#{config.bucket_name}" in line:
                    # Replace existing entry
                    new_lines.append(fstab_entry + "\n")
                    entry_exists = True
                    logger.info(f"Updated existing fstab entry for {config.bucket_name}")
                else:
                    new_lines.append(line)
            
            # Add new entry if not exists
            if not entry_exists:
                new_lines.append(fstab_entry + "\n")
                logger.info(f"Added new fstab entry for {config.bucket_name}")
            
            # Write back fstab
            with open("/etc/fstab", "w") as f:
                f.writelines(new_lines)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update /etc/fstab: {e}")
            return False
    
    def remove_fstab_entry(self, bucket_name: str) -> bool:
        """
        Remove entry from /etc/fstab
        
        Args:
            bucket_name: S3 bucket name
            
        Returns:
            True if successful, False otherwise
        """
        if os.geteuid() != 0:
            logger.error("Root privileges required to modify /etc/fstab")
            return False
        
        try:
            with open("/etc/fstab", "r") as f:
                lines = f.readlines()
            
            # Filter out entries for this bucket
            new_lines = [
                line for line in lines 
                if f"s3fs#{bucket_name}" not in line
            ]
            
            # Only write if something changed
            if len(new_lines) != len(lines):
                with open("/etc/fstab", "w") as f:
                    f.writelines(new_lines)
                logger.info(f"Removed fstab entry for {bucket_name}")
                return True
            else:
                logger.info(f"No fstab entry found for {bucket_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to remove fstab entry: {e}")
            return False
    
    def start_monitoring(self, interval: int = 60):
        """
        Start health monitoring for all active mounts
        
        Args:
            interval: Health check interval in seconds
        """
        if self.monitor_running:
            logger.warning("Monitoring already running")
            return
        
        self.monitor_running = True
        
        def monitor_loop():
            while self.monitor_running:
                try:
                    for mount_point, config in list(self.active_mounts.items()):
                        health = self.check_mount_health(mount_point)
                        self.mount_health[mount_point] = health
                        
                        # Auto-remount on error
                        if (health.status == MountStatus.ERROR and 
                            config.auto_remount):
                            logger.warning(f"Auto-remounting {mount_point}")
                            self.unmount(mount_point)
                            time.sleep(2)
                            self.mount(config)
                        
                        # Log warnings
                        if health.warnings:
                            for warning in health.warnings:
                                logger.warning(f"{mount_point}: {warning}")
                    
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"Started health monitoring with {interval}s interval")
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitor_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Stopped health monitoring")
    
    def get_status_report(self) -> Dict:
        """
        Generate comprehensive status report
        
        Returns:
            Dictionary with status information
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "active_mounts": {},
            "saved_configs": list(self.saved_configs.keys()),
            "monitoring": self.monitor_running,
        }
        
        for mount_point, config in self.active_mounts.items():
            health = self.mount_health.get(mount_point)
            
            report["active_mounts"][str(mount_point)] = {
                "bucket": config.bucket_name,
                "profile": config.profile,
                "endpoint": config.endpoint_url,
                "health": {
                    "status": health.status.value if health else "unknown",
                    "errors": health.errors if health else [],
                    "warnings": health.warnings if health else [],
                    "read_speed": health.read_speed if health else None,
                } if health else None
            }
        
        return report
    
    def print_status(self):
        """Print formatted status report to console"""
        report = self.get_status_report()
        
        print("\n" + "=" * 80)
        print("S3FS MOUNT MANAGER STATUS")
        print("=" * 80)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Monitoring: {'ACTIVE' if report['monitoring'] else 'INACTIVE'}")
        print(f"Saved Configurations: {', '.join(report['saved_configs'])}")
        
        if report['active_mounts']:
            print("\nACTIVE MOUNTS:")
            print("-" * 80)
            for mount_point, info in report['active_mounts'].items():
                print(f"Mount Point: {mount_point}")
                print(f"  Bucket: {info['bucket']}")
                print(f"  Profile: {info['profile']}")
                print(f"  Endpoint: {info['endpoint']}")
                if info['health']:
                    print(f"  Status: {info['health']['status'].upper()}")
                    if info['health']['read_speed']:
                        print(f"  Read Speed: {info['health']['read_speed']:.2f} MB/s")
                    if info['health']['errors']:
                        print(f"  Errors: {', '.join(info['health']['errors'])}")
                    if info['health']['warnings']:
                        print(f"  Warnings: {', '.join(info['health']['warnings'])}")
                print()
        else:
            print("\nNo active mounts")
        
        print("=" * 80)


def main():
    """Command-line interface for S3FS Mount Manager"""
    parser = argparse.ArgumentParser(
        description="Ultimate S3FS Mount Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Mount a bucket with default settings
  %(prog)s mount my-bucket
  
  # Mount with performance preset
  %(prog)s mount my-bucket --preset performance --mount-dir /mnt/s3
  
  # Mount using specific AWS profile
  %(prog)s mount my-bucket --profile production --save-as prod-bucket
  
  # Unmount a directory
  %(prog)s unmount /mnt/s3
  
  # Show status
  %(prog)s status
  
  # Add to fstab for persistence
  %(prog)s fstab my-bucket --comment "Production data"
  
  # Load and mount saved configuration
  %(prog)s load prod-bucket
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Mount command
    mount_parser = subparsers.add_parser("mount", help="Mount S3 bucket")
    mount_parser.add_argument("bucket", help="S3 bucket name")
    mount_parser.add_argument("--profile", default="default", help="AWS profile name")
    mount_parser.add_argument("--mount-dir", help="Mount directory (default: ~/bucket)")
    mount_parser.add_argument("--preset", default="standard", 
                             choices=["standard", "performance", "reliable", "low_memory", "high_latency"],
                             help="Configuration preset")
    mount_parser.add_argument("--save-as", help="Save configuration with this name")
    mount_parser.add_argument("--force", action="store_true", help="Force remount if already mounted")
    mount_parser.add_argument("--fstab", action="store_true", help="Add to /etc/fstab")
    mount_parser.add_argument("--comment", help="Comment for fstab entry")
    
    # Unmount command
    unmount_parser = subparsers.add_parser("unmount", help="Unmount directory")
    unmount_parser.add_argument("mount_point", help="Mount point to unmount")
    unmount_parser.add_argument("--force", action="store_true", help="Force unmount")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show mount status")
    
    # Fstab command
    fstab_parser = subparsers.add_parser("fstab", help="Manage /etc/fstab entries")
    fstab_parser.add_argument("action", choices=["add", "remove"], help="Add or remove entry")
    fstab_parser.add_argument("bucket", help="S3 bucket name")
    fstab_parser.add_argument("--profile", default="default", help="AWS profile name")
    fstab_parser.add_argument("--mount-dir", help="Mount directory")
    fstab_parser.add_argument("--comment", help="Comment for fstab entry")
    
    # Load command
    load_parser = subparsers.add_parser("load", help="Load and mount saved configuration")
    load_parser.add_argument("config_name", help="Saved configuration name")
    load_parser.add_argument("--force", action="store_true", help="Force remount")
    
    # Save command
    save_parser = subparsers.add_parser("save", help="Save current configuration")
    save_parser.add_argument("name", help="Configuration name")
    save_parser.add_argument("--bucket", required=True, help="S3 bucket name")
    save_parser.add_argument("--profile", default="default", help="AWS profile name")
    save_parser.add_argument("--mount-dir", help="Mount directory")
    save_parser.add_argument("--preset", default="standard", help="Configuration preset")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List saved configurations")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor mounts")
    monitor_parser.add_argument("action", choices=["start", "stop", "status"], 
                               help="Monitor action")
    monitor_parser.add_argument("--interval", type=int, default=60, 
                               help="Health check interval in seconds")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize manager
    manager = S3FSMountManager()
    
    try:
        if args.command == "mount":
            # Create configuration
            config = manager.create_config(
                bucket_name=args.bucket,
                profile=args.profile,
                mount_point=args.mount_dir,
                preset=args.preset
            )
            
            # Save if requested
            if args.save_as:
                manager.save_config(args.save_as, config)
            
            # Mount
            success = manager.mount(config, force=args.force)
            
            if success and args.fstab:
                manager.update_fstab(config, comment=args.comment)
            
            sys.exit(0 if success else 1)
        
        elif args.command == "unmount":
            success = manager.unmount(args.mount_point, force=args.force)
            sys.exit(0 if success else 1)
        
        elif args.command == "status":
            manager.print_status()
        
        elif args.command == "fstab":
            if args.action == "add":
                config = manager.create_config(
                    bucket_name=args.bucket,
                    profile=args.profile,
                    mount_point=args.mount_dir
                )
                success = manager.update_fstab(config, comment=args.comment)
                sys.exit(0 if success else 1)
            else:  # remove
                success = manager.remove_fstab_entry(args.bucket)
                sys.exit(0 if success else 1)
        
        elif args.command == "load":
            config = manager.load_config(args.config_name)
            success = manager.mount(config, force=args.force)
            sys.exit(0 if success else 1)
        
        elif args.command == "save":
            config = manager.create_config(
                bucket_name=args.bucket,
                profile=args.profile,
                mount_point=args.mount_dir,
                preset=args.preset
            )
            manager.save_config(args.name, config)
            print(f"Saved configuration: {args.name}")
        
        elif args.command == "list":
            configs = manager.saved_configs
            if configs:
                print("Saved Configurations:")
                for name in configs:
                    print(f"  {name}: {configs[name].bucket_name}")
            else:
                print("No saved configurations")
        
        elif args.command == "monitor":
            if args.action == "start":
                manager.start_monitoring(args.interval)
                print(f"Monitoring started with {args.interval}s interval")
            elif args.action == "stop":
                manager.stop_monitoring()
                print("Monitoring stopped")
            else:  # status
                if manager.monitor_running:
                    print("Monitoring is ACTIVE")
                else:
                    print("Monitoring is INACTIVE")
    
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()