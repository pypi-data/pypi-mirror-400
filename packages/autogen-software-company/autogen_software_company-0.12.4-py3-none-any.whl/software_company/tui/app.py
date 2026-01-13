from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, RichLog, Label, Markdown
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.binding import Binding
from datetime import datetime
import asyncio
import json
import os
import shutil

from .widgets import TaskControlHeader, TaskExplorerSidebar, StepCard
from .adapter import TuiUIAdapter
from ..workflow import SoftwareCompanyWorkflow

class SoftwareCompanyApp(App):
    TITLE = "Task Control"
    SUB_TITLE = "Autonomous Agent Orchestration"
    
    BINDINGS = [
        Binding("q", "quit", "✖ Quit", show=True),
        Binding("s", "stop_workflow", "⏹ Stop", show=True),
        Binding("r", "resume_workflow", "▶ Resume", show=True),
        Binding("b", "toggle_sidebar", "☰ Sidebar", show=True),
        Binding("d", "toggle_dark", "🌗 Theme", show=True)
    ]

    CSS = """
    /* --- Theming --- */
    
    /* Global Backgrounds & Colors */
    Screen { background: #1e1e2e; color: #cdd6f4; }
    .-light-mode Screen { background: #eff1f5; color: #4c4f69; }

    TaskControlHeader {
        dock: top;
        background: #11111b;
        color: #89b4fa;
        height: 3;
        layout: horizontal;
        border-bottom: solid #313244;
    }
    .-light-mode TaskControlHeader { background: #dce0e8; color: #1e66f5; border-bottom: solid #bcc0cc; }

    #header-logo {
        width: auto;
        height: 3;
        content-align: center middle;
        padding: 0 2;
        background: #181825;
        color: #89b4fa;
        text-style: bold italic;
    }
    .-light-mode #header-logo { background: #e6e9ef; color: #1e66f5; }

    #main-header {
        width: 1fr;
        background: #11111b;
        color: #cdd6f4;
    }
    .-light-mode #main-header { background: #dce0e8; color: #4c4f69; }

    Footer {
        dock: bottom;
        background: #11111b;
        color: #a6e3a1;
        height: 1;
    }
    .-light-mode Footer { background: #dce0e8; color: #40a02b; }

    /* Layout */
    #main-layout { width: 100%; height: 1fr; }

    /* Sidebar */
    #sidebar {
        width: 30%;
        height: 100%;
        background: #181825;
        padding: 1;
        transition: width 200ms in_out_cubic;
        border-right: solid #313244;
    }
    .-light-mode #sidebar { background: #e6e9ef; border-right: solid #bcc0cc; }
    
    #sidebar.hidden { display: none; width: 0%; border: none; }
    
    .sidebar-header {
        text-align: center;
        color: #89b4fa;
        text-style: bold;
        padding-bottom: 1;
        border-bottom: solid #313244;
    }
    .-light-mode .sidebar-header { color: #1e66f5; border-bottom: solid #bcc0cc; }

    ListView { background: #181825; border: none; }
    .-light-mode ListView { background: #e6e9ef; }
    
    ListItem { padding: 1; background: #181825; color: #cdd6f4; }
    .-light-mode ListItem { background: #e6e9ef; color: #4c4f69; }
    
    ListItem:hover { background: #313244; }
    .-light-mode ListItem:hover { background: #bcc0cc; }
    
    ListItem.--highlight { background: #313244; color: #89b4fa; }
    .-light-mode ListItem.--highlight { background: #bcc0cc; color: #1e66f5; }

    /* Main Content Area */
    #right-side-container { width: 1fr; height: 100%; background: #1e1e2e; }
    .-light-mode #right-side-container { background: #eff1f5; }

    #main-content { width: 100%; height: 1fr; padding: 1 2; }
    
    #task-header {
        height: 3;
        background: #1e1e2e;
        color: #bac2de;
        text-style: bold;
        content-align: center middle;
        border-bottom: solid #313244;
        margin-bottom: 1;
    }
    .-light-mode #task-header { background: #eff1f5; color: #6c6f85; border-bottom: solid #bcc0cc; }

    #steps-container { height: 1fr; scrollbar-background: #1e1e2e; scrollbar-color: #313244; }
    .-light-mode #steps-container { scrollbar-background: #eff1f5; scrollbar-color: #bcc0cc; }

    #bottom-deck {
        width: 100%;
        height: 12;
        background: #11111b;
        border-top: solid #313244;
    }
    .-light-mode #bottom-deck { background: #dce0e8; border-top: solid #bcc0cc; }

    #log-panel {
        width: 100%;
        height: 1fr;
        background: #11111b;
        color: #cdd6f4;
        border: none;
    }
    .-light-mode #log-panel { background: #dce0e8; color: #4c4f69; }
    
    #log-label {
        background: #313244;
        color: #cdd6f4;
        padding-left: 1;
        text-style: bold;
    }
    .-light-mode #log-label { background: #bcc0cc; color: #4c4f69; }

    /* Step Card Styles */
    StepCard {
        height: auto;
        background: #181825;
        margin-bottom: 1;
        padding: 1 1;
        border-left: thick #bac2de;
    }
    .-light-mode StepCard { background: #e6e9ef; border-left: thick #9399b2; }
    
    StepCard.running { border-left: thick #89b4fa; background: #313244; }
    .-light-mode StepCard.running { border-left: thick #1e66f5; background: #ccd0da; }
    
    StepCard.completed { border-left: thick #a6e3a1; }
    .-light-mode StepCard.completed { border-left: thick #40a02b; }
    
    StepCard.failed { border-left: thick #f38ba8; }
    .-light-mode StepCard.failed { border-left: thick #d20f39; }

    .step-header { height: auto; margin: 0; padding: 0; }
    .step-title { width: 1fr; text-style: bold; color: #f9e2af; }
    .-light-mode .step-title { color: #df8e1d; }
    
    .step-status { width: auto; color: #bac2de; }
    .-light-mode .step-status { color: #6c6f85; }

    .step-body { height: auto; margin: 0; padding: 0; }
    .step-meta { color: #89b4fa; }
    .-light-mode .step-meta { color: #1e66f5; }
    
    .step-io { color: #9399b2; text-style: italic; }
    .-light-mode .step-io { color: #6c6f85; }

    .file-list-container { height: auto; margin: 0; padding: 0; }
    .file-row { height: auto; margin: 0; padding: 0; }
    .file-path { color: #a6e3a1; width: 1fr; }
    .-light-mode .file-path { color: #40a02b; }

    .icon-btn {
        width: 4; min-width: 4; height: 1; border: none;
        background: transparent; color: #89b4fa; padding: 0; margin: 0;
    }
    .-light-mode .icon-btn { color: #1e66f5; }
    
    .rerun-btn { color: #f9e2af; }
    .-light-mode .rerun-btn { color: #df8e1d; }
    
    .toggle-btn { color: #cdd6f4; }
    .-light-mode .toggle-btn { color: #4c4f69; }
    
    .output-section { height: auto; padding: 1 2; border-top: solid #313244; margin-top: 1; }
    .-light-mode .output-section { border-top: solid #bcc0cc; }
    
    .output-section.hidden { display: none; }
    
    .output-key { color: #f9e2af; text-style: bold; margin-top: 1; }
    .-light-mode .output-key { color: #df8e1d; }
    
    .output-content { color: #a6e3a1; width: 100%; margin: 0 1; }
    .-light-mode .output-content { color: #40a02b; }
    
    .task-card { height: auto; margin-bottom: 1; }
    .task-card-container { height: auto; }
    .task-card-header { height: auto; width: 100%; }
    .task-card-body { height: auto; }
    .task-card-info { height: auto; }
    
    .delete-btn { color: #f38ba8; }
    .-light-mode .delete-btn { color: #d20f39; }
    
    .task-list-item { height: auto; padding: 1; margin: 0; }
    .task-list-item Horizontal { width: 100%; }
    
    .step-footer { height: auto; margin-top: 1; padding: 0; border-top: solid #313244; }
    .-light-mode .step-footer { border-top: solid #bcc0cc; }
    
    .step-output-files { width: 1fr; color: #a6e3a1; text-style: dim; }
    .-light-mode .step-output-files { color: #40a02b; }
    
    .step-time { width: auto; color: #bac2de; text-align: right; }
    .-light-mode .step-time { color: #6c6f85; }
    """

    def __init__(self, workflow_factory, state_directory: str, **kwargs):
        super().__init__(**kwargs)
        self._workflow_factory = workflow_factory
        self.state_directory = state_directory
        self.workflow = None
        self._worker = None
        self._step_start_times = {}

    def compose(self) -> ComposeResult:
        yield TaskControlHeader()
        
        with Horizontal(id="main-layout"):
            # Sidebar
            with Vertical(id="sidebar"):
                yield TaskExplorerSidebar(self.state_directory)
            
            # Right Side (Stage + Logs)
            with Vertical(id="right-side-container"):
                # Main Content
                with Vertical(id="main-content"):
                    yield Label("Task Details", id="task-header")
                    yield VerticalScroll(id="steps-container")
                
                # Bottom Deck
                with Vertical(id="bottom-deck"):
                    yield Label("EXECUTION LOGS", id="log-label")
                    yield RichLog(highlight=True, markup=True, id="log-panel", wrap=True)
        
        yield Footer()

    async def on_mount(self):
        # Initial Load using default args (from CLI)
        await self.load_workflow_async()

    async def on_task_explorer_sidebar_selected(self, message: TaskExplorerSidebar.Selected):
        await self.load_workflow_async(task_id_override=message.task_id)
    
    async def on_task_explorer_sidebar_delete_requested(self, message: TaskExplorerSidebar.DeleteRequested):
        """Handle task deletion request."""
        import shutil
        task_dir = os.path.join(self.state_directory, message.task_id)
        try:
            shutil.rmtree(task_dir)
            self.notify(f"✓ Task {message.task_id} deleted!", timeout=2)
            # Refresh task list
            sidebar = self.query_one(TaskExplorerSidebar)
            sidebar.refresh_tasks()
        except Exception as e:
            self.notify(f"Failed to delete task: {e}", severity="error", timeout=2)
    
    async def on_step_card_rerun_requested(self, message: StepCard.RerunRequested):
        """Handle step re-run request."""
        if not self.workflow:
            self.notify("No workflow loaded", severity="warning")
            return
        
        step = self.workflow.steps[message.step_index]
        self.notify(f"🔄 Re-running from step: {step.name}...", timeout=1)
        
        # Revert workflow from this step onwards
        self.workflow.revert_from_step(message.step_index)
        
        # Start workflow execution from that step
        if self._worker and self._worker.is_running:
            self._worker.cancel()
        
        self._worker = self.run_worker(self.run_workflow_task, exclusive=True)

    async def load_workflow_async(self, task_id_override=None):
        if self._worker and self._worker.is_running:
            self._worker.cancel()

        try:
            self.query_one("#log-panel", RichLog).clear()
        except:
            pass

        adapter = TuiUIAdapter(self)
        self.workflow = self._workflow_factory(ui=adapter, task_id_override=task_id_override)
        
        self.query_one("#task-header", Label).update(f"Task ID: {self.workflow.task_id}")

        container = self.query_one("#steps-container", VerticalScroll)
        await container.remove_children()
        
        # Load history
        timeline = self.workflow.state_manager.get_timeline()
        context = self.workflow.state_manager.state.get("context", {})
        
        for i, step in enumerate(self.workflow.steps):
            card = StepCard(i, step, id=f"step-card-{i}")
            await container.mount(card)
            
            # hydration
            step_entry = next((e for e in timeline if e["step_name"] == step.name and e["status"] == "COMPLETED"), None)
            
            if step_entry:
                card.status = "Completed"
                card.duration = f"{step_entry.get('duration', '-')}"
                
                outputs = {}
                files = []
                for key in step.output_keys:
                    val = context.get(key)
                    if val:
                        outputs[key] = val
                        if isinstance(val, dict) and val.get("type") == "file":
                            files.append((key, val["path"]))
                
                if outputs:
                    card.set_output(outputs)
                if files:
                    card.set_files(files)

        self._worker = self.run_worker(self.run_workflow_task, exclusive=True)

    async def run_workflow_task(self):
        try:
            await self.workflow.run()
        except asyncio.CancelledError:
             pass
        except Exception as e:
            self.notify(f"Workflow Error: {e}", severity="error")

    def action_stop_workflow(self):
        if self._worker and self._worker.is_running:
            self._worker.cancel()
            self.notify("Workflow Stopped")

    def action_resume_workflow(self):
        if self._worker and self._worker.is_running:
            self.notify("Workflow is already running", severity="warning")
            return

        if not self.workflow:
            self.notify("No workflow loaded to resume", severity="warning")
            return

        self.notify("Resuming Workflow...")
        self._worker = self.run_worker(self.run_workflow_task, exclusive=True)

    def action_toggle_sidebar(self):
        sidebar = self.query_one("#sidebar")
        sidebar.toggle_class("hidden")

    def action_load_mission(self):
        def on_mission_selected(task_id):
            if task_id:
                self.write_to_console(f"[bold cyan]Switching to task: {task_id}[/bold cyan]")
                self.call_from_thread(self.load_workflow_async, task_id_override=task_id)

        self.push_screen(TaskSelectionScreen(self.state_directory), on_mission_selected)

    def action_toggle_dark(self):
        self.toggle_class("-light-mode")

    # --- Adapter Methods ---

    def on_step_start(self, step_number: int, step_name: str):
        idx = step_number - 1
        try:
            card = self.query_one(f"#step-card-{idx}", StepCard)
            card.status = "Running"
            self._step_start_times[idx] = datetime.now()
            card.scroll_visible()
        except:
            pass

    def update_step_output(self, step_name: str, output: dict):
        for i, step in enumerate(self.workflow.steps):
            if step.name == step_name:
                try:
                    card = self.query_one(f"#step-card-{i}", StepCard)
                    card.status = "Completed"
                    card.set_output(output)
                    
                    if i in self._step_start_times:
                        delta = datetime.now() - self._step_start_times[i]
                        card.duration = f"{delta.total_seconds():.1f}s"
                except:
                    pass
                break

    def update_step_artifacts(self, step_name: str, artifacts: list):
        for i, step in enumerate(self.workflow.steps):
            if step.name == step_name:
                try:
                    card = self.query_one(f"#step-card-{i}", StepCard)
                    card.set_files(artifacts)
                except Exception as e:
                    self.write_to_console(f"[bold red]Error updating artifacts for {step_name}: {e}[/bold red]")
                break

    def write_to_console(self, message: str):
        try:
            log_panel = self.query_one("#log-panel", RichLog)
            log_panel.write(message)
        except:
            pass

    def stream_log(self, text: str):
        try:
            log_panel = self.query_one("#log-panel", RichLog)
            log_panel.write(text)
        except:
            pass