"""
# Basic usage
setup_docker_workstation()

# Custom setup with additional packages
setup_docker_workstation(
    work_dir="~/my-dev",
    image_tag="dev-env:latest",
    additional_packages=["nodejs", "docker.io", "postgresql-client"],
    pip_packages=["django", "flask", "fastapi", "black"],
    python_version="3.9"
)

# Skip build if image exists
setup_docker_workstation(skip_build=True)

# Load from config file
setup_docker_workstation(config_file="~/workspace_config.json")

# Force rebuild
setup_docker_workstation(force_rebuild=True)

#! command line usage:
# Basic setup
python docker2ls.py

# Custom directory and packages
python docker2ls.py --work-dir ~/projects --image-tag myproject:dev

# With additional packages
python docker2ls.py --packages nodejs npm --pip-packages django flask

# Skip build
python docker2ls.py --skip-build

# Load from config
python docker2ls.py --config ./workspace_config.json

"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from typing import List, Dict, Optional, Union
import platform
import getpass


try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: reportlab not installed. PDF generation will be disabled.")
    print("Install with: pip install reportlab")

def setup_docker_workstation(
    work_dir: str = "~/workstation",
    image_tag: str = "py2ls:latest",
    base_image: str = "ubuntu:22.04",
    python_version: str = "3",
    additional_packages: Optional[List[str]] = None,
    pip_packages: Optional[List[str]] = ["py2ls[slim]"],
    system_user: str = None,
    user_id: Optional[int] = None,
    group_id: Optional[int] = None,
    build_args: Optional[Dict[str, str]] = None,
    dockerfile_path: Optional[str] = None,
    force_rebuild: bool = False,
    skip_build: bool = False,
    config_file: Optional[str] = None
) -> Dict[str, Union[bool, str]]:
    """
    Sets up a persistent Docker workstation with advanced features.
    
    Args:
        work_dir: Host folder to persist work
        image_tag: Tag for the Docker image
        base_image: Base Docker image to use
        python_version: Python version (e.g., "3", "3.9")
        additional_packages: Additional system packages to install
        pip_packages: Additional Python packages to install via pip
        system_user: Username to create inside container
        user_id: User ID for the container user (defaults to host user ID)
        group_id: Group ID for the container user (defaults to host group ID)
        build_args: Additional build arguments for Docker
        dockerfile_path: Custom Dockerfile path (defaults to work_dir/Dockerfile)
        force_rebuild: Force rebuild even if image exists
        skip_build: Skip the build process (just generate Dockerfile)
        config_file: Load configuration from JSON file
        
    Returns:
        Dictionary with operation results and information
    """
    
    # Load configuration from file if provided
    if config_file:
        config = load_config(config_file)
        # Update function arguments with config values
        for key, value in config.items():
            if hasattr(sys, '_getframe'):
                # This is a workaround to access local variables
                if key == 'work_dir':
                    work_dir = value
                elif key == 'image_tag':
                    image_tag = value
                elif key == 'base_image':
                    base_image = value
                elif key == 'python_version':
                    python_version = value
                elif key == 'additional_packages':
                    additional_packages = value
                elif key == 'pip_packages':
                    pip_packages = value
                elif key == 'system_user':
                    system_user = value
                elif key == 'user_id':
                    user_id = value
                elif key == 'group_id':
                    group_id = value
                elif key == 'build_args':
                    build_args = value
                elif key == 'dockerfile_path':
                    dockerfile_path = value
                elif key == 'force_rebuild':
                    force_rebuild = value
                elif key == 'skip_build':
                    skip_build = value 
    
    # Initialize default lists if None
    if additional_packages is None:
        additional_packages = []
    if pip_packages is None:
        pip_packages = []
    if build_args is None:
        build_args = {}
    if system_user is None:
        system_user = getpass.getuser()
    # Expand user directory
    work_dir = os.path.expanduser(work_dir)
    work_dir = os.path.abspath(work_dir)
    
    # Check Docker availability
    docker_available = check_docker_availability()
    if not docker_available["available"]:
        print(f"Docker is not available: {docker_available['message']}")
        install_docker = input("Would you like to install Docker? (y/n): ")
        if install_docker.lower() == 'y':
            install_docker_tool()
        else:
            return {"success": False, "message": "Docker not available"}
    
    # Create workspace directory
    os.makedirs(work_dir, exist_ok=True)
    
    # Set default Dockerfile path
    if dockerfile_path is None:
        dockerfile_path = os.path.join(work_dir, "Dockerfile")
    
    # Generate Dockerfile content
    dockerfile_content = generate_dockerfile(
        base_image=base_image,
        python_version=python_version,
        additional_packages=additional_packages,
        pip_packages=pip_packages,
        system_user=system_user,
        user_id=user_id,
        group_id=group_id
    )
    
    # Write Dockerfile
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content)
    
    print(f"✓ Dockerfile created at {dockerfile_path}")
    
    # Check if image already exists
    if not force_rebuild and image_exists(image_tag):
        print(f"✓ Docker image '{image_tag}' already exists")
        if skip_build:
            result = {"success": True, "image_exists": True, "built": False}
        else:
            rebuild = input(f"Image '{image_tag}' exists. Rebuild? (y/n): ")
            if rebuild.lower() != 'y':
                skip_build = True
    
    # Build Docker image if not skipped
    build_result = {"success": True, "built": False}
    if not skip_build:
        print(f"Building Docker image '{image_tag}'...")
        build_result = build_docker_image(
            dockerfile_path=os.path.dirname(dockerfile_path),
            image_tag=image_tag,
            build_args=build_args
        )
    
    if build_result["success"]:
        # Save configuration
        config_data = {
            "work_dir": work_dir,
            "image_tag": image_tag,
            "base_image": base_image,
            "python_version": python_version,
            "additional_packages": additional_packages,
            "pip_packages": pip_packages,
            "system_user": system_user,
            "dockerfile_path": dockerfile_path
        }
        
        config_save_path = os.path.join(work_dir, "workspace_config.json")
        with open(config_save_path, "w") as f:
            json.dump(config_data, f, indent=2)
        
        print(f"✓ Configuration saved to {config_save_path}")
        
        # Display instructions
        display_instructions(
            work_dir=work_dir,
            image_tag=image_tag,
            system_user=system_user
        )
        
        # Generate helper scripts
        generate_helper_scripts(work_dir, image_tag, system_user)
    
    return {
        "success": build_result["success"],
        "work_dir": work_dir,
        "image_tag": image_tag,
        "dockerfile_path": dockerfile_path,
        "built": build_result.get("built", False)
    }


def check_docker_availability() -> Dict[str, Union[bool, str]]:
    """Check if Docker is available on the system."""
    try:
        # Check if docker command exists
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Check if Docker daemon is running
            daemon_result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True
            )
            if daemon_result.returncode == 0:
                return {
                    "available": True,
                    "message": "Docker is available and running",
                    "version": result.stdout.strip()
                }
            else:
                return {
                    "available": False,
                    "message": "Docker is installed but daemon is not running"
                }
        else:
            return {"available": False, "message": "Docker is not installed"}
    except FileNotFoundError:
        return {"available": False, "message": "Docker command not found"}


def install_docker_tool() -> bool:
    """Install Docker based on the operating system."""
    system = platform.system().lower()
    
    print(f"Detected system: {system}")
    
    if system == "linux":
        print("Installing Docker on Linux...")
        # Try to detect distribution
        try:
            with open("/etc/os-release", "r") as f:
                os_release = f.read()
            
            if "ubuntu" in os_release.lower() or "debian" in os_release.lower():
                commands = [
                    "sudo apt-get update",
                    "sudo apt-get install -y docker.io",
                    "sudo systemctl start docker",
                    "sudo systemctl enable docker",
                    "sudo usermod -aG docker $USER"
                ]
                for cmd in commands:
                    print(f"Running: {cmd}")
                    subprocess.run(cmd, shell=True, check=False)
                
                print("\n✓ Docker installed. Please log out and log back in for group changes to take effect.")
                return True
                
        except Exception as e:
            print(f"Error installing Docker: {e}")
            print("Please install Docker manually from: https://docs.docker.com/engine/install/")
    
    elif system == "darwin":  # macOS
        print("Please install Docker Desktop for Mac from: https://docs.docker.com/desktop/install/mac-install/")
    
    elif system == "windows":
        print("Please install Docker Desktop for Windows from: https://docs.docker.com/desktop/install/windows-install/")
    
    return False

def generate_dockerfile(
    base_image: str = "ubuntu:22.04",
    python_version: str = "3",
    additional_packages: List[str] = None,
    pip_packages: List[str] = None,
    system_user: str = None,
    user_id: Optional[int] = None,
    group_id: Optional[int] = None
) -> str:
    """Generate Dockerfile content dynamically."""
    if additional_packages is None:
        additional_packages = []
    if pip_packages is None:
        pip_packages = []
    
    # Default packages
    default_packages=[
        "python3","python3-pip","python3-venv","python-is-python3","software-properties-common",# Python runtime
        "bash", "zsh", "fzf", "tmux", "htop", "vim", "nano", "tree", # Shells & UX
        "rsync", "curl","wget",# Networking & transfer
        "rclone", # cloud
        "build-essential","git",# Build & dev
        "procps", "util-linux", "coreutils",# System introspection
        "lsof","strace",# Debug / power tools
    ]
    # default_packages = [
    #     # Core development
    #     "python3",
    #     "python3-pip",
    #     "python3-venv",
    #     "python3-dev",
    #     "build-essential",
    #     "cmake",
    #     "pkg-config",
        
    #     # Version control
    #     "git",
    #     "git-lfs",
    #     "tig",
        
    #     # Networking
    #     "curl",
    #     "wget",
    #     "httpie",
    #     "net-tools",
    #     "dnsutils",
    #     "iputils-ping",
    #     "traceroute",
    #     "mtr",
    #     "nmap",
    #     "ncat",
    #     "socat",
    #     "netcat-openbsd",
    #     "openssh-client",
    #     "openssh-server",
        
    #     # Editors & terminals
    #     "vim",
    #     "neovim",
    #     "nano",
    #     "micro",
    #     "tmux",
    #     "screen",
    #     "zsh",
        
    #     # File management
    #     "tree",
    #     "ncdu",
    #     "ranger",
    #     "rsync",
    #     "unzip",
    #     "zip",
    #     "p7zip-full",
    #     "rar",
    #     "unrar",
    #     "sshfs",
        
    #     # System monitoring
    #     "htop",
    #     "btop",
    #     "iotop",
    #     "iftop",
    #     "nethogs",
    #     "glances",
        
    #     # Process & system tools
    #     "procps",
    #     "lsof",
    #     "strace",
    #     "ltrace",
    #     "gdb",
    #     "valgrind",
        
    #     # Text processing
    #     "jq",
    #     "yq",
    #     "xmlstarlet",
    #     "csvkit",
    #     "moreutils",
        
    #     # Searching
    #     "ripgrep",
    #     "silversearcher-ag",
    #     "fd-find",
    #     "fzf",
        
    #     # Development utilities
    #     "direnv",
    #     "tldr",
    #     "cheat",
    #     "bat",
    #     "exa",
    #     "duf",
    #     "dust",
    #     "procs",
    #     "sd",
    #     "hyperfine",
    #     "bottom",
        
    #     # Documentation & fonts
    #     "pandoc",
    #     "texlive-latex-extra",
    #     "fonts-powerline",
    #     "fonts-firacode",
        
    #     # Misc utilities
    #     "neofetch",
    #     "cowsay",
    #     "figlet",
    #     "toilet",
    #     "lolcat",
    #     "sl",
    #     "cmatrix",
        
    #     # Container tools
    #     "docker.io",
    #     "docker-compose",
    #     "podman",
    #     "buildah",
    #     "skopeo",
        
    #     # Database clients
    #     "postgresql-client",
    #     "mysql-client",
    #     "redis-tools",
    #     "mongodb-clients",
    #     "sqlite3",
        
    #     # Cloud & orchestration
    #     "kubectl",
    #     "helm",
    #     "terraform",
    #     "awscli",
    #     "azure-cli",
    #     "google-cloud-sdk",
    # ]
    
    # Get current user IDs if not specified
    if user_id is None:
        user_id = os.getuid()
    if group_id is None:
        group_id = os.getgid()
    
    if system_user is None:
        system_user = getpass.getuser()
    # Combine packages
    all_packages = default_packages + additional_packages
    packages_str = " \\\n        ".join(all_packages)
    
    # Combine pip packages (including py2ls by default) 
    all_pip_packages = ["py2ls[slim]"] + pip_packages if not any('py2ls' in str(i).lower() for i in pip_packages) else pip_packages

    # Remove duplicates while preserving order
    seen = set()
    unique_pip_packages = []
    for pkg in all_pip_packages:
        if pkg not in seen:
            seen.add(pkg)
            unique_pip_packages.append(pkg)
    
    pip_packages_str = " \\\n        ".join(unique_pip_packages)
    
    dockerfile = f"""# Dockerfile for development workstation
FROM {base_image}

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \\
        {packages_str} \\
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python packages
RUN python{python_version} -m pip install --upgrade pip setuptools wheel

# Install additional Python packages
RUN python{python_version} -m pip install \\
        --progress-bar on \\
        --no-cache-dir \\
        {pip_packages_str}

# Create workspace directory
WORKDIR /workspace

# Create user with same UID/GID as host for file permissions
# Check if group already exists, create if not
RUN if ! getent group {group_id}; then groupadd -g {group_id} {system_user}; else groupmod -n {system_user} $(getent group {group_id} | cut -d: -f1); fi && \\
    useradd -m -u {user_id} -g {group_id} -s /bin/bash {system_user}

# Set ownership of workspace
RUN chown -R {user_id}:{group_id} /workspace

# Switch to non-root user
USER {system_user}

# Set up bashrc with common aliases
RUN echo 'alias ll="ls -la"' >> ~/.bashrc && \\
    echo 'alias python="python{python_version}"' >> ~/.bashrc && \\
    echo 'alias pip="python{python_version} -m pip"' >> ~/.bashrc

# Default command
CMD ["/bin/bash"]
"""
    
    return dockerfile
 
def image_exists(image_tag: str) -> bool:
    """Check if Docker image already exists."""
    try:
        result = subprocess.run(
            ["docker", "image", "inspect", image_tag],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def build_docker_image(
    dockerfile_path: str,
    image_tag: str,
    build_args: Dict[str, str] = None
) -> Dict[str, Union[bool, str]]:
    """Build Docker image with live progress output."""
    if build_args is None:
        build_args = {}

    try:
        cmd = ["docker", "build", "-t", image_tag]

        for key, value in build_args.items():
            cmd.extend(["--build-arg", f"{key}={value}"])

        cmd.append(dockerfile_path)

        print(f"Running: {' '.join(cmd)}\n")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        spin_idx = 0

        for line in process.stdout:
            # Live spinner (overwrites same line)
            sys.stdout.write(
                f"\r{spinner[spin_idx % len(spinner)]} Building Docker image…"
            )
            sys.stdout.flush()
            spin_idx += 1

            # Print meaningful docker output
            if line.strip():
                print(f"\n{line}", end="")

        process.wait()
        print()  # newline after spinner

        if process.returncode == 0:
            print(f"\n✓ Docker image '{image_tag}' built successfully!")
            return {"success": True, "built": True}
        else:
            print("\n✗ Docker build failed")
            return {"success": False, "error": "Docker build failed"}

    except Exception as e:
        print(f"\n✗ Error building Docker image: {e}")
        return {"success": False, "error": str(e)}

def display_instructions(
    work_dir: str,
    image_tag: str,
    system_user: str = None,
    dockerhub_user: str = None,
    return_content: bool = False
) -> Union[None, Dict[str, List[str]]]:
    """
    Display professional, comprehensive, and practical daily usage instructions
    for the Docker workstation container.
    
    Args:
        work_dir: Workspace directory
        image_tag: Docker image tag
        system_user: System username
        dockerhub_user: Docker Hub username
        return_content: If True, return content instead of printing
    
    Returns:
        If return_content=True: Dictionary with section titles and content
        Otherwise: None (prints to console)
    """
    if system_user is None:
        system_user = getpass.getuser()
    if dockerhub_user is None:
        try:
            dockerhub_user = get_dockerhub_username()
        except:
            dockerhub_user = system_user
    
    container_name = image_tag.split(":")[0].replace("/", "_")
    image_name = image_tag.split(":")[0]
    tag = image_tag.split(":")[1] if ":" in image_tag else "latest"
    
    # Prepare content sections
    sections = {}
    
    # ============================================================================
    # SECTION 0: DOCKER HUB OPERATIONS
    # ============================================================================
    sections["SECTION 0: DOCKER HUB OPERATIONS"] = []
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append("-" * 40)
    
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append("\nDOCKER HUB AUTHENTICATION:")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"# Login to Docker Hub")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker login")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"\n# Login with specific credentials")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker login -u {dockerhub_user}")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"\n# Logout from Docker Hub")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker logout")
    
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append("\nPULL IMAGES FROM DOCKER HUB:")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"# Pull latest version")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker pull {dockerhub_user}/{image_name}:latest")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"\n# Pull specific version")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker pull {dockerhub_user}/{image_name}:v1.0.0")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"\n# Pull with digest (immutable)")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker pull {dockerhub_user}/{image_name}@sha256:abc123...")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"\n# Pull all tags")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker pull --all-tags {dockerhub_user}/{image_name}")
    
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append("\nPREPARE IMAGES FOR PUSH:")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"# Tag local image for Docker Hub")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker tag {image_tag} {dockerhub_user}/{image_name}:{tag}")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"\n# Tag with multiple tags")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker tag {image_tag} {dockerhub_user}/{image_name}:latest")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker tag {image_tag} {dockerhub_user}/{image_name}:v1.0.0")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker tag {image_tag} {dockerhub_user}/{image_name}:$(date +%Y%m%d)")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"\n# Build and tag directly")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker build -t {dockerhub_user}/{image_name}:latest -t {dockerhub_user}/{image_name}:v1.0.0 .")
    
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append("\nPUSH IMAGES TO DOCKER HUB:")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"# Push single tag")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker push {dockerhub_user}/{image_name}:latest")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"\n# Push all tags for an image")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker push {dockerhub_user}/{image_name} --all-tags")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"\n# Multi-architecture push (if using buildx)")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker buildx build --platform linux/amd64,linux/arm64 -t {dockerhub_user}/{image_name}:latest --push .")
    
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append("\nIMAGE MANAGEMENT:")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"# List local images")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker images")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker image ls")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"\n# Search Docker Hub")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker search {image_name}")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"\n# Remove unused images")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker image prune -a")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"\n# Remove specific image")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker rmi {dockerhub_user}/{image_name}:latest")
    
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append("\nDOCKER HUB BEST PRACTICES:")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"# Use version tags")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker tag {image_name}:latest {dockerhub_user}/{image_name}:v1.2.3")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"\n# Keep images small")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker history {dockerhub_user}/{image_name}:latest")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"\n# Scan for vulnerabilities")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker scan {dockerhub_user}/{image_name}:latest")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"\n# Inspect pushed image")
    sections["SECTION 0: DOCKER HUB OPERATIONS"].append(f"docker inspect {dockerhub_user}/{image_name}:latest")
    
    # ============================================================================
    # SECTION 1: ENVIRONMENT OVERVIEW
    # ============================================================================
    sections["SECTION 1: ENVIRONMENT OVERVIEW"] = []
    sections["SECTION 1: ENVIRONMENT OVERVIEW"].append("-" * 40)
    sections["SECTION 1: ENVIRONMENT OVERVIEW"].append(f"Host Workspace Directory: {work_dir}")
    sections["SECTION 1: ENVIRONMENT OVERVIEW"].append(f"Docker Image-Tag: {image_tag}")
    sections["SECTION 1: ENVIRONMENT OVERVIEW"].append(f"Docker Hub Repository: {dockerhub_user}/{image_name}")
    sections["SECTION 1: ENVIRONMENT OVERVIEW"].append(f"Container Name: {container_name}")
    sections["SECTION 1: ENVIRONMENT OVERVIEW"].append(f"Container User: {system_user}")
    sections["SECTION 1: ENVIRONMENT OVERVIEW"].append(f"Container Workspace: /workspace")
    sections["SECTION 1: ENVIRONMENT OVERVIEW"].append(f"Volume Mount: {work_dir} <-> /workspace")
    
    # ============================================================================
    # SECTION 2: COMPLETE FIRST-TIME SETUP
    # ============================================================================
    sections["SECTION 2: COMPLETE FIRST-TIME SETUP"] = []
    sections["SECTION 2: COMPLETE FIRST-TIME SETUP"].append("-" * 20 + "90% cases" + "-" * 20)
    sections["SECTION 2: COMPLETE FIRST-TIME SETUP"].append(f"""docker run -dit --name {container_name} \\ \n    -v {work_dir}:/workspace \\ \n    {image_tag}""")
    
    sections["SECTION 2: COMPLETE FIRST-TIME SETUP"].append("""
