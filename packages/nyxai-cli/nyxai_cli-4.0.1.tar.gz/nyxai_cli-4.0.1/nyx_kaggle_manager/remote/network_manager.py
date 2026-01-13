"""
Network Manager - Secure Tunnel Setup for Kaggle Workers
Automates Cloudflare Tunnel and Tailscale VPN setup.
"""
import subprocess
import os
import time
import sys
from pathlib import Path


class NetworkManager:
    """
    Automates secure networking for worker nodes.
    
    Features:
    - Cloudflare Tunnel for HTTP/HTTPS access
    - Tailscale VPN for SSH and direct access
    - Automatic installation and configuration
    """
    
    # Load from environment (Kaggle Secrets)
    CF_TOKEN = os.environ.get("NYX_CF_TOKEN", "")
    TS_AUTH_KEY = os.environ.get("NYX_TS_KEY", "")

    @staticmethod
    def _run(cmd: str, bg: bool = False):
        """Execute shell command with logging."""
        print(f"[NET] Running: {cmd[:60]}...", flush=True)
        
        if bg:
            return subprocess.Popen(
                cmd, shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
        
        try:
            result = subprocess.run(
                cmd, shell=True, check=True, 
                capture_output=True, text=True
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"[NET ERROR] {e.stderr or str(e)}", file=sys.stderr)
            return None

    @staticmethod
    def setup_cloudflare():
        """Install and run Cloudflared tunnel."""
        print("\n=== Cloudflare Tunnel Setup ===")
        
        # Check if installed
        check = subprocess.call(
            "command -v cloudflared", 
            shell=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        if check != 0:
            print("[NET] Installing cloudflared...")
            commands = [
                "mkdir -p --mode=0755 /usr/share/keyrings",
                "curl -fsSL https://pkg.cloudflare.com/cloudflare-public-v2.gpg | tee /usr/share/keyrings/cloudflare-public-v2.gpg >/dev/null",
                "echo 'deb [signed-by=/usr/share/keyrings/cloudflare-public-v2.gpg] https://pkg.cloudflare.com/cloudflared any main' | tee /etc/apt/sources.list.d/cloudflared.list",
                "apt-get update",
                "apt-get install -y cloudflared"
            ]
            for cmd in commands:
                NetworkManager._run(cmd)
        else:
            print("[NET] Cloudflared already installed")

        # Start tunnel
        if NetworkManager.CF_TOKEN:
            print("[NET] Starting Cloudflare Tunnel...")
            log_file = "/var/log/cloudflared.log"
            cmd = f"nohup cloudflared tunnel run --token {NetworkManager.CF_TOKEN} > {log_file} 2>&1 &"
            NetworkManager._run(cmd, bg=True)
            print(f"[NET] ✓ Tunnel running (logs: {log_file})")
        else:
            print("[NET WARN] CF_TOKEN not set, skipping tunnel start")

    @staticmethod
    def setup_tailscale():
        """Install and connect Tailscale VPN."""
        print("\n=== Tailscale VPN Setup ===")
        
        # Check if installed
        check = subprocess.call(
            "command -v tailscale", 
            shell=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        if check != 0:
            print("[NET] Installing Tailscale...")
            NetworkManager._run("curl -fsSL https://tailscale.com/install.sh | sh")
        else:
            print("[NET] Tailscale already installed")

        # Connect
        if NetworkManager.TS_AUTH_KEY:
            print("[NET] Connecting to Tailscale network...")
            hostname = f"nyx-worker-{os.environ.get('KAGGLE_KERNEL_RUN_TYPE', 'local')}"
            cmd = f"tailscale up --auth-key={NetworkManager.TS_AUTH_KEY} --hostname={hostname} --accept-routes --ssh"
            
            result = NetworkManager._run(cmd)
            if result and result.returncode == 0:
                print("[NET] ✓ Tailscale connected")
            else:
                print("[NET WARN] Tailscale connection may have issues")
        else:
            print("[NET WARN] TS_AUTH_KEY not set, skipping connection")

    @staticmethod
    def start():
        """Initialize all networking components."""
        print("\n" + "="*50)
        print("Nyx Network Manager - Initializing")
        print("="*50)
        
        try:
            NetworkManager.setup_cloudflare()
        except Exception as e:
            print(f"[NET ERROR] Cloudflare setup failed: {e}", file=sys.stderr)

        try:
            NetworkManager.setup_tailscale()
        except Exception as e:
            print(f"[NET ERROR] Tailscale setup failed: {e}", file=sys.stderr)
        
        print("\n" + "="*50)
        print("Network initialization complete")
        print("="*50 + "\n")


if __name__ == "__main__":
    NetworkManager.start()
    
    # Keep alive
    print("[NET] Network manager running (keeping alive)...")
    try:
        while True:
            time.sleep(3600)  # Check every hour
    except KeyboardInterrupt:
        print("\n[NET] Shutting down...")
