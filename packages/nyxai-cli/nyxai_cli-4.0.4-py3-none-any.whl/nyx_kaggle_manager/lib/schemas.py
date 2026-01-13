"""
Data Schemas for Nyx System
Defines type-safe data structures for tasks, workers, and hardware requirements.
"""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime


class WorkloadType(Enum):
    """Classification of workload types."""
    INFERENCE = "inference"
    TRAINING = "training"
    SETUP = "setup"
    DATA_PROC = "data_processing"
    UNKNOWN = "unknown"


class WorkerStatus(Enum):
    """Worker node status states."""
    OFFLINE = "offline"
    STARTING = "starting"
    READY = "ready"
    BUSY = "busy"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class HardwareRequirement:
    """Hardware requirements for a task."""
    needs_gpu: bool
    min_vram_gb: int
    estimated_vram_gb: int
    gpu_preference: str  # 't4', 't4x2', 'p100', 'cpu'
    reason: str


@dataclass
class Task:
    """Represents a computational task to be executed."""
    id: str
    filename: str
    code: str
    workload_type: WorkloadType
    hardware: HardwareRequirement
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, running, completed, failed
    worker_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization."""
        return {
            k: str(v) if isinstance(v, (datetime, WorkloadType)) else v 
            for k, v in asdict(self).items()
        }


@dataclass
class WorkerNode:
    """Represents a worker node in the infrastructure."""
    id: str
    kernel_slug: str
    hardware: str
    role: str  # 'master' or 'worker'
    status: WorkerStatus = WorkerStatus.OFFLINE
    last_heartbeat: Optional[datetime] = None
    current_task_id: Optional[str] = None

    @property
    def is_alive(self) -> bool:
        """Check if worker is alive based on heartbeat."""
        if not self.last_heartbeat:
            return False
        return (datetime.now() - self.last_heartbeat).total_seconds() < 120
