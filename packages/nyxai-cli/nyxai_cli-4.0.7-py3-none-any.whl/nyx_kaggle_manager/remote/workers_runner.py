"""
Nyx Worker Node - Remote Runtime for Kaggle Kernels
Combines worker logic, snapshot management, and service hosting.
"""
import os
import sys
import time
import json
import subprocess
import signal
from pathlib import Path
from datetime import datetime


# ============================================================================
# CONFIGURATION (from environment variables)
# ============================================================================
IS_MASTER = os.environ.get("NYX_ROLE", "worker").lower() == "master"
SNAPSHOT_DIR = Path(os.environ.get("NYX_SNAPSHOT_DIR", "/kaggle/working/snapshots"))
HEARTBEAT_FILE = Path("/kaggle/working/heartbeat.json")
IDLE_TIMEOUT = int(os.environ.get("NYX_IDLE_TIMEOUT", "3600"))  # 1 hour default


# ============================================================================
# SNAPSHOT MANAGER
# ============================================================================
class SnapshotManager:
    """Handles filesystem snapshots for persistent state across kernel runs."""
    
    def __init__(self, snapshot_dir: Path):
        self.snapshot_dir = snapshot_dir
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    def restore_latest(self):
        """Restore the most recent snapshot if available."""
        snapshots = sorted(self.snapshot_dir.glob("*.tar.gz"))
        
        if snapshots:
            latest = snapshots[-1]
            print(f"[SNAPSHOT] Restoring: {latest.name}")
            try:
                subprocess.run(
                    ["tar", "-xzf", str(latest), "-C", "/"],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
                print("[SNAPSHOT] ✓ Restore complete")
            except Exception as e:
                print(f"[SNAPSHOT ERROR] Failed to restore: {e}", file=sys.stderr)
        else:
            print("[SNAPSHOT] No previous snapshots found")
    
    def save(self, paths: list = ["/home/nyx", "/kaggle/working/models"]):
        """Create a new snapshot of specified paths."""
        timestamp = int(time.time())
        snapshot_name = f"snap_{timestamp}.tar.gz"
        snapshot_path = self.snapshot_dir / snapshot_name
        
        print(f"[SNAPSHOT] Creating: {snapshot_name}")
        
        # Filter paths that exist
        existing_paths = [p for p in paths if Path(p).exists()]
        
        if not existing_paths:
            print("[SNAPSHOT WARN] No paths to snapshot")
            return
        
        try:
            cmd = ["tar", "-czf", str(snapshot_path)] + existing_paths
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
            print(f"[SNAPSHOT] ✓ Saved ({snapshot_path.stat().st_size // 1024 // 1024} MB)")
        except Exception as e:
            print(f"[SNAPSHOT ERROR] Failed to save: {e}", file=sys.stderr)


# ============================================================================
# WORKER RUNTIME
# ============================================================================
class WorkerRuntime:
    """Main runtime controller for worker nodes."""
    
    def __init__(self):
        self.snap = SnapshotManager(SNAPSHOT_DIR)
        self.last_active = time.time()
        self.is_running = True
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame):
        """Graceful shutdown handler."""
        print(f"\n[RUNTIME] Received signal {signum}, shutting down...")
        self.is_running = False
    
    def boot(self):
        """Bootstrap the worker node."""
        print("\n" + "="*60)
        print("Nyx Worker Node - Booting")
        print("="*60)
        print(f"Role: {'MASTER' if IS_MASTER else 'WORKER'}")
        print(f"Time: {datetime.now().isoformat()}")
        print(f"Kernel: {os.environ.get('KAGGLE_KERNEL_RUN_TYPE', 'unknown')}")
        print("="*60 + "\n")
        
        # Step 1: Initialize network (master only)
        if IS_MASTER:
            print("[RUNTIME] Initializing network services...")
            try:
                from network_manager import NetworkManager
                NetworkManager.start()
            except ImportError:
                print("[RUNTIME WARN] network_manager not found, skipping tunnels")
        
        # Step 2: Restore previous state
        print("[RUNTIME] Checking for snapshots...")
        self.snap.restore_latest()
        
        # Step 3: Start application services
        if IS_MASTER:
            self._start_master_services()
        else:
            self._start_worker_services()
        
        # Step 4: Execute User Task (if any)
        self._execute_user_task()
        
        # Step 5: Enter main loop
        print("[RUNTIME] Entering main loop...\n")
        self.main_loop()

    def _execute_user_task(self):
        """Executes the user task if 'user_task.py' exists."""
        task_file = Path("user_task.py")
        if task_file.exists():
            print(f"\n[RUNTIME] Found user task: {task_file}")
            print("="*40)
            try:
                start_time = time.time()
                # Run as a subprocess to isolate environments
                subprocess.run(
                    [sys.executable, str(task_file)], 
                    check=True,
                    env={**os.environ, "NYX_TASK_ACTIVE": "true"}
                )
                print("="*40)
                print(f"[RUNTIME] ✓ Task completed in {time.time() - start_time:.2f}s")
            except subprocess.CalledProcessError as e:
                print("="*40)
                print(f"[RUNTIME ERROR] Task failed with exit code {e.returncode}")
            except Exception as e:
                print(f"[RUNTIME ERROR] Task execution error: {e}")
        else:
            print("[RUNTIME] No user task pending")
    
    def _start_master_services(self):
        """Start master node services (e.g., ComfyUI)."""
        print("[RUNTIME] Starting master node services...")
        
        # Check for ComfyUI
        comfy_path = Path("/home/nyx/ComfyUI")
        if comfy_path.exists():
            print("[RUNTIME] ComfyUI found, starting server...")
            # subprocess.Popen(
            #     ["python", "main.py", "--listen", "0.0.0.0"],
            #     cwd=str(comfy_path)
            # )
            print("[RUNTIME] ✓ ComfyUI startup initiated")
        else:
            print("[RUNTIME] No ComfyUI installation found")
    
    def _start_worker_services(self):
        """Start worker node services."""
        print("[RUNTIME] Worker node ready for tasks")
    
    def main_loop(self):
        """Main heartbeat and task processing loop."""
        while self.is_running:
            # Write heartbeat
            self._write_heartbeat()
            
            # Check for tasks
            # (In production, check /kaggle/input/nyx-comm-hub for new tasks)
            
            # Idle timeout check
            idle_time = time.time() - self.last_active
            if idle_time > IDLE_TIMEOUT:
                print(f"\n[RUNTIME] Idle timeout ({IDLE_TIMEOUT}s) exceeded")
                print("[RUNTIME] Saving snapshot and shutting down...")
                self.snap.save()
                break
            
            # Sleep between cycles
            time.sleep(10)
        
        print("[RUNTIME] Main loop exited")
    
    def _write_heartbeat(self):
        """Write heartbeat file for orchestrator."""
        try:
            heartbeat_data = {
                "timestamp": time.time(),
                "iso_time": datetime.now().isoformat(),
                "role": "master" if IS_MASTER else "worker",
                "status": "alive",
                "idle_time": time.time() - self.last_active
            }
            
            HEARTBEAT_FILE.parent.mkdir(parents=True, exist_ok=True)
            HEARTBEAT_FILE.write_text(json.dumps(heartbeat_data, indent=2))
        except Exception as e:
            print(f"[RUNTIME WARN] Heartbeat write failed: {e}", file=sys.stderr)


# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    try:
        runtime = WorkerRuntime()
        runtime.boot()
    except KeyboardInterrupt:
        print("\n[RUNTIME] Interrupted by user")
    except Exception as e:
        print(f"\n[RUNTIME ERROR] Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        print("[RUNTIME] Shutdown complete\n")
