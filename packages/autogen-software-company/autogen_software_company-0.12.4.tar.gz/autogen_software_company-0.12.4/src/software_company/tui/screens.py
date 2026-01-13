from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable, Button, Label
from textual.containers import Container, Vertical
from textual.binding import Binding
import os
import json
from datetime import datetime

class TaskSelectionScreen(Screen):
    """Screen for exploring and selecting existing tasks."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Cancel"),
    ]

    CSS = """
    TaskSelectionScreen {
        align: center middle;
    }

    #dialog {
        grid-size: 2;
        grid-gutter: 1 2;
        grid-rows: 1fr 3;
        padding: 0 1;
        width: 80%;
        height: 80%;
        border: thick $background 80%;
        background: $surface;
    }

    #task-table {
        height: 1fr;
        border: solid #89b4fa;
    }
    
    #title-label {
        text-style: bold;
        color: #cba6f7;
        margin-bottom: 1;
        text-align: center;
    }
    """

    def __init__(self, state_directory: str, **kwargs):
        super().__init__(**kwargs)
        self.state_directory = state_directory
        self.selected_task_id = None

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Select a Task to Resume", id="title-label")
            yield DataTable(id="task-table", cursor_type="row")
            yield Button("Cancel", variant="error", id="cancel-btn")

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("Task ID", "Status", "Last Updated", "Description")
        self.load_tasks()

    def load_tasks(self):
        table = self.query_one(DataTable)
        table.clear()

        if not os.path.exists(self.state_directory):
            return

        tasks = []
        try:
            items = os.listdir(self.state_directory)
        except OSError:
            return

        for item in items:
            item_path = os.path.join(self.state_directory, item)
            if os.path.isdir(item_path):
                task_id = item
                state_file_path = os.path.join(item_path, f"task_{task_id}.json")

                if os.path.exists(state_file_path):
                    try:
                        mtime = os.path.getmtime(state_file_path)
                        last_updated = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')

                        with open(state_file_path, 'r') as f:
                            state = json.load(f)

                        context = state.get("context", {})
                        user_request = context.get("user_request", "No description.")
                        if isinstance(user_request, dict):
                            description = "[File Reference]"
                        else:
                            description = str(user_request).replace('\n', ' ')
                            if len(description) > 60:
                                description = description[:57] + "..."

                        timeline = state.get("timeline", [])
                        status = "Pending"
                        if timeline:
                            last_entry = timeline[-1]
                            if last_entry.get("status") == "FAILED":
                                status = "Failed"
                            elif last_entry.get("status") == "COMPLETED":
                                # Check if it was the last step
                                status = "In Progress" # Simplified logic

                        tasks.append({
                            "id": task_id,
                            "status": status,
                            "description": description,
                            "last_updated": last_updated,
                            "mtime": mtime
                        })
                    except:
                        continue

        tasks.sort(key=lambda x: x["mtime"], reverse=True)

        for task in tasks:
            table.add_row(
                task["id"], 
                task["status"], 
                task["last_updated"], 
                task["description"],
                key=task["id"] # Use ID as row key
            )
        
        table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        self.selected_task_id = event.row_key.value
        self.dismiss(self.selected_task_id)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "cancel-btn":
            self.dismiss(None)
