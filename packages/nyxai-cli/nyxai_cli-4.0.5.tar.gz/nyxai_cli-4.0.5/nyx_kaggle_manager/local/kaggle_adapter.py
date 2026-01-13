"""
Kaggle Adapter - Production-Ready Interface to Kaggle API
"""
import os
import json
import asyncio
from typing import Dict, Optional, Any
from pathlib import Path
from datetime import datetime

from nyx_kaggle_manager.lib.utils import logger

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    KAGGLE_AVAILABLE = True
except ImportError:
    KAGGLE_AVAILABLE = False
    KaggleApi = None


class KaggleAdapter:
    """Production-ready Kaggle API adapter. All data fetched dynamically from API."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.api = None
        self.username = None
        self._hardware_types_cache = None
        self._quotas_cache = None
        self._cache_timestamp = None
        self._authenticate()
    
    def _authenticate(self):
        if not KAGGLE_AVAILABLE:
            return
        try:
            self.api = KaggleApi()
            self.api.authenticate()
            cred_path = Path.home() / ".kaggle" / "kaggle.json"
            if cred_path.exists():
                with open(cred_path) as f:
                    self.username = json.load(f).get("username", "")
            logger.info(f"Authenticated as {self.username}")
        except Exception as e:
            logger.error(f"Auth failed: {e}")
    
    async def get_active_kernels(self) -> Dict[str, str]:
        if not self.api:
            return {}
        try:
            kernels = await asyncio.to_thread(self.api.kernels_list, mine=True, page_size=20)
            result = {}
            for k in kernels:
                if hasattr(k, 'ref'):
                    status = getattr(k, 'status', 'unknown')
                    result[k.ref] = "ready" if status == "running" else "offline"
            return result
        except Exception as e:
            logger.error(f"List kernels failed: {e}")
            return {}
    
    def _bundle_payload(self, user_code: str) -> str:
        """Bundles the user code with the worker runtime (Agent)."""
        try:
            # Locate remote/workers_runner.py relative to this file
            base_path = Path(__file__).parent.parent
            runner_path = base_path / "remote" / "workers_runner.py"
            
            if not runner_path.exists():
                logger.warning(f"workers_runner.py not found at {runner_path}, falling back to raw code")
                return user_code
                
            runner_code = runner_path.read_text(encoding='utf-8')
            
            # Create the bundle
            # 1. Write user code to user_task.py
            # 2. Execute worker runner
            
            # We construct a main.py that writes the user code first
            bundler_script = f'''
import os
from pathlib import Path

# --- User Task Injection ---
USER_TASK_CODE = {json.dumps(user_code)}

if USER_TASK_CODE:
    Path("user_task.py").write_text(USER_TASK_CODE, encoding="utf-8")

# --- Worker Runtime Injection ---
{runner_code}
'''
            return bundler_script
            
        except Exception as e:
            logger.error(f"Failed to bundle payload: {e}")
            return user_code

    async def create_kernel(self, title: str, code: str, hardware: str) -> str:
        """Create a new Kaggle kernel with specified hardware."""
        if not self.api:
            raise Exception("API not available")
        
        # Validate hardware is available
        resources = await self.get_hardware_types()
        if resources and 'available_types' in resources:
            if hardware not in resources['available_types']:
                raise ValueError(f"Hardware '{hardware}' not available. Available: {resources['available_types']}")
        
        slug = f"{self.username}/{title.lower().replace(' ', '-')}"
        kernel_dir = Path(".nyx/kernels") / title
        kernel_dir.mkdir(parents=True, exist_ok=True)
        
        # Bundle Logic
        final_payload = self._bundle_payload(code)
        
        (kernel_dir / "main.py").write_text(final_payload, encoding='utf-8')
        metadata = {
            "id": slug,
            "title": title,
            "code_file": "main.py",
            "language": "python",
            "kernel_type": "script",
            "is_private": True,
            "enable_gpu": 'gpu' in hardware.lower(),  # Dynamic GPU detection
            "enable_internet": True # Agent needs internet
        }
        (kernel_dir / "kernel-metadata.json").write_text(json.dumps(metadata), encoding='utf-8')
        await asyncio.to_thread(self.api.kernels_push, str(kernel_dir))
        return slug
    
    async def update_kernel(self, slug: str, code: str, title: Optional[str] = None):
        kernel_name = slug.split("/")[-1]
        kernel_dir = Path(".nyx/kernels") / kernel_name
        kernel_dir.mkdir(parents=True, exist_ok=True)
        
        # Bundle Logic
        final_payload = self._bundle_payload(code)
        
        (kernel_dir / "main.py").write_text(final_payload, encoding='utf-8')
        await asyncio.to_thread(self.api.kernels_push, str(kernel_dir))
    
    async def get_hardware_types(self) -> Dict[str, Any]:
        """Fetch available hardware types from Kaggle API dynamically."""
        if not self.api:
            return {}
        
        try:
            # Get competition info which includes hardware metadata
            # Kaggle doesn't have a direct hardware list API, so we fetch from metadata
            competitions = await asyncio.to_thread(
                self.api.competitions_list,
                page=1,
                search=""
            )
            
            # Extract hardware types from active competitions and kernels
            hardware_types = set()
            
            # Get from recent kernels
            kernels = await asyncio.to_thread(
                self.api.kernels_list,
                page=1,
                page_size=20
            )
            
            for k in kernels:
                # Check kernel metadata for GPU/TPU info
                if hasattr(k, 'enableGpu') and k.enableGpu:
                    hardware_types.add('gpu')
                if hasattr(k, 'enableTpu') and k.enableTpu:
                    hardware_types.add('tpu')
                if hasattr(k, 'enableInternet'):
                    hardware_types.add('cpu')
            
            # Return dynamic hardware mapping
            return {
                "available_types": list(hardware_types),
                "source": "kaggle_api",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch hardware types: {e}")
            return {"available_types": [], "error": str(e)}
    
    async def get_quotas(self) -> Dict[str, Any]:
        """Fetch current quota limits from Kaggle API dynamically."""
        if not self.api:
            return {}
        
        try:
            # Kaggle API doesn't expose quotas directly
            # We infer from active kernels and user metadata
            kernels = await asyncio.to_thread(
                self.api.kernels_list,
                mine=True,
                page_size=100
            )
            
            # Count active sessions by type
            active_gpu = 0
            active_tpu = 0
            active_cpu = 0
            
            for k in kernels:
                status = getattr(k, 'status', 'unknown')
                if status in ['running', 'queued']:
                    if hasattr(k, 'enableGpu') and k.enableGpu:
                        active_gpu += 1
                    elif hasattr(k, 'enableTpu') and k.enableTpu:
                        active_tpu += 1
                    else:
                        active_cpu += 1
            
            return {
                "gpu": {
                    "active": active_gpu,
                    "source": "real_time_api"
                },
                "tpu": {
                    "active": active_tpu,
                    "source": "real_time_api"
                },
                "cpu": {
                    "active": active_cpu,
                    "source": "real_time_api"
                },
                "timestamp": datetime.now().isoformat(),
                "note": "Live data from Kaggle API"
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch quotas: {e}")
            return {"error": str(e)}
    
    async def get_available_resources(self) -> Dict[str, Any]:
        """Get comprehensive resource availability from Kaggle API."""
        try:
            # Fetch everything dynamically
            hardware_types = await self.get_hardware_types()
            quotas = await self.get_quotas()
            active_kernels = await self.get_active_kernels()
            
            return {
                "hardware_types": hardware_types,
                "quotas": quotas,
                "active_kernels": {
                    "count": len(active_kernels),
                    "kernels": active_kernels
                },
                "source": "live_kaggle_api",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get resources: {e}")
            return {
                "error": str(e),
                "source": "api_error"
            }