docker run → creates new container 'Start a NEW Container'
docker start → starts existing container
docker exec → enters running container
          """)
    
    sections["SECTION 2: COMPLETE FIRST-TIME SETUP"].append(f"""docker run -dit --name {container_name} \\
    --hostname {container_name}-dev \\
    --restart unless-stopped \\
    --memory="4g" \\
    --cpus="2.0" \\
    --shm-size="1g" \\
    -v {work_dir}:/workspace \\
    -v {work_dir}/.cache:/home/{system_user}/.cache \\
    -v {work_dir}/.config:/home/{system_user}/.config \\
    -v ~/.ssh:/home/{system_user}/.ssh:ro \\
    -v ~/.gitconfig:/home/{system_user}/.gitconfig:ro \\
    -v ~/.aws:/home/{system_user}/.aws:ro \\
    -v ~/.docker:/home/{system_user}/.docker:ro \\
    -v /tmp/.X11-unix:/tmp/.X11-unix \\
    -v /var/run/docker.sock:/var/run/docker.sock \\
    -e DISPLAY=${{DISPLAY}} \\
    -e TERM=xterm-256color \\
    -e LANG=C.UTF-8 \\
    -e LC_ALL=C.UTF-8 \\
    -e PYTHONPATH=/workspace \\
    -e PYTHONUNBUFFERED=1 \\
    -p 8888:8888 \\
    -p 8080:8080 \\
    -p 3000:3000 \\
    -p 5432:5432 \\
    -p 6379:6379 \\
    --add-host=host.docker.internal:host-gateway \\
    --security-opt seccomp=unconfined \\
    --cap-add=SYS_PTRACE \\
    {image_tag}""")
    
    sections["SECTION 2: COMPLETE FIRST-TIME SETUP"].append(f""" # Full explanation
    docker run -dit --name {container_name} \\  # -d: detached mode, -i: interactive, -t: allocate a pseudo-TTY
        --hostname {container_name}-dev \\      # Set container hostname
        --restart unless-stopped \\            # Automatically restart container unless manually stopped
        --memory="4g" \\                       # Limit container memory to 4 GB
        --cpus="2.0" \\                        # Limit container to 2 CPU cores
        --shm-size="1g" \\                     # Shared memory size, useful for Jupyter or ML workloads
        -v {work_dir}:/workspace \\            # Mount your workspace folder (persistent code/data)
        -v {work_dir}/.cache:/home/{system_user}/.cache \\  # Cache folder inside container
        -v {work_dir}/.config:/home/{system_user}/.config \\ # Config folder inside container
        -v ~/.ssh:/home/{system_user}/.ssh:ro \\           # Mount SSH keys read-only
        -v ~/.gitconfig:/home/{system_user}/.gitconfig:ro \\ # Mount Git config read-only
        -v ~/.aws:/home/{system_user}/.aws:ro \\           # Mount AWS credentials read-only
        -v ~/.docker:/home/{system_user}/.docker:ro \\     # Mount Docker config read-only (for docker-in-docker)
        -v /tmp/.X11-unix:/tmp/.X11-unix \\               # For GUI apps (X11 forwarding)
        -v /var/run/docker.sock:/var/run/docker.sock \\   # Allow container to run Docker commands
        -e DISPLAY=${{DISPLAY}} \\                        # Forward display for GUI apps
        -e TERM=xterm-256color \\                         # Set terminal type
        -e LANG=C.UTF-8 \\                                # Language setting
        -e LC_ALL=C.UTF-8 \\                              # Language/locale
        -e PYTHONPATH=/workspace \\                       # Python path inside container
        -e PYTHONUNBUFFERED=1 \\                          # Python output is unbuffered (real-time logging)
        -p 8888:8888 \\                                   # Map host port 8888 (e.g., Jupyter) to container
        -p 8080:8080 \\                                   # Map host port 8080 (e.g., web app) to container
        -p 3000:3000 \\                                   # Map host port 3000 (frontend dev) to container
        -p 5432:5432 \\                                   # Map host port 5432 (PostgreSQL) to container
        -p 6379:6379 \\                                   # Map host port 6379 (Redis) to container
        --add-host=host.docker.internal:host-gateway \\   # Map host.docker.internal to host gateway
        --security-opt seccomp=unconfined \\              # Relax security for debugging/tracing
        --cap-add=SYS_PTRACE \\                           # Allow debugging (ptrace)
        {image_tag}                                      # Docker image to use
    """)
    
    # ============================================================================
    # SECTION 3: DAILY DEVELOPMENT WORKFLOW
    # ============================================================================
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"] = []
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"].append("-" * 40)
    
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"].append("\nCONTAINER LIFE CYCLE MANAGEMENT:")
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"].append(f"  # Start container")
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"].append(f"  docker start {container_name}")
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"].append(f"  \n  # Attach with interactive shell")
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"].append(f"  docker exec -it {container_name} bash")
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"].append(f"  \n  # Attach as root (for admin tasks)")
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"].append(f"  docker exec -it -u root {container_name} bash")
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"].append(f"  \n  # Execute single command")
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"].append(f"  docker exec {container_name} python --version")
    
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"].append("\nPROJECT SETUP TEMPLATE:")
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"].append(f"""mkdir -p {work_dir}/{{project_name}}/{{src,tests,docs,data,notebooks}}
cd {work_dir}/project_name
echo "# Project Structure
├── src/           # Source code
├── tests/         # Test files
├── docs/          # Documentation
├── data/          # Datasets
├── notebooks/     # Jupyter notebooks
└── requirements.txt
" > README.md""")
    
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"].append("\nPYTHON ENVIRONMENT SETUP:")
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"].append(r"""# Inside container at /workspace/project_name
python -m venv venv --prompt="project_name"
source venv/bin/activate

# Create comprehensive requirements
cat > requirements.txt << EOF
# Core dependencies
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0

# Development tools
black>=23.0.0
flake8>=6.0.0
pytest>=7.0.0
pytest-cov>=4.0.0
pre-commit>=3.0.0

# Documentation
sphinx>=7.0.0
myst-parser>=2.0.0

# Notebook support
jupyter>=1.0.0
ipykernel>=6.0.0
EOF

# Install with optimizations
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Register kernel for Jupyter
python -m ipykernel install --user --name="project_name" --display-name="Python (project_name)"

# Setup pre-commit hooks
pre-commit install""")
    
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"].append("\nDAILY DEVELOPMENT COMMANDS:")
    sections["SECTION 3: DAILY DEVELOPMENT WORKFLOW"].append(r"""# Code editing
code .                          # VS Code in container
vim main.py                     # Terminal editor

# Testing
pytest tests/ -v               # Run all tests
pytest tests/ -xvs             # Stop on first failure with verbose output
pytest --cov=src tests/        # Coverage report

# Formatting & Linting
black src/                     # Auto-format
flake8 src/                    # Lint check
mypy src/                      # Type checking

# Package management
pip list --outdated           # Check outdated packages
pip install -U package        # Update specific package
pip freeze > requirements.txt # Freeze dependencies""")
    
    # ============================================================================
    # SECTION 4: VS CODE INTEGRATION
    # ============================================================================
    sections["SECTION 4: VS CODE INTEGRATION"] = []
    sections["SECTION 4: VS CODE INTEGRATION"].append("-" * 40)
    
    sections["SECTION 4: VS CODE INTEGRATION"].append("\nADVANCED DEV CONTAINER CONFIGURATION:")
    sections["SECTION 4: VS CODE INTEGRATION"].append(f"""Create {work_dir}/.devcontainer/devcontainer.json:
{{
  "name": "{container_name} Development",
  "dockerComposeFile": "docker-compose.yml",
  "service": "workspace",
  "workspaceFolder": "/workspace",
  "remoteUser": "{system_user}",
  
  // VS Code extensions for Python development
  "extensions": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "ms-toolsai.jupyter",
    "GitHub.copilot",
    "eamodio.gitlens",
    "charliermarsh.ruff"
  ],
  
  // Port forwarding
  "forwardPorts": [8888, 8080, 3000],
  
  // Container environment variables
  "containerEnv": {{
    "PYTHONPATH": "/workspace",
    "PYTHONUNBUFFERED": "1"
  }},
  
  // Post-create commands
  "postCreateCommand": "pip install --upgrade pip && pre-commit install",
  
  // Customizations
  "customizations": {{
    "vscode": {{
      "settings": {{
        "python.defaultInterpreterPath": "/workspace/venv/bin/python",
        "python.linting.enabled": true,
        "python.formatting.provider": "black",
        "editor.formatOnSave": true
      }}
    }}
  }}
}}""")
    
    sections["SECTION 4: VS CODE INTEGRATION"].append("\nQUICK START WITH VS CODE:")
    sections["SECTION 4: VS CODE INTEGRATION"].append("1. Install 'Remote - Containers' extension")
    sections["SECTION 4: VS CODE INTEGRATION"].append("2. Open command palette (Ctrl+Shift+P)")
    sections["SECTION 4: VS CODE INTEGRATION"].append("3. 'Remote-Containers: Open Folder in Container'")
    sections["SECTION 4: VS CODE INTEGRATION"].append("4. Select your workspace directory")
    sections["SECTION 4: VS CODE INTEGRATION"].append("5. VS Code will build and connect automatically")
    
    # ============================================================================
    # SECTION 5: JUPYTER ECOSYSTEM
    # ============================================================================
    sections["SECTION 5: JUPYTER ECOSYSTEM"] = []
    sections["SECTION 5: JUPYTER ECOSYSTEM"].append("-" * 40)
    
    sections["SECTION 5: JUPYTER ECOSYSTEM"].append("\nJUPYTER SETUP:")
    sections["SECTION 5: JUPYTER ECOSYSTEM"].append("""# Production Jupyter Lab configuration
mkdir -p ~/.jupyter
cat > ~/.jupyter/jupyter_lab_config.py << EOF
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.root_dir = '/workspace'
c.ServerApp.token = ''  # Set password in production
c.ServerApp.password = ''
c.ServerApp.allow_origin = '*'
c.ServerApp.allow_root = True
c.LabApp.collaborative = True
c.ContentsManager.allow_hidden = True
EOF

# Start Jupyter Lab with optimizations
jupyter lab --config=~/.jupyter/jupyter_lab_config.py \
            --LabApp.allow_remote_access=True \
            --no-browser \
            --NotebookApp.terminado_settings={{'shell_command': ['bash']}}
            
# Alternative: Jupyter Notebook
jupyter notebook --notebook-dir=/workspace \
                 --ip=0.0.0.0 \
                 --port=8888 \
                 --no-browser \
                 --allow-root""")
    
    sections["SECTION 5: JUPYTER ECOSYSTEM"].append("\nACCESS JUPYTER FROM HOST:")
    sections["SECTION 5: JUPYTER ECOSYSTEM"].append("  Local: http://localhost:8888")
    sections["SECTION 5: JUPYTER ECOSYSTEM"].append("  Network: http://<your-ip>:8888")
    sections["SECTION 5: JUPYTER ECOSYSTEM"].append("\nSECURITY NOTE: In production, use:")
    sections["SECTION 5: JUPYTER ECOSYSTEM"].append("  --NotebookApp.token='your-secret-token'")
    sections["SECTION 5: JUPYTER ECOSYSTEM"].append("  Or set password with: jupyter notebook password")
    
    # ============================================================================
    # SECTION 6: GIT WORKFLOW & COLLABORATION
    # ============================================================================
    sections["SECTION 6: GIT WORKFLOW & COLLABORATION"] = []
    sections["SECTION 6: GIT WORKFLOW & COLLABORATION"].append("-" * 40)
    
    sections["SECTION 6: GIT WORKFLOW & COLLABORATION"].append("\nGIT CONFIGURATION:")
    sections["SECTION 6: GIT WORKFLOW & COLLABORATION"].append("""# Inside container, set up Git identity
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global core.editor "vim"
git config --global pull.rebase true
git config --global init.defaultBranch main

# SSH Agent forwarding (if needed)
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa""")
    
    sections["SECTION 6: GIT WORKFLOW & COLLABORATION"].append("\nGIT WORKFLOW COMMANDS:")
    sections["SECTION 6: GIT WORKFLOW & COLLABORATION"].append("""# Clone repositories
git clone git@github.com:username/repo.git /workspace/repo

# Daily workflow
git status                      # Check changes
git diff                        # Review changes
git add -p                     # Interactive staging
git commit -s -m "feat: add feature"  # Signed commit
git push origin main           # Push to remote

# Branch management
git checkout -b feature/new-feature
git push -u origin feature/new-feature
git checkout main
git merge --no-ff feature/new-feature""")
    
    sections["SECTION 6: GIT WORKFLOW & COLLABORATION"].append("\nPRE-COMMIT HOOKS SETUP:")
    sections["SECTION 6: GIT WORKFLOW & COLLABORATION"].append("""# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
  
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8""")
    
    # ============================================================================
    # SECTION 7: NETWORKING & PORTS
    # ============================================================================
    sections["SECTION 7: NETWORKING & PORTS"] = []
    sections["SECTION 7: NETWORKING & PORTS"].append("-" * 40)
    
    sections["SECTION 7: NETWORKING & PORTS"].append("\nPORT MAPPING REFERENCE:")
    sections["SECTION 7: NETWORKING & PORTS"].append("  Port 8888  -> Jupyter Notebook/Lab")
    sections["SECTION 7: NETWORKING & PORTS"].append("  Port 8080  -> Web applications/APIs")
    sections["SECTION 7: NETWORKING & PORTS"].append("  Port 3000  -> Node.js/React development")
    sections["SECTION 7: NETWORKING & PORTS"].append("  Port 5432  -> PostgreSQL")
    sections["SECTION 7: NETWORKING & PORTS"].append("  Port 6379  -> Redis")
    sections["SECTION 7: NETWORKING & PORTS"].append("  Port 27017 -> MongoDB")
    sections["SECTION 7: NETWORKING & PORTS"].append("  Port 9200  -> Elasticsearch")
    sections["SECTION 7: NETWORKING & PORTS"].append("  Port 5601  -> Kibana")
    
    sections["SECTION 7: NETWORKING & PORTS"].append("\nDYNAMIC PORT FORWARDING:")
    sections["SECTION 7: NETWORKING & PORTS"].append(f"# Map additional ports after container creation")
    sections["SECTION 7: NETWORKING & PORTS"].append(f"docker stop {container_name}")
    sections["SECTION 7: NETWORKING & PORTS"].append(f"docker commit {container_name} {image_tag}-backup")
    sections["SECTION 7: NETWORKING & PORTS"].append(f"docker run -d -p 5000:5000 -p 8000:8000 --name {container_name}-new [other_options] {image_tag}")
    
    sections["SECTION 7: NETWORKING & PORTS"].append("\nNETWORK CONFIGURATION:")
    sections["SECTION 7: NETWORKING & PORTS"].append("""# Create custom network
docker network create dev-network

# Run container on custom network
docker run --network=dev-network --name=workspace ...

# Connect containers
docker network connect dev-network postgres-container
docker network connect dev-network redis-container

# Test connectivity
docker exec workspace ping postgres-container
docker exec workspace curl http://postgres-container:5432""")
    
    # ============================================================================
    # SECTION 8: VOLUME MANAGEMENT
    # ============================================================================
    sections["SECTION 8: VOLUME MANAGEMENT"] = []
    sections["SECTION 8: VOLUME MANAGEMENT"].append("-" * 40)
    
    sections["SECTION 8: VOLUME MANAGEMENT"].append("\nVOLUME STRATEGIES:")
    sections["SECTION 8: VOLUME MANAGEMENT"].append(f"  - Primary: {work_dir} <-> /workspace (Project files)")
    sections["SECTION 8: VOLUME MANAGEMENT"].append(f"  - Config: ~/.config <-> /home/{system_user}/.config (User settings)")
    sections["SECTION 8: VOLUME MANAGEMENT"].append(f"  - Cache: ~/.cache <-> /home/{system_user}/.cache (Build cache)")
    sections["SECTION 8: VOLUME MANAGEMENT"].append(f"  - SSH: ~/.ssh <-> /home/{system_user}/.ssh:ro (Git authentication)")
    sections["SECTION 8: VOLUME MANAGEMENT"].append(f"  - AWS: ~/.aws <-> /home/{system_user}/.aws:ro (Cloud credentials)")
    
    sections["SECTION 8: VOLUME MANAGEMENT"].append("\nNAMED VOLUMES (For databases):")
    sections["SECTION 8: VOLUME MANAGEMENT"].append("""# Create persistent data volumes
docker volume create postgres-data
docker volume create redis-data

# Use with containers
docker run -d --name postgres \
  -v postgres-data:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=secret \
  postgres:15

docker run -d --name redis \
  -v redis-data:/data \
  redis:7-alpine""")
    
    sections["SECTION 8: VOLUME MANAGEMENT"].append("\nBACKUP & RESTORE:")
    sections["SECTION 8: VOLUME MANAGEMENT"].append(f"""# Backup workspace from container
docker cp {container_name}:/workspace ./workspace-backup-$(date +%Y%m%d)

# Backup to tar archive
docker run --rm --volumes-from {container_name} \
  -v $(pwd):/backup ubuntu tar cvf /backup/workspace.tar /workspace

# Restore from backup
docker run --rm --volumes-from {container_name} \
  -v $(pwd):/backup ubuntu bash -c "cd / && tar xvf /backup/workspace.tar" """)
    
    # ============================================================================
    # SECTION 9: RESOURCE MANAGEMENT
    # ============================================================================
    sections["SECTION 9: RESOURCE MANAGEMENT"] = []
    sections["SECTION 9: RESOURCE MANAGEMENT"].append("-" * 40)
    
    sections["SECTION 9: RESOURCE MANAGEMENT"].append("\nMONITORING COMMANDS:")
    sections["SECTION 9: RESOURCE MANAGEMENT"].append(f"# Container statistics")
    sections["SECTION 9: RESOURCE MANAGEMENT"].append(f"docker stats {container_name}")
    sections["SECTION 9: RESOURCE MANAGEMENT"].append(f"\n# Detailed resource usage")
    sections["SECTION 9: RESOURCE MANAGEMENT"].append(f"docker stats {container_name} --format 'table {{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}\\t{{.MemPerc}}\\t{{.NetIO}}\\t{{.BlockIO}}'")
    sections["SECTION 9: RESOURCE MANAGEMENT"].append(f"\n# Process list inside container")
    sections["SECTION 9: RESOURCE MANAGEMENT"].append(f"docker top {container_name}")
    
    sections["SECTION 9: RESOURCE MANAGEMENT"].append("\nRESOURCE LIMITS ADJUSTMENT:")
    sections["SECTION 9: RESOURCE MANAGEMENT"].append(f"""# Update limits on running container
docker update {container_name} \\
  --memory="8g" \\
  --memory-swap="10g" \\
  --cpus="4.0" \\
  --restart=always""")
    
    sections["SECTION 9: RESOURCE MANAGEMENT"].append("\nDEBUGGING RESOURCE ISSUES:")
    sections["SECTION 9: RESOURCE MANAGEMENT"].append(f"""# Check container logs
docker logs {container_name} --tail 100 -f

# Inspect container configuration
docker inspect {container_name}

# Check Docker system resources
docker system df
docker system info""")
    
    # ============================================================================
    # SECTION 10: SECURITY PRACTICES
    # ============================================================================
    sections["SECTION 10: SECURITY PRACTICES"] = []
    sections["SECTION 10: SECURITY PRACTICES"].append("-" * 40)
    
    sections["SECTION 10: SECURITY PRACTICES"].append("\nSECURITY RECOMMENDATIONS:")
    sections["SECTION 10: SECURITY PRACTICES"].append("  1. Use read-only volumes for credentials (.ssh:ro, .aws:ro)")
    sections["SECTION 10: SECURITY PRACTICES"].append("  2. Regularly update base images")
    sections["SECTION 10: SECURITY PRACTICES"].append("  3. Scan images for vulnerabilities: docker scan {image_tag}")
    sections["SECTION 10: SECURITY PRACTICES"].append("  4. Use Docker Content Trust: export DOCKER_CONTENT_TRUST=1")
    sections["SECTION 10: SECURITY PRACTICES"].append("  5. Limit container capabilities")
    sections["SECTION 10: SECURITY PRACTICES"].append("  6. Use non-root user inside container")
    sections["SECTION 10: SECURITY PRACTICES"].append("  7. Set resource limits to prevent DoS")
    
    sections["SECTION 10: SECURITY PRACTICES"].append("\nSECRET MANAGEMENT:")
    sections["SECTION 10: SECURITY PRACTICES"].append("""# Use Docker secrets or environment files
echo "DB_PASSWORD=secret123" > .env
docker run --env-file .env ...

# Or use Docker secrets (Swarm mode)
echo "secret123" | docker secret create db_password -
docker service create --secret db_password ...""")
    
    # ============================================================================
    # SECTION 11: TROUBLESHOOTING
    # ============================================================================
    sections["SECTION 11: TROUBLESHOOTING"] = []
    sections["SECTION 11: TROUBLESHOOTING"].append("-" * 40)
    
    sections["SECTION 11: TROUBLESHOOTING"].append("\nCOMMON ISSUES & SOLUTIONS:")
    sections["SECTION 11: TROUBLESHOOTING"].append(f"""Issue: Container won't start
  Solution: docker logs {container_name} --tail 50

Issue: Permission denied on volumes
  Solution: docker exec -it -u root {container_name} chown -R {system_user}:{system_user} /workspace

Issue: Port already in use
  Solution: Change port mapping: -p 8889:8888

Issue: Out of disk space
  Solution: docker system prune -a --volumes

Issue: Slow performance
  Solution: Increase resources: docker update --memory="8g" --cpus="4" {container_name}

Issue: Network connectivity
  Solution: Check firewall: ufw allow 8888/tcp""")
    
    sections["SECTION 11: TROUBLESHOOTING"].append("\nDIAGNOSTIC COMMANDS:")
    sections["SECTION 11: TROUBLESHOOTING"].append(f"""# Check container health
docker inspect --format='{{json .State.Health}}' {container_name}

# Test network connectivity from container
docker exec {container_name} curl -I http://google.com

# Check mounted volumes
docker inspect --format='{{json .Mounts}}' {container_name}

# View resource usage history
docker stats {container_name} --no-stream""")
    
    # ============================================================================
    # SECTION 12: FZF (FUZZY FINDER) TOOLS
    # ============================================================================
    sections["SECTION 12: FZF (FUZZY FINDER) TOOLS"] = []
    sections["SECTION 12: FZF (FUZZY FINDER) TOOLS"].append("-" * 40)
    
    sections["SECTION 12: FZF (FUZZY FINDER) TOOLS"].append("\nFZF INTEGRATION WITH DOCKER:")
    sections["SECTION 12: FZF (FUZZY FINDER) TOOLS"].append("""# List containers with fzf
alias dps='docker ps --format "table {{.ID}}\\t{{.Names}}\\t{{.Status}}\\t{{.Ports}}" | fzf'

# List all containers (including stopped) with fzf
alias dpsa='docker ps -a --format "table {{.ID}}\\t{{.Names}}\\t{{.Status}}\\t{{.Ports}}" | fzf'

# List images with fzf
alias dim='docker images --format "table {{.Repository}}\\t{{.Tag}}\\t{{.Size}}" | fzf'

# Select and enter container
dshell() {
    container=$(docker ps --format "{{.Names}}" | fzf)
    [ -n "$container" ] && docker exec -it "$container" bash
}

# Select and stop container
dstop() {
    container=$(docker ps --format "{{.Names}}" | fzf)
    [ -n "$container" ] && docker stop "$container"
}

# Select and remove container
drm() {
    container=$(docker ps -a --format "{{.Names}}" | fzf)
    [ -n "$container" ] && docker rm "$container"
}

# Select and view container logs
dlogs() {
    container=$(docker ps --format "{{.Names}}" | fzf)
    [ -n "$container" ] && docker logs -f "$container"
}

# Search in Docker Hub with fzf
dsearch() {
    query=$(echo "" | fzf --print-query --prompt="Search Docker Hub: ")
    [ -n "$query" ] && docker search "$query" | fzf
}

# Docker compose services with fzf
dcomp() {
    service=$(docker compose ps --services | fzf)
    [ -n "$service" ] && docker compose logs -f "$service"
}

# FZF for file searching inside container
dfind() {
    container=$(docker ps --format "{{.Names}}" | fzf)
    [ -n "$container" ] && read -p "Search pattern: " pattern && docker exec "$container" find /workspace -name "$pattern" 2>/dev/null | fzf
}

# FZF for process selection inside container
dtop() {
    container=$(docker ps --format "{{.Names}}" | fzf)
    [ -n "$container" ] && docker exec "$container" ps aux | fzf
}

# FZF for volume management
dvol() {
    volume=$(docker volume ls --format "{{.Name}}" | fzf)
    [ -n "$volume" ] && docker volume inspect "$volume" | jq .
}

# FZF for network management
dnet() {
    network=$(docker network ls --format "{{.Name}}" | fzf)
    [ -n "$network" ] && docker network inspect "$network" | jq .
}""")
    
    sections["SECTION 12: FZF (FUZZY FINDER) TOOLS"].append("\nFZF ENHANCED COMMANDS:")
    sections["SECTION 12: FZF (FUZZY FINDER) TOOLS"].append("""# Enhanced grep with ripgrep and fzf
alias fzgrep='rg --color=always --line-number --no-heading . | fzf --ansi --height=60%'

# Enhanced find with fd and fzf
alias fzfind='fd --type f | fzf --height=60%'

# Enhanced file preview with bat and fzf
alias fzcat='fzf --preview "bat --color=always --style=numbers --line-range=:500 {}"'

# Git with fzf
alias fzgit='git status --short | fzf --multi --preview "git diff --color=always {+2} | head -200"'

# Process search with fzf
alias fzps='ps aux | fzf'

# History search with fzf
alias fzh='history | fzf'

# Directory navigation with fzf
alias fzcd='cd $(find . -type d | fzf)'""")
    
    sections["SECTION 12: FZF (FUZZY FINDER) TOOLS"].append("\nFZF CONFIGURATION:")
    sections["SECTION 12: FZF (FUZZY FINDER) TOOLS"].append("""# Add to ~/.bashrc for better fzf experience
export FZF_DEFAULT_OPTS="--height=60% --layout=reverse --border --preview-window=right:60%"
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'

# Color scheme
export FZF_DEFAULT_OPTS=$FZF_DEFAULT_OPTS'
 --color=fg:#ebdbb2,bg:#282828,hl:#fabd2f,fg+:#ebdbb2,bg+:#3c3836,hl+:#fabd2f
 --color=info:#83a598,prompt:#bdae93,spinner:#fabd2f,pointer:#83a598,marker:#fe8019,header:#665c54'""")
    
    # ============================================================================
    # SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE
    # ============================================================================
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"] = []
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("-" * 40)
    
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("\n🚀 MODERN COMMAND REPLACEMENTS:")
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("""# Modern replacements for classic commands
ll          → exa -la --git --icons     # Better ls with git status
cat         → bat                       # Syntax highlighting cat
du          → dust                      Interactive disk usage
df          → duf                       Better df with colors
ps          → procs                     Better process viewer
top         → btop                      Beautiful system monitor
find        → fd                        Faster, simpler find
grep        → rg (ripgrep)             Faster grep
http        → httpie                    User-friendly HTTP client
ping        → mtr                       Traceroute + ping combined
man         → tldr                      Simplified man pages
curl        → httpie                    Easier HTTP requests
nc          → ncat                      Enhanced netcat
dig         → dog                       Better DNS lookup""")
    
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("\n📁 FILE & DIRECTORY MANAGEMENT:")
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("""# Navigation
z <pattern>     # Smart directory jumping with zoxide
ranger          # Terminal file manager with Vim keys
ncdu            # Interactive disk usage analyzer
tree            # Directory tree visualization

# Search & find
fd "*.py"       # Find Python files
rg "import"     # Search for 'import' in files
ag "TODO"       # Fast code search
fzf             # Fuzzy find anything

# File operations
rsync -avz source/ dest/  # Advanced file syncing
sshfs user@host:/path /mnt # Mount remote via SSH
pv file > newfile         # Progress bar for transfers""")
    
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("\n🐍 PYTHON DEVELOPMENT:")
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("""# Virtual environments
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Package management
pipx install tool      # Install Python tools globally
poetry init           # Modern dependency management
pdm init              # Fast Python package manager

# Development tools
black .              # Auto-format code
ruff check .        # Ultra-fast linting
mypy .              # Type checking
pytest -v           # Run tests
pre-commit install  # Git hooks
ipython             # Enhanced REPL
jupyter lab         # Notebook interface""")
    
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("\n🔧 SYSTEM MONITORING & DEBUGGING:")
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("""# System monitoring
htop               # Process viewer
glances            # All-in-one system monitor
nethogs            # Network traffic by process
iftop              # Bandwidth monitoring
iotop              # Disk I/O monitoring

# Network tools
mtr google.com     # Continuous traceroute
nmap localhost     # Network discovery
tcpdump -i any     # Packet capture
socat              # Multipurpose relay

# Debugging
strace command     # System call tracing
ltrace command     # Library call tracing
gdb program        # Debugger
valgrind program   # Memory debugging""")
    
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("\n📊 TEXT PROCESSING & DATA:")
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("""# JSON/XML/CSV processing
jq '.key' file.json            # JSON query
yq e '.key' file.yaml          # YAML query
xmlstarlet sel -t -v '//tag'  # XML query
csvsql --query "SELECT *" file.csv  # SQL on CSV
xsv headers file.csv          # CSV inspection

# Text manipulation
sed 's/old/new/g' file        # Stream editor
awk '{print $1}' file         # Pattern scanning
cut -d',' -f1 file.csv        # Column extraction
paste file1 file2             # Merge files
column -t file                # Column formatting""")
    
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("\n🐳 DOCKER & CONTAINER TOOLS:")
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("""# Container management
docker compose up -d          # Start services
docker exec -it container bash # Enter container
docker logs -f container      # Follow logs
docker stats                  # Container resources
docker system prune -a        # Cleanup

# Image management
docker build -t name .
docker push name:tag
docker save image > file.tar
docker load < file.tar

# Podman (Docker alternative)
podman run --rm image
podman build -t name .
buildah bud -t name .""")
    
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("\n☁️ CLOUD & KUBERNETES:")
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("""# Kubernetes
kubectl get pods -A
kubectl describe pod name
kubectl logs -f pod
kubectl exec -it pod -- bash
kubectl apply -f manifest.yaml
helm install name chart

# Cloud CLI
aws s3 ls
az vm list
gcloud compute instances list
terraform init
terraform apply""")
    
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("\n🎨 TERMINAL ENHANCEMENTS:")
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("""# Terminal multiplexers
tmux new -s session     # New session
tmux attach -t session  # Attach to session
tmux ls                 # List sessions
screen -S session       # Screen alternative

# Shell enhancements
zsh                     # Advanced shell
starship prompt         # Fast cross-shell prompt
direnv                  # Directory-specific env vars
fzf-tmux                # FZF in tmux pane

# Productivity
tig                     # Git TUI
ranger                  # File manager TUI
ncdu                    # Disk usage TUI
btop                    # Resource monitor TUI""")
    
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("\n🔐 SECURITY TOOLS:")
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("""# Network security
nmap -sV target         # Service detection
ssh-keygen -t ed25519   # Generate SSH key
openssl s_client -connect host:443  # SSL test
ncat -l -p 8080         # Open listener
socat TCP-LISTEN:8080,fork TCP:host:80  # Port forward""")
    
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("\n🎮 FUN & PRODUCTIVITY:")
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("""# Fun commands
neofetch                # System info in style
cowsay "Hello"          # Talking cow
figlet "TEXT"           # ASCII art
toilet -f term "BIG"    # Fancy display
lolcat file             # Rainbow output
cmatrix                 # Matrix effect
sl                      # Steam locomotive

# Productivity
tldr command            # Simplified help
cheat command           # Command cheatsheets
speedtest-cli           # Internet speed test
youtube-dl URL          # Download videos
http --download URL     # Download with progress""")
    
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("\n⚡ QUICK REFERENCE CARDS:")
    sections["SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE"].append("""# Git shortcuts
gst  = git status
gco  = git checkout
gc   = git commit
gp   = git push
gl   = git pull
glog = git log --oneline --graph

# Docker shortcuts
dps  = docker ps
dpsi = docker ps -a
dim  = docker images
dlog = docker logs -f
dex  = docker exec -it

# Kubernetes shortcuts
k   = kubectl
kgp = kubectl get pods
kdp = kubectl describe pod
kl  = kubectl logs -f
ke  = kubectl exec -it""")
    
    # ============================================================================
    # SECTION 14: PDF CHEATSHEET INFO
    # ============================================================================
    sections["PDF CHEATSHEET INFO"] = []
    sections["PDF CHEATSHEET INFO"].append("="*20 + " PDF CHEATSHEET " + "="*20)
    sections["PDF CHEATSHEET INFO"].append(f"\n trying to generate a comprehensive PDF cheatsheet:")
    sections["PDF CHEATSHEET INFO"].append(f"   Location: {work_dir}/docker_workstation_cheatsheet.pdf")
    sections["PDF CHEATSHEET INFO"].append("\nThe cheatsheet contains:")
    sections["PDF CHEATSHEET INFO"].append("  • Quick start commands")
    sections["PDF CHEATSHEET INFO"].append("  • Essential Docker commands")
    sections["PDF CHEATSHEET INFO"].append("  • Modern tool replacements")
    sections["PDF CHEATSHEET INFO"].append("  • Python development guide")
    sections["PDF CHEATSHEET INFO"].append("  • Git workflow")
    sections["PDF CHEATSHEET INFO"].append("  • VS Code integration")
    sections["PDF CHEATSHEET INFO"].append("  • System monitoring tools")
    sections["PDF CHEATSHEET INFO"].append("  • Troubleshooting tips")
    sections["PDF CHEATSHEET INFO"].append(f"\nTo regenerate the PDF anytime:")
    sections["PDF CHEATSHEET INFO"].append(f"   python docker2ls.py pdf --work-dir {work_dir} --image-tag {image_tag}")
    
    # Return content or print based on parameter
    if return_content:
        return sections
    
    # Original printing behavior
    print("\n" + "="*20 + " DOCKER WORKSTATION: USAGE GUIDE " + "="*20)
    
    # Print all sections
    for section_title, section_lines in sections.items():
        if section_title == "PDF CHEATSHEET INFO":
            continue  # Don't print PDF info in terminal (will print separately)
        
        print(f"\n{section_title}")
        if "SECTION" in section_title:
            print("-" * 40)
        
        for line in section_lines:
            print(line)
    
    print("\n" + "="*20 + " END OF PROFESSIONAL GUIDE " + "="*20)
    
    # Print PDF info separately at the end
    print("\n" + "="*20 + " PDF CHEATSHEET " + "="*20)
    for line in sections["PDF CHEATSHEET INFO"][1:]:  # Skip the header line
        print(line)
    
    return None

