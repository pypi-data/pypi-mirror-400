#!/usr/bin/env python3
"""
Nyx CLI - AI Workload Orchestrator for Kaggle
Main entry point for all CLI operations.
"""
import sys
import asyncio
import os
import json
import argparse
import subprocess
from pathlib import Path

# Ensure imports work from any context
PROJECT_ROOT = Path(__file__).parent
# Check if we can import the package directly (installed mode)
try:
    import nyx_kaggle_manager
except ImportError:
    # Development mode or direct script execution: add parent directory to path
    # This allows 'import nyx_kaggle_manager' to resolve to the source directory
    sys.path.insert(0, str(PROJECT_ROOT.parent))

try:
    from nyx_kaggle_manager.lib.utils import load_config, logger, save_json, NYX_DATA_DIR
    from nyx_kaggle_manager.lib.inspector import Inspector
    
    try:
        from nyx_kaggle_manager.local.scheduler import Scheduler
        _SCHEDULER_IMPORT_ERROR = None
    except ImportError as e:
        Scheduler = None
        _SCHEDULER_IMPORT_ERROR = str(e)
except ImportError as e:
    # If absolute imports fail, we might be in a very strange environment.
    # But let's fallback to relative imports just in case (e.g. built as single zip)
    # This restores previous behavior as a last resort
    try:
        from lib.utils import load_config, logger, save_json, NYX_DATA_DIR
        from lib.inspector import Inspector
        from local.scheduler import Scheduler
        _SCHEDULER_IMPORT_ERROR = None
    except ImportError as e2:
        print(f"Critical Error: Failed to import Nyx modules. \nTrace 1: {e}\nTrace 2: {e2}")
        sys.exit(1)


# CLI COMMAND REGISTRY
COMMANDS = {
    "init": {"description": "Initialize configuration and start orchestrator", "category": "Setup"},
    "kaggle": {"description": "Wrapper for official Kaggle CLI (passes all args)", "category": "Management"},
    "run": {"description": "Submit a script for execution on Kaggle", "category": "Management"},
    "ps": {"description": "List active workers and queued tasks", "category": "Management"},
    "ssh": {"description": "Connect to remote infrastructure via SSH", "category": "Management"},
    "inspect": {"description": "Analyze a local file for hardware requirements", "category": "Analysis"},
    "sync": {"description": "Sync local context with remote API", "category": "Analysis"},
    "terminal": {"description": "Launch Warp Terminal in current directory", "category": "Setup"},
    "resources": {"description": "List available hardware resources", "category": "Analysis"}
}


