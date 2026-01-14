#!/usr/bin/env python3
"""
SSH2LS - Ultimate SSH Multi-Hop Connection Manager
Handles complex jump host setups, key management, agent forwarding, and secure file transfers.
usage:
# 1. Interactive Wizard Mode:
# Start the interactive wizard
python ssh2ls.py wizard

# Or just (defaults to wizard)
python ssh2ls.py
# 2. Quick deNBI Setup:
# Run the automated deNBI setup
python denbi_setup.py

3. Command Line Usage:
# Setup a connection (like your deNBI setup)
python ssh2ls.py setup denbi \
  --jumphost 193.196.20.189 \
  --jumphost-user ubuntu \
  --target 192.168.54.219 \
  --key ~/.ssh/denbi

# Connect to target via jumphost
python ssh2ls.py connect denbi --hop target

# Upload files
python ssh2ls.py transfer upload denbi ./local_data /home/ubuntu/data/

# Setup remote environment (bioinformatics)
python ssh2ls.py setup-env denbi --template bioinfo

# Create SSH tunnel for web access
python ssh2ls.py tunnel create denbi 8080 localhost 80

# Show quick commands
python ssh2ls.py quick denbi

# Test connection
python ssh2ls.py test denbi

# List all connections
python ssh2ls.py list

4. Quick Aliases Created:
# Add to your shell
source ~/denbi_aliases.sh

# Then use:
denbi-jump      # Connect to jumphost
denbi-vm        # Connect to target VM
denbi-upload    # Upload files
denbi-download  # Download files
denbi-test      # Test connection
denbi-copy-data /path/to/data  # Copy data to VM
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
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
import shutil
import paramiko
from cryptography.fernet import Fernet
import base64
import tempfile
import threading
import queue
import select

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
        if not key_name:
            key_name = f"id_{key_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        private_key_path = self.ssh_dir / key_name
        public_key_path = private_key_path.with_suffix('.pub')
        
        if private_key_path.exists():
            raise FileExistsError(f"Key {private_key_path} already exists")
        
        # Generate key using paramiko
        if key_type == "rsa":
            key = paramiko.RSAKey.generate(bits=key_size)
        elif key_type == "ed25519":
            key = paramiko.Ed25519Key.generate()
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
            comment = f"{getpass.getuser()}@{socket.gethostname()}-{datetime.now().strftime('%Y%m%d')}"
        
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
    
    def add_key_to_agent(self, key_path: Path, passphrase: str = None) -> bool:
        """Add SSH key to SSH agent"""
        if not self.agent_socket:
            print("⚠ SSH agent not running. Start with: eval $(ssh-agent)")
            return False
        
        try:
            # Try using ssh-add command
            cmd = ['ssh-add', str(key_path)]
            if passphrase:
                # For passphrase-protected keys, we need to handle it interactively
                result = subprocess.run(cmd, capture_output=True, text=True, input=passphrase)
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
            return []
        
        try:
            result = subprocess.run(['ssh-add', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
        except Exception:
            pass
        return []
    
    def remove_key_from_agent(self, key_path: Path) -> bool:
        """Remove specific key from SSH agent"""
        if not self.agent_socket:
            return False
        
        try:
            result = subprocess.run(['ssh-add', '-d', str(key_path)], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def check_key_permissions(self, key_path: Path) -> bool:
        """Check if SSH key has correct permissions (600)"""
        try:
            mode = key_path.stat().st_mode
            return stat.S_IMODE(mode) == 0o600
        except Exception:
            return False
    
    def fix_key_permissions(self, key_path: Path):
        """Fix SSH key permissions to 600"""
        key_path.chmod(0o600)
        print(f"✓ Fixed permissions for: {key_path}")
    
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
        try:
            for key_class in [paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey, paramiko.DSSKey]:
                try:
                    key = key_class(filename=str(private_key_path))
                    return f"{key.get_name()} {key.get_base64()} {getpass.getuser()}@{socket.gethostname()}"
                except paramiko.SSHException:
                    continue
        except Exception as e:
            print(f"✗ Error extracting public key: {e}")
        
        return None

class MultiHopSSHManager:
    """Manages complex multi-hop SSH connections with agent forwarding"""
    
    def __init__(self, config_dir: str = "~/.ssh/ssh2ls"):
        self.config_dir = Path(config_dir).expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_file = self.config_dir / "sessions.json"
        self.tunnels_file = self.config_dir / "tunnels.json"
        self.sessions = self.load_sessions()
        self.tunnels = self.load_tunnels()
        self.key_manager = SSHKeyManager()
    
    def load_sessions(self) -> Dict:
        """Load saved SSH sessions"""
        if self.sessions_file.exists():
            with open(self.sessions_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_sessions(self):
        """Save SSH sessions to file"""
        with open(self.sessions_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
    def load_tunnels(self) -> Dict:
        """Load saved tunnel configurations"""
        if self.tunnels_file.exists():
            with open(self.tunnels_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_tunnels(self):
        """Save tunnel configurations"""
        with open(self.tunnels_file, 'w') as f:
            json.dump(self.tunnels, f, indent=2)
    
    def create_jumphost_config(self, name: str, jumphost_ip: str, jumphost_user: str, 
                              private_key_path: str, target_ip: str, target_user: str = None,
                              description: str = "") -> Dict:
        """Create a jumphost configuration like in your notes"""
        
        if not target_user:
            target_user = jumphost_user
        
        config = {
            "name": name,
            "jumphost": {
                "ip": jumphost_ip,
                "user": jumphost_user,
                "private_key": private_key_path,
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
        print(f"  Key:      {private_key_path}")
        
        return config
    
    def generate_ssh_config(self, session_name: str) -> str:
        """Generate SSH config for a session"""
        if session_name not in self.sessions:
            raise KeyError(f"Session '{session_name}' not found")
        
        session = self.sessions[session_name]
        jh = session["jumphost"]
        target = session["target"]
        
        config = f"""
