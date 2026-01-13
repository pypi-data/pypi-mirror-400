import json
import os
from typing import Dict, Any

DEFAULT_CONFIG_FILENAME = "default_config.json"
USER_CONFIG_FILENAME = "config.json"

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Loads configuration.
    1. If config_path is provided, load it.
    2. Else, try loading 'config.json' from current working directory.
    3. Fallback to 'default_config.json' in the package directory.
    """
    # 1. Explicit path provided via CLI
    if config_path:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    print(f"Loading configuration from {config_path}...")
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {config_path}: {e}. Aborting.")
                raise # Explicit path failure should probably raise error
        else:
            print(f"Error: Config file '{config_path}' not found.")
            raise FileNotFoundError(f"Config file '{config_path}' not found.")

    # 2. Try loading user config from CWD
    if os.path.exists(USER_CONFIG_FILENAME):
        try:
            with open(USER_CONFIG_FILENAME, 'r') as f:
                print(f"Loading configuration from {USER_CONFIG_FILENAME} (CWD)...")
                return json.load(f)
        except Exception as e:
            print(f"Error loading {USER_CONFIG_FILENAME} from CWD: {e}. Falling back to default.")

    # 3. Load default config from package
    package_dir = os.path.dirname(__file__)
    default_config_path = os.path.join(package_dir, DEFAULT_CONFIG_FILENAME)
    print(f"Loading default config from {default_config_path}...")
    
    if os.path.exists(default_config_path):
        with open(default_config_path, 'r') as f:
            return json.load(f)
    
    # 4. Fallback hardcoded (should not happen if installed correctly)
    return {
        "state_directory": "workflow_states",
        "default_tool": "gemini",
        "sandbox": {
            "enabled": False,
            "image": "python:3.11-slim",
            "mount_path": "/workspace"
        },
        "steps": []
    }