def format_help():
    """Generate formatted help text."""
    header = "\nNyx CLI (v4.0.5) - AI Workload Orchestrator\nUsage: nyxcli <command> [arguments]\n"
    categories = {}
    
    for cmd, details in COMMANDS.items():
        cat = details["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(f"  {cmd:<13} {details['description']}")
    
    body = ""
    for cat, lines in categories.items():
        body += f"\n{cat}:\n" + "\n".join(lines) + "\n"
    
    body += "\nFlags:\n  --help        Show this help message\n"
    return header + body


async def handle_inspect(args):
    """Analyze a local file."""
    if not args.file:
        print("Missing file path. Usage: nyxcli inspect <file>")
        return
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    code = file_path.read_text(encoding='utf-8')
    inspector = Inspector()
    analysis = inspector.analyze(code, file_path.name)
    
    print(f"\nAnalysis Results for {file_path.name}")
    print("=" * 50)
    print(f"Workload Type: {analysis['workload_type']}")
    print(f"Deep Learning: {'Yes' if analysis['deep_learning'] else 'No'}")
    print(f"Confidence: {analysis['confidence']:.1%}")
    print(f"Frameworks: {', '.join(analysis['frameworks']) if analysis['frameworks'] else 'None'}")


async def handle_kaggle(kaggle_args):
    """Wrapper for Kaggle CLI."""
    cmd_str = f"kaggle {' '.join(kaggle_args)}"
    print(f"🔌  Nyx Wrapper: {cmd_str}")
    
    try:
        # We inherit stdout/stderr/stdin to provide full interactive experience
        # This allows things like progress bars and color output to work naturally
        process = await asyncio.create_subprocess_exec(
            "kaggle", *kaggle_args
        )
        await process.wait()
        
    except FileNotFoundError:
        print("Error: 'kaggle' command not found. Please install it: pip install kaggle")
    except Exception as e:
        print(f"Error executing kaggle command: {e}")


async def handle_run(args, config):
    """Submit a script."""
    if not args.file:
        print("Missing file path. Usage: nyxcli run <file>")
        return
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    if not Scheduler:
        print("Scheduler module not available")
        return
    
    scheduler = Scheduler(config)
    code = file_path.read_text(encoding='utf-8')
    
    # Fetch available hardware dynamically from API
    if not args.hardware:
        print("Fetching available hardware from Kaggle API...")
        try:
            import asyncio
            resources = asyncio.run(scheduler.kaggle.get_hardware_types())
            if resources and 'available_types' in resources:
                available = resources['available_types']
                print(f"Available hardware: {', '.join(available)}")
                hardware = available[0] if available else None
            else:
                print("Warning: Could not fetch hardware types from API")
                hardware = None
        except Exception as e:
            print(f"Error fetching hardware: {e}")
            hardware = None
        
        if not hardware:
            print("Error: No hardware specified and could not fetch from API")
            return
    else:
        hardware = args.hardware
    
    task_id = scheduler.submit_task(
        filename=file_path.name,
        code=code,
        hardware_choice=hardware,
        priority=args.priority or 1
    )
    
    print(f"Task submitted: {task_id}")
    print(f"File: {file_path.name}")
    print(f"Hardware: {hardware}")


async def handle_ps(config):
    """List status."""
    if not Scheduler:
        print("Scheduler module not available")
        return
    
    scheduler = Scheduler(config)
    status = scheduler.get_status_summary()
    
    print("\nNyx System Status")
    print("=" * 50)
    print(f"Scheduler: {status['scheduler_status']}")
    print(f"Tasks Pending: {status['tasks_pending']}")
    print(f"Tasks Active: {status['tasks_active']}")
    print(f"Workers: {status['workers_ready']}/{status['workers_total']}")


async def handle_init(config_arg=None):
    """Initialize configuration and start system."""
    config_dir = NYX_DATA_DIR
    config_file = config_dir / "config.yaml"
    
    if not config_file.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / "logs").mkdir(exist_ok=True)
        (config_dir / "kernels").mkdir(exist_ok=True)
        
        default_config = {
            "project_name": "Nyx-Kaggle-Manager",
            "version": "4.0.0",
            "system": {
                "home_dir": ".nyx",
                "logs_dir": "logs",
                "kernels_dir": "kernels",
                "state_file": "state.json"
            },
            "kaggle": {
                "username": "${KAGGLE_USERNAME}",
                "dataset_slug": "nyx-communication-hub"
            },
            "orchestrator": {
                "max_workers": 5, 
                "check_interval": 10
            }
        }
        
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        print(f"Configuration initialized at {config_file}")
    else:
        print("Configuration already exists.")

    # Start the daemon
    print("Starting system...")
    
    # Reload config to ensure we have latest (if just created)
    config = load_config(str(config_file)) if not config_arg else config_arg
    await handle_start(config)


async def handle_start(config):
    """Start the scheduler daemon."""
    if not Scheduler:
        print("Scheduler not available")
        if _SCHEDULER_IMPORT_ERROR:
             print(f"Reason: {_SCHEDULER_IMPORT_ERROR}")
        return

    scheduler = Scheduler(config)
    await scheduler.start()