# SSH Configuration for {session_name}
# Generated by ssh2ls on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Description: {session.get('description', '')}

Host {session_name}_jumphost
    HostName {jh['ip']}
    User {jh['user']}
    IdentityFile {jh['private_key']}
    ForwardAgent {"yes" if session.get('agent_forwarding', True) else "no"}
    ServerAliveInterval 30
    ServerAliveCountMax 3
    # Add any custom options here

Host {session_name}
    HostName {target['ip']}
    User {target['user']}
    ProxyJump {session_name}_jumphost
    # Connection through jumphost
    
# Direct access to target (requires being on the same network)
Host {session_name}_direct
    HostName {target['ip']}
    User {target['user']}
    # Only use this if you have direct network access

# Quick commands
# ssh {session_name}_jumphost        # Connect to jumphost
# ssh {session_name}                 # Connect to target via jumphost
"""
        return config.strip()
    
    def test_connection(self, session_name: str, max_hops: int = 2) -> Dict[str, bool]:
        """Test connection through all hops"""
        if session_name not in self.sessions:
            raise KeyError(f"Session '{session_name}' not found")
        
        session = self.sessions[session_name]
        results = {}
        
        print(f"\n🔍 Testing connection for '{session_name}'...")
        
        # Test jumphost connection
        jh = session["jumphost"]
        print(f"\n1. Testing jumphost: {jh['user']}@{jh['ip']}")
        
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Load private key
            key = self._load_private_key(jh['private_key'])
            
            client.connect(
                hostname=jh['ip'],
                username=jh['user'],
                pkey=key,
                timeout=10
            )
            
            # Test basic command
            stdin, stdout, stderr = client.exec_command('echo "Jumphost connection successful"')
            output = stdout.read().decode().strip()
            
            if "successful" in output:
                print(f"   ✓ Jumphost connection successful")
                results['jumphost'] = True
                
                # Test target connection via jumphost
                if max_hops > 1:
                    print(f"\n2. Testing target via jumphost: {session['target']['user']}@{session['target']['ip']}")
                    
                    # Use agent forwarding if configured
                    if session.get('agent_forwarding', True):
                        print("   Using agent forwarding...")
                    
                    # Try to execute command on target via jumphost
                    # This is simplified - in reality you'd need to tunnel through
                    cmd = f"ssh -o ConnectTimeout=5 {session['target']['user']}@{session['target']['ip']} 'echo Target-connection-successful'"
                    stdin, stdout, stderr = client.exec_command(cmd)
                    
                    stdout_text = stdout.read().decode().strip()
                    stderr_text = stderr.read().decode().strip()
                    
                    if "Target-connection-successful" in stdout_text:
                        print(f"   ✓ Target connection via jumphost successful")
                        results['target_via_jumphost'] = True
                    else:
                        print(f"   ✗ Target connection failed: {stderr_text}")
                        results['target_via_jumphost'] = False
            else:
                print(f"   ✗ Jumphost connection failed")
                results['jumphost'] = False
            
            client.close()
            
        except Exception as e:
            print(f"   ✗ Connection error: {e}")
            results['jumphost'] = False
        
        # Update usage stats
        session['last_used'] = datetime.now().isoformat()
        session['usage_count'] = session.get('usage_count', 0) + 1
        self.save_sessions()
        
        return results
    
    def _load_private_key(self, key_path: str) -> Optional[paramiko.PKey]:
        """Load private key from file"""
        try:
            key_path = Path(key_path).expanduser()
            
            # Try different key types
            for key_class in [paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey, paramiko.DSSKey]:
                try:
                    return key_class.from_private_key_file(str(key_path))
                except paramiko.SSHException:
                    continue
            
            print(f"✗ Could not load private key: {key_path}")
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
            print("⚠ SSH agent is not running. Starting SSH agent...")
            subprocess.run(['ssh-agent'], shell=True)
            print("⚠ Please run: eval $(ssh-agent)")
            return False
        
        # Add key to agent if needed
        key_path = session['jumphost']['private_key']
        if self.key_manager.add_key_to_agent(Path(key_path).expanduser()):
            print("✓ Key added to SSH agent")
        else:
            print("⚠ Could not add key to agent")
        
        # Test agent forwarding
        print("\nTesting agent forwarding...")
        cmd = ['ssh', '-A', 
               f"{session['jumphost']['user']}@{session['jumphost']['ip']}",
               '-i', key_path,
               'ssh-add -l && echo "Agent-forwarding-successful"']
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if "Agent-forwarding-successful" in result.stdout:
                print("✓ SSH agent forwarding is working correctly")
                print(f"  Keys available on jumphost: {result.stdout.strip()}")
                
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
        print(f"  Command: {tunnel_config['command']}")
        
        return tunnel_config
    
    def _generate_tunnel_command(self, session: Dict, local_port: int, 
                               remote_host: str, remote_port: int) -> str:
        """Generate SSH tunnel command"""
        jh = session["jumphost"]
        
        cmd = [
            "ssh", "-N", "-L",
            f"{local_port}:{remote_host}:{remote_port}",
            "-i", jh['private_key'],
            f"{jh['user']}@{jh['ip']}"
        ]
        
        if session.get('agent_forwarding', True):
            cmd.insert(2, "-A")
        
        return " ".join(cmd)
    
    def start_tunnel(self, tunnel_name: str, background: bool = True) -> bool:
        """Start SSH tunnel"""
        if tunnel_name not in self.tunnels:
            raise KeyError(f"Tunnel '{tunnel_name}' not found")
        
        tunnel = self.tunnels[tunnel_name]
        
        print(f"\nStarting tunnel '{tunnel_name}'...")
        print(f"Command: {tunnel['command']}")
        
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
        
        print(f"\nTransferring files for '{session_name}'...")
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
            "-i", jh['private_key']
        ]
        
        if session.get('agent_forwarding', True):
            cmd.extend(["-o", "ForwardAgent=yes"])
        
        cmd.extend([src, dst])
        
        print(f"\nCommand: {' '.join(cmd)}")
        
        try:
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
        hop: 'jumphost' or 'target'
        """
        if session_name not in self.sessions:
            raise KeyError(f"Session '{session_name}' not found")
        
        session = self.sessions[session_name]
        
        if hop == "jumphost":
            host = session["jumphost"]
            ssh_cmd = [
                "ssh", "-i", host["private_key"],
                f"{host['user']}@{host['ip']}"
            ]
            
            if session.get('agent_forwarding', True):
                ssh_cmd.insert(1, "-A")
                
        else:  # target via jumphost
            host = session["target"]
            jh = session["jumphost"]
            
            ssh_cmd = [
                "ssh", "-J", f"{jh['user']}@{jh['ip']}",
                "-i", jh["private_key"],
                f"{host['user']}@{host['ip']}"
            ]
            
            if session.get('agent_forwarding', True):
                ssh_cmd.insert(1, "-A")
        
        print(f"\nStarting interactive SSH session to {hop}...")
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
        Useful for setting up environments (like your nf-core setup)
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
        script_content += "# Generated by ssh2ls\n\n"
        
        for i, cmd in enumerate(commands, 1):
            script_content += f"echo 'Step {i}: {cmd}'\n"
            script_content += f"{cmd}\n"
            script_content += "echo ''\n"
        
        script_content += "echo 'Environment setup complete!'\n"
        
        # Save script locally
        temp_script = tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False)
        temp_script.write(script_content)
        temp_script.close()
        
        # Make executable
        os.chmod(temp_script.name, 0o755)
        
        try:
            # Upload script
            print("Uploading setup script...")
            upload_success = self.transfer_files(
                session_name=session_name,
                local_path=temp_script.name,
                remote_path="~/setup_env.sh",
                direction="upload"
            )
            
            if not upload_success:
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
            os.unlink(temp_script.name)
            
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
            "add_key": f"ssh-add {jh['private_key']}"
        }

