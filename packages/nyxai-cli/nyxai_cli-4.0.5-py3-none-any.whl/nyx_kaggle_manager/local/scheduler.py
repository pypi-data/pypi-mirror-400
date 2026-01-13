"""
Scheduler - The Brain of Nyx Orchestration System
Manages task queuing, worker assignment, and infrastructure lifecycle.
Implements a robust file-based queue system similar to Linux spoolers for process isolation.
"""
import asyncio
import uuid
import os
import json
import heapq
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from nyx_kaggle_manager.lib.schemas import Task, WorkerNode, WorkerStatus, HardwareRequirement, WorkloadType
from nyx_kaggle_manager.lib.inspector import Inspector
from nyx_kaggle_manager.lib.utils import logger, save_json, load_json, NYX_DATA_DIR
from nyx_kaggle_manager.local.kaggle_adapter import KaggleAdapter


class Scheduler:
    """
    Central orchestration controller for Nyx system.
    
    Architecture:
    - Daemon Mode: The 'init' process runs the main loop, digesting tasks from disk and managing workers.
    - Client Mode: 'run', 'ps' commands interact via file system IPC (queues and status files).
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.kaggle = KaggleAdapter(config)
        self.inspector = Inspector()
        
        # Directories for IPC
        self.queue_dir = NYX_DATA_DIR / "queue"
        self.pending_dir = self.queue_dir / "pending"
        self.completed_dir = self.queue_dir / "completed"
        self.status_file = NYX_DATA_DIR / "status.json"
        
        # In-Memory State (Managed by Daemon only)
        # We use a list as a heap for the priority queue
        self.task_queue: List[Task] = []
        self.workers: Dict[str, WorkerNode] = {}
        self.active_tasks: Dict[str, Task] = {}
        
        self.is_running = False
        self._ensure_directories()
        
        # Hardware cache to prevent API spam
        self._hardware_cache = {} 
        
        logger.info("Scheduler initialized")

    def _ensure_directories(self):
        """Create necessary directories for operation."""
        self.pending_dir.mkdir(parents=True, exist_ok=True)
        self.completed_dir.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # CLIENT METHODS (Used by CLI 'run', 'ps')
    # =========================================================================

    def submit_task(self, filename: str, code: str, hardware_choice: str, priority: int = 1) -> str:
        """
        Submit a task by writing it to the pending queue directory.
        Safe to call from concurrent CLI processes.
        """
        task_id = str(uuid.uuid4())[:8]
        analysis = self.inspector.analyze(code, filename)
        
        # We can't easily do async calls here in sync context without full loop setup.
        # So we pass 0 for VRAM and let the Daemon update it later, 
        # OR we rely on the user/cache if available. 
        # For simplicity and speed in CLI, we set placeholders and let Daemon refine it.
        needs_gpu = 'gpu' in hardware_choice.lower()
        
        hardware = HardwareRequirement(
            needs_gpu=needs_gpu,
            min_vram_gb=0, # Resolved by Daemon
            estimated_vram_gb=0,
            gpu_preference=hardware_choice,
            reason=f"User selected {hardware_choice}"
        )
        
        task_data = {
            "id": task_id,
            "filename": filename,
            "code": code,
            "workload_type": analysis['workload_type'],
            "hardware": {
                "needs_gpu": hardware.needs_gpu,
                "min_vram_gb": hardware.min_vram_gb,
                "estimated_vram_gb": hardware.estimated_vram_gb,
                "gpu_preference": hardware.gpu_preference,
                "reason": hardware.reason
            },
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # Atomic write: write to temp then rename
        task_file = self.pending_dir / f"{priority}_{task_id}.json"
        temp_file = self.pending_dir / f".tmp_{task_id}"
        
        with open(temp_file, 'w') as f:
            json.dump(task_data, f, indent=2)
        
        os.rename(temp_file, task_file)
        logger.info(f"Task {task_id} queued at {task_file}")
        return task_id

    def get_status_summary(self) -> Dict[str, Any]:
        """Read the live status from the status file updated by the daemon."""
        if self.status_file.exists():
            try:
                return load_json(self.status_file)
            except Exception:
                return {"error": "Status file unreadable"}
        return {"scheduler_status": "offline (no status file)"}

    # =========================================================================
    # DAEMON METHODS (Used by 'init' loop)
    # =========================================================================

    async def start(self):
        """Start the main event loop."""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Scheduler Daemon started")
        
        # Load any persisted state if needed? 
        # Actually better to just start fresh and scan directories.
        
        await asyncio.gather(
            self._queue_watcher_loop(),
            self._worker_monitor_loop(),
            self._main_scheduler_loop(),
            self._state_reporter_loop()
        )

    async def _queue_watcher_loop(self):
        """Monitors pending directory for new tasks."""
        logger.info("Starting Queue Watcher...")
        while self.is_running:
            try:
                # Scan for .json files
                # sort by name implies priority because we prefixed filename with priority
                # {priority}_{id}.json -> "1_abc.json", "5_xyz.json"
                # Since '1' < '5', lower number comes first? 
                # Usually higher priority number means 'more important' in Linux nice? 
                # Let's assume User Input: Higher is better. 
                # But file sort: '10' comes before '2'. 
                # We should rely on parsing the file content or simple glob.
                
                for file_path in self.pending_dir.glob("*.json"):
                    try:
                        data = load_json(file_path)
                        # Reconstruct Task object
                        hw_data = data['hardware']
                        hardware = HardwareRequirement(**hw_data)
                        
                        task = Task(
                            id=data['id'],
                            filename=data['filename'],
                            code=data['code'],
                            workload_type=WorkloadType(data['workload_type']),
                            hardware=hardware,
                            priority=data['priority'],
                            created_at=datetime.fromisoformat(data['created_at']),
                            status="queued"
                        )
                        
                        # Refine VRAM info relative to now
                        vram = await self._get_hardware_vram(task.hardware.gpu_preference)
                        task.hardware.min_vram_gb = vram
                        
                        # Add to internal priority queue (Min-heap by default in Python)
                        # We want Max-heap behavior for priority (10 > 1).
                        # Tuple comparison: (-priority, date, task)
                        heapq.heappush(self.task_queue, (-task.priority, task.created_at.timestamp(), task))
                        
                        logger.info(f"Imported task {task.id} with priority {task.priority}")
                        
                        # Move file to 'processed' or just delete? 
                        # Delete is fine since it's now in memory. 
                        # If daemon crashes, we might lose it? 
                        # -> Robustness: Move to 'active' folder/state file.
                        file_path.unlink() 
                        
                    except Exception as e:
                        logger.error(f"Corrupt task file {file_path}: {e}")
                        # Move to failed/corrupt folder to avoid infinite loop
                        file_path.rename(file_path.with_suffix(".corrupt"))
            
            except Exception as e:
                logger.error(f"Watcher loop error: {e}")
            
            await asyncio.sleep(2)

    async def _main_scheduler_loop(self):
        """Core logic: Assign tasks to workers."""
        logger.info("Starting Main Scheduler Loop...")
        while self.is_running:
            if self.task_queue:
                # Peek at highest priority task
                # storage is (-priority, created, task)
                priority_neg, _, task = self.task_queue[0]
                
                # Try to find a worker
                worker = self._find_available_worker(task.hardware.gpu_preference)
                
                if not worker and len(self.workers) < self.config['orchestrator'].get('max_workers', 5):
                    # Provisioning
                    # Async provision shouldn't block loop, but we need to wait for result to assign.
                    # We can spawn provision and continue loop in next iteration.
                    asyncio.create_task(
                        self._provision_new_worker(task.hardware.gpu_preference)
                    )
                    # Don't pop task yet
                elif worker:
                    # Pop task from heap
                    heapq.heappop(self.task_queue)
                    
                    # Execute
                    task.status = "running"
                    self.active_tasks[task.id] = task
                    worker.status = WorkerStatus.BUSY
                    worker.current_task_id = task.id
                    
                    asyncio.create_task(self._execute_task(task, worker))
            
            await asyncio.sleep(1)

    async def _execute_task(self, task: Task, worker: WorkerNode):
        """Submit and monitor a task execution."""
        logger.info(f"Executing task {task.id} on worker {worker.id}")
        try:
            await self.kaggle.update_kernel(worker.kernel_slug, task.code, f"Nyx Task {task.id}")
            # Real execution monitoring would go here (polling status)
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            task.status = "failed"
            worker.status = WorkerStatus.READY

    async def _state_reporter_loop(self):
        """Periodically dump state to disk for 'ps' command."""
        logger.info("Starting State Reporter...")
        while self.is_running:
            try:
                # Reconstruct list from heap for display
                # Note: This is an O(N) operation, okay for small N (<100)
                queued_tasks = [t[2] for t in self.task_queue]
                
                status_data = {
                    "last_updated": datetime.now().isoformat(),
                    "scheduler_status": "running",
                    "tasks_pending": len(queued_tasks),
                    "tasks_active": len(self.active_tasks),
                    "workers_total": len(self.workers),
                    "workers_ready": sum(1 for w in self.workers.values() if w.status == WorkerStatus.READY),
                    "queue": [
                        {"id": t.id, "filename": t.filename, "priority": t.priority, "hardware": t.hardware.gpu_preference} 
                        for t in queued_tasks
                    ],
                    "active": [
                        {"id": t.id, "filename": t.filename, "worker": getattr(t, 'worker_id', 'unknown')}
                        for t in self.active_tasks.values()
                    ],
                    "workers": [
                        {"id": w.id, "status": w.status.value, "hardware": w.hardware} 
                        for w in self.workers.values()
                    ]
                }
                
                # Atomic write
                temp = self.status_file.with_suffix(".tmp")
                with open(temp, 'w') as f:
                    json.dump(status_data, f, indent=2)
                os.replace(temp, self.status_file)
                
            except Exception as e:
                logger.error(f"Reporting error: {e}")
            
            await asyncio.sleep(2)

    async def _worker_monitor_loop(self):
        # Placeholder for existing logic
        while self.is_running:
            await asyncio.sleep(10)

    async def _provision_new_worker(self, hardware: str):
        # Existing logic placeholder
        # Actual provisioning takes time
        await asyncio.sleep(0.1) 

    def _find_available_worker(self, hardware: str) -> Optional[WorkerNode]:
        for w in self.workers.values():
            if w.status == WorkerStatus.READY and w.hardware == hardware:
                return w
        return None

    async def _get_hardware_vram(self, hardware: str) -> int:
        # Existing logic adapted
        if hardware in self._hardware_cache:
            return self._hardware_cache[hardware].get('vram', 0)
        return 16 # fallback default

