"""
Code Inspector - Static Analysis for AI Workloads
Analyzes Python code to detect frameworks, workload types, and hardware needs.
"""
import ast
from typing import Dict, Any, Set
from .schemas import WorkloadType


class Inspector:
    """
    Static analyzer for AI workload classification.
    
    Detects:
    - Deep learning frameworks
    - Workload type (training vs inference)
    - Imported libraries
    
    Provides metadata for LLM-based hardware selection decisions.
    """
    
    # Deep Learning Framework Detection
    DL_FRAMEWORKS: Set[str] = {
        'torch', 'pytorch', 'tensorflow', 'tf', 'jax', 'flax',
        'diffusers', 'transformers', 'accelerate', 'bitsandbytes',
        'stable_baselines3', 'keras', 'mxnet', 'paddlepaddle',
        'onnx', 'onnxruntime', 'tvm', 'openvino'
    }
    
    # Training Indicators
    TRAINING_KEYWORDS: Set[str] = {
        'train', 'training', 'fit', 'fine-tune', 'finetune',
        'backprop', 'optimizer', 'loss.backward', 'gradient',
        'epoch', 'batch_size', 'learning_rate', 'model.train()'
    }
    
    # Data Processing Libraries
    DATA_LIBS: Set[str] = {
        'pandas', 'numpy', 'polars', 'dask', 'vaex',
        'modin', 'ray', 'spark', 'pyspark'
    }
    
    @staticmethod
    def analyze(code: str, filename: str) -> Dict[str, Any]:
        """
        Analyze Python code and extract features.
        
        Args:
            code: Python source code to analyze
            filename: Name of the file (for context)
            
        Returns:
            dict with keys:
                - imports: List of imported modules
                - frameworks: List of detected DL frameworks
                - deep_learning: Boolean indicating DL code
                - workload_type: Classification of workload
                - confidence: Confidence score (0-1)
        """
        features = {
            "workload_type": WorkloadType.UNKNOWN.value,
            "imports": [],
            "frameworks": [],
            "deep_learning": False,
            "confidence": 0.0
        }

        # Extract imports via AST
        try:
            tree = ast.parse(code)
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(n.name.split('.')[0] for n in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split('.')[0])
            
            features["imports"] = sorted(imports)
            
            # Detect DL frameworks
            detected_frameworks = imports & Inspector.DL_FRAMEWORKS
            features["frameworks"] = sorted(detected_frameworks)
            
            if detected_frameworks:
                features["deep_learning"] = True
                features["workload_type"] = WorkloadType.INFERENCE.value
                features["confidence"] = 0.7
                
        except (SyntaxError, Exception):
            # Code may be incomplete or have errors
            pass

        # Detect training workload
        code_lower = code.lower()
        training_signals = sum(1 for kw in Inspector.TRAINING_KEYWORDS if kw in code_lower)
        
        if training_signals >= 2:
            features["workload_type"] = WorkloadType.TRAINING.value
            features["confidence"] = min(0.9, 0.5 + training_signals * 0.1)
            
        # Detect data processing patterns
        data_libs_detected = imports & Inspector.DATA_LIBS
        if data_libs_detected and not features["deep_learning"]:
            features["workload_type"] = WorkloadType.DATA_PROC.value
            features["confidence"] = 0.6

        # Add detected data libraries to imports for visibility
        if data_libs_detected:
            features["data_processing_libs"] = sorted(data_libs_detected)

        return features
