#!/usr/bin/env python3
"""
SSH2LS - SSH Multi-Hop Connection Manager

# Direct connection
python ssh2ls.py direct setup myserver --host 192.168.1.100 --user admin --key ~/.ssh/id_rsa

# Or via wizard (choose option 1 for direct connection)
python ssh2ls.py wizard

# Make executable
chmod +x ssh2ls.py

# Run interactive wizard
python ssh2ls.py wizard

# Or use as command
python ssh2ls.py setup denbi --<jumphost>--target <fixed IP>

# Display instructions
python ssh2ls.py display

# Test deNBI setup
python ssh2ls.py test denbi

# Transfer files
python ssh2ls.py transfer upload denbi ./data/ ~/chipseq_data/


1. Regular Setup:

ssh2ls setup myserver --jumphost 192.168.1.100 --target 10.0.0.10
2. Setup with Floating IP:

# Option 1: Using regular setup with floating IP
ssh2ls setup myserver --jumphost 203.0.113.10 --fixed-ip 192.168.1.100 --target 10.0.0.10

# Option 2: Using dedicated floating IP command
ssh2ls setup-with-floating myserver --floating-ip 203.0.113.10 --fixed-ip 192.168.1.100 --target 10.0.0.10
3. Floating IP Management:

bash
# Register floating IP
ssh2ls floating register web-floating --floating-ip 203.0.113.10 --fixed-ip 192.168.1.100

# List floating IPs
ssh2ls floating list

# Test floating IP
ssh2ls floating test web-floating

# Update mapping
ssh2ls floating update web-floating

# Delete floating IP
ssh2ls floating delete web-floating
4. Test Connection (auto-detects floating IP):

# Automatically uses floating IP test if configured
ssh2ls test myserver
5. List Connections (shows floating IP info):

ssh2ls list
# Shows: myserver: ubuntu@203.0.113.10 → ubuntu@10.0.0.10 [Floating: 203.0.113.10]

"""

import os
import sys
import json
import yaml
import argparse
import getpass
import subprocess
import textwrap
import platform
import socket
import stat
import time
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
import shutil
import ipaddress
import tempfile
import hashlib
import secrets
import string

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False
    print("Warning: paramiko not installed. Install with: pip install paramiko")

try:
    import cryptography
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    print("Warning: cryptography not installed. Install with: pip install cryptography")

# ============================================================================
# INSTRUCTION DISPLAY CLASS
# ============================================================================

class InstructionDisplay:
    """Display comprehensive instructions for SSH2LS"""
    
    @staticmethod
    def display_full_instructions():
        """Display comprehensive instructions"""
        print("\n" + "="*80)
        print("📚 SSH2LS - COMPLETE USER GUIDE")
        print("="*80)
        
        print("\n🔹 OVERVIEW:")
        print("SSH2LS is a powerful tool for managing complex SSH connections, especially")
        print("multi-hop setups like deNBI infrastructure. It automates everything from")
        print("key management to file transfers through jump hosts.")
        
        print("\n" + "="*80)
        print("QUICK START")
        print("="*80)
        
        print("\n1. Interactive Wizard (Recommended for beginners):")
        print("   python ssh2ls.py wizard")
        print("   python ssh2ls.py                    # Defaults to wizard mode")
        
        print("\n2. Automated deNBI Setup (specific setup):")
        print("   python ssh2ls.py setup denbi \\")
        print("     --jumphost 193.196.20.189 \\")
        print("     --jumphost-user ubuntu \\")
        print("     --target 192.168.54.219 \\")
        print("     --key ~/.ssh/denbi")
        
        print("\n3. Connect to deNBI VM:")
        print("   python ssh2ls.py connect denbi --hop target")
        
        print("\n" + "="*80)
        print("COMMAND REFERENCE")
        print("="*80)
        
        print("\n🔸 SETUP COMMANDS:")
        print("  wizard                    Interactive setup wizard")
        print("  setup <name>              Setup new connection")
        print("    --jumphost IP            Jumphost IP address")
        print("    --jumphost-user USER     Jumphost username (default: ubuntu)")
        print("    --target IP              Target VM IP")
        print("    --target-user USER       Target username")
        print("    --key PATH               Private key path")
        
        print("\n🔸 CONNECTION COMMANDS:")
        print("  connect <name>            Connect to host")
        print("    --hop [jumphost|target]  Which host to connect to (default: target)")
        print("  test <name>               Test connection")
        print("  list                      List all connections")
        
        print("\n🔸 FILE TRANSFER COMMANDS:")
        print("  transfer upload <name> <source> <dest>")
        print("  transfer download <name> <source> <dest>")
        
        print("\n🔸 ENVIRONMENT COMMANDS:")
        print("  setup-env <name>          Setup remote environment")
        print("    --template [basic|bioinfo|docker|python]")
        
        print("\n🔸 TUNNEL COMMANDS:")
        print("  tunnel create <name> <local> <remote_host> <remote_port>")
        print("  tunnel start <tunnel_name>")
        print("  tunnel stop <tunnel_name>")
        
        print("\n🔸 UTILITY COMMANDS:")
        print("  quick <name>              Show quick commands for connection")
        print("  display                   Show these instructions")
        print("  help                      Show help message")
        
        print("\n🔸 EXPORT COMMANDS:")
        print("  export ssh                Export as SSH config")
        print("  export json               Export as JSON")
        print("  export yaml               Export as YAML")
        print("  export ansible            Export as Ansible inventory")
        print("  export csv                Export as CSV")
        
        print("\n" + "="*80)
        print("🎯 REAL-WORLD EXAMPLES (FROM NOTES)")
        print("="*80)
        
        print("\n📝 EXAMPLE 1: Complete deNBI Setup Workflow")
        print("-" * 40)
        print("# 1. Generate SSH key (if not done already)")
        print("ssh-keygen -t ed25519 -f ~/.ssh/denbi -C 'your_email@example.com'")
        print()
        print("# 2. Share public key with admin (Mohamad)")
        print("cat ~/.ssh/denbi.pub")
        print("# Send this output to admin to add to jumphost")
        print()
        print("# 3. Setup connection with ssh2ls")
        print("python ssh2ls.py setup denbi \\")
        print("  --jumphost 193.196.20.189 \\")
        print("  --jumphost-user ubuntu \\")
        print("  --target 192.168.54.219 \\")
        print("  --key ~/.ssh/denbi")
        print()
        print("# 4. Add key to SSH agent")
        print("ssh-add ~/.ssh/denbi")
        print()
        print("# 5. Test the connection")
        print("python ssh2ls.py test denbi")
        print()
        print("# 6. Connect to target VM")
        print("python ssh2ls.py connect denbi --hop target")
        
        print("\n📝 EXAMPLE 2: File Transfer Through Jumphost")
        print("-" * 40)
        print("# Upload local data to remote VM")
        print("python ssh2ls.py transfer upload denbi \\")
        print("  ./fastq_files/ \\")
        print("  /home/ubuntu/chipseq_data/")
        print()
        print("# Download results from VM")
        print("python ssh2ls.py transfer download denbi \\")
        print("  /home/ubuntu/chipseq_data/results/ \\")
        print("  ./local_results/")
        
        print("\n📝 EXAMPLE 3: Setup Bioinformatics Environment")
        print("-" * 40)
        print("# Setup nf-core environment on remote VM")
        print("python ssh2ls.py setup-env denbi --template bioinfo")
        print()
        print("# Manual alternative (what this does):")
        print("ssh -A -i ~/.ssh/denbi -J ubuntu@193.196.20.189 ubuntu@192.168.54.219")
        print("# Then on the remote VM:")
        print("sudo apt update && sudo apt upgrade -y")
        print("sudo apt install -y git wget curl python3 python3-pip")
        print("sudo apt install -y apptainer")
        print("mkdir -p ~/chipseq_data")
        
        print("\n" + "="*80)
        print("🔧 TROUBLESHOOTING COMMON ISSUES")
        print("="*80)
        
        print("\n❌ Issue: Permission denied (publickey)")
        print("Solution:")
        print("  1. Check key is added to agent: ssh-add -l")
        print("  2. Add key: ssh-add ~/.ssh/your_key")
        print("  3. Verify public key is on jumphost")
        print("  4. Check key permissions: chmod 600 ~/.ssh/your_key")
        
        print("\n❌ Issue: SSH agent not running")
        print("Solution:")
        print("  eval $(ssh-agent)")
        print("  ssh-add ~/.ssh/your_key")
        
        print("\n❌ Issue: Connection timeout to jumphost")
        print("Solution:")
        print("  1. Check network connectivity")
        print("  2. Verify jumphost IP: 193.196.20.189")
        print("  3. Check firewall rules")
        print("  4. Test with: ping 193.196.20.189")
        
        print("\n❌ Issue: Can't connect from jumphost to target")
        print("Solution:")
        print("  1. Verify target IP: 192.168.54.219")
        print("  2. Check if you're on jumphost: ssh ubuntu@193.196.20.189")
        print("  3. From jumphost, test: ping 192.168.54.219")
        print("  4. Check agent forwarding: ssh-add -l (on jumphost)")
        
        print("\n" + "="*80)
        print("✅ GETTING STARTED CHECKLIST")
        print("="*80)
        
        checklist = [
            ("Generate SSH key pair", "ssh-keygen -t ed25519 -f ~/.ssh/denbi"),
            ("Share public key with admin", "cat ~/.ssh/denbi.pub"),
            ("Add key to SSH agent", "ssh-add ~/.ssh/denbi"),
            ("Test jumphost connection", "ssh -A -i ~/.ssh/denbi ubuntu@193.196.20.189"),
            ("Setup ssh2ls connection", "python ssh2ls.py setup denbi [options]"),
            ("Test full connection", "python ssh2ls.py test denbi"),
            ("Transfer test file", "python ssh2ls.py transfer upload denbi test.txt ~/"),
            ("Setup remote environment", "python ssh2ls.py setup-env denbi --template bioinfo"),
        ]
        
        for i, (item, cmd) in enumerate(checklist, 1):
            print(f"{i}. {item}")
            print(f"   Command: {cmd}")
        
        print("\n" + "="*80)
        print("🎉 You're ready to use SSH2LS! Start with: python ssh2ls.py wizard")
        print("="*80 + "\n")
    
    @staticmethod
    def display_deNBI_specific():
        """Display deNBI-specific instructions"""
        print("\n" + "="*80)
        print("🎯 deNBI SPECIFIC SETUP INSTRUCTIONS")
        print("="*80)
        
        print("\nSPECIFIC CONFIGURATION:")
        print("-" * 40)
        print("Jumphost:      ubuntu@193.196.20.189")
        print("Target VM:      ubuntu@192.168.54.219")
        print("Private key:    ~/.ssh/denbi")
        print("Purpose:        nf-core ChIP-seq analysis")
        
        print("\nCOMPLETE WORKFLOW:")
        print("-" * 40)
        print("1. KEY EXCHANGE:")
        print("   - Generate key: ssh-keygen -t ed25519 -f ~/.ssh/denbi")
        print("   - Share public key with Mohamad:")
        print("     cat ~/.ssh/denbi.pub")
        print("   - Wait for confirmation that key is added to jumphost")
        
        print("\n2. INITIAL SETUP:")
        print("   # Add key to agent")
        print("   ssh-add ~/.ssh/denbi")
        print("   ")
        print("   # Test jumphost connection")
        print("   ssh -A -i ~/.ssh/denbi ubuntu@193.196.20.189")
        print("   # You should see Ubuntu welcome message")
        print("   ")
        print("   # From jumphost, test target connection")
        print("   ssh ubuntu@192.168.54.219")
        print("   # Should connect without password")
        
        print("\n3. AUTOMATE WITH SSH2LS:")
        print("   # Run the setup wizard")
        print("   python ssh2ls.py wizard")
        print("   ")
        print("   # OR use quick setup")
        print("   python ssh2ls.py setup denbi \\")
        print("     --jumphost 193.196.20.189 \\")
        print("     --jumphost-user ubuntu \\")
        print("     --target 192.168.54.219 \\")
        print("     --key ~/.ssh/denbi")
        
        print("\n4. TRANSFER DATA:")
        print("   # Create directory structure")
        print("   python ssh2ls.py setup-env denbi --template bioinfo")
        print("   ")
        print("   # Upload FASTQ files")
        print("   python ssh2ls.py transfer upload denbi \\")
        print("     /path/to/your/fastq/files/ \\")
        print("     /home/ubuntu/chipseq_data/")
        
        print("\n5. RUN nf-core ChIP-seq:")
        print("   # Connect to VM")
        print("   python ssh2ls.py connect denbi --hop target")
        print("   ")
        print("   # On the VM:")
        print("   # Pull container")
        print("   apptainer pull docker://nfcore/chipseq")
        print("   ")
        print("   # Run pipeline")
        print("   apptainer exec nfcore_chipseq_latest.sif \\")
        print("     nextflow run nf-core/chipseq \\")
        print("     -r 2.1.0 \\")
        print("     -profile standard \\")
        print("     --input ~/chipseq_data/samplesheet.csv \\")
        print("     --genome GRCh38 \\")
        print("     --outdir ~/chipseq_results/")
        
        print("\n" + "="*80)
        print("🔧 TROUBLESHOOTING deNBI SETUP")
        print("="*80)
        
        print("\n❌ 'Permission denied' when connecting to jumphost")
        print("Solution:")
        print("   1. Verify key was added to jumphost by admin")
        print("   2. Check key is in agent: ssh-add -l")
        print("   3. Test with: ssh -v -i ~/.ssh/denbi ubuntu@193.196.20.189")
        
        print("\n❌ Can't connect from jumphost to target")
        print("Solution:")
        print("   1. On jumphost, check if agent has keys: ssh-add -l")
        print("   2. Test direct connection from jumphost:")
        print("      ssh -v ubuntu@192.168.54.219")
        print("   3. Check network: ping 192.168.54.219")
        
        print("\n❌ File transfer fails")
        print("Solution:")
        print("   1. Check ProxyJump is working")
        print("   2. Test with small file first")
        print("   3. Use verbose mode: scp -v ...")
        
        print("\n" + "="*80)
        print("✅ deNBI Setup Complete!")
        print("="*80 + "\n")
    
    @staticmethod
    def display_cheatsheet():
        """Display SSH2LS cheatsheet"""
        print("\n" + "="*80)
        print("📖 SSH2LS CHEATSHEET")
        print("="*80)
        
        print("\n🔑 KEY MANAGEMENT:")
        print("  ssh-keygen -t ed25519 -f ~/.ssh/denbi")
        print("  ssh-add ~/.ssh/denbi")
        print("  ssh-add -l")
        print("  ssh-add -d ~/.ssh/denbi")
        
        print("\nCONNECTION:")
        print("  # Direct methods")
        print("  ssh -A -i ~/.ssh/denbi ubuntu@193.196.20.189")
        print("  ssh -A -i ~/.ssh/denbi -J ubuntu@193.196.20.189 ubuntu@192.168.54.219")
        print("  ")
        print("  # Using ssh2ls")
        print("  python ssh2ls.py connect denbi --hop jumphost")
        print("  python ssh2ls.py connect denbi --hop target")
        
        print("\n📁 FILE TRANSFER:")
        print("  # Manual")
        print("  scp -r -o ProxyJump=ubuntu@193.196.20.189 \\")
        print("    -i ~/.ssh/denbi local_file ubuntu@192.168.54.219:remote_path")
        print("  ")
        print("  # Using ssh2ls")
        print("  python ssh2ls.py transfer upload denbi local_path remote_path")
        print("  python ssh2ls.py transfer download denbi remote_path local_path")
        
        print("\nTUNNELS:")
        print("  # Create web tunnel")
        print("  ssh -N -L 8080:localhost:80 \\")
        print("    -i ~/.ssh/denbi \\")
        print("    -J ubuntu@193.196.20.189 \\")
        print("    ubuntu@192.168.54.219")
        print("  ")
        print("  # Using ssh2ls")
        print("  python ssh2ls.py tunnel create denbi 8080 localhost 80")
        print("  python ssh2ls.py tunnel start denbi_tunnel_8080_80")
        
        print("\n⚙️  ENVIRONMENT:")
        print("  python ssh2ls.py setup-env denbi --template bioinfo")
        print("  python ssh2ls.py setup-env denbi --template docker")
        print("  python ssh2ls.py setup-env denbi --template python")
        
        print("\n🔍 DEBUGGING:")
        print("  ssh -vvv denbi                    # Verbose level 3")
        print("  ssh -O check denbi               # Check connection")
        print("  python ssh2ls.py test denbi      # Test with ssh2ls")
        print("  tail -f ~/.ssh/config            # Monitor config")
        
        print("\n📝 USEFUL ALIASES (add to ~/.bashrc or ~/.zshrc):")
        print("  alias denbi='ssh denbi'")
        print("  alias denbi-jump='ssh -A -i ~/.ssh/denbi ubuntu@193.196.20.189'")
        print("  alias denbi-vm='ssh -A -i ~/.ssh/denbi -J ubuntu@193.196.20.189 ubuntu@192.168.54.219'")
        print("  alias denbi-copy='scp -r -o ProxyJump=ubuntu@193.196.20.189 -i ~/.ssh/denbi'")
        
        print("\n" + "="*80)
        print("CONFIGURATION FILES")
        print("="*80)
        
        print("\n~/.ssh/config (generated by ssh2ls):")
        print("-" * 40)
        print("Host denbi_jumphost")
        print("    HostName 193.196.20.189")
        print("    User ubuntu")
        print("    IdentityFile ~/.ssh/denbi")
        print("    ForwardAgent yes")
        print("")
        print("Host denbi")
        print("    HostName 192.168.54.219")
        print("    User ubuntu")
        print("    ProxyJump denbi_jumphost")
        
        print("\n" + "="*80 + "\n")
# ============================================================================
# FLOATING IP MANAGER
# ============================================================================