def generate_helper_scripts(work_dir: str, image_tag: str, system_user: str = None) -> None:
    """
    Generate comprehensive helper shell scripts for Docker container management.
    
    Creates scripts for:
    - Container lifecycle management
    - Development workflows
    - Monitoring and debugging
    - Project setup templates
    - Backup and maintenance
    - Restore from backups
    """
    
    if system_user is None:
        system_user = getpass.getuser()
    
    container_name = image_tag.split(":")[0].replace("/", "_")
    image_name = image_tag.split(":")[0]
    tag = image_tag.split(":")[1] if ":" in image_tag else "latest"
    
    # Create scripts directory structure
    scripts_dir = os.path.join(work_dir, ".scripts")
    os.makedirs(scripts_dir, exist_ok=True)
    
    # Create subdirectories
    subdirs = ["templates", "examples", "backups", "logs"]
    for subdir in subdirs:
        os.makedirs(os.path.join(scripts_dir, subdir), exist_ok=True)
    
    print(f"\n📜 GENERATING HELPER SCRIPTS in {scripts_dir}/")
    print("-" * 50)
    
    # ============================================================================
    # 1. BASIC CONTAINER MANAGEMENT SCRIPTS
    # ============================================================================
    
    # 1.1 Run container (basic)
    run_script = os.path.join(scripts_dir, "01_run_basic.sh")
    run_content = f"""#!/bin/bash
# 01_run_basic.sh - Basic container startup
echo "Starting basic container: {container_name}"

docker run -it --name {container_name} \\
    -v {work_dir}:/workspace \\
    {image_tag}

echo "Container {container_name} started"
"""
    write_script(run_script, run_content)
    
    # 1.2 Run container (advanced development)
    run_advanced = os.path.join(scripts_dir, "02_run_advanced.sh")
    run_advanced_content = f"""#!/bin/bash
# 02_run_advanced.sh - Advanced development container with all features
echo "Starting advanced development container"

# Check if container already exists
if docker ps -a --format "{{{{.Names}}}}" | grep -q "^{container_name}$"; then
    echo "Container {container_name} already exists. Removing..."
    docker stop {container_name} 2>/dev/null
    docker rm {container_name} 2>/dev/null
fi

# Advanced run command with all features
docker run -dit --name {container_name} \\
    --hostname {container_name}-dev \\
    --restart unless-stopped \\
    --memory="4g" \\
    --cpus="2.0" \\
    --shm-size="1g" \\
    -v {work_dir}:/workspace \\
    -v {work_dir}/.cache:/home/{system_user}/.cache \\
    -v {work_dir}/.config:/home/{system_user}/.config \\
    -v ~/.ssh:/home/{system_user}/.ssh:ro \\
    -v ~/.gitconfig:/home/{system_user}/.gitconfig:ro \\
    -v ~/.aws:/home/{system_user}/.aws:ro \\
    -v /var/run/docker.sock:/var/run/docker.sock \\
    -e TERM=xterm-256color \\
    -e LANG=C.UTF-8 \\
    -e PYTHONPATH=/workspace \\
    -p 8888:8888 \\
    -p 8080:8080 \\
    -p 3000:3000 \\
    --add-host=host.docker.internal:host-gateway \\
    {image_tag}

echo "Advanced container started"
echo "Ports: 8888(Jupyter), 8080(Web), 3000(Node)"
echo "Use: ./03_exec.sh to enter container"
"""
    write_script(run_advanced, run_advanced_content)
    
    # 1.3 Execute into running container
    exec_script = os.path.join(scripts_dir, "03_exec.sh")
    exec_content = f"""#!/bin/bash
# 03_exec.sh - Enter running container with bash
echo "Entering container: {container_name}"

# Check if container is running
if ! docker ps --format "{{{{.Names}}}}" | grep -q "^{container_name}$"; then
    echo "Container is not running. Starting it first..."
    docker start {container_name}
    sleep 2
fi

docker exec -it {container_name} bash
"""
    write_script(exec_script, exec_content)
    
    # 1.4 Start existing container
    start_script = os.path.join(scripts_dir, "04_start.sh")
    start_content = f"""#!/bin/bash
# 04_start.sh - Start existing container
echo "Starting container: {container_name}"

if docker ps -a --format "{{{{.Names}}}}" | grep -q "^{container_name}$"; then
    docker start -ai {container_name}
else
    echo "❌ Container {container_name} not found"
    echo "Run ./01_run_basic.sh or ./02_run_advanced.sh first"
fi
"""
    write_script(start_script, start_content)
    
    # ============================================================================
    # 2. DEVELOPMENT WORKFLOW SCRIPTS
    # ============================================================================
    
    # 2.1 Python development environment setup
    python_setup = os.path.join(scripts_dir, "05_setup_python_project.sh")
    python_setup_content = r"""#!/bin/bash
# 05_setup_python_project.sh - Setup Python project template
echo "Setting up Python project template"

PROJECT_NAME=${{1:-"my_project"}}
PROJECT_DIR="/workspace/$PROJECT_NAME"

echo "Creating project: $PROJECT_NAME in $PROJECT_DIR"

docker exec {container_name} bash -c "
mkdir -p $PROJECT_DIR/{{src,tests,docs,data,notebooks}}
cd $PROJECT_DIR

# Create README
cat > README.md << 'EOF'
# $PROJECT_NAME

## Project Structure
- src/ - Source code
- tests/ - Test files
- docs/ - Documentation
- data/ - Datasets
- notebooks/ - Jupyter notebooks

## Setup
\`\`\`bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Core dependencies
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0

# Development tools
black>=23.0.0
flake8>=6.0.0
pytest>=7.0.0
pytest-cov>=4.0.0
jupyter>=1.0.0

# Project specific
py2ls[slim]>=1.0.0
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Jupyter
.ipynb_checkpoints/

# Data
data/raw/
data/processed/

# IDE
.vscode/
.idea/
*.swp
*.swo
EOF

# Create sample Python file
cat > src/__init__.py << 'EOF'
"$PROJECT_NAME package"
__version__ = '0.1.0'
EOF

cat > src/main.py << 'EOF'
"Main module for $PROJECT_NAME"
import pandas as pd
import numpy as np

def hello_world():
    "Simple test function"
    return f'Hello from $PROJECT_NAME!'

if __name__ == '__main__':
    print(hello_world())
EOF

# Create test file
cat > tests/test_basic.py << 'EOF'
"Basic tests for $PROJECT_NAME"
from src.main import hello_world

def test_hello_world():
    "Test hello_world function"
    result = hello_world()
    assert 'Hello' in result
    assert '$PROJECT_NAME' in result
EOF

echo 'Python project template created'
"

echo "Project created at: {work_dir}/$PROJECT_NAME"
echo "Next steps:"
echo "   1. ./03_exec.sh to enter container"
echo "   2. cd /workspace/$PROJECT_NAME"
echo "   3. python -m venv venv"
echo "   4. source venv/bin/activate"
echo "   5. pip install -r requirements.txt"
"""
    write_script(python_setup, python_setup_content)
    
    # 2.2 Jupyter notebook setup
    jupyter_script = os.path.join(scripts_dir, "06_start_jupyter.sh")
    jupyter_content = f"""#!/bin/bash
# 06_start_jupyter.sh - Start Jupyter Lab/Notebook
echo "Starting Jupyter server..."

# Check if container is running
if ! docker ps --format "{{{{.Names}}}}" | grep -q "^{container_name}$"; then
    echo "Container not running. Starting it first..."
    ./04_start.sh
fi

echo "Jupyter will be available at:"
echo "   🔗 Local: http://localhost:8888"
echo "   🔗 Network: http://$(hostname -I | awk '{{print $1}}'):8888"
echo ""
echo "Starting Jupyter Lab..."

docker exec -d {container_name} \\
    bash -c "jupyter lab \\
        --ip=0.0.0.0 \\
        --port=8888 \\
        --no-browser \\
        --notebook-dir=/workspace \\
        --allow-root \\
        --NotebookApp.token='' \\
        --NotebookApp.password=''"

sleep 2
echo "Jupyter Lab started"
echo "To view logs: docker logs {container_name} | grep jupyter"
echo "🛑 To stop: docker exec {container_name} pkill jupyter"
"""
    write_script(jupyter_script, jupyter_content)
    
    # 2.3 Run tests in container
    test_script = os.path.join(scripts_dir, "07_run_tests.sh")
    test_content = f"""#!/bin/bash
# 07_run_tests.sh - Run Python tests in container
echo "Running tests..."

PROJECT_DIR=${{1:-"."}}
FULL_PATH="/workspace/$PROJECT_DIR"

echo "Testing directory: $FULL_PATH"

docker exec {container_name} bash -c "
if [ -d \"$FULL_PATH\" ]; then
    cd \"$FULL_PATH\"
    
    # Check for virtual environment
    if [ -f \"venv/bin/activate\" ]; then
        source venv/bin/activate
    fi
    
    # Run tests
    echo 'Running pytest...'
    python -m pytest tests/ -v
    
    # Run with coverage if available
    if python -c \"import pytest_cov\" 2>/dev/null; then
        echo 'Running coverage...'
        python -m pytest tests/ --cov=src --cov-report=term-missing
    fi
    
    # Linting
    echo 'Running flake8...'
    python -m flake8 src/ --max-line-length=88
    
    # Formatting check
    echo 'Checking formatting...'
    python -m black --check src/ tests/
    
else
    echo \"❌ Directory $FULL_PATH not found\"
fi
"
"""
    write_script(test_script, test_content)
    
    # ============================================================================
    # 3. MONITORING AND DEBUGGING SCRIPTS
    # ============================================================================
    
    # 3.1 Container status and monitoring
    status_script = os.path.join(scripts_dir, "08_container_status.sh")
    status_content = f"""#!/bin/bash
# 08_container_status.sh - Check container status and resources
echo "Container Status: {container_name}"
echo "=" * 50

# Basic info
echo "Basic Information:"
docker ps -a --filter "name={container_name}" --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}\\t{{.Image}}"

echo ""
echo "Resource Usage:"
docker stats {container_name} --no-stream --format "table {{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}\\t{{.MemPerc}}\\t{{.NetIO}}"

echo ""
echo "Logs (last 10 lines):"
docker logs {container_name} --tail 10

echo ""
echo "Container Details:"
docker inspect {container_name} --format '
ID: {{.Id}}
Image: {{.Config.Image}}
User: {{.Config.User}}
Hostname: {{.Config.Hostname}}
Workdir: {{.Config.WorkingDir}}
Entrypoint: {{.Config.Entrypoint}}
Cmd: {{.Config.Cmd}}
Mounts:
{{range .Mounts}}   📍 {{.Source}} -> {{.Destination}} ({{.Type}})
{{end}}'

echo ""
echo "Network Info:"
docker inspect {container_name} --format '{{range .NetworkSettings.Networks}}IP: {{.IPAddress}}
Gateway: {{.Gateway}}
{{end}}'
"""
    write_script(status_script, status_content)
    
    # 3.2 Container logs with follow
    logs_script = os.path.join(scripts_dir, "09_follow_logs.sh")
    logs_content = f"""#!/bin/bash
# 09_follow_logs.sh - Follow container logs in real-time
echo "Following logs for: {container_name}"
echo "🛑 Press Ctrl+C to stop"
echo "-" * 50

docker logs {container_name} --follow
"""
    write_script(logs_script, logs_content)
    
    # ============================================================================
    # 4. BACKUP AND RESTORE SCRIPTS
    # ============================================================================
    
    # 4.1 Backup container data - FIXED VERSION
    backup_script = os.path.join(scripts_dir, "10_backup_workspace.sh")
    # Use double {{ to escape { in f-strings, and handle $ properly
    backup_content = '''#!/bin/bash
# 10_backup_workspace.sh - Backup workspace to tar archive
echo "Creating backup..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="''' + work_dir + '''/.scripts/backups"
LOG_DIR="''' + work_dir + '''/.scripts/logs"
BACKUP_FILE="$BACKUP_DIR/workspace_backup_$TIMESTAMP.tar.gz"
BACKUP_LOG="$LOG_DIR/backup_$TIMESTAMP.log"

mkdir -p "$BACKUP_DIR"
mkdir -p "$LOG_DIR"
echo "Backing up {work_dir} to $BACKUP_FILE"
echo "Log: $BACKUP_LOG"

{
    echo "=== BACKUP STARTED at $(date) ==="
    echo "Source: ''' + work_dir + '''"
    echo "Destination: $BACKUP_FILE"
    echo ""
    
    # List what will be backed up
    echo "Files to be backed up:"
    find ''' + work_dir + ''' -type f -name "*.py" -o -name "*.md" -o -name "*.txt" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" | head -20
    echo "... and others"
    echo ""
    
    # Create backup using tar with progress
    echo "Creating tar archive..."
    tar -czvf "$BACKUP_FILE" \\
        -C ''' + work_dir + ''' \\
        --exclude=".scripts/backups" \\
        --exclude=".scripts/logs" \\
        --exclude=".cache" \\
        --exclude="__pycache__" \\
        --exclude="*.pyc" \\
        --exclude="*.log" \\
        --exclude="node_modules" \\
        --exclude=".git" \\
        --exclude=".venv" \\
        --exclude="venv" \\
        --exclude=".env" \\
        .
    
    # Calculate size
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    FILE_COUNT=$(tar -tzf "$BACKUP_FILE" | wc -l)
    
    echo ""
    echo "Backup completed!"
    echo "Backup size: $SIZE"
    echo "Files backed up: $FILE_COUNT"
    echo "Backup location: $BACKUP_FILE"
    
    # Generate checksum
    echo ""
    echo "Generating checksums..."
    md5sum "$BACKUP_FILE" > "$BACKUP_FILE.md5"
    sha256sum "$BACKUP_FILE" > "$BACKUP_FILE.sha256"
    
    echo "MD5: $(cat $BACKUP_FILE.md5)"
    echo "SHA256: $(cat $BACKUP_FILE.sha256)"
    
    echo ""
    echo "Available backups:"
    ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -10
    
    echo ""
    echo "To restore: ./11_restore_workspace.sh $BACKUP_FILE"
    echo "=== BACKUP COMPLETED at $(date) ==="
} 2>&1 | tee "$BACKUP_LOG"

echo ""
echo "Backup summary saved to: $BACKUP_LOG"
'''
    write_script(backup_script, backup_content)
    
    # 4.2 RESTORE from backup - FIXED VERSION
    restore_script = os.path.join(scripts_dir, "11_restore_workspace.sh")
    restore_content = '''#!/bin/bash
# 11_restore_workspace.sh - Restore workspace from backup
echo "RESTORE WORKSPACE FROM BACKUP"
echo "=" * 60

BACKUP_FILE="${1:-}"

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ Usage: $0 <backup_file.tar.gz>"
    echo ""
    echo "Available backups:"
    ls -lh ''' + work_dir + '''/.scripts/backups/*.tar.gz 2>/dev/null | nl -v 0
    echo ""
    echo "Example: $0 ''' + work_dir + '''/.scripts/backups/workspace_backup_20240101_120000.tar.gz"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "Restoring from: $BACKUP_FILE"
echo "Target directory: ''' + work_dir + '''"
echo ""

# Verify backup file
echo "Verifying backup file..."
if ! tar -tzf "$BACKUP_FILE" >/dev/null 2>&1; then
    echo "❌ Invalid backup file or corrupted archive"
    exit 1
fi

# Check checksums if available
if [ -f "$BACKUP_FILE.md5" ]; then
    echo "Verifying MD5 checksum..."
    if ! md5sum -c "$BACKUP_FILE.md5" >/dev/null 2>&1; then
        echo "MD5 checksum verification failed (file may be corrupted)"
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

if [ -f "$BACKUP_FILE.sha256" ]; then
    echo "Verifying SHA256 checksum..."
    if ! sha256sum -c "$BACKUP_FILE.sha256" >/dev/null 2>&1; then
        echo "SHA256 checksum verification failed (file may be corrupted)"
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Show what\'s in the backup
echo ""
echo "Contents of backup:"
tar -tzf "$BACKUP_FILE" | head -20
echo "... (and more)"
FILE_COUNT=$(tar -tzf "$BACKUP_FILE" | wc -l)
echo "Total files: $FILE_COUNT"
echo ""

# Ask for confirmation
echo "WARNING ⚠️"
echo "This will RESTORE files to: ''' + work_dir + '''"
echo "Existing files may be OVERWRITTEN!"
echo ""
read -p "Are you sure you want to continue? (type \'YES\' to confirm): " -r
echo
if [[ ! $REPLY == "YES" ]]; then
    echo "❌ Restore cancelled"
    exit 1
fi

# Create restore log
RESTORE_LOG="''' + work_dir + '''/.scripts/logs/restore_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$RESTORE_LOG")"

echo "Starting restore at $(date)" | tee "$RESTORE_LOG"
echo "Backup: $BACKUP_FILE" | tee -a "$RESTORE_LOG"
echo "Target: ''' + work_dir + '''" | tee -a "$RESTORE_LOG"
echo "" | tee -a "$RESTORE_LOG"

# Stop container if running
if docker ps --format "{{.Names}}" | grep -q "^''' + container_name + '''$"; then
    echo "🛑 Stopping container ''' + container_name + '''..." | tee -a "$RESTORE_LOG"
    docker stop ''' + container_name + ''' | tee -a "$RESTORE_LOG"
fi

# Create pre-restore backup
PRE_RESTORE_BACKUP="''' + work_dir + '''/.scripts/backups/pre_restore_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
echo "Creating pre-restore backup..." | tee -a "$RESTORE_LOG"
tar -czf "$PRE_RESTORE_BACKUP" -C ''' + work_dir + ''' . 2>/dev/null
echo "Pre-restore backup: $PRE_RESTORE_BACKUP" | tee -a "$RESTORE_LOG"

# Extract backup
echo "" | tee -a "$RESTORE_LOG"
echo "Extracting backup..." | tee -a "$RESTORE_LOG"

# Create temporary directory for extraction
TEMP_DIR=$(mktemp -d)
echo "Temp dir: $TEMP_DIR" | tee -a "$RESTORE_LOG"

# Extract to temp dir first
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR" | tee -a "$RESTORE_LOG"

# Compare and copy
echo "" | tee -a "$RESTORE_LOG"
echo "Comparing files..." | tee -a "$RESTORE_LOG"

# List what will be restored
echo "Files to be restored:" | tee -a "$RESTORE_LOG"
find "$TEMP_DIR" -type f | sed "s|^$TEMP_DIR/||" | tee -a "$RESTORE_LOG"

# Copy files
echo "" | tee -a "$RESTORE_LOG"
echo "Copying files to ''' + work_dir + '''..." | tee -a "$RESTORE_LOG"
rsync -av --progress "$TEMP_DIR/" "''' + work_dir + '''/" | tee -a "$RESTORE_LOG"

# Cleanup temp dir
rm -rf "$TEMP_DIR"

# Fix permissions
echo "" | tee -a "$RESTORE_LOG"
echo "Fixing permissions..." | tee -a "$RESTORE_LOG"
chmod -R u+rwX,go+rX,go-w "''' + work_dir + '''" 2>/dev/null | tee -a "$RESTORE_LOG"

# Restart container
echo "" | tee -a "$RESTORE_LOG"
echo "Restarting container ''' + container_name + '''..." | tee -a "$RESTORE_LOG"
docker start ''' + container_name + ''' | tee -a "$RESTORE_LOG"

echo "" | tee -a "$RESTORE_LOG"
echo "Restore completed successfully!" | tee -a "$RESTORE_LOG"
echo "Log saved to: $RESTORE_LOG" | tee -a "$RESTORE_LOG"
echo "Pre-restore backup: $PRE_RESTORE_BACKUP" | tee -a "$RESTORE_LOG"
echo "" | tee -a "$RESTORE_LOG"
echo "🎯 Next steps:" | tee -a "$RESTORE_LOG"
echo "   1. Verify restored files in ''' + work_dir + '''" | tee -a "$RESTORE_LOG"
echo "   2. Run: ./03_exec.sh to enter container" | tee -a "$RESTORE_LOG"
echo "   3. Check if everything works correctly" | tee -a "$RESTORE_LOG"
echo "" | tee -a "$RESTORE_LOG"
echo "Restore finished at $(date)" | tee -a "$RESTORE_LOG"
'''
    write_script(restore_script, restore_content)
    
    # 4.3 List and manage backups - FIXED VERSION
    list_backups_script = os.path.join(scripts_dir, "12_list_backups.sh")
    list_backups_content = '''#!/bin/bash
# 12_list_backups.sh - List and manage backups
echo "BACKUP MANAGEMENT"
echo "=" * 60

BACKUP_DIR="''' + work_dir + '''/.scripts/backups"
LOG_DIR="''' + work_dir + '''/.scripts/logs"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup directory not found: $BACKUP_DIR"
    echo "Run ./10_backup_workspace.sh first to create backups"
    exit 1
fi

echo "Storage Information:"
echo "Backup directory: $BACKUP_DIR"
echo "Log directory: $LOG_DIR"
echo ""

# Show disk usage
echo "Disk Usage:"
du -sh "$BACKUP_DIR" 2>/dev/null
du -sh "$LOG_DIR" 2>/dev/null
echo ""

# List backups with details
echo "AVAILABLE BACKUPS:"
echo "----------------------------------------------------------------"
printf "%-4s %-20s %-10s %-10s %s\\n" "#" "Date/Time" "Size" "Files" "Backup File"
echo "----------------------------------------------------------------"

count=0
for backup in "$BACKUP_DIR"/workspace_backup_*.tar.gz; do
    if [ -f "$backup" ]; then
        count=$((count + 1))
        
        # Extract timestamp from filename
        filename=$(basename "$backup")
        timestamp=$(echo "$filename" | sed 's/workspace_backup_\\(.*\\)\\.tar\\.gz/\\1/')
        
        # Format timestamp for display
        if [[ $timestamp =~ ^[0-9]{8}_[0-9]{6}$ ]]; then
            display_time="${timestamp:0:4}-${timestamp:4:2}-${timestamp:6:2} ${timestamp:9:2}:${timestamp:11:2}:${timestamp:13:2}"
        else
            display_time="$timestamp"
        fi
        
        # Get file size
        size=$(du -h "$backup" | cut -f1)
        
        # Count files in backup
        files=$(tar -tzf "$backup" 2>/dev/null | wc -l)
        
        printf "%-4s %-20s %-10s %-10s %s\\n" "$count" "$display_time" "$size" "$files" "$filename"
    fi
done

if [ $count -eq 0 ]; then
    echo "No backups found"
    echo "Run: ./10_backup_workspace.sh to create your first backup"
else
    echo "----------------------------------------------------------------"
    echo "Total backups: $count"
    echo ""
    
    # Show restore options
    echo "RESTORE OPTIONS:"
    echo "   To restore a backup, use:"
    echo "   ./11_restore_workspace.sh <backup_file>"
    echo ""
    echo "   Example:"
    echo "   ./11_restore_workspace.sh $BACKUP_DIR/workspace_backup_20240101_120000.tar.gz"
    echo ""
    
    # Show verification options
    echo "VERIFICATION OPTIONS:"
    echo "   To verify a backup:"
    echo "   md5sum -c <backup_file>.md5"
    echo "   sha256sum -c <backup_file>.sha256"
    echo ""
    
    # Show cleanup options
    echo "🧹 CLEANUP OPTIONS:"
    echo "   To remove old backups (keep last 10):"
    echo "   ls -t $BACKUP_DIR/workspace_backup_*.tar.gz | tail -n +11 | xargs rm -f"
fi

echo ""
echo "RECENT BACKUP LOGS:"
ls -lt "$LOG_DIR"/backup_*.log 2>/dev/null | head -5
'''
    write_script(list_backups_script, list_backups_content)
    
    # 4.4 Cleanup old backups - FIXED VERSION
    cleanup_backups_script = os.path.join(scripts_dir, "13_cleanup_backups.sh")
    cleanup_backups_content = '''#!/bin/bash
# 13_cleanup_backups.sh - Cleanup old backups automatically
echo "🧹 CLEANUP OLD BACKUPS"
echo "=" * 60

BACKUP_DIR="''' + work_dir + '''/.scripts/backups"
LOG_DIR="''' + work_dir + '''/.scripts/logs"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup directory not found: $BACKUP_DIR"
    exit 1
fi

echo "Current backup status:"
total_backups=$(ls "$BACKUP_DIR"/workspace_backup_*.tar.gz 2>/dev/null | wc -l)
total_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)

echo "   Total backups: $total_backups"
echo "   Total size: $total_size"
echo ""

# Ask how many to keep
read -p "How many backups to keep? (default: 10): " KEEP_COUNT
KEEP_COUNT="${KEEP_COUNT:-10}"

if ! [[ "$KEEP_COUNT" =~ ^[0-9]+$ ]]; then
    echo "❌ Invalid number"
    exit 1
fi

echo ""
echo "Will keep the latest $KEEP_COUNT backups"
echo ""

# List what will be deleted
echo "🗑️ Backups to be deleted:"
ls -t "$BACKUP_DIR"/workspace_backup_*.tar.gz 2>/dev/null | tail -n +$((KEEP_COUNT + 1)) | while read backup; do
    if [ -f "$backup" ]; then
        size=$(du -h "$backup" | cut -f1)
        filename=$(basename "$backup")
        echo "   $filename ($size)"
    fi
done

to_delete=$(ls -t "$BACKUP_DIR"/workspace_backup_*.tar.gz 2>/dev/null | tail -n +$((KEEP_COUNT + 1)) | wc -l)

if [ $to_delete -eq 0 ]; then
    echo ""
    echo "No backups to delete (already have $total_backups backups)"
    exit 0
fi

echo ""
echo "Total backups to delete: $to_delete"
echo ""

# Ask for confirmation
read -p "Are you sure you want to delete these backups? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cleanup cancelled"
    exit 0
fi

echo ""
echo "🗑️  Deleting old backups..."
deleted_count=0
deleted_size=0

ls -t "$BACKUP_DIR"/workspace_backup_*.tar.gz 2>/dev/null | tail -n +$((KEEP_COUNT + 1)) | while read backup; do
    if [ -f "$backup" ]; then
        size=$(du -k "$backup" | cut -f1)
        filename=$(basename "$backup")
        
        # Delete backup file
        rm -f "$backup"
        
        # Delete checksum files if they exist
        rm -f "$backup.md5" 2>/dev/null
        rm -f "$backup.sha256" 2>/dev/null
        
        deleted_count=$((deleted_count + 1))
        deleted_size=$((deleted_size + size))
        
        echo "   Deleted: $filename"
    fi
done

# Also cleanup old logs (keep last 50)
echo ""
echo "Cleaning up old logs..."
ls -t "$LOG_DIR"/backup_*.log 2>/dev/null | tail -n +51 | xargs rm -f 2>/dev/null
ls -t "$LOG_DIR"/restore_*.log 2>/dev/null | tail -n +51 | xargs rm -f 2>/dev/null

# Convert size to human readable
deleted_size_mb=$((deleted_size / 1024))

echo ""
echo "Cleanup completed!"
echo "Results:"
echo "   Backups deleted: $deleted_count"
echo "   Space freed: ~${deleted_size_mb} MB"
echo ""
echo "Remaining backups:"
ls -lh "$BACKUP_DIR"/workspace_backup_*.tar.gz 2>/dev/null
'''
    write_script(cleanup_backups_script, cleanup_backups_content)
    
    # 4.5 Cleanup Docker resources (updated to 14)
    cleanup_docker_script = os.path.join(scripts_dir, "14_cleanup_docker.sh")
    cleanup_docker_content = r"""#!/bin/bash
# 14_cleanup_docker.sh - Cleanup Docker resources
echo "🧹 Cleaning up Docker resources"

echo "Current status:"
docker system df

echo ""
read -p "❓ Remove stopped containers? (y/n): " -n 1 -r
echo
if [[ \$REPLY =~ ^[Yy]$ ]]; then
    docker container prune -f
fi

echo ""
read -p "❓ Remove dangling images? (y/n): " -n 1 -r
echo
if [[ \$REPLY =~ ^[Yy]$ ]]; then
    docker image prune -f
fi

echo ""
read -p "❓ Remove unused volumes? (y/n): " -n 1 -r
echo
if [[ \$REPLY =~ ^[Yy]$ ]]; then
    docker volume prune -f
fi

echo ""
read -p "❓ Remove build cache? (y/n): " -n 1 -r
echo
if [[ \$REPLY =~ ^[Yy]$ ]]; then
    docker builder prune -a -f
fi

echo ""
echo "Cleanup complete. Final status:"
docker system df
"""
    write_script(cleanup_docker_script, cleanup_docker_content)
    
    # 4.6 Stop and remove container (updated to 15)
    remove_script = os.path.join(scripts_dir, "15_stop_remove.sh")
    remove_content = r"""#!/bin/bash
# 15_stop_remove.sh - Stop and remove container
echo "🛑 Stopping and removing container: {container_name}"

# Backup before removal
read -p "Create backup before removing container? (y/n): " -n 1 -r
echo
if [[ \$REPLY =~ ^[Yy]$ ]]; then
    ./10_backup_workspace.sh
fi

# Stop container if running
if docker ps --format "{{{{.Names}}}}" | grep -q "^{container_name}$"; then
    echo "⏹️  Stopping container..."
    docker stop {container_name}
    echo "Container stopped"
fi

# Remove container if exists
if docker ps -a --format "{{{{.Names}}}}" | grep -q "^{container_name}$"; then
    echo "🗑️  Removing container..."
    docker rm {container_name}
    echo "Container removed"
else
    echo "ℹ️  Container {container_name} not found"
fi

echo ""
echo "Remaining containers:"
docker ps -a --format "table {{.Names}}\\t{{.Status}}\\t{{.Image}}" | head -10
"""
    write_script(remove_script, remove_content)
    
    # ============================================================================
    # 5. TEMPLATE AND EXAMPLE FILES
    # ============================================================================
    
    # Create template files
    templates_dir = os.path.join(scripts_dir, "templates")
    
    # Docker Compose template
    docker_compose_template = os.path.join(templates_dir, "docker-compose.yml")
    docker_compose_content = f"""version: '3.8'

services:
  workspace:
    image: {image_tag}
    container_name: {container_name}
    hostname: {container_name}-dev
    restart: unless-stopped
    volumes:
      - {work_dir}:/workspace
      - {work_dir}/.cache:/home/{system_user}/.cache
      - {work_dir}/.config:/home/{system_user}/.config
      - ~/.ssh:/home/{system_user}/.ssh:ro
      - ~/.gitconfig:/home/{system_user}/.gitconfig:ro
    environment:
      - PYTHONPATH=/workspace
      - PYTHONUNBUFFERED=1
      - TERM=xterm-256color
    ports:
      - "8888:8888"
      - "8080:8080"
      - "3000:3000"
    networks:
      - dev-network
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  postgres:
    image: postgres:15-alpine
    container_name: {container_name}-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=developer
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=development
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - dev-network

  redis:
    image: redis:7-alpine
    container_name: {container_name}-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    networks:
      - dev-network

networks:
  dev-network:
    driver: bridge

volumes:
  postgres-data:
"""
    
    with open(docker_compose_template, "w") as f:
        f.write(docker_compose_content)
    
    # VS Code devcontainer template
    devcontainer_template = os.path.join(templates_dir, "devcontainer.json")
    devcontainer_content = f"""{{
  "name": "{container_name} Development",
  "dockerComposeFile": "docker-compose.yml",
  "service": "workspace",
  "workspaceFolder": "/workspace",
  "remoteUser": "{system_user}",
  
  "extensions": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "ms-toolsai.jupyter",
    "GitHub.copilot",
    "eamodio.gitlens",
    "charliermarsh.ruff"
  ],
  
  "forwardPorts": [8888, 8080, 5432, 6379],
  
  "containerEnv": {{
    "PYTHONPATH": "/workspace",
    "PYTHONUNBUFFERED": "1"
  }},
  
  "postCreateCommand": "pip install --upgrade pip && echo 'Container ready!'",
  
  "customizations": {{
    "vscode": {{
      "settings": {{
        "python.defaultInterpreterPath": "/usr/bin/python3",
        "python.linting.enabled": true,
        "python.formatting.provider": "black",
        "editor.formatOnSave": true,
        "files.autoSave": "afterDelay"
      }}
    }}
  }}
}}
"""
    
    with open(devcontainer_template, "w") as f:
        f.write(devcontainer_content)
    
    # Backup configuration template
    backup_config_template = os.path.join(templates_dir, "backup_config.json")
    backup_config_content = f"""{{
  "backup_settings": {{
    "backup_dir": "{work_dir}/.scripts/backups",
    "log_dir": "{work_dir}/.scripts/logs",
    "retention_days": 30,
    "max_backups": 10,
    "exclude_patterns": [
      "**/__pycache__/",
      "**/*.pyc",
      "**/.git/",
      "**/node_modules/",
      "**/.venv/",
      "**/venv/",
      "**/.env",
      "**/.cache/",
      "**/.scripts/backups/",
      "**/.scripts/logs/"
    ],
    "include_patterns": [
      "**/*.py",
      "**/*.md",
      "**/*.txt",
      "**/*.json",
      "**/*.yaml",
      "**/*.yml",
      "**/*.ipynb",
      "**/requirements*.txt",
      "**/Dockerfile",
      "**/.gitignore"
    ],
    "schedule": {{
      "daily": "0 2 * * *",
      "weekly": "0 3 * * 0",
      "monthly": "0 4 1 * *"
    }}
  }},
  "restore_settings": {{
    "verify_checksums": true,
    "create_pre_restore_backup": true,
    "stop_container_during_restore": true,
    "fix_permissions_after_restore": true
  }}
}}
"""
    
    with open(backup_config_template, "w") as f:
        f.write(backup_config_content)
    
    # ============================================================================
    # 6. MASTER USAGE SCRIPT (updated)
    # ============================================================================
    
    # Create a master usage script
    master_script = os.path.join(scripts_dir, "00_usage.sh")
    master_content = f"""#!/bin/bash
# 00_usage.sh - Master usage guide for Docker workstation
echo "DOCKER WORKSTATION HELPER SCRIPTS"
echo "=" * 60
echo "Container: {container_name}"
echo "Image: {image_tag}"
echo "Workspace: {work_dir}"
echo "Backup Dir: {work_dir}/.scripts/backups"
echo "=" * 60

cat << 'EOF'

📚 BASIC USAGE EXAMPLES:

1. FIRST-TIME SETUP:
   ./02_run_advanced.sh    # Start container with all features
   ./03_exec.sh            # Enter container with bash

2. DAILY WORKFLOW:
   ./04_start.sh           # Start existing container
   ./03_exec.sh            # Enter container
   ./06_start_jupyter.sh   # Start Jupyter Lab
   ./07_run_tests.sh       # Run tests in project

3. BACKUP & RESTORE:
   ./10_backup_workspace.sh     # Create backup
   ./11_restore_workspace.sh    # Restore from backup
   ./12_list_backups.sh         # List and manage backups
   ./13_cleanup_backups.sh      # Cleanup old backups

4. MONITORING:
   ./08_container_status.sh     # Check container status
   ./09_follow_logs.sh         # Follow logs in real-time

5. 🧹 MAINTENANCE:
   ./14_cleanup_docker.sh      # Cleanup Docker resources
   ./15_stop_remove.sh         # Stop and remove container

6. 🎯 PROJECT SETUP:
   ./05_setup_python_project.sh [project_name]
      # Creates Python project template

QUICK COMMAND REFERENCE:

# Container lifecycle
docker start {container_name}           # Start container
docker exec -it {container_name} bash  # Enter container
docker stop {container_name}           # Stop container
docker rm {container_name}             # Remove container

# Backup & Restore
./10_backup_workspace.sh               # Create backup
./11_restore_workspace.sh backup.tar.gz # Restore backup
./12_list_backups.sh                   # List backups

# Development
docker exec {container_name} python script.py    # Run Python script
docker exec {container_name} jupyter lab --ip=0.0.0.0  # Start Jupyter

# Monitoring
docker logs {container_name}           # View logs
docker stats {container_name}          # Resource usage
docker inspect {container_name}        # Detailed info

FILES AND TEMPLATES:

• templates/docker-compose.yml   - Docker Compose setup
• templates/devcontainer.json    - VS Code Dev Container config
• templates/backup_config.json   - Backup configuration
• backups/                       - Backup archives
• logs/                          - Backup and restore logs

BACKUP WORKFLOW:

1. Regular backups:
   ./10_backup_workspace.sh

2. List backups:
   ./12_list_backups.sh

3. Restore if needed:
   ./11_restore_workspace.sh <backup_file>

4. Cleanup old backups:
   ./13_cleanup_backups.sh

NEXT STEPS:

1. Run ./02_run_advanced.sh to start container
2. Run ./03_exec.sh to enter container
3. Run ./05_setup_python_project.sh myproject
4. Run ./10_backup_workspace.sh to create first backup
5. Access Jupyter at http://localhost:8888

TIPS:
• Backup regularly: Add to cron: 0 2 * * * cd {work_dir} && ./.scripts/10_backup_workspace.sh
• Verify backups: Check checksums before restore
• Test restore: Periodically test restoring from backups
• Monitor disk: Keep an eye on backup directory size

TROUBLESHOOTING:
• Container won't start: ./08_container_status.sh
• Files missing: ./11_restore_workspace.sh
• Disk full: ./13_cleanup_backups.sh
• Docker issues: ./14_cleanup_docker.sh

LOGS:
• Backup logs: {work_dir}/.scripts/logs/backup_*.log
• Restore logs: {work_dir}/.scripts/logs/restore_*.log
EOF
"""
    write_script(master_script, master_content)
    
    # ============================================================================
    # 7. CRON/AUTOMATION SCRIPTS - FIXED VERSION
    # ============================================================================
    
    # Create cron automation script
    cron_script = os.path.join(scripts_dir, "16_setup_cron_backup.sh")
    cron_content = '''#!/bin/bash
# 16_setup_cron_backup.sh - Setup automated backups with cron
echo "⏰ SETUP AUTOMATED BACKUPS WITH CRON"
echo "=" * 60

SCRIPT_PATH="''' + work_dir + '''/.scripts/10_backup_workspace.sh"
LOG_DIR="''' + work_dir + '''/.scripts/logs"
CRON_JOB=""

echo "Backup script: $SCRIPT_PATH"
echo "Log directory: $LOG_DIR"
echo ""

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Backup script not found: $SCRIPT_PATH"
    exit 1
fi

echo "🕐 Select backup frequency:"
echo "   1) Daily (2:00 AM)"
echo "   2) Weekly (Sunday 3:00 AM)"
echo "   3) Monthly (1st of month 4:00 AM)"
echo "   4) Custom schedule"
echo "   5) Remove existing cron jobs"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        CRON_JOB="0 2 * * * cd ''' + work_dir + ''' && $SCRIPT_PATH >> $LOG_DIR/cron_backup.log 2>&1"
        echo "Set to run daily at 2:00 AM"
        ;;
    2)
        CRON_JOB="0 3 * * 0 cd ''' + work_dir + ''' && $SCRIPT_PATH >> $LOG_DIR/cron_backup.log 2>&1"
        echo "Set to run weekly on Sunday at 3:00 AM"
        ;;
    3)
        CRON_JOB="0 4 1 * * cd ''' + work_dir + ''' && $SCRIPT_PATH >> $LOG_DIR/cron_backup.log 2>&1"
        echo "Set to run monthly on 1st at 4:00 AM"
        ;;
    4)
        echo ""
        echo "📅 Enter custom cron schedule (min hour day month weekday):"
        echo "   Example: '0 2 * * *' for daily at 2 AM"
        read -p "Schedule: " custom_schedule
        CRON_JOB="$custom_schedule cd ''' + work_dir + ''' && $SCRIPT_PATH >> $LOG_DIR/cron_backup.log 2>&1"
        echo "Set custom schedule: $custom_schedule"
        ;;
    5)
        echo "🗑️  Removing existing cron jobs..."
        (crontab -l | grep -v "''' + work_dir + '''" | grep -v "$SCRIPT_PATH" | crontab -) 2>/dev/null
        echo "Cron jobs removed"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Cron job to be added:"
echo "   $CRON_JOB"
echo ""

# Ask for confirmation
read -p "Add this cron job? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 0
fi

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo ""
echo "Cron job added successfully!"
echo ""
echo "Current crontab:"
crontab -l
echo ""
echo "To edit/remove manually: crontab -e"
echo "Logs will be saved to: $LOG_DIR/cron_backup.log"
'''
    write_script(cron_script, cron_content)
    
    # Make all scripts executable
    for script in os.listdir(scripts_dir):
        if script.endswith(".sh"):
            os.chmod(os.path.join(scripts_dir, script), 0o755)
    
    # ============================================================================
    # FINAL OUTPUT
    # ============================================================================
    
    print("Generated 17 helper scripts:")
    print("")
    print("BASIC CONTAINER MANAGEMENT:")
    print("   00_usage.sh          - Master usage guide")
    print("   01_run_basic.sh      - Basic container startup")
    print("   02_run_advanced.sh   - Advanced development container")
    print("   03_exec.sh           - Enter container with bash")
    print("   04_start.sh          - Start existing container")
    print("")
    print("DEVELOPMENT WORKFLOW:")
    print("   05_setup_python_project.sh - Python project template")
    print("   06_start_jupyter.sh   - Start Jupyter Lab")
    print("   07_run_tests.sh       - Run Python tests")
    print("")
    print("BACKUP & RESTORE:")
    print("   10_backup_workspace.sh - Create backup with checksums")
    print("   11_restore_workspace.sh - Restore from backup")
    print("   12_list_backups.sh    - List and manage backups")
    print("   13_cleanup_backups.sh - Cleanup old backups")
    print("")
    print("MONITORING & DEBUGGING:")
    print("   08_container_status.sh - Container status and resources")
    print("   09_follow_logs.sh     - Follow logs in real-time")
    print("")
    print("🧹 MAINTENANCE:")
    print("   14_cleanup_docker.sh  - Cleanup Docker resources")
    print("   15_stop_remove.sh     - Stop and remove container")
    print("   16_setup_cron_backup.sh - Setup automated backups")
    print("")
    print("TEMPLATES:")
    print("   templates/docker-compose.yml - Multi-service setup")
    print("   templates/devcontainer.json  - VS Code configuration")
    print("   templates/backup_config.json - Backup configuration")
    print("")
    print("QUICK START:")
    print(f"   cd {work_dir}")
    print("   ./.scripts/00_usage.sh      # View full usage guide")
    print("   ./.scripts/02_run_advanced.sh  # Start container")
    print("   ./.scripts/10_backup_workspace.sh # First backup")
    print("")
    print("BACKUP WORKFLOW EXAMPLE:")
    print("   1. ./scripts/10_backup_workspace.sh  # Create backup")
    print("   2. ./scripts/12_list_backups.sh     # List backups")
    print("   3. # ... work for a while ...")
    print("   4. ./scripts/11_restore_workspace.sh backups/workspace_backup_*.tar.gz")
    print("")
    print("⏰ AUTOMATED BACKUPS:")
    print("   ./scripts/16_setup_cron_backup.sh  # Setup scheduled backups")
    print("")
    print("SECURITY FEATURES:")
    print("   • Checksum verification (MD5, SHA256)")
    print("   • Pre-restore backups")
    print("   • Logging for all operations")
    print("   • Confirmation prompts")
    print("   • Permission fixing")


