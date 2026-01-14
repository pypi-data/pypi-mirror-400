"""
apptainer2ls.py - Ultimate Singularity/Apptainer Development Environment Tool

A comprehensive tool for creating, managing, and using Singularity/Apptainer
containers for development and HPC workflows.

Features:
- Create persistent development environments
- GPU support (CUDA, ROCm)
- HPC cluster compatibility
- SSH forwarding for remote execution
- X11 forwarding for GUI applications
- Batch job templates
- Backup and migration tools
- Performance monitoring
- Multi-architecture support
- Container security scanning
"""

import os
import sys
import subprocess
import shutil
import json
import time
import tempfile
import getpass
import platform
import argparse
import textwrap
import hashlib
import re
import stat
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Union, Tuple, Any
import warnings
import socket
import pwd
import grp
import shlex
import secrets
import string
import tarfile
import gzip
import zipfile

# Try to import optional dependencies
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Version
__version__ = "1.0.0"
__author__ = "Singularity/Apptainer Development Tools"

def check_apptainer_availability() -> Dict[str, Union[bool, str]]:
    """
    Check if Singularity/Apptainer is available on the system.
    
    Returns:
        Dictionary with availability status and information
    """
    # Try Apptainer first (newer name)
    for cmd in ["apptainer", "singularity"]:
        try:
            result = subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse version
                version_output = result.stdout.strip()
                version_match = re.search(r'(\d+\.\d+\.\d+)', version_output)
                version = version_match.group(1) if version_match else "unknown"
                
                return {
                    "available": True,
                    "command": cmd,
                    "version": version,
                    "full_version": version_output,
                    "message": f"{cmd.capitalize()} is available"
                }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    return {
        "available": False,
        "command": None,
        "version": None,
        "message": "Neither Apptainer nor Singularity found. Please install one of them."
    }

def install_apptainer_tool() -> bool:
    """
    Install Singularity/Apptainer based on the operating system.
    
    Returns:
        True if installation was attempted/succeeded, False otherwise
    """
    system = platform.system().lower()
    distro = None
    
    print("Installing Singularity/Apptainer...")
    print(f"Detected system: {system}")
    
    if system == "linux":
        # Try to detect distribution
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    content = f.read().lower()
                    
                    if "ubuntu" in content or "debian" in content:
                        distro = "debian"
                    elif "centos" in content or "rhel" in content or "rocky" in content:
                        distro = "rhel"
                    elif "fedora" in content:
                        distro = "fedora"
                    elif "arch" in content:
                        distro = "arch"
                    elif "opensuse" in content or "suse" in content:
                        distro = "suse"
        except:
            pass
        
        print(f"Detected distribution: {distro or 'unknown'}")
        
        # Installation instructions
        if distro == "debian":
            print("\nFor Ubuntu/Debian:")
            print("1. Install dependencies:")
            print("   sudo apt-get update")
            print("   sudo apt-get install -y \\")
            print("       build-essential \\")
            print("       libssl-dev \\")
            print("       uuid-dev \\")
            print("       libgpgme-dev \\")
            print("       squashfs-tools \\")
            print("       libseccomp-dev \\")
            print("       pkg-config")
            print("\n2. Install Go (required):")
            print("   wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz")
            print("   sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz")
            print("   echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc")
            print("   source ~/.bashrc")
            print("\n3. Install Apptainer (recommended):")
            print("   wget https://github.com/apptainer/apptainer/releases/download/v1.2.0/apptainer_1.2.0_amd64.deb")
            print("   sudo dpkg -i apptainer_1.2.0_amd64.deb")
            print("\n4. OR Install Singularity:")
            print("   See: https://docs.sylabs.io/guides/admin-guide/installation.html")
            
        elif distro == "rhel":
            print("\nFor RHEL/CentOS/Rocky:")
            print("1. Enable EPEL repository:")
            print("   sudo yum install -y epel-release")
            print("\n2. Install dependencies:")
            print("   sudo yum groupinstall -y 'Development Tools'")
            print("   sudo yum install -y \\")
            print("       openssl-devel \\")
            print("       libuuid-devel \\")
            print("       squashfs-tools \\")
            print("       libseccomp-devel")
            print("\n3. Install Go and Apptainer from source or use conda:")
            print("   conda install -c conda-forge apptainer")
            
        elif distro == "arch":
            print("\nFor Arch Linux:")
            print("   yay -S apptainer  # or singularity from AUR")
            
        elif distro == "fedora":
            print("\nFor Fedora:")
            print("   sudo dnf install -y apptainer")
            
        else:
            print("\nGeneral installation instructions:")
            print("1. Check official documentation:")
            print("   Apptainer: https://apptainer.org/docs/admin/main/installation.html")
            print("   Singularity: https://docs.sylabs.io/guides/admin-guide/installation.html")
            print("\n2. Using conda (recommended for users):")
            print("   conda create -n apptainer -c conda-forge apptainer")
            print("   conda activate apptainer")
        
        print("\n3. Verify installation:")
        print("   apptainer --version  # or singularity --version")
        
    elif system == "darwin":  # macOS
        print("\nFor macOS:")
        print("Using conda (recommended):")
        print("  conda install -c conda-forge apptainer")
        print("\nOr using Homebrew:")
        print("  brew install --cask docker  # Required for VM")
        print("  brew install singularity")
        print("\nNote: On macOS, Singularity runs in a VM")
        
    else:
        print(f"\nUnsupported system: {system}")
        print("Please see:")
        print("- https://apptainer.org/docs/admin/main/installation.html")
        print("- https://docs.sylabs.io/guides/admin-guide/installation.html")
    
    print("\n⚠️  Note: Some installations require root privileges.")
    print("  Consider using conda installation for user-space setup.")
    
    return True

def create_apptainer_sandbox(
    base_image: str,
    sandbox_dir: str,
    image_type: str = "sandbox",
    force: bool = False,
    pull_folder: str = None,
    library_url: str = "https://library.sylabs.io",
    auth_token: str = None,
    keystore: str = None
) -> Dict[str, Any]:
    """
    Create a sandbox/writable Singularity container from a base image.
    
    Args:
        base_image: Source image (docker://, library://, shub://, oras://, etc.)
        sandbox_dir: Directory for the sandbox
        image_type: 'sandbox' (writable) or 'sif' (read-only single file)
        force: Overwrite existing sandbox
        pull_folder: Cache directory for pulled images
        library_url: Container library URL
        auth_token: Authentication token for private images
        keystore: GPG keystore for verified images
    
    Returns:
        Dictionary with operation results
    """
    apptainer_info = check_apptainer_availability()
    if not apptainer_info["available"]:
        return {
            "success": False,
            "error": "Apptainer/Singularity not available",
            "message": apptainer_info["message"]
        }
    
    cmd = apptainer_info["command"]
    sandbox_dir = os.path.abspath(os.path.expanduser(sandbox_dir))
    
    # Check if sandbox already exists
    if os.path.exists(sandbox_dir) and not force:
        return {
            "success": True,
            "sandbox_dir": sandbox_dir,
            "message": f"Sandbox already exists at {sandbox_dir}",
            "existing": True
        }
    
    # Remove existing if force=True
    if force and os.path.exists(sandbox_dir):
        try:
            if os.path.isdir(sandbox_dir):
                shutil.rmtree(sandbox_dir)
            else:
                os.remove(sandbox_dir)
        except Exception as e:
            return {
                "success": False,
                "error": f"Could not remove existing sandbox: {e}",
                "sandbox_dir": sandbox_dir
            }
    
    # Create parent directory if it doesn't exist
    os.makedirs(os.path.dirname(sandbox_dir), exist_ok=True)
    
    # Build command
    singularity_cmd = [cmd, "build"]
    
    # Add options based on image type
    if image_type == "sandbox":
        singularity_cmd.append("--sandbox")
    
    # Add authentication if provided
    if auth_token:
        singularity_cmd.extend(["--authfile", auth_token])
    
    # Add keystore if provided
    if keystore:
        singularity_cmd.extend(["--keyring", keystore])
    
    # Add library URL if provided
    if library_url and not base_image.startswith(("docker://", "shub://", "oras://")):
        singularity_cmd.extend(["--library", library_url])
    
    # Add pull folder if provided
    if pull_folder:
        singularity_cmd.extend(["--pull-folder", pull_folder])
    
    # Add target and source
    singularity_cmd.append(sandbox_dir)
    singularity_cmd.append(base_image)
    
    # Execute command
    print(f"Creating {image_type} from {base_image}...")
    print(f"Command: {' '.join(singularity_cmd)}")
    
    try:
        result = subprocess.run(
            singularity_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✓ Successfully created {image_type} at {sandbox_dir}")
        
        return {
            "success": True,
            "sandbox_dir": sandbox_dir,
            "output": result.stdout,
            "stderr": result.stderr,
            "command": ' '.join(singularity_cmd)
        }
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to create {image_type}: {e.stderr}"
        print(f"✗ {error_msg}")
        
        return {
            "success": False,
            "error": error_msg,
            "sandbox_dir": sandbox_dir,
            "stderr": e.stderr,
            "stdout": e.stdout,
            "returncode": e.returncode
        }
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"✗ {error_msg}")
        
        return {
            "success": False,
            "error": error_msg,
            "sandbox_dir": sandbox_dir
        }

def create_development_sandbox(
    base_image: str = "docker://ubuntu:22.04",
    sandbox_dir: str = "~/singularity_sandbox",
    packages: List[str] = None,
    pip_packages: List[str] = None,
    conda_packages: List[str] = None,
    environment_vars: Dict[str, str] = None,
    files_to_copy: Dict[str, str] = None,
    post_install_commands: List[str] = None,
    force: bool = False,
    gpu_support: bool = False,
    cuda_version: str = None,
    rocm_version: str = None,
    mpi_support: bool = False,
    mpi_flavor: str = "openmpi",
    workdir: str = "/workspace",
    shell: str = "/bin/bash"
) -> Dict[str, Any]:
    """
    Create a development sandbox with common development tools and configurations.
    
    Args:
        base_image: Base container image
        sandbox_dir: Directory for the sandbox
        packages: System packages to install
        pip_packages: Python packages to install via pip
        conda_packages: Conda packages to install
        environment_vars: Environment variables to set
        files_to_copy: Files to copy into container (host_path: container_path)
        post_install_commands: Commands to run after installation
        force: Overwrite existing sandbox
        gpu_support: Enable GPU support
        cuda_version: CUDA version for GPU support
        rocm_version: ROCm version for AMD GPU support
        mpi_support: Enable MPI support
        mpi_flavor: MPI implementation (openmpi, mpich, intel-mpi)
        workdir: Default working directory
        shell: Default shell
    
    Returns:
        Dictionary with operation results
    """
    if packages is None:
        packages = []
    
    if pip_packages is None:
        pip_packages = []
    
    if conda_packages is None:
        conda_packages = []
    
    if environment_vars is None:
        environment_vars = {}
    
    if files_to_copy is None:
        files_to_copy = {}
    
    if post_install_commands is None:
        post_install_commands = []
    
    # Create temporary definition file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.def', delete=False) as def_file:
        definition = generate_singularity_definition(
            base_image=base_image,
            packages=packages,
            pip_packages=pip_packages,
            conda_packages=conda_packages,
            environment_vars=environment_vars,
            files_to_copy=files_to_copy,
            post_install_commands=post_install_commands,
            gpu_support=gpu_support,
            cuda_version=cuda_version,
            rocm_version=rocm_version,
            mpi_support=mpi_support,
            mpi_flavor=mpi_flavor,
            workdir=workdir,
            shell=shell
        )
        
        def_file.write(definition)
        def_file_path = def_file.name
    
    try:
        # Build from definition file
        result = create_apptainer_sandbox(
            base_image=def_file_path,
            sandbox_dir=sandbox_dir,
            image_type="sandbox",
            force=force
        )
        
        # Clean up definition file
        os.unlink(def_file_path)
        
        return result
        
    except Exception as e:
        # Clean up definition file on error
        if os.path.exists(def_file_path):
            os.unlink(def_file_path)
        raise

