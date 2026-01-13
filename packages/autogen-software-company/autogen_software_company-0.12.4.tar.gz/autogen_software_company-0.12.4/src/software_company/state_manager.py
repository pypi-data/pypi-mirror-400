import os
import json
from typing import Dict, Any, Optional

class StateManager:
    def __init__(self, task_id: str, state_directory: str):
        self.task_id = task_id
        self.state_directory = state_directory
        self.task_dir = os.path.join(self.state_directory, self.task_id)
        self.state_file = os.path.join(self.task_dir, f"task_{self.task_id}.json")
        self.state: Dict[str, Any] = {
            "current_step_index": 0,
            "context": {},
            "timeline": []
        }

        os.makedirs(self.task_dir, exist_ok=True)
        self.load_state()

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
                    if "timeline" not in self.state:
                        self.state["timeline"] = []
            except Exception as e:
                print(f"Error loading state from {self.state_file}: {e}. Starting fresh.")
                self.state = {"current_step_index": 0, "context": {}, "timeline": []}

    def save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def write_context_to_file(self, step_index: int, step_name: str, key: str, content: str) -> str:
        """Writes context content to a formatted MD file inside task directory and returns the relative path."""
        safe_step_name = step_name.lower().replace(" ", "_")
        filename = f"step_{step_index}_{safe_step_name}_{key}.md"
        filepath = os.path.join(self.task_dir, filename)

        # Check if content is JSON and wrap it in a code block if so
        formatted_content = content
        try:
            parsed = json.loads(content)
            if isinstance(parsed, (dict, list)):
                formatted_content = f"```json\n{content}\n```"
        except (json.JSONDecodeError, TypeError):
            pass

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_content)

        return filepath

    def read_context_from_file(self, path: str) -> str:
        """Reads context content from a file."""
        if not os.path.isabs(path):
            if os.path.exists(path):
                target_path = path
            elif os.path.exists(os.path.join(self.task_dir, os.path.basename(path))):
                # Try task directory
                target_path = os.path.join(self.task_dir, os.path.basename(path))
            elif os.path.exists(os.path.join(self.state_directory, os.path.basename(path))):
                # Fallback to state directory (backward compatibility)
                target_path = os.path.join(self.state_directory, os.path.basename(path))
            else:
                return f"[Error: Context file {path} not found]"
        else:
             target_path = path

        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"[Error reading context file: {e}]"

    def get_context(self, key: str) -> Any:
        return self.state["context"].get(key)

    def set_context(self, key: str, value: Any):
        self.state["context"][key] = value

    def remove_context(self, key: str):
        if key in self.state["context"]:
            del self.state["context"][key]

    def get_current_step_index(self) -> int:
        return self.state["current_step_index"]

    def set_current_step_index(self, index: int):
        self.state["current_step_index"] = index

    def delete_file(self, filepath: str) -> bool:
        """Deletes a file if it exists. Returns True if deleted, False otherwise."""
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    def add_timeline_entry(self, entry: Dict[str, Any]):
        """Adds an entry to the execution timeline."""
        if "timeline" not in self.state:
            self.state["timeline"] = []
        self.state["timeline"].append(entry)

    def get_timeline(self) -> list:
        """Returns the execution timeline."""
        return self.state.get("timeline", [])