class FloatingIPManager:
    """Manages floating IPs and dynamic IP addresses"""
    
    def __init__(self, config_dir: str = "~/.ssh/ssh2ls"):
        self.config_dir = Path(config_dir).expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.floating_ips_file = self.config_dir / "floating_ips.json"
        self.floating_ips = self.load_floating_ips()
    
    def load_floating_ips(self) -> Dict:
        """Load floating IP configurations"""
        if self.floating_ips_file.exists():
            try:
                with open(self.floating_ips_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load floating IPs: {e}")
        return {}
    
    def save_floating_ips(self):
        """Save floating IP configurations"""
        try:
            with open(self.floating_ips_file, 'w') as f:
                json.dump(self.floating_ips, f, indent=2)
        except Exception as e:
            print(f"Error saving floating IPs: {e}")
    
    def register_floating_ip(self, name: str, floating_ip: str, 
                           fixed_ip: str = None, description: str = "",
                           cloud_provider: str = "", region: str = "") -> Dict:
        """Register a floating IP configuration"""
        config = {
            "name": name,
            "floating_ip": floating_ip,
            "fixed_ip": fixed_ip,
            "description": description,
            "cloud_provider": cloud_provider,
            "region": region,
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "status": "unknown"
        }
        
        self.floating_ips[name] = config
        self.save_floating_ips()
        
        print(f"✓ Registered floating IP '{name}':")
        print(f"  Floating IP: {floating_ip}")
        if fixed_ip:
            print(f"  Fixed IP:    {fixed_ip}")
        if description:
            print(f"  Description: {description}")
        
        return config
    
    def detect_current_ip(self, floating_ip_config: Dict) -> Optional[str]:
        """Detect current IP mapping for floating IP"""
        floating_ip = floating_ip_config["floating_ip"]
        fixed_ip = floating_ip_config.get("fixed_ip")
        
        print(f"\n🔍 Detecting IP mapping for {floating_ip}...")
        
        # Method 1: DNS resolution
        try:
            resolved = socket.gethostbyname(floating_ip)
            if resolved != floating_ip:
                print(f"  DNS resolution: {floating_ip} → {resolved}")
                return resolved
        except socket.gaierror:
            pass
        
        # Method 2: Ping and trace (if fixed_ip is known)
        if fixed_ip:
            # Check if floating IP responds to ping
            if self._ping_ip(floating_ip):
                print(f"  ✓ {floating_ip} is reachable")
                # Try to see if it maps to fixed IP
                if self._compare_hosts(floating_ip, fixed_ip):
                    print(f"  ✓ Appears to map to {fixed_ip}")
                    return fixed_ip
        
        # Method 3: SSH connection test
        if fixed_ip:
            # Try to connect via both IPs and compare
            floating_result = self._test_ssh_connection(floating_ip, "ubuntu", None, timeout=3)
            fixed_result = self._test_ssh_connection(fixed_ip, "ubuntu", None, timeout=3)
            
            if floating_result and fixed_result:
                # Both respond, check if they're the same host
                if self._are_same_host(floating_ip, fixed_ip):
                    print(f"  ✓ {floating_ip} and {fixed_ip} appear to be same host")
                    return fixed_ip
        
        print(f"  Could not determine mapping for {floating_ip}")
        return None
    
    def _ping_ip(self, ip: str) -> bool:
        """Ping an IP address"""
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', '-W', '1', ip]
            result = subprocess.run(command, capture_output=True, text=True, timeout=2)
            return result.returncode == 0
        except:
            return False
    
    def _test_ssh_connection(self, host: str, user: str, key_path: str = None, 
                           timeout: int = 5) -> bool:
        """Test SSH connection to host"""
        try:
            cmd = ['ssh', '-o', f'ConnectTimeout={timeout}',
                   '-o', 'BatchMode=yes',
                   '-o', 'StrictHostKeyChecking=no']
            
            if key_path:
                cmd.extend(['-i', key_path])
            
            cmd.extend([f'{user}@{host}', 'echo ping'])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
            return result.returncode == 0
        except:
            return False
    
    def _compare_hosts(self, ip1: str, ip2: str) -> bool:
        """Compare if two IPs appear to be the same host"""
        # This is a heuristic - we can't be 100% sure without proper access
        # Compare ping response times or other characteristics
        return True  # Simplified for now
    
    def _are_same_host(self, ip1: str, ip2: str) -> bool:
        """Check if two IPs point to the same host"""
        # Try to get hostname from both
        try:
            hostname1 = socket.gethostbyaddr(ip1)[0]
            hostname2 = socket.gethostbyaddr(ip2)[0]
            return hostname1 == hostname2
        except:
            return False
    
    def update_floating_ip_status(self, name: str) -> Dict:
        """Update floating IP status and mapping"""
        if name not in self.floating_ips:
            raise KeyError(f"Floating IP '{name}' not found")
        
        config = self.floating_ips[name]
        current_ip = self.detect_current_ip(config)
        
        if current_ip:
            config["current_mapping"] = current_ip
            config["last_checked"] = datetime.now().isoformat()
            config["status"] = "active"
            
            if current_ip == config.get("fixed_ip"):
                config["status"] = "mapped_to_fixed"
            elif current_ip:
                config["status"] = f"mapped_to_{current_ip}"
        else:
            config["status"] = "unreachable"
            config["last_checked"] = datetime.now().isoformat()
        
        self.floating_ips[name] = config
        self.save_floating_ips()
        
        return config
    
    def list_floating_ips(self) -> List[Dict]:
        """List all floating IP configurations"""
        return list(self.floating_ips.values())
    
    def get_floating_ip(self, name: str) -> Optional[Dict]:
        """Get floating IP configuration"""
        return self.floating_ips.get(name)
    
    def delete_floating_ip(self, name: str) -> bool:
        """Delete floating IP configuration"""
        if name in self.floating_ips:
            del self.floating_ips[name]
            self.save_floating_ips()
            return True
        return False
# ============================================================================
# SSH HOST CONFIGURATION
# ============================================================================

@dataclass
class SSHHost:
    """Represents an SSH host configuration"""
    name: str
    hostname: str
    user: str = "ubuntu"
    port: int = 22
    identity_file: Optional[str] = None
    proxy_jump: Optional[str] = None
    forward_agent: bool = True
    is_direct: bool = False  # True for direct connections, False for jumphost/proxy
    connection_type: str = "auto"  # "direct", "jumphost", or "auto"
    # Floating IP support
    floating_ip: Optional[str] = None
    fixed_ip: Optional[str] = None
    use_floating_ip: bool = False
    detect_ip_automatically: bool = True
    forward_x11: bool = False
    compression: bool = False
    server_alive_interval: int = 30
    server_alive_count_max: int = 3
    strict_host_key_checking: str = "yes"
    user_known_hosts_file: str = "~/.ssh/known_hosts"
    control_master: bool = False
    control_path: str = "~/.ssh/controlmasters/%r@%h:%p"
    control_persist: str = "5m"
    reconnect: bool = True
    escape_char: str = "~"
    log_level: str = "INFO"
    tunnel: Optional[str] = None
    local_forward: List[str] = field(default_factory=list)
    remote_forward: List[str] = field(default_factory=list)
    dynamic_forward: Optional[str] = None
    send_env: List[str] = field(default_factory=list)
    set_env: Dict[str, str] = field(default_factory=dict)
    preferred_authentications: str = "publickey,password"
    host_key_algorithms: Optional[str] = None
    kex_algorithms: Optional[str] = None
    ciphers: Optional[str] = None
    macs: Optional[str] = None
    batch_mode: bool = False
    connect_timeout: int = 30
    connect_retries: int = 3
    custom_options: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    description: str = ""
    groups: List[str] = field(default_factory=list)
    created: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    
    def get_effective_hostname(self) -> str:
        """Get the hostname to use for connection"""
        if self.use_floating_ip and self.floating_ip:
            return self.floating_ip
        return self.hostname
    
    def to_ssh_config(self) -> str:
        """Convert host configuration to SSH config format"""
        lines = [f"Host {self.name}"]
        
        if self.description:
            lines.append(f"    # {self.description}")
        
        # Use effective hostname
        effective_host = self.get_effective_hostname()
        
        # Basic settings
        lines.append(f"    HostName {self.hostname}")
        lines.append(f"    User {self.user}")
        if self.port != 22:
            lines.append(f"    Port {self.port}")
        
        # Authentication
        if self.identity_file:
            lines.append(f"    IdentityFile {self.identity_file}")
        
        # Proxy/Jump host
        if self.proxy_jump and not self.is_direct:
            lines.append(f"    ProxyJump {self.proxy_jump}")
        
        # Connection settings
        if self.forward_agent:
            lines.append("    ForwardAgent yes")
        if self.forward_x11:
            lines.append("    ForwardX11 yes")
        if self.compression:
            lines.append("    Compression yes")
        
        # Timeout and keepalive
        lines.append(f"    ServerAliveInterval {self.server_alive_interval}")
        lines.append(f"    ServerAliveCountMax {self.server_alive_count_max}")
        
        # Security
        lines.append(f"    StrictHostKeyChecking {self.strict_host_key_checking}")
        lines.append(f"    UserKnownHostsFile {self.user_known_hosts_file}")
        
        # Comment about floating IP if used
        if self.use_floating_ip and self.floating_ip:
            if self.fixed_ip:
                lines.append(f"    # Floating IP: {self.floating_ip} (maps to {self.fixed_ip})")
            else:
                lines.append(f"    # Floating IP: {self.floating_ip}")
        # ControlMaster for persistent connections
        if self.control_master:
            lines.append("    ControlMaster auto")
            lines.append(f"    ControlPath {self.control_path}")
            lines.append(f"    ControlPersist {self.control_persist}")
        
        # Tunnels and port forwarding
        if self.tunnel:
            lines.append(f"    Tunnel {self.tunnel}")
        for lf in self.local_forward:
            lines.append(f"    LocalForward {lf}")
        for rf in self.remote_forward:
            lines.append(f"    RemoteForward {rf}")
        if self.dynamic_forward:
            lines.append(f"    DynamicForward {self.dynamic_forward}")
        
        # Environment
        if self.send_env:
            lines.append(f"    SendEnv {' '.join(self.send_env)}")
        for key, value in self.set_env.items():
            lines.append(f"    SetEnv {key}={value}")
        
        # Algorithms and ciphers
        if self.preferred_authentications:
            lines.append(f"    PreferredAuthentications {self.preferred_authentications}")
        if self.host_key_algorithms:
            lines.append(f"    HostKeyAlgorithms {self.host_key_algorithms}")
        if self.kex_algorithms:
            lines.append(f"    KexAlgorithms {self.kex_algorithms}")
        if self.ciphers:
            lines.append(f"    Ciphers {self.ciphers}")
        if self.macs:
            lines.append(f"    MACs {self.macs}")
        
        # Connection settings
        if self.batch_mode:
            lines.append("    BatchMode yes")
        lines.append(f"    ConnectTimeout {self.connect_timeout}")
        
        # Escape character
        if self.escape_char:
            lines.append(f"    EscapeChar {self.escape_char}")
        
        # Logging
        if self.log_level:
            lines.append(f"    LogLevel {self.log_level}")
        
        # Custom options
        for key, value in self.custom_options.items():
            lines.append(f"    {key} {value}")
        
        return "\n".join(lines)
    
    def get_connection_info(self) -> Dict:
        """Get connection information"""
        return {
            "name": self.name,
            "effective_host": self.get_effective_hostname(),
            "user": self.user,
            "port": self.port,
            "floating_ip": self.floating_ip if self.use_floating_ip else None,
            "fixed_ip": self.fixed_ip,
            "description": self.description
        }

@dataclass
class SSHConfig:
    """Manages SSH configuration"""
    hosts: Dict[str, SSHHost] = field(default_factory=dict)
    global_options: Dict[str, str] = field(default_factory=dict)
    includes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_host(self, host: SSHHost):
        """Add a host to configuration"""
        self.hosts[host.name] = host
    
    def remove_host(self, hostname: str):
        """Remove a host from configuration"""
        if hostname in self.hosts:
            del self.hosts[hostname]
    
    def find_hosts(self, pattern: str = None, tag: str = None, group: str = None) -> List[SSHHost]:
        """Find hosts by pattern, tag, or group"""
        results = []
        for host in self.hosts.values():
            if pattern and pattern.lower() not in host.name.lower():
                continue
            if tag and tag not in host.tags:
                continue
            if group and group not in host.groups:
                continue
            results.append(host)
        return results
    
    def to_ssh_config(self) -> str:
        """Generate complete SSH config file"""
        lines = []
        
        # Global options
        if self.global_options:
            lines.append("Host *")
            for key, value in self.global_options.items():
                lines.append(f"    {key} {value}")
            lines.append("")  # Empty line
        
        # Includes
        if self.includes:
            for include in self.includes:
                lines.append(f"Include {include}")
            lines.append("")
        
        # Host configurations
        for host in sorted(self.hosts.values(), key=lambda h: h.name):
            lines.append(host.to_ssh_config())
            lines.append("")  # Empty line between hosts
        
        return "\n".join(lines).strip()
    
    def save(self, filename: str = "~/.ssh/config"):
        """Save configuration to file"""
        path = Path(filename).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing config
        if path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = path.with_name(f"config.backup.{timestamp}")
            shutil.copy2(path, backup_path)
            print(f"✓ Backup created: {backup_path}")
        
        path.write_text(self.to_ssh_config())
        print(f"✓ Configuration saved to {path}")
    
    def load(self, filename: str = "~/.ssh/config"):
        """Load configuration from file"""
        path = Path(filename).expanduser()
        if not path.exists():
            return
        
        current_host = None
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('Host '):
                    if current_host:
                        self.add_host(current_host)
                    hostnames = line[5:].split()
                    current_host = SSHHost(name=hostnames[0], hostname="")
                elif current_host and ' ' in line:
                    key, value = line.split(maxsplit=1)
                    self._set_host_attribute(current_host, key, value)
            
            if current_host:
                self.add_host(current_host)
    
    def _set_host_attribute(self, host: SSHHost, key: str, value: str):
        """Set host attribute based on SSH config key"""
        attr_map = {
            "HostName": "hostname",
            "User": "user",
            "Port": "port",
            "IdentityFile": "identity_file",
            "ProxyJump": "proxy_jump",
            "ForwardAgent": "forward_agent",
            "ForwardX11": "forward_x11",
            "Compression": "compression",
            "ServerAliveInterval": "server_alive_interval",
            "ServerAliveCountMax": "server_alive_count_max",
            "StrictHostKeyChecking": "strict_host_key_checking",
            "UserKnownHostsFile": "user_known_hosts_file",
            "ControlMaster": "control_master",
            "ControlPath": "control_path",
            "ControlPersist": "control_persist",
            "Tunnel": "tunnel",
            "LocalForward": "local_forward",
            "RemoteForward": "remote_forward",
            "DynamicForward": "dynamic_forward",
            "SendEnv": "send_env",
            "SetEnv": "set_env",
            "PreferredAuthentications": "preferred_authentications",
            "HostKeyAlgorithms": "host_key_algorithms",
            "KexAlgorithms": "kex_algorithms",
            "Ciphers": "ciphers",
            "MACs": "macs",
            "BatchMode": "batch_mode",
            "ConnectTimeout": "connect_timeout",
            "EscapeChar": "escape_char",
            "LogLevel": "log_level",
        }
        
        if key in attr_map:
            attr_name = attr_map[key]
            if hasattr(host, attr_name):
                current_value = getattr(host, attr_name)
                
                # Handle boolean values
                if isinstance(current_value, bool):
                    setattr(host, attr_name, value.lower() in ['yes', 'true', '1'])
                # Handle integer values
                elif isinstance(current_value, int):
                    try:
                        setattr(host, attr_name, int(value))
                    except ValueError:
                        setattr(host, attr_name, value)
                # Handle list values (like LocalForward, RemoteForward)
                elif isinstance(current_value, list):
                    if key in ["LocalForward", "RemoteForward", "SendEnv"]:
                        current_value.append(value)
                else:
                    setattr(host, attr_name, value)

# ============================================================================
# SSH KEY MANAGER
# ============================================================================

class SSHKeyManager:
    """Manages SSH keys including generation, loading, and agent operations"""
    
    def __init__(self, ssh_dir: str = "~/.ssh"):
        self.ssh_dir = Path(ssh_dir).expanduser()
        self.ssh_dir.mkdir(parents=True, exist_ok=True)
        self.agent_socket = os.environ.get('SSH_AUTH_SOCK')
        self.key_cache = {}
    
    def generate_key_pair(self, key_name: str = None, key_type: str = "ed25519", 
                         key_size: int = 4096, passphrase: str = None, 
                         comment: str = None) -> Tuple[Path, Path]:
        """
        Generate SSH key pair with specified parameters
        Returns: (private_key_path, public_key_path)
        """
        if not HAS_PARAMIKO:
            print("✗ Paramiko not installed. Install with: pip install paramiko")
            raise ImportError("Paramiko required for key generation")
        
        if not key_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            key_name = f"id_{key_type}_{timestamp}"
        
        private_key_path = self.ssh_dir / key_name
        public_key_path = private_key_path.with_suffix('.pub')
        
        if private_key_path.exists():
            raise FileExistsError(f"Key {private_key_path} already exists")
        
        # Generate key using paramiko
        try:
            if key_type == "rsa":
                key = paramiko.RSAKey.generate(bits=key_size)
            elif key_type == "ed25519":
                try:
                    key = paramiko.Ed25519Key.generate()
                except AttributeError: 
                    print("⚠️  Paramiko doesn't support Ed25519, using ssh-keygen instead...")
                    return self._generate_key_with_ssh_keygen(
                        key_name=key_name,
                        key_type=key_type,
                        private_key_path=private_key_path,
                        public_key_path=public_key_path,
                        comment=comment,
                        passphrase=passphrase
                    )
            elif key_type == "ecdsa":
                key = paramiko.ECDSAKey.generate()
            else:
                raise ValueError(f"Unsupported key type: {key_type}")
            
            # Save private key
            if passphrase:
                key.write_private_key_file(str(private_key_path), password=passphrase)
            else:
                key.write_private_key_file(str(private_key_path))
            
            # Save public key
            if not comment:
                comment = f"{getpass.getuser()}@{socket.gethostname()}"
            
            with open(public_key_path, 'w') as f:
                f.write(f"{key.get_name()} {key.get_base64()} {comment}")
            
            # Set proper permissions
            private_key_path.chmod(0o600)
            public_key_path.chmod(0o644)
            
            print(f"✓ Generated key pair:")
            print(f"  Private: {private_key_path}")
            print(f"  Public:  {public_key_path}")
            print(f"  Comment: {comment}")
            
            # Show public key for easy copying
            print(f"\nPublic key (copy this to share):")
            print("-" * 80)
            with open(public_key_path, 'r') as f:
                print(f.read().strip())
            print("-" * 80)
            
            return private_key_path, public_key_path
            
        except Exception as e:
            print(f"✗ Error generating key with paramiko: {e}")
            print("⚠️  Trying fallback to ssh-keygen command...")
            return self._generate_key_with_ssh_keygen(
                key_name=key_name,
                key_type=key_type,
                private_key_path=private_key_path,
                public_key_path=public_key_path,
                comment=comment,
                passphrase=passphrase
            )
    
    
    def _generate_key_with_ssh_keygen(self, key_name: str, key_type: str,
                                     private_key_path: Path, public_key_path: Path,
                                     comment: str, passphrase: str = None) -> Tuple[Path, Path]:
        """Generate key using ssh-keygen command (fallback)"""
        try:
            if not comment:
                comment = f"{getpass.getuser()}@{socket.gethostname()}"
            
            # Build ssh-keygen command
            cmd = ['ssh-keygen', '-t', key_type, '-f', str(private_key_path), '-C', comment]
            
            if key_type == "rsa":
                cmd.extend(['-b', '4096'])  # 4096-bit RSA
            
            if passphrase:
                # For passphrase, we need to handle it differently
                # ssh-keygen will prompt for passphrase
                print(f"\nGenerating {key_type} key with ssh-keygen...")
                print(f"Note: You'll be prompted for passphrase interactively.")
                subprocess.run(cmd, check=True)
            else:
                # No passphrase, use -N flag with empty string
                cmd.extend(['-N', ''])
                subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Set proper permissions
            private_key_path.chmod(0o600)
            public_key_path.chmod(0o644)
            
            print(f"✓ Generated key pair with ssh-keygen:")
            print(f"  Private: {private_key_path}")
            print(f"  Public:  {public_key_path}")
            print(f"  Comment: {comment}")
            
            # Show public key for easy copying
            print(f"\nPublic key (copy this to share):")
            print("-" * 80)
            with open(public_key_path, 'r') as f:
                print(f.read().strip())
            print("-" * 80)
            
            return private_key_path, public_key_path
            
        except subprocess.CalledProcessError as e:
            print(f"✗ ssh-keygen failed: {e}")
            if e.stderr:
                print(f"  Error: {e.stderr}")
            raise
        except Exception as e:
            print(f"✗ Error generating key: {e}")
            raise
    
    def add_key_to_agent(self, key_path: Path, passphrase: str = None) -> bool:
        """Add SSH key to SSH agent"""
        if not self.agent_socket:
            print("SSH agent not running. Start with: eval $(ssh-agent)")
            return False
        
        try:
            # Try using ssh-add command
            cmd = ['ssh-add', str(key_path)]
            
            if passphrase:
                # For passphrase-protected keys, we need to handle it interactively
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(input=passphrase + '\n')
                return process.returncode == 0
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✓ Key added to SSH agent: {key_path.name}")
                    return True
                else:
                    print(f"✗ Failed to add key to agent: {result.stderr}")
                    return False
                
        except Exception as e:
            print(f"✗ Error adding key to agent: {e}")
            return False
    
    def list_keys_in_agent(self) -> List[str]:
        """List all keys currently loaded in SSH agent"""
        if not self.agent_socket:
            print("SSH agent not running")
            return []
        
        try:
            result = subprocess.run(['ssh-add', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                keys = result.stdout.strip().split('\n')
                if keys and keys[0]:  # Check if not empty
                    print(f"Found {len(keys)} key(s) in SSH agent:")
                    for i, key in enumerate(keys, 1):
                        # Extract key type and fingerprint
                        parts = key.split()
                        if len(parts) >= 3:
                            key_type = parts[0]
                            fingerprint = parts[1]
                            comment = ' '.join(parts[2:])
                            print(f"  {i}. {key_type} {fingerprint[:20]}... {comment}")
                        else:
                            print(f"  {i}. {key}")
                    return keys
                else:
                    print("No keys in SSH agent")
                    return []
            else:
                print("Failed to list keys from agent")
                return []
        except Exception as e:
            print(f"Error listing keys: {e}")
            return []
    
    def remove_key_from_agent(self, key_path: Path) -> bool:
        """Remove specific key from SSH agent"""
        if not self.agent_socket:
            print("SSH agent not running")
            return False
        
        try:
            result = subprocess.run(['ssh-add', '-d', str(key_path)], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Key removed from SSH agent: {key_path.name}")
                return True
            else:
                print(f"✗ Failed to remove key: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Error removing key: {e}")
            return False
    
    def remove_all_keys_from_agent(self) -> bool:
        """Remove all keys from SSH agent"""
        if not self.agent_socket:
            print("SSH agent not running")
            return False
        
        try:
            result = subprocess.run(['ssh-add', '-D'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ All keys removed from SSH agent")
                return True
            else:
                print(f"✗ Failed to remove keys: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Error removing keys: {e}")
            return False
    
    def check_key_permissions(self, key_path: Path) -> bool:
        """Check if SSH key has correct permissions (600)"""
        try:
            mode = key_path.stat().st_mode
            return stat.S_IMODE(mode) == 0o600
        except Exception as e:
            print(f"Error checking permissions: {e}")
            return False
    
    def fix_key_permissions(self, key_path: Path):
        """Fix SSH key permissions to 600"""
        try:
            key_path.chmod(0o600)
            print(f"✓ Fixed permissions for: {key_path}")
            return True
        except Exception as e:
            print(f"✗ Error fixing permissions: {e}")
            return False
    
    def find_available_keys(self) -> List[Path]:
        """Find all SSH keys in .ssh directory"""
        key_patterns = ['id_rsa', 'id_ed25519', 'id_ecdsa', 'id_dsa']
        keys = []
        
        for pattern in key_patterns:
            for key_file in self.ssh_dir.glob(f"{pattern}*"):
                if not key_file.name.endswith('.pub'):
                    keys.append(key_file)
        
        return keys
    
    def get_public_key_from_private(self, private_key_path: Path) -> Optional[str]:
        """Extract public key from private key"""
        if not HAS_PARAMIKO:
            print("✗ Paramiko required for key extraction")
            return None
        
        try:
            # Try different key types
            for key_class in [paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey, paramiko.DSSKey]:
                try:
                    key = key_class.from_private_key_file(str(private_key_path))
                    return f"{key.get_name()} {key.get_base64()} {getpass.getuser()}@{socket.gethostname()}"
                except (paramiko.SSHException, paramiko.PasswordRequiredException):
                    continue
        except Exception as e:
            print(f"✗ Error extracting public key: {e}")
        
        return None
    
    def verify_key_pair(self, private_key_path: Path, public_key_path: Path) -> bool:
        """Verify that private and public keys match"""
        if not HAS_PARAMIKO:
            return False
        
        try:
            # Extract public key from private
            private_pub = self.get_public_key_from_private(private_key_path)
            if not private_pub:
                return False
            
            # Read public key file
            with open(public_key_path, 'r') as f:
                file_pub = f.read().strip()
            
            # Compare (ignoring comments)
            private_pub_no_comment = ' '.join(private_pub.split()[:2])
            file_pub_no_comment = ' '.join(file_pub.split()[:2])
            
            return private_pub_no_comment == file_pub_no_comment
            
        except Exception as e:
            print(f"Error verifying key pair: {e}")
            return False


    def copy_public_key_to_server(self, private_key_path: Path, 
                                 host: str, user: str, port: int = 22,
                                 password: str = None, 
                                 use_paramiko: bool = HAS_PARAMIKO) -> bool:
        """
        Copy public key to remote server's authorized_keys
        Returns True if successful
        """
        private_key_path = Path(private_key_path).expanduser()
        public_key_path = private_key_path.with_suffix('.pub')
        
        if not public_key_path.exists():
            print(f"✗ Public key not found: {public_key_path}")
            return False
        
        # Read public key
        with open(public_key_path, 'r') as f:
            public_key = f.read().strip()
        
        print(f"\n📤 Setting up password-less login for {user}@{host}:{port}...")
        
        if use_paramiko and HAS_PARAMIKO:
            return self._copy_key_with_paramiko(host, user, port, password, public_key)
        else:
            return self._copy_key_with_sshpass(host, user, port, password, public_key)
    
    def _copy_key_with_paramiko(self, host: str, user: str, port: int,
                               password: str, public_key: str) -> bool:
        """Copy key using paramiko (more control)"""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect with password
            client.connect(
                hostname=host,
                username=user,
                port=port,
                password=password,
                timeout=10
            )
            
            # Check if .ssh directory exists
            stdin, stdout, stderr = client.exec_command('test -d ~/.ssh && echo "exists"')
            ssh_dir_exists = "exists" in stdout.read().decode()
            
            if not ssh_dir_exists:
                # Create .ssh directory
                client.exec_command('mkdir -p ~/.ssh && chmod 700 ~/.ssh')
                print("  Created ~/.ssh directory")
            
            # Append public key to authorized_keys
            # Using a safer method that doesn't duplicate keys
            sftp = client.open_sftp()
            
            # Read existing authorized_keys
            try:
                with sftp.open('.ssh/authorized_keys', 'r') as f:
                    existing_keys = f.read().decode()
            except IOError:
                existing_keys = ""
            
            # Check if key already exists
            key_fingerprint = public_key.split()[1][:30]  # First 30 chars of key
            if key_fingerprint in existing_keys:
                print(f"  ✓ Public key already exists on server")
                client.close()
                return True
            
            # Append key
            append_command = f'echo "{public_key}" >> ~/.ssh/authorized_keys'
            stdin, stdout, stderr = client.exec_command(append_command)
            
            if stderr.read():
                # Try alternative method
                sftp = client.open_sftp()
                try:
                    with sftp.open('.ssh/authorized_keys', 'a') as f:
                        f.write(public_key + '\n')
                except:
                    client.close()
                    return False
            
            # Set proper permissions
            client.exec_command('chmod 600 ~/.ssh/authorized_keys')
            
            client.close()
            print(f"  ✓ Public key added to {user}@{host}")
            return True
            
        except paramiko.AuthenticationException:
            print(f"  ✗ Authentication failed for {user}@{host}")
            return False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    def _copy_key_with_sshpass(self, host: str, user: str, port: int,
                              password: str, public_key: str) -> bool:
        """Copy key using sshpass command"""
        try:
            # Create temporary file with public key
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pub', delete=False) as tmp:
                tmp.write(public_key + '\n')
                tmp_path = tmp.name
            
            # Use sshpass to copy key
            cmd = [
                'sshpass', '-p', password,
                'ssh-copy-id',
                '-f',  # Force mode (don't check if key exists)
                '-i', tmp_path,
                '-p', str(port),
                f'{user}@{host}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Clean up temp file
            import os
            os.unlink(tmp_path)
            
            if result.returncode == 0:
                print(f"  ✓ Public key added to {user}@{host}")
                return True
            else:
                print(f"  ✗ Failed: {result.stderr[:200]}")
                return False
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
# ============================================================================
# MULTI-HOP SSH MANAGER
# ============================================================================

class MultiHopSSHManager:
    """Manages complex multi-hop SSH connections with agent forwarding"""
    
    def __init__(self, config_dir: str = "~/.ssh/ssh2ls"):
        self.config_dir = Path(config_dir).expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_file = self.config_dir / "sessions.json"
        self.tunnels_file = self.config_dir / "tunnels.json"
        self.floating_ip_manager = FloatingIPManager(self.config_dir)
        self.key_manager = SSHKeyManager()
        self.sessions = self._load_json(self.sessions_file, {})
        self.tunnels = self._load_json(self.tunnels_file, {})
    
    def _load_json(self, filepath: Path, default: Any) -> Any:
        """Load JSON file with error handling"""
        try:
            if filepath.exists():
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load {filepath}: {e}")
        return default
    
    def _save_json(self, filepath: Path, data: Any):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
    
    def save_sessions(self):
        """Save SSH sessions to file"""
        self._save_json(self.sessions_file, self.sessions)
    
    def save_tunnels(self):
        """Save tunnel configurations"""
        self._save_json(self.tunnels_file, self.tunnels)
    
    def create_jumphost_config(self, name: str, jumphost_ip: str, jumphost_user: str, 
                              private_key_path: str, target_ip: str, target_user: str = None,
                              description: str = "", floating_ip: str = None,
                              use_floating_ip: bool = False) -> Dict:
        """Create a jumphost configuration"""
        
        if not target_user:
            target_user = jumphost_user
        
        config = {
            "name": name,
            "connection_type": "jumphost",
            "jumphost": {
                "ip": jumphost_ip,
                "user": jumphost_user,
                "private_key": private_key_path,
                "floating_ip": floating_ip,
                "use_floating_ip": use_floating_ip,
                "effective_ip": floating_ip if use_floating_ip else jumphost_ip,
                "description": f"Jumphost for accessing {target_ip}"
            },
            "target": {
                "ip": target_ip,
                "user": target_user,
                "description": description or f"Target VM behind {jumphost_ip}"
            },
            "agent_forwarding": True,
            "created": datetime.now().isoformat(),
            "last_used": None,
            "usage_count": 0
        }
        
        # Add to sessions
        self.sessions[name] = config
        self.save_sessions()
        
        print(f"✓ Created jumphost configuration '{name}':")
        print(f"  Jumphost: {jumphost_user}@{jumphost_ip}")
        print(f"  Target:   {target_user}@{target_ip}")
        if floating_ip and use_floating_ip:
            print(f"  Using floating IP: {floating_ip}")
        print(f"  Key:      {private_key_path}") 
        
        return config
    
    def generate_ssh_config(self, session_name: str) -> str:
        """Generate SSH config for a session"""
        if session_name not in self.sessions:
            raise KeyError(f"Session '{session_name}' not found")
        
        session = self.sessions[session_name]
        connection_type = session.get("connection_type", "jumphost")
        
        if connection_type == "direct":
            return self._generate_direct_ssh_config(session)
        else:
            return self._generate_jumphost_ssh_config(session)

    
    def _generate_direct_ssh_config(self, session: Dict) -> str:
        """Generate SSH config for direct connection"""
        host = session["host"]
        
        effective_ip = host.get('effective_ip', host['ip'])
        
        config = f"""# SSH Configuration for {session['name']} (Direct Connection)
# Generated by ssh2ls on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Description: {session.get('description', 'Direct connection')}

Host {session['name']}
    HostName {effective_ip}
    User {host['user']}"""
        
        if host.get('port', 22) != 22:
            config += f"\n    Port {host['port']}"
        
        if host.get('private_key'):
            config += f"\n    IdentityFile {host['private_key']}"
        
        config += """
    ForwardAgent yes
    ServerAliveInterval 30
    ServerAliveCountMax 3"""
        
        # Comment about floating IP if used
        if host.get('floating_ip') and host.get('use_floating_ip', False):
            config += f"\n    # Floating IP: {host['floating_ip']}"
        
        config += f"""

# Quick command
# ssh {session['name']}        # Direct connection to {host['user']}@{effective_ip}
"""
        return config.strip()
    
    
    def _generate_jumphost_ssh_config(self, session: Dict) -> str:
        """Generate SSH config for jumphost connection"""
        jh = session["jumphost"]
        target = session["target"]
        
        effective_ip = jh.get('effective_ip', jh['ip'])
        
        config = f"""# SSH Configuration for {session['name']}
# Generated by ssh2ls on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Description: {session.get('description', '')}

Host {session['name']}_jumphost
    HostName {effective_ip}
    User {jh['user']}"""
        
        if jh.get('private_key'):
            config += f"\n    IdentityFile {jh['private_key']}"
        
        config += f"""
    ForwardAgent {"yes" if session.get('agent_forwarding', True) else "no"}
    ServerAliveInterval 30
    ServerAliveCountMax 3"""

        if jh.get('floating_ip') and jh.get('use_floating_ip', False):
            config += f"\n    # Floating IP: {jh['floating_ip']}"
        
        config += f"""

Host {session['name']}
    HostName {target['ip']}
    User {target['user']}
    ProxyJump {session['name']}_jumphost
    # Connection through jumphost

# Quick commands
# ssh {session['name']}_jumphost        # Connect to jumphost
# ssh {session['name']}                 # Connect to target via jumphost
"""
        return config.strip()

    def update_floating_ip_mapping(self, session_name: str) -> Dict:
        """Update floating IP mapping for a session"""
        if session_name not in self.sessions:
            raise KeyError(f"Session '{session_name}' not found")
        
        session = self.sessions[session_name]
        
        if 'floating_ip_config' not in session:
            print(f"Session '{session_name}' doesn't have floating IP configured")
            return session
        
        # Update floating IP status
        floating_config = self.floating_ip_manager.update_floating_ip_status(
            session['floating_ip_config']['name']
        )
        
        # Update effective IP based on detection
        if floating_config.get('current_mapping'):
            if session['jumphost'].get('use_floating_ip', True):
                session['jumphost']['effective_ip'] = session['jumphost']['floating_ip']
            else:
                session['jumphost']['effective_ip'] = floating_config['current_mapping']
        
        session['floating_ip_config'] = floating_config
        session['last_updated'] = datetime.now().isoformat()
        
        self.sessions[session_name] = session
        self.save_sessions()
        
        print(f"\n✓ Updated floating IP mapping for '{session_name}':")
        print(f"  Status:         {floating_config['status']}")
        if 'current_mapping' in floating_config:
            print(f"  Current mapping: {floating_config['current_mapping']}")
        print(f"  Effective IP:   {session['jumphost']['effective_ip']}")
        
        return session
    
    def generate_ssh_config_with_floating_ip(self, session_name: str) -> str:
        """Generate SSH config for a session with floating IP"""
        if session_name not in self.sessions:
            raise KeyError(f"Session '{session_name}' not found")
        
        session = self.sessions[session_name]
        jh = session["jumphost"]
        target = session["target"]
        
        # Determine which IP to use
        if jh.get('use_floating_ip', True):
            host_ip = jh.get('floating_ip', jh.get('effective_ip', 'unknown'))
            ip_type = "Floating IP"
        else:
            host_ip = jh.get('fixed_ip', jh.get('effective_ip', 'unknown'))
            ip_type = "Fixed IP"
        
        config = f"""# SSH Configuration for {session_name}
# Generated by ssh2ls on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Description: {session.get('description', '')}
# IP Type: {ip_type}

Host {session_name}_jumphost
    HostName {host_ip}
    User {jh['user']}
    IdentityFile {jh['private_key']}
    ForwardAgent {"yes" if session.get('agent_forwarding', True) else "no"}
    ServerAliveInterval 30
    ServerAliveCountMax 3
    # {ip_type}: {host_ip}
"""
        
        if target.get('ip'):
            config += f"""
Host {session_name}
    HostName {target['ip']}
    User {target['user']}
    ProxyJump {session_name}_jumphost
    # Connection through jumphost ({ip_type}: {host_ip})

# Quick commands
# ssh {session_name}_jumphost        # Connect to jumphost ({ip_type})
# ssh {session_name}                 # Connect to target via jumphost
"""
        
        # Add alternative hosts if both floating and fixed IPs are available
        if jh.get('floating_ip') and jh.get('fixed_ip'):
            config += f"""
# Alternative connections
Host {session_name}_floating
    HostName {jh['floating_ip']}
    User {jh['user']}
    IdentityFile {jh['private_key']}
    ForwardAgent yes

Host {session_name}_fixed
    HostName {jh['fixed_ip']}
    User {jh['user']}
    IdentityFile {jh['private_key']}
    ForwardAgent yes
"""
        
        return config.strip()
    
    def test_connection_with_floating_ip(self, session_name: str) -> Dict[str, Any]:
        """Test connection with floating IP support"""
        if session_name not in self.sessions:
            raise KeyError(f"Session '{session_name}' not found")
        
        session = self.sessions[session_name]
        jh = session["jumphost"]
        
        print(f"\n🔍 Testing connection for '{session_name}' with floating IP...")
        
        results = {
            'session': session_name,
            'floating_ip': jh.get('floating_ip'),
            'fixed_ip': jh.get('fixed_ip'),
            'effective_ip': jh.get('effective_ip'),
            'use_floating_ip': jh.get('use_floating_ip', True),
            'tests': {}
        }
        
        # Test floating IP if available
        if jh.get('floating_ip'):
            print(f"\n1. Testing floating IP: {jh['floating_ip']}")
            floating_result = self._test_ssh_host(
                jh['floating_ip'], 
                jh['user'], 
                jh['private_key']
            )
            results['tests']['floating_ip'] = floating_result
        
        # Test fixed IP if available
        if jh.get('fixed_ip') and jh['fixed_ip'] != jh.get('floating_ip'):
            print(f"\n2. Testing fixed IP: {jh['fixed_ip']}")
            fixed_result = self._test_ssh_host(
                jh['fixed_ip'], 
                jh['user'], 
                jh['private_key']
            )
            results['tests']['fixed_ip'] = fixed_result
        
        # Test effective IP (whichever is being used)
        effective_ip = jh.get('effective_ip')
        if effective_ip and effective_ip not in [jh.get('floating_ip'), jh.get('fixed_ip')]:
            print(f"\n3. Testing effective IP: {effective_ip}")
            effective_result = self._test_ssh_host(
                effective_ip, 
                jh['user'], 
                jh['private_key']
            )
            results['tests']['effective_ip'] = effective_result
        
        # Test target connection if configured
        if session['target'].get('ip'):
            print(f"\n4. Testing target via jumphost: {session['target']['ip']}")
            target_result = self._test_via_jumphost(session)
            results['tests']['target_via_jumphost'] = target_result
        
        # Update session stats
        session['last_used'] = datetime.now().isoformat()
        session['usage_count'] = session.get('usage_count', 0) + 1
        self.save_sessions()
        
        # Print summary
        self._print_connection_summary(results)
        
        return results
    
    def test_connection(self, session_name: str) -> Dict[str, Any]:
        """Test connection (supports both direct and jumphost)"""
        if session_name not in self.sessions:
            raise KeyError(f"Session '{session_name}' not found")
        
        session = self.sessions[session_name]
        connection_type = session.get("connection_type", "jumphost")
        
        print(f"\n🔍 Testing connection for '{session_name}' ({connection_type})...")
        
        if connection_type == "direct":
            result = self._test_direct_connection(session)
            # Print result
            if result.get('success'):
                print(f"✓ Connection successful!")
                test_result = result.get('test_result', {})
                if test_result.get('response_time'):
                    print(f"  Response time: {test_result['response_time']}s")
                if test_result.get('hostname'):
                    print(f"  Hostname: {test_result['hostname']}")
            else:
                print(f"✗ Connection failed")
                test_result = result.get('test_result', {})
                if test_result.get('error'):
                    print(f"  Error: {test_result['error']}")
            return result

        else:
            return self._test_jumphost_connection(session)

    def _test_direct_connection(self, session: Dict) -> Dict[str, Any]:
        """Test direct connection"""
        host = session["host"]
        effective_ip = host.get('effective_ip', host['ip'])
        port = host.get('port', 22)
        key_path = host.get('private_key')
        
        print(f"Testing direct connection to {host['user']}@{effective_ip}:{port}")
        
        # Use the updated _test_ssh_host method
        result = self._test_ssh_host(
            host=effective_ip,
            user=host['user'],
            key_path=key_path,
            port=port
        )
        
        # Update session stats
        session['last_used'] = datetime.now().isoformat()
        session['usage_count'] = session.get('usage_count', 0) + 1
        self.save_sessions()
        
        return {
            'session': session['name'],
            'type': 'direct',
            'host': f"{host['user']}@{effective_ip}:{port}",
            'test_result': result,
            'success': result.get('success', False)
        }

    def _test_direct_ssh_connection(self, host: str, user: str, key_path: str = None, 
                                port: int = 22, timeout: int = 10) -> Dict:
        """Test direct SSH connection to a host"""
        result = {
            'host': host,
            'port': port,
            'user': user,
            'success': False,
            'error': None,
            'response_time': None
        }
        
        start_time = time.time()
        
        try:
            cmd = ['ssh']
            
            if key_path:
                cmd.extend(['-i', key_path])
            
            # Add port if not default
            if port != 22:
                cmd.extend(['-p', str(port)])
            
            cmd.extend([
                '-o', f'ConnectTimeout={timeout//2}',
                '-o', 'BatchMode=yes',
                '-o', 'StrictHostKeyChecking=no',
                f"{user}@{host}",
                'echo "SSH2LS_TEST_SUCCESS $(hostname) $(date +%s)"'
            ])
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            end_time = time.time()
            
            result['response_time'] = round(end_time - start_time, 2)
            
            if process.returncode == 0 and "SSH2LS_TEST_SUCCESS" in process.stdout:
                result['success'] = True
                # Parse response
                lines = process.stdout.strip().split('\n')
                for line in lines:
                    if "SSH2LS_TEST_SUCCESS" in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            result['hostname'] = parts[1]
                            result['timestamp'] = parts[2]
            else:
                result['success'] = False
                result['error'] = process.stderr.strip()
                
        except subprocess.TimeoutExpired:
            result['success'] = False
            result['error'] = "Connection timeout"
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
        
        return result 
    
    def _test_jumphost_connection(self, session: Dict) -> Dict[str, Any]:
        """Test jumphost connection"""
        jh = session["jumphost"]
        target = session["target"]
        
        results = {
            'session': session['name'],
            'type': 'jumphost',
            'tests': {}
        }
        
        # Test jumphost
        print(f"\n1. Testing jumphost: {jh['user']}@{jh['ip']}")
        jh_result = self._test_ssh_host(
            jh['ip'],
            jh['user'],
            jh['private_key']
        )
        results['tests']['jumphost'] = jh_result
        
        # Test target via jumphost if jumphost is reachable
        if jh_result.get('success'):
            print(f"\n2. Testing target via jumphost: {target['user']}@{target['ip']}")
            target_result = self._test_via_jumphost(session)
            results['tests']['target_via_jumphost'] = target_result
            
            results['success'] = target_result.get('success', False)
            results['full_connection'] = target_result.get('success', False)
        else:
            results['success'] = False
            results['full_connection'] = False
        
        # Update session stats
        session['last_used'] = datetime.now().isoformat()
        session['usage_count'] = session.get('usage_count', 0) + 1
        self.save_sessions()
        
        # Print summary
        print(f"\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        if results['tests'].get('jumphost', {}).get('success'):
            print("✓ Jumphost connection successful")
        else:
            print("✗ Jumphost connection failed")
        
        if results.get('full_connection'):
            print("✓ Full connection (jumphost → target) successful")
        elif results['tests'].get('jumphost', {}).get('success'):
            print("⚠️  Jumphost OK, but target connection failed")
        else:
            print("✗ Connection failed at jumphost")
        
        return results

    def _load_private_key(self, key_path: str, passphrase: str = None, max_attempts: int = 3) -> Optional[Any]:
        """Load private key from file with passphrase support"""
        if not HAS_PARAMIKO:
            return None
        
        try:
            key_path = Path(key_path).expanduser()
            
            # Try to load without passphrase first
            for key_class in [paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey, paramiko.DSSKey]:
                try:
                    return key_class.from_private_key_file(str(key_path))
                except paramiko.PasswordRequiredException:
                    # Key is encrypted, need passphrase
                    if passphrase is not None:
                        try:
                            return key_class.from_private_key_file(str(key_path), password=passphrase)
                        except paramiko.SSHException:
                            # Wrong passphrase
                            continue
                    else:
                        # Ask for passphrase interactively
                        for attempt in range(max_attempts):
                            try:
                                import getpass
                                passphrase = getpass.getpass(f"Enter passphrase for {key_path.name} (attempt {attempt + 1}/{max_attempts}): ")
                                return key_class.from_private_key_file(str(key_path), password=passphrase)
                            except paramiko.SSHException:
                                if attempt == max_attempts - 1:
                                    print(f"Failed to load key after {max_attempts} attempts")
                                    return None
                                continue
                except paramiko.SSHException:
                    # Try next key type
                    continue
            
            print(f"✗ Could not load private key: {key_path}")
            print("  Possible reasons:")
            print("  1. Key requires a passphrase")
            print("  2. Key file is corrupted")
            print("  3. Key format is not supported")
            print("  4. Wrong passphrase entered")
            return None
            
        except Exception as e:
            print(f"✗ Error loading key: {e}")
            return None

    def setup_agent_forwarding(self, session_name: str) -> bool:
        """Setup and test SSH agent forwarding"""
        if session_name not in self.sessions:
            raise KeyError(f"Session '{session_name}' not found")
        
        session = self.sessions[session_name]
        
        print(f"\n🔧 Setting up agent forwarding for '{session_name}'...")
        
        # Check if SSH agent is running
        agent_socket = os.environ.get('SSH_AUTH_SOCK')
        if not agent_socket:
            print("SSH agent is not running.")
            print("Start it with: eval $(ssh-agent)")
            print("Then add key: ssh-add ~/.ssh/your_key")
            return False
        
        # Add key to agent if needed
        key_path = Path(session['jumphost']['private_key']).expanduser()
        if self.key_manager.add_key_to_agent(key_path):
            print("✓ Key added to SSH agent")
        else:
            print("Could not add key to agent")
        
        # Test agent forwarding
        print("\nTesting agent forwarding...")
        jh = session["jumphost"]
        
        # First check what keys are in agent locally
        local_keys = self.key_manager.list_keys_in_agent()
        if not local_keys:
            print("No keys in local SSH agent")
            return False
        
        # Test if we can forward the agent
        cmd = ['ssh', '-A', 
               '-i', jh['private_key'],
               '-o', 'ConnectTimeout=5',
               f"{jh['user']}@{jh['ip']}",
               'ssh-add -l && echo "Agent-forwarding-successful"']
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if "Agent-forwarding-successful" in result.stdout:
                print("✓ SSH agent forwarding is working correctly")
                if "no identities" not in result.stdout.lower():
                    print(f"  Keys available on jumphost:")
                    for line in result.stdout.strip().split('\n'):
                        if line and "Agent-forwarding-successful" not in line:
                            print(f"    {line}")
                
                # Update session
                session['agent_forwarding'] = True
                session['agent_forwarding_tested'] = datetime.now().isoformat()
                self.save_sessions()
                
                return True
            else:
                print("✗ Agent forwarding test failed")
                print(f"  Output: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("✗ Connection timeout")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def create_tunnel(self, session_name: str, local_port: int, 
                     remote_host: str, remote_port: int, 
                     tunnel_name: str = None) -> Dict:
        """Create SSH tunnel configuration"""
        if session_name not in self.sessions:
            raise KeyError(f"Session '{session_name}' not found")
        
        session = self.sessions[session_name]
        
        if not tunnel_name:
            tunnel_name = f"{session_name}_tunnel_{local_port}_{remote_port}"
        
        tunnel_config = {
            "name": tunnel_name,
            "session": session_name,
            "local_port": local_port,
            "remote_host": remote_host,
            "remote_port": remote_port,
            "type": "local_forward",
            "command": self._generate_tunnel_command(session, local_port, remote_host, remote_port),
            "status": "stopped",
            "created": datetime.now().isoformat(),
            "pid": None
        }
        
        self.tunnels[tunnel_name] = tunnel_config
        self.save_tunnels()
        
        print(f"✓ Created tunnel '{tunnel_name}':")
        print(f"  Local:  localhost:{local_port}")
        print(f"  Remote: {remote_host}:{remote_port}")
        
        return tunnel_config
    
    def _generate_tunnel_command(self, session: Dict, local_port: int, 
                               remote_host: str, remote_port: int) -> str:
        """Generate SSH tunnel command"""
        jh = session["jumphost"]
        target = session["target"]
        
        # Build command to tunnel through jumphost to target
        cmd_parts = [
            "ssh", "-N",
            "-L", f"{local_port}:{remote_host}:{remote_port}",
            "-i", jh['private_key'],
            "-J", f"{jh['user']}@{jh['ip']}",
            f"{target['user']}@{target['ip']}"
        ]
        
        if session.get('agent_forwarding', True):
            cmd_parts.insert(2, "-A")
        
        return " ".join(cmd_parts)
    
    def start_tunnel(self, tunnel_name: str, background: bool = True) -> bool:
        """Start SSH tunnel"""
        if tunnel_name not in self.tunnels:
            raise KeyError(f"Tunnel '{tunnel_name}' not found")
        
        tunnel = self.tunnels[tunnel_name]
        
        print(f"\nStarting tunnel '{tunnel_name}'...")
        
        try:
            if background:
                # Start in background
                process = subprocess.Popen(
                    tunnel['command'].split(),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    start_new_session=True
                )
                
                # Give it a moment to start
                time.sleep(2)
                
                if process.poll() is None:
                    tunnel['pid'] = process.pid
                    tunnel['status'] = 'running'
                    tunnel['started'] = datetime.now().isoformat()
                    self.save_tunnels()
                    
                    print(f"✓ Tunnel started in background (PID: {process.pid})")
                    print(f"  Check status with: ssh2ls tunnel status {tunnel_name}")
                    return True
                else:
                    stderr = process.stderr.read().decode() if process.stderr else ""
                    print(f"✗ Tunnel failed to start: {stderr}")
                    return False
            else:
                # Run in foreground
                print("\nRunning tunnel in foreground (Ctrl+C to stop)...")
                print(f"Command: {tunnel['command']}")
                subprocess.run(tunnel['command'].split())
                return True
                
        except Exception as e:
            print(f"✗ Error starting tunnel: {e}")
            return False
    
    def stop_tunnel(self, tunnel_name: str) -> bool:
        """Stop SSH tunnel"""
        if tunnel_name not in self.tunnels:
            raise KeyError(f"Tunnel '{tunnel_name}' not found")
        
        tunnel = self.tunnels[tunnel_name]
        
        if tunnel['status'] != 'running' or not tunnel.get('pid'):
            print(f"Tunnel '{tunnel_name}' is not running")
            return False
        
        try:
            print(f"\n🛑 Stopping tunnel '{tunnel_name}' (PID: {tunnel['pid']})...")
            
            # Try graceful termination
            try:
                os.kill(tunnel['pid'], 15)  # SIGTERM
                time.sleep(1)
                
                # Check if still running
                try:
                    os.kill(tunnel['pid'], 0)
                    # Still running, force kill
                    os.kill(tunnel['pid'], 9)  # SIGKILL
                    print("Force killed tunnel")
                except OSError:
                    # Process terminated
                    pass
                    
            except ProcessLookupError:
                # Process already dead
                pass
            
            tunnel['status'] = 'stopped'
            tunnel['stopped'] = datetime.now().isoformat()
            tunnel['pid'] = None
            self.save_tunnels()
            
            print(f"✓ Tunnel stopped")
            return True
            
        except Exception as e:
            print(f"✗ Error stopping tunnel: {e}")
            return False
    
    def transfer_files(self, session_name: str, local_path: str, 
                      remote_path: str, direction: str = "upload") -> bool:
        """
        Transfer files through jumphost
        direction: 'upload' (local→remote) or 'download' (remote→local)
        """
        if session_name not in self.sessions:
            raise KeyError(f"Session '{session_name}' not found")
        
        session = self.sessions[session_name]
        jh = session["jumphost"]
        target = session["target"]
        
        print(f"\n📁 Transferring files for '{session_name}'...")
        print(f"Direction: {direction}")
        print(f"Local:  {local_path}")
        print(f"Remote: {remote_path}")
        
        # Build SCP command with ProxyJump
        if direction == "upload":
            src = local_path
            dst = f"{target['user']}@{target['ip']}:{remote_path}"
        else:  # download
            src = f"{target['user']}@{target['ip']}:{remote_path}"
            dst = local_path
        
        cmd = [
            "scp", "-r",
            "-o", f"ProxyJump={jh['user']}@{jh['ip']}",
            "-i", jh['private_key'],
            "-o", "ConnectTimeout=30"
        ]
        
        if session.get('agent_forwarding', True):
            cmd.extend(["-o", "ForwardAgent=yes"])
        
        cmd.extend([src, dst])
        
        print(f"\nExecuting: {' '.join(cmd)}")
        
        try:
            # Show progress
            print("Transferring... (this may take a while for large files)")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ File transfer successful")
                return True
            else:
                print(f"✗ File transfer failed:")
                print(f"  Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Error during file transfer: {e}")
            return False
    
    def interactive_shell(self, session_name: str, hop: str = "target") -> bool:
        """
        Start interactive SSH shell
        hop: 'direct' or 'jumphost' or 'target'
        """
        if session_name not in self.sessions:
            raise KeyError(f"Session '{session_name}' not found")
        
        session = self.sessions[session_name]
        connection_type = session.get("connection_type", "jumphost")
        
        if connection_type == "direct":
            # Direct connection
            host = session["host"]
            effective_ip = host.get('effective_ip', host['ip'])
            
            ssh_cmd = ["ssh"]
            
            if host.get('private_key'):
                ssh_cmd.extend(['-i', host['private_key']])
            
            if host.get('port', 22) != 22:
                ssh_cmd.extend(['-p', str(host['port'])])
            
            ssh_cmd.append(f"{host['user']}@{effective_ip}")
            
        else:
            # Jumphost connection
            if hop == "jumphost":
                host = session["jumphost"]
                effective_ip = host.get('effective_ip', host['ip'])
                
                ssh_cmd = ["ssh", "-i", host["private_key"]]
                
                if session.get('agent_forwarding', True):
                    ssh_cmd.insert(1, "-A")
                    
                if host.get('port', 22) != 22:
                    ssh_cmd.extend(['-p', str(host['port'])])
                
                ssh_cmd.append(f"{host['user']}@{effective_ip}")
                
            else:  # target via jumphost
                host = session["target"]
                jh = session["jumphost"]
                effective_ip = jh.get('effective_ip', jh['ip'])
                
                ssh_cmd = [
                    "ssh", "-J", f"{jh['user']}@{effective_ip}",
                    "-i", jh["private_key"],
                ]
                
                if session.get('agent_forwarding', True):
                    ssh_cmd.insert(1, "-A")
                
                ssh_cmd.append(f"{host['user']}@{host['ip']}")
        
        print(f"\nStarting interactive SSH session...")
        print(f"Command: {' '.join(ssh_cmd)}")
        print("(Press Ctrl+D or type 'exit' to disconnect)")
        
        try:
            # Update usage stats
            session['last_used'] = datetime.now().isoformat()
            session['usage_count'] = session.get('usage_count', 0) + 1
            self.save_sessions()
            
            # Start interactive session
            subprocess.run(ssh_cmd)
            return True
            
        except KeyboardInterrupt:
            print("\nSession interrupted")
            return False
        except Exception as e:
            print(f"✗ Error starting session: {e}")
            return False

    
    def batch_setup_environment(self, session_name: str, commands: List[str]) -> bool:
        """
        Execute batch commands on target through jumphost
        Useful for setting up environments
        """
        if session_name not in self.sessions:
            raise KeyError(f"Session '{session_name}' not found")
        
        session = self.sessions[session_name]
        jh = session["jumphost"]
        target = session["target"]
        
        print(f"\n⚙️  Setting up environment on target...")
        
        # Create a temporary script with all commands
        script_content = "#!/bin/bash\nset -e\n\n"
        script_content += "# Environment setup script\n"
        script_content += "# Generated by ssh2ls on " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n"
        
        for i, cmd in enumerate(commands, 1):
            script_content += f"echo 'Step {i}: {cmd}'\n"
            script_content += f"{cmd}\n"
            script_content += "echo ''\n"
        
        script_content += "echo 'Environment setup complete!'\n"
        
        # Save script locally
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as temp_script:
            temp_script.write(script_content)
            temp_script_path = temp_script.name
        
        # Make executable
        os.chmod(temp_script_path, 0o755)
        
        try:
            # Upload script
            print("Uploading setup script...")
            
            # Use direct SSH command to upload
            upload_cmd = [
                "scp", 
                "-o", f"ProxyJump={jh['user']}@{jh['ip']}",
                "-i", jh['private_key'],
                temp_script_path,
                f"{target['user']}@{target['ip']}:~/setup_env.sh"
            ]
            
            upload_result = subprocess.run(upload_cmd, capture_output=True, text=True)
            
            if upload_result.returncode != 0:
                print(f"✗ Failed to upload script: {upload_result.stderr}")
                os.unlink(temp_script_path)
                return False
            
            # Execute script on target
            print("\nExecuting setup script...")
            
            # Build SSH command to execute script
            ssh_cmd = [
                "ssh", "-J", f"{jh['user']}@{jh['ip']}",
                "-i", jh["private_key"],
                f"{target['user']}@{target['ip']}",
                "bash ~/setup_env.sh"
            ]
            
            if session.get('agent_forwarding', True):
                ssh_cmd.insert(1, "-A")
            
            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
            
            # Clean up temporary script
            os.unlink(temp_script_path)
            
            if result.returncode == 0:
                print("✓ Environment setup completed successfully")
                print("\nOutput:")
                print("-" * 60)
                print(result.stdout)
                print("-" * 60)
                return True
            else:
                print("✗ Environment setup failed:")
                print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Error during environment setup: {e}")
            if os.path.exists(temp_script_path):
                os.unlink(temp_script_path)
            return False
    
    def get_quick_commands(self, session_name: str) -> Dict[str, str]:
        """Get quick commands for common operations"""
        if session_name not in self.sessions:
            raise KeyError(f"Session '{session_name}' not found")
        
        session = self.sessions[session_name]
        jh = session["jumphost"]
        target = session["target"]
        
        return {
            "connect_jumphost": f"ssh -A -i {jh['private_key']} {jh['user']}@{jh['ip']}",
            "connect_target": f"ssh -A -i {jh['private_key']} -J {jh['user']}@{jh['ip']} {target['user']}@{target['ip']}",
            "copy_to_target": f"scp -r -o ProxyJump={jh['user']}@{jh['ip']} -i {jh['private_key']} LOCAL_FILE {target['user']}@{target['ip']}:REMOTE_PATH",
            "copy_from_target": f"scp -r -o ProxyJump={jh['user']}@{jh['ip']} -i {jh['private_key']} {target['user']}@{target['ip']}:REMOTE_FILE LOCAL_PATH",
            "check_agent": "ssh-add -l",
            "add_key": f"ssh-add {jh['private_key']}",
            "test_connection": f"ssh -o ConnectTimeout=5 -i {jh['private_key']} -J {jh['user']}@{jh['ip']} {target['user']}@{target['ip']} 'echo Connection successful'"
        }
    
    def list_sessions(self) -> List[str]:
        """List all configured sessions"""
        return list(self.sessions.keys())
    
    def delete_session(self, session_name: str) -> bool:
        """Delete a session"""
        if session_name in self.sessions:
            del self.sessions[session_name]
            self.save_sessions()
            print(f"✓ Deleted session: {session_name}")
            return True
        else:
            print(f"Session not found: {session_name}")
            return False
        
    def _test_ssh_host(self, host: str, user: str, key_path: str = None, 
                    port: int = 22, timeout: int = 10) -> Dict:
        """Test SSH connection to a host"""
        result = {
            'host': host,
            'port': port,
            'user': user,
            'success': False,
            'error': None,
            'response_time': None
        }
        
        start_time = time.time()
        
        try:
            cmd = ['ssh']
            
            if key_path:
                cmd.extend(['-i', key_path])
            
            # Add port if not default
            if port != 22:
                cmd.extend(['-p', str(port)])
            
            cmd.extend([
                '-o', f'ConnectTimeout={timeout//2}',
                '-o', 'BatchMode=yes',
                '-o', 'StrictHostKeyChecking=no',
                f"{user}@{host}",
                'echo "SSH2LS_TEST_SUCCESS $(hostname) $(date +%s)"'
            ])
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            end_time = time.time()
            
            result['response_time'] = round(end_time - start_time, 2)
            
            if process.returncode == 0 and "SSH2LS_TEST_SUCCESS" in process.stdout:
                result['success'] = True
                # Parse response
                lines = process.stdout.strip().split('\n')
                for line in lines:
                    if "SSH2LS_TEST_SUCCESS" in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            result['hostname'] = parts[1]
                            result['timestamp'] = parts[2]
                print(f"   ✓ Connected successfully ({result['response_time']}s)")
                if 'hostname' in result:
                    print(f"   Hostname: {result['hostname']}")
            else:
                result['success'] = False
                result['error'] = process.stderr.strip()
                print(f"   ✗ Connection failed: {result['error'][:100]}")
                    
        except subprocess.TimeoutExpired:
            result['success'] = False
            result['error'] = "Connection timeout"
            print(f"   ✗ Connection timeout")
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            print(f"   ✗ Error: {e}")
        
        return result
    
    def _test_via_jumphost(self, session: Dict) -> Dict:
        """Test connection via jumphost"""
        result = {
            'success': False,
            'error': None,
            'response_time': None
        }
        
        jh = session["jumphost"]
        target = session["target"]
        
        # Get effective IP with better error checking
        effective_ip = jh.get('effective_ip', jh.get('floating_ip', jh.get('ip')))
        
        if not effective_ip:
            result['error'] = "No IP address configured for jumphost"
            print(f"   ✗ {result['error']}")
            return result
        
        if not target.get('ip'):
            result['error'] = "No target IP configured"
            print(f"   ✗ {result['error']}")
            return result
        
        print(f"   Testing via: {jh['user']}@{effective_ip} → {target['user']}@{target['ip']}")
        
        start_time = time.time()
        
        try:
            cmd = ['ssh', '-i', jh['private_key'],
                '-J', f"{jh['user']}@{effective_ip}",
                '-o', 'ConnectTimeout=5',
                '-o', 'StrictHostKeyChecking=no',
                f"{target['user']}@{target['ip']}",
                'echo "SSH2LS_TARGET_TEST_SUCCESS $(hostname) $(date +%s)"']
            
            print(f"   Command: {' '.join(cmd)}")  # Debug output
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            end_time = time.time()
            
            result['response_time'] = round(end_time - start_time, 2)
            
            if process.returncode == 0 and "SSH2LS_TARGET_TEST_SUCCESS" in process.stdout:
                result['success'] = True
                lines = process.stdout.strip().split('\n')
                for line in lines:
                    if "SSH2LS_TARGET_TEST_SUCCESS" in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            result['hostname'] = parts[1]
                print(f"   ✓ Connected via jumphost ({result['response_time']}s)")
                if 'hostname' in result:
                    print(f"   Target hostname: {result['hostname']}")
            else:
                result['success'] = False
                result['error'] = process.stderr.strip()
                print(f"   ✗ Connection failed: {result['error']}")
                
        except subprocess.TimeoutExpired:
            result['success'] = False
            result['error'] = "Connection timeout"
            print(f"   ✗ Connection timeout")
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            print(f"   ✗ Error: {e}")
        
        return result
    def _print_connection_summary(self, results: Dict):
        """Print connection test summary"""
        print(f"\n" + "="*60)
        print("CONNECTION TEST SUMMARY")
        print("="*60)
        
        print(f"\nSession: {results['session']}")
        print(f"Floating IP: {results.get('floating_ip', 'Not configured')}")
        print(f"Fixed IP:    {results.get('fixed_ip', 'Not configured')}")
        print(f"Using:       {'Floating IP' if results.get('use_floating_ip') else 'Fixed IP'}")
        print(f"Effective:   {results.get('effective_ip', 'Unknown')}")
        
        print(f"\nTest Results:")
        print("-" * 40)
        
        for test_name, test_result in results['tests'].items():
            if isinstance(test_result, dict):
                status = "✓" if test_result.get('success') else "✗"
                host = test_result.get('host', test_name)
                time_str = f"({test_result.get('response_time', '?')}s)" if test_result.get('response_time') else ""
                print(f"{status} {test_name:20} {host:15} {time_str}")
                
                if not test_result.get('success') and test_result.get('error'):
                    print(f"    Error: {test_result['error'][:80]}")

    
    def create_direct_connection(self, name: str, host_ip: str, host_user: str = "ubuntu",
                               private_key_path: str = None, port: int = 22,
                               description: str = "", floating_ip: str = None,
                               use_floating_ip: bool = False) -> Dict:
        """Create a direct SSH connection (no jumphost)"""
        
        config = {
            "name": name,
            "connection_type": "direct",
            "host": {
                "ip": host_ip,
                "user": host_user,
                "private_key": private_key_path,
                "port": port,
                "floating_ip": floating_ip,
                "use_floating_ip": use_floating_ip,
                "effective_ip": floating_ip if use_floating_ip else host_ip,
                "description": description
            },
            "created": datetime.now().isoformat(),
            "last_used": None,
            "usage_count": 0
        }
        
        # Add to sessions
        self.sessions[name] = config
        self.save_sessions()
        
        print(f"✓ Created direct connection '{name}':")
        print(f"  Host: {host_user}@{host_ip}:{port}")
        if floating_ip and use_floating_ip:
            print(f"  Using floating IP: {floating_ip}")
        print(f"  Key:      {private_key_path}")
        print(f"  Type:     Direct connection (no jumphost)")
        
        return config
    def create_jumphost_config_with_floating_ip(self, name: str, floating_ip: str, fixed_ip: str = None,
                                            jumphost_user: str = "ubuntu", target_ip: str = None,
                                            target_user: str = "ubuntu", private_key_path: str = None,
                                            use_floating_ip: bool = True, description: str = "") -> Dict:
        """Create a jumphost configuration with floating IP support"""
        
        if not target_user:
            target_user = jumphost_user
        
        effective_ip = floating_ip if use_floating_ip else (fixed_ip or floating_ip)
        
        config = {
            "name": name,
            "connection_type": "jumphost",
            "jumphost": {
                "ip": fixed_ip or floating_ip,  # Store the base IP
                "floating_ip": floating_ip,
                "fixed_ip": fixed_ip,
                "user": jumphost_user,
                "private_key": private_key_path,
                "use_floating_ip": use_floating_ip,
                "effective_ip": effective_ip,
                "description": f"Jumphost with floating IP {floating_ip}"
            },
            "target": {
                "ip": target_ip,
                "user": target_user,
                "description": description or f"Target VM"
            },
            "floating_ip_config": {
                "name": name,
                "floating_ip": floating_ip,
                "fixed_ip": fixed_ip,
                "use_floating_ip": use_floating_ip
            },
            "agent_forwarding": True,
            "created": datetime.now().isoformat(),
            "last_used": None,
            "usage_count": 0
        }
        
        # Add to sessions
        self.sessions[name] = config
        self.save_sessions()
        
        print(f"✓ Created jumphost configuration with floating IP '{name}':")
        print(f"  Floating IP: {floating_ip}")
        if fixed_ip:
            print(f"  Fixed IP:    {fixed_ip}")
        print(f"  Using:       {'Floating IP' if use_floating_ip else 'Fixed IP'}")
        print(f"  Effective:   {effective_ip}")
        if target_ip:
            print(f"  Target:      {target_user}@{target_ip}")
        print(f"  Key:         {private_key_path}")
        
        return config
    
    def test_and_setup_passwordless(self, session_name: str, 
                                   ask_for_password: bool = True) -> Dict[str, Any]:
        """
        Test connection and if successful, setup password-less authentication
        """
        if session_name not in self.sessions:
            raise KeyError(f"Session '{session_name}' not found")
        
        session = self.sessions[session_name]
        connection_type = session.get("connection_type", "jumphost")
        
        print(f"\n🔍 Testing and setting up password-less login for '{session_name}'...")
        
        if connection_type == "direct":
            return self._test_and_setup_direct_passwordless(session, ask_for_password)
        else:
            return self._test_and_setup_jumphost_passwordless(session, ask_for_password)
    
    def _test_and_setup_direct_passwordless(self, session: Dict, 
                                           ask_for_password: bool) -> Dict[str, Any]:
        """Test and setup password-less for direct connection"""
        host = session["host"]
        effective_ip = host.get('effective_ip', host['ip'])
        port = host.get('port', 22)
        user = host['user']
        key_path = host.get('private_key')
        
        print(f"Testing connection to {user}@{effective_ip}:{port}")
        
        # First test without password (might already be password-less)
        test_result = self._test_ssh_host(
            host=effective_ip,
            user=user,
            key_path=key_path,
            port=port
        )
        
        if test_result.get('success'):
            print(f"✓ Already password-less!")
            return {
                'session': session['name'],
                'type': 'direct',
                'already_passwordless': True,
                'host': f"{user}@{effective_ip}:{port}",
                'test_result': test_result
            }
        
        # Connection failed, try with password to setup password-less
        print(f"✗ Not password-less yet. Let's set it up...")
        
        if ask_for_password:
            import getpass
            password = getpass.getpass(f"Enter password for {user}@{effective_ip}: ")
        else:
            password = None
        
        if not password:
            print("  Skipping password-less setup (no password provided)")
            return {
                'session': session['name'],
                'type': 'direct',
                'setup_complete': False,
                'error': 'No password provided'
            }
        
        # Test connection with password
        print(f"Testing connection with password...")
        password_test = self._test_ssh_with_password(effective_ip, user, port, password)
        
        if not password_test.get('success'):
            print(f"✗ Password authentication also failed")
            return {
                'session': session['name'],
                'type': 'direct',
                'setup_complete': False,
                'error': password_test.get('error', 'Authentication failed')
            }
        
        print(f"✓ Password authentication successful")
        
        # Now copy public key to server
        if key_path:
            success = self.key_manager.copy_public_key_to_server(
                private_key_path=key_path,
                host=effective_ip,
                user=user,
                port=port,
                password=password
            )
            
            if success:
                # Test again to verify password-less works
                print(f"\nVerifying password-less login...")
                final_test = self._test_ssh_host(
                    host=effective_ip,
                    user=user,
                    key_path=key_path,
                    port=port
                )
                
                if final_test.get('success'):
                    print(f"✅ Password-less setup complete!")
                    
                    # Update session stats
                    session['last_used'] = datetime.now().isoformat()
                    session['usage_count'] = session.get('usage_count', 0) + 1
                    session['passwordless_setup'] = datetime.now().isoformat()
                    self.save_sessions()
                    
                    return {
                        'session': session['name'],
                        'type': 'direct',
                        'setup_complete': True,
                        'host': f"{user}@{effective_ip}:{port}",
                        'final_test': final_test
                    }
        
        return {
            'session': session['name'],
            'type': 'direct',
            'setup_complete': False,
            'error': 'Failed to setup password-less login'
        }
    
    def _test_ssh_with_password(self, host: str, user: str, port: int, 
                               password: str, timeout: int = 10) -> Dict:
        """Test SSH connection with password authentication"""
        result = {
            'success': False,
            'error': None
        }
        
        try:
            if HAS_PARAMIKO:
                # Use paramiko for password auth
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                client.connect(
                    hostname=host,
                    username=user,
                    port=port,
                    password=password,
                    timeout=timeout
                )
                
                # Test a simple command
                stdin, stdout, stderr = client.exec_command('echo "SSH2LS_PASSWORD_TEST_SUCCESS"')
                output = stdout.read().decode().strip()
                
                if "SSH2LS_PASSWORD_TEST_SUCCESS" in output:
                    result['success'] = True
                else:
                    result['error'] = stderr.read().decode()
                
                client.close()
            else:
                # Use sshpass for password auth
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as tmp:
                    tmp.write('#!/bin/bash\necho "SSH2LS_PASSWORD_TEST_SUCCESS"\n')
                    tmp_path = tmp.name
                
                import os
                os.chmod(tmp_path, 0o755)
                
                cmd = [
                    'sshpass', '-p', password,
                    'ssh',
                    '-o', 'StrictHostKeyChecking=no',
                    '-p', str(port),
                    f'{user}@{host}',
                    f'bash {tmp_path}'
                ]
                
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
                os.unlink(tmp_path)
                
                result['success'] = process.returncode == 0
                if not result['success']:
                    result['error'] = process.stderr
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _test_and_setup_jumphost_passwordless(self, session: Dict, 
                                             ask_for_password: bool) -> Dict[str, Any]:
        """Test and setup password-less for jumphost connection"""
        jh = session["jumphost"]
        target = session["target"]
        
        print(f"\nJumphost: {jh['user']}@{jh.get('effective_ip', jh['ip'])}")
        print(f"Target: {target['user']}@{target['ip']}")
        
        results = {
            'session': session['name'],
            'type': 'jumphost',
            'jumphost_setup': False,
            'target_setup': False,
            'full_connection': False
        }
        
        # Step 1: Setup jumphost password-less
        print(f"\n1. Setting up jumphost password-less...")
        jh_result = self._test_and_setup_direct_passwordless({
            "name": session['name'] + "_jumphost",
            "connection_type": "direct",
            "host": jh
        }, ask_for_password)
        
        results['jumphost_setup'] = jh_result.get('setup_complete', False)
        
        if not results['jumphost_setup']:
            print(f"✗ Jumphost password-less setup failed")
            return results
        
        # Step 2: Now setup target through jumphost
        print(f"\n2. Setting up target password-less through jumphost...")
        
        # First test if we can reach target via jumphost
        print(f"   Testing target connection via jumphost...")
        target_test = self._test_via_jumphost(session)
        
        if target_test.get('success'):
            print(f"   ✓ Target already password-less!")
            results['target_setup'] = True
            results['full_connection'] = True
            return results
        
        # Need to setup target password-less
        print(f"   Target not password-less yet")
        
        if ask_for_password:
            import getpass
            target_password = getpass.getpass(f"Enter password for {target['user']}@{target['ip']}: ")
        else:
            target_password = None
        
        if not target_password:
            print("   Skipping target password-less setup")
            return results
        
        # Copy key to target through jumphost
        print(f"   Copying public key to target via jumphost...")
        
        # Use SSH tunnel through jumphost to copy key
        success = self._copy_key_via_jumphost(session, target_password)
        
        if success:
            results['target_setup'] = True
            
            # Test full connection
            print(f"\n3. Testing full password-less connection...")
            final_test = self._test_via_jumphost(session)
            
            if final_test.get('success'):
                print(f"   ✅ Full password-less connection working!")
                results['full_connection'] = True
        
        return results
    
    def _copy_key_via_jumphost(self, session: Dict, target_password: str) -> bool:
        """Copy public key to target via jumphost"""
        jh = session["jumphost"]
        target = session["target"]
        key_path = jh.get('private_key')
        
        if not key_path:
            print("   ✗ No private key path found")
            return False
        
        # Read public key
        import os
        pub_key_path = Path(key_path).expanduser().with_suffix('.pub')
        
        if not pub_key_path.exists():
            print(f"   ✗ Public key not found: {pub_key_path}")
            return False
        
        with open(pub_key_path, 'r') as f:
            public_key = f.read().strip()
        
        # Create a script to copy key on target
        script = f'''#!/bin/bash
# Create .ssh directory if needed
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Check if key already exists
if grep -q "{public_key.split()[1][:30]}" ~/.ssh/authorized_keys 2>/dev/null; then
    echo "Key already exists"
    exit 0
fi

# Append key
echo "{public_key}" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo "Key added successfully"
'''
        
        # Execute script on target via jumphost
        try:
            # Write script to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as tmp:
                tmp.write(script)
                tmp_path = tmp.name
            
            # Copy script to target through jumphost
            cmd = [
                'sshpass', '-p', target_password,
                'ssh',
                '-J', f"{jh['user']}@{jh.get('effective_ip', jh['ip'])}",
                f"{target['user']}@{target['ip']}",
                f'bash -s'
            ]
            
            process = subprocess.run(
                cmd, 
                input=script.encode(),
                capture_output=True,
                timeout=30
            )
            
            os.unlink(tmp_path)
            
            if process.returncode == 0:
                print(f"   ✓ Public key added to target")
                return True
            else:
                print(f"   ✗ Failed: {process.stderr.decode()[:200]}")
                return False
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
# ============================================================================
# MAIN SSH2LS APPLICATION
# ============================================================================

class SSH2LS:
    """Main SSH2LS application"""
    
    def __init__(self):
        self.key_manager = SSHKeyManager()
        self.ssh_manager = MultiHopSSHManager()
        self.config_dir = Path("~/.ssh/ssh2ls").expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.instructions = InstructionDisplay()
## set up restart-agent-recover
    def setup_autostart_persistence(self):
        """Setup SSH agent persistence and auto-load keys on startup"""
        print("\n" + "="*80)
        print("🔄 SETUP AUTO-LOAD KEYS ON STARTUP")
        print("="*80)
        
        print("\nThis will configure your system to automatically:")
        print("1. Start SSH agent on login")
        print("2. Load your SSH keys into the agent")
        print("3. Make SSH available immediately after restart")
        
        print("\nChoose setup method:")
        print("1. macOS (LaunchAgent) - Recommended for macOS")
        print("2. Shell config (.zshrc/.bash_profile) - Simple")
        print("3. Both methods - Most reliable")
        print("4. Custom configuration")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            self._setup_macos_launchagent()
        elif choice == "2":
            self._setup_shell_config()
        elif choice == "3":
            self._setup_macos_launchagent()
            self._setup_shell_config()
        elif choice == "4":
            self._setup_custom_persistence()
        else:
            print("Invalid option")
    
    def _setup_macos_launchagent(self):
        """Setup macOS LaunchAgent for auto-start"""
        print("\n🖥️  Setting up macOS LaunchAgent...")
        
        # Find SSH keys to auto-load
        keys_to_load = self._find_keys_to_autoload()
        
        # Create LaunchAgent plist
        plist_content = self._generate_launchagent_plist(keys_to_load)
        
        plist_path = Path.home() / "Library" / "LaunchAgents" / "com.ssh2ls.autostart.plist"
        plist_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(plist_path, 'w') as f:
            f.write(plist_content)
        
        # Load the LaunchAgent
        try:
            subprocess.run(['launchctl', 'load', str(plist_path)], check=True)
            subprocess.run(['launchctl', 'start', 'com.ssh2ls.autostart'], check=True)
            
            print(f"✓ LaunchAgent created: {plist_path}")
            print("✓ SSH agent will auto-start on login")
            print("\nTo test immediately:")
            print(f"  launchctl start com.ssh2ls.autostart")
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Could not load LaunchAgent: {e}")
            print("You may need to load it manually:")
            print(f"  launchctl load {plist_path}")
    
    def _setup_shell_config(self):
        """Add SSH agent startup to shell config"""
        print("\n🐚 Setting up shell configuration...")
        
        # Determine shell
        shell = os.environ.get('SHELL', '')
        if 'zsh' in shell:
            config_file = "~/.zshrc"
        elif 'bash' in shell:
            config_file = "~/.bash_profile"
        else:
            config_file = "~/.bashrc"
        
        config_path = Path(config_file).expanduser()
        
        # Find SSH keys to auto-load
        keys_to_load = self._find_keys_to_autoload()
        
        # Create config snippet
        config_snippet = self._generate_shell_config_snippet(keys_to_load)
        
        # Check if already configured
        if config_path.exists():
            with open(config_path, 'r') as f:
                existing = f.read()
            
            if "SSH_AUTH_SOCK" in existing and "ssh-agent" in existing:
                print(f"✓ SSH agent already configured in {config_file}")
                return
        
        # Append to config file
        with open(config_path, 'a') as f:
            f.write("\n\n" + config_snippet)
        
        print(f"✓ Added SSH agent configuration to {config_file}")
        print("\nTo apply immediately, run:")
        print(f"  source {config_file}")
        print("\nOr restart your terminal")
    
    def _find_keys_to_autoload(self):
        """Find SSH keys that should be auto-loaded"""
        print("\n🔍 Finding SSH keys to auto-load...")
        
        all_keys = self.key_manager.find_available_keys()
        keys_to_load = []
        
        # Always include common key names
        common_patterns = ['denbi', 'id_ed25519', 'id_rsa', 'github', 'gitlab']
        
        for key in all_keys:
            key_name = key.name
            # Check if key matches common patterns
            if any(pattern in key_name for pattern in common_patterns):
                keys_to_load.append(str(key))
                print(f"  ✓ Will auto-load: {key_name}")
        
        # Also check sessions for keys
        for session_name, session in self.ssh_manager.sessions.items():
            if 'jumphost' in session:
                key_path = session['jumphost'].get('private_key')
                if key_path and key_path not in keys_to_load:
                    keys_to_load.append(key_path)
                    print(f"  ✓ Will auto-load (from session '{session_name}'): {key_path}")
            elif 'host' in session:
                key_path = session['host'].get('private_key')
                if key_path and key_path not in keys_to_load:
                    keys_to_load.append(key_path)
                    print(f"  ✓ Will auto-load (from session '{session_name}'): {key_path}")
        
        # Ask user to confirm
        print(f"\nFound {len(keys_to_load)} key(s) to auto-load")
        if keys_to_load:
            confirm = input("\nProceed with these keys? (Y/n): ").strip().lower()
            if confirm == 'n':
                # Let user customize
                keys_to_load = self._customize_key_selection(keys_to_load)
        
        return keys_to_load
    
    def _customize_key_selection(self, keys):
        """Let user customize which keys to auto-load"""
        print("\nCustomize key selection:")
        selected_keys = []
        
        for i, key in enumerate(keys, 1):
            include = input(f"Auto-load {key}? (Y/n): ").strip().lower()
            if include != 'n':
                selected_keys.append(key)
                print(f"  ✓ Will auto-load")
            else:
                print(f"  ✗ Skipping")
        
        return selected_keys
    
    def _generate_launchagent_plist(self, keys):
        """Generate macOS LaunchAgent plist content"""
        # Build commands to load each key
        load_commands = []
        for key in keys:
            key_path = Path(key).expanduser()
            if key_path.exists():
                load_commands.append(f'ssh-add {key_path}')
        
        # Join commands with &&
        command_string = " && ".join(load_commands)
        
        plist_template = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ssh2ls.autostart</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>eval "$(ssh-agent)" && {command_string}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/ssh2ls_agent.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/ssh2ls_agent_error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>'''
        
        return plist_template
    
    def _generate_shell_config_snippet(self, keys):
        """Generate shell configuration snippet"""
        key_load_commands = []
        for key in keys:
            key_path = Path(key).expanduser()
            if key_path.exists():
                key_load_commands.append(f'    ssh-add {key_path} 2>/dev/null')
        
        snippet = f'''# SSH2LS - Auto-start SSH agent and load keys
# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

if [ -z "$SSH_AUTH_SOCK" ]; then
    # Start SSH agent if not running
    eval "$(ssh-agent -s)" > /dev/null
    
    # Load SSH keys
{chr(10).join(key_load_commands)}
    
    # Display loaded keys
    echo "🔑 SSH keys loaded: $(ssh-add -l | wc -l | tr -d ' ')"
fi

# Function to reload SSH keys
ssh2ls-reload-keys() {{
    echo "Reloading SSH keys..."
    ssh-add -D 2>/dev/null
{chr(10).join(key_load_commands)}
    echo "✅ Keys reloaded: $(ssh-add -l | wc -l | tr -d ' ')"
}}

# Alias for quick key reload
alias reload-ssh='ssh2ls-reload-keys'
'''
        
        return snippet
    
    def _setup_custom_persistence(self):
        """Setup custom persistence configuration"""
        print("\n⚙️  Custom persistence setup")
        
        print("\nAvailable options:")
        print("1. Add to ~/.ssh/config (SSH config)")
        print("2. Create standalone script")
        print("3. Add to crontab (run on boot)")
        print("4. Create system service")
        
        option = input("\nSelect option (1-4): ").strip()
        
        if option == "1":
            self._add_to_ssh_config()
        elif option == "2":
            self._create_standalone_script()
        elif option == "3":
            self._add_to_crontab()
        elif option == "4":
            self._create_system_service()
        else:
            print("Invalid option")
    
    def _add_to_ssh_config(self):
        """Add persistence configuration to SSH config"""
        ssh_config_path = Path("~/.ssh/config").expanduser()
        
        config_lines = [
            "# SSH2LS Auto-start Configuration",
            "# Add keys to agent automatically",
            "Host *",
            "    AddKeysToAgent yes",
            "    UseKeychain yes",  # macOS keychain integration
            ""
        ]
        
        if ssh_config_path.exists():
            with open(ssh_config_path, 'a') as f:
                f.write("\n" + "\n".join(config_lines))
        else:
            with open(ssh_config_path, 'w') as f:
                f.write("\n".join(config_lines))
        
        print(f"✓ Added to {ssh_config_path}")
        print("This enables 'AddKeysToAgent' for all SSH connections")
    
    def _create_standalone_script(self):
        """Create standalone restart recovery script"""
        keys_to_load = self._find_keys_to_autoload()
        
        script_content = f'''#!/bin/bash
# SSH2LS Restart Recovery Script
# Run this after restarting your system

echo "🔧 Restoring SSH access..."
echo "Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# Start SSH agent if needed
if [ -z "$SSH_AUTH_SOCK" ]; then
    echo "Starting SSH agent..."
    eval "$(ssh-agent -s)"
fi

# Load keys
echo "Loading SSH keys..."
'''
        
        for key in keys_to_load:
            key_path = Path(key).expanduser()
            if key_path.exists():
                script_content += f'ssh-add {key_path} 2>/dev/null && echo "  ✓ Loaded: {key}" || echo "  ✗ Failed: {key}"\n'
        
        script_content += '''
# Display status
echo ""
echo "✅ SSH Agent Status:"
ssh-add -l

# Test common connections
echo ""
echo "🔍 Testing connections..."
'''

        # Add connection tests for configured sessions
        for session_name in self.ssh_manager.list_sessions():
            script_content += f'echo "Testing {session_name}..."\n'
        
        script_path = Path.home() / "restore_ssh_access.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        script_path.chmod(0o755)
        
        print(f"\n📝 Created recovery script: {script_path}")
        print(f"Run with: {script_path}")
        print(f"\nTo run on startup, add to crontab:")
        print(f"  @reboot {script_path}")
    
    def _add_to_crontab(self):
        """Add to crontab for auto-start on boot"""
        keys_to_load = self._find_keys_to_autoload()
        
        # Create startup command
        load_commands = []
        for key in keys_to_load:
            key_path = Path(key).expanduser()
            if key_path.exists():
                load_commands.append(f'ssh-add {key_path}')
        
        startup_command = f'eval "$(ssh-agent -s)" && {" && ".join(load_commands)}'
        
        print(f"\n📋 Add this line to your crontab:")
        print(f"  @reboot {startup_command}")
        print("\nTo edit crontab:")
        print("  crontab -e")
        print("\nThen add the line above")
    
    def _create_system_service(self):
        """Create system service for auto-start"""
        if platform.system() == "Darwin":
            self._setup_macos_launchagent()
        else:
            print("System service creation only available for macOS via LaunchAgent")
            print("Use LaunchAgent option instead")
    
    # ADD THIS METHOD TOO:
    def check_persistence_status(self):
        """Check current SSH agent persistence status"""
        print("\n" + "="*80)
        print("🔍 SSH AGENT PERSISTENCE STATUS")
        print("="*80)
        
        checks = [
            ("SSH agent running", self._check_agent_running),
            ("Keys loaded", self._check_keys_loaded),
            ("LaunchAgent installed", self._check_launchagent),
            ("Shell config setup", self._check_shell_config),
        ]
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                status = "✅" if result else "❌"
                print(f"{status} {check_name}")
            except Exception as e:
                print(f"❌ {check_name}: Error - {e}")
    
    def _check_agent_running(self):
        """Check if SSH agent is running"""
        return bool(os.environ.get('SSH_AUTH_SOCK'))
    
    def _check_keys_loaded(self):
        """Check if keys are loaded in agent"""
        try:
            result = subprocess.run(['ssh-add', '-l'], capture_output=True, text=True)
            return result.returncode == 0 and result.stdout.strip() != ""
        except:
            return False
    
    def _check_launchagent(self):
        """Check if LaunchAgent is installed"""
        plist_path = Path.home() / "Library" / "LaunchAgents" / "com.ssh2ls.autostart.plist"
        return plist_path.exists()
    
    def _check_shell_config(self):
        """Check if shell config has SSH agent setup"""
        shell = os.environ.get('SHELL', '')
        if 'zsh' in shell:
            config_file = "~/.zshrc"
        elif 'bash' in shell:
            config_file = "~/.bash_profile"
        else:
            config_file = "~/.bashrc"
        
        config_path = Path(config_file).expanduser()
        if not config_path.exists():
            return False
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        return "SSH_AUTH_SOCK" in content and "ssh-agent" in content
    
    def quick_recovery(self):
        """Quick recovery after system restart"""
        print("\n🔄 QUICK RESTART RECOVERY")
        
        # Check SSH agent
        if not self._check_agent_running():
            print("Starting SSH agent...")
            subprocess.run(['eval', '$(ssh-agent)'], shell=True, capture_output=True)
        
        # Load all known keys
        keys = self.key_manager.find_available_keys()
        keys_loaded = 0
        
        for key in keys:
            print(f"Loading {key.name}...", end=" ")
            if self.key_manager.add_key_to_agent(key):
                print("✅")
                keys_loaded += 1
            else:
                print("❌")
        
        print(f"\n✅ Loaded {keys_loaded} key(s)")
        
        # Test connections
        print("\n🔍 Testing connections...")
        for session_name in self.ssh_manager.list_sessions():
            print(f"\nTesting {session_name}:")
            self.ssh_manager.test_connection(session_name)
    def _test_autostart(self):
        """Test the auto-start setup"""
        print("\n🧪 Testing auto-start configuration...")
        
        # Simulate a fresh environment
        print("1. Checking current environment...")
        print(f"   SSH_AUTH_SOCK: {'✅ Set' if os.environ.get('SSH_AUTH_SOCK') else '❌ Not set'}")
        
        # Test if keys would load
        print("\n2. Testing key loading...")
        test_key = Path("~/.ssh/denbi").expanduser()
        if test_key.exists():
            print(f"   Test key found: {test_key}")
            # Try to load it
            result = self.key_manager.add_key_to_agent(test_key)
            print(f"   Key loading: {'✅ Success' if result else '❌ Failed'}")
        else:
            print("   Test key not found")
        
        print("\n3. Checking persistence methods...")
        print(f"   LaunchAgent: {'✅ Installed' if self._check_launchagent() else '❌ Not installed'}")
        print(f"   Shell config: {'✅ Configured' if self._check_shell_config() else '❌ Not configured'}")
        
        print("\n✅ Auto-start test complete")
        print("\nTo fully test, restart your computer and check if:")
        print("1. SSH agent starts automatically")
        print("2. Your keys are loaded")
        print("3. You can connect without manual setup")
    ## set up restart-agent-recover
    def interactive_wizard(self):
        """Interactive wizard for setting up SSH connections"""
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                  SSH2LS - Connection Wizard                  ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print("\nThis wizard will help you setup SSH connections.")
        print("\nChoose connection type:")
        print("1. Direct connection (to a single host)")
        print("2. Multi-hop connection (jumphost → target)")
        print("3. Floating IP connection")
        print("4. Setup Password-less Authentication")  # NEW
        print("5. Manage Existing Connections")
        print("6. Transfer Files")
        print("7. Setup Remote Environment")
        print("8. Create SSH Tunnels")
        print("9. Test Connections (with password-less setup)")  # UPDATED
        print("0. Export Configuration")
        print("11. Setup Auto-load Keys on Startup") 
        print("X. Exit")
        
        choice = input("\nSelect type (0-9, X): ").strip()
        
        if choice == "1":
            self.setup_direct_connection_menu()
        elif choice == "2":
            self.setup_multi_hop_menu()
        elif choice == "3":
            self.floating_ip_menu()
        elif choice == "4": 
            self.setup_passwordless_menu()
        elif choice == "5":
            self.manage_connections_menu()
        elif choice == "6":
            self.file_transfer_menu()
        elif choice == "7":
            self.environment_setup_menu()
        elif choice == "8":
            self.tunnel_management_menu()
        elif choice == "9":
            self.test_connections_menu()
        elif choice == "0":
            self.export_configuration()
        elif choice == "11":
            self.setup_autostart_persistence()
        elif choice == "X":
            print("\nbye ~") 
        else:
            print("Invalid choice.")

    
    def setup_direct_connection_menu(self):
        """Setup direct SSH connection (no jumphost)"""
        print("\n" + "─"*70)
        print("SETUP DIRECT CONNECTION")
        print("─"*70)
        print("\nThis will setup a direct SSH connection to a single host.")
        print("Example: ssh user@server.example.com")
        print()
        
        session_name = input("Connection name (e.g., 'production', 'backup'): ").strip()
        if not session_name:
            print("✗ Connection name is required")
            return
        
        print("\n--- Host Configuration ---")
        host_ip = input("Host IP/Hostname: ").strip()
        if not host_ip:
            print("✗ Host IP is required")
            return
        
        host_user = input(f"Username [ubuntu]: ").strip() or "ubuntu"
        host_port = input(f"Port [22]: ").strip() or "22"
        
        try:
            host_port = int(host_port)
        except ValueError:
            print("✗ Port must be a number")
            return
        
        print("\n--- SSH Key ---")
        print("1. Use existing key")
        print("2. Generate new key")
        print("3. Enter path manually")
        
        key_choice = input("\nSelect option (1-3): ").strip()
        
        private_key_path = ""
        
        if key_choice == "1":
            # List available keys
            keys = self.key_manager.find_available_keys()
            if keys:
                print("\nAvailable keys:")
                for i, key in enumerate(keys, 1):
                    print(f"  {i}. {key.name}")
                
                key_idx = input(f"\nSelect key (1-{len(keys)}) or enter path: ").strip()
                if key_idx.isdigit() and 1 <= int(key_idx) <= len(keys):
                    private_key_path = str(keys[int(key_idx) - 1])
                else:
                    private_key_path = key_idx
            else:
                print("No keys found in ~/.ssh")
                private_key_path = input("Path to private key: ").strip()
        
        elif key_choice == "2":
            print("\nGenerating key...")
            try:
                private_key, public_key = self.key_manager.generate_key_pair(
                    key_name=f"id_ed25519_{session_name}",
                    key_type="ed25519",
                    comment=f"{getpass.getuser()}@{session_name}"
                )
                private_key_path = str(private_key)
            except Exception as e:
                print(f"✗ Error generating key: {e}")
                return
        
        else:
            private_key_path = input("Path to private key: ").strip()
        
        # Floating IP option
        use_floating = input("\nUse floating IP? (y/N): ").strip().lower() == 'y'
        floating_ip = None
        if use_floating:
            floating_ip = input("Floating IP address: ").strip()
        
        description = input("Description (optional): ").strip()
        
        # Create the configuration
        try:
            config = self.ssh_manager.create_direct_connection(
                name=session_name,
                host_ip=host_ip,
                host_user=host_user,
                private_key_path=private_key_path,
                port=host_port,
                description=description,
                floating_ip=floating_ip,
                use_floating_ip=use_floating
            )
            
            # Generate SSH config
            ssh_config = self.ssh_manager.generate_ssh_config(session_name)
            
            print(f"\n✅ Direct connection created!")
            print(f"\nSSH Configuration:")
            print("-" * 60)
            print(ssh_config)
            print("-" * 60)
            
            # Save to SSH config file
            save_to_ssh = input("\nAdd to ~/.ssh/config? (y/N): ").strip().lower() == 'y'
            if save_to_ssh:
                self._append_to_ssh_config(ssh_config)
                print("✓ Added to ~/.ssh/config")
            
            # Add key to agent
            add_to_agent = input("\nAdd key to SSH agent? (y/N): ").strip().lower() == 'y'
            if add_to_agent and private_key_path:
                key_path = Path(private_key_path).expanduser()
                self.key_manager.add_key_to_agent(key_path)
            
            # Test connection
            test_now = input("\nTest connection now? (y/N): ").strip().lower() == 'y'
            if test_now:
                result = self.ssh_manager.test_connection(session_name)
                if result.get('success'):
                    print("✓ Connection test successful!")
                else:
                    print(f"✗ Connection test failed: {result.get('test_result', {}).get('error')}")
            
        except Exception as e:
            print(f"✗ Error creating configuration: {e}")
        # while True:
        #     print("\n" + "="*70)
        #     print("MAIN MENU")
        #     print("="*70)
        #     print("1. SSH Key Management")
        #     print("2. Setup Multi-Hop Connection (like deNBI)")
        #     print("3. Manage Existing Connections")
        #     print("4. Transfer Files")
        #     print("5. Setup Remote Environment")
        #     print("6. Create SSH Tunnels")
        #     print("7. Show Quick Commands")
        #     print("8. Test Connections")
        #     print("9. Export Configuration")
        #     print("0. Exit")
            
        #     choice = input("\nSelect option (0-9): ").strip()
            
        #     if choice == "1":
        #         # self.key_management_menu()
        #         self.setup_connection_with_floating_ip()
        #     elif choice == "2":
        #         self.setup_multi_hop_menu()
        #         self.floating_ip_menu()
        #     elif choice == "3":
        #         self.manage_connections_menu()
        #     elif choice == "4":
        #         self.file_transfer_menu()
        #     elif choice == "5":
        #         self.environment_setup_menu()
        #     elif choice == "6":
        #         self.tunnel_management_menu()
        #     elif choice == "7":
        #         self.show_quick_commands()
        #     elif choice == "8":
        #         self.test_connections_menu()
        #     elif choice == "9":
        #         self.export_configuration()
        #     elif choice == "0":
        #         print("\n bye! ...")
        #         break
        #     else:
        #         print("Invalid option. Please try again.")
    
    def key_management_menu(self):
        """SSH key management menu"""
        print("\n" + "─"*70)
        print("SSH KEY MANAGEMENT")
        print("─"*70)
        
        while True:
            print("\nOptions:")
            print("1. Generate new SSH key pair")
            print("2. List keys in SSH agent")
            print("3. Add key to SSH agent")
            print("4. Remove key from SSH agent")
            print("5. Remove all keys from agent")
            print("6. Find available keys")
            print("7. Fix key permissions")
            print("8. Extract public key from private")
            print("9. Verify key pair")
            print("0. Back to main menu")
            
            choice = input("\nSelect option (0-9): ").strip()
            
            if choice == "1":
                self.generate_key_interactive()
            elif choice == "2":
                self.key_manager.list_keys_in_agent()
            elif choice == "3":
                self.add_key_to_agent_interactive()
            elif choice == "4":
                self.remove_key_from_agent_interactive()
            elif choice == "5":
                self.key_manager.remove_all_keys_from_agent()
            elif choice == "6":
                self.find_available_keys()
            elif choice == "7":
                self.fix_key_permissions_interactive()
            elif choice == "8":
                self.extract_public_key()
            elif choice == "9":
                self.verify_key_pair()
            elif choice == "0":
                break
            else:
                print("Invalid option.")
    
    def generate_key_interactive(self):
        """Interactive SSH key generation"""
        print("\nGenerating SSH key pair...")
        
        key_name = input("Key name [id_ed25519_denbi]: ").strip() or "id_ed25519_denbi"
        key_type = input("Key type (rsa/ed25519/ecdsa) [ed25519]: ").strip() or "ed25519"
        
        
        # Show available key types based on what's supported
        print("\nAvailable key types:")
        print("1. RSA (4096-bit) - Most compatible")
        print("2. Ed25519 - Most secure, if supported")
        print("3. ECDSA - Good alternative")
        type_choice = input("\nSelect key type (1-3) [1]: ").strip() or "1"
    
        if type_choice == "1":
            key_type = "rsa"
            key_size = 4096
        elif type_choice == "2":
            key_type = "ed25519"
            key_size = None
        elif type_choice == "3":
            key_type = "ecdsa"
            key_size = 521  # 521-bit ECDSA
        else:
            print("Invalid choice, using RSA")
            key_type = "rsa"
            key_size = 4096
        
        use_passphrase = input("Use passphrase? (y/N): ").strip().lower() == 'y'
        passphrase = None
        if use_passphrase:
            passphrase = getpass.getpass("Passphrase: ")
            passphrase_confirm = getpass.getpass("Confirm passphrase: ")
            if passphrase != passphrase_confirm:
                print("✗ Passphrases do not match!")
                return
        
        comment = input(f"Comment [{getpass.getuser()}@proj]: ").strip() or f"{getpass.getuser()}@denbi"
        
        try:
            private_key, public_key = self.key_manager.generate_key_pair(
                key_name=key_name,
                key_type=key_type,
                key_size=key_size,
                passphrase=passphrase,
                comment=comment
            )
            
            # Optionally add to agent
            add_to_agent = input("\nAdd key to SSH agent now? (y/N): ").strip().lower() == 'y'
            if add_to_agent:
                self.key_manager.add_key_to_agent(private_key, passphrase)
            
        except Exception as e:
            print(f"✗ Error generating key: {e}")
    
    def add_key_to_agent_interactive(self):
        """Add key to SSH agent interactively"""
        print("\nAdd key to SSH agent")
        
        # Find available keys
        keys = self.key_manager.find_available_keys()
        if keys:
            print("\nAvailable keys:")
            for i, key in enumerate(keys, 1):
                print(f"  {i}. {key.name}")
            
            key_idx = input(f"\nSelect key (1-{len(keys)}) or enter path: ").strip()
            if key_idx.isdigit() and 1 <= int(key_idx) <= len(keys):
                key_path = keys[int(key_idx) - 1]
            else:
                key_path = Path(key_idx).expanduser()
        else:
            key_path_str = input("Path to private key: ").strip()
            key_path = Path(key_path_str).expanduser()
        
        if not key_path.exists():
            print(f"✗ Key file not found: {key_path}")
            return
        
        # Check if key needs passphrase
        passphrase = None
        if HAS_PARAMIKO:
            try:
                # Try to load without passphrase first
                try:
                    paramiko.RSAKey.from_private_key_file(str(key_path))
                except paramiko.PasswordRequiredException:
                    passphrase = getpass.getpass(f"Passphrase for {key_path.name}: ")
            except Exception:
                pass
        
        success = self.key_manager.add_key_to_agent(key_path, passphrase)
        if success:
            print("✓ Key added successfully")
        else:
            print("✗ Failed to add key")
    
    def remove_key_from_agent_interactive(self):
        """Remove key from SSH agent interactively"""
        print("\nRemove key from SSH agent")
        
        # List keys in agent
        keys = self.key_manager.list_keys_in_agent()
        if not keys:
            print("No keys in SSH agent")
            return
        
        key_idx = input("\nSelect key number to remove (or 'all'): ").strip()
        if key_idx.lower() == 'all':
            self.key_manager.remove_all_keys_from_agent()
        elif key_idx.isdigit():
            # In ssh-add -l output, we can't easily remove by index
            # Instead, ask for key path
            key_path_str = input("Path to private key to remove: ").strip()
            key_path = Path(key_path_str).expanduser()
            self.key_manager.remove_key_from_agent(key_path)
        else:
            print("Invalid selection")
    
    def find_available_keys(self):
        """Find and display available keys"""
        print("\nFinding available SSH keys...")
        keys = self.key_manager.find_available_keys()
        
        if keys:
            print(f"\nFound {len(keys)} key(s):")
            for i, key in enumerate(keys, 1):
                pub_key = key.with_suffix('.pub')
                has_pub = "✓" if pub_key.exists() else "✗"
                permissions = oct(key.stat().st_mode)[-3:]
                correct_perms = "✓" if permissions == "600" else "✗"
                
                print(f"{i:2}. {key.name}")
                print(f"     Path: {key}")
                print(f"     Public key: {has_pub}")
                print(f"     Permissions: {permissions} {correct_perms}")
                
                # Check if in agent
                if HAS_PARAMIKO:
                    try:
                        # Extract public key for comparison
                        pub_key_content = self.key_manager.get_public_key_from_private(key)
                        if pub_key_content:
                            print(f"     Type: {pub_key_content.split()[0]}")
                    except:
                        pass
        else:
            print("No SSH keys found in ~/.ssh")
    
    def fix_key_permissions_interactive(self):
        """Fix key permissions interactively"""
        print("\nFix SSH key permissions")
        
        keys = self.key_manager.find_available_keys()
        if not keys:
            print("No keys found")
            return
        
        print("\nKeys with incorrect permissions:")
        keys_to_fix = []
        
        for key in keys:
            if not self.key_manager.check_key_permissions(key):
                permissions = oct(key.stat().st_mode)[-3:]
                print(f"  {key.name}: {permissions} (should be 600)")
                keys_to_fix.append(key)
        
        if not keys_to_fix:
            print("All keys have correct permissions")
            return
        
        fix_all = input("\nFix all incorrect permissions? (y/N): ").strip().lower() == 'y'
        if fix_all:
            for key in keys_to_fix:
                self.key_manager.fix_key_permissions(key)
        else:
            for key in keys_to_fix:
                fix = input(f"Fix permissions for {key.name}? (y/N): ").strip().lower() == 'y'
                if fix:
                    self.key_manager.fix_key_permissions(key)
    
    def extract_public_key(self):
        """Extract public key from private key"""
        print("\nExtract public key from private key")
        
        key_path_str = input("Path to private key: ").strip()
        key_path = Path(key_path_str).expanduser()
        
        if not key_path.exists():
            print(f"✗ Key file not found: {key_path}")
            return
        
        pub_key = self.key_manager.get_public_key_from_private(key_path)
        if pub_key:
            print(f"\nPublic key:")
            print("-" * 80)
            print(pub_key)
            print("-" * 80)
            
            save = input("\nSave to file? (y/N): ").strip().lower() == 'y'
            if save:
                pub_file = key_path.with_suffix('.pub')
                with open(pub_file, 'w') as f:
                    f.write(pub_key)
                print(f"✓ Saved to {pub_file}")
        else:
            print("✗ Could not extract public key")
    
    def verify_key_pair(self):
        """Verify that private and public keys match"""
        print("\nVerify key pair")
        
        priv_path_str = input("Path to private key: ").strip()
        priv_path = Path(priv_path_str).expanduser()
        
        pub_path_str = input("Path to public key [auto-detect]: ").strip()
        if not pub_path_str:
            pub_path = priv_path.with_suffix('.pub')
        else:
            pub_path = Path(pub_path_str).expanduser()
        
        if not priv_path.exists():
            print(f"✗ Private key not found: {priv_path}")
            return
        
        if not pub_path.exists():
            print(f"✗ Public key not found: {pub_path}")
            return
        
        if self.key_manager.verify_key_pair(priv_path, pub_path):
            print("✓ Key pair is valid - private and public keys match")
        else:
            print("✗ Key pair is invalid - private and public keys do not match")
    
    def setup_multi_hop_menu(self):
        """Setup multi-hop connection like deNBI"""
        print("\n" + "─"*70)
        print("SETUP MULTI-HOP CONNECTION")
        print("─"*70)
        print("\nThis will setup a connection like deNBI setup:")
        print("  Mac → Jumphost → Target VM")
        print()
        
        session_name = input("Connection name (e.g., 'denbi', 'production'): ").strip()
        if not session_name:
            print("✗ Connection name is required")
            return
        
        print("\n--- Jumphost Configuration ---")
        jumphost_ip = input("Jumphost IP/Hostname (e.g., 193.196.20.189): ").strip()
        if not jumphost_ip:
            print("✗ Jumphost IP is required")
            return
        
        jumphost_user = input(f"Jumphost username [ubuntu]: ").strip() or "ubuntu"
        
        print("\n--- SSH Key for Jumphost ---")
        print("1. Use existing key")
        print("2. Generate new key")
        print("3. Enter path manually")
        
        key_choice = input("\nSelect option (1-3): ").strip()
        
        private_key_path = ""
        
        if key_choice == "1":
            # List available keys
            keys = self.key_manager.find_available_keys()
            if keys:
                print("\nAvailable keys:")
                for i, key in enumerate(keys, 1):
                    print(f"  {i}. {key.name}")
                
                key_idx = input(f"\nSelect key (1-{len(keys)}) or enter path: ").strip()
                if key_idx.isdigit() and 1 <= int(key_idx) <= len(keys):
                    private_key_path = str(keys[int(key_idx) - 1])
                else:
                    private_key_path = key_idx
            else:
                print("No keys found in ~/.ssh")
                private_key_path = input("Path to private key: ").strip()
        
        elif key_choice == "2":
            print("\nGenerating key for jumphost...")
            try:
                private_key, public_key = self.key_manager.generate_key_pair(
                    key_name=f"id_ed25519_{session_name}",
                    key_type="ed25519",
                    comment=f"{getpass.getuser()}@{session_name}"
                )
                private_key_path = str(private_key)
                
                print("\nIMPORTANT: Share this public key with admin:")
                print("-" * 80)
                with open(public_key, 'r') as f:
                    print(f.read().strip())
                print("-" * 80)
                print("\nAsk them to add it to the jumphost's authorized_keys")
                input("\nPress Enter when the key has been added to the jumphost...")
            except Exception as e:
                print(f"✗ Error generating key: {e}")
                return
        
        else:
            private_key_path = input("Path to private key: ").strip()
        
        if not private_key_path:
            print("✗ Private key path is required")
            return
        
        print("\n--- Target VM Configuration ---")
        target_ip = input("Target VM IP (e.g., 192.168.54.219): ").strip()
        if not target_ip:
            print("✗ Target IP is required")
            return
        
        target_user = input(f"Target username [{jumphost_user}]: ").strip() or jumphost_user
        
        description = input("Description (optional): ").strip()
        
        # Create the configuration
        try:
            config = self.ssh_manager.create_jumphost_config(
                name=session_name,
                jumphost_ip=jumphost_ip,
                jumphost_user=jumphost_user,
                private_key_path=private_key_path,
                target_ip=target_ip,
                target_user=target_user,
                description=description
            )
            
            # Generate SSH config
            ssh_config = self.ssh_manager.generate_ssh_config(session_name)
            
            print(f"\n✅ Configuration created!")
            print(f"\nSSH Configuration:")
            print("-" * 60)
            print(ssh_config)
            print("-" * 60)
            
            # Save to SSH config file
            save_to_ssh = input("\nAdd to ~/.ssh/config? (y/N): ").strip().lower() == 'y'
            if save_to_ssh:
                self._append_to_ssh_config(ssh_config)
                print("✓ Added to ~/.ssh/config")
            
            # Setup agent forwarding
            setup_agent = input("\nSetup SSH agent forwarding? (y/N): ").strip().lower() == 'y'
            if setup_agent:
                self.ssh_manager.setup_agent_forwarding(session_name)
            
            # Test connection
            test_now = input("\nTest connection now? (y/N): ").strip().lower() == 'y'
            if test_now:
                self.ssh_manager.test_connection(session_name)
            
        except Exception as e:
            print(f"✗ Error creating configuration: {e}")
    
    
    def floating_ip_menu(self):
        """Floating IP management menu"""
        print("\n" + "="*70)
        print("FLOATING IP MANAGEMENT")
        print("="*70)
        
        while True:
            print("\nOptions:")
            print("1. Register new floating IP")
            print("2. List floating IPs")
            print("3. Update floating IP mapping")
            print("4. Test floating IP connection")
            print("5. Delete floating IP")
            print("6. Setup connection with floating IP")
            print("7. Back to main menu")
            
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == "1":
                self.register_floating_ip()
            elif choice == "2":
                self.list_floating_ips()
            elif choice == "3":
                self.update_floating_ip_mapping()
            elif choice == "4":
                self.test_floating_ip()
            elif choice == "5":
                self.delete_floating_ip()
            elif choice == "6":
                self.setup_connection_with_floating_ip()
            elif choice == "7":
                break
            else:
                print("Invalid option.")
    
    def register_floating_ip(self):
        """Register a new floating IP"""
        print("\n" + "="*70)
        print("REGISTER FLOATING IP")
        print("="*70)
        
        name = input("Floating IP name (e.g., 'web-floating', 'db-floating'): ").strip()
        if not name:
            print("✗ Name is required")
            return
        
        floating_ip = input("Floating IP address: ").strip()
        if not floating_ip:
            print("✗ Floating IP is required")
            return
        
        fixed_ip = input("Fixed IP address (optional, press Enter to skip): ").strip()
        
        description = input("Description (optional): ").strip()
        cloud_provider = input("Cloud provider (e.g., OpenStack, AWS, GCP) [OpenStack]: ").strip() or "OpenStack"
        region = input("Region (optional): ").strip()
        
        try:
            config = self.ssh_manager.floating_ip_manager.register_floating_ip(
                name=name,
                floating_ip=floating_ip,
                fixed_ip=fixed_ip or None,
                description=description,
                cloud_provider=cloud_provider,
                region=region
            )
            
            # Test the floating IP
            test_now = input("\nTest floating IP now? (y/N): ").strip().lower() == 'y'
            if test_now:
                updated = self.ssh_manager.floating_ip_manager.update_floating_ip_status(name)
                print(f"\nStatus: {updated['status']}")
                if 'current_mapping' in updated:
                    print(f"Current mapping: {updated['current_mapping']}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def list_floating_ips(self):
        """List all floating IPs"""
        print("\n" + "="*70)
        print("FLOATING IPS")
        print("="*70)
        
        floating_ips = self.ssh_manager.floating_ip_manager.list_floating_ips()
        
        if not floating_ips:
            print("No floating IPs registered.")
            return
        
        print(f"\nFound {len(floating_ips)} floating IP(s):")
        print("-" * 70)
        
        for i, config in enumerate(floating_ips, 1):
            print(f"\n{i}. {config['name']}:")
            print(f"   Floating IP: {config['floating_ip']}")
            if config.get('fixed_ip'):
                print(f"   Fixed IP:    {config['fixed_ip']}")
            print(f"   Status:      {config.get('status', 'unknown')}")
            if config.get('current_mapping'):
                print(f"   Maps to:     {config['current_mapping']}")
            if config.get('description'):
                print(f"   Description: {config['description']}")
            print(f"   Created:     {config.get('created', '')}")
    
    def update_floating_ip_mapping(self):
        """Update floating IP mapping"""
        floating_ips = self.ssh_manager.floating_ip_manager.list_floating_ips()
        
        if not floating_ips:
            print("No floating IPs registered.")
            return
        
        print("\nSelect floating IP to update:")
        for i, config in enumerate(floating_ips, 1):
            print(f"{i}. {config['name']} ({config['floating_ip']})")
        
        choice = input(f"\nSelect (1-{len(floating_ips)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(floating_ips):
            name = floating_ips[int(choice) - 1]['name']
            self.ssh_manager.floating_ip_manager.update_floating_ip_status(name)
        else:
            print("Invalid selection.")
    
    def test_floating_ip(self):
        """Test floating IP connection"""
        floating_ips = self.ssh_manager.floating_ip_manager.list_floating_ips()
        
        if not floating_ips:
            print("No floating IPs registered.")
            return
        
        print("\nSelect floating IP to test:")
        for i, config in enumerate(floating_ips, 1):
            print(f"{i}. {config['name']} ({config['floating_ip']})")
        
        choice = input(f"\nSelect (1-{len(floating_ips)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(floating_ips):
            name = floating_ips[int(choice) - 1]['name']
            
            # Get SSH credentials for testing
            print("\nSSH credentials for testing:")
            user = input("Username [ubuntu]: ").strip() or "ubuntu"
            key_path = input("Private key path [~/.ssh/id_rsa]: ").strip() or "~/.ssh/id_rsa"
            
            config = self.ssh_manager.floating_ip_manager.get_floating_ip(name)
            if config:
                print(f"\nTesting floating IP: {config['floating_ip']}")
                
                # Test with ssh command
                cmd = ['ssh', '-i', key_path,
                       '-o', 'ConnectTimeout=5',
                       '-o', 'BatchMode=yes',
                       f"{user}@{config['floating_ip']}",
                       'echo "Floating IP test: $(hostname)"']
                
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        print("✓ Floating IP is reachable")
                        print(f"Response: {result.stdout.strip()}")
                    else:
                        print(f"✗ Floating IP is not reachable")
                        print(f"Error: {result.stderr}")
                        
                except Exception as e:
                    print(f"✗ Error: {e}")
        else:
            print("Invalid selection.")
    
    def delete_floating_ip(self):
        """Delete a floating IP"""
        floating_ips = self.ssh_manager.floating_ip_manager.list_floating_ips()
        
        if not floating_ips:
            print("No floating IPs registered.")
            return
        
        print("\nSelect floating IP to delete:")
        for i, config in enumerate(floating_ips, 1):
            print(f"{i}. {config['name']} ({config['floating_ip']})")
        
        choice = input(f"\nSelect (1-{len(floating_ips)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(floating_ips):
            name = floating_ips[int(choice) - 1]['name']
            
            confirm = input(f"\nDelete floating IP '{name}'? (y/N): ").strip().lower()
            if confirm == 'y':
                if self.ssh_manager.floating_ip_manager.delete_floating_ip(name):
                    print(f"✓ Deleted floating IP: {name}")
                else:
                    print(f"✗ Could not delete floating IP: {name}")
        else:
            print("Invalid selection.")
    
    def setup_connection_with_floating_ip(self):
        """Setup a connection with floating IP"""
        print("\n" + "="*70)
        print("SETUP CONNECTION WITH FLOATING IP")
        print("="*70)
        
        session_name = input("Connection name: ").strip()
        if not session_name:
            print("✗ Connection name is required")
            return
        
        print("\n--- Floating IP Configuration ---")
        floating_ip = input("Floating IP address: ").strip()
        if not floating_ip:
            print("✗ Floating IP is required")
            return
        
        fixed_ip = input("Fixed IP address (optional): ").strip()
        
        use_floating = input("Use floating IP? (Y/n): ").strip().lower()
        use_floating_ip = use_floating != 'n'
        
        print("\n--- SSH Configuration ---")
        jumphost_user = input("Jumphost username [ubuntu]: ").strip() or "ubuntu"
        
        private_key_path = input("Private key path [~/.ssh/id_rsa]: ").strip() 
        if not private_key_path:
            private_key_path = "~/.ssh/id_rsa"
        
        print("\n--- Target Configuration (Optional) ---")
        target_ip = input("Target IP (press Enter to skip): ").strip()
        target_user = ""
        if target_ip:
            target_user = input(f"Target username [{jumphost_user}]: ").strip() or jumphost_user
        
        description = input("Description (optional): ").strip()
        
        try:
            config = self.ssh_manager.create_jumphost_config_with_floating_ip(
                name=session_name,
                floating_ip=floating_ip,
                fixed_ip=fixed_ip or None,
                jumphost_user=jumphost_user,
                target_ip=target_ip or None,
                target_user=target_user or None,
                private_key_path=private_key_path,
                use_floating_ip=use_floating_ip,
                description=description
            )
            
            # Generate SSH config
            ssh_config = self.ssh_manager.generate_ssh_config_with_floating_ip(session_name)
            
            print(f"\n✅ Configuration created!")
            print(f"\nSSH Configuration:")
            print("-" * 60)
            print(ssh_config)
            print("-" * 60)
            
            # Save to SSH config file
            save_to_ssh = input("\nAdd to ~/.ssh/config? (y/N): ").strip().lower() == 'y'
            if save_to_ssh:
                self._append_to_ssh_config(ssh_config)
                print("✓ Added to ~/.ssh/config")
            
            # Test connection
            test_now = input("\nTest connection now? (y/N): ").strip().lower() == 'y'
            if test_now:
                self.ssh_manager.test_connection_with_floating_ip(session_name)
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def _append_to_ssh_config(self, config_text: str):
        """Append configuration to ~/.ssh/config"""
        ssh_config_path = Path("~/.ssh/config").expanduser()
        ssh_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add separator if file exists and isn't empty
        if ssh_config_path.exists() and ssh_config_path.stat().st_size > 0:
            with open(ssh_config_path, 'a') as f:
                f.write(f"\n\n# Added by ssh2ls on {datetime.now().strftime('%Y-%m-%d')}\n")
                f.write(config_text)
                f.write("\n")
        else:
            with open(ssh_config_path, 'w') as f:
                f.write(f"\n\n# Added by ssh2ls on {datetime.now().strftime('%Y-%m-%d')}\n")
                f.write(config_text)
                f.write("\n")

    def manage_connections_menu(self):
        """Manage existing connections"""
        sessions = self.ssh_manager.list_sessions()
        
        if not sessions:
            print("No connections configured.")
            return
        
        print("\n" + "─"*70)
        print("MANAGE CONNECTIONS")
        print("─"*70)
        
        while True:
            print("\nConfigured connections:")
            for i, name in enumerate(sessions, 1):
                session = self.ssh_manager.sessions[name]
                connection_type = session.get("connection_type", "jumphost")
                
                try:
                    if connection_type == "direct":
                        # Direct connection display
                        host = session.get("host", {})
                        if host:
                            effective_ip = host.get('effective_ip', host.get('ip', 'unknown'))
                            user = host.get('user', 'unknown')
                            port = host.get('port', 22)
                            print(f"{i:2}. {name}: {user}@{effective_ip}:{port} (Direct)")
                        else:
                            print(f"{i:2}. {name}: Invalid direct configuration")
                    else:
                        # Jumphost connection display
                        jh = session.get("jumphost", {})
                        target = session.get("target", {})
                        if jh and target:
                            jh_ip = jh.get('effective_ip', jh.get('ip', 'unknown'))
                            jh_user = jh.get('user', 'unknown')
                            target_ip = target.get('ip', 'unknown')
                            target_user = target.get('user', 'unknown')
                            print(f"{i:2}. {name}: {jh_user}@{jh_ip} → {target_user}@{target_ip}")
                        else:
                            print(f"{i:2}. {name}: Invalid jumphost configuration")
                except Exception as e:
                    print(f"{i:2}. {name}: Error displaying - {e}")
            print("\nOptions:")
            print("1. Connect to jumphost")
            print("2. Connect to target via jumphost")
            print("3. Test connection")
            print("4. Show SSH config")
            print("5. Delete connection")
            print("6. Setup agent forwarding")
            print("7. Back to main menu")
            
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == "1":
                self._connect_to_host("jumphost")
            elif choice == "2":
                self._connect_to_host("target")
            elif choice == "3":
                self._test_specific_connection()
            elif choice == "4":
                self._show_ssh_config()
            elif choice == "5":
                self._delete_connection()
            elif choice == "6":
                self._setup_agent_for_connection()
            elif choice == "7":
                break
            else:
                print("Invalid option.")
    
    def _connect_to_host(self, host_type: str):
        """Connect to jumphost or target"""
        sessions = self.ssh_manager.list_sessions()
        if not sessions:
            print("No connections configured.")
            return
        
        print("\nSelect connection:")
        for i, name in enumerate(sessions, 1):
            session = self.ssh_manager.sessions[name]
            connection_type = session.get("connection_type", "jumphost")
            
            if connection_type == "direct":
                host = session["host"]
                print(f"{i}. {name} (Direct: {host['user']}@{host['ip']})")
            else:
                jh = session["jumphost"]
                print(f"{i}. {name} (Jumphost: {jh['user']}@{jh['ip']})")
    
        choice = input(f"\nSelect connection (1-{len(sessions)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(sessions):
            session_name = sessions[int(choice) - 1]
            
            # Check connection type
            session = self.ssh_manager.sessions[session_name]
            connection_type = session.get("connection_type", "jumphost")
            
            if connection_type == "direct":
                # For direct connections, only "jumphost" option makes sense
                # (it connects to the direct host)
                self.ssh_manager.interactive_shell(session_name, "jumphost")
            else:
                # For jumphost connections, use the specified hop
                self.ssh_manager.interactive_shell(session_name, host_type)
        else:
            print("Invalid selection.") 
    def _test_specific_connection(self):
        """Test a specific connection"""
        sessions = self.ssh_manager.list_sessions()
        if not sessions:
            print("No connections configured.")
            return
        
        print("\nSelect connection to test:")
        for i, name in enumerate(sessions, 1):
            session = self.ssh_manager.sessions[name]
            connection_type = session.get("connection_type", "jumphost")
            
            if connection_type == "direct":
                host = session["host"]
                print(f"{i}. {name} (Direct: {host['user']}@{host['ip']})")
            else:
                jh = session["jumphost"]
                target = session["target"]
                print(f"{i}. {name} ({jh['user']}@{jh['ip']} → {target['user']}@{target['ip']})")
        
        choice = input(f"\nSelect connection (1-{len(sessions)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(sessions):
            session_name = sessions[int(choice) - 1]
            self.ssh_manager.test_connection(session_name)
        else:
            print("Invalid selection.")
    def _show_ssh_config(self):
        """Show SSH config for a connection"""
        sessions = self.ssh_manager.list_sessions()
        if not sessions:
            print("No connections configured.")
            return
        
        print("\nSelect connection:")
        for i, name in enumerate(sessions, 1):
            session = self.ssh_manager.sessions[name]
            connection_type = session.get("connection_type", "jumphost")
            
            if connection_type == "direct":
                host = session["host"]
                print(f"{i}. {name} (Direct: {host['user']}@{host['ip']})")
            else:
                jh = session["jumphost"]
                target = session["target"]
                print(f"{i}. {name} ({jh['user']}@{jh['ip']} → {target['user']}@{target['ip']})")
        
        choice = input(f"\nSelect connection (1-{len(sessions)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(sessions):
            session_name = sessions[int(choice) - 1]
            config = self.ssh_manager.generate_ssh_config(session_name)
            print(f"\nSSH Config for '{session_name}':")
            print("-" * 60)
            print(config)
            print("-" * 60)
        else:
            print("Invalid selection.")

    def _delete_connection(self):
        """Delete a connection"""
        sessions = self.ssh_manager.list_sessions()
        if not sessions:
            print("No connections configured.")
            return
        
        print("\nSelect connection to delete:")
        for i, name in enumerate(sessions, 1):
            session = self.ssh_manager.sessions[name]
            connection_type = session.get("connection_type", "jumphost")
            
            if connection_type == "direct":
                host = session["host"]
                print(f"{i}. {name} (Direct: {host['user']}@{host['ip']})")
            else:
                jh = session["jumphost"]
                target = session["target"]
                print(f"{i}. {name} ({jh['user']}@{jh['ip']} → {target['user']}@{target['ip']})")
        
        choice = input(f"\nSelect connection (1-{len(sessions)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(sessions):
            session_name = sessions[int(choice) - 1]
            confirm = input(f"\nAre you sure you want to delete '{session_name}'? (y/N): ").strip().lower()
            if confirm == 'y':
                self.ssh_manager.delete_session(session_name)
        else:
            print("Invalid selection.")
    

    def _setup_agent_for_connection(self):
        """Setup agent forwarding for a connection"""
        sessions = self.ssh_manager.list_sessions()
        if not sessions:
            print("No connections configured.")
            return
        
        print("\nSelect connection:")
        for i, name in enumerate(sessions, 1):
            session = self.ssh_manager.sessions[name]
            connection_type = session.get("connection_type", "jumphost")
            
            if connection_type == "direct":
                host = session["host"]
                print(f"{i}. {name} (Direct: {host['user']}@{host['ip']})")
            else:
                jh = session["jumphost"]
                target = session["target"]
                print(f"{i}. {name} ({jh['user']}@{jh['ip']} → {target['user']}@{target['ip']})")
        
        choice = input(f"\nSelect connection (1-{len(sessions)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(sessions):
            session_name = sessions[int(choice) - 1]
            session = self.ssh_manager.sessions[session_name]
            connection_type = session.get("connection_type", "jumphost")
            
            if connection_type == "direct":
                print("Note: Agent forwarding is always enabled for direct connections")
                # Just add key to agent
                host = session["host"]
                if host.get('private_key'):
                    key_path = Path(host['private_key']).expanduser()
                    self.key_manager.add_key_to_agent(key_path)
            else:
                self.ssh_manager.setup_agent_forwarding(session_name)
        else:
            print("Invalid selection.")

    
    def file_transfer_menu(self):
        """File transfer menu"""
        sessions = self.ssh_manager.list_sessions()
        
        if not sessions:
            print("No connections configured.")
            return
        
        print("\n" + "─"*70)
        print("FILE TRANSFER")
        print("─"*70)
        
        print("\nSelect connection:")
        for i, name in enumerate(sessions, 1):
            print(f"{i}. {name}")
        
        choice = input(f"\nSelect connection (1-{len(sessions)}): ").strip()
        if not (choice.isdigit() and 1 <= int(choice) <= len(sessions)):
            print("Invalid selection.")
            return
        
        session_name = sessions[int(choice) - 1]
        
        print("\nTransfer direction:")
        print("1. Upload (local → remote)")
        print("2. Download (remote → local)")
        
        direction_choice = input("\nSelect direction (1-2): ").strip()
        if direction_choice == "1":
            direction = "upload"
        elif direction_choice == "2":
            direction = "download"
        else:
            print("Invalid selection.")
            return
        
        if direction == "upload":
            local_path = input("Local file/folder path: ").strip()
            remote_path = input("Remote destination path: ").strip()
        else:
            remote_path = input("Remote file/folder path: ").strip()
            local_path = input("Local destination path: ").strip()
        
        if not local_path or not remote_path:
            print("Both paths are required")
            return
        
        print(f"\nTransferring {direction}...")
        success = self.ssh_manager.transfer_files(
            session_name=session_name,
            local_path=local_path,
            remote_path=remote_path,
            direction=direction
        )
        
        if success:
            print("✅ Transfer completed successfully!")
        else:
            print("❌ Transfer failed.")
    
    def environment_setup_menu(self):
        """Setup remote environment (like nf-core setup)"""
        sessions = self.ssh_manager.list_sessions()
        
        if not sessions:
            print("No connections configured.")
            return
        
        print("\n" + "─"*70)
        print("REMOTE ENVIRONMENT SETUP")
        print("─"*70)
        print("\nThis will help you setup a remote environment like nf-core setup.")
        
        print("\nSelect connection:")
        for i, name in enumerate(sessions, 1):
            print(f"{i}. {name}")
        
        choice = input(f"\nSelect connection (1-{len(sessions)}): ").strip()
        if not (choice.isdigit() and 1 <= int(choice) <= len(sessions)):
            print("Invalid selection.")
            return
        
        session_name = sessions[int(choice) - 1]
        
        print("\nChoose setup template:")
        print("1. Basic Ubuntu setup (update, install tools)")
        print("2. Bioinformatics/nf-core setup")
        print("3. Docker setup")
        print("4. Python development")
        print("5. Custom commands")
        
        template_choice = input("\nSelect template (1-5): ").strip()
        
        commands = []
        
        if template_choice == "1":
            # Basic Ubuntu setup
            commands = [
                "sudo apt update",
                "sudo apt upgrade -y",
                "sudo apt install -y git wget curl python3 python3-pip",
                "sudo apt install -y htop ncdu tmux",
                "echo 'Basic setup complete!'"
            ]
        
        elif template_choice == "2":
            # Bioinformatics/nf-core setup
            commands = [
                "sudo apt update && sudo apt upgrade -y",
                "sudo apt install -y git wget curl python3 python3-pip",
                "# Install Apptainer (Singularity)",
                "sudo apt install -y apptainer",
                "# Create data directory",
                "mkdir -p ~/chipseq_data",
                "# Download nf-core ChIP-seq pipeline",
                "git clone https://github.com/nf-core/chipseq.git",
                "cd chipseq && git checkout 2.1.0",
                "echo 'nf-core setup complete!'",
                "echo 'Next: Copy data and run: apptainer pull docker://nfcore/chipseq'"
            ]
        
        elif template_choice == "3":
            # Docker setup
            commands = [
                "sudo apt update",
                "sudo apt install -y docker.io",
                "sudo systemctl start docker",
                "sudo systemctl enable docker",
                "sudo usermod -aG docker $USER",
                "echo 'Docker setup complete!'",
                "echo 'Log out and log back in for group changes to take effect'"
            ]
        
        elif template_choice == "4":
            # Python development
            commands = [
                "sudo apt update",
                "sudo apt install -y python3-pip python3-venv",
                "python3 -m pip install --upgrade pip",
                "mkdir -p ~/projects",
                "echo 'Python development setup complete!'"
            ]
        
        elif template_choice == "5":
            # Custom commands
            print("\nEnter commands (one per line, empty line to finish):")
            while True:
                cmd = input("> ").strip()
                if not cmd:
                    break
                commands.append(cmd)
        
        else:
            print("Invalid selection.")
            return
        
        if not commands:
            print("No commands to execute.")
            return
        
        print("\nCommands to execute:")
        for i, cmd in enumerate(commands, 1):
            print(f"{i:2}. {cmd}")
        
        confirm = input("\nExecute these commands on the remote server? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return
        
        print("\nStarting environment setup...")
        success = self.ssh_manager.batch_setup_environment(session_name, commands)
        
        if success:
            print("✅ Environment setup completed!")
        else:
            print("❌ Environment setup failed.")
    
    def tunnel_management_menu(self):
        """SSH tunnel management menu"""
        print("\n" + "─"*70)
        print("SSH TUNNEL MANAGEMENT")
        print("─"*70)
        
        tunnels = list(self.ssh_manager.tunnels.keys())
        
        while True:
            if tunnels:
                print("\nConfigured tunnels:")
                for i, name in enumerate(tunnels, 1):
                    tunnel = self.ssh_manager.tunnels[name]
                    status = "🟢" if tunnel['status'] == 'running' else "🔴"
                    print(f"{i:2}. {status} {name}: localhost:{tunnel['local_port']} → {tunnel['remote_host']}:{tunnel['remote_port']}")
            else:
                print("\nNo tunnels configured.")
            
            print("\nOptions:")
            print("1. Create new tunnel")
            print("2. Start tunnel")
            print("3. Stop tunnel")
            print("4. View tunnel details")
            print("5. Delete tunnel")
            print("6. Back to main menu")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == "1":
                self._create_tunnel_interactive()
                tunnels = list(self.ssh_manager.tunnels.keys())  # Refresh list
            elif choice == "2":
                self._start_tunnel_interactive()
            elif choice == "3":
                self._stop_tunnel_interactive()
            elif choice == "4":
                self._view_tunnel_details()
            elif choice == "5":
                self._delete_tunnel()
                tunnels = list(self.ssh_manager.tunnels.keys())  # Refresh list
            elif choice == "6":
                break
            else:
                print("Invalid option.")
    
    def _create_tunnel_interactive(self):
        """Create tunnel interactively"""
        sessions = self.ssh_manager.list_sessions()
        
        if not sessions:
            print("No connections configured. Create a connection first.")
            return
        
        print("\nSelect connection:")
        for i, name in enumerate(sessions, 1):
            print(f"{i}. {name}")
        
        choice = input(f"\nSelect connection (1-{len(sessions)}): ").strip()
        if not (choice.isdigit() and 1 <= int(choice) <= len(sessions)):
            print("Invalid selection.")
            return
        
        session_name = sessions[int(choice) - 1]
        
        print("\nTunnel configuration:")
        local_port = input("Local port (e.g., 8080): ").strip()
        remote_host = input("Remote host (e.g., localhost or 192.168.1.100): ").strip()
        remote_port = input("Remote port (e.g., 80): ").strip()
        tunnel_name = input("Tunnel name (optional): ").strip()
        
        try:
            local_port = int(local_port)
            remote_port = int(remote_port)
            
            tunnel = self.ssh_manager.create_tunnel(
                session_name=session_name,
                local_port=local_port,
                remote_host=remote_host,
                remote_port=remote_port,
                tunnel_name=tunnel_name
            )
            
            start_now = input("\nStart tunnel now? (y/N): ").strip().lower() == 'y'
            if start_now:
                background = input("Run in background? (y/N): ").strip().lower() == 'y'
                self.ssh_manager.start_tunnel(tunnel['name'], background)
            
        except ValueError:
            print("✗ Ports must be numbers.")
        except Exception as e:
            print(f"✗ Error creating tunnel: {e}")
    
    def _start_tunnel_interactive(self):
        """Start tunnel interactively"""
        tunnels = list(self.ssh_manager.tunnels.keys())
        if not tunnels:
            print("No tunnels configured.")
            return
        
        print("\nSelect tunnel to start:")
        for i, name in enumerate(tunnels, 1):
            tunnel = self.ssh_manager.tunnels[name]
            status = "🟢" if tunnel['status'] == 'running' else "🔴"
            print(f"{i}. {status} {name}")
        
        choice = input(f"\nSelect tunnel (1-{len(tunnels)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(tunnels):
            tunnel_name = tunnels[int(choice) - 1]
            background = input("Run in background? (y/N): ").strip().lower() == 'y'
            self.ssh_manager.start_tunnel(tunnel_name, background)
        else:
            print("Invalid selection.")
    
    def _stop_tunnel_interactive(self):
        """Stop tunnel interactively"""
        tunnels = list(self.ssh_manager.tunnels.keys())
        if not tunnels:
            print("No tunnels configured.")
            return
        
        # Filter for running tunnels
        running_tunnels = []
        for name in tunnels:
            tunnel = self.ssh_manager.tunnels[name]
            if tunnel['status'] == 'running':
                running_tunnels.append(name)
        
        if not running_tunnels:
            print("No running tunnels.")
            return
        
        print("\nSelect tunnel to stop:")
        for i, name in enumerate(running_tunnels, 1):
            tunnel = self.ssh_manager.tunnels[name]
            print(f"{i}. {name} (PID: {tunnel.get('pid', 'N/A')})")
        
        choice = input(f"\nSelect tunnel (1-{len(running_tunnels)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(running_tunnels):
            tunnel_name = running_tunnels[int(choice) - 1]
            self.ssh_manager.stop_tunnel(tunnel_name)
        else:
            print("Invalid selection.")
    
    def _view_tunnel_details(self):
        """View tunnel details"""
        tunnels = list(self.ssh_manager.tunnels.keys())
        if not tunnels:
            print("No tunnels configured.")
            return
        
        print("\nSelect tunnel to view:")
        for i, name in enumerate(tunnels, 1):
            print(f"{i}. {name}")
        
        choice = input(f"\nSelect tunnel (1-{len(tunnels)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(tunnels):
            tunnel_name = tunnels[int(choice) - 1]
            tunnel = self.ssh_manager.tunnels[tunnel_name]
            
            print(f"\nTunnel: {tunnel_name}")
            print("-" * 60)
            print(f"Status:      {tunnel['status']}")
            print(f"Local port:  {tunnel['local_port']}")
            print(f"Remote:      {tunnel['remote_host']}:{tunnel['remote_port']}")
            print(f"Type:        {tunnel['type']}")
            print(f"Created:     {tunnel['created']}")
            
            if tunnel['status'] == 'running':
                print(f"PID:         {tunnel.get('pid', 'N/A')}")
                print(f"Started:     {tunnel.get('started', 'N/A')}")
            
            print(f"\nCommand:")
            print(tunnel['command'])
            print("-" * 60)
        else:
            print("Invalid selection.")
    
    def _delete_tunnel(self):
        """Delete a tunnel"""
        tunnels = list(self.ssh_manager.tunnels.keys())
        if not tunnels:
            print("No tunnels configured.")
            return
        
        print("\nSelect tunnel to delete:")
        for i, name in enumerate(tunnels, 1):
            print(f"{i}. {name}")
        
        choice = input(f"\nSelect tunnel (1-{len(tunnels)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(tunnels):
            tunnel_name = tunnels[int(choice) - 1]
            
            # Stop if running
            tunnel = self.ssh_manager.tunnels[tunnel_name]
            if tunnel['status'] == 'running':
                stop = input(f"Tunnel is running. Stop it first? (y/N): ").strip().lower() == 'y'
                if stop:
                    self.ssh_manager.stop_tunnel(tunnel_name)
            
            confirm = input(f"\nDelete tunnel '{tunnel_name}'? (y/N): ").strip().lower()
            if confirm == 'y':
                del self.ssh_manager.tunnels[tunnel_name]
                self.ssh_manager.save_tunnels()
                print(f"✓ Deleted tunnel: {tunnel_name}")
        else:
            print("Invalid selection.")
    
    def show_quick_commands(self):
        """Show quick commands for a connection"""
        sessions = self.ssh_manager.list_sessions()
        
        if not sessions:
            print("No connections configured.")
            return
        
        print("\n" + "─"*70)
        print("QUICK COMMANDS")
        print("─"*70)
        
        print("\nSelect connection:")
        for i, name in enumerate(sessions, 1):
            print(f"{i}. {name}")
        
        choice = input(f"\nSelect connection (1-{len(sessions)}): ").strip()
        if not (choice.isdigit() and 1 <= int(choice) <= len(sessions)):
            print("Invalid selection.")
            return
        
        session_name = sessions[int(choice) - 1]
        
        commands = self.ssh_manager.get_quick_commands(session_name)
        
        print(f"\nQuick commands for '{session_name}':")
        print("-" * 70)
        for desc, cmd in commands.items():
            print(f"\n{desc.replace('_', ' ').title()}:")
            print(f"  {cmd}")
        print("-" * 70)
        
        # Copy to clipboard option
        if platform.system() == "Darwin":  # macOS
            copy_all = input("\nCopy all commands to clipboard? (y/N): ").strip().lower()
            if copy_all == 'y':
                all_cmds = "\n".join([f"# {k}\n{v}\n" for k, v in commands.items()])
                subprocess.run(['pbcopy'], input=all_cmds.encode())
                print("✓ Commands copied to clipboard!")
    def test_connections_menu(self):
            """Test connections menu with password-less option"""
            sessions = self.ssh_manager.list_sessions()
            
            if not sessions:
                print("No connections configured.")
                return
            
            print("\n" + "="*70)
            print("🔍 TEST CONNECTIONS")
            print("="*70)
            
            print("\nSelect connection:")
            print("1. Test all connections")
            for i, name in enumerate(sessions, 2):
                print(f"{i}. Test {name}")
            
            choice = input(f"\nSelect option (1-{len(sessions)+1}): ").strip()
            
            if choice == "1":
                print("\nTesting all connections...")
                for session_name in sessions:
                    print(f"\n--- Testing {session_name} ---")
                    self.ssh_manager.test_connection(session_name)
                    
                    # Ask if they want to setup password-less
                    setup = input(f"\nSetup password-less login for {session_name}? (y/N): ").strip().lower()
                    if setup == 'y':
                        self.ssh_manager.test_and_setup_passwordless(session_name, ask_for_password=True)
            
            elif choice.isdigit() and 2 <= int(choice) <= len(sessions) + 1:
                session_name = sessions[int(choice) - 2]
                
                # Test first
                print(f"\n--- Testing {session_name} ---")
                result = self.ssh_manager.test_connection(session_name)
                
                # Check if already password-less
                if isinstance(result, dict) and result.get('success'):
                    print(f"\n✓ Connection is already password-less!")
                    return
                
                # Offer to setup password-less
                print(f"\n⚠️  Connection may require password authentication")
                setup = input("Would you like to setup password-less login? (y/N): ").strip().lower()
                
                if setup == 'y':
                    self.ssh_manager.test_and_setup_passwordless(session_name, ask_for_password=True)
            
            else:
                print("Invalid selection.")
    
    def export_configuration(self):
        """Export configuration to various formats"""
        sessions = self.ssh_manager.sessions
        
        if not sessions:
            print("No configurations to export.")
            return
        
        print("\n" + "─"*70)
        print("EXPORT CONFIGURATION")
        print("─"*70)
        
        print("\nExport options:")
        print("1. SSH config format")
        print("2. JSON format")
        print("3. YAML format")
        print("4. Ansible inventory")
        print("5. CSV format")
        print("6. Back to main menu")
        
        choice = input("\nSelect format (1-6): ").strip()
        
        if choice == "1":
            self._export_ssh_config()
        elif choice == "2":
            self._export_json()
        elif choice == "3":
            self._export_yaml()
        elif choice == "4":
            self._export_ansible()
        elif choice == "5":
            self._export_csv()
        elif choice == "6":
            return
        else:
            print("Invalid choice.")
    
    def _export_ssh_config(self):
        """Export as SSH config"""
        filename = input("Filename [ssh2ls_export_config]: ").strip() or "ssh2ls_export_config"
        
        config_lines = []
        for session_name in self.ssh_manager.list_sessions():
            config_lines.append(self.ssh_manager.generate_ssh_config(session_name))
            config_lines.append("")  # Empty line between configs
        
        with open(filename, 'w') as f:
            f.write("\n".join(config_lines))
        
        print(f"✓ SSH config exported to {filename}")
    
    def _export_json(self):
        """Export as JSON"""
        filename = input("Filename [ssh2ls_export.json]: ").strip() or "ssh2ls_export.json"
        
        with open(filename, 'w') as f:
            json.dump(self.ssh_manager.sessions, f, indent=2, default=str)
        
        print(f"✓ JSON exported to {filename}")
    
    def _export_yaml(self):
        """Export as YAML"""
        try:
            import yaml
        except ImportError:
            print("✗ PyYAML not installed. Install with: pip install pyyaml")
            return
        
        filename = input("Filename [ssh2ls_export.yaml]: ").strip() or "ssh2ls_export.yaml"
        
        with open(filename, 'w') as f:
            yaml.dump(self.ssh_manager.sessions, f, default_flow_style=False)
        
        print(f"✓ YAML exported to {filename}")
    
    def _export_ansible(self):
        """Export as Ansible inventory"""
        filename = input("Filename [ssh2ls_inventory.ini]: ").strip() or "ssh2ls_inventory.ini"
        
        groups = {}
        
        # Group hosts by tags and groups
        for session_name, session in self.ssh_manager.sessions.items():
            # Add to all groups specified in the session
            if 'groups' in session:
                for group in session['groups']:
                    if group not in groups:
                        groups[group] = []
                    groups[group].append(session_name)
            
            # Add to tag groups
            if 'tags' in session:
                for tag in session['tags']:
                    if tag not in groups:
                        groups[tag] = []
                    groups[tag].append(session_name)
        
        # Generate inventory
        lines = []
        lines.append("# Ansible inventory generated by ssh2ls")
        lines.append(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Ungrouped hosts
        ungrouped = []
        for session_name in self.ssh_manager.list_sessions():
            if not any(session_name in groups[g] for g in groups):
                ungrouped.append(session_name)
        
        if ungrouped:
            lines.append("[ungrouped]")
            for session_name in ungrouped:
                session = self.ssh_manager.sessions[session_name]
                target = session["target"]
                lines.append(f"{session_name} ansible_host={target['ip']} ansible_user={target['user']}")
            lines.append("")
        
        # Grouped hosts
        for group, hosts in groups.items():
            lines.append(f"[{group}]")
            for session_name in hosts:
                session = self.ssh_manager.sessions[session_name]
                target = session["target"]
                lines.append(f"{session_name} ansible_host={target['ip']} ansible_user={target['user']}")
            
            # Add group variables if any
            lines.append("")
        
        with open(filename, 'w') as f:
            f.write("\n".join(lines))
        
        print(f"✓ Ansible inventory exported to {filename}")
    
    def _export_csv(self):
        """Export as CSV"""
        filename = input("Filename [ssh2ls_export.csv]: ").strip() or "ssh2ls_export.csv"
        
        fieldnames = ['name', 'jumphost_ip', 'jumphost_user', 'target_ip', 'target_user', 
                     'private_key', 'created', 'last_used', 'usage_count']
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for session_name, session in self.ssh_manager.sessions.items():
                jh = session["jumphost"]
                target = session["target"]
                
                row = {
                    'name': session_name,
                    'jumphost_ip': jh['ip'],
                    'jumphost_user': jh['user'],
                    'target_ip': target['ip'],
                    'target_user': target['user'],
                    'private_key': jh['private_key'],
                    'created': session.get('created', ''),
                    'last_used': session.get('last_used', ''),
                    'usage_count': session.get('usage_count', 0)
                }
                writer.writerow(row)
        
        print(f"✓ CSV exported to {filename}")

    def run_from_cli(self, args):
        """Run from command line arguments"""
        if args.command == 'wizard':
            self.interactive_wizard()
    
        elif args.command == 'autostart':
            if args.autostart_command == 'setup':
                self.setup_autostart_persistence()
            elif args.autostart_command == 'status':
                self.check_persistence_status()
            elif args.autostart_command == 'test':
                self._test_autostart()
    
        elif args.command == 'direct' and args.direct_command == 'setup':
            # Setup direct connection
            self.ssh_manager.create_direct_connection(
                name=args.name,
                host_ip=args.host,
                host_user=args.user,
                port=args.port,
                private_key_path=args.key,
                floating_ip=args.floating_ip,
                use_floating_ip=args.use_floating
            )
    
        elif args.command == 'setup':
            if not all([args.jumphost, args.target]):
                print("Error: --jumphost and --target are required")
                return
            
            # Check if floating IP is provided
            if hasattr(args, 'floating_ip') and args.floating_ip:
                # Use floating IP setup
                self.ssh_manager.create_jumphost_config_with_floating_ip(
                    name=args.name,
                    floating_ip=args.floating_ip,
                    fixed_ip=args.fixed_ip or args.jumphost,  # Use jumphost as fixed IP if not specified
                    jumphost_user=args.jumphost_user or "ubuntu",
                    target_ip=args.target,
                    target_user=args.target_user or (args.jumphost_user or "ubuntu"),
                    private_key_path=args.key or f"~/.ssh/id_ed25519_{args.name}",
                    use_floating_ip=True,  # Default to using floating IP
                    description=f"Connection with floating IP {args.floating_ip}"
                )
            else:
                # Regular setup
                self.ssh_manager.create_jumphost_config(
                    name=args.name,
                    jumphost_ip=args.jumphost,
                    jumphost_user=args.jumphost_user or "ubuntu",
                    private_key_path=args.key or f"~/.ssh/id_ed25519_{args.name}",
                    target_ip=args.target,
                    target_user=args.target_user or (args.jumphost_user or "ubuntu")
                )
        
        elif args.command == 'setup-with-floating':
            # Dedicated floating IP setup command
            if not args.floating_ip:
                print("Error: --floating-ip is required")
                return
            
            self.ssh_manager.create_jumphost_config_with_floating_ip(
                name=args.name,
                floating_ip=args.floating_ip,
                fixed_ip=args.fixed_ip,
                jumphost_user=args.user or "ubuntu",
                target_ip=args.target if hasattr(args, 'target') else None,
                target_user=args.target_user if hasattr(args, 'target_user') else (args.user or "ubuntu"),
                private_key_path=args.key or f"~/.ssh/id_ed25519_{args.name}",
                use_floating_ip=getattr(args, 'use_floating', True),
                description=getattr(args, 'description', f"Connection with floating IP {args.floating_ip}")
            )
        
        elif args.command == 'connect':
            if args.name not in self.ssh_manager.sessions:
                print(f"Error: Connection '{args.name}' not found")
                return
            
            self.ssh_manager.interactive_shell(args.name, args.hop)
        
        elif args.command == 'transfer':
            if args.name not in self.ssh_manager.sessions:
                print(f"Error: Connection '{args.name}' not found")
                return
            
            self.ssh_manager.transfer_files(
                session_name=args.name,
                local_path=args.source,
                remote_path=args.dest,
                direction=args.direction
            )
        
        elif args.command == 'tunnel':
            if args.tunnel_command == 'create':
                if args.name not in self.ssh_manager.sessions:
                    print(f"Error: Connection '{args.name}' not found")
                    return
                
                self.ssh_manager.create_tunnel(
                    session_name=args.name,
                    local_port=args.local_port,
                    remote_host=args.remote_host,
                    remote_port=args.remote_port,
                    tunnel_name=args.tunnel_name
                )
            
            elif args.tunnel_command == 'start':
                if args.tunnel_name not in self.ssh_manager.tunnels:
                    print(f"Error: Tunnel '{args.tunnel_name}' not found")
                    return
                
                self.ssh_manager.start_tunnel(args.tunnel_name, args.background)
            
            elif args.tunnel_command == 'stop':
                if args.tunnel_name not in self.ssh_manager.tunnels:
                    print(f"Error: Tunnel '{args.tunnel_name}' not found")
                    return
                
                self.ssh_manager.stop_tunnel(args.tunnel_name)
        
        elif args.command == 'setup-env':
            if args.name not in self.ssh_manager.sessions:
                print(f"Error: Connection '{args.name}' not found")
                return
            
            templates = {
                'basic': [
                    "sudo apt update",
                    "sudo apt upgrade -y",
                    "sudo apt install -y git wget curl python3 python3-pip"
                ],
                'bioinfo': [
                    "sudo apt update && sudo apt upgrade -y",
                    "sudo apt install -y git wget curl python3 python3-pip",
                    "sudo apt install -y apptainer",
                    "mkdir -p ~/data"
                ],
                'docker': [
                    "sudo apt update",
                    "sudo apt install -y docker.io",
                    "sudo systemctl start docker",
                    "sudo systemctl enable docker"
                ],
                'python': [
                    "sudo apt update",
                    "sudo apt install -y python3-pip python3-venv",
                    "python3 -m pip install --upgrade pip"
                ]
            }
            
            self.ssh_manager.batch_setup_environment(args.name, templates[args.template])
        
        elif args.command == 'quick':
            if args.name not in self.ssh_manager.sessions:
                print(f"Error: Connection '{args.name}' not found")
                return
            
            commands = self.ssh_manager.get_quick_commands(args.name)
            for desc, cmd in commands.items():
                print(f"{desc}: {cmd}")
        
        elif args.command == 'test':
            if args.name not in self.ssh_manager.sessions:
                print(f"Error: Connection '{args.name}' not found")
                return
            
            # Check if session has floating IP
            session = self.ssh_manager.sessions[args.name]
            if 'floating_ip_config' in session:
                # Use floating IP test
                self.ssh_manager.test_connection_with_floating_ip(args.name)
            else:
                # Use regular test
                self.ssh_manager.test_connection(args.name)
        
        elif args.command == 'list':
            sessions = self.ssh_manager.list_sessions()
            if sessions:
                print("Configured connections:")
                for name in sessions:
                    session = self.ssh_manager.sessions[name]
                    jh = session["jumphost"]
                    target = session["target"]
                    
                    # Show floating IP info if available
                    floating_info = ""
                    if 'floating_ip' in jh:
                        floating_info = f" [Floating: {jh['floating_ip']}]"
                    
                    print(f"  {name}: {jh['user']}@{jh.get('effective_ip', jh.get('ip', 'unknown'))} → {target['user']}@{target['ip']}{floating_info}")
            else:
                print("No connections configured.")
        
        elif args.command == 'display':
            if args.denbi:
                self.instructions.display_deNBI_specific()
            elif args.cheatsheet:
                self.instructions.display_cheatsheet()
            else:
                self.instructions.display_full_instructions()
        
        elif args.command == 'export':
            if args.format == 'ssh':
                self._export_ssh_config()
            elif args.format == 'json':
                self._export_json()
            elif args.format == 'yaml':
                self._export_yaml()
            elif args.format == 'ansible':
                self._export_ansible()
            elif args.format == 'csv':
                self._export_csv()
        
        elif args.command == 'key':
            if args.key_command == 'generate':
                self.generate_key_interactive()
            elif args.key_command == 'list':
                self.key_manager.list_keys_in_agent()
            elif args.key_command == 'add':
                self.add_key_to_agent_interactive()
            elif args.key_command == 'remove':
                self.remove_key_from_agent_interactive()
        
        elif args.command == 'floating':
            if args.floating_command == 'list':
                self.list_floating_ips()
            elif args.floating_command == 'test':
                self.test_floating_ip()
            elif args.floating_command == 'register':
                self.ssh_manager.floating_ip_manager.register_floating_ip(
                    name=args.name,
                    floating_ip=args.floating_ip,
                    fixed_ip=args.fixed_ip,
                    description=args.description or ""
                )
            elif args.floating_command == 'update':
                self.update_floating_ip_mapping()
            elif args.floating_command == 'delete':
                self.delete_floating_ip()
    def check_sshpass_installed(self):
        """Check if sshpass is installed (needed for password-less setup)"""
        try:
            result = subprocess.run(['which', 'sshpass'], 
                                capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def setup_passwordless_menu(self):
        """Menu for setting up password-less authentication"""
        # Check dependencies
        if not self.check_sshpass_installed():
            print("\nsshpass not found. It's needed for password-less setup.")
            print("Install it with:")
            print("  macOS: brew install hudochenkov/sshpass/sshpass")
            print("  Ubuntu/Debian: sudo apt-get install sshpass")
            print("  CentOS/RHEL: sudo yum install sshpass")

            install = input("\nContinue without sshpass? (some features limited) (y/N): ").strip().lower()
            if install != 'y':
                return
        sessions = self.ssh_manager.list_sessions()
        
        if not sessions:
            print("No connections configured.")
            return
        
        print("\n" + "="*70)
        print("🔑 SETUP PASSWORD-LESS AUTHENTICATION")
        print("="*70)
        
        print("\nSelect connection to setup password-less login:")
        for i, name in enumerate(sessions, 1):
            session = self.ssh_manager.sessions[name]
            connection_type = session.get("connection_type", "jumphost")
            
            if connection_type == "direct":
                host = session["host"]
                info = f"{host['user']}@{host.get('effective_ip', host['ip'])}"
            else:
                jh = session["jumphost"]
                target = session["target"]
                info = f"{jh['user']}@{jh.get('effective_ip', jh['ip'])} → {target['user']}@{target['ip']}"
            
            print(f"{i}. {name} ({connection_type}): {info}")
        
        choice = input(f"\nSelect connection (1-{len(sessions)}): ").strip()
        if not (choice.isdigit() and 1 <= int(choice) <= len(sessions)):
            print("Invalid selection.")
            return
        
        session_name = sessions[int(choice) - 1]
        
        print(f"\nSetting up password-less login for '{session_name}'...")
        print("This will:")
        print("1. Test the connection")
        print("2. Ask for password if needed")
        print("3. Copy your public key to the server")
        print("4. Verify password-less login works")
        
        confirm = input("\nContinue? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return
        
        # Run the password-less setup
        result = self.ssh_manager.test_and_setup_passwordless(session_name, ask_for_password=True)
        
        # Show results
        print("\n" + "="*70)
        print("📊 SETUP RESULTS")
        print("="*70)
        
        if result.get('setup_complete') or result.get('already_passwordless'):
            print("✅ SUCCESS: Password-less login is now configured!")
            
            if result.get('already_passwordless'):
                print("   (It was already working)")
            else:
                print("   You can now connect without passwords:")
                
                if result['type'] == 'direct':
                    print(f"   ssh {session_name}")
                else:
                    print(f"   ssh {session_name}_jumphost    # Connect to jumphost")
                    print(f"   ssh {session_name}             # Connect to target via jumphost")
        else:
            print("❌ SETUP FAILED")
            
            if result.get('error'):
                print(f"   Error: {result['error']}")
            
            print("\n💡 Troubleshooting tips:")
            print("1. Check username and password")
            print("2. Ensure SSH service is running on the server")
            print("3. Check firewall rules")
            print("4. Try manual setup: ssh-copy-id user@host")
def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="SSH2LS - Ultimate SSH Connection Manager (Direct & Multi-Hop)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          ssh2ls wizard                     # Interactive wizard
          ssh2ls direct setup               # Setup direct connection
          ssh2ls setup denbi                # Setup deNBI-like multi-hop
          ssh2ls connect server1            # Connect to direct host
          ssh2ls connect denbi              # Connect via jumphost
        
        Connection Types:
          1. Direct: ssh user@host
          2. Jumphost: local → jumphost → target
          3. Floating IP: Direct or via jumphost with floating IP
        """)
    )

    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Wizard command
    subparsers.add_parser('wizard', help='Interactive wizard')
    
    
    # Direct connection command
    direct_parser = subparsers.add_parser('direct', help='Direct connection management')
    direct_subparsers = direct_parser.add_subparsers(dest='direct_command', help='Direct command')
    
    direct_setup = direct_subparsers.add_parser('setup', help='Setup direct connection')
    direct_setup.add_argument('name', help='Connection name')
    direct_setup.add_argument('--host', required=True, help='Host IP/hostname')
    direct_setup.add_argument('--user', default='ubuntu', help='Username')
    direct_setup.add_argument('--port', type=int, default=22, help='Port')
    direct_setup.add_argument('--key', help='Private key path')
    direct_setup.add_argument('--floating-ip', help='Floating IP address')
    direct_setup.add_argument('--use-floating', action='store_true', help='Use floating IP')
    
    # Setup command (regular)
    setup_parser = subparsers.add_parser('setup', help='Setup multi-hop connection')
    setup_parser.add_argument('name', help='Connection name')
    setup_parser.add_argument('--jumphost', required=True, help='Jumphost IP (or floating IP)')
    setup_parser.add_argument('--jumphost-user', default='ubuntu', help='Jumphost username')
    setup_parser.add_argument('--target', required=True, help='Target IP')
    setup_parser.add_argument('--target-user', help='Target username')
    setup_parser.add_argument('--key', help='Private key path')
    setup_parser.add_argument('--fixed-ip', help='Fixed IP address (if jumphost is floating IP)')
    setup_parser.add_argument('--floating-ip', help='Floating IP address (alternative to --jumphost)')
    
    # Setup with floating IP (dedicated command)
    setup_floating_parser = subparsers.add_parser('setup-with-floating', help='Setup with floating IP')
    setup_floating_parser.add_argument('name', help='Connection name')
    setup_floating_parser.add_argument('--floating-ip', required=True, help='Floating IP address')
    setup_floating_parser.add_argument('--fixed-ip', help='Fixed IP address')
    setup_floating_parser.add_argument('--user', default='ubuntu', help='Username')
    setup_floating_parser.add_argument('--key', help='Private key path')
    setup_floating_parser.add_argument('--use-floating', action='store_true', help='Use floating IP')
    setup_floating_parser.add_argument('--target', help='Target IP')
    setup_floating_parser.add_argument('--target-user', help='Target username')
    setup_floating_parser.add_argument('--description', help='Description')
    
    # Connect command
    connect_parser = subparsers.add_parser('connect', help='Connect to host')
    connect_parser.add_argument('name', help='Connection name')
    connect_parser.add_argument('--hop', choices=['jumphost', 'target'], 
                              default='target', help='Which hop to connect to')
    
    # Floating IP management
    floating_parser = subparsers.add_parser('floating', help='Floating IP management')
    floating_subparsers = floating_parser.add_subparsers(dest='floating_command', required=True)
    
    floating_list = floating_subparsers.add_parser('list', help='List floating IPs')
    
    floating_test = floating_subparsers.add_parser('test', help='Test floating IP')
    floating_test.add_argument('name', help='Floating IP name')
    
    floating_register = floating_subparsers.add_parser('register', help='Register floating IP')
    floating_register.add_argument('name', help='Floating IP name')
    floating_register.add_argument('--floating-ip', required=True, help='Floating IP address')
    floating_register.add_argument('--fixed-ip', help='Fixed IP address')
    floating_register.add_argument('--description', help='Description')
    
    floating_update = floating_subparsers.add_parser('update', help='Update floating IP mapping')
    floating_update.add_argument('name', help='Floating IP name')
    
    floating_delete = floating_subparsers.add_parser('delete', help='Delete floating IP')
    floating_delete.add_argument('name', help='Floating IP name')
    
    # Transfer command
    transfer_parser = subparsers.add_parser('transfer', help='Transfer files')
    transfer_parser.add_argument('direction', choices=['upload', 'download'])
    transfer_parser.add_argument('name', help='Connection name')
    transfer_parser.add_argument('source', help='Source path')
    transfer_parser.add_argument('dest', help='Destination path')
    
    # Tunnel command
    tunnel_parser = subparsers.add_parser('tunnel', help='Manage tunnels')
    tunnel_subparsers = tunnel_parser.add_subparsers(dest='tunnel_command', required=True)
    
    tunnel_create = tunnel_subparsers.add_parser('create', help='Create tunnel')
    tunnel_create.add_argument('name', help='Connection name')
    tunnel_create.add_argument('local_port', type=int, help='Local port')
    tunnel_create.add_argument('remote_host', help='Remote host')
    tunnel_create.add_argument('remote_port', type=int, help='Remote port')
    tunnel_create.add_argument('--tunnel-name', help='Tunnel name')
    
    tunnel_start = tunnel_subparsers.add_parser('start', help='Start tunnel')
    tunnel_start.add_argument('tunnel_name', help='Tunnel name')
    tunnel_start.add_argument('--background', action='store_true', help='Run in background')
    
    tunnel_stop = tunnel_subparsers.add_parser('stop', help='Stop tunnel')
    tunnel_stop.add_argument('tunnel_name', help='Tunnel name')
    
    # Setup environment command
    env_parser = subparsers.add_parser('setup-env', help='Setup remote environment')
    env_parser.add_argument('name', help='Connection name')
    env_parser.add_argument('--template', choices=['basic', 'bioinfo', 'docker', 'python'],
                          default='basic', help='Environment template')
    
    # Quick commands
    quick_parser = subparsers.add_parser('quick', help='Show quick commands')
    quick_parser.add_argument('name', help='Connection name')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test connection')
    test_parser.add_argument('name', help='Connection name')
    
    # List command
    subparsers.add_parser('list', help='List all connections')
    
    # Display command
    display_parser = subparsers.add_parser('display', help='Display instructions')
    display_parser.add_argument('--denbi', action='store_true', 
                              help='Show deNBI-specific instructions')
    display_parser.add_argument('--cheatsheet', action='store_true',
                              help='Show cheatsheet')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export configuration')
    export_parser.add_argument('format', choices=['ssh', 'json', 'yaml', 'ansible', 'csv'],
                             help='Export format')
    
    # Key management command
    key_parser = subparsers.add_parser('key', help='SSH key management')
    key_subparsers = key_parser.add_subparsers(dest='key_command', required=True)
    key_subparsers.add_parser('generate', help='Generate SSH key')
    key_subparsers.add_parser('list', help='List keys in agent')
    key_subparsers.add_parser('add', help='Add key to agent')
    key_subparsers.add_parser('remove', help='Remove key from agent')
    
    
    # passwordless command
    passwordless_parser = subparsers.add_parser('passwordless', 
                                                help='Setup password-less authentication')
    passwordless_subparsers = passwordless_parser.add_subparsers(dest='passwordless_command', 
                                                                help='Passwordless command')
    passwordless_setup = passwordless_subparsers.add_parser('setup', 
                                                           help='Setup password-less login')
    passwordless_setup.add_argument('name', help='Connection name')
    passwordless_setup.add_argument('--password', help='Password (unsafe, better to prompt)')

    # Autostart command
    autostart_parser = subparsers.add_parser('autostart', help='Auto-load keys on startup')
    autostart_subparsers = autostart_parser.add_subparsers(dest='autostart_command', required=True)

    autostart_setup = autostart_subparsers.add_parser('setup', help='Setup auto-load keys')
    autostart_status = autostart_subparsers.add_parser('status', help='Check auto-start status')
    autostart_test = autostart_subparsers.add_parser('test', help='Test auto-start setup')

    # Parse arguments
    args = parser.parse_args()
    
    # If no command provided, default to wizard
    if not args.command:
        args.command = 'wizard'
    
    elif args.command == 'passwordless' and args.passwordless_command == 'setup':
        # Setup password-less authentication
        print(f"\n🔑 Setting up password-less login for '{args.name}'...")
        
        if args.password:
            print("⚠️  WARNING: Passing password via command line is unsafe!")
            print("   It may be visible in process lists and shell history.")
            confirm = input("Continue anyway? (y/N): ").strip().lower()
            if confirm != 'y':
                print("Cancelled.")
                return
        
        result = self.ssh_manager.test_and_setup_passwordless(
            args.name,
            ask_for_password=(not args.password)
        )
        
        if result.get('setup_complete') or result.get('already_passwordless'):
            print("✅ Password-less setup successful!")
        else:
            print("❌ Password-less setup failed")
    
    if not args.command:
        # No command provided, show help
        parser.print_help()
        print("\n" + "="*60)
        print("Starting interactive mode...")
        print("="*60)
        args.command = 'wizard'
    
    # Create and run application
    app = SSH2LS()
    
    try:
        app.run_from_cli(args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Check for required dependencies
        if not HAS_PARAMIKO:
            print("Warning: paramiko not installed. Some features will be limited.")
            print("Install with: pip install paramiko")
        
        if not HAS_CRYPTO:
            print("Warning: cryptography not installed. Some features will be limited.")
            print("Install with: pip install cryptography")
        
        # Ensure the script is executable
        if sys.platform != "win32":
            script_path = Path(sys.argv[0])
            if script_path.exists():
                # Make executable if not already
                if not (script_path.stat().st_mode & stat.S_IEXEC):
                    script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
        
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)