def generate_singularity_definition(
    base_image: str = "docker://ubuntu:22.04",
    packages: List[str] = None,
    pip_packages: List[str] = None,
    conda_packages: List[str] = None,
    environment_vars: Dict[str, str] = None,
    files_to_copy: Dict[str, str] = None,
    post_install_commands: List[str] = None,
    gpu_support: bool = False,
    cuda_version: str = None,
    rocm_version: str = None,
    mpi_support: bool = False,
    mpi_flavor: str = "openmpi",
    workdir: str = "/workspace",
    shell: str = "/bin/bash"
) -> str:
    """
    Generate a Singularity definition file.
    
    Returns:
        Singularity definition file content
    """
    if packages is None:
        packages = []
    
    if pip_packages is None:
        pip_packages = []
    
    if conda_packages is None:
        conda_packages = []
    
    if environment_vars is None:
        environment_vars = {}
    
    if files_to_copy is None:
        files_to_copy = {}
    
    if post_install_commands is None:
        post_install_commands = []
    
    # Default packages for development
    default_packages = [
        # Core development
        "build-essential",
        "cmake",
        "pkg-config",
        "git",
        "curl",
        "wget",
        "vim",
        "nano",
        
        # Python
        "python3",
        "python3-pip",
        "python3-dev",
        "python3-venv",
        
        # System tools
        "htop",
        "tree",
        "rsync",
        "unzip",
        "ssh",
        
        # Network tools
        "net-tools",
        "iputils-ping",
        "dnsutils",
        
        # Compression
        "gzip",
        "bzip2",
        "xz-utils",
        "zip",
        
        # Editors
        "emacs-nox",
        "micro",
    ]
    
    # Combine packages
    all_packages = default_packages + packages
    
    # Add GPU support packages
    gpu_packages = []
    if gpu_support:
        if cuda_version:
            # CUDA support
            cuda_major = cuda_version.split('.')[0] if cuda_version else "12"
            gpu_packages.extend([
                f"cuda-toolkit-{cuda_major}-0",
                "nvidia-cuda-dev",
                "nvidia-container-toolkit"
            ])
        elif rocm_version:
            # ROCm support
            gpu_packages.extend([
                "rocm-dev",
                "hip-dev",
                "rocblas",
                "rocsolver"
            ])
    
    # Add MPI support packages
    mpi_packages = []
    if mpi_support:
        if mpi_flavor == "openmpi":
            mpi_packages.extend(["openmpi-bin", "libopenmpi-dev"])
        elif mpi_flavor == "mpich":
            mpi_packages.extend(["mpich", "libmpich-dev"])
        elif mpi_flavor == "intel-mpi":
            mpi_packages.append("intel-mpi")  # Usually from Intel repos
    
    all_packages.extend(gpu_packages + mpi_packages)
    
    # Start building definition
    lines = [
        f"Bootstrap: docker",
        f"From: {base_image.replace('docker://', '')}",
        "",
        "%post",
        "    # Update and install packages",
        "    apt-get update -y",
        "    apt-get install -y --no-install-recommends \\"
    ]
    
    # Add packages in chunks to avoid line length issues
    package_chunks = [all_packages[i:i+10] for i in range(0, len(all_packages), 10)]
    for chunk in package_chunks:
        if chunk == package_chunks[0]:
            lines.append("        " + " \\\n        ".join(chunk))
        else:
            lines[-1] += " \\"
            lines.append("        " + " \\\n        ".join(chunk))
    
    lines.extend([
        "    ",
        "    # Clean up",
        "    apt-get clean",
        "    rm -rf /var/lib/apt/lists/*",
        "",
        "    # Install pip packages",
    ])
    
    if pip_packages:
        lines.append(f"    pip3 install --upgrade pip")
        lines.append(f"    pip3 install {' '.join(pip_packages)}")
    
    # Add conda installation if requested
    if conda_packages:
        lines.extend([
            "",
            "    # Install Miniconda",
            "    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh",
            "    bash /tmp/miniconda.sh -b -p /opt/conda",
            "    rm /tmp/miniconda.sh",
            "    echo 'export PATH=/opt/conda/bin:$PATH' >> /etc/profile",
            "",
            "    # Install conda packages",
            f"    /opt/conda/bin/conda install -y {' '.join(conda_packages)}",
            "    /opt/conda/bin/conda clean -y --all"
        ])
    
    # Add post-install commands
    if post_install_commands:
        lines.append("")
        lines.append("    # Post-install commands")
        for cmd in post_install_commands:
            lines.append(f"    {cmd}")
    
    # Environment section
    lines.extend([
        "",
        "%environment",
        f"    export SHELL={shell}",
        f"    export WORKDIR={workdir}",
        "    export LC_ALL=C.UTF-8",
        "    export LANG=C.UTF-8",
        "    export PYTHONUNBUFFERED=1",
    ])
    
    # Add custom environment variables
    for key, value in environment_vars.items():
        lines.append(f"    export {key}={value}")
    
    # Add conda to PATH if installed
    if conda_packages:
        lines.append("    export PATH=/opt/conda/bin:$PATH")
    
    # Add GPU environment variables
    if gpu_support:
        lines.append("    # GPU support")
        lines.append("    export NVIDIA_VISIBLE_DEVICES=all")
        lines.append("    export NVIDIA_DRIVER_CAPABILITIES=compute,utility")
        if cuda_version:
            lines.append(f"    export CUDA_VERSION={cuda_version}")
            lines.append("    export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH")
            lines.append("    export PATH=/usr/local/cuda/bin:$PATH")
    
    # Files section
    if files_to_copy:
        lines.extend(["", "%files"])
        for host_path, container_path in files_to_copy.items():
            lines.append(f"    {host_path} {container_path}")
    
    # Labels section
    lines.extend([
        "",
        "%labels",
        f"    Author {getpass.getuser()}",
        f"    Version 1.0",
        f"    Description Development sandbox",
        f"    Created {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ])
    
    # Runscript section
    lines.extend([
        "",
        "%runscript",
        f"    cd {workdir}",
        "    exec /bin/bash \"$@\"",
        "",
        "%startscript",
        "    # Commands to run when container starts",
        f"    cd {workdir}",
        "    echo 'Container started at $(date)'",
        "",
        "%test",
        "    # Test commands",
        "    python3 --version",
        "    pip3 --version",
        "    git --version",
        "",
        "%help",
        "    This is a development sandbox container.",
        "    Mount your workspace to /workspace for persistent storage.",
        "    Example: singularity shell --bind /host/path:/workspace sandbox/",
    ])
    
    return "\n".join(lines)

def run_singularity_command(
    image_path: str,
    command: str,
    bind_mounts: Dict[str, str] = None,
    environment: Dict[str, str] = None,
    working_dir: str = None,
    home_dir: str = None,
    scratch_dir: str = "/tmp",
    gpu: bool = False,
    nv_gpu: bool = False,
    rocm_gpu: bool = False,
    enable_networking: bool = True,
    hostname: str = None,
    network: str = None,
    security_options: List[str] = None,
    cleanup: bool = True,
    writable_tmpfs: bool = False,
    fakeroot: bool = False,
    keep_privileges: bool = False,
    singularity_options: List[str] = None
) -> Dict[str, Any]:
    """
    Run a command inside a Singularity container.
    
    Args:
        image_path: Path to Singularity image or sandbox
        command: Command to run inside container
        bind_mounts: Bind mounts (host_path: container_path)
        environment: Environment variables to set
        working_dir: Working directory inside container
        home_dir: Home directory inside container
        scratch_dir: Scratch directory
        gpu: Enable GPU support
        nv_gpu: Enable NVIDIA GPU support
        rocm_gpu: Enable AMD ROCm GPU support
        enable_networking: Enable network access
        hostname: Set container hostname
        network: Network type (bridge, none, host, etc.)
        security_options: Security options (seccomp, etc.)
        cleanup: Clean up temporary files
        writable_tmpfs: Mount tmpfs as writable
        fakeroot: Use fakeroot for unprivileged builds
        keep_privileges: Keep user privileges
        singularity_options: Additional Singularity options
    
    Returns:
        Dictionary with command results
    """
    apptainer_info = check_apptainer_availability()
    if not apptainer_info["available"]:
        return {
            "success": False,
            "error": "Apptainer/Singularity not available",
            "message": apptainer_info["message"]
        }
    
    cmd = apptainer_info["command"]
    image_path = os.path.expanduser(image_path)
    
    # Check if image exists
    if not os.path.exists(image_path):
        return {
            "success": False,
            "error": f"Image not found: {image_path}",
            "image_path": image_path
        }
    
    # Build command
    singularity_cmd = [cmd, "exec"]
    
    # Add bind mounts
    if bind_mounts:
        for host_path, container_path in bind_mounts.items():
            host_path = os.path.expanduser(host_path)
            singularity_cmd.extend(["--bind", f"{host_path}:{container_path}"])
    
    # Add environment variables
    if environment:
        for key, value in environment.items():
            singularity_cmd.extend(["--env", f"{key}={value}"])
    
    # Add working directory
    if working_dir:
        singularity_cmd.extend(["--pwd", working_dir])
    
    # Add home directory
    if home_dir:
        singularity_cmd.extend(["--home", home_dir])
    
    # Add GPU support
    if gpu or nv_gpu:
        singularity_cmd.append("--nv")  # NVIDIA GPU
    elif rocm_gpu:
        singularity_cmd.append("--rocm")  # AMD ROCm GPU
    
    # Add network options
    if not enable_networking:
        singularity_cmd.append("--net")
        singularity_cmd.append("--network")
        singularity_cmd.append("none")
    elif network:
        singularity_cmd.extend(["--network", network])
    
    # Add hostname
    if hostname:
        singularity_cmd.extend(["--hostname", hostname])
    
    # Add security options
    if security_options:
        for opt in security_options:
            singularity_cmd.extend(["--security", opt])
    
    # Add writable tmpfs
    if writable_tmpfs:
        singularity_cmd.append("--writable-tmpfs")
    
    # Add fakeroot
    if fakeroot:
        singularity_cmd.append("--fakeroot")
    
    # Add keep privileges
    if keep_privileges:
        singularity_cmd.append("--keep-privs")
    
    # Add additional options
    if singularity_options:
        singularity_cmd.extend(singularity_options)
    
    # Add scratch directory
    singularity_cmd.extend(["--scratch", scratch_dir])
    
    # Add cleanup
    if cleanup:
        singularity_cmd.append("--cleanenv")
    
    # Add image path and command
    singularity_cmd.append(image_path)
    singularity_cmd.extend(["sh", "-c", command])
    
    # Execute command
    print(f"Running command in container: {command}")
    print(f"Image: {image_path}")
    
    try:
        result = subprocess.run(
            singularity_cmd,
            capture_output=True,
            text=True,
            check=False  # Don't raise exception on non-zero return
        )
        
        output = {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": ' '.join(singularity_cmd),
            "image_path": image_path
        }
        
        if result.returncode == 0:
            print(f"✓ Command executed successfully")
        else:
            print(f"✗ Command failed with return code {result.returncode}")
            print(f"Stderr: {result.stderr[:500]}...")
        
        return output
        
    except Exception as e:
        error_msg = f"Failed to execute command: {str(e)}"
        print(f"✗ {error_msg}")
        
        return {
            "success": False,
            "error": error_msg,
            "image_path": image_path,
            "command": command
        }

def shell_into_container(
    image_path: str,
    bind_mounts: Dict[str, str] = None,
    environment: Dict[str, str] = None,
    working_dir: str = None,
    home_dir: str = None,
    gpu: bool = False,
    nv_gpu: bool = False,
    rocm_gpu: bool = False,
    enable_networking: bool = True,
    hostname: str = None,
    fakeroot: bool = False,
    shell: str = "/bin/bash"
) -> None:
    """
    Start an interactive shell inside a Singularity container.
    
    Args:
        image_path: Path to Singularity image or sandbox
        bind_mounts: Bind mounts (host_path: container_path)
        environment: Environment variables to set
        working_dir: Working directory inside container
        home_dir: Home directory inside container
        gpu: Enable GPU support
        nv_gpu: Enable NVIDIA GPU support
        rocm_gpu: Enable AMD ROCm GPU support
        enable_networking: Enable network access
        hostname: Set container hostname
        fakeroot: Use fakeroot for unprivileged builds
        shell: Shell to use
    
    Returns:
        None (starts interactive shell)
    """
    apptainer_info = check_apptainer_availability()
    if not apptainer_info["available"]:
        print(f"✗ {apptainer_info['message']}")
        return
    
    cmd = apptainer_info["command"]
    image_path = os.path.expanduser(image_path)
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"✗ Image not found: {image_path}")
        return
    
    # Build command
    singularity_cmd = [cmd, "shell"]
    
    # Add bind mounts
    if bind_mounts:
        for host_path, container_path in bind_mounts.items():
            host_path = os.path.expanduser(host_path)
            singularity_cmd.extend(["--bind", f"{host_path}:{container_path}"])
    
    # Add environment variables
    if environment:
        for key, value in environment.items():
            singularity_cmd.extend(["--env", f"{key}={value}"])
    
    # Add working directory
    if working_dir:
        singularity_cmd.extend(["--pwd", working_dir])
    
    # Add home directory
    if home_dir:
        singularity_cmd.extend(["--home", home_dir])
    
    # Add GPU support
    if gpu or nv_gpu:
        singularity_cmd.append("--nv")
    elif rocm_gpu:
        singularity_cmd.append("--rocm")
    
    # Add network options
    if not enable_networking:
        singularity_cmd.extend(["--net", "--network", "none"])
    
    # Add hostname
    if hostname:
        singularity_cmd.extend(["--hostname", hostname])
    
    # Add fakeroot
    if fakeroot:
        singularity_cmd.append("--fakeroot")
    
    # Add image path
    singularity_cmd.append(image_path)
    
    # Execute command (interactive)
    print(f"Starting interactive shell in container")
    print(f"Image: {image_path}")
    print(f"Shell: {shell}")
    print(f"Working directory: {working_dir or '/workspace'}")
    
    if bind_mounts:
        print("Bind mounts:")
        for host_path, container_path in bind_mounts.items():
            print(f"  {host_path} -> {container_path}")
    
    print("\nType 'exit' to leave the container")
    print("-" * 50)
    
    try:
        subprocess.run(singularity_cmd, check=True)
        print("\n" + "-" * 50)
        print("Exited container")
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Failed to start shell: {e}")
    
    except KeyboardInterrupt:
        print("\n\nShell interrupted")

def convert_docker_to_singularity(
    docker_image: str,
    singularity_image: str,
    force: bool = False,
    sandbox: bool = False,
    library_url: str = "https://library.sylabs.io",
    auth_token: str = None,
    build_args: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Convert a Docker image to a Singularity image.
    
    Args:
        docker_image: Docker image name (e.g., ubuntu:22.04)
        singularity_image: Output Singularity image path
        force: Overwrite existing image
        sandbox: Create writable sandbox instead of SIF
        library_url: Container library URL
        auth_token: Authentication token
        build_args: Build arguments
    
    Returns:
        Dictionary with operation results
    """
    apptainer_info = check_apptainer_availability()
    if not apptainer_info["available"]:
        return {
            "success": False,
            "error": "Apptainer/Singularity not available",
            "message": apptainer_info["message"]
        }
    
    cmd = apptainer_info["command"]
    singularity_image = os.path.expanduser(singularity_image)
    
    # Check if output already exists
    if os.path.exists(singularity_image) and not force:
        return {
            "success": True,
            "singularity_image": singularity_image,
            "message": f"Image already exists at {singularity_image}",
            "existing": True
        }
    
    # Remove existing if force=True
    if force and os.path.exists(singularity_image):
        try:
            if os.path.isdir(singularity_image):
                shutil.rmtree(singularity_image)
            else:
                os.remove(singularity_image)
        except Exception as e:
            return {
                "success": False,
                "error": f"Could not remove existing image: {e}",
                "singularity_image": singularity_image
            }
    
    # Ensure Docker image has docker:// prefix
    if not docker_image.startswith("docker://"):
        docker_image = f"docker://{docker_image}"
    
    # Create parent directory if it doesn't exist
    os.makedirs(os.path.dirname(singularity_image), exist_ok=True)
    
    # Build command
    singularity_cmd = [cmd, "build"]
    
    # Add sandbox option
    if sandbox:
        singularity_cmd.append("--sandbox")
    
    # Add authentication if provided
    if auth_token:
        singularity_cmd.extend(["--authfile", auth_token])
    
    # Add library URL
    if library_url:
        singularity_cmd.extend(["--library", library_url])
    
    # Add build arguments
    if build_args:
        for key, value in build_args.items():
            singularity_cmd.extend(["--build-arg", f"{key}={value}"])
    
    # Add output and input
    singularity_cmd.append(singularity_image)
    singularity_cmd.append(docker_image)
    
    # Execute command
    print(f"Converting Docker image {docker_image} to Singularity...")
    print(f"Output: {singularity_image}")
    print(f"Command: {' '.join(singularity_cmd)}")
    
    try:
        result = subprocess.run(
            singularity_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✓ Successfully converted Docker image to Singularity")
        
        return {
            "success": True,
            "singularity_image": singularity_image,
            "docker_image": docker_image,
            "output": result.stdout,
            "stderr": result.stderr,
            "command": ' '.join(singularity_cmd)
        }
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to convert Docker image: {e.stderr}"
        print(f"✗ {error_msg}")
        
        return {
            "success": False,
            "error": error_msg,
            "singularity_image": singularity_image,
            "docker_image": docker_image,
            "stderr": e.stderr,
            "stdout": e.stdout,
            "returncode": e.returncode
        }
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"✗ {error_msg}")
        
        return {
            "success": False,
            "error": error_msg,
            "singularity_image": singularity_image,
            "docker_image": docker_image
        }

def create_singularity_workstation(
    work_dir: str = "~/singularity_workstation",
    base_image: str = "docker://ubuntu:22.04",
    image_name: str = "dev_sandbox",
    packages: List[str] = None,
    pip_packages: List[str] = None,
    conda_packages: List[str] = None,
    environment_vars: Dict[str, str] = None,
    bind_mounts: Dict[str, str] = None,
    force_rebuild: bool = False,
    gpu_support: bool = False,
    cuda_version: str = None,
    rocm_version: str = None,
    mpi_support: bool = False,
    create_wrapper_scripts: bool = True,
    create_config_file: bool = True,
    config_file: str = None
) -> Dict[str, Any]:
    """
    Create a comprehensive Singularity development workstation.
    
    Args:
        work_dir: Workspace directory
        base_image: Base container image
        image_name: Name for the Singularity image/sandbox
        packages: System packages to install
        pip_packages: Python packages to install
        conda_packages: Conda packages to install
        environment_vars: Environment variables to set
        bind_mounts: Default bind mounts
        force_rebuild: Force rebuild even if image exists
        gpu_support: Enable GPU support
        cuda_version: CUDA version for GPU support
        rocm_version: ROCm version for AMD GPU support
        mpi_support: Enable MPI support
        create_wrapper_scripts: Create helper scripts
        create_config_file: Create configuration file
        config_file: Load configuration from file
    
    Returns:
        Dictionary with operation results
    """
    # Load configuration from file if provided
    if config_file:
        config = load_apptainer_config(config_file)
        # Update arguments with config values
        for key, value in config.items():
            if key in locals():
                locals()[key] = value
    
    # Initialize defaults
    if packages is None:
        packages = []
    
    if pip_packages is None:
        pip_packages = []
    
    if conda_packages is None:
        conda_packages = []
    
    if environment_vars is None:
        environment_vars = {}
    
    if bind_mounts is None:
        bind_mounts = {}
    
    # Expand paths
    work_dir = os.path.expanduser(work_dir)
    work_dir = os.path.abspath(work_dir)
    
    # Create workspace directory
    os.makedirs(work_dir, exist_ok=True)
    
    # Paths for images and scripts
    sandbox_dir = os.path.join(work_dir, f"{image_name}_sandbox")
    sif_file = os.path.join(work_dir, f"{image_name}.sif")
    scripts_dir = os.path.join(work_dir, "scripts")
    config_dir = os.path.join(work_dir, "config")
    
    # Check if sandbox already exists
    if os.path.exists(sandbox_dir) and not force_rebuild:
        print(f"✓ Sandbox already exists at {sandbox_dir}")
        print(f"  Use --force-rebuild to recreate")
        
        result = {
            "success": True,
            "sandbox_dir": sandbox_dir,
            "sif_file": sif_file if os.path.exists(sif_file) else None,
            "work_dir": work_dir,
            "existing": True
        }
    
    else:
        # Create sandbox
        print(f"Creating development sandbox from {base_image}...")
        
        result = create_development_sandbox(
            base_image=base_image,
            sandbox_dir=sandbox_dir,
            packages=packages,
            pip_packages=pip_packages,
            conda_packages=conda_packages,
            environment_vars=environment_vars,
            gpu_support=gpu_support,
            cuda_version=cuda_version,
            rocm_version=rocm_version,
            mpi_support=mpi_support,
            force=force_rebuild
        )
        
        if not result["success"]:
            return result
    
    # Create SIF file from sandbox (optional but recommended for portability)
    if result["success"] and not os.path.exists(sif_file):
        print(f"\nCreating SIF file for portability...")
        sif_result = create_apptainer_sandbox(
            base_image=sandbox_dir,
            sandbox_dir=sif_file,
            image_type="sif",
            force=True
        )
        
        if sif_result["success"]:
            print(f"✓ SIF file created: {sif_file}")
        else:
            print(f"⚠️ Could not create SIF file: {sif_result.get('error', 'Unknown error')}")
    
    # Create wrapper scripts
    if create_wrapper_scripts and result["success"]:
        print(f"\nCreating wrapper scripts...")
        create_wrapper_scripts_for_sandbox(
            sandbox_dir=sandbox_dir,
            sif_file=sif_file if os.path.exists(sif_file) else None,
            work_dir=work_dir,
            bind_mounts=bind_mounts,
            gpu_support=gpu_support,
            scripts_dir=scripts_dir
        )
    
    # Create configuration file
    if create_config_file:
        config_data = {
            "work_dir": work_dir,
            "sandbox_dir": sandbox_dir,
            "sif_file": sif_file if os.path.exists(sif_file) else None,
            "base_image": base_image,
            "image_name": image_name,
            "packages": packages,
            "pip_packages": pip_packages,
            "conda_packages": conda_packages,
            "environment_vars": environment_vars,
            "bind_mounts": bind_mounts,
            "gpu_support": gpu_support,
            "cuda_version": cuda_version,
            "rocm_version": rocm_version,
            "mpi_support": mpi_support,
            "created": datetime.now().isoformat()
        }
        
        config_path = os.path.join(config_dir, "apptainer_config.json")
        os.makedirs(config_dir, exist_ok=True)
        
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)
        
        print(f"✓ Configuration saved to {config_path}")
    
    # Display usage instructions
    if result["success"]:
        display_apptainer_instructions(
            work_dir=work_dir,
            sandbox_dir=sandbox_dir,
            sif_file=sif_file if os.path.exists(sif_file) else None,
            bind_mounts=bind_mounts,
            gpu_support=gpu_support,
            image_name=image_name
        )
    
    return result

def create_wrapper_scripts_for_sandbox(
    sandbox_dir: str,
    work_dir: str,
    bind_mounts: Dict[str, str] = None,
    gpu_support: bool = False,
    scripts_dir: str = "scripts",
    sif_file: str = None
) -> None:
    """
    Create wrapper scripts for easy interaction with the sandbox.
    
    Args:
        sandbox_dir: Path to sandbox directory
        work_dir: Workspace directory
        bind_mounts: Default bind mounts
        gpu_support: Enable GPU support in scripts
        scripts_dir: Directory for scripts
        sif_file: Optional SIF file path
    """
    if bind_mounts is None:
        bind_mounts = {}
    
    # Create scripts directory
    scripts_path = os.path.join(work_dir, scripts_dir)
    os.makedirs(scripts_path, exist_ok=True)
    
    # Determine which image to use
    image_path = sif_file if sif_file and os.path.exists(sif_file) else sandbox_dir
    
    # Common bind mounts
    default_binds = {
        work_dir: "/workspace",
        os.path.expanduser("~/.ssh"): "/root/.ssh",
        os.path.expanduser("~/.gitconfig"): "/root/.gitconfig",
        "/tmp": "/tmp"
    }
    
    # Add custom bind mounts
    if bind_mounts:
        default_binds.update(bind_mounts)
    
    # Build bind mount string for scripts
    bind_args = []
    for host_path, container_path in default_binds.items():
        host_path = os.path.expanduser(host_path)
        if os.path.exists(host_path):
            bind_args.append(f"--bind {host_path}:{container_path}")
    
    bind_string = " ".join(bind_args)
    
    # GPU flag
    gpu_flag = "--nv" if gpu_support else ""
    
    # Script 1: Enter shell
    shell_script = os.path.join(scripts_path, "enter_sandbox.sh")
    shell_content = f"""#!/bin/bash
# Enter the development sandbox
SINGULARITY_CMD="$(which apptainer 2>/dev/null || which singularity 2>/dev/null)"

if [ -z "$SINGULARITY_CMD" ]; then
    echo "Error: Neither apptainer nor singularity found in PATH"
    exit 1
fi

echo "Entering development sandbox..."
echo "Sandbox: {sandbox_dir}"
echo "Working directory: /workspace"
echo ""

$SINGULARITY_CMD shell {gpu_flag} {bind_string} {image_path}
"""
    
    with open(shell_script, "w") as f:
        f.write(shell_content)
    
    os.chmod(shell_script, 0o755)
    
    # Script 2: Run command
    run_script = os.path.join(scripts_path, "run_in_sandbox.sh")
    run_content = f"""#!/bin/bash
# Run a command in the development sandbox
SINGULARITY_CMD="$(which apptainer 2>/dev/null || which singularity 2>/dev/null)"

if [ -z "$SINGULARITY_CMD" ]; then
    echo "Error: Neither apptainer nor singularity found in PATH"
    exit 1
fi

if [ $# -eq 0 ]; then
    echo "Usage: $0 <command> [args...]"
    echo "Example: $0 python script.py"
    exit 1
fi

echo "Running command in sandbox: $@"
echo ""

$SINGULARITY_CMD exec {gpu_flag} {bind_string} {image_path} "$@"
"""
    
    with open(run_script, "w") as f:
        f.write(run_content)
    
    os.chmod(run_script, 0o755)
    
    # Script 3: Start Jupyter
    jupyter_script = os.path.join(scripts_path, "start_jupyter.sh")
    jupyter_content = f"""#!/bin/bash
# Start Jupyter server in the sandbox
SINGULARITY_CMD="$(which apptainer 2>/dev/null || which singularity 2>/dev/null)"

if [ -z "$SINGULARITY_CMD" ]; then
    echo "Error: Neither apptainer nor singularity found in PATH"
    exit 1
fi

PORT=${{1:-8888}}
NOTEBOOK_DIR=${{2:-/workspace}}

echo "Starting Jupyter on port $PORT..."
echo "Notebook directory: $NOTEBOOK_DIR"
echo ""
echo "Open in browser: http://localhost:$PORT"
echo ""

$SINGULARITY_CMD exec {gpu_flag} {bind_string} \\
    --env JUPYTER_PORT=$PORT \\
    --env JUPYTER_NOTEBOOK_DIR=$NOTEBOOK_DIR \\
    {image_path} \\
    jupyter lab --ip=0.0.0.0 --port=$PORT --no-browser --notebook-dir=$NOTEBOOK_DIR
"""
    
    with open(jupyter_script, "w") as f:
        f.write(jupyter_content)
    
    os.chmod(jupyter_script, 0o755)
    
    # Script 4: Python environment
    python_script = os.path.join(scripts_path, "python_env.sh")
    python_content = f"""#!/bin/bash
# Set up Python virtual environment in sandbox
SINGULARITY_CMD="$(which apptainer 2>/dev/null || which singularity 2>/dev/null)"

if [ -z "$SINGULARITY_CMD" ]; then
    echo "Error: Neither apptainer nor singularity found in PATH"
    exit 1
fi

VENV_DIR="/workspace/venv"

echo "Setting up Python virtual environment..."
echo ""

$SINGULARITY_CMD exec {bind_string} {image_path} \\
    bash -c "
        if [ ! -d "$VENV_DIR" ]; then
            echo 'Creating virtual environment...'
            python3 -m venv $VENV_DIR
        fi
        
        echo 'Activating virtual environment...'
        source $VENV_DIR/bin/activate
        
        echo 'Upgrading pip...'
        pip install --upgrade pip
        
        echo 'Virtual environment ready at $VENV_DIR'
        echo 'To activate: source $VENV_DIR/bin/activate'
    "
"""
    
    with open(python_script, "w") as f:
        f.write(python_content)
    
    os.chmod(python_script, 0o755)
    
    # Script 5: Backup sandbox
    backup_script = os.path.join(scripts_path, "backup_sandbox.sh")
    backup_content = f"""#!/bin/bash
# Backup the sandbox
BACKUP_DIR="{work_dir}/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="sandbox_backup_$TIMESTAMP"

echo "Backing up sandbox..."
echo "Source: {sandbox_dir}"
echo "Destination: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
echo ""

mkdir -p "$BACKUP_DIR"

# Create backup
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" -C "{os.path.dirname(sandbox_dir)}" "{os.path.basename(sandbox_dir)}"

if [ $? -eq 0 ]; then
    echo "✓ Backup created: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
    echo "Size: $(du -h "$BACKUP_DIR/$BACKUP_NAME.tar.gz" | cut -f1)"
else
    echo "✗ Backup failed"
    exit 1
fi
"""
    
    with open(backup_script, "w") as f:
        f.write(backup_content)
    
    os.chmod(backup_script, 0o755)
    
    print(f"Created wrapper scripts in {scripts_path}:")
    print(f"  enter_sandbox.sh    - Enter interactive shell")
    print(f"  run_in_sandbox.sh   - Run command in sandbox")
    print(f"  start_jupyter.sh    - Start Jupyter server")
    print(f"  python_env.sh       - Set up Python environment")
    print(f"  backup_sandbox.sh   - Backup sandbox")

def display_apptainer_instructions(
    work_dir: str,
    sandbox_dir: str,
    bind_mounts: Dict[str, str] = None,
    gpu_support: bool = False,
    image_name: str = "dev_sandbox",
    sif_file: str = None
) -> None:
    """
    Display comprehensive usage instructions for the Singularity workstation.
    
    Args:
        work_dir: Workspace directory
        sandbox_dir: Path to sandbox directory
        bind_mounts: Default bind mounts
        gpu_support: GPU support enabled
        image_name: Image name
        sif_file: Optional SIF file path
    """
    if bind_mounts is None:
        bind_mounts = {}
    
    # Determine image to use
    image_path = sif_file if sif_file and os.path.exists(sif_file) else sandbox_dir
    image_type = "SIF" if sif_file and os.path.exists(sif_file) else "sandbox"
    
    # Common bind mounts
    default_binds = {
        work_dir: "/workspace",
        "~/.ssh": "/root/.ssh",
        "~/.gitconfig": "/root/.gitconfig",
        "/tmp": "/tmp"
    }
    default_binds.update(bind_mounts)
    
    print("\n" + "="*60)
    print(" SINGULARITY/APPTAINER DEVELOPMENT WORKSTATION")
    print("="*60)
    
    print(f"\n📍 Workspace: {work_dir}")
    print(f"📦 Sandbox: {sandbox_dir}")
    if sif_file and os.path.exists(sif_file):
        print(f"📁 SIF File: {sif_file}")
    print(f"🖥️  Image Type: {image_type}")
    print(f"🎮 GPU Support: {'Yes' if gpu_support else 'No'}")
    
    print("\n📂 Default Bind Mounts:")
    for host_path, container_path in default_binds.items():
        print(f"  {host_path} -> {container_path}")
    
    print("\n🚀 QUICK START COMMANDS:")
    print("-" * 40)
    
    # Build common bind arguments
    bind_args = []
    for host_path, container_path in default_binds.items():
        expanded_host = os.path.expanduser(host_path)
        if os.path.exists(expanded_host):
            bind_args.append(f"--bind {expanded_host}:{container_path}")
    
    bind_string = " ".join(bind_args)
    gpu_string = "--nv" if gpu_support else ""
    
    print(f"\n1. Enter interactive shell:")
    print(f"   singularity shell {gpu_string} {bind_string} {image_path}")
    
    print(f"\n2. Run a command:")
    print(f"   singularity exec {gpu_string} {bind_string} {image_path} <command>")
    print(f"   Example: singularity exec {bind_string} {image_path} python --version")
    
    print(f"\n3. Start Jupyter server:")
    print(f"   singularity exec {gpu_string} {bind_string} \\")
    print(f"       --env JUPYTER_PORT=8888 \\")
    print(f"       {image_path} \\")
    print(f"       jupyter lab --ip=0.0.0.0 --port=8888 --no-browser")
    
    print(f"\n4. Using wrapper scripts (if created):")
    print(f"   cd {work_dir}")
    print(f"   ./scripts/enter_sandbox.sh")
    print(f"   ./scripts/run_in_sandbox.sh python script.py")
    print(f"   ./scripts/start_jupyter.sh")
    
    print("\n🔧 ADVANCED USAGE:")
    print("-" * 40)
    
    print(f"\n1. Create writable overlay:")
    print(f"   singularity shell --overlay overlay.img {bind_string} {image_path}")
    
    print(f"\n2. Use fakeroot (unprivileged):")
    print(f"   singularity shell --fakeroot {bind_string} {image_path}")
    
    print(f"\n3. Set working directory:")
    print(f"   singularity shell --pwd /workspace {bind_string} {image_path}")
    
    print(f"\n4. Set environment variables:")
    print(f"   singularity shell --env MY_VAR=value {bind_string} {image_path}")
    
    print(f"\n5. Mount additional directories:")
    print(f"   singularity shell --bind /host/data:/data {bind_string} {image_path}")
    
    print("\n🔄 CONVERTING TO/FROM OTHER FORMATS:")
    print("-" * 40)
    
    print(f"\n1. Convert sandbox to SIF:")
    print(f"   singularity build {image_name}.sif {sandbox_dir}")
    
    print(f"\n2. Convert Docker to Singularity:")
    print(f"   singularity build {image_name}.sif docker://ubuntu:22.04")
    
    print(f"\n3. Convert SIF to sandbox:")
    print(f"   singularity build --sandbox {image_name}_sandbox {image_name}.sif")
    
    print("\n📊 MONITORING AND MAINTENANCE:")
    print("-" * 40)
    
    print(f"\n1. Check container info:")
    print(f"   singularity inspect {image_path}")
    
    print(f"\n2. Run container tests:")
    print(f"   singularity test {image_path}")
    
    print(f"\n3. Verify container:")
    print(f"   singularity verify {image_path}")
    
    print(f"\n4. Clean cache:")
    print(f"   singularity cache clean")
    
    print("\n🎯 HPC/CLUSTER USAGE:")
    print("-" * 40)
    
    print(f"\n1. Copy to cluster:")
    print(f"   scp {image_path} user@cluster:/path/to/containers/")
    
    print(f"\n2. SSH with X11 forwarding:")
    print(f"   ssh -X user@cluster")
    print(f"   singularity shell --bind /path/to/data {image_path}")
    
    print(f"\n3. Submit batch job (SLURM example):")
    print(f'''   #!/bin/bash
   #SBATCH --job-name=singularity_job
   #SBATCH --nodes=1
   #SBATCH --ntasks=1
   #SBATCH --cpus-per-task=4
   #SBATCH --mem=8G
   #SBATCH --time=01:00:00
   
   module load singularity
   
   singularity exec {bind_string} {image_path} \\
       python /workspace/script.py
   ''')
    
    print("\n🛡️ SECURITY NOTES:")
    print("-" * 40)
    
    print(f"\n• Containers run with user privileges (more secure than Docker)")
    print(f"• Use --fakeroot for unprivileged operations")
    print(f"• Consider using --contain for better isolation")
    print(f"• Use --scratch for temporary files")
    print(f"• Verify images with 'singularity verify' when possible")
    
    print("\n🔗 HELPFUL LINKS:")
    print("-" * 40)
    
    print(f"\n• Apptainer documentation: https://apptainer.org/docs/")
    print(f"• Singularity documentation: https://docs.sylabs.io/")
    print(f"• Singularity containers library: https://cloud.sylabs.io/library")
    print(f"• HPC best practices: https://sylabs.io/guides/latest/user-guide/hpc.html")
    
    print("\n" + "="*60)
    print(" READY TO DEVELOP WITH SINGULARITY/APPTAINER!")
    print("="*60)

def setup_ssh_forwarding(
    container_image: str,
    ssh_config: Dict[str, Any] = None,
    local_port: int = 2222,
    container_port: int = 22,
    bind_host: str = "127.0.0.1",
    key_path: str = None
) -> Dict[str, Any]:
    """
    Set up SSH forwarding to a Singularity container.
    
    Args:
        container_image: Path to Singularity image
        ssh_config: SSH configuration
        local_port: Local port for SSH
        container_port: Container SSH port
        bind_host: Bind host address
        key_path: Path to SSH key
    
    Returns:
        Dictionary with SSH forwarding setup
    """
    if ssh_config is None:
        ssh_config = {}
    
    # Default SSH configuration
    default_config = {
        "user": "root",
        "password": None,
        "key_auth": True,
        "port": container_port,
        "hostname": "localhost",
        "allow_agent": True,
        "compress": True
    }
    
    # Update with user config
    default_config.update(ssh_config)
    
    # Generate SSH key if not provided
    if key_path is None:
        key_path = os.path.expanduser("~/.ssh/id_rsa_singularity")
    
    if not os.path.exists(key_path):
        print(f"Generating SSH key at {key_path}...")
        result = subprocess.run(
            ["ssh-keygen", "-t", "rsa", "-b", "4096", "-f", key_path, "-N", ""],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Failed to generate SSH key: {result.stderr}",
                "key_path": key_path
            }
    
    # Start SSH server in container
    print(f"Starting SSH server in container...")
    
    # Check if SSH server is running in container
    check_result = run_singularity_command(
        image_path=container_image,
        command="which sshd"
    )
    
    if not check_result["success"]:
        # Install SSH server
        print("Installing OpenSSH server in container...")
        install_result = run_singularity_command(
            image_path=container_image,
            command="apt-get update && apt-get install -y openssh-server"
        )
        
        if not install_result["success"]:
            return {
                "success": False,
                "error": f"Failed to install SSH server: {install_result.get('stderr', 'Unknown error')}",
                "container_image": container_image
            }
    
    # Configure SSH server
    print("Configuring SSH server...")
    
    # Create SSH directory and configure
    config_commands = [
        "mkdir -p /run/sshd",
        "echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config",
        "echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config",
        "echo 'PubkeyAuthentication yes' >> /etc/ssh/sshd_config",
        f"mkdir -p /root/.ssh",
        f"echo 'ssh-rsa ...' > /root/.ssh/authorized_keys",  # Would add actual key
    ]
    
    for cmd in config_commands:
        run_singularity_command(
            image_path=container_image,
            command=cmd
        )
    
    # Start SSH server in background
    print(f"Starting SSH server on port {container_port}...")
    
    # We need to run the container in daemon mode with SSH
    # This is complex and would require a more sophisticated setup
    # For now, return instructions
    
    instructions = {
        "manual_setup": "SSH forwarding requires running container in background with SSHD",
        "steps": [
            f"1. Start container with SSHD: singularity instance start --bind /path/to/ssh/key {container_image} ssh_instance",
            f"2. Connect to container: ssh -p {local_port} {default_config['user']}@{bind_host}",
            f"3. Stop container: singularity instance stop ssh_instance"
        ],
        "ssh_config": default_config,
        "key_path": key_path
    }
    
    print("\n📝 SSH Forwarding Setup Instructions:")
    print("-" * 40)
    for step in instructions["steps"]:
        print(f"  {step}")
    
    return {
        "success": True,
        "instructions": instructions,
        "ssh_config": default_config,
        "key_path": key_path
    }

def setup_x11_forwarding(
    container_image: str,
    display: str = None,
    xauth_path: str = None
) -> Dict[str, Any]:
    """
    Set up X11 forwarding for GUI applications in Singularity container.
    
    Args:
        container_image: Path to Singularity image
        display: DISPLAY environment variable
        xauth_path: Path to Xauthority file
    
    Returns:
        Dictionary with X11 forwarding setup
    """
    # Get current DISPLAY
    if display is None:
        display = os.environ.get("DISPLAY", ":0")
    
    # Get Xauthority path
    if xauth_path is None:
        xauth_path = os.environ.get("XAUTHORITY", os.path.expanduser("~/.Xauthority"))
    
    # Check if X11 is available
    if not os.path.exists(xauth_path):
        return {
            "success": False,
            "error": f"Xauthority file not found: {xauth_path}",
            "display": display
        }
    
    # Prepare bind mounts for X11
    x11_binds = {
        "/tmp/.X11-unix": "/tmp/.X11-unix",
        xauth_path: "/root/.Xauthority"
    }
    
    # Test X11 forwarding
    print("Testing X11 forwarding...")
    
    test_result = run_singularity_command(
        image_path=container_image,
        command="which xeyes || echo 'X11 apps not installed'",
        bind_mounts=x11_binds,
        environment={"DISPLAY": display}
    )
    
    if test_result["success"]:
        print("✓ X11 forwarding setup complete")
        
        return {
            "success": True,
            "display": display,
            "xauth_path": xauth_path,
            "bind_mounts": x11_binds,
            "environment": {"DISPLAY": display},
            "test_command": f"singularity exec --bind /tmp/.X11-unix:/tmp/.X11-unix --bind {xauth_path}:/root/.Xauthority --env DISPLAY={display} {container_image} xeyes"
        }
    
    else:
        # X11 apps might not be installed in container
        print("⚠️ X11 apps not found in container. Installing...")
        
        install_result = run_singularity_command(
            image_path=container_image,
            command="apt-get update && apt-get install -y x11-apps"
        )
        
        if install_result["success"]:
            print("✓ X11 apps installed")
            
            return {
                "success": True,
                "display": display,
                "xauth_path": xauth_path,
                "bind_mounts": x11_binds,
                "environment": {"DISPLAY": display},
                "installed_x11": True
            }
        else:
            return {
                "success": False,
                "error": "Failed to install X11 apps",
                "display": display,
                "xauth_path": xauth_path,
                "install_stderr": install_result.get("stderr")
            }

def create_batch_job_template(
    job_name: str = "singularity_job",
    image_path: str = None,
    work_dir: str = "/workspace",
    bind_mounts: Dict[str, str] = None,
    gpu_support: bool = False,
    mpi_support: bool = False,
    slurm_config: Dict[str, Any] = None,
    pbs_config: Dict[str, Any] = None,
    lsf_config: Dict[str, Any] = None,
    output_dir: str = "."
) -> Dict[str, str]:
    """
    Create batch job templates for HPC schedulers.
    
    Args:
        job_name: Name of the job
        image_path: Path to Singularity image
        work_dir: Working directory in container
        bind_mounts: Bind mounts
        gpu_support: Enable GPU support
        mpi_support: Enable MPI support
        slurm_config: SLURM configuration
        pbs_config: PBS configuration
        lsf_config: LSF configuration
        output_dir: Output directory for templates
    
    Returns:
        Dictionary with template paths
    """
    if bind_mounts is None:
        bind_mounts = {}
    
    if slurm_config is None:
        slurm_config = {
            "nodes": 1,
            "ntasks": 1,
            "cpus_per_task": 4,
            "mem": "8G",
            "time": "01:00:00",
            "partition": "normal",
            "gpus": 1 if gpu_support else 0,
            "account": None,
            "qos": None
        }
    
    if pbs_config is None:
        pbs_config = {
            "nodes": 1,
            "ppn": 4,
            "mem": "8gb",
            "walltime": "01:00:00",
            "queue": "normal",
            "gpus": 1 if gpu_support else 0
        }
    
    if lsf_config is None:
        lsf_config = {
            "cores": 4,
            "mem": 8000,
            "time": "01:00",
            "queue": "normal",
            "gpus": 1 if gpu_support else 0
        }
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Build bind arguments string
    bind_args = []
    for host_path, container_path in bind_mounts.items():
        host_path = os.path.expanduser(host_path)
        bind_args.append(f"--bind {host_path}:{container_path}")
    
    bind_string = " ".join(bind_args)
    gpu_string = "--nv" if gpu_support else ""
    
    # SLURM template
    slurm_template = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --nodes={slurm_config['nodes']}
#SBATCH --ntasks={slurm_config['ntasks']}
#SBATCH --cpus-per-task={slurm_config['cpus_per_task']}
#SBATCH --mem={slurm_config['mem']}
#SBATCH --time={slurm_config['time']}
#SBATCH --partition={slurm_config['partition']}
"""
    
    if slurm_config['gpus'] > 0:
        slurm_template += f"#SBATCH --gpus={slurm_config['gpus']}\n"
    
    if slurm_config['account']:
        slurm_template += f"#SBATCH --account={slurm_config['account']}\n"
    
    if slurm_config['qos']:
        slurm_template += f"#SBATCH --qos={slurm_config['qos']}\n"
    
    slurm_template += f"""
#SBATCH --output={job_name}_%j.out
#SBATCH --error={job_name}_%j.err

# Load Singularity/Apptainer module
module load singularity

# Set working directory
cd {work_dir}

# Run container
singularity exec {gpu_string} {bind_string} {image_path or '$SINGULARITY_IMAGE'} \\
    python /workspace/script.py

echo "Job completed at $(date)"
"""
    
    slurm_path = os.path.join(output_dir, f"{job_name}.slurm")
    with open(slurm_path, "w") as f:
        f.write(slurm_template)
    
    # PBS template
    pbs_template = f"""#!/bin/bash
#PBS -N {job_name}
#PBS -l nodes={pbs_config['nodes']}:ppn={pbs_config['ppn']}
#PBS -l mem={pbs_config['mem']}
#PBS -l walltime={pbs_config['walltime']}
#PBS -q {pbs_config['queue']}
"""
    
    if pbs_config['gpus'] > 0:
        pbs_template += f"#PBS -l gpus={pbs_config['gpus']}\n"
    
    pbs_template += f"""
#PBS -j oe
#PBS -o {job_name}_${{PBS_JOBID}}.out

# Load Singularity/Apptainer module
module load singularity

# Set working directory
cd {work_dir}

# Run container
singularity exec {gpu_string} {bind_string} {image_path or '$SINGULARITY_IMAGE'} \\
    python /workspace/script.py

echo "Job completed at $(date)"
"""
    
    pbs_path = os.path.join(output_dir, f"{job_name}.pbs")
    with open(pbs_path, "w") as f:
        f.write(pbs_template)
    
    # LSF template
    lsf_template = f"""#!/bin/bash
#BSUB -J {job_name}
#BSUB -n {lsf_config['cores']}
#BSUB -R "rusage[mem={lsf_config['mem']}]"
#BSUB -W {lsf_config['time']}
#BSUB -q {lsf_config['queue']}
"""
    
    if lsf_config['gpus'] > 0:
        lsf_template += f"#BSUB -gpu num={lsf_config['gpus']}\n"
    
    lsf_template += f"""
#BSUB -o {job_name}_%J.out
#BSUB -e {job_name}_%J.err

# Load Singularity/Apptainer module
module load singularity

# Set working directory
cd {work_dir}

# Run container
singularity exec {gpu_string} {bind_string} {image_path or '$SINGULARITY_IMAGE'} \\
    python /workspace/script.py

echo "Job completed at $(date)"
"""
    
    lsf_path = os.path.join(output_dir, f"{job_name}.lsf")
    with open(lsf_path, "w") as f:
        f.write(lsf_template)
    
    # Make scripts executable
    for path in [slurm_path, pbs_path, lsf_path]:
        os.chmod(path, 0o755)
    
    print(f"Created batch job templates in {output_dir}:")
    print(f"  {job_name}.slurm - SLURM job script")
    print(f"  {job_name}.pbs   - PBS/Torque job script")
    print(f"  {job_name}.lsf   - LSF job script")
    
    return {
        "slurm": slurm_path,
        "pbs": pbs_path,
        "lsf": lsf_path,
        "bind_string": bind_string,
        "gpu_string": gpu_string
    }

def backup_singularity_environment(
    sandbox_dir: str,
    backup_dir: str = None,
    backup_name: str = None,
    compression: str = "gzip",
    exclude_patterns: List[str] = None,
    include_patterns: List[str] = None,
    verify: bool = True
) -> Dict[str, Any]:
    """
    Backup a Singularity sandbox or SIF file.
    
    Args:
        sandbox_dir: Path to sandbox or SIF file
        backup_dir: Directory for backups
        backup_name: Name for backup file
        compression: Compression method (gzip, bzip2, xz, none)
        exclude_patterns: Patterns to exclude
        include_patterns: Patterns to include
        verify: Verify backup after creation
    
    Returns:
        Dictionary with backup results
    """
    sandbox_dir = os.path.expanduser(sandbox_dir)
    
    if not os.path.exists(sandbox_dir):
        return {
            "success": False,
            "error": f"Sandbox/SIF not found: {sandbox_dir}",
            "sandbox_dir": sandbox_dir
        }
    
    # Set backup directory
    if backup_dir is None:
        backup_dir = os.path.join(os.path.dirname(sandbox_dir), "backups")
    
    backup_dir = os.path.expanduser(backup_dir)
    os.makedirs(backup_dir, exist_ok=True)
    
    # Set backup name
    if backup_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(sandbox_dir.rstrip('/'))
        backup_name = f"{base_name}_backup_{timestamp}"
    
    # Determine if it's a directory (sandbox) or file (SIF)
    is_dir = os.path.isdir(sandbox_dir)
    
    # Create backup
    backup_path = os.path.join(backup_dir, backup_name)
    
    print(f"Creating backup of {sandbox_dir}...")
    print(f"Backup destination: {backup_path}")
    print(f"Type: {'Directory' if is_dir else 'File'}")
    print(f"Compression: {compression}")
    
    try:
        if is_dir:
            # Backup directory (sandbox)
            if compression == "gzip":
                backup_path += ".tar.gz"
                with tarfile.open(backup_path, "w:gz") as tar:
                    tar.add(sandbox_dir, arcname=os.path.basename(sandbox_dir))
            
            elif compression == "bzip2":
                backup_path += ".tar.bz2"
                with tarfile.open(backup_path, "w:bz2") as tar:
                    tar.add(sandbox_dir, arcname=os.path.basename(sandbox_dir))
            
            elif compression == "xz":
                backup_path += ".tar.xz"
                with tarfile.open(backup_path, "w:xz") as tar:
                    tar.add(sandbox_dir, arcname=os.path.basename(sandbox_dir))
            
            else:  # none
                backup_path += ".tar"
                with tarfile.open(backup_path, "w") as tar:
                    tar.add(sandbox_dir, arcname=os.path.basename(sandbox_dir))
        
        else:
            # Backup file (SIF)
            if compression == "gzip":
                backup_path += ".sif.gz"
                with open(sandbox_dir, "rb") as f_in:
                    with gzip.open(backup_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            elif compression == "bzip2":
                backup_path += ".sif.bz2"
                import bz2
                with open(sandbox_dir, "rb") as f_in:
                    with bz2.open(backup_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            else:  # none or other
                backup_path += ".sif"
                shutil.copy2(sandbox_dir, backup_path)
        
        # Get backup size
        backup_size = os.path.getsize(backup_path)
        backup_size_mb = backup_size / (1024 * 1024)
        
        print(f"✓ Backup created: {backup_path}")
        print(f"  Size: {backup_size_mb:.2f} MB")
        
        # Verify backup
        if verify:
            print("Verifying backup...")
            if is_dir:
                # Verify tar archive
                try:
                    with tarfile.open(backup_path, "r") as tar:
                        tar.getmembers()  # Just try to read
                    print("✓ Backup verified (tar archive is readable)")
                    verified = True
                except Exception as e:
                    print(f"✗ Backup verification failed: {e}")
                    verified = False
            else:
                # Verify file copy
                if os.path.getsize(backup_path) == os.path.getsize(sandbox_dir):
                    print("✓ Backup verified (file sizes match)")
                    verified = True
                else:
                    print(f"✗ Backup verification failed (size mismatch)")
                    verified = False
            
            if not verified:
                os.remove(backup_path)
                return {
                    "success": False,
                    "error": "Backup verification failed",
                    "backup_path": backup_path,
                    "sandbox_dir": sandbox_dir
                }
        
        # Create checksum
        print("Creating checksum...")
        with open(backup_path, "rb") as f:
            file_hash = hashlib.sha256()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
        
        checksum = file_hash.hexdigest()
        
        # Save checksum to file
        checksum_path = backup_path + ".sha256"
        with open(checksum_path, "w") as f:
            f.write(f"{checksum}  {os.path.basename(backup_path)}\n")
        
        print(f"✓ Checksum saved: {checksum_path}")
        print(f"  SHA256: {checksum}")
        
        return {
            "success": True,
            "backup_path": backup_path,
            "checksum_path": checksum_path,
            "checksum": checksum,
            "size_bytes": backup_size,
            "size_mb": backup_size_mb,
            "sandbox_dir": sandbox_dir,
            "compression": compression,
            "verified": verified if verify else None
        }
    
    except Exception as e:
        error_msg = f"Failed to create backup: {str(e)}"
        print(f"✗ {error_msg}")
        
        # Clean up failed backup
        if os.path.exists(backup_path):
            os.remove(backup_path)
        
        return {
            "success": False,
            "error": error_msg,
            "backup_path": backup_path,
            "sandbox_dir": sandbox_dir
        }

def restore_singularity_environment(
    backup_path: str,
    restore_dir: str = None,
    restore_name: str = None,
    overwrite: bool = False,
    verify_checksum: bool = True
) -> Dict[str, Any]:
    """
    Restore a Singularity environment from backup.
    
    Args:
        backup_path: Path to backup file
        restore_dir: Directory to restore to
        restore_name: Name for restored environment
        overwrite: Overwrite existing environment
        verify_checksum: Verify backup checksum before restore
    
    Returns:
        Dictionary with restore results
    """
    backup_path = os.path.expanduser(backup_path)
    
    if not os.path.exists(backup_path):
        return {
            "success": False,
            "error": f"Backup file not found: {backup_path}",
            "backup_path": backup_path
        }
    
    # Determine restore directory
    if restore_dir is None:
        restore_dir = os.path.dirname(backup_path)
    
    restore_dir = os.path.expanduser(restore_dir)
    
    # Determine restore name
    if restore_name is None:
        # Extract from backup filename
        base_name = os.path.basename(backup_path)
        # Remove backup suffix and extensions
        restore_name = base_name.replace("_backup_", "_").split(".")[0]
    
    restore_path = os.path.join(restore_dir, restore_name)
    
    print(f"Restoring from backup: {backup_path}")
    print(f"Restore destination: {restore_path}")
    
    # Check if restore path already exists
    if os.path.exists(restore_path) and not overwrite:
        return {
            "success": False,
            "error": f"Restore path already exists: {restore_path}",
            "backup_path": backup_path,
            "restore_path": restore_path,
            "suggestion": "Use overwrite=True to overwrite"
        }
    
    # Verify checksum if requested
    if verify_checksum:
        checksum_path = backup_path + ".sha256"
        if os.path.exists(checksum_path):
            print("Verifying backup checksum...")
            
            with open(checksum_path, "r") as f:
                expected_checksum = f.read().split()[0]
            
            with open(backup_path, "rb") as f:
                file_hash = hashlib.sha256()
                chunk = f.read(8192)
                while chunk:
                    file_hash.update(chunk)
                    chunk = f.read(8192)
            
            actual_checksum = file_hash.hexdigest()
            
            if expected_checksum == actual_checksum:
                print(f"✓ Checksum verified")
            else:
                print(f"✗ Checksum mismatch!")
                print(f"  Expected: {expected_checksum}")
                print(f"  Actual:   {actual_checksum}")
                return {
                    "success": False,
                    "error": "Checksum verification failed",
                    "backup_path": backup_path,
                    "expected_checksum": expected_checksum,
                    "actual_checksum": actual_checksum
                }
        else:
            print(f"⚠️ Checksum file not found: {checksum_path}")
    
    try:
        # Remove existing if overwriting
        if os.path.exists(restore_path):
            if os.path.isdir(restore_path):
                shutil.rmtree(restore_path)
            else:
                os.remove(restore_path)
        
        # Determine backup type and restore
        if backup_path.endswith((".tar.gz", ".tar.bz2", ".tar.xz", ".tar")):
            # Directory backup (sandbox)
            print("Restoring directory (sandbox)...")
            
            # Extract archive
            with tarfile.open(backup_path, "r:*") as tar:
                tar.extractall(path=restore_dir)
            
            # Find extracted directory
            extracted_members = tar.getnames()
            if extracted_members:
                # The first member should be the directory
                extracted_dir = extracted_members[0].split('/')[0]
                actual_restore_path = os.path.join(restore_dir, extracted_dir)
                
                # Rename if needed
                if actual_restore_path != restore_path:
                    os.rename(actual_restore_path, restore_path)
        
        elif backup_path.endswith((".sif.gz", ".sif.bz2")):
            # Compressed SIF file
            print("Restoring compressed SIF file...")
            
            if backup_path.endswith(".sif.gz"):
                with gzip.open(backup_path, "rb") as f_in:
                    with open(restore_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            elif backup_path.endswith(".sif.bz2"):
                import bz2
                with bz2.open(backup_path, "rb") as f_in:
                    with open(restore_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
        
        elif backup_path.endswith(".sif"):
            # Plain SIF file
            print("Restoring SIF file...")
            shutil.copy2(backup_path, restore_path)
        
        else:
            return {
                "success": False,
                "error": f"Unsupported backup format: {backup_path}",
                "backup_path": backup_path
            }
        
        # Verify restore
        if os.path.exists(restore_path):
            restore_size = os.path.getsize(restore_path) if os.path.isfile(restore_path) else None
            restore_size_mb = restore_size / (1024 * 1024) if restore_size else None
            
            print(f"✓ Restore successful: {restore_path}")
            if restore_size_mb:
                print(f"  Size: {restore_size_mb:.2f} MB")
            
            return {
                "success": True,
                "restore_path": restore_path,
                "backup_path": backup_path,
                "size_bytes": restore_size,
                "size_mb": restore_size_mb
            }
        else:
            return {
                "success": False,
                "error": "Restore failed - destination not created",
                "backup_path": backup_path,
                "restore_path": restore_path
            }
    
    except Exception as e:
        error_msg = f"Failed to restore: {str(e)}"
        print(f"✗ {error_msg}")
        
        # Clean up failed restore
        if os.path.exists(restore_path):
            if os.path.isdir(restore_path):
                shutil.rmtree(restore_path)
            else:
                os.remove(restore_path)
        
        return {
            "success": False,
            "error": error_msg,
            "backup_path": backup_path,
            "restore_path": restore_path
        }

def migrate_singularity_environment(
    source_path: str,
    destination_host: str,
    destination_path: str = None,
    ssh_user: str = None,
    ssh_key: str = None,
    compress: bool = True,
    exclude_patterns: List[str] = None,
    resume: bool = False
) -> Dict[str, Any]:
    """
    Migrate a Singularity environment to another host.
    
    Args:
        source_path: Path to sandbox or SIF on source
        destination_host: Destination host (user@hostname)
        destination_path: Path on destination host
        ssh_user: SSH username (if not in destination_host)
        ssh_key: Path to SSH key
        compress: Compress during transfer
        exclude_patterns: Patterns to exclude
        resume: Resume interrupted transfer
    
    Returns:
        Dictionary with migration results
    """
    source_path = os.path.expanduser(source_path)
    
    if not os.path.exists(source_path):
        return {
            "success": False,
            "error": f"Source not found: {source_path}",
            "source_path": source_path
        }
    
    # Parse destination host
    if "@" in destination_host:
        ssh_user, hostname = destination_host.split("@", 1)
    else:
        hostname = destination_host
        ssh_user = ssh_user or getpass.getuser()
    
    # Set destination path
    if destination_path is None:
        destination_path = f"/home/{ssh_user}/singularity_envs/{os.path.basename(source_path)}"
    
    print(f"Migrating Singularity environment to {destination_host}...")
    print(f"Source: {source_path}")
    print(f"Destination: {ssh_user}@{hostname}:{destination_path}")
    print(f"Compress: {compress}")
    print(f"Resume: {resume}")
    
    # Build rsync command
    rsync_cmd = ["rsync", "-avz", "--progress"]
    
    if resume:
        rsync_cmd.append("--partial")
        rsync_cmd.append("--append")
    
    if compress:
        rsync_cmd.append("--compress")
    
    # Add exclude patterns
    if exclude_patterns:
        for pattern in exclude_patterns:
            rsync_cmd.extend(["--exclude", pattern])
    
    # Add SSH options
    ssh_options = []
    if ssh_key:
        ssh_options.extend(["-i", ssh_key])
    
    if ssh_options:
        rsync_cmd.extend(["-e", f"ssh {' '.join(ssh_options)}"])
    
    # Add source and destination
    rsync_cmd.append(source_path)
    rsync_cmd.append(f"{ssh_user}@{hostname}:{destination_path}")
    
    print(f"\nCommand: {' '.join(rsync_cmd)}")
    print("-" * 60)
    
    try:
        # Execute rsync
        result = subprocess.run(
            rsync_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"\n✓ Migration successful")
        print(f"Destination: {ssh_user}@{hostname}:{destination_path}")
        
        # Test that destination is accessible
        print("\nTesting destination...")
        test_cmd = ["ssh"]
        if ssh_key:
            test_cmd.extend(["-i", ssh_key])
        test_cmd.extend([f"{ssh_user}@{hostname}", f"ls -la {destination_path}"])
        
        test_result = subprocess.run(
            test_cmd,
            capture_output=True,
            text=True
        )
        
        if test_result.returncode == 0:
            print(f"✓ Destination verified")
        else:
            print(f"⚠️ Could not verify destination: {test_result.stderr}")
        
        return {
            "success": True,
            "source_path": source_path,
            "destination": f"{ssh_user}@{hostname}:{destination_path}",
            "destination_host": hostname,
            "destination_path": destination_path,
            "ssh_user": ssh_user,
            "output": result.stdout,
            "stderr": result.stderr
        }
    
    except subprocess.CalledProcessError as e:
        error_msg = f"Migration failed: {e.stderr}"
        print(f"\n✗ {error_msg}")
        
        return {
            "success": False,
            "error": error_msg,
            "source_path": source_path,
            "destination": f"{ssh_user}@{hostname}:{destination_path}",
            "stderr": e.stderr,
            "stdout": e.stdout,
            "returncode": e.returncode
        }
    
    except Exception as e:
        error_msg = f"Unexpected error during migration: {str(e)}"
        print(f"\n✗ {error_msg}")
        
        return {
            "success": False,
            "error": error_msg,
            "source_path": source_path,
            "destination": f"{ssh_user}@{hostname}:{destination_path}"
        }

def scan_singularity_image(
    image_path: str,
    scan_type: str = "security",
    output_format: str = "text",
    output_file: str = None,
    check_vulnerabilities: bool = True,
    check_malware: bool = False,
    check_secrets: bool = True,
    check_config: bool = True
) -> Dict[str, Any]:
    """
    Scan a Singularity image for security issues and vulnerabilities.
    
    Args:
        image_path: Path to Singularity image
        scan_type: Type of scan (security, vulnerabilities, all)
        output_format: Output format (text, json, html)
        output_file: Output file path
        check_vulnerabilities: Check for known vulnerabilities
        check_malware: Check for malware (requires external tools)
        check_secrets: Check for exposed secrets
        check_config: Check configuration issues
    
    Returns:
        Dictionary with scan results
    """
    image_path = os.path.expanduser(image_path)
    
    if not os.path.exists(image_path):
        return {
            "success": False,
            "error": f"Image not found: {image_path}",
            "image_path": image_path
        }
    
    print(f"Scanning Singularity image: {image_path}")
    print(f"Scan type: {scan_type}")
    print(f"Output format: {output_format}")
    
    results = {
        "image_path": image_path,
        "scan_type": scan_type,
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "issues": [],
        "warnings": [],
        "recommendations": []
    }
    
    # Check 1: Basic image information
    print("\n1. Basic image information...")
    try:
        inspect_result = subprocess.run(
            ["singularity", "inspect", image_path],
            capture_output=True,
            text=True
        )
        
        if inspect_result.returncode == 0:
            results["checks"]["inspect"] = "success"
            results["image_info"] = inspect_result.stdout
        else:
            results["checks"]["inspect"] = "failed"
            results["warnings"].append("Could not inspect image")
    except:
        results["checks"]["inspect"] = "failed"
    
    # Check 2: File permissions and ownership
    print("2. Checking file permissions...")
    try:
        # Run a simple check inside container
        perm_check = run_singularity_command(
            image_path=image_path,
            command="find / -type f -perm /o+w -ls 2>/dev/null | head -20"
        )
        
        if perm_check["success"] and perm_check["stdout"].strip():
            results["issues"].append({
                "type": "permissions",
                "severity": "medium",
                "description": "World-writable files found",
                "details": perm_check["stdout"].strip().split('\n')
            })
        
        results["checks"]["permissions"] = "completed"
    except:
        results["checks"]["permissions"] = "failed"
    
    # Check 3: Exposed secrets (placeholder - would use trufflehog or similar)
    if check_secrets:
        print("3. Checking for exposed secrets...")
        # This would require external tools like trufflehog, gitleaks, etc.
        results["checks"]["secrets"] = "skipped (requires external tools)"
        results["recommendations"].append("Install and run trufflehog for secret scanning")
    
    # Check 4: Known vulnerabilities (placeholder)
    if check_vulnerabilities:
        print("4. Checking for known vulnerabilities...")
        # This would require external tools like grype, trivy, etc.
        results["checks"]["vulnerabilities"] = "skipped (requires external tools)"
        results["recommendations"].append("Install and run grype or trivy for vulnerability scanning")
    
    # Check 5: Configuration issues
    if check_config:
        print("5. Checking configuration...")
        try:
            # Check environment variables
            env_check = run_singularity_command(
                image_path=image_path,
                command="env | grep -i 'pass\|key\|secret\|token' | head -10"
            )
            
            if env_check["success"] and env_check["stdout"].strip():
                results["issues"].append({
                    "type": "environment",
                    "severity": "high",
                    "description": "Potential secrets in environment variables",
                    "details": env_check["stdout"].strip().split('\n')
                })
            
            results["checks"]["configuration"] = "completed"
        except:
            results["checks"]["configuration"] = "failed"
    
    # Summary
    total_issues = len(results["issues"])
    total_warnings = len(results["warnings"])
    
    print(f"\nScan completed: {total_issues} issues, {total_warnings} warnings")
    
    # Generate output
    if output_file:
        print(f"Writing output to: {output_file}")
        
        if output_format == "json":
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)
        elif output_format == "html":
            # Generate HTML report
            html_content = generate_html_report(results)
            with open(output_file, "w") as f:
                f.write(html_content)
        else:  # text
            with open(output_file, "w") as f:
                f.write(generate_text_report(results))
    
    return results

def generate_html_report(results: Dict[str, Any]) -> str:
    """Generate HTML report from scan results."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Singularity Image Scan Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .issue {{ background: #ffe6e6; padding: 10px; margin: 10px 0; border-left: 4px solid #ff4444; }}
        .warning {{ background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }}
        .recommendation {{ background: #d4edda; padding: 10px; margin: 10px 0; border-left: 4px solid #28a745; }}
        .check {{ background: #e9ecef; padding: 5px; margin: 5px 0; }}
        .success {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .severity-high {{ color: #dc3545; font-weight: bold; }}
        .severity-medium {{ color: #ffc107; font-weight: bold; }}
        .severity-low {{ color: #17a2b8; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Singularity Image Scan Report</h1>
        <p><strong>Image:</strong> {results.get('image_path', 'Unknown')}</p>
        <p><strong>Scan Type:</strong> {results.get('scan_type', 'Unknown')}</p>
        <p><strong>Timestamp:</strong> {results.get('timestamp', 'Unknown')}</p>
    </div>
    
    <div class="section">
        <h2>Summary</h2>
        <p>Issues: {len(results.get('issues', []))}</p>
        <p>Warnings: {len(results.get('warnings', []))}</p>
        <p>Recommendations: {len(results.get('recommendations', []))}</p>
    </div>
"""
    
    # Issues
    if results.get('issues'):
        html += """
    <div class="section">
        <h2>Issues Found</h2>
"""
        for issue in results['issues']:
            html += f"""
        <div class="issue">
            <h3 class="severity-{issue.get('severity', 'medium')}">{issue.get('type', 'Unknown')} - {issue.get('severity', 'medium').upper()}</h3>
            <p>{issue.get('description', 'No description')}</p>
"""
            if issue.get('details'):
                html += "<ul>"
                for detail in issue['details']:
                    html += f"<li>{detail}</li>"
                html += "</ul>"
            html += "</div>"
        html += "</div>"
    
    # Warnings
    if results.get('warnings'):
        html += """
    <div class="section">
        <h2>Warnings</h2>
"""
        for warning in results['warnings']:
            html += f'<div class="warning">{warning}</div>'
        html += "</div>"
    
    # Recommendations
    if results.get('recommendations'):
        html += """
    <div class="section">
        <h2>Recommendations</h2>
"""
        for recommendation in results['recommendations']:
            html += f'<div class="recommendation">{recommendation}</div>'
        html += "</div>"
    
    # Checks performed
    if results.get('checks'):
        html += """
    <div class="section">
        <h2>Checks Performed</h2>
"""
        for check, status in results['checks'].items():
            status_class = "success" if status == "success" or status == "completed" else "failed"
            html += f'<div class="check"><span class="{status_class}">●</span> {check}: {status}</div>'
        html += "</div>"
    
    html += """
</body>
</html>
"""
    
    return html

def generate_text_report(results: Dict[str, Any]) -> str:
    """Generate text report from scan results."""
    text = f"""Singularity Image Scan Report
{'=' * 50}

Image: {results.get('image_path', 'Unknown')}
Scan Type: {results.get('scan_type', 'Unknown')}
Timestamp: {results.get('timestamp', 'Unknown')}

SUMMARY
{'=' * 50}
Issues: {len(results.get('issues', []))}
Warnings: {len(results.get('warnings', []))}
Recommendations: {len(results.get('recommendations', []))}

"""
    
    # Issues
    if results.get('issues'):
        text += "ISSUES FOUND\n"
        text += "=" * 50 + "\n"
        for i, issue in enumerate(results['issues'], 1):
            text += f"\n{i}. [{issue.get('severity', 'medium').upper()}] {issue.get('type', 'Unknown')}\n"
            text += f"   {issue.get('description', 'No description')}\n"
            if issue.get('details'):
                for detail in issue['details']:
                    text += f"   - {detail}\n"
    
    # Warnings
    if results.get('warnings'):
        text += "\nWARNINGS\n"
        text += "=" * 50 + "\n"
        for i, warning in enumerate(results['warnings'], 1):
            text += f"{i}. {warning}\n"
    
    # Recommendations
    if results.get('recommendations'):
        text += "\nRECOMMENDATIONS\n"
        text += "=" * 50 + "\n"
        for i, recommendation in enumerate(results['recommendations'], 1):
            text += f"{i}. {recommendation}\n"
    
    # Checks performed
    if results.get('checks'):
        text += "\nCHECKS PERFORMED\n"
        text += "=" * 50 + "\n"
        for check, status in results['checks'].items():
            status_symbol = "✓" if status == "success" or status == "completed" else "✗"
            text += f"{status_symbol} {check}: {status}\n"
    
    return text

def load_apptainer_config(config_file: str) -> Dict[str, Any]:
    """
    Load Apptainer/Singularity configuration from file.
    
    Args:
        config_file: Path to configuration file
    
    Returns:
        Dictionary with configuration
    """
    config_file = os.path.expanduser(config_file)
    
    if not os.path.exists(config_file):
        print(f"Warning: Config file not found: {config_file}")
        return {}
    
    try:
        with open(config_file, "r") as f:
            if config_file.endswith(".json"):
                return json.load(f)
            elif config_file.endswith((".yaml", ".yml")) and YAML_AVAILABLE:
                return yaml.safe_load(f)
            else:
                print(f"Warning: Unsupported config format: {config_file}")
                return {}
    except Exception as e:
        print(f"Warning: Could not load config file {config_file}: {e}")
        return {}

def save_apptainer_config(
    config: Dict[str, Any],
    config_file: str,
    format: str = "json"
) -> bool:
    """
    Save Apptainer/Singularity configuration to file.
    
    Args:
        config: Configuration dictionary
        config_file: Path to configuration file
        format: File format (json, yaml)
    
    Returns:
        True if successful, False otherwise
    """
    config_file = os.path.expanduser(config_file)
    
    try:
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        with open(config_file, "w") as f:
            if format == "json":
                json.dump(config, f, indent=2)
            elif format == "yaml" and YAML_AVAILABLE:
                yaml.dump(config, f, default_flow_style=False)
            else:
                print(f"Warning: Unsupported format {format}, using JSON")
                json.dump(config, f, indent=2)
        
        print(f"✓ Configuration saved to {config_file}")
        return True
    
    except Exception as e:
        print(f"✗ Failed to save configuration: {e}")
        return False

def list_singularity_images(
    directory: str = None,
    recursive: bool = False,
    show_details: bool = False,
    filter_type: str = None
) -> List[Dict[str, Any]]:
    """
    List Singularity images in a directory.
    
    Args:
        directory: Directory to search
        recursive: Search recursively
        show_details: Show detailed information
        filter_type: Filter by type (sif, sandbox, all)
    
    Returns:
        List of image information dictionaries
    """
    if directory is None:
        directory = os.getcwd()
    
    directory = os.path.expanduser(directory)
    
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return []
    
    images = []
    
    # Define what to look for
    if filter_type == "sif":
        patterns = ["*.sif"]
    elif filter_type == "sandbox":
        # Sandboxes are directories, not files with extensions
        pass
    else:
        patterns = ["*.sif", "*.simg"]
    
    # Find SIF files
    for pattern in patterns:
        if recursive:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(pattern.replace("*", "")):
                        filepath = os.path.join(root, file)
                        images.append({
                            "path": filepath,
                            "type": "sif",
                            "size": os.path.getsize(filepath),
                            "modified": os.path.getmtime(filepath)
                        })
        else:
            for file in os.listdir(directory):
                if file.endswith(pattern.replace("*", "")):
                    filepath = os.path.join(directory, file)
                    images.append({
                        "path": filepath,
                        "type": "sif",
                        "size": os.path.getsize(filepath),
                        "modified": os.path.getmtime(filepath)
                    })
    
    # Find sandboxes (directories that might be sandboxes)
    # This is heuristic - we look for directories with common sandbox structure
    if filter_type in [None, "sandbox", "all"]:
        if recursive:
            for root, dirs, files in os.walk(directory):
                for dir_name in dirs:
                    dirpath = os.path.join(root, dir_name)
                    # Check if it might be a sandbox
                    if os.path.exists(os.path.join(dirpath, ".singularity.d")) or \
                       os.path.exists(os.path.join(dirpath, "bin")) and \
                       os.path.exists(os.path.join(dirpath, "etc")):
                        images.append({
                            "path": dirpath,
                            "type": "sandbox",
                            "size": get_directory_size(dirpath),
                            "modified": os.path.getmtime(dirpath)
                        })
        else:
            for item in os.listdir(directory):
                itempath = os.path.join(directory, item)
                if os.path.isdir(itempath):
                    # Check if it might be a sandbox
                    if os.path.exists(os.path.join(itempath, ".singularity.d")) or \
                       os.path.exists(os.path.join(itempath, "bin")) and \
                       os.path.exists(os.path.join(itempath, "etc")):
                        images.append({
                            "path": itempath,
                            "type": "sandbox",
                            "size": get_directory_size(itempath),
                            "modified": os.path.getmtime(itempath)
                        })
    
    # Add details if requested
    if show_details:
        for img in images:
            try:
                inspect_result = subprocess.run(
                    ["singularity", "inspect", img["path"]],
                    capture_output=True,
                    text=True
                )
                if inspect_result.returncode == 0:
                    img["details"] = inspect_result.stdout
            except:
                img["details"] = "Could not inspect"
    
    return images

def get_directory_size(path: str) -> int:
    """
    Get total size of a directory.
    
    Args:
        path: Directory path
    
    Returns:
        Size in bytes
    """
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # Skip if it is a symlink
            if not os.path.islink(fp):
                try:
                    total += os.path.getsize(fp)
                except:
                    pass
    return total

def clean_singularity_cache(
    cache_type: str = "all",
    force: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Clean Singularity/Apptainer cache.
    
    Args:
        cache_type: Type of cache to clean (all, library, oci, blob, shub, net)
        force: Force cleanup without confirmation
        dry_run: Show what would be removed without actually removing
    
    Returns:
        Dictionary with cleanup results
    """
    apptainer_info = check_apptainer_availability()
    if not apptainer_info["available"]:
        return {
            "success": False,
            "error": "Apptainer/Singularity not available",
            "message": apptainer_info["message"]
        }
    
    cmd = apptainer_info["command"]
    
    # Build command
    cache_cmd = [cmd, "cache", "clean"]
    
    if cache_type != "all":
        cache_cmd.append(cache_type)
    
    if force:
        cache_cmd.append("--force")
    
    if dry_run:
        print("DRY RUN - Showing what would be cleaned:")
        # We can't actually do a dry run with singularity cache clean
        # So we'll list the cache contents instead
        list_cmd = [cmd, "cache", "list"]
        result = subprocess.run(list_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
            return {
                "success": True,
                "dry_run": True,
                "output": result.stdout,
                "cache_type": cache_type
            }
        else:
            return {
                "success": False,
                "dry_run": True,
                "error": f"Failed to list cache: {result.stderr}",
                "cache_type": cache_type
            }
    
    print(f"Cleaning {cache_type} cache...")
    
    try:
        result = subprocess.run(
            cache_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✓ Cache cleaned")
        if result.stdout:
            print(result.stdout)
        
        return {
            "success": True,
            "cache_type": cache_type,
            "output": result.stdout,
            "stderr": result.stderr
        }
    
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to clean cache: {e.stderr}"
        print(f"✗ {error_msg}")
        
        return {
            "success": False,
            "error": error_msg,
            "cache_type": cache_type,
            "stderr": e.stderr,
            "stdout": e.stdout,
            "returncode": e.returncode
        }

def create_singularity_overlay(
    size_mb: int = 1024,
    overlay_file: str = "overlay.img",
    filesystem: str = "ext3",
    sparse: bool = True
) -> Dict[str, Any]:
    """
    Create a writable overlay filesystem for Singularity.
    
    Args:
        size_mb: Size of overlay in MB
        overlay_file: Path to overlay file
        filesystem: Filesystem type (ext3, ext4, xfs)
        sparse: Create sparse file (allocate on demand)
    
    Returns:
        Dictionary with overlay creation results
    """
    overlay_file = os.path.expanduser(overlay_file)
    
    if os.path.exists(overlay_file):
        return {
            "success": False,
            "error": f"Overlay file already exists: {overlay_file}",
            "overlay_file": overlay_file,
            "suggestion": "Remove existing file or choose different name"
        }
    
    print(f"Creating overlay filesystem: {overlay_file}")
    print(f"Size: {size_mb} MB")
    print(f"Filesystem: {filesystem}")
    print(f"Sparse: {sparse}")
    
    try:
        # Create empty file
        if sparse:
            # Create sparse file
            with open(overlay_file, "wb") as f:
                f.seek(size_mb * 1024 * 1024 - 1)
                f.write(b'\0')
        else:
            # Create pre-allocated file
            with open(overlay_file, "wb") as f:
                f.write(b'\0' * size_mb * 1024 * 1024)
        
        # Format filesystem
        format_cmd = ["mkfs", "-t", filesystem, overlay_file]
        result = subprocess.run(
            format_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✓ Overlay created: {overlay_file}")
        print(f"  Size: {size_mb} MB")
        print(f"  Filesystem: {filesystem}")
        
        return {
            "success": True,
            "overlay_file": overlay_file,
            "size_mb": size_mb,
            "filesystem": filesystem,
            "sparse": sparse,
            "output": result.stdout
        }
    
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to create overlay: {e.stderr}"
        print(f"✗ {error_msg}")
        
        # Clean up failed file
        if os.path.exists(overlay_file):
            os.remove(overlay_file)
        
        return {
            "success": False,
            "error": error_msg,
            "overlay_file": overlay_file,
            "stderr": e.stderr
        }
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"✗ {error_msg}")
        
        # Clean up failed file
        if os.path.exists(overlay_file):
            os.remove(overlay_file)
        
        return {
            "success": False,
            "error": error_msg,
            "overlay_file": overlay_file
        }

def test_singularity_environment(
    image_path: str,
    test_commands: List[str] = None,
    bind_mounts: Dict[str, str] = None,
    working_dir: str = "/workspace",
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Test a Singularity environment with various commands.
    
    Args:
        image_path: Path to Singularity image
        test_commands: Commands to test
        bind_mounts: Bind mounts for testing
        working_dir: Working directory for tests
        timeout: Timeout for each command in seconds
    
    Returns:
        Dictionary with test results
    """
    if test_commands is None:
        test_commands = [
            "python3 --version",
            "pip3 --version",
            "git --version",
            "gcc --version",
            "make --version",
            "curl --version",
            "which bash",
            "ls -la /"
        ]
    
    if bind_mounts is None:
        bind_mounts = {}
    
    image_path = os.path.expanduser(image_path)
    
    if not os.path.exists(image_path):
        return {
            "success": False,
            "error": f"Image not found: {image_path}",
            "image_path": image_path
        }
    
    print(f"Testing Singularity environment: {image_path}")
    print(f"Number of tests: {len(test_commands)}")
    print(f"Timeout: {timeout} seconds per test")
    
    results = {
        "image_path": image_path,
        "tests": [],
        "passed": 0,
        "failed": 0,
        "total": len(test_commands)
    }
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\nTest {i}/{len(test_commands)}: {cmd}")
        
        try:
            test_result = run_singularity_command(
                image_path=image_path,
                command=cmd,
                bind_mounts=bind_mounts,
                working_dir=working_dir
            )
            
            test_info = {
                "command": cmd,
                "success": test_result["success"],
                "returncode": test_result.get("returncode"),
                "stdout": test_result.get("stdout", "").strip(),
                "stderr": test_result.get("stderr", "").strip()
            }
            
            if test_result["success"]:
                print(f"  ✓ Passed")
                results["passed"] += 1
            else:
                print(f"  ✗ Failed (return code: {test_result.get('returncode')})")
                if test_result.get("stderr"):
                    print(f"    Error: {test_result['stderr'][:100]}...")
                results["failed"] += 1
            
            results["tests"].append(test_info)
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            results["tests"].append({
                "command": cmd,
                "success": False,
                "error": str(e)
            })
            results["failed"] += 1
    
    # Summary
    print(f"\n{'=' * 50}")
    print(f"TEST SUMMARY")
    print(f"{'=' * 50}")
    print(f"Total tests: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success rate: {(results['passed'] / results['total'] * 100):.1f}%")
    
    results["success_rate"] = results["passed"] / results["total"] * 100
    results["overall_success"] = results["failed"] == 0
    
    if results["overall_success"]:
        print(f"\n✓ All tests passed!")
    else:
        print(f"\n⚠️ Some tests failed")
    
    return results

def generate_singularity_usage_guide(
    image_path: str,
    output_file: str = None,
    format: str = "text"
) -> str:
    """
    Generate a usage guide for a Singularity image.
    
    Args:
        image_path: Path to Singularity image
        output_file: Output file path
        format: Output format (text, markdown, html)
    
    Returns:
        Usage guide content
    """
    image_path = os.path.expanduser(image_path)
    
    if not os.path.exists(image_path):
        return f"Error: Image not found: {image_path}"
    
    # Get image information
    try:
        inspect_result = subprocess.run(
            ["singularity", "inspect", image_path],
            capture_output=True,
            text=True
        )
        
        if inspect_result.returncode != 0:
            image_info = "Could not inspect image"
        else:
            image_info = inspect_result.stdout
    except:
        image_info = "Could not inspect image"
    
    # Determine image type
    is_sandbox = os.path.isdir(image_path)
    image_type = "sandbox" if is_sandbox else "SIF"
    image_name = os.path.basename(image_path)
    
    # Generate guide
    if format == "markdown":
        guide = f"""# Singularity Image Usage Guide

## Image Information
- **Name**: {image_name}
- **Type**: {image_type}
- **Path**: {image_path}
- **Size**: {os.path.getsize(image_path) / (1024*1024):.1f} MB

## Basic Commands

### 1. Interactive Shell
```bash
singularity shell {image_path}
### 2. Run a Command
singularity exec {image_path} <command>
#### Example:
singularity exec {image_path} python --version
### 3. With Bind Mounts
singularity shell --bind /host/path:/container/path {image_path}
### 4. With GPU Support (NVIDIA)
singularity shell --nv {image_path}
####Advanced Usage
##### Environment Variables
singularity exec --env MY_VAR=value {image_path} env
##### Working Directory
singularity exec --pwd /workspace {image_path} pwd
#### Fakeroot (Unprivileged)
#### HPC/Cluster Usage 
#### Copy to Cluster
scp {image_path} user@cluster:/path/to/containers/
#### SLURM Job Script
#!/bin/bash
#SBATCH --job-name=singularity_job
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G

module load singularity

singularity exec {image_path} python /workspace/script.py
#### Image Information
{image_info}
#### Notes
1. Use `singularity inspect {image_path}` for detailed information
2. Use `singularity run {image_path}` if the image has a runscript
3. Use `singularity test {image_path}` to run container tests
#### Help
Singularity documentation: https://docs.sylabs.io/
Apptainer documentation: https://apptainer.org/docs/
"""
    else:  # text format
        guide = f"""Singularity Image Usage Guide
        {'=' * 60}

IMAGE INFORMATION
{'=' * 60}
Name: {image_name}
Type: {image_type}
Path: {image_path}
Size: {os.path.getsize(image_path) / (1024*1024):.1f} MB

BASIC COMMANDS
{'=' * 60}

Interactive Shell
singularity shell {image_path}
Run a Command
singularity exec {image_path} <command>
Example: singularity exec {image_path} python --version
With Bind Mounts
singularity shell --bind /host/path:/container/path {image_path}
With GPU Support (NVIDIA)
singularity shell --nv {image_path}
ADVANCED USAGE
{'=' * 60}

Environment Variables
singularity exec --env MY_VAR=value {image_path} env
Working Directory
singularity exec --pwd /workspace {image_path} pwd
Fakeroot (Unprivileged)
singularity shell --fakeroot {image_path}
HPC/CLUSTER USAGE
{'=' * 60}

Copy to Cluster
scp {image_path} user@cluster:/path/to/containers/
SLURM Job Script Example
#!/bin/bash
#SBATCH --job-name=singularity_job
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
module load singularity
singularity exec {image_path} python /workspace/script.py
IMAGE INFORMATION
{'=' * 60}
{image_info}

NOTES
{'=' * 60}
• Use 'singularity inspect {image_path}' for detailed information
• Use 'singularity run {image_path}' if the image has a runscript
• Use 'singularity test {image_path}' to run container tests

HELP
{'=' * 60}
• Singularity documentation: https://docs.sylabs.io/
• Apptainer documentation: https://apptainer.org/docs/
"""
    # Save to file if requested
    if output_file:
        output_file = os.path.expanduser(output_file)
        with open(output_file, "w") as f:
            f.write(guide)
        print(f"✓ Usage guide saved to: {output_file}")

    return guide
def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(
    description="Apptainer2LS - Ultimate Singularity/Apptainer Development Environment Tool",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
    Examples:
    %(prog)s create --work-dir ~/singularity_ws --image-name dev_env
    %(prog)s shell --image ~/singularity_ws/dev_env_sandbox
    %(prog)s test --image ~/singularity_ws/dev_env.sif
    %(prog)s convert --docker ubuntu:22.04 --output ubuntu.sif
    """
    )
    parser.add_argument(
    "--version", "-v",
    action="version",
    version=f"Apptainer2LS v{__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a development sandbox")
    create_parser.add_argument("--work-dir", default="~/singularity_workstation", help="Workspace directory")
    create_parser.add_argument("--base-image", default="docker://ubuntu:22.04", help="Base container image")
    create_parser.add_argument("--image-name", default="dev_sandbox", help="Name for the Singularity image")
    create_parser.add_argument("--packages", nargs="+", help="Additional system packages")
    create_parser.add_argument("--pip-packages", nargs="+", help="Python packages to install")
    create_parser.add_argument("--conda-packages", nargs="+", help="Conda packages to install")
    create_parser.add_argument("--gpu-support", action="store_true", help="Enable GPU support")
    create_parser.add_argument("--cuda-version", help="CUDA version for GPU support")
    create_parser.add_argument("--mpi-support", action="store_true", help="Enable MPI support")
    create_parser.add_argument("--force-rebuild", action="store_true", help="Force rebuild even if exists")
    create_parser.add_argument("--config", help="Configuration file")

    # Shell command
    shell_parser = subparsers.add_parser("shell", help="Start interactive shell in container")
    shell_parser.add_argument("--image", required=True, help="Path to Singularity image/sandbox")
    shell_parser.add_argument("--bind", nargs="+", help="Bind mounts (host:container)")
    shell_parser.add_argument("--gpu", action="store_true", help="Enable GPU support")
    shell_parser.add_argument("--workdir", help="Working directory in container")
    shell_parser.add_argument("--env", nargs="+", help="Environment variables (KEY=VALUE)")

    # Exec command
    exec_parser = subparsers.add_parser("exec", help="Execute command in container")
    exec_parser.add_argument("--image", required=True, help="Path to Singularity image/sandbox")
    exec_parser.add_argument("--bind", nargs="+", help="Bind mounts (host:container)")
    exec_parser.add_argument("--gpu", action="store_true", help="Enable GPU support")
    exec_parser.add_argument("--workdir", help="Working directory in container")
    exec_parser.add_argument("--env", nargs="+", help="Environment variables (KEY=VALUE)")
    exec_parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to execute")

    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert Docker to Singularity")
    convert_parser.add_argument("--docker", required=True, help="Docker image name")
    convert_parser.add_argument("--output", required=True, help="Output Singularity image path")
    convert_parser.add_argument("--sandbox", action="store_true", help="Create sandbox instead of SIF")
    convert_parser.add_argument("--force", action="store_true", help="Overwrite existing")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test container environment")
    test_parser.add_argument("--image", required=True, help="Path to Singularity image/sandbox")
    test_parser.add_argument("--bind", nargs="+", help="Bind mounts (host:container)")
    test_parser.add_argument("--workdir", default="/workspace", help="Working directory for tests")

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup Singularity environment")
    backup_parser.add_argument("--image", required=True, help="Path to Singularity image/sandbox")
    backup_parser.add_argument("--output", help="Output backup file path")
    backup_parser.add_argument("--compress", choices=["gzip", "bzip2", "xz", "none"], default="gzip", help="Compression method")
    backup_parser.add_argument("--verify", action="store_true", help="Verify backup after creation")

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore Singularity environment")
    restore_parser.add_argument("--backup", required=True, help="Path to backup file")
    restore_parser.add_argument("--output", help="Output path for restored environment")
    restore_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing")
    restore_parser.add_argument("--verify", action="store_true", default=True, help="Verify checksum before restore")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan image for security issues")
    scan_parser.add_argument("--image", required=True, help="Path to Singularity image/sandbox")
    scan_parser.add_argument("--output", help="Output file for report")
    scan_parser.add_argument("--format", choices=["text", "json", "html"], default="text", help="Output format")

    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Create batch job templates")
    batch_parser.add_argument("--job-name", default="singularity_job", help="Job name")
    batch_parser.add_argument("--image", help="Path to Singularity image")
    batch_parser.add_argument("--gpu", action="store_true", help="Include GPU support")
    batch_parser.add_argument("--output-dir", default=".", help="Output directory")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check Apptainer/Singularity availability")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install Apptainer/Singularity")

    # Guide command
    guide_parser = subparsers.add_parser("guide", help="Generate usage guide")
    guide_parser.add_argument("--image", required=True, help="Path to Singularity image/sandbox")
    guide_parser.add_argument("--output", help="Output file")
    guide_parser.add_argument("--format", choices=["text", "markdown", "html"], default="text", help="Output format")

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == "create":
        # Parse bind mounts
        bind_mounts = {}
        if hasattr(args, "bind") and args.bind:
            for bind in args.bind:
                if ":" in bind:
                    host, container = bind.split(":", 1)
                    bind_mounts[host] = container
        
        # Parse environment variables
        env_vars = {}
        if hasattr(args, "env") and args.env:
            for env in args.env:
                if "=" in env:
                    key, value = env.split("=", 1)
                    env_vars[key] = value
        
        result = create_singularity_workstation(
            work_dir=args.work_dir,
            base_image=args.base_image,
            image_name=args.image_name,
            packages=args.packages,
            pip_packages=args.pip_packages,
            conda_packages=args.conda_packages,
            bind_mounts=bind_mounts,
            force_rebuild=args.force_rebuild,
            gpu_support=args.gpu_support,
            cuda_version=args.cuda_version,
            mpi_support=args.mpi_support,
            config_file=args.config
        )
        
        if not result.get("success", False):
            sys.exit(1)

    elif args.command == "shell":
        # Parse bind mounts
        bind_mounts = {}
        if args.bind:
            for bind in args.bind:
                if ":" in bind:
                    host, container = bind.split(":", 1)
                    bind_mounts[host] = container
        
        # Parse environment variables
        env_vars = {}
        if args.env:
            for env in args.env:
                if "=" in env:
                    key, value = env.split("=", 1)
                    env_vars[key] = value
        
        shell_into_container(
            image_path=args.image,
            bind_mounts=bind_mounts,
            environment=env_vars,
            working_dir=args.workdir,
            gpu=args.gpu
        )

    elif args.command == "exec":
        if not args.command:
            print("Error: No command specified")
            sys.exit(1)
        
        # Parse bind mounts
        bind_mounts = {}
        if args.bind:
            for bind in args.bind:
                if ":" in bind:
                    host, container = bind.split(":", 1)
                    bind_mounts[host] = container
        
        # Parse environment variables
        env_vars = {}
        if args.env:
            for env in args.env:
                if "=" in env:
                    key, value = env.split("=", 1)
                    env_vars[key] = value
        
        cmd = " ".join(args.command)
        result = run_singularity_command(
            image_path=args.image,
            command=cmd,
            bind_mounts=bind_mounts,
            environment=env_vars,
            working_dir=args.workdir,
            gpu=args.gpu
        )
        
        if not result.get("success", False):
            sys.exit(1)
        
        # Print output
        if result.get("stdout"):
            print(result["stdout"])
        if result.get("stderr"):
            print(result["stderr"], file=sys.stderr)

    elif args.command == "convert":
        result = convert_docker_to_singularity(
            docker_image=args.docker,
            singularity_image=args.output,
            sandbox=args.sandbox,
            force=args.force
        )
        
        if not result.get("success", False):
            sys.exit(1)

    elif args.command == "test":
        # Parse bind mounts
        bind_mounts = {}
        if args.bind:
            for bind in args.bind:
                if ":" in bind:
                    host, container = bind.split(":", 1)
                    bind_mounts[host] = container
        
        result = test_singularity_environment(
            image_path=args.image,
            bind_mounts=bind_mounts,
            working_dir=args.workdir
        )
        
        if not result.get("overall_success", False):
            sys.exit(1)

    elif args.command == "backup":
        result = backup_singularity_environment(
            sandbox_dir=args.image,
            backup_dir=os.path.dirname(args.output) if args.output else None,
            backup_name=os.path.basename(args.output) if args.output else None,
            compression=args.compress,
            verify=args.verify
        )
        
        if not result.get("success", False):
            sys.exit(1)

    elif args.command == "restore":
        result = restore_singularity_environment(
            backup_path=args.backup,
            restore_dir=os.path.dirname(args.output) if args.output else None,
            restore_name=os.path.basename(args.output) if args.output else None,
            overwrite=args.overwrite,
            verify_checksum=args.verify
        )
        
        if not result.get("success", False):
            sys.exit(1)

    elif args.command == "scan":
        result = scan_singularity_image(
            image_path=args.image,
            output_format=args.format,
            output_file=args.output
        )
        
        if args.output:
            print(f"Scan report saved to: {args.output}")
        else:
            print(generate_text_report(result))

    elif args.command == "batch":
        result = create_batch_job_template(
            job_name=args.job_name,
            image_path=args.image,
            gpu_support=args.gpu,
            output_dir=args.output_dir
        )
        
        print(f"Batch job templates created in: {args.output_dir}")

    elif args.command == "check":
        result = check_apptainer_availability()
        print(f"Apptainer/Singularity availability:")
        print(f"  Available: {result['available']}")
        print(f"  Command: {result['command']}")
        print(f"  Version: {result['version']}")
        print(f"  Message: {result['message']}")
        
        if not result["available"]:
            sys.exit(1)

    elif args.command == "install":
        install_apptainer_tool()

    elif args.command == "guide":
        guide = generate_singularity_usage_guide(
            image_path=args.image,
            output_file=args.output,
            format=args.format
        )
        
        if not args.output:
            print(guide)

if name == "main__":
    usage_str="""
# 检查Apptainer/Singularity可用性
python apptainer2ls.py check

# 创建开发沙盒
python apptainer2ls.py create --work-dir ~/dev_ws --image-name my_env

# 进入交互式Shell
python apptainer2ls.py shell --image ~/dev_ws/my_env_sandbox

# 执行命令
python apptainer2ls.py exec --image my_env.sif -- python script.py

# Docker转换
python apptainer2ls.py convert --docker tensorflow/tensorflow:latest --output tf.sif

# 备份环境
python apptainer2ls.py backup --image my_env_sandbox --output backup.tar.gz

# 安全扫描
python apptainer2ls.py scan --image my_env.sif --output scan_report.html

# 生成批处理模板
python apptainer2ls.py batch --job-name my_job --gpu --output-dir ./jobs
    """
    main()
    print(usage_str)