class SSH2LS:
    """Main SSH2LS application"""
    
    def __init__(self):
        self.key_manager = SSHKeyManager()
        self.ssh_manager = MultiHopSSHManager()
        self.config_dir = Path("~/.ssh/ssh2ls").expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.instructions = InstructionDisplay()
    def interactive_wizard(self):
        """Interactive wizard for setting up SSH connections"""
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                  SSH2LS - Connection Wizard                  ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print("\nTo setup complex SSH connections.")
        print("  Local → Jumphost (xxx.xxx.xx.xxx) → Remote VM (xxx.xxx.xx.xxx)")
        print()
        
        while True:
            print("\n" + "="*70)
            print("MAIN MENU")
            print("="*70)
            print("1. SSH Key Management")
            print("2. Setup Multi-Hop Connection (like deNBI)")
            print("3. Manage Existing Connections")
            print("4. Transfer Files")
            print("5. Setup Remote Environment")
            print("6. Create SSH Tunnels")
            print("7. Show Quick Commands")
            print("8. Test Connections")
            print("9. Export Configuration")
            print("0. Exit")
            
            choice = input("\nSelect option (0-9): ").strip()
            
            if choice == "1":
                self.key_management_menu()
            elif choice == "2":
                self.setup_multi_hop_menu()
            elif choice == "3":
                self.manage_connections_menu()
            elif choice == "4":
                self.file_transfer_menu()
            elif choice == "5":
                self.environment_setup_menu()
            elif choice == "6":
                self.tunnel_management_menu()
            elif choice == "7":
                self.show_quick_commands()
            elif choice == "8":
                self.test_connections_menu()
            elif choice == "9":
                self.export_configuration()
            elif choice == "0":
                print("\nbye!")
                break
            else:
                print("Invalid option. Please try again.")
    
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
            print("5. Find available keys")
            print("6. Fix key permissions")
            print("7. Extract public key from private")
            print("8. Back to main menu")
            
            choice = input("\nSelect option (1-8): ").strip()
            
            if choice == "1":
                self.generate_key_interactive()
            elif choice == "2":
                self.list_keys_in_agent()
            elif choice == "3":
                self.add_key_to_agent_interactive()
            elif choice == "4":
                self.remove_key_from_agent_interactive()
            elif choice == "5":
                self.find_available_keys()
            elif choice == "6":
                self.fix_key_permissions_interactive()
            elif choice == "7":
                self.extract_public_key()
            elif choice == "8":
                break
            else:
                print("Invalid option.")
    
    def generate_key_interactive(self):
        """Interactive SSH key generation"""
        print("\nGenerating SSH key pair...")
        
        key_name = input("Key name [id_ed25519_denbi]: ").strip() or "id_ed25519_denbi"
        key_type = input("Key type (rsa/ed25519/ecdsa) [ed25519]: ").strip() or "ed25519"
        
        if key_type == "rsa":
            key_size = input("Key size (2048/3072/4096) [4096]: ").strip() or "4096"
            key_size = int(key_size)
        else:
            key_size = None
        
        use_passphrase = input("Use passphrase? (y/N): ").strip().lower() == 'y'
        passphrase = None
        if use_passphrase:
            passphrase = getpass.getpass("Passphrase: ")
            passphrase_confirm = getpass.getpass("Confirm passphrase: ")
            if passphrase != passphrase_confirm:
                print("✗ Passphrases do not match!")
                return
        
        comment = input(f"Comment [{getpass.getuser()}@denbi]: ").strip() or f"{getpass.getuser()}@denbi"
        
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
    
    def setup_multi_hop_menu(self):
        """Setup multi-hop connection like deNBI"""
        print("\n" + "─"*70)
        print("SETUP MULTI-HOP CONNECTION")
        print("─"*70)
        print("\nThis will setup a connection like your deNBI setup:")
        print("  Your Mac → Jumphost → Target VM")
        print()
        
        session_name = input("Connection name (e.g., 'denbi', 'production'): ").strip()
        if not session_name:
            print("✗ Connection name is required")
            return
        
        print("\n--- Jumphost Configuration ---")
        jumphost_ip = input("Jumphost IP/Hostname (e.g., 193.196.20.189): ").strip()
        jumphost_user = input(f"Jumphost username [ubuntu]: ").strip() or "ubuntu"
        
        print("\n--- SSH Key for Jumphost ---")
        print("1. Use existing key")
        print("2. Generate new key")
        print("3. Skip for now")
        
        key_choice = input("\nSelect option (1-3): ").strip()
        
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
            private_key, public_key = self.key_manager.generate_key_pair(
                key_name=f"id_ed25519_{session_name}",
                key_type="ed25519",
                comment=f"{getpass.getuser()}@{session_name}"
            )
            private_key_path = str(private_key)
            
            print("\n⚠ IMPORTANT: Share this public key with your admin:")
            print("-" * 80)
            with open(public_key, 'r') as f:
                print(f.read().strip())
            print("-" * 80)
            print("\nAsk them to add it to the jumphost's authorized_keys")
            input("\nPress Enter when the key has been added to the jumphost...")
        
        else:
            private_key_path = input("Path to private key: ").strip()
        
        print("\n--- Target VM Configuration ---")
        target_ip = input("Target VM IP (e.g., 192.168.54.219): ").strip()
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
    
    def manage_connections_menu(self):
        """Manage existing connections"""
        sessions = self.ssh_manager.sessions
        
        if not sessions:
            print("No connections configured.")
            return
        
        print("\n" + "─"*70)
        print("MANAGE CONNECTIONS")
        print("─"*70)
        
        while True:
            print("\nConfigured connections:")
            for i, (name, session) in enumerate(sessions.items(), 1):
                jh = session["jumphost"]
                target = session["target"]
                last_used = session.get("last_used", "Never")
                print(f"{i:2}. {name}: {jh['user']}@{jh['ip']} → {target['user']}@{target['ip']}")
                print(f"    Last used: {last_used}")
            
            print("\nOptions:")
            print("1. Connect to jumphost")
            print("2. Connect to target via jumphost")
            print("3. Test connection")
            print("4. Edit connection")
            print("5. Delete connection")
            print("6. Show SSH config")
            print("7. Back to main menu")
            
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == "1":
                self._connect_to_host("jumphost")
            elif choice == "2":
                self._connect_to_host("target")
            elif choice == "3":
                self._test_specific_connection()
            elif choice == "4":
                self._edit_connection()
            elif choice == "5":
                self._delete_connection()
            elif choice == "6":
                self._show_ssh_config()
            elif choice == "7":
                break
            else:
                print("Invalid option.")
    
    def _connect_to_host(self, host_type: str):
        """Connect to jumphost or target"""
        sessions = self.ssh_manager.sessions
        if not sessions:
            print("No connections configured.")
            return
        
        print("\nSelect connection:")
        names = list(sessions.keys())
        for i, name in enumerate(names, 1):
            print(f"{i}. {name}")
        
        choice = input(f"\nSelect connection (1-{len(names)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(names):
            session_name = names[int(choice) - 1]
            self.ssh_manager.interactive_shell(session_name, host_type)
        else:
            print("Invalid selection.")
    
    def file_transfer_menu(self):
        """File transfer menu"""
        sessions = self.ssh_manager.sessions
        
        if not sessions:
            print("No connections configured.")
            return
        
        print("\n" + "─"*70)
        print("FILE TRANSFER")
        print("─"*70)
        
        print("\nSelect connection:")
        names = list(sessions.keys())
        for i, name in enumerate(names, 1):
            print(f"{i}. {name}")
        
        choice = input(f"\nSelect connection (1-{len(names)}): ").strip()
        if not (choice.isdigit() and 1 <= int(choice) <= len(names)):
            print("Invalid selection.")
            return
        
        session_name = names[int(choice) - 1]
        
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
        sessions = self.ssh_manager.sessions
        
        if not sessions:
            print("No connections configured.")
            return
        
        print("\n" + "─"*70)
        print("REMOTE ENVIRONMENT SETUP")
        print("─"*70)
        print("\nThis will help you setup a remote environment like your nf-core setup.")
        
        print("\nSelect connection:")
        names = list(sessions.keys())
        for i, name in enumerate(names, 1):
            print(f"{i}. {name}")
        
        choice = input(f"\nSelect connection (1-{len(names)}): ").strip()
        if not (choice.isdigit() and 1 <= int(choice) <= len(names)):
            print("Invalid selection.")
            return
        
        session_name = names[int(choice) - 1]
        
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
                "echo 'Next: Copy your data and run: apptainer pull docker://nfcore/chipseq'"
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
        
        while True:
            tunnels = self.ssh_manager.tunnels
            
            if tunnels:
                print("\nActive tunnels:")
                for name, tunnel in tunnels.items():
                    status = "🟢" if tunnel['status'] == 'running' else "🔴"
                    print(f"{status} {name}: localhost:{tunnel['local_port']} → {tunnel['remote_host']}:{tunnel['remote_port']}")
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
            elif choice == "2":
                self._start_tunnel_interactive()
            elif choice == "3":
                self._stop_tunnel_interactive()
            elif choice == "4":
                self._view_tunnel_details()
            elif choice == "5":
                self._delete_tunnel()
            elif choice == "6":
                break
            else:
                print("Invalid option.")
    
    def _create_tunnel_interactive(self):
        """Create tunnel interactively"""
        sessions = self.ssh_manager.sessions
        
        if not sessions:
            print("No connections configured. Create a connection first.")
            return
        
        print("\nSelect connection:")
        names = list(sessions.keys())
        for i, name in enumerate(names, 1):
            print(f"{i}. {name}")
        
        choice = input(f"\nSelect connection (1-{len(names)}): ").strip()
        if not (choice.isdigit() and 1 <= int(choice) <= len(names)):
            print("Invalid selection.")
            return
        
        session_name = names[int(choice) - 1]
        
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
    
    def show_quick_commands(self):
        """Show quick commands for a connection"""
        sessions = self.ssh_manager.sessions
        
        if not sessions:
            print("No connections configured.")
            return
        
        print("\n" + "─"*70)
        print("QUICK COMMANDS")
        print("─"*70)
        
        print("\nSelect connection:")
        names = list(sessions.keys())
        for i, name in enumerate(names, 1):
            print(f"{i}. {name}")
        
        choice = input(f"\nSelect connection (1-{len(names)}): ").strip()
        if not (choice.isdigit() and 1 <= int(choice) <= len(names)):
            print("Invalid selection.")
            return
        
        session_name = names[int(choice) - 1]
        
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
    
    def _append_to_ssh_config(self, config_text: str):
        """Append configuration to ~/.ssh/config"""
        ssh_config_path = Path("~/.ssh/config").expanduser()
        ssh_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing config
        if ssh_config_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = ssh_config_path.with_name(f"config.backup.{timestamp}")
            shutil.copy2(ssh_config_path, backup_path)
            print(f"✓ Backup created: {backup_path}")
        
        # Append new config
        with open(ssh_config_path, 'a') as f:
            f.write(f"\n\n{config_text}\n")
    
    def run_from_cli(self):
        """Run from command line arguments"""
        parser = argparse.ArgumentParser(
            description="SSH2LS - Ultimate SSH Multi-Hop Manager",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.dedent("""
            Examples:
              %(prog)s wizard                     # Interactive wizard
              %(prog)s setup denbi                # Setup deNBI-like connection
              %(prog)s connect denbi              # Connect to target via jumphost
              %(prog)s tunnel create              # Create SSH tunnel
              %(prog)s transfer upload denbi      # Upload files
              %(prog)s setup-env denbi            # Setup remote environment
              %(prog)s quick denbi                # Show quick commands
              %(prog)s display                    # Display detailed instructions
              %(prog)s display --denbi            # deNBI-specific instructions
              %(prog)s display --cheatsheet       # Quick cheatsheet
            """)
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Command')
        
        # Wizard command
        subparsers.add_parser('wizard', help='Interactive wizard')
        
        # Setup command
        setup_parser = subparsers.add_parser('setup', help='Setup multi-hop connection')
        setup_parser.add_argument('name', help='Connection name')
        setup_parser.add_argument('--jumphost', required=True, help='Jumphost IP')
        setup_parser.add_argument('--jumphost-user', default='ubuntu', help='Jumphost username')
        setup_parser.add_argument('--target', required=True, help='Target IP')
        setup_parser.add_argument('--target-user', help='Target username')
        setup_parser.add_argument('--key', help='Private key path')
        
        # Connect command
        connect_parser = subparsers.add_parser('connect', help='Connect to host')
        connect_parser.add_argument('name', help='Connection name')
        connect_parser.add_argument('--hop', choices=['jumphost', 'target'], 
                                  default='target', help='Which hop to connect to')
        
        # Transfer command
        transfer_parser = subparsers.add_parser('transfer', help='Transfer files')
        transfer_parser.add_argument('direction', choices=['upload', 'download'])
        transfer_parser.add_argument('name', help='Connection name')
        transfer_parser.add_argument('source', help='Source path')
        transfer_parser.add_argument('dest', help='Destination path')
        
        # Tunnel command
        tunnel_parser = subparsers.add_parser('tunnel', help='Manage tunnels')
        tunnel_subparsers = tunnel_parser.add_subparsers(dest='tunnel_command')
        
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
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        try:
            if args.command == 'wizard':
                self.interactive_wizard()
            
            elif args.command == 'setup':
                self.ssh_manager.create_jumphost_config(
                    name=args.name,
                    jumphost_ip=args.jumphost,
                    jumphost_user=args.jumphost_user,
                    private_key_path=args.key or f"~/.ssh/id_ed25519_{args.name}",
                    target_ip=args.target,
                    target_user=args.target_user or args.jumphost_user
                )
            
            elif args.command == 'connect':
                self.ssh_manager.interactive_shell(args.name, args.hop)
            
            elif args.command == 'transfer':
                self.ssh_manager.transfer_files(
                    session_name=args.name,
                    local_path=args.source,
                    remote_path=args.dest,
                    direction=args.direction
                )
            
            elif args.command == 'tunnel':
                if args.tunnel_command == 'create':
                    self.ssh_manager.create_tunnel(
                        session_name=args.name,
                        local_port=args.local_port,
                        remote_host=args.remote_host,
                        remote_port=args.remote_port,
                        tunnel_name=args.tunnel_name
                    )
                elif args.tunnel_command == 'start':
                    self.ssh_manager.start_tunnel(args.tunnel_name, args.background)
                elif args.tunnel_command == 'stop':
                    self.ssh_manager.stop_tunnel(args.tunnel_name)
            
            elif args.command == 'setup-env':
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
                commands = self.ssh_manager.get_quick_commands(args.name)
                for desc, cmd in commands.items():
                    print(f"{desc}: {cmd}")
            
            elif args.command == 'test':
                self.ssh_manager.test_connection(args.name)
            
            elif args.command == 'list':
                sessions = self.ssh_manager.sessions
                if sessions:
                    for name, session in sessions.items():
                        jh = session["jumphost"]
                        target = session["target"]
                        print(f"{name}: {jh['user']}@{jh['ip']} → {target['user']}@{target['ip']}")
                else:
                    print("No connections configured.")
            
            elif args.command == 'display':
                if args.denbi:
                    self.instructions.display_deNBI_specific()
                elif args.cheatsheet:
                    self.instructions.display_cheatsheet()
                else:
                    self.instructions.display_full_instructions()
        
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)


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
        print("multi-hop setups like your deNBI infrastructure. It automates everything from")
        print("key management to file transfers through jump hosts.")
        
        print("\n" + "="*80)
        print("🚀 QUICK START")
        print("="*80)
        
        print("\n1. Interactive Wizard (Recommended for beginners):")
        print("   python ssh2ls.py wizard")
        print("   python ssh2ls.py                    # Defaults to wizard mode")
        
        print("\n2. Automated deNBI Setup (Your specific setup):")
        print("   python ssh2ls.py setup denbi \\")
        print("     --jumphost 193.196.20.189 \\")
        print("     --jumphost-user ubuntu \\")
        print("     --target 192.168.54.219 \\")
        print("     --key ~/.ssh/denbi")
        
        print("\n3. Connect to your deNBI VM:")
        print("   python ssh2ls.py connect denbi --hop target")
        
        print("\n" + "="*80)
        print("📋 COMMAND REFERENCE")
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
        
        print("\n" + "="*80)
        print("🎯 REAL-WORLD EXAMPLES (FROM YOUR NOTES)")
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
        
        print("\n📝 EXAMPLE 4: Create SSH Tunnel for Web Access")
        print("-" * 40)
        print("# Tunnel local port 8888 to remote port 80")
        print("python ssh2ls.py tunnel create denbi 8888 localhost 80")
        print("python ssh2ls.py tunnel start denbi_tunnel_8888_80")
        print()
        print("# Now access http://localhost:8888 in your browser")
        print("# This tunnels through jumphost to target VM")
        
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
        print("⚙️  ADVANCED CONFIGURATION")
        print("="*80)
        
        print("\n📁 SSH Config File (Automatically Generated):")
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
        
        print("\n🔐 SSH Agent Forwarding:")
        print("-" * 40)
        print("# Enable agent forwarding (automatic with -A flag)")
        print("ssh -A -i ~/.ssh/denbi ubuntu@193.196.20.189")
        print("# On jumphost, your keys are available:")
        print("ssh-add -l  # Should show your keys")
        
        print("\n📊 File Transfer Syntax:")
        print("-" * 40)
        print("# Manual SCP through jumphost:")
        print("scp -r -o ProxyJump=ubuntu@193.196.20.189 \\")
        print("  -i ~/.ssh/denbi \\")
        print("  local_file ubuntu@192.168.54.219:remote_path")
        
        print("\n" + "="*80)
        print("🎮 INTERACTIVE WIZARD WALKTHROUGH")
        print("="*80)
        
        print("\n1. Start wizard: python ssh2ls.py wizard")
        print("2. Choose 'Setup Multi-Hop Connection'")
        print("3. Enter connection details:")
        print("   - Name: denbi")
        print("   - Jumphost IP: 193.196.20.189")
        print("   - Jumphost user: ubuntu")
        print("   - Target IP: 192.168.54.219")
        print("   - Target user: ubuntu")
        print("   - Private key: ~/.ssh/denbi")
        print("4. Wizard will:")
        print("   - Generate SSH config")
        print("   - Setup agent forwarding")
        print("   - Test connection")
        print("   - Create useful aliases")
        
        print("\n" + "="*80)
        print("📚 ADDITIONAL RESOURCES")
        print("="*80)
        
        print("\n🔗 Useful SSH Documentation:")
        print("  • SSH Config Manual: man ssh_config")
        print("  • ProxyJump: https://en.wikibooks.org/wiki/OpenSSH/Cookbook/Proxies_and_Jump_Hosts")
        print("  • Agent Forwarding: https://en.wikibooks.org/wiki/OpenSSH/Cookbook/Agent_Forwarding")
        
        print("\n🔗 nf-core Resources:")
        print("  • nf-core ChIP-seq: https://nf-co.re/chipseq")
        print("  • Pipeline documentation: https://nf-co.re/chipseq/docs")
        
        print("\n🔗 deNBI Resources:")
        print("  • deNBI Cloud: https://cloud.denbi.de/")
        print("  • Documentation: https://docs.denbi.de/")
        
        print("\n" + "="*80)
        print("💡 PRO TIPS")
        print("="*80)
        
        print("\n1. Use SSH config aliases:")
        print("   ssh denbi         # Connect to target via jumphost")
        print("   ssh denbi_jumphost # Connect to jumphost directly")
        
        print("\n2. Persistent connections with ControlMaster:")
        print("   Add to ~/.ssh/config:")
        print("   Host *")
        print("     ControlMaster auto")
        print("     ControlPath ~/.ssh/controlmasters/%r@%h:%p")
        print("     ControlPersist 10m")
        
        print("\n3. Monitor SSH connections:")
        print("   ssh -O check denbi    # Check connection status")
        print("   ssh -O exit denbi     # Close connection")
        
        print("\n4. Verbose debugging:")
        print("   ssh -vvv denbi        # Level 3 verbosity")
        print("   scp -v ...            # Verbose SCP")
        
        print("\n5. Transfer entire directories:")
        print("   tar czf - /local/dir | ssh denbi 'tar xzf - -C /remote/dir'")
        
        print("\n" + "="*80)
        print("❓ NEED HELP?")
        print("="*80)
        
        print("\nRun these commands for help:")
        print("  python ssh2ls.py --help            # Command line help")
        print("  python ssh2ls.py display           # Show these instructions")
        print("  man ssh                            # SSH manual")
        print("  man ssh_config                     # SSH config manual")
        
        print("\nCommon problems and solutions are in the troubleshooting section above.")
        print("For specific issues with your deNBI setup, check the examples section.")
        
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
        
        print("\n📋 YOUR SPECIFIC CONFIGURATION:")
        print("-" * 40)
        print("Jumphost:      ubuntu@193.196.20.189")
        print("Target VM:      ubuntu@192.168.54.219")
        print("Private key:    ~/.ssh/denbi")
        print("Purpose:        nf-core ChIP-seq analysis")
        
        print("\n🚀 COMPLETE WORKFLOW:")
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
        
        print("\n4. TRANSFER YOUR DATA:")
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
        print("📞 SUPPORT CONTACTS")
        print("="*80)
        
        print("\nFor deNBI infrastructure issues:")
        print("  • Mohamad (Admin): Provided jumphost access")
        print("  • deNBI Support: https://cloud.denbi.de/support")
        
        print("\nFor nf-core pipeline issues:")
        print("  • nf-core documentation: https://nf-co.re/chipseq/docs")
        print("  • GitHub issues: https://github.com/nf-core/chipseq/issues")
        
        print("\nFor SSH2LS tool issues:")
        print("  • Run: python ssh2ls.py --help")
        print("  • Use: python ssh2ls.py display (these instructions)")
        
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
        
        print("\n🔗 CONNECTION:")
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
        
        print("\n🌐 TUNNELS:")
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
        print("💾 CONFIGURATION FILES")
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
        
        print("\n~/.ssh/ssh2ls/sessions.json (managed by ssh2ls):")
        print("-" * 40)
        print("Stores all your connection configurations")
        
        print("\n" + "="*80)
        print("🚀 QUICK START RECAP")
        print("="*80)
        
        print("\nFor your deNBI setup:")
        print("  1. ssh-keygen -t ed25519 -f ~/.ssh/denbi")
        print("  2. cat ~/.ssh/denbi.pub → share with admin")
        print("  3. python ssh2ls.py setup denbi [options]")
        print("  4. python ssh2ls.py connect denbi")
        print("  5. python ssh2ls.py transfer upload denbi data/ ~/")
        
        print("\n" + "="*80 + "\n")
def main():
    """Main entry point"""
    app = SSH2LS()
    
    if len(sys.argv) > 1:
        app.run_from_cli()
    else:
        # Check dependencies
        try:
            import paramiko
            import cryptography
            print("✓ All dependencies found")
        except ImportError as e:
            print(f"⚠ Missing dependency: {e}")
            print("Install with: pip install paramiko cryptography pyyaml")
            sys.exit(1)
        
        # Start interactive wizard
        app.interactive_wizard()

if __name__ == "__main__":
    main()