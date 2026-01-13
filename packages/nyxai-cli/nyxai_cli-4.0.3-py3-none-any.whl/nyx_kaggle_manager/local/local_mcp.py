"""
Local MCP Server - Nyx-Specific Tools for Warp/Claude Integration
Provides tools for file analysis, task submission, and system monitoring.
"""
import json
import sys
import os
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from lib.utils import load_config, logger
from lib.inspector import Inspector

try:
    from .scheduler import Scheduler
except ImportError:
    logger.warning("Scheduler module could not be imported. Task submission may fail.")
    Scheduler = None


class LocalNyxMcp:
    """
    Minimal MCP server for Nyx-specific operations.
    Implements JSON-RPC 2.0 protocol for tool invocation.
    
    Available Tools:
    - nyx_analyze_file: Static code analysis for hardware requirements
    - nyx_get_resources: Get available Kaggle hardware and quota
    - nyx_submit_task: Submit task to orchestrator
    - nyx_status: Get real-time system status
    """
    
    def __init__(self):
        """Initialize MCP server with scheduler."""
        # Change to project root
        os.chdir(PROJECT_ROOT)
        
        # Load configuration
        from lib.utils import NYX_DATA_DIR
        config_path = NYX_DATA_DIR / "config.yaml"
        self.config = load_config(str(config_path))
        
        # Initialize inspector
        self.inspector = Inspector()
        
        # Initialize scheduler if available
        if Scheduler:
            self.scheduler = Scheduler(self.config)
        else:
            self.scheduler = None
        
        logger.info("Local MCP server initialized")
    
    def process_message(self, line: str):
        """
        Process incoming JSON-RPC 2.0 message.
        
        Args:
            line: JSON-RPC formatted message string
        """
        msg = None
        try:
            msg = json.loads(line)
            
            # Basic JSON-RPC 2.0 handling
            if msg.get("method") == "tools/list":
                self.send_response(msg["id"], {
                    "tools": [
                        {
                            "name": "nyx_analyze_file",
                            "description": "Analyze a local file for AI hardware requirements (GPU VRAM, frameworks)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "path": {"type": "string", "description": "Absolute path to the Python file"}
                                },
                                "required": ["path"]
                            }
                        },
                        {
                            "name": "nyx_get_resources",
                            "description": "Get list of available Kaggle Accelerator Types and current availability",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        {
                            "name": "nyx_submit_task",
                            "description": "Submit a file to the Nyx Orchestrator for execution on Kaggle",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "path": {"type": "string", "description": "Path to the Python script"},
                                    "priority": {"type": "integer", "description": "Priority level (default: 1)"},
                                    "hardware": {
                                        "type": "string",
                                        "description": "Selected hardware accelerator (fetched dynamically from Kaggle API)"
                                    },
                                    "reasoning": {"type": "string", "description": "Reason for hardware choice"}
                                },
                                "required": ["path", "hardware", "reasoning"]
                            }
                        },
                        {
                            "name": "nyx_status",
                            "description": "Get current status of Nyx workers, queue, and active tasks",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        }
                    ]
                })
            
            elif msg.get("method") == "tools/call":
                params = msg.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "nyx_analyze_file":
                    result = self.handle_analyze(arguments)
                    self.send_response(msg["id"], result)
                
                elif tool_name == "nyx_get_resources":
                    result = self.handle_get_resources()
                    self.send_response(msg["id"], result)
                
                elif tool_name == "nyx_submit_task":
                    result = self.handle_submit_task(arguments)
                    self.send_response(msg["id"], result)
                
                elif tool_name == "nyx_status":
                    result = self.handle_status()
                    self.send_response(msg["id"], result)
                
                else:
                    self.send_error(msg["id"], -32601, f"Unknown tool: {tool_name}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            self.send_error(None, -32700, "Parse error")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            req_id = msg.get("id") if msg else None
            self.send_error(req_id, -32603, str(e))
    
    def handle_analyze(self, args: Dict) -> Dict:
        """Handle file analysis request."""
        try:
            path = args.get("path")
            if not path:
                return {"error": "Missing parameter"}
            
            path_obj = Path(path)
            if not path_obj.exists():
                return {"error": f"File not found: {path}"}
            
            # Read file content
            code = path_obj.read_text(encoding="utf-8")
            
            # Analyze
            analysis = self.inspector.analyze(code, path_obj.name)
            
            # Add hardware recommendations
            hardware_recs = self._generate_hardware_recommendations(analysis)
            
            return {
                "success": True,
                "analysis": analysis,
                "recommendations": hardware_recs
            }
        
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return {"error": str(e)}
    
    def handle_get_resources(self) -> Dict:
        """Handle resource availability request."""
        try:
            if not self.scheduler:
                return {"error": "Scheduler not available"}
            
            # Get resources from Kaggle adapter
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            resources = loop.run_until_complete(
                self.scheduler.kaggle.get_available_resources()
            )
            loop.close()
            
            return {
                "success": True,
                "resources": resources
            }
        
        except Exception as e:
            logger.error(f"Resource query error: {e}")
            return {"error": str(e)}
    
    def handle_submit_task(self, args: Dict) -> Dict:
        """Handle task submission request."""
        try:
            if not self.scheduler:
                return {"error": "Scheduler not available"}
            
            path = args.get("path")
            hardware = args.get("hardware")
            reasoning = args.get("reasoning", "User specified")
            priority = args.get("priority", 1)
            
            if not path or not hardware:
                return {"error": "Missing required parameters: path, hardware"}
            
            path_obj = Path(path)
            if not path_obj.exists():
                return {"error": f"File not found: {path}"}
            
            # Read code
            code = path_obj.read_text(encoding="utf-8")
            
            # Submit task
            task_id = self.scheduler.submit_task(
                filename=path_obj.name,
                code=code,
                hardware_choice=hardware,
                priority=priority
            )
            
            return {
                "success": True,
                "task_id": task_id,
                "message": f"Task submitted successfully with ID: {task_id}"
            }
        
        except Exception as e:
            logger.error(f"Task submission error: {e}")
            return {"error": str(e)}
    
    def handle_status(self) -> Dict:
        """Handle status query request."""
        try:
            if not self.scheduler:
                return {"error": "Scheduler not available"}
            
            status = self.scheduler.get_status_summary()
            
            return {
                "success": True,
                "status": status
            }
        
        except Exception as e:
            logger.error(f"Status query error: {e}")
            return {"error": str(e)}
    
    def _generate_hardware_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate hardware recommendations dynamically based on available resources from Kaggle API."""
        recommendations = []
        
        try:
            # Fetch available hardware types dynamically from API
            if not self.scheduler:
                return recommendations
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            resources = loop.run_until_complete(
                self.scheduler.kaggle.get_hardware_types()
            )
            loop.close()
            
            if not resources or 'available_types' not in resources:
                logger.warning("No hardware types available from API")
                return recommendations
            
            available_hardware = resources['available_types']
            frameworks = analysis.get("frameworks", [])
            workload = analysis.get("workload_type", "unknown")
            is_deep_learning = analysis.get("deep_learning", False)
            
            # Generate recommendations based on workload and available hardware
            for hw in available_hardware:
                hw_lower = hw.lower()
                
                # CPU for non-deep learning
                if not is_deep_learning and 'cpu' in hw_lower:
                    recommendations.append({
                        "hardware": hw,
                        "reason": "No deep learning frameworks detected. CPU sufficient.",
                        "confidence": "high"
                    })
                
                # GPU for inference
                if is_deep_learning and workload == "inference" and 'gpu' in hw_lower:
                    recommendations.append({
                        "hardware": hw,
                        "reason": f"Inference workload with {', '.join(frameworks)}. GPU recommended.",
                        "confidence": "high"
                    })
                
                # Powerful GPU for training
                if workload == "training" and 'gpu' in hw_lower:
                    recommendations.append({
                        "hardware": hw,
                        "reason": "Training workload detected. High-performance GPU recommended.",
                        "confidence": "medium"
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate dynamic recommendations: {e}")
            return recommendations
    
    def send_response(self, req_id: Any, result: Any):
        """Send JSON-RPC success response."""
        response = {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": result
        }
        print(json.dumps(response), flush=True)
    
    def send_error(self, req_id: Any, code: int, message: str):
        """Send JSON-RPC error response."""
        response = {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        print(json.dumps(response), flush=True)
    
    def run(self):
        """Main loop - read from stdin and process messages."""
        logger.info("MCP server started. Listening on stdin...")
        
        try:
            for line in sys.stdin:
                line = line.strip()
                if line:
                    self.process_message(line)
        except KeyboardInterrupt:
            logger.info("MCP server stopped by user")
        except Exception as e:
            logger.error(f"Fatal error in MCP server: {e}")


def main():
    """Entry point for MCP server."""
    server = LocalNyxMcp()
    server.run()


if __name__ == "__main__":
    main()
