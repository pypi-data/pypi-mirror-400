from textual.widgets import Static, Header, Label, Button, ListView, ListItem
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.message import Message
from rich.text import Text
import os
import json
from datetime import datetime


class TaskControlHeader(Static):
    """Custom header with a stylized logo."""
    
    def compose(self) -> ComposeResult:
        logo_text = Text(" ⚡ AUTO-SOFTWARE-CO ", style="bold italic #89b4fa on #181825")
        yield Label(logo_text, id="header-logo")
        yield Header(show_clock=True, id="main-header")


class TaskCard(Static):
    """Card widget for displaying task information."""
    
    class Selected(Message):
        """Posted when user selects a task."""
        def __init__(self, task_id: str):
            self.task_id = task_id
            super().__init__()
    
    class DeleteRequested(Message):
        """Posted when user requests to delete a task."""
        def __init__(self, task_id: str):
            self.task_id = task_id
            super().__init__()
    
    task_id = reactive("")
    status = reactive("Pending")
    current_step = reactive("Start")
    timestamp = reactive("")
    
    def __init__(self, task_id: str, status: str, current_step: str, timestamp: str, **kwargs):
        super().__init__(**kwargs)
        self.task_id = task_id
        self.status = status
        self.current_step = current_step
        self.timestamp = timestamp
        
        # Determine icon based on status
        if status == "Failed":
            self.icon = "❌"
        elif status == "Done":
            self.icon = "✔"
        else:
            self.icon = "⏳"
    
    def compose(self) -> ComposeResult:
        with Vertical(classes="task-card-container"):
            with Horizontal(classes="task-card-header"):
                yield Label(f"{self.icon} {self.task_id}", classes="task-card-title")
                delete_btn = Button("🗑", id=f"delete-task-{self.task_id}", classes="icon-btn delete-btn", variant="primary")
                yield delete_btn
            
            with Vertical(classes="task-card-body"):
                yield Label(f"Step: {self.current_step}", classes="task-card-info")
                yield Label(f"Time: {self.timestamp}", classes="task-card-info")
    
    def on_click(self):
        """Handle card click."""
        self.post_message(self.Selected(self.task_id))


class TaskExplorerSidebar(Static):
    """Sidebar widget to display tasks as cards."""
    
    class Selected(Message):
        def __init__(self, task_id: str):
            self.task_id = task_id
            super().__init__()
    
    class DeleteRequested(Message):
        """Posted when user requests to delete a task."""
        def __init__(self, task_id: str):
            self.task_id = task_id
            super().__init__()

    def __init__(self, state_directory: str, **kwargs):
        super().__init__(**kwargs)
        self.state_directory = state_directory
        self.tasks = []

    def compose(self) -> ComposeResult:
        yield Label("☰ PROJECT TASKS", classes="sidebar-header")
        yield VerticalScroll(id="task-cards-container")

    def on_mount(self):
        self.refresh_tasks()

    def refresh_tasks(self):
        container = self.query_one(VerticalScroll)
        container.remove_children()
        
        if not os.path.exists(self.state_directory):
            return

        tasks_data = []
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
                        with open(state_file_path, 'r') as f:
                            state = json.load(f)

                        timeline = state.get("timeline", [])
                        status = "Pending"
                        current_step = "Start"
                        
                        if timeline:
                            last = timeline[-1]
                            if last.get("status") == "FAILED":
                                status = "Failed"
                            elif last.get("status") == "COMPLETED":
                                status = "In Progress"
                            
                            current_step = last.get("step_name", "Unknown")

                        # Format timestamp
                        dt = datetime.fromtimestamp(mtime)
                        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")

                        tasks_data.append({
                            "id": task_id,
                            "status": status,
                            "current_step": current_step,
                            "timestamp": timestamp,
                            "mtime": mtime
                        })
                    except:
                        continue
        
        tasks_data.sort(key=lambda x: x["mtime"], reverse=True)

        for t in tasks_data:
            card = TaskCard(
                t['id'],
                t['status'],
                t['current_step'],
                t['timestamp'],
                id=f"task-card-{t['id']}",
                classes="task-card"
            )
            container.mount(card)

    def on_task_card_selected(self, message: TaskCard.Selected):
        """Handle task card selection."""
        self.post_message(self.Selected(message.task_id))
    
    def on_task_card_delete_requested(self, message: TaskCard.DeleteRequested):
        """Handle task deletion request."""
        self.post_message(self.DeleteRequested(message.task_id))


