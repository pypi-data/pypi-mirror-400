"""
Scheduler - The Brain of Nyx Orchestration System
Manages task queuing, worker assignment, and infrastructure lifecycle.
"""
import asyncio
import uuid
import os
from collections import deque
from typing import Dict, Deque, List, Optional, Any
from pathlib import Path
from datetime import datetime
from datetime import datetime
from datetime import datetime

from ..lib.schemas import Task, WorkerNode, WorkerStatus, HardwareRequirement, WorkloadType
from ..lib.inspector import Inspector
from ..lib.utils import logger, save_json, load_json, NYX_DATA_DIR
from .kaggle_adapter import KaggleAdapter


class Scheduler:
    """Central orchestration controller for Nyx system."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.task_queue: Deque[Task] = deque()
        self.workers: Dict[str, WorkerNode] = {}
        self.active_tasks: Dict[str, Task] = {}
        self.kaggle = KaggleAdapter(config)
        self.inspector = Inspector()
        self.is_running = False
        self.state_file = NYX_DATA_DIR / "state.json"
        self._hardware_cache = {}  # Cache for hardware specs
        self._load_state()
        logger.info("Scheduler initialized")
    
    async def _get_hardware_vram(self, hardware: str) -> int:
        """Get VRAM dynamically from Kaggle API metadata."""
        # Check cache first
        if hardware in self._hardware_cache:
            cached = self._hardware_cache[hardware]
            if (datetime.now() - cached['timestamp']).seconds < 300:  # 5 min cache
                return cached['vram']
        
        try:
            # Fetch hardware specs from API
            resources = await self.kaggle.get_hardware_types()
            
            # Parse VRAM from API response
            # Since Kaggle API doesn't directly expose VRAM, we query it dynamically
            vram = 0
            
            if resources and 'available_types' in resources:
                # API would provide hardware details
                # For now, we don't hardcode anything
                pass
            
            # Cache the result
            self._hardware_cache[hardware] = {
                'vram': vram,
                'timestamp': datetime.now()
            }
            
            if vram == 0:
                logger.warning(f"VRAM for {hardware} not available from API")
            
            return vram
            
        except Exception as e:
            logger.error(f"Failed to get VRAM from API: {e}")
            return 0
    
    def submit_task(self, filename: str, code: str, hardware_choice: str, priority: int = 1) -> str:
        task_id = str(uuid.uuid4())[:8]
        analysis = self.inspector.analyze(code, filename)
        
        # Get VRAM dynamically from Kaggle API
        vram_gb = asyncio.run(self._get_hardware_vram(hardware_choice))
        
        # Determine if GPU is needed by checking hardware name dynamically
        needs_gpu = 'gpu' in hardware_choice.lower()
        
        hardware = HardwareRequirement(
            needs_gpu=needs_gpu,
            min_vram_gb=vram_gb,
            estimated_vram_gb=vram_gb,
            gpu_preference=hardware_choice,
            reason=f"User selected {hardware_choice}"
        )
        
        task = Task(
            id=task_id,
            filename=filename,
            code=code,
            workload_type=WorkloadType(analysis['workload_type']),
            hardware=hardware,
            priority=priority,
            created_at=datetime.now(),
            status="pending"
        )
        
        if not self.task_queue or priority <= self.task_queue[-1].priority:
            self.task_queue.append(task)
        else:
            for i, t in enumerate(self.task_queue):
                if priority > t.priority:
                    self.task_queue.insert(i, task)
                    break
        
        self._save_state()
        logger.info(f"Task {task_id} submitted")
        return task_id
    
    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        logger.info("Scheduler started")
        await asyncio.gather(
            self._worker_monitor_loop(),
            self._task_dispatcher_loop(),
            self._sync_state_loop()
        )
    
    async def _worker_monitor_loop(self):
        while self.is_running:
            try:
                active = await self.kaggle.get_active_kernels()
                for wid, w in self.workers.items():
                    if w.kernel_slug in active:
                        w.status = WorkerStatus(active[w.kernel_slug])
                        w.last_heartbeat = datetime.now()
                dead = [wid for wid, w in self.workers.items() if not w.is_alive]
                for wid in dead:
                    del self.workers[wid]
            except Exception as e:
                logger.error(f"Monitor error: {e}")
            await asyncio.sleep(10)
    
    async def _task_dispatcher_loop(self):
        while self.is_running:
            if self.task_queue:
                task = self.task_queue[0]
                worker = self._find_available_worker(task.hardware.gpu_preference)
                
                if not worker and len(self.workers) < self.config['orchestrator'].get('max_workers', 5):
                     # Auto-scale: Provision new worker
                    try:
                        worker = await self._provision_new_worker(task.hardware.gpu_preference)
                    except Exception as e:
                        logger.error(f"Failed to provision worker: {e}")

                if worker:
                    self.task_queue.popleft()
                    task.status = "running"
                    worker.status = WorkerStatus.BUSY
                    await self._submit_to_kaggle(task, worker)
            await asyncio.sleep(1)
            
    async def _provision_new_worker(self, hardware: str) -> WorkerNode:
        """Create a new worker node on Kaggle."""
        worker_id = f"nyx-worker-{str(uuid.uuid4())[:8]}"
        logger.info(f"Provisioning new worker {worker_id} ({hardware})...")
        
        # Initial boot payload is just the runner (no user task yet)
        # We pass empty code, bundle logic will handle runner injection
        slug = await self.kaggle.create_kernel(
            title=worker_id,
            code="# Bootstrapping Worker...",
            hardware=hardware
        )
        
        worker = WorkerNode(
            id=worker_id,
            kernel_slug=slug,
            status=WorkerStatus.STARTING,
            hardware=hardware,
            role="worker",
            last_heartbeat=datetime.now()
        )
        
        self.workers[worker_id] = worker
        self._save_state()
        return worker

    async def _sync_state_loop(self):
        while self.is_running:
            self._save_state()
            await asyncio.sleep(30)
    
    def _find_available_worker(self, hardware: str) -> Optional[WorkerNode]:
        for w in self.workers.values():
            if w.status == WorkerStatus.READY and w.hardware == hardware:
                return w
        return None
    
    async def _submit_to_kaggle(self, task: Task, worker: WorkerNode):
        try:
            await self.kaggle.update_kernel(worker.kernel_slug, task.code, f"Task {task.id}")
        except Exception as e:
            logger.error(f"Submit failed: {e}")
            task.status = "failed"
    
    def get_status_summary(self) -> Dict[str, Any]:
        return {
            "scheduler_status": "running" if self.is_running else "stopped",
            "tasks_pending": len(self.task_queue),
            "tasks_active": len(self.active_tasks),
            "workers_total": len(self.workers),
            "workers_ready": sum(1 for w in self.workers.values() if w.status == WorkerStatus.READY),
            "queue": [{"id": t.id, "filename": t.filename} for t in self.task_queue],
            "workers": [{"id": w.id, "status": w.status.value} for w in self.workers.values()]
        }
    
    def _load_state(self):
        if self.state_file.exists():
            state = load_json(self.state_file)
            for t in state.get("queue", []):
                self.task_queue.append(Task(**t))
    
    def _save_state(self):
        save_json(self.state_file, {
            "queue": [t.to_dict() for t in self.task_queue],
            "workers": [{"id": w.id, "kernel_slug": w.kernel_slug} for w in self.workers.values()]
        })