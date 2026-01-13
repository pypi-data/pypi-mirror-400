import os
import json
import time
from datetime import datetime
from typing import List

def list_tools(tool_names: List[str]):
    """Lists available tool wrappers."""
    print("Available Tools:")
    for tool in tool_names:
        print(f"  - {tool}")

def list_tasks(state_directory: str):
    """Lists tasks in the state directory."""
    if not os.path.exists(state_directory):
        print(f"State directory '{state_directory}' does not exist.")
        return

    tasks = []

    try:
        items = os.listdir(state_directory)
    except OSError as e:
        print(f"Error accessing state directory: {e}")
        return

    for item in items:
        item_path = os.path.join(state_directory, item)
        if os.path.isdir(item_path):
            task_id = item
            state_file_name = f"task_{task_id}.json"
            state_file_path = os.path.join(item_path, state_file_name)

            if os.path.exists(state_file_path):
                try:
                    # Get modification time
                    mtime = os.path.getmtime(state_file_path)
                    last_updated = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')

                    with open(state_file_path, 'r') as f:
                        state = json.load(f)

                    context = state.get("context", {})
                    user_request = context.get("user_request", "No description provided.")

                    # Handle if user_request is a file reference (unlikely but possible)
                    if isinstance(user_request, dict) and user_request.get("type") == "file":
                         # We don't want to read the file here, just show a placeholder
                         description = f"[File: {user_request.get('path')}]"
                    else:
                        description = str(user_request).replace('\n', ' ')

                    if len(description) > 50:
                        description = description[:47] + "..."

                    timeline = state.get("timeline", [])
                    status = "Pending"
                    if timeline:
                        last_entry = timeline[-1]
                        if last_entry.get("status") == "FAILED":
                            status = "Failed"
                        else:
                            status = "In Progress"

                    tasks.append({
                        "id": task_id,
                        "status": status,
                        "description": description,
                        "last_updated": last_updated,
                        "mtime": mtime
                    })

                except Exception:
                    # Skip malformed tasks
                    continue

    if not tasks:
        print("No previous tasks found.")
        return

    # Sort by last updated (descending)
    tasks.sort(key=lambda x: x["mtime"], reverse=True)

    headers = ["Task ID", "Status", "Last Updated", "Description"]
    widths = [len(h) for h in headers]

    for task in tasks:
        widths[0] = max(widths[0], len(task["id"]))
        widths[1] = max(widths[1], len(task["status"]))
        widths[2] = max(widths[2], len(task["last_updated"]))
        widths[3] = max(widths[3], len(task["description"]))

    fmt = f"{{:<{widths[0]}}}  {{:<{widths[1]}}}  {{:<{widths[2]}}}  {{:<{widths[3]}}}"

    print(fmt.format(*headers))
    print("-" * (sum(widths) + 6))

    for task in tasks:
        print(fmt.format(task["id"], task["status"], task["last_updated"], task["description"]))