class StepCard(Static):
    """Card widget for displaying step information."""
    
    class RerunRequested(Message):
        """Posted when user requests to re-run a step."""
        def __init__(self, step_index: int):
            self.step_index = step_index
            super().__init__()
    
    role = reactive("")
    tool = reactive("Gemini")
    model = reactive("Default")
    status = reactive("Pending")
    duration = reactive("-")
    
    def __init__(self, step_index: int, step_data, **kwargs):
        super().__init__(**kwargs)
        self.step_index = step_index
        self.step_data = step_data
        self.role = step_data.name
        self.tool = step_data.tool or "Default"
        self.model = step_data.model or "Default"
        
        input_list = step_data.input_keys or []
        self.input_keys = ", ".join(input_list) if input_list else "None"
        
        output_list = step_data.output_keys or []
        self.output_keys = ", ".join(output_list) if output_list else "None"
        
        self.output_content_map = {}
        self.generated_files = []
        self.output_visible = False  # Track if output is expanded

    def compose(self) -> ComposeResult:
        with Horizontal(classes="step-header"):
            yield Label(f"{self.step_index + 1}. {self.role}", classes="step-title")
            yield Label(self.status, classes="step-status")
            rerun_btn = Button("🔄", id=f"rerun-btn-{self.step_index}", classes="icon-btn rerun-btn", variant="primary")
            yield rerun_btn
            # Toggle output button
            toggle_btn = Button("▼", id=f"toggle-output-{self.step_index}", classes="icon-btn toggle-btn", variant="primary")
            yield toggle_btn
        
        with Vertical(classes="step-body"):
            yield Label(f"Tool: {self.tool} ({self.model})", classes="step-meta")
            yield Label(f"In: {self.input_keys}", classes="step-io")
            yield Label(f"Out: {self.output_keys}", classes="step-io")
            yield Vertical(classes="file-list-container")
            # Output section (hidden by default)
            yield Vertical(id=f"output-section-{self.step_index}", classes="output-section hidden")
        
        with Horizontal(classes="step-footer"):
            yield Label("", classes="step-output-files")
            yield Label(f"{self.duration}", classes="step-time")

    def watch_status(self, val):
        if not self.is_mounted:
            return
        lbl = self.query_one(".step-status", Label)
        
        if val == "Running":
            lbl.update(f"🔄 Running")
            self.add_class("running")
        elif val == "Completed":
            lbl.update(f"✔ Done")
            self.remove_class("running")
            self.add_class("completed")
        elif val == "Failed":
            lbl.update(f"❌ Failed")
            self.add_class("failed")
        else:
            lbl.update(f"○ Pending")

    def watch_duration(self, val):
        if not self.is_mounted:
            return
        self.query_one(".step-time", Label).update(f"{val}")

    def set_output(self, output_dict):
        """Stores the full output dictionary."""
        self.output_content_map = {k: str(v) if not isinstance(v, str) else v for k, v in output_dict.items()}

    def set_files(self, files: list):
        """Populates the file list with copy buttons."""
        if not self.is_mounted:
            return
        
        self.generated_files = files
        container = self.query_one(".file-list-container", Vertical)
        container.remove_children()
        
        if files:
            for key, path in files:
                row = Horizontal(classes="file-row")
                filename = os.path.basename(path)
                label = Label(f"📄 {filename}", classes="file-path")
                btn_id = f"copy-btn-{self.step_index}-{key}"
                btn = Button("📋", id=btn_id, classes="icon-btn", variant="primary")
                btn.copy_key = key
                
                container.mount(row)
                row.mount(label)
                row.mount(btn)
        
        self._update_footer_files(files)

    def on_button_pressed(self, event: Button.Pressed):
        """Handle button clicks: copy, re-run, and toggle buttons."""
        # Handle toggle output button
        if event.button.id and event.button.id.startswith("toggle-output-"):
            self._toggle_output()
            return
        
        # Handle re-run button
        if event.button.id and event.button.id.startswith("rerun-btn-"):
            self.post_message(self.RerunRequested(self.step_index))
            self.app.notify(f"🔄 Re-running {self.role}...", timeout=2)
            return
        
        # Handle copy button clicks for step output
        if hasattr(event.button, "copy_key"):
            key = event.button.copy_key
            content = self.output_content_map.get(key)
            if content:
                try:
                    import pyperclip
                    pyperclip.copy(content)
                    self.app.notify(f"✓ Copied {key} to clipboard!", timeout=2)
                except Exception as e:
                    try:
                        self.app.copy_to_clipboard(content)
                        self.app.notify(f"✓ Copied {key} to clipboard!", timeout=2)
                    except Exception as e2:
                        self.app.notify(f"Failed to copy: {e2}", severity="warning", timeout=2)
            else:
                self.app.notify(f"No content for {key}", severity="warning", timeout=2)

    def _update_footer_files(self, files: list):
        """Update the footer label with output file paths."""
        if not self.is_mounted:
            return
        
        try:
            footer_label = self.query_one(".step-output-files", Label)
            if files:
                file_paths = []
                for key, path in files:
                    filename = os.path.basename(path)
                    file_paths.append(filename)
                file_info = " | ".join(file_paths)
                footer_label.update(file_info)
            else:
                footer_label.update("")
        except:
            pass
    
    def _toggle_output(self):
        """Toggle output section visibility."""
        try:
            output_section = self.query_one(f"#output-section-{self.step_index}", Vertical)
            toggle_btn = self.query_one(f"#toggle-output-{self.step_index}", Button)
            
            if self.output_visible:
                # Hide output
                output_section.add_class("hidden")
                toggle_btn.label = "▼"
                self.output_visible = False
            else:
                # Show output
                output_section.remove_class("hidden")
                toggle_btn.label = "▲"
                self.output_visible = True
                # Populate output if not already done
                if not output_section.children:
                    self._populate_output_section(output_section)
        except Exception as e:
            self.app.notify(f"Error toggling output: {e}", severity="warning", timeout=2)
    
    def _populate_output_section(self, container: Vertical):
        """Populate the output section with step outputs."""
        for key, content in self.output_content_map.items():
            # Add key label
            key_label = Label(f"[bold]{key}:[/bold]", classes="output-key")
            container.mount(key_label)
            # Add content (selectable text)
            content_label = Label(str(content), classes="output-content", expand=True)
            container.mount(content_label)