def write_script(filepath: str, content: str) -> None:
    """Write script content to file and make executable."""
    with open(filepath, "w") as f:
        f.write(content)
    os.chmod(filepath, 0o755)

def load_config(config_file: str) -> Dict:
    """Load configuration from JSON file."""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load config file {config_file}: {e}")
        return {}

def get_dockerhub_username() -> str:
    """
    Get Docker Hub username using multiple fallback methods.
    Returns the username or a default placeholder.
    """
    username = None
    
    # Method 1: Check docker config file (most reliable)
    try:
        # Docker config is usually at ~/.docker/config.json
        docker_config_path = Path.home() / ".docker" / "config.json"
        if docker_config_path.exists():
            with open(docker_config_path, 'r') as f:
                config = json.load(f)
                
            # Check for auths (older format)
            if "auths" in config:
                for registry in config["auths"]:
                    if "https://index.docker.io/v1/" in registry or "docker.io" in registry:
                        # Extract username from auth token
                        auth = config["auths"][registry].get("auth", "")
                        if auth:
                            import base64
                            try:
                                decoded = base64.b64decode(auth).decode('utf-8')
                                username = decoded.split(':')[0]
                                break
                            except:
                                pass
    
    except (json.JSONDecodeError, KeyError, IOError) as e:
        print(f"Warning: Could not read Docker config: {e}")
    
    # Method 2: Try to get from environment variable
    if not username:
        username = os.environ.get('DOCKERHUB_USERNAME')
    
    # Method 3: Try to get from docker login command output
    if not username:
        try:
            # Try to get username from whoami command against Docker Hub
            result = subprocess.run(
                ["docker", "login", "--username", "DUMMY", "--password-stdin"],
                input="dummy\n",
                capture_output=True,
                text=True,
                timeout=5
            )
            # Parse error message which often contains current username
            if "you are logged in as" in result.stderr.lower():
                import re
                match = re.search(r'logged in as (\w+)', result.stderr, re.IGNORECASE)
                if match:
                    username = match.group(1)
        except:
            pass
    
    # Method 4: Try docker system info (some versions store it)
    if not username:
        try:
            result = subprocess.run(
                ["docker", "system", "info", "--format", "{{json .}}"],
                capture_output=True,
                text=True,
                check=True
            )
            info = json.loads(result.stdout)
            # Some Docker versions store registry username
            if "RegistryConfig" in info and "IndexConfigs" in info["RegistryConfig"]:
                for registry in info["RegistryConfig"]["IndexConfigs"]:
                    if "docker.io" in registry or "index.docker.io" in registry:
                        username = info["RegistryConfig"]["IndexConfigs"][registry].get("Name")
                        break
        except:
            pass
    
    # Method 5: Check if we can get it from a test push/pull (if we have an image)
    if not username:
        try:
            # Try to inspect a local image's metadata
            result = subprocess.run(
                ["docker", "images", "--format", "{{.Repository}}"],
                capture_output=True,
                text=True
            )
            if result.stdout:
                # Look for images with Docker Hub format (username/image)
                for line in result.stdout.strip().split('\n'):
                    if '/' in line and not line.startswith('localhost/'):
                        potential_user = line.split('/')[0]
                        # Check if this looks like a valid username (not a registry URL)
                        if '.' not in potential_user and ':' not in potential_user:
                            username = potential_user
                            break
        except:
            pass
    
    # Method 6: Check .npmrc or other config files that might contain Docker Hub username
    if not username:
        try:
            # Some users store it in .npmrc for npm packages on Docker Hub
            npmrc_path = Path.home() / ".npmrc"
            if npmrc_path.exists():
                with open(npmrc_path, 'r') as f:
                    content = f.read()
                    # Look for Docker Hub registry config
                    import re
                    match = re.search(r'//registry\.npmjs\.org/:_authToken=(\w+)', content)
                    if match:
                        # Sometimes npm username matches Docker Hub
                        username = match.group(1)
        except:
            pass
    
    # Final fallback: Use environment username or default
    if not username:
        username = os.environ.get('USER') or os.environ.get('USERNAME') or 'dockerhub_username'
    
    return username
