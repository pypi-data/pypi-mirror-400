from textual.app import App
from typing import List, Optional
import threading
from ..ui import UserInterface

class TuiUIAdapter(UserInterface):
    def __init__(self, app: App):
        self.app = app

    def _safe_call(self, callback, *args, **kwargs):
        if threading.get_ident() == self.app._thread_id:
            callback(*args, **kwargs)
        else:
            self.app.call_from_thread(lambda: callback(*args, **kwargs))

    def print_step_header(self, step_number: int, step_name: str, work_dir: str = None):
        self._safe_call(self.app.on_step_start, step_number, step_name)

    def print_output(self, step_name: str, output: dict):
        self._safe_call(self.app.update_step_output, step_name, output)

    # Implement other methods to avoid crashes, but they might be no-ops or simple notifications
    def print_assignment(self, role: str, tool: str, model: str):
        pass 

    def print_timeout(self, timeout_val: int):
        pass

    def print_input_loading(self, input_key: str, path: str):
        pass

    def print_tool_start(self, step_name: str, tool_name: str):
        pass

    def start_spinner(self, message: str):
        pass

    def stop_spinner(self):
        pass

    def print_error(self, message: str):
        self._safe_call(self.app.notify, message, severity="error")

    def print_warning(self, message: str):
        self._safe_call(self.app.notify, message, severity="warning")

    def print_info(self, message: str):
        self._safe_call(self.app.write_to_console, f"[dim]{message}[/dim]")

    def print_success(self, message: str):
        self._safe_call(self.app.write_to_console, f"[bold green]{message}[/bold green]")

    def print_stream_line(self, line: str, source: str = "stdout"):
        self._safe_call(self.app.stream_log, line)

    def input(self, prompt: str) -> str:
        return ""

    def print_user_intervention(self, step_name: str, files: list):
        self._safe_call(self.app.notify, f"User Intervention Required: {step_name}", severity="warning")
        self._safe_call(self.app.write_to_console, f"[bold yellow]USER INTERVENTION REQUIRED for {step_name}[/bold yellow]")
        for k, p in files:
            self._safe_call(self.app.write_to_console, f" - {k}: {p}")

    def print_artifacts(self, step_name: str, artifacts: list):
        self._safe_call(self.app.update_step_artifacts, step_name, artifacts)

    def print_step_outputs_summary(self, step_name: str, artifacts: list):
        self._safe_call(self.app.update_step_artifacts, step_name, artifacts)

    def print_newline(self):
        self._safe_call(self.app.write_to_console, "")