class ShellParser(argparse.ArgumentParser):
    """ArgumentParser that doesn't exit on error."""
    def exit(self, status=0, message=None):
        if message:
            print(message)
        # raise ValueError(message) 
        # No longer used since handle_cli loop is gone, but keeping just in case needed elsewhere or remove.
        pass
    def error(self, message):
         print(f"Error: {message}")
         # raise ValueError(message)
         pass


async def handle_terminal(config):
    """Launch Warp Terminal in the current directory."""
    
    # Try to locate Warp on Windows common paths
    import shutil
    warp_cmd = "warp"
    
    # Check if 'warp' is in PATH
    if shutil.which("warp"):
         # Ideally we want to prevent the Python window from staying open if double clicked, 
         # but here we are in a CLI.
         # subprocess.run/Popen with shell=True is okay.
         # For Warp on Windows, 'warp-terminal'? 'warp.exe'?
         # Usually 'warp .' works if added to path.
         pass
    else:
        # Check standard installation paths
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        program_files = os.environ.get("ProgramFiles", "")
        
        possible_paths = [
            Path(local_app_data) / "Programs" / "Warp" / "Warp.exe",
            Path(local_app_data) / "Microsoft" / "WinGet" / "Links" / "warp.exe",
            Path(program_files) / "Warp" / "Warp.exe"
        ]
        
        for path in possible_paths:
            if path.exists():
                warp_cmd = str(path)
                break
        else:
            print("❌ Error: Warp Terminal not found.")
            print("Locations checked:")
            for p in possible_paths:
                print(f" - {p}")
            print("\nPlease install Warp Terminal from https://www.warp.dev/ or add it to your PATH.")
            print("Alternatively, you can use 'nyxcli init' to configure a custom terminal path (feature coming soon).")
            sys.exit(1)

    print(f"🚀 Launching Warp Terminal ({warp_cmd})...")
    try:
        # Launch Warp (attempts to inherit current working directory)
        subprocess.Popen(f'"{warp_cmd}"', shell=True, cwd=os.getcwd())
        print("✅ Warp launched.")
    except Exception as e:
        print(f"❌ Failed to launch Warp: {e}")

async def handle_interactive_shell(config):
    """Deprecated: Internal interactive shell was removed by request."""
    print("❌ Interactive shell is deprecated. Using 'terminal' now launches Warp Terminal exclusively.")
    sys.exit(1)


async def main():
    """Main entry point."""
    # Intercept 'kaggle' command to act as a raw wrapper
    if len(sys.argv) > 1 and sys.argv[1] == "kaggle":
        await handle_kaggle(sys.argv[2:])
        return

    parser = argparse.ArgumentParser(description="Nyx - AI Workload Orchestrator", add_help=False)
    parser.add_argument("command", nargs='?')
    parser.add_argument("file", nargs='?')
    parser.add_argument("--hardware", help="Hardware type (fetched dynamically from Kaggle API if not specified)")
    parser.add_argument("--priority", type=int, default=1)
    parser.add_argument("--help", action="store_true")
    
    args = parser.parse_args()
    
    if args.help or not args.command:
        print(format_help())
        return
    
    config = load_config(str(NYX_DATA_DIR / "config.yaml"))
    
    try:
        if args.command == "init":
            await handle_init(config)
        elif args.command == "inspect":
            await handle_inspect(args)
        elif args.command == "run":
            await handle_run(args, config)
        elif args.command == "ps":
            await handle_ps(config)
        elif args.command == "terminal":
            await handle_terminal(config)
        # start command is removed/merged but logic remains for internal use if needed, 
        # or handle_start is reused by init only. 
        # But if user types 'start' (old habit), we can just alias it to handle_start or remove it.
        # Since I removed it from COMMANDS, it will hit "Unknown command" if typed, which is fine per request.
        else:
            print(f"Unknown command: {args.command}")
            print(format_help())
    except KeyboardInterrupt:
        print("\nCancelled")
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

def main_entry_point():
    """Entry point for setuptools console_scripts."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Fatal Error: {e}")
        sys.exit(1)