# Example usage function
def setup_example_workstation():
    """Example usage of the setup function."""
    
    # Basic setup
    print("Setting up basic workstation...")
    result = setup_docker_workstation(
        work_dir="~/my-dev-workspace",
        image_tag="my-dev:latest",
        additional_packages=["nodejs", "npm", "build-essential"],
        pip_packages=["py2ls[slim]"],
        skip_build=False
    )
    
    if result["success"]:
        print("\nSetup completed successfully!")
        print(f"Workspace: {result['work_dir']}")
        print(f"Image: {result['image_tag']}")
        
        # You could also load from config
        print("\nTo load from saved config next time:")
        print(f"setup_docker_workstation(config_file='{result['work_dir']}/workspace_config.json')")

def tester(
    image_tag: str = "py2ls:latest",
    work_dir: str = "~/workstation",
    test_script: str = None,
    interactive: bool = False,
    cleanup: bool = False
) -> Dict[str, Union[bool, str]]:
    """
    Docker instructor: Test your Docker setup step-by-step.
    
    Walks through:
    1. Starting the container correctly
    2. Going inside the container
    3. Running a small Python test (file + stdout)
    4. Mounting a local folder and observing host ↔ container interaction
    5. Understanding why each step works
    
    Args:
        image_tag: Docker image tag to test
        work_dir: Workspace directory for volume mounting
        test_script: Optional custom Python script to test
        interactive: Whether to run in interactive mode with explanations
        cleanup: Whether to cleanup test containers after testing
    
    Returns:
        Dictionary with test results and information
    """
    
    print("\n" + "="*60)
    print(" DOCKER INSTRUCTOR: TEST YOUR SETUP")
    print("="*60)
    
    # Expand work_dir
    work_dir = os.path.expanduser(work_dir)
    work_dir = os.path.abspath(work_dir)
    
    # Create test directory
    test_dir = os.path.join(work_dir, "docker_tests")
    os.makedirs(test_dir, exist_ok=True)
    
    container_name = f"test_{image_tag.split(':')[0].replace('/', '_')}_{int(time.time())}"
    
    test_results = {
        "success": True,
        "steps": {},
        "container_name": container_name,
        "test_dir": test_dir
    }
    
    try:
        # STEP 1: Check if image exists
        print("\nSTEP 1: Checking if Docker image exists...")
        if not image_exists(image_tag):
            print(f"❌ Image '{image_tag}' not found!")
            print(f"   Try running: python docker2ls.py --image-tag {image_tag}")
            test_results["success"] = False
            test_results["steps"]["image_check"] = False
            return test_results
        print(f" Image '{image_tag}' found!")
        test_results["steps"]["image_check"] = True
        
        # STEP 2: Create test files
        print("\n STEP 2: Creating test files...")
        
        # Test Python script
        test_py = os.path.join(test_dir, "hello_docker.py")
        with open(test_py, "w") as f:
            f.write("""#!/usr/bin/env python3
# Hello Docker Test Script
import os
import sys
import socket
import platform
import datetime

print("=" * 50)
print(" DOCKER CONTAINER TEST RESULTS")
print("=" * 50)

# System Info
print(f"Python Version: {sys.version}")
print(f"Python Path: {sys.executable}")
print(f"💻 Platform: {platform.platform()}")
print(f"Hostname: {socket.gethostname()}")

# Environment
print(f"User: {os.environ.get('USER', 'Unknown')}")
print(f"User ID: {os.getuid()}")
print(f" Current Directory: {os.getcwd()}")
print(f"Directory Contents: {os.listdir('.')}")

# Workspace test
workspace_files = []
try:
    workspace_files = os.listdir('/workspace')
    print(f"Workspace (/workspace) Contents: {workspace_files[:10]}")  # Show first 10
except:
    print("Workspace (/workspace) not accessible")

# Test file operations
test_file = "/workspace/docker_tests/test_write.txt"
try:
    with open(test_file, "w") as f:
        f.write(f"Test written from container at {datetime.datetime.now()}\\n")
        f.write(f"Container ID: {socket.gethostname()}\\n")
    print(f" Successfully wrote to: {test_file}")
except Exception as e:
    print(f" Could not write to workspace: {e}")

# Test imports
print("\\nTesting Python imports:")
try:
    import numpy
    print(f"    numpy {numpy.__version__}")
except ImportError:
    print("   ❌ numpy not installed")

try:
    import pandas
    print(f"    pandas {pandas.__version__}")
except ImportError:
    print("   ❌ pandas not installed")

# Check mounted volumes
print("\\n Checking mounted volumes:")
mounts = []
try:
    with open("/proc/self/mountinfo", "r") as f:
        for line in f:
            if "/workspace" in line:
                parts = line.split()
                mounts.append({
                    "source": parts[3] if len(parts) > 3 else "unknown",
                    "destination": parts[4] if len(parts) > 4 else "unknown"
                })
    if mounts:
        for mount in mounts[:3]:  # Show first 3 mounts
            print(f"   📍 {mount['source']} -> {mount['destination']}")
    else:
        print("   📍 No mounts found in /proc/self/mountinfo")
except:
    print("   📍 Could not read mount info")

print("\\n" + "=" * 50)
print("🎉 TEST COMPLETE - Container is working!")
print("=" * 50)
""")
        
        # Bash test script
        test_sh = os.path.join(test_dir, "test_interactive.sh")
        with open(test_sh, "w") as f:
            f.write("""#!/bin/bash
echo "🐚 Interactive shell test"
echo "Current directory: $(pwd)"
echo "User: $(whoami)"
echo "Hostname: $(hostname)"
echo ""
echo "Try these commands:"
echo "  python --version"
echo "  pip list | head -10"
echo "  ls -la /workspace"
echo "  df -h"
echo ""
""")
        
        # Host file to check
        host_file = os.path.join(test_dir, "from_host.txt")
        with open(host_file, "w") as f:
            f.write(f"This file was created on the HOST machine at {datetime.datetime.now()}\n")
            f.write("If you can see this in the container, volume mounting is working!\n")
        
        os.chmod(test_sh, 0o755)
        print(f" Created test files in {test_dir}")
        print(f"   hello_docker.py - Python test script")
        print(f"   test_interactive.sh - Shell test script")
        print(f"   from_host.txt - Host file for volume test")
        test_results["steps"]["create_files"] = True
        
        # STEP 3: Start container with volume mount
        print("\n STEP 3: Starting container with volume mount...")
        print(f"   Host directory: {work_dir}")
        print(f"   Container directory: /workspace")
        print(f"   Container name: {container_name}")
        
        if interactive:
            input("\n EXPLANATION: We're using '-v' flag to mount your host directory to /workspace")
            input("   This creates a persistent link between host and container")
            input("   Press Enter to continue...")
        
        # Run container in detached mode
        cmd = [
            "docker", "run", "-dit",
            "--name", container_name,
            "-v", f"{work_dir}:/workspace",
            "--hostname", f"test-{socket.gethostname()}",
            image_tag
        ]
        
        print(f"\n💻 Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to start container: {result.stderr}")
            test_results["success"] = False
            test_results["steps"]["start_container"] = False
            return test_results
        
        print(f" Container started successfully! (ID: {result.stdout.strip()})")
        test_results["steps"]["start_container"] = True
        
        # Give container time to start
        time.sleep(2)
        
        # STEP 4: Run Python test script inside container
        print("\nSTEP 4: Running Python test script in container...")
        print(f"   Script: /workspace/docker_tests/hello_docker.py")
        
        if interactive:
            input("\n EXPLANATION: 'docker exec' runs commands inside a running container")
            input("   We're executing Python to run our test script")
            input("   Press Enter to continue...")
        
        cmd = [
            "docker", "exec", container_name,
            "python", "/workspace/docker_tests/hello_docker.py"
        ]
        
        print(f"\n💻 Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to run Python script: {result.stderr}")
            test_results["success"] = False
        else:
            print(f" Python script output:")
            print("-" * 40)
            print(result.stdout)
            print("-" * 40)
        
        test_results["steps"]["run_python"] = result.returncode == 0
        
        # STEP 5: Interactive shell test
        print("\n🐚 STEP 5: Testing interactive shell access...")
        
        if interactive:
            input("\n EXPLANATION: '-it' flags give us interactive terminal access")
            input("   This is how you 'go inside' the container")
            input("   Press Enter to continue to interactive shell...")
        
        print(f"\n💻 To enter the container interactively, run:")
        print(f"   docker exec -it {container_name} bash")
        print(f"\n   Or run our test shell script:")
        print(f"   docker exec -it {container_name} /workspace/docker_tests/test_interactive.sh")
        
        # Ask if user wants to enter container
        if interactive:
            enter = input("\n Would you like to enter the container now? (y/n): ")
            if enter.lower() == 'y':
                print(f"\nEntering container {container_name}...")
                print("   (Type 'exit' to return to host)")
                subprocess.run(["docker", "exec", "-it", container_name, "bash"])
        
        test_results["steps"]["interactive_test"] = True
        
        # STEP 6: Test file system interaction
        print("\n STEP 6: Testing host ↔ container file system interaction...")
        
        # Check if host file is visible in container
        cmd = [
            "docker", "exec", container_name,
            "cat", "/workspace/docker_tests/from_host.txt"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f" Host file accessible in container:")
            print(f"   {result.stdout.strip()}")
            
            # Create file in container and check on host
            container_file = os.path.join(test_dir, "from_container.txt")
            cmd = [
                "docker", "exec", container_name,
                "bash", "-c", f"echo 'File created INSIDE container at $(date)' > /workspace/docker_tests/from_container.txt"
            ]
            subprocess.run(cmd, capture_output=True)
            
            if os.path.exists(os.path.join(test_dir, "from_container.txt")):
                with open(os.path.join(test_dir, "from_container.txt"), "r") as f:
                    print(f" Container file accessible on host:")
                    print(f"   {f.read().strip()}")
            else:
                print("❌ Container file not found on host")
        else:
            print("❌ Volume mount not working correctly")
            test_results["success"] = False
        
        test_results["steps"]["filesystem_test"] = result.returncode == 0
        
        # STEP 7: Check container status and info
        print("\n STEP 7: Checking container status and information...")
        
        # Get container info
        cmd = ["docker", "inspect", container_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            try:
                info = json.loads(result.stdout)[0]
                print(f" Container Information:")
                print(f"   ID: {info['Id'][:12]}")
                print(f"   📍 Status: {info['State']['Status']}")
                print(f"   🖥️  Image: {info['Config']['Image']}")
                
                # Show mounts
                mounts = info.get('Mounts', [])
                if mounts:
                    print(f"   Mounts:")
                    for mount in mounts:
                        print(f"      {mount['Source']} -> {mount['Destination']}")
                
            except:
                print("    Container info available (use 'docker inspect' for details)")
        
        # Show running containers
        print(f"\n Current running containers:")
        subprocess.run(["docker", "ps", "--filter", f"name={container_name}"])
        
        test_results["steps"]["container_info"] = True
        
        # STEP 8: Summary and cleanup
        print("\n" + "="*60)
        print(" TEST SUMMARY")
        print("="*60)
        
        all_steps_passed = all(test_results["steps"].values())
        
        if all_steps_passed:
            print("🎉 ALL TESTS PASSED! Your Docker setup is working correctly.")
            test_results["success"] = True
        else:
            print(" Some tests failed. Check the output above for details.")
            test_results["success"] = False
        
        print("\n Steps completed:")
        for step, passed in test_results["steps"].items():
            status = "✅" if passed else "❌"
            step_name = step.replace("_", " ").title()
            print(f"   {status} {step_name}")
        
        print(f"\nTest files created in: {test_dir}")
        print(f" Test container name: {container_name}")
        
        if cleanup:
            print("\n🧹 Cleaning up test container...")
            subprocess.run(["docker", "stop", container_name], capture_output=True)
            subprocess.run(["docker", "rm", container_name], capture_output=True)
            print(f" Container {container_name} removed")
        else:
            print(f"\nTest container preserved for further exploration:")
            print(f"   Enter container: docker exec -it {container_name} bash")
            print(f"   Stop container: docker stop {container_name}")
            print(f"   Remove container: docker rm {container_name}")
            print(f"   View logs: docker logs {container_name}")
        
        print("\nNEXT STEPS:")
        print(f"   1. Explore your mounted workspace: cd {work_dir}")
        print(f"   2. Create Python projects in /workspace")
        print(f"   3. Use 'docker exec' to run commands in container")
        print(f"   4. Stop container when done: docker stop {container_name}")
        
        print("\n" + "="*60)
        print(" DOCKER INSTRUCTOR: TEST COMPLETE")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        test_results["success"] = False
    
    return test_results


def docker_tester_cli():
    """Command line interface for Docker tester."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Docker setup step-by-step")
    parser.add_argument("--image-tag", default="py2ls:latest", help="Docker image tag to test")
    parser.add_argument("--work-dir", default="~/workstation", help="Workspace directory")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode with explanations")
    parser.add_argument("--cleanup", "-c", action="store_true", help="Cleanup containers after test")
    parser.add_argument("--test-script", help="Custom Python test script")
    
    args = parser.parse_args()
    
    # Import modules needed for tester
    import time
    import socket
    import datetime
    
    # Run tester
    result = tester(
        image_tag=args.image_tag,
        work_dir=args.work_dir,
        test_script=args.test_script,
        interactive=args.interactive,
        cleanup=args.cleanup
    )
    
    sys.exit(0 if result["success"] else 1)

# def generate_cheatsheet_pdf(
#     work_dir: str,
#     image_tag: str,
#     system_user: str = None,
#     dockerhub_user: str = None,
#     filename: str = "docker_workstation_cheatsheet.pdf"
# ) -> str:
#     """
#     Generate a PDF cheatsheet with all Docker workstation instructions.
    
#     Args:
#         work_dir: Workspace directory
#         image_tag: Docker image tag
#         system_user: System username
#         dockerhub_user: Docker Hub username
#         filename: Output PDF filename
    
#     Returns:
#         Path to the generated PDF file
#     """
    
#     from reportlab.lib.pagesizes import A4
#     from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted
#     from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
#     from reportlab.lib import colors
#     from reportlab.lib.units import inch
#     from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
#     import io
#     from datetime import datetime
    
#     if system_user is None:
#         system_user = getpass.getuser()
    
#     # Get content from display_instructions function
#     sections = display_instructions(
#         work_dir=work_dir,
#         image_tag=image_tag,
#         system_user=system_user,
#         dockerhub_user=dockerhub_user,
#         return_content=True
#     )
    
#     # Create PDF in workspace directory
#     pdf_path = os.path.join(work_dir, filename)
    
#     # Create document
#     doc = SimpleDocTemplate(
#         pdf_path,
#         pagesize=A4,
#         rightMargin=72,
#         leftMargin=72,
#         topMargin=72,
#         bottomMargin=18
#     )
    
#     # Get styles
#     styles = getSampleStyleSheet()
    
#     # Custom styles
#     title_style = ParagraphStyle(
#         'CustomTitle',
#         parent=styles['Title'],
#         fontSize=24,
#         spaceAfter=30,
#         alignment=TA_CENTER
#     )
    
#     heading1_style = ParagraphStyle(
#         'Heading1',
#         parent=styles['Heading1'],
#         fontSize=14,
#         spaceBefore=12,
#         spaceAfter=6,
#         textColor=colors.HexColor('#2C3E50'),
#         fontName='Helvetica-Bold'
#     )
    
#     heading2_style = ParagraphStyle(
#         'Heading2',
#         parent=styles['Heading2'],
#         fontSize=12,
#         spaceBefore=10,
#         spaceAfter=4,
#         textColor=colors.HexColor('#3498DB'),
#         fontName='Helvetica-Bold'
#     )
    
#     # 改进的代码样式
#     code_style = ParagraphStyle(
#         'CodeStyle',
#         parent=styles['Code'],
#         fontSize=6.5,
#         fontName='Courier',
#         leading=7.5,  # 行距，非常重要！
#         spaceBefore=4,
#         spaceAfter=4,
#         leftIndent=10,
#         textColor=colors.HexColor('#2C3E50'),
#         backColor=colors.HexColor('#F8F9FA'),
#         borderColor=colors.HexColor('#DEE2E6'),
#         borderWidth=0.5,
#         borderPadding=5,
#     )
    
#     normal_style = ParagraphStyle(
#         'Normal',
#         parent=styles['Normal'],
#         fontSize=9,
#         spaceAfter=4,
#         leading=12
#     )
    
#     # Story holds the content
#     story = []
    
#     # Title
#     story.append(Paragraph("DOCKER WORKSTATION CHEATSHEET", title_style))
#     story.append(Spacer(1, 12))
    
#     # Metadata table
#     metadata = [
#         ["Workspace", work_dir],
#         ["Image Tag", image_tag],
#         ["User", system_user],
#         ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
#     ]
    
#     metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
#     metadata_table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F8FF')),
#         ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
#         ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
#         ('ALIGN', (1, 0), (1, -1), 'LEFT'),
#         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, -1), 9),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
#         ('TOPPADDING', (0, 0), (-1, -1), 6),
#         ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D6DBDF')),
#     ]))
    
#     story.append(metadata_table)
#     story.append(Spacer(1, 20))
    
#     # Helper function to preserve line breaks
#     def preserve_line_breaks(text):
#         """Replace newlines with HTML line breaks."""
#         # 首先将反斜杠加倍显示
#         text = text.replace('\\', '\\\\')
#         # 然后将换行符替换为HTML换行
#         return text.replace('\n', '<br/>')
    
#     # Helper function to process multi-line commands
#     def process_multiline_command(command_text):
#         """处理多行命令，确保每行单独显示"""
#         lines = command_text.split('\n')
#         processed_lines = []
        
#         for line in lines:
#             if not line.strip():
#                 continue
            
#             # 检查是否是命令的延续行（以反斜杠结尾）
#             if line.rstrip().endswith('\\'):
#                 # 这是命令的延续行，保持格式
#                 processed_lines.append(f"<font face='Courier' size='7'>{line}</font>")
#             else:
#                 processed_lines.append(f"<font face='Courier' size='7'>{line}</font>")
        
#         return '<br/>'.join(processed_lines)
    
#     # Helper function to format content with proper line breaks
#     def format_content_for_pdf(content_lines):
#         """Format content lines for PDF with proper line breaks."""
#         formatted = []
        
#         current_block = []
#         in_code_block = False
        
#         for line in content_lines:
#             if not line.strip():
#                 if current_block:
#                     # 处理当前块
#                     block_text = '<br/>'.join(current_block)
#                     if in_code_block:
#                         formatted.append(Paragraph(f"<font face='Courier' size='7'>{block_text}</font>", normal_style))
#                     else:
#                         formatted.append(Paragraph(f"<font face='Helvetica' size='9'>{block_text}</font>", normal_style))
#                     current_block = []
#                 formatted.append(Spacer(1, 4))
#                 continue
            
#             # 检查是否是分隔线
#             if all(char == '-' or char == '=' or char == '*' for char in line.strip()):
#                 if current_block:
#                     block_text = '<br/>'.join(current_block)
#                     if in_code_block:
#                         formatted.append(Paragraph(f"<font face='Courier' size='7'>{block_text}</font>", normal_style))
#                     else:
#                         formatted.append(Paragraph(f"<font face='Helvetica' size='9'>{block_text}</font>", normal_style))
#                     current_block = []
#                 formatted.append(Spacer(1, 8))
#                 continue
            
#             # 检查是否是代码/命令
#             is_code_line = False
#             if any(line.strip().startswith(prefix) for prefix in 
#                    ['docker', '#', 'alias', 'git ', 'python ', 'pip ', 'jupyter ', 'kubectl']):
#                 is_code_line = True
#             elif any(marker in line for marker in ['\\', '--', '-v ', '-e ', '-p ', '|', '→']):
#                 is_code_line = True
#             elif line.strip().startswith(('# ', '// ', '/*')):
#                 is_code_line = True
            
#             # 处理多行命令
#             if '\\' in line and ('docker' in line or 'alias' in line or 'git' in line):
#                 # 这是一个多行命令，特殊处理
#                 if current_block:
#                     # 结束当前块
#                     block_text = '<br/>'.join(current_block)
#                     if in_code_block:
#                         formatted.append(Paragraph(f"<font face='Courier' size='7'>{block_text}</font>", normal_style))
#                     else:
#                         formatted.append(Paragraph(f"<font face='Helvetica' size='9'>{block_text}</font>", normal_style))
#                     current_block = []
                
#                 # 直接添加为代码段落
#                 formatted.append(Paragraph(f"<font face='Courier' size='7'>{line}</font>", normal_style))
#                 continue
            
#             # 添加到当前块
#             current_block.append(line)
#             in_code_block = is_code_line if not current_block else in_code_block
        
#         # 处理最后一个块
#         if current_block:
#             block_text = '<br/>'.join(current_block)
#             if in_code_block:
#                 formatted.append(Paragraph(f"<font face='Courier' size='7'>{block_text}</font>", normal_style))
#             else:
#                 formatted.append(Paragraph(f"<font face='Helvetica' size='9'>{block_text}</font>", normal_style))
        
#         return formatted
    
#     # Add all sections to PDF
#     for section_title, section_content in sections.items():
#         if "PDF CHEATSHEET INFO" in section_title:
#             continue  # Skip PDF info in main content
        
#         # Clean up section title
#         if "SECTION" in section_title:
#             # Extract section number and title
#             parts = section_title.split(": ", 1)
#             if len(parts) == 2:
#                 section_num, section_name = parts
#                 clean_title = f"{section_num.replace('SECTION ', '')}. {section_name}"
#             else:
#                 clean_title = section_title.replace("SECTION ", "")
#         else:
#             clean_title = section_title
        
#         story.append(Paragraph(clean_title, heading1_style))
        
#         # Add section separator
#         story.append(Spacer(1, 4))
#         story.append(Paragraph("<font color='gray'>" + "─" * 50 + "</font>", normal_style))
#         story.append(Spacer(1, 8))
        
#         # Process section content with improved formatting
#         for line in section_content:
#             if not line.strip():
#                 story.append(Spacer(1, 4))
#                 continue
            
#             # 检查是否是分隔线
#             if all(char == '-' or char == '=' or char == '*' for char in line.strip()):
#                 story.append(Spacer(1, 8))
#                 continue
            
#             # 特殊处理多行docker命令
#             if line.strip().startswith('docker run'):
#                 # 这是一个docker run命令，需要特殊处理换行
#                 # 将命令分割成多行
#                 lines = [line]
#                 # 查找后续的续行
#                 story.append(Paragraph(f"<font face='Courier' size='7'>{line}</font>", normal_style))
#                 continue
#             elif '\\' in line and line.strip().endswith('\\'):
#                 # 这是命令的续行
#                 story.append(Paragraph(f"<font face='Courier' size='7'>{line}</font>", normal_style))
#                 continue
            
#             # 检查是否是代码/命令
#             is_code = False
#             code_prefixes = ['docker', '# ', 'alias', 'git ', 'python ', 'pip ', 'jupyter ', 
#                             'kubectl', 'aws ', 'az ', 'gcloud ', 'terraform']
#             code_markers = ['\\', '--', '-v ', '-e ', '-p ', '|', '→', '├', '└', '│']
            
#             if any(line.strip().startswith(prefix) for prefix in code_prefixes):
#                 is_code = True
#             elif any(marker in line for marker in code_markers):
#                 is_code = True
            
#             if is_code:
#                 # 使用等宽字体，处理换行符
#                 line_fixed = line.replace('\n', '<br/>').replace('\\', '\\\\')
#                 story.append(Paragraph(f"<font face='Courier' size='7'>{line_fixed}</font>", normal_style))
#             elif line.strip().startswith(('•', '-')):
#                 story.append(Paragraph(f"<font face='Helvetica' size='9'>{line}</font>", normal_style))
#             else:
#                 story.append(Paragraph(f"<font face='Helvetica' size='9'>{line}</font>", normal_style))
        
#         story.append(Spacer(1, 20))
    
#     # Build PDF
#     doc.build(story)
    
#     print(f"✓ PDF cheatsheet generated: {pdf_path}")
#     return pdf_path
def generate_cheatsheet_pdf(
    work_dir: str,
    image_tag: str,
    system_user: str = None,
    dockerhub_user: str = None,
    filename: str = "docker_workstation_cheatsheet.pdf"
) -> str:
    """生成简单但格式正确的PDF"""
    
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    import io
    from datetime import datetime
    
    if system_user is None:
        system_user = getpass.getuser()
    
    # Get content
    sections = display_instructions(
        work_dir=work_dir,
        image_tag=image_tag,
        system_user=system_user,
        dockerhub_user=dockerhub_user,
        return_content=True
    )
    
    # Create PDF
    pdf_path = os.path.join(work_dir, filename)
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    styles = getSampleStyleSheet()
    
    # 样式
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading1'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=8,
        textColor=colors.HexColor('#2C3E50'),
        fontName='Helvetica-Bold'
    )
    
    # Preformatted 样式
    pre_style = ParagraphStyle(
        'PreformattedStyle',
        parent=styles['Code'],
        fontSize=6.5,
        fontName='Courier',
        leading=7.5,
        spaceBefore=5,
        spaceAfter=5,
        leftIndent=10,
        textColor=colors.HexColor('#2C3E50'),
        backColor=colors.HexColor('#F8F9FA'),
        borderColor=colors.HexColor('#DEE2E6'),
        borderWidth=0.5,
        borderPadding=5,
    )
    
    story = []
    
    # 标题
    story.append(Paragraph("DOCKER WORKSTATION CHEATSHEET", title_style))
    story.append(Spacer(1, 20))
    
    # Metadata table
    metadata = [
        ["Workspace", work_dir],
        ["Image Tag", image_tag],
        ["User", system_user],
        ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    ]
    
    metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F8FF')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D6DBDF')),
    ]))
    
    story.append(metadata_table)
    story.append(Spacer(1, 20))
    # 添加内容
    for section_title, section_lines in sections.items():
        if "PDF CHEATSHEET INFO" in section_title:
            continue
        
        # 清理标题
        if "SECTION" in section_title:
            parts = section_title.split(": ", 1)
            if len(parts) == 2:
                clean_title = f"{parts[0].replace('SECTION ', '')}. {parts[1]}"
            else:
                clean_title = section_title
        else:
            clean_title = section_title
        
        story.append(Paragraph(clean_title, heading_style))
        story.append(Spacer(1, 10))
        
        # 将整个section内容作为Preformatted添加
        section_text = '\n'.join(section_lines)
        
        # 使用Preformatted保持原始格式
        story.append(Preformatted(section_text, pre_style))
        story.append(Spacer(1, 20))
    
    doc.build(story)
    print(f"✓ PDF generated with preserved formatting: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="Set up Docker development workstation")
    subparsers = parser.add_subparsers(dest="command", help="Command to run", required=True)  # 添加 required=True
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up Docker development workstation")
    setup_parser.add_argument("--work-dir", default="~/workstation", help="Workspace directory")
    setup_parser.add_argument("--image-tag", default="py2ls:latest", help="Docker image tag")
    setup_parser.add_argument("--config", help="Configuration JSON file")
    setup_parser.add_argument("--packages", nargs="+", help="Additional system packages")
    setup_parser.add_argument("--pip-packages", nargs="+", help="Additional pip packages")
    setup_parser.add_argument("--skip-build", action="store_true", help="Skip build process")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test Docker setup step-by-step")
    test_parser.add_argument("--image-tag", default="py2ls:latest", help="Docker image tag to test")
    test_parser.add_argument("--work-dir", default="~/workstation", help="Workspace directory")
    test_parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode with explanations")
    test_parser.add_argument("--cleanup", "-c", action="store_true", help="Cleanup containers after test")
    test_parser.add_argument("--test-script", help="Custom Python test script")
    
    # Display instructions command
    display_parser = subparsers.add_parser("display", help="Display comprehensive usage instructions")
    display_parser.add_argument("--work-dir", default="~/workstation", help="Workspace directory")
    display_parser.add_argument("--image-tag", default="py2ls:latest", help="Docker image tag")
    display_parser.add_argument("--config", help="Configuration JSON file")
    # 添加 --pdf 参数到 display 命令
    display_parser.add_argument("--pdf", action="store_true", help="Also generate PDF cheatsheet")

    # PDF command
    if PDF_AVAILABLE:
        pdf_parser = subparsers.add_parser("pdf", help="Generate PDF cheatsheet")
        pdf_parser.add_argument("--work-dir", default="~/workstation", help="Workspace directory")
        pdf_parser.add_argument("--image-tag", default="py2ls:latest", help="Docker image tag")
        pdf_parser.add_argument("--output", default="docker_workstation_cheatsheet.pdf", help="Output PDF filename")
    
    args = parser.parse_args()
    
    # 处理各个命令
    if args.command == "setup":
        # Run setup
        result = setup_docker_workstation(
            work_dir=args.work_dir,
            image_tag=args.image_tag,
            config_file=args.config,
            additional_packages=args.packages,
            pip_packages=args.pip_packages,
            skip_build=args.skip_build
        )
        sys.exit(0 if result["success"] else 1)
    
    elif args.command == "test":
        # Run tester
        result = tester(
            image_tag=args.image_tag,
            work_dir=args.work_dir,
            test_script=args.test_script,
            interactive=args.interactive,
            cleanup=args.cleanup
        )
        sys.exit(0 if result["success"] else 1)
    
    elif args.command == "pdf" and PDF_AVAILABLE:
        # Generate PDF only
        work_dir = os.path.expanduser(args.work_dir)
        work_dir = os.path.abspath(work_dir)
        
        if not os.path.exists(work_dir):
            print(f"Error: Workspace directory does not exist: {work_dir}")
            sys.exit(1)
        
        try:
            pdf_path = generate_cheatsheet_pdf(
                work_dir=work_dir,
                image_tag=args.image_tag,
                filename=args.output
            )
            print(f"✓ PDF cheatsheet generated: {pdf_path}")
            sys.exit(0)
        except Exception as e:
            print(f"Error generating PDF: {e}")
            sys.exit(1)
    
    elif args.command == "display":
        # Display instructions
        work_dir = os.path.expanduser(args.work_dir)
        work_dir = os.path.abspath(work_dir)
        
        # Load config if provided
        system_user = getpass.getuser()
        image_tag = args.image_tag
        if args.config:
            try:
                with open(args.config, 'r') as f:
                    config_data = json.load(f)
                    work_dir = config_data.get("work_dir", work_dir)
                    image_tag = config_data.get("image_tag", image_tag)
                    system_user = config_data.get("system_user", system_user)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        display_instructions(
            work_dir=work_dir,
            image_tag=image_tag,
            system_user=system_user
        )
        
        # 检查是否有 --pdf 参数
        if hasattr(args, 'pdf') and args.pdf:
            if PDF_AVAILABLE:
                try:
                    pdf_path = generate_cheatsheet_pdf(
                        work_dir=work_dir,
                        image_tag=image_tag,
                        system_user=system_user
                    )
                    print(f"\n✓ PDF cheatsheet saved to: {pdf_path}")
                except Exception as e:
                    print(f"⚠️ Could not generate PDF: {e}")
            else:
                print("⚠️ PDF generation not available. Install reportlab with: pip install reportlab")
    
    else:
        # 不应该执行到这里，因为设置了 required=True
        print(f"Error: Unknown command '{args.command}'")
        parser.print_help()
        sys.exit(1)

# # Main execution block
# if __name__ == "__main__":
#     # Parse command line arguments
#     import argparse
    
#     parser = argparse.ArgumentParser(description="Set up Docker development workstation")
#     subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
#     # Setup command
#     setup_parser = subparsers.add_parser("setup", help="Set up Docker development workstation")
#     setup_parser.add_argument("--work-dir", default="~/workstation", help="Workspace directory")
#     setup_parser.add_argument("--image-tag", default="py2ls:latest", help="Docker image tag")
#     setup_parser.add_argument("--config", help="Configuration JSON file")
#     setup_parser.add_argument("--packages", nargs="+", help="Additional system packages")
#     setup_parser.add_argument("--pip-packages", nargs="+", help="Additional pip packages")
#     setup_parser.add_argument("--skip-build", action="store_true", help="Skip build process")
    
#     # Test command
#     test_parser = subparsers.add_parser("test", help="Test Docker setup step-by-step")
#     test_parser.add_argument("--image-tag", default="py2ls:latest", help="Docker image tag to test")
#     test_parser.add_argument("--work-dir", default="~/workstation", help="Workspace directory")
#     test_parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode with explanations")
#     test_parser.add_argument("--cleanup", "-c", action="store_true", help="Cleanup containers after test")
#     test_parser.add_argument("--test-script", help="Custom Python test script")
    
#     # Display instructions command
#     display_parser = subparsers.add_parser("display", help="Display comprehensive usage instructions")
#     display_parser.add_argument("--work-dir", default="~/workstation", help="Workspace directory")
#     display_parser.add_argument("--image-tag", default="py2ls:latest", help="Docker image tag")
#     display_parser.add_argument("--config", help="Configuration JSON file")
#     # 添加 --pdf 参数到 display 命令
#     display_parser.add_argument("--pdf", action="store_true", help="Also generate PDF cheatsheet")

#     parser.set_defaults(command='setup')
#     args = parser.parse_args()
    
#     # PDF command
#     if PDF_AVAILABLE:
#         pdf_parser = subparsers.add_parser("pdf", help="Generate PDF cheatsheet")
#         pdf_parser.add_argument("--work-dir", default="~/workstation", help="Workspace directory")
#         pdf_parser.add_argument("--image-tag", default="py2ls:latest", help="Docker image tag")
#         pdf_parser.add_argument("--output", default="docker_workstation_cheatsheet.pdf", help="Output PDF filename")
#     else:
#         print(f"PDF_AVAILABLE:{PDF_AVAILABLE}")
#     if args.command == "setup" or args.command is None:
#         # Run setup
#         result = setup_docker_workstation(
#             work_dir=args.work_dir,
#             image_tag=args.image_tag,
#             config_file=args.config,
#             additional_packages=args.packages,
#             pip_packages=args.pip_packages,
#             skip_build=args.skip_build
#         )
#         sys.exit(0 if result["success"] else 1)
    
#     elif args.command == "test":
#         # Run tester
#         result = tester(
#             image_tag=args.image_tag,
#             work_dir=args.work_dir,
#             test_script=args.test_script,
#             interactive=args.interactive,
#             cleanup=args.cleanup
#         )
#         sys.exit(0 if result["success"] else 1) 
#     elif args.command == "pdf" and PDF_AVAILABLE:
#         # Generate PDF only
#         work_dir = os.path.expanduser(args.work_dir)
#         work_dir = os.path.abspath(work_dir)
        
#         if not os.path.exists(work_dir):
#             print(f"Error: Workspace directory does not exist: {work_dir}")
#             sys.exit(1)
        
#         try:
#             pdf_path = generate_cheatsheet_pdf(
#                 work_dir=work_dir,
#                 image_tag=args.image_tag,
#                 filename=args.output
#             )
#             print(f"✓ PDF cheatsheet generated: {pdf_path}")
#             sys.exit(0)
#         except Exception as e:
#             print(f"Error generating PDF: {e}")
#             sys.exit(1)
    
#     else:
#         # Display instructions
#         work_dir = os.path.expanduser(args.work_dir)
#         work_dir = os.path.abspath(work_dir)
        
#         # Load config if provided
#         system_user = getpass.getuser()
#         if args.config:
#             try:
#                 with open(args.config, 'r') as f:
#                     config_data = json.load(f)
#                     work_dir = config_data.get("work_dir", work_dir)
#                     image_tag = config_data.get("image_tag", args.image_tag)
#                     system_user = config_data.get("system_user", system_user)
#             except Exception as e:
#                 print(f"Warning: Could not load config file: {e}")
        
#         display_instructions(
#             work_dir=work_dir,
#             image_tag=args.image_tag,
#             system_user=system_user
#         ) 
#         if PDF_AVAILABLE:
#             try:
#                 pdf_path = generate_cheatsheet_pdf(
#                     work_dir=work_dir,
#                     image_tag=args.image_tag,
#                     system_user=system_user
#                 )
#                 print(f"\n✓ PDF cheatsheet saved to: {pdf_path}")
#             except Exception as e:
#                 print(f"⚠️ Could not generate PDF: {e}")
#         else:
#             print("⚠️ PDF generation not available. Install reportlab with: pip install reportlab") 
 




# def display_instructions(
#     work_dir: str,
#     image_tag: str,
#     system_user: str = None,
#     dockerhub_user: str = None,
# ) -> None:
#     """
#     Display professional, comprehensive, and practical daily usage instructions
#     for the Docker workstation container.
    
#     Enhanced coverage:
#         - Detailed workspace and container configuration
#         - First-time setup with advanced options
#         - Comprehensive daily development workflow
#         - Advanced VS Code Dev Container integration
#         - Professional Python development practices
#         - Jupyter ecosystem with optimizations
#         - Git workflow with best practices
#         - Advanced networking and port management
#         - Resource optimization and monitoring
#         - Backup and recovery strategies
#         - Security considerations
#         - Troubleshooting guide
#         - Team collaboration practices
#     """
#     if dockerhub_user is None:
#         dockerhub_user = get_dockerhub_username()
#     if system_user is None:
#         system_user = getpass.getuser()
#     container_name = image_tag.split(":")[0].replace("/", "_")
#     image_name = image_tag.split(":")[0]
#     tag = image_tag.split(":")[1] if ":" in image_tag else "latest"
#     print("\n" + "="*20 + " DOCKER WORKSTATION: USAGE GUIDE " + "="*20)
    
#     # SECTION 0: DOCKER HUB OPERATIONS
#     print(f"\nSECTION 0: DOCKER HUB OPERATIONS")
#     print("-" * 40)
    
#     print("\nDOCKER HUB AUTHENTICATION:")
#     print(f"# Login to Docker Hub")
#     print(f"docker login")
#     print(f"\n# Login with specific credentials")
#     print(f"docker login -u {dockerhub_user}")
#     print(f"\n# Logout from Docker Hub")
#     print(f"docker logout")
    
#     print("\nPULL IMAGES FROM DOCKER HUB:")
#     print(f"# Pull latest version")
#     print(f"docker pull {dockerhub_user}/{image_name}:latest")
#     print(f"\n# Pull specific version")
#     print(f"docker pull {dockerhub_user}/{image_name}:v1.0.0")
#     print(f"\n# Pull with digest (immutable)")
#     print(f"docker pull {dockerhub_user}/{image_name}@sha256:abc123...")
#     print(f"\n# Pull all tags")
#     print(f"docker pull --all-tags {dockerhub_user}/{image_name}")
    
#     print("\nPREPARE IMAGES FOR PUSH:")
#     print(f"# Tag local image for Docker Hub")
#     print(f"docker tag {image_tag} {dockerhub_user}/{image_name}:{tag}")
#     print(f"\n# Tag with multiple tags")
#     print(f"docker tag {image_tag} {dockerhub_user}/{image_name}:latest")
#     print(f"docker tag {image_tag} {dockerhub_user}/{image_name}:v1.0.0")
#     print(f"docker tag {image_tag} {dockerhub_user}/{image_name}:$(date +%Y%m%d)")
#     print(f"\n# Build and tag directly")
#     print(f"docker build -t {dockerhub_user}/{image_name}:latest -t {dockerhub_user}/{image_name}:v1.0.0 .")
    
#     print("\nPUSH IMAGES TO DOCKER HUB:")
#     print(f"# Push single tag")
#     print(f"docker push {dockerhub_user}/{image_name}:latest")
#     print(f"\n# Push all tags for an image")
#     print(f"docker push {dockerhub_user}/{image_name} --all-tags")
#     print(f"\n# Multi-architecture push (if using buildx)")
#     print(f"docker buildx build --platform linux/amd64,linux/arm64 -t {dockerhub_user}/{image_name}:latest --push .")
    
#     print("\nIMAGE MANAGEMENT:")
#     print(f"# List local images")
#     print(f"docker images")
#     print(f"docker image ls")
#     print(f"\n# Search Docker Hub")
#     print(f"docker search {image_name}")
#     print(f"\n# Remove unused images")
#     print(f"docker image prune -a")
#     print(f"\n# Remove specific image")
#     print(f"docker rmi {dockerhub_user}/{image_name}:latest")
    
#     print("\nDOCKER HUB BEST PRACTICES:")
#     print(f"# Use version tags")
#     print(f"docker tag {image_name}:latest {dockerhub_user}/{image_name}:v1.2.3")
#     print(f"\n# Keep images small")
#     print(f"docker history {dockerhub_user}/{image_name}:latest")
#     print(f"\n# Scan for vulnerabilities")
#     print(f"docker scan {dockerhub_user}/{image_name}:latest")
#     print(f"\n# Inspect pushed image")
#     print(f"docker inspect {dockerhub_user}/{image_name}:latest")
    
#     # SECTION 1: ENVIRONMENT OVERVIEW
#     print(f"\n\nSECTION 1: ENVIRONMENT OVERVIEW")
#     print("-" * 40)
#     print(f"Host Workspace Directory: {work_dir}")
#     print(f"Docker Image-Tag: {image_tag}")
#     print(f"Docker Hub Repository: {dockerhub_user}/{image_name}")
#     print(f"Container Name: {container_name}")
#     print(f"Container User: {system_user}")
#     print(f"Container Workspace: /workspace")
#     print(f"Volume Mount: {work_dir} <-> /workspace")
    
#     # SECTION 2: COMPLETE FIRST-TIME SETUP
#     print("\n\nSECTION 2: COMPLETE FIRST-TIME SETUP")
#     print("-" * 20+"90% cases"+"-"*20)
#     print(f"""docker run -dit --name {container_name} \\ 
#     -v {work_dir}:/workspace \\ 
#     {image_tag}""")
#     print("""
# docker run → creates new container 'Start a NEW Container'
# docker start → starts existing container
# docker exec → enters running container
#           """)
    
#     print(f"""docker run -dit --name {container_name} \\
#     --hostname {container_name}-dev \\
#     --restart unless-stopped \\
#     --memory="4g" \\
#     --cpus="2.0" \\
#     --shm-size="1g" \\
#     -v {work_dir}:/workspace \\
#     -v {work_dir}/.cache:/home/{system_user}/.cache \\
#     -v {work_dir}/.config:/home/{system_user}/.config \\
#     -v ~/.ssh:/home/{system_user}/.ssh:ro \\
#     -v ~/.gitconfig:/home/{system_user}/.gitconfig:ro \\
#     -v ~/.aws:/home/{system_user}/.aws:ro \\
#     -v ~/.docker:/home/{system_user}/.docker:ro \\
#     -v /tmp/.X11-unix:/tmp/.X11-unix \\
#     -v /var/run/docker.sock:/var/run/docker.sock \\
#     -e DISPLAY=${{DISPLAY}} \\
#     -e TERM=xterm-256color \\
#     -e LANG=C.UTF-8 \\
#     -e LC_ALL=C.UTF-8 \\
#     -e PYTHONPATH=/workspace \\
#     -e PYTHONUNBUFFERED=1 \\
#     -p 8888:8888 \\
#     -p 8080:8080 \\
#     -p 3000:3000 \\
#     -p 5432:5432 \\
#     -p 6379:6379 \\
#     --add-host=host.docker.internal:host-gateway \\
#     --security-opt seccomp=unconfined \\
#     --cap-add=SYS_PTRACE \\
#     {image_tag}""")
    
#     print(f""" # Full explaination
#     docker run -dit --name {container_name} \\  # -d: detached mode, -i: interactive, -t: allocate a pseudo-TTY
#         --hostname {container_name}-dev \\      # Set container hostname
#         --restart unless-stopped \\            # Automatically restart container unless manually stopped
#         --memory="4g" \\                       # Limit container memory to 4 GB
#         --cpus="2.0" \\                        # Limit container to 2 CPU cores
#         --shm-size="1g" \\                     # Shared memory size, useful for Jupyter or ML workloads
#         -v {work_dir}:/workspace \\            # Mount your workspace folder (persistent code/data)
#         -v {work_dir}/.cache:/home/{system_user}/.cache \\  # Cache folder inside container
#         -v {work_dir}/.config:/home/{system_user}/.config \\ # Config folder inside container
#         -v ~/.ssh:/home/{system_user}/.ssh:ro \\           # Mount SSH keys read-only
#         -v ~/.gitconfig:/home/{system_user}/.gitconfig:ro \\ # Mount Git config read-only
#         -v ~/.aws:/home/{system_user}/.aws:ro \\           # Mount AWS credentials read-only
#         -v ~/.docker:/home/{system_user}/.docker:ro \\     # Mount Docker config read-only (for docker-in-docker)
#         -v /tmp/.X11-unix:/tmp/.X11-unix \\               # For GUI apps (X11 forwarding)
#         -v /var/run/docker.sock:/var/run/docker.sock \\   # Allow container to run Docker commands
#         -e DISPLAY=${{DISPLAY}} \\                        # Forward display for GUI apps
#         -e TERM=xterm-256color \\                         # Set terminal type
#         -e LANG=C.UTF-8 \\                                # Language setting
#         -e LC_ALL=C.UTF-8 \\                              # Language/locale
#         -e PYTHONPATH=/workspace \\                       # Python path inside container
#         -e PYTHONUNBUFFERED=1 \\                          # Python output is unbuffered (real-time logging)
#         -p 8888:8888 \\                                   # Map host port 8888 (e.g., Jupyter) to container
#         -p 8080:8080 \\                                   # Map host port 8080 (e.g., web app) to container
#         -p 3000:3000 \\                                   # Map host port 3000 (frontend dev) to container
#         -p 5432:5432 \\                                   # Map host port 5432 (PostgreSQL) to container
#         -p 6379:6379 \\                                   # Map host port 6379 (Redis) to container
#         --add-host=host.docker.internal:host-gateway \\   # Map host.docker.internal to host gateway
#         --security-opt seccomp=unconfined \\              # Relax security for debugging/tracing
#         --cap-add=SYS_PTRACE \\                            # Allow debugging (ptrace)
#         {image_tag}                                      # Docker image to use
#     """)
    
#     # SECTION 3: DAILY DEVELOPMENT WORKFLOW
#     print("\n\nSECTION 3: DAILY DEVELOPMENT WORKFLOW")
#     print("-" * 40)
    
#     print("\nCONTAINER LIFE CYCLE MANAGEMENT:")
#     print(f"  # Start container")
#     print(f"  docker start {container_name}")
#     print(f"  \n  # Attach with interactive shell")
#     print(f"  docker exec -it {container_name} bash")
#     print(f"  \n  # Attach as root (for admin tasks)")
#     print(f"  docker exec -it -u root {container_name} bash")
#     print(f"  \n  # Execute single command")
#     print(f"  docker exec {container_name} python --version")
    
#     print("\nPROJECT SETUP TEMPLATE:")
#     print(f"""mkdir -p {work_dir}/{{project_name}}/{{src,tests,docs,data,notebooks}}
# cd {work_dir}/project_name
# echo "# Project Structure
# ├── src/           # Source code
# ├── tests/         # Test files
# ├── docs/          # Documentation
# ├── data/          # Datasets
# ├── notebooks/     # Jupyter notebooks
# └── requirements.txt
# " > README.md""")
    
#     print("\nPYTHON ENVIRONMENT SETUP:")
#     print("""# Inside container at /workspace/project_name
# python -m venv venv --prompt="project_name"
# source venv/bin/activate

# # Create comprehensive requirements
# cat > requirements.txt << EOF
# # Core dependencies
# pandas>=2.0.0
# numpy>=1.24.0
# scikit-learn>=1.3.0

# # Development tools
# black>=23.0.0
# flake8>=6.0.0
# pytest>=7.0.0
# pytest-cov>=4.0.0
# pre-commit>=3.0.0

# # Documentation
# sphinx>=7.0.0
# myst-parser>=2.0.0

# # Notebook support
# jupyter>=1.0.0
# ipykernel>=6.0.0
# EOF

# # Install with optimizations
# pip install --upgrade pip
# pip install --no-cache-dir -r requirements.txt

# # Register kernel for Jupyter
# python -m ipykernel install --user --name="project_name" --display-name="Python (project_name)"

# # Setup pre-commit hooks
# pre-commit install""")
    
#     print("\nDAILY DEVELOPMENT COMMANDS:")
#     print("""# Code editing
# code .                          # VS Code in container
# vim main.py                     # Terminal editor

# # Testing
# pytest tests/ -v               # Run all tests
# pytest tests/ -xvs             # Stop on first failure with verbose output
# pytest --cov=src tests/        # Coverage report

# # Formatting & Linting
# black src/                     # Auto-format
# flake8 src/                    # Lint check
# mypy src/                      # Type checking

# # Package management
# pip list --outdated           # Check outdated packages
# pip install -U package        # Update specific package
# pip freeze > requirements.txt # Freeze dependencies""")
    
#     # SECTION 4: VS CODE INTEGRATION
#     print("\n\nSECTION 4: VS CODE INTEGRATION")
#     print("-" * 40)
    
#     print("\nADVANCED DEV CONTAINER CONFIGURATION:")
#     print(f"""Create {work_dir}/.devcontainer/devcontainer.json:
# {{
#   "name": "{container_name} Development",
#   "dockerComposeFile": "docker-compose.yml",
#   "service": "workspace",
#   "workspaceFolder": "/workspace",
#   "remoteUser": "{system_user}",
  
#   // VS Code extensions for Python development
#   "extensions": [
#     "ms-python.python",
#     "ms-python.vscode-pylance",
#     "ms-python.black-formatter",
#     "ms-toolsai.jupyter",
#     "GitHub.copilot",
#     "eamodio.gitlens",
#     "charliermarsh.ruff"
#   ],
  
#   // Port forwarding
#   "forwardPorts": [8888, 8080, 3000],
  
#   // Container environment variables
#   "containerEnv": {{
#     "PYTHONPATH": "/workspace",
#     "PYTHONUNBUFFERED": "1"
#   }},
  
#   // Post-create commands
#   "postCreateCommand": "pip install --upgrade pip && pre-commit install",
  
#   // Customizations
#   "customizations": {{
#     "vscode": {{
#       "settings": {{
#         "python.defaultInterpreterPath": "/workspace/venv/bin/python",
#         "python.linting.enabled": true,
#         "python.formatting.provider": "black",
#         "editor.formatOnSave": true
#       }}
#     }}
#   }}
# }}""")
    
#     print("\nQUICK START WITH VS CODE:")
#     print("1. Install 'Remote - Containers' extension")
#     print("2. Open command palette (Ctrl+Shift+P)")
#     print("3. 'Remote-Containers: Open Folder in Container'")
#     print("4. Select your workspace directory")
#     print("5. VS Code will build and connect automatically")
    
#     # SECTION 5: JUPYTER ECOSYSTEM
#     print("\n\nSECTION 5: JUPYTER ECOSYSTEM")
#     print("-" * 40)
    
#     print("\nJUPYTER SETUP:")
#     print("""# Production Jupyter Lab configuration
# mkdir -p ~/.jupyter
# cat > ~/.jupyter/jupyter_lab_config.py << EOF
# c.ServerApp.ip = '0.0.0.0'
# c.ServerApp.port = 8888
# c.ServerApp.open_browser = False
# c.ServerApp.root_dir = '/workspace'
# c.ServerApp.token = ''  # Set password in production
# c.ServerApp.password = ''
# c.ServerApp.allow_origin = '*'
# c.ServerApp.allow_root = True
# c.LabApp.collaborative = True
# c.ContentsManager.allow_hidden = True
# EOF

# # Start Jupyter Lab with optimizations
# jupyter lab --config=~/.jupyter/jupyter_lab_config.py \
#             --LabApp.allow_remote_access=True \
#             --no-browser \
#             --NotebookApp.terminado_settings={{'shell_command': ['bash']}}
            
# # Alternative: Jupyter Notebook
# jupyter notebook --notebook-dir=/workspace \
#                  --ip=0.0.0.0 \
#                  --port=8888 \
#                  --no-browser \
#                  --allow-root""")
    
#     print("\nACCESS JUPYTER FROM HOST:")
#     print("  Local: http://localhost:8888")
#     print("  Network: http://<your-ip>:8888")
#     print("\nSECURITY NOTE: In production, use:")
#     print("  --NotebookApp.token='your-secret-token'")
#     print("  Or set password with: jupyter notebook password")
    
#     # SECTION 6: GIT WORKFLOW & COLLABORATION
#     print("\n\nSECTION 6: GIT WORKFLOW & COLLABORATION")
#     print("-" * 40)
    
#     print("\nGIT CONFIGURATION:")
#     print("""# Inside container, set up Git identity
# git config --global user.name "Your Name"
# git config --global user.email "your.email@example.com"
# git config --global core.editor "vim"
# git config --global pull.rebase true
# git config --global init.defaultBranch main

# # SSH Agent forwarding (if needed)
# eval "$(ssh-agent -s)"
# ssh-add ~/.ssh/id_rsa""")
    
#     print("\nGIT WORKFLOW COMMANDS:")
#     print("""# Clone repositories
# git clone git@github.com:username/repo.git /workspace/repo

# # Daily workflow
# git status                      # Check changes
# git diff                        # Review changes
# git add -p                     # Interactive staging
# git commit -s -m "feat: add feature"  # Signed commit
# git push origin main           # Push to remote

# # Branch management
# git checkout -b feature/new-feature
# git push -u origin feature/new-feature
# git checkout main
# git merge --no-ff feature/new-feature""")
    
#     print("\nPRE-COMMIT HOOKS SETUP:")
#     print("""# .pre-commit-config.yaml
# repos:
#   - repo: https://github.com/pre-commit/pre-commit-hooks
#     rev: v4.4.0
#     hooks:
#       - id: trailing-whitespace
#       - id: end-of-file-fixer
#       - id: check-yaml
#       - id: check-added-large-files
  
#   - repo: https://github.com/psf/black
#     rev: 23.0.0
#     hooks:
#       - id: black
  
#   - repo: https://github.com/PyCQA/flake8
#     rev: 6.0.0
#     hooks:
#       - id: flake8""")
    
#     # SECTION 7: NETWORKING & PORTS
#     print("\n\nSECTION 7: NETWORKING & PORTS")
#     print("-" * 40)
    
#     print("\nPORT MAPPING REFERENCE:")
#     print("  Port 8888  -> Jupyter Notebook/Lab")
#     print("  Port 8080  -> Web applications/APIs")
#     print("  Port 3000  -> Node.js/React development")
#     print("  Port 5432  -> PostgreSQL")
#     print("  Port 6379  -> Redis")
#     print("  Port 27017 -> MongoDB")
#     print("  Port 9200  -> Elasticsearch")
#     print("  Port 5601  -> Kibana")
    
#     print("\nDYNAMIC PORT FORWARDING:")
#     print(f"# Map additional ports after container creation")
#     print(f"docker stop {container_name}")
#     print(f"docker commit {container_name} {image_tag}-backup")
#     print(f"docker run -d -p 5000:5000 -p 8000:8000 --name {container_name}-new [other_options] {image_tag}")
    
#     print("\nNETWORK CONFIGURATION:")
#     print("""# Create custom network
# docker network create dev-network

# # Run container on custom network
# docker run --network=dev-network --name=workspace ...

# # Connect containers
# docker network connect dev-network postgres-container
# docker network connect dev-network redis-container

# # Test connectivity
# docker exec workspace ping postgres-container
# docker exec workspace curl http://postgres-container:5432""")
    
#     # SECTION 8: VOLUME MANAGEMENT
#     print("\n\nSECTION 8: VOLUME MANAGEMENT")
#     print("-" * 40)
    
#     print("\nVOLUME STRATEGIES:")
#     print(f"  - Primary: {work_dir} <-> /workspace (Project files)")
#     print(f"  - Config: ~/.config <-> /home/{system_user}/.config (User settings)")
#     print(f"  - Cache: ~/.cache <-> /home/{system_user}/.cache (Build cache)")
#     print(f"  - SSH: ~/.ssh <-> /home/{system_user}/.ssh:ro (Git authentication)")
#     print(f"  - AWS: ~/.aws <-> /home/{system_user}/.aws:ro (Cloud credentials)")
    
#     print("\nNAMED VOLUMES (For databases):")
#     print("""# Create persistent data volumes
# docker volume create postgres-data
# docker volume create redis-data

# # Use with containers
# docker run -d --name postgres \
#   -v postgres-data:/var/lib/postgresql/data \
#   -e POSTGRES_PASSWORD=secret \
#   postgres:15

# docker run -d --name redis \
#   -v redis-data:/data \
#   redis:7-alpine""")
    
#     print("\nBACKUP & RESTORE:")
#     print(f"""# Backup workspace from container
# docker cp {container_name}:/workspace ./workspace-backup-$(date +%Y%m%d)

# # Backup to tar archive
# docker run --rm --volumes-from {container_name} \
#   -v $(pwd):/backup ubuntu tar cvf /backup/workspace.tar /workspace

# # Restore from backup
# docker run --rm --volumes-from {container_name} \
#   -v $(pwd):/backup ubuntu bash -c "cd / && tar xvf /backup/workspace.tar" """)
    
#     # SECTION 9: RESOURCE MANAGEMENT
#     print("\n\nSECTION 9: RESOURCE MANAGEMENT")
#     print("-" * 40)
    
#     print("\nMONITORING COMMANDS:")
#     print(f"# Container statistics")
#     print(f"docker stats {container_name}")
#     print(f"\n# Detailed resource usage")
#     print(f"docker stats {container_name} --format 'table {{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}\\t{{.MemPerc}}\\t{{.NetIO}}\\t{{.BlockIO}}'")
#     print(f"\n# Process list inside container")
#     print(f"docker top {container_name}")
    
#     print("\nRESOURCE LIMITS ADJUSTMENT:")
#     print(f"""# Update limits on running container
# docker update {container_name} \\
#   --memory="8g" \\
#   --memory-swap="10g" \\
#   --cpus="4.0" \\
#   --restart=always""")
    
#     print("\nDEBUGGING RESOURCE ISSUES:")
#     print(f"""# Check container logs
# docker logs {container_name} --tail 100 -f

# # Inspect container configuration
# docker inspect {container_name}

# # Check Docker system resources
# docker system df
# docker system info""")
    
#     # SECTION 10: SECURITY PRACTICES
#     print("\n\nSECTION 10: SECURITY PRACTICES")
#     print("-" * 40)
    
#     print("\nSECURITY RECOMMENDATIONS:")
#     print("  1. Use read-only volumes for credentials (.ssh:ro, .aws:ro)")
#     print("  2. Regularly update base images")
#     print("  3. Scan images for vulnerabilities: docker scan {image_tag}")
#     print("  4. Use Docker Content Trust: export DOCKER_CONTENT_TRUST=1")
#     print("  5. Limit container capabilities")
#     print("  6. Use non-root user inside container")
#     print("  7. Set resource limits to prevent DoS")
    
#     print("\nSECRET MANAGEMENT:")
#     print("""# Use Docker secrets or environment files
# echo "DB_PASSWORD=secret123" > .env
# docker run --env-file .env ...

# # Or use Docker secrets (Swarm mode)
# echo "secret123" | docker secret create db_password -
# docker service create --secret db_password ...""")
    
#     # SECTION 11: TROUBLESHOOTING
#     print("\n\nSECTION 11: TROUBLESHOOTING")
#     print("-" * 40)
    
#     print("\nCOMMON ISSUES & SOLUTIONS:")
#     print(f"""Issue: Container won't start
#   Solution: docker logs {container_name} --tail 50

# Issue: Permission denied on volumes
#   Solution: docker exec -it -u root {container_name} chown -R {system_user}:{system_user} /workspace

# Issue: Port already in use
#   Solution: Change port mapping: -p 8889:8888

# Issue: Out of disk space
#   Solution: docker system prune -a --volumes

# Issue: Slow performance
#   Solution: Increase resources: docker update --memory="8g" --cpus="4" {container_name}

# Issue: Network connectivity
#   Solution: Check firewall: ufw allow 8888/tcp""")
    
#     print("\nDIAGNOSTIC COMMANDS:")
#     print(f"""# Check container health
# docker inspect --format='{{json .State.Health}}' {container_name}

# # Test network connectivity from container
# docker exec {container_name} curl -I http://google.com

# # Check mounted volumes
# docker inspect --format='{{json .Mounts}}' {container_name}

# # View resource usage history
# docker stats {container_name} --no-stream""")


    
#     # SECTION 5: IMAGE VERSIONING AND DEPLOYMENT
#     print("\n\nSECTION 5: IMAGE VERSIONING AND DEPLOYMENT")
#     print("-" * 40)
    
#     print("\nIMAGE VERSIONING STRATEGY:")
#     print(f"""# Build with version tags
# VERSION=1.0.0
# DATE_TAG=$(date +%Y%m%d)

# docker build -t {image_name}:latest \
#              -t {image_name}:$VERSION \
#              -t {image_name}:$DATE_TAG \
#              -t {dockerhub_user}/{image_name}:latest \
#              -t {dockerhub_user}/{image_name}:$VERSION \
#              -t {dockerhub_user}/{image_name}:$DATE_TAG .
             
# # Push all versions
# docker push {dockerhub_user}/{image_name}:latest
# docker push {dockerhub_user}/{image_name}:$VERSION
# docker push {dockerhub_user}/{image_name}:$DATE_TAG""")
    
#     print("\nPULL SPECIFIC VERSIONS ON OTHER MACHINES:")
#     print(f"""# On another developer's machine
# docker pull {dockerhub_user}/{image_name}:latest
# docker pull {dockerhub_user}/{image_name}:v1.0.0
# docker pull {dockerhub_user}/{image_name}:20240115""")
    
#     print("\nUPDATE WORKFLOW:")
#     print(f"""# 1. Update your Dockerfile and rebuild
# docker build -t {image_name}:latest -t {dockerhub_user}/{image_name}:latest .

# # 2. Test the new image
# docker run --rm {image_name}:latest python --version

# # 3. Push to Docker Hub
# docker push {dockerhub_user}/{image_name}:latest

# # 4. Notify team to pull the update
# # 5. Team members run: docker pull {dockerhub_user}/{image_name}:latest""")
    
#     # SECTION 6: BACKUP AND SHARE CONTAINER STATE
#     print("\n\nSECTION 6: BACKUP AND SHARE CONTAINER STATE")
#     print("-" * 40)
    
#     print("\nCOMMIT CONTAINER AS NEW IMAGE:")
#     print(f"""# Save current container state as new image
# docker commit {container_name} {image_name}-snapshot-$(date +%Y%m%d)
# docker commit {container_name} {dockerhub_user}/{image_name}-snapshot:$(date +%Y%m%d)

# # Tag and push the snapshot
# docker tag {image_name}-snapshot-$(date +%Y%m%d) {dockerhub_user}/{image_name}-snapshot:$(date +%Y%m%d)
# docker push {dockerhub_user}/{image_name}-snapshot:$(date +%Y%m%d)""")
    
#     print("\nSAVE AND LOAD IMAGES (FOR OFFLINE TRANSFER):")
#     print(f"""# Save image to tar file
# docker save -o {image_name}-backup.tar {dockerhub_user}/{image_name}:latest
# docker save -o {image_name}-backup.tar {dockerhub_user}/{image_name}:latest {dockerhub_user}/{image_name}:v1.0.0

# # Load image from tar file
# docker load -i {image_name}-backup.tar

# # Share between machines without Docker Hub
# scp {image_name}-backup.tar user@other-machine:~/""")
    
#     # SECTION 7: DOCKER HUB AUTOMATION
#     print("\n\nSECTION 7: DOCKER HUB AUTOMATION")
#     print("-" * 40)
    
#     print("\nAUTOMATED BUILD SCRIPT:")
#     print(f"""#!/bin/bash
# # build-and-push.sh

# set -e  # Exit on error

# VERSION=${{1:-latest}}
# DOCKERHUB_USER="{dockerhub_user}"
# IMAGE_NAME="{image_name}"

# echo "Building image..."
# docker build -t $IMAGE_NAME:$VERSION -t $DOCKERHUB_USER/$IMAGE_NAME:$VERSION .

# echo "Testing image..."
# docker run --rm $IMAGE_NAME:$VERSION python --version

# echo "Pushing to Docker Hub..."
# docker push $DOCKERHUB_USER/$IMAGE_NAME:$VERSION

# echo "Done! Image available at: https://hub.docker.com/r/$DOCKERHUB_USER/$IMAGE_NAME""")
    
#     print("\nGITHUB ACTIONS WORKFLOW FOR DOCKER HUB:")
#     print(f"""# .github/workflows/docker-publish.yml
# name: Docker Build and Push

# on:
#   push:
#     branches: [ main ]
#     tags: [ 'v*' ]

# jobs:
#   build-and-push:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v3
      
#       - name: Docker meta
#         id: meta
#         uses: docker/metadata-action@v4
#         with:
#           images: {dockerhub_user}/{image_name}
#           tags: |
#             type=ref,event=branch
#             type=ref,event=pr
#             type=semver,pattern={{version}}
#             type=semver,pattern={{major}}.{{minor}}
#             type=sha
            
#       - name: Login to Docker Hub
#         uses: docker/login-action@v2
#         with:
#           username: ${{{{ secrets.DOCKERHUB_USERNAME }}}}
#           password: ${{{{ secrets.DOCKERHUB_TOKEN }}}}
          
#       - name: Build and push
#         uses: docker/build-push-action@v4
#         with:
#           context: .
#           push: true
#           tags: ${{{{ steps.meta.outputs.tags }}}}
#           labels: ${{{{ steps.meta.outputs.labels }}}}""")
    
#     # SECTION 8: MULTI-USER COLLABORATION
#     print("\n\nSECTION 8: MULTI-USER COLLABORATION")
#     print("-" * 40)
    
#     print("\nTEAM COLLABORATION WORKFLOW:")
#     print(f"""# Team Lead: Build and push base image
# docker build -t {dockerhub_user}/{image_name}:base .
# docker push {dockerhub_user}/{image_name}:base

# # Team Members: Pull and use
# docker pull {dockerhub_user}/{image_name}:base
# docker run -it --name my-dev {dockerhub_user}/{image_name}:base bash

# # Customize for specific project
# docker commit my-dev {dockerhub_user}/{image_name}:project-x
# docker push {dockerhub_user}/{image_name}:project-x""")
    
#     print("\nIMAGE LAYERS AND CACHING:")
#     print(f"""# Check image layers
# docker history {dockerhub_user}/{image_name}:latest

# # Optimize Dockerfile for caching
# # 1. Put rarely changing layers first
# # 2. Put frequently changing layers last
# # 3. Use multi-stage builds for production""")
    
#     # SECTION 9: SECURITY AND BEST PRACTICES
#     print("\n\nSECTION 9: SECURITY AND BEST PRACTICES")
#     print("-" * 40)
    
#     print("\nSECURITY SCANNING:")
#     print(f"""# Scan image for vulnerabilities
# docker scan {dockerhub_user}/{image_name}:latest

# # Use trusted base images
# docker pull python:3.11-slim  # Instead of python:latest

# # Sign images with Docker Content Trust
# export DOCKER_CONTENT_TRUST=1
# docker push {dockerhub_user}/{image_name}:latest""")
    
#     print("\nPRIVATE REGISTRIES:")
#     print(f"""# Use private registry
# docker tag {image_name}:latest registry.example.com/{dockerhub_user}/{image_name}:latest
# docker push registry.example.com/{dockerhub_user}/{image_name}:latest
# docker pull registry.example.com/{dockerhub_user}/{image_name}:latest""")
    
#     # SECTION 10: TROUBLESHOOTING DOCKER HUB
#     print("\n\nSECTION 10: TROUBLESHOOTING DOCKER HUB")
#     print("-" * 40)
    
#     print("\nCOMMON DOCKER HUB ISSUES:")
#     print(f"""Issue: Permission denied when pushing
#   Solution: docker login
#   Solution: Check if you have push access to {dockerhub_user}/{image_name}

# Issue: Image not found when pulling
#   Solution: Check spelling: docker pull {dockerhub_user}/{image_name}:latest
#   Solution: Check if image exists: https://hub.docker.com/r/{dockerhub_user}/{image_name}

# Issue: Push hangs or times out
#   Solution: Check network connectivity
#   Solution: Increase timeout: docker push --timeout 600s {dockerhub_user}/{image_name}:latest

# Issue: Out of disk space
#   Solution: Clean up: docker system prune -a
#   Solution: Remove specific images: docker rmi {dockerhub_user}/{image_name}:old-tag""")
    
#     print("\nDIAGNOSTIC COMMANDS:")
#     print(f"""# Check Docker Hub rate limits
# docker pull --help | grep -i rate

# # Inspect image details
# docker inspect {dockerhub_user}/{image_name}:latest

# # Check image digest
# docker images --digests | grep {image_name}

# # Test pull without downloading
# docker pull --dry-run {dockerhub_user}/{image_name}:latest""")
    
#     # SECTION 11: CLEANUP & MAINTENANCE
#     print("\n\nSECTION 11: CLEANUP & MAINTENANCE")
#     print("-" * 40)
    
#     print("\nREGULAR MAINTENANCE SCRIPT:")
#     print(f"""#!/bin/bash
# # docker-maintenance.sh

# echo "=== Docker Hub Image Management ==="

# # List all images with Docker Hub tags
# docker images | grep {dockerhub_user}

# # Remove old tags (keep last 5)
# docker images {dockerhub_user}/{image_name} --format "{{{{.Tag}}}}" | sort -V | head -n -5 | \\
#   xargs -I {{}} docker rmi {dockerhub_user}/{image_name}:{{}}

# echo "=== Current Status ==="
# docker system df""")
    
#     print("\nFULL WORKFLOW EXAMPLE:")
#     print(f"""# 1. Build and tag
# docker build -t {image_name}:latest -t {dockerhub_user}/{image_name}:latest .

# # 2. Test locally
# docker run --rm {image_name}:latest python -c "print('Test passed')"

# # 3. Push to Docker Hub
# docker push {dockerhub_user}/{image_name}:latest

# # 4. Pull on another machine
# docker pull {dockerhub_user}/{image_name}:latest

# # 5. Run on another machine
# docker run -it {dockerhub_user}/{image_name}:latest bash""")
    
#     # FINAL NOTES
#     print("\n" + "="*20 + " DOCKER HUB WORKFLOW SUMMARY " + "="*20)
#     print("\nKEY PRINCIPLES:")
#     print("  1. Always tag images with versions (latest, v1.0.0, date)")
#     print(f"  2. Push to Docker Hub: {dockerhub_user}/{image_name}")
#     print(f"  3. Pull from Docker Hub: docker pull {dockerhub_user}/{image_name}:latest")
#     print("  4. Use multi-stage builds for smaller images")
#     print("  5. Scan images regularly for vulnerabilities")
#     print("  6. Use private registries for sensitive projects")
#     print("  7. Automate builds with CI/CD")
    
#     print("\nQUICK REFERENCE:")
#     print(f"  Login: docker login")
#     print(f"  Build: docker build -t {dockerhub_user}/{image_name}:latest .")
#     print(f"  Push: docker push {dockerhub_user}/{image_name}:latest")
#     print(f"  Pull: docker pull {dockerhub_user}/{image_name}:latest")
#     print(f"  Run: docker run -it {dockerhub_user}/{image_name}:latest bash")
    
#     print("\nSUPPORT:")
#     print(f"  Docker Hub: https://hub.docker.com/r/{dockerhub_user}/{image_name}")
#     print(f"  Check images: docker images | grep {dockerhub_user}")
#     print(f"  Test pull: docker pull --dry-run {dockerhub_user}/{image_name}:latest")
#     print(f"  Inspect: docker inspect {dockerhub_user}/{image_name}:latest")
    
#     print("\n" + "="*20 + " END OF PROFESSIONAL GUIDE " + "="*20)


#     # SECTION 12: CLEANUP & MAINTENANCE
#     print("\n\nSECTION 12: CLEANUP & MAINTENANCE")
#     print("-" * 40)
    
#     print("\nREGULAR MAINTENANCE SCRIPT:")
#     print("""#!/bin/bash
# # cleanup.sh - Docker maintenance script

# echo "=== Docker System Cleanup ==="

# # Remove stopped containers
# docker container prune -f

# # Remove dangling images
# docker image prune -f

# # Remove unused volumes (careful!)
# docker volume prune -f

# # Remove unused networks
# docker network prune -f

# # Clean build cache
# docker builder prune -a -f

# echo "=== Current Status ==="
# docker system df""")
    
#     print("\nCONTAINER LIFECYCLE:")
#     print(f"""# Stop container gracefully
# docker stop {container_name}

# # Create backup before removal
# docker commit {container_name} {image_tag}-backup-$(date +%Y%m%d)

# # Remove container (data preserved in volumes)
# docker rm {container_name}

# # Remove image
# docker rmi {image_tag}

# # Full cleanup (DANGER - removes volumes)
# docker system prune -a --volumes -f""")
    
#     print("\nMIGRATION BETWEEN SYSTEMS:")
#     print(f"""# Save container as image
# docker commit {container_name} {image_tag}-migrate

# # Save image to file
# docker save {image_tag}-migrate > workspace-backup.tar

# # Transfer and load on new system
# docker load < workspace-backup.tar

# # Run with same volumes
# docker run -v {work_dir}:/workspace ... {image_tag}-migrate""")
#     # SECTION 12: FZF (FUZZY FINDER) TOOLS
#     print("\n\nSECTION 12: FZF (FUZZY FINDER) TOOLS")
#     print("-" * 40)
    
#     print("\nFZF INTEGRATION WITH DOCKER:")
#     print("""# List containers with fzf
# alias dps='docker ps --format "table {{.ID}}\\t{{.Names}}\\t{{.Status}}\\t{{.Ports}}" | fzf'

# # List all containers (including stopped) with fzf
# alias dpsa='docker ps -a --format "table {{.ID}}\\t{{.Names}}\\t{{.Status}}\\t{{.Ports}}" | fzf'

# # List images with fzf
# alias dim='docker images --format "table {{.Repository}}\\t{{.Tag}}\\t{{.Size}}" | fzf'

# # Select and enter container
# dshell() {
#     container=$(docker ps --format "{{.Names}}" | fzf)
#     [ -n "$container" ] && docker exec -it "$container" bash
# }

# # Select and stop container
# dstop() {
#     container=$(docker ps --format "{{.Names}}" | fzf)
#     [ -n "$container" ] && docker stop "$container"
# }

# # Select and remove container
# drm() {
#     container=$(docker ps -a --format "{{.Names}}" | fzf)
#     [ -n "$container" ] && docker rm "$container"
# }

# # Select and view container logs
# dlogs() {
#     container=$(docker ps --format "{{.Names}}" | fzf)
#     [ -n "$container" ] && docker logs -f "$container"
# }

# # Search in Docker Hub with fzf
# dsearch() {
#     query=$(echo "" | fzf --print-query --prompt="Search Docker Hub: ")
#     [ -n "$query" ] && docker search "$query" | fzf
# }

# # Docker compose services with fzf
# dcomp() {
#     service=$(docker compose ps --services | fzf)
#     [ -n "$service" ] && docker compose logs -f "$service"
# }

# # FZF for file searching inside container
# dfind() {
#     container=$(docker ps --format "{{.Names}}" | fzf)
#     [ -n "$container" ] && read -p "Search pattern: " pattern && docker exec "$container" find /workspace -name "$pattern" 2>/dev/null | fzf
# }

# # FZF for process selection inside container
# dtop() {
#     container=$(docker ps --format "{{.Names}}" | fzf)
#     [ -n "$container" ] && docker exec "$container" ps aux | fzf
# }

# # FZF for volume management
# dvol() {
#     volume=$(docker volume ls --format "{{.Name}}" | fzf)
#     [ -n "$volume" ] && docker volume inspect "$volume" | jq .
# }

# # FZF for network management
# dnet() {
#     network=$(docker network ls --format "{{.Name}}" | fzf)
#     [ -n "$network" ] && docker network inspect "$network" | jq .
# }""")

#     print("\nFZF ENHANCED COMMANDS:")
#     print("""# Enhanced grep with ripgrep and fzf
# alias fzgrep='rg --color=always --line-number --no-heading . | fzf --ansi --height=60%'

# # Enhanced find with fd and fzf
# alias fzfind='fd --type f | fzf --height=60%'

# # Enhanced file preview with bat and fzf
# alias fzcat='fzf --preview "bat --color=always --style=numbers --line-range=:500 {}"'

# # Git with fzf
# alias fzgit='git status --short | fzf --multi --preview "git diff --color=always {+2} | head -200"'

# # Process search with fzf
# alias fzps='ps aux | fzf'

# # History search with fzf
# alias fzh='history | fzf'

# # Directory navigation with fzf
# alias fzcd='cd $(find . -type d | fzf)'""")

#     print("\nFZF CONFIGURATION:")
#     print("""# Add to ~/.bashrc for better fzf experience
# export FZF_DEFAULT_OPTS="--height=60% --layout=reverse --border --preview-window=right:60%"
# export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
# export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
# export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'

# # Color scheme
# export FZF_DEFAULT_OPTS=$FZF_DEFAULT_OPTS'
#  --color=fg:#ebdbb2,bg:#282828,hl:#fabd2f,fg+:#ebdbb2,bg+:#3c3836,hl+:#fabd2f
#  --color=info:#83a598,prompt:#bdae93,spinner:#fabd2f,pointer:#83a598,marker:#fe8019,header:#665c54'""")

#     # SECTION 13: COMPREHENSIVE DEV TOOLS GUIDE
#     print("\n\nSECTION 13: COMPREHENSIVE DEV TOOLS GUIDE")
#     print("-" * 40)
    
#     print("\nMODERN COMMAND REPLACEMENTS:")
#     print("""# Modern replacements for classic commands
# ll          → exa -la --git --icons     # Better ls with git status
# cat         → bat                       # Syntax highlighting cat
# du          → dust                      Interactive disk usage
# df          → duf                       Better df with colors
# ps          → procs                     Better process viewer
# top         → btop                      Beautiful system monitor
# find        → fd                        Faster, simpler find
# grep        → rg (ripgrep)             Faster grep
# http        → httpie                    User-friendly HTTP client
# ping        → mtr                       Traceroute + ping combined
# man         → tldr                      Simplified man pages
# curl        → httpie                    Easier HTTP requests
# nc          → ncat                      Enhanced netcat
# dig         → dog                       Better DNS lookup""")

#     print("\nFILE & DIRECTORY MANAGEMENT:")
#     print("""# Navigation
# z <pattern>     # Smart directory jumping with zoxide
# ranger          # Terminal file manager with Vim keys
# ncdu            # Interactive disk usage analyzer
# tree            # Directory tree visualization

# # Search & find
# fd "*.py"       # Find Python files
# rg "import"     # Search for 'import' in files
# ag "TODO"       # Fast code search
# fzf             # Fuzzy find anything

# # File operations
# rsync -avz source/ dest/  # Advanced file syncing
# sshfs user@host:/path /mnt # Mount remote via SSH
# pv file > newfile         # Progress bar for transfers""")

#     print("\nPYTHON DEVELOPMENT:")
#     print("""# Virtual environments
# python -m venv .venv
# source .venv/bin/activate
# pip install -r requirements.txt

# # Package management
# pipx install tool      # Install Python tools globally
# poetry init           # Modern dependency management
# pdm init              # Fast Python package manager

# # Development tools
# black .              # Auto-format code
# ruff check .        # Ultra-fast linting
# mypy .              # Type checking
# pytest -v           # Run tests
# pre-commit install  # Git hooks
# ipython             # Enhanced REPL
# jupyter lab         # Notebook interface""")

#     print("\nSYSTEM MONITORING & DEBUGGING:")
#     print("""# System monitoring
# htop               # Process viewer
# glances            # All-in-one system monitor
# nethogs            # Network traffic by process
# iftop              # Bandwidth monitoring
# iotop              # Disk I/O monitoring

# # Network tools
# mtr google.com     # Continuous traceroute
# nmap localhost     # Network discovery
# tcpdump -i any     # Packet capture
# socat              # Multipurpose relay

# # Debugging
# strace command     # System call tracing
# ltrace command     # Library call tracing
# gdb program        # Debugger
# valgrind program   # Memory debugging""")

#     print("\nTEXT PROCESSING & DATA:")
#     print("""# JSON/XML/CSV processing
# jq '.key' file.json            # JSON query
# yq e '.key' file.yaml          # YAML query
# xmlstarlet sel -t -v '//tag'  # XML query
# csvsql --query "SELECT *" file.csv  # SQL on CSV
# xsv headers file.csv          # CSV inspection

# # Text manipulation
# sed 's/old/new/g' file        # Stream editor
# awk '{print $1}' file         # Pattern scanning
# cut -d',' -f1 file.csv        # Column extraction
# paste file1 file2             # Merge files
# column -t file                # Column formatting""")

#     print("\nDOCKER & CONTAINER TOOLS:")
#     print("""# Container management
# docker compose up -d          # Start services
# docker exec -it container bash # Enter container
# docker logs -f container      # Follow logs
# docker stats                  # Container resources
# docker system prune -a        # Cleanup

# # Image management
# docker build -t name .
# docker push name:tag
# docker save image > file.tar
# docker load < file.tar

# # Podman (Docker alternative)
# podman run --rm image
# podman build -t name .
# buildah bud -t name .""")

#     print("\nCLOUD & KUBERNETES:")
#     print("""# Kubernetes
# kubectl get pods -A
# kubectl describe pod name
# kubectl logs -f pod
# kubectl exec -it pod -- bash
# kubectl apply -f manifest.yaml
# helm install name chart

# # Cloud CLI
# aws s3 ls
# az vm list
# gcloud compute instances list
# terraform init
# terraform apply""")

#     print("\nTERMINAL ENHANCEMENTS:")
#     print("""# Terminal multiplexers
# tmux new -s session     # New session
# tmux attach -t session  # Attach to session
# tmux ls                 # List sessions
# screen -S session       # Screen alternative

# # Shell enhancements
# zsh                     # Advanced shell
# starship prompt         # Fast cross-shell prompt
# direnv                  # Directory-specific env vars
# fzf-tmux                # FZF in tmux pane

# # Productivity
# tig                     # Git TUI
# ranger                  # File manager TUI
# ncdu                    # Disk usage TUI
# btop                    # Resource monitor TUI""")

#     print("\nSECURITY TOOLS:")
#     print("""# Network security
# nmap -sV target         # Service detection
# ssh-keygen -t ed25519   # Generate SSH key
# openssl s_client -connect host:443  # SSL test
# ncat -l -p 8080         # Open listener
# socat TCP-LISTEN:8080,fork TCP:host:80  # Port forward""")

#     print("\nFUN & PRODUCTIVITY:")
#     print("""# Fun commands
# neofetch                # System info in style
# cowsay "Hello"          # Talking cow
# figlet "TEXT"           # ASCII art
# toilet -f term "BIG"    # Fancy display
# lolcat file             # Rainbow output
# cmatrix                 # Matrix effect
# sl                      # Steam locomotive

# # Productivity
# tldr command            # Simplified help
# cheat command           # Command cheatsheets
# speedtest-cli           # Internet speed test
# youtube-dl URL          # Download videos
# http --download URL     # Download with progress""")

#     print("\nQUICK REFERENCE CARDS:")
#     print("""# Git shortcuts
# gst  = git status
# gco  = git checkout
# gc   = git commit
# gp   = git push
# gl   = git pull
# glog = git log --oneline --graph

# # Docker shortcuts
# dps  = docker ps
# dpsi = docker ps -a
# dim  = docker images
# dlog = docker logs -f
# dex  = docker exec -it

# # Kubernetes shortcuts
# k   = kubectl
# kgp = kubectl get pods
# kdp = kubectl describe pod
# kl  = kubectl logs -f
# ke  = kubectl exec -it""")

#     # FINAL NOTES
#     print("\n" + "="*20 + " DOCKER WORKFLOW SUMMARY " + "="*20)
#     print("\nKEY PRINCIPLES:")
#     print("  1. Everything in /workspace persists via host volume")
#     print("  2. Use virtual environments for Python projects")
#     print("  3. Commit code regularly, container is ephemeral")
#     print("  4. Monitor resources, adjust limits as needed")
#     print("  5. Regular maintenance prevents issues")
#     print("  6. Backup important data outside Docker")
#     print("  7. Security: least privilege, read-only mounts")
    
#     print("\nQUICK REFERENCE:")
#     print(f"  Start: docker start {container_name}")
#     print(f"  Attach: docker exec -it {container_name} bash")
#     print(f"  Jupyter: http://localhost:8888")
#     print(f"  VS Code: Remote-Containers extension")
#     print(f"  Workspace: {work_dir} <-> /workspace")
    
#     print("\nSUPPORT:")
#     print(f"  - Check logs: docker logs {container_name}")
#     print(f"  - Inspect: docker inspect {container_name}")
#     print(f"  - Stats: docker stats {container_name}")
#     print(f"  - Shell access: docker exec -it {container_name} bash")
    
#     print("\n" + "="*20 + " END OF GUIDE " + "="*20)
