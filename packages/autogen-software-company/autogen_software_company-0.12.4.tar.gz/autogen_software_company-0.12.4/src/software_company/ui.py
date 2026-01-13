from typing import Protocol, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.theme import Theme
from rich.json import JSON
from rich.table import Table
import json

class UserInterface(Protocol):
    def print_step_header(self, step_number: int, step_name: str, work_dir: str = None):
        ...

    def print_assignment(self, role: str, tool: str, model: str):
        ...

    def print_timeout(self, timeout_val: int):
        ...

    def print_input_loading(self, input_key: str, path: str):
        ...

    def print_tool_start(self, step_name: str, tool_name: str):
        ...

    def start_spinner(self, message: str):
        ...

    def stop_spinner(self):
        ...

    def print_output(self, step_name: str, output: dict):
        ...

    def print_error(self, message: str):
        ...

    def print_warning(self, message: str):
        ...

    def print_info(self, message: str):
        ...

    def print_success(self, message: str):
        ...

    def print_stream_line(self, line: str, source: str = "stdout"):
        ...

    def input(self, prompt: str) -> str:
        ...

    def print_user_intervention(self, step_name: str, files: list):
        ...

    def print_artifacts(self, step_name: str, artifacts: list):
        ...

    def print_step_outputs_summary(self, step_name: str, artifacts: list):
        ...

    def print_newline(self):
        ...


class ConsoleUI:
    def __init__(self):
        self.console = Console(theme=Theme({
            "info": "dim cyan",
            "warning": "magenta",
            "error": "bold red",
            "success": "bold green",
            "step": "bold blue",
            "json.key": "bold cyan",
            "json.str": "green",
            "highlight": "bold yellow",
            "role": "bold magenta",
            "tool": "bold cyan",
            "file": "underline blue",
        }))
        self.status = None

    def print_artifacts(self, step_name: str, artifacts: list):
        self.console.print(f"[bold]Generated Artifacts:[/bold]")
        for key, path in artifacts:
            self.console.print(f" - [bold cyan]{key}[/bold cyan]: [file]{path}[/file]")
        self.console.print()

    def print_step_outputs_summary(self, step_name: str, artifacts: list):
        """Display output file paths from a completed step in a summary section."""
        self.console.print(f"[bold green]✓ Completed:[/bold green] {step_name}")
        for key, path in artifacts:
            self.console.print(f"  [dim]→[/dim] [bold cyan]{key}[/bold cyan]: [file]{path}[/file]")
        self.console.print()

    def print_newline(self):
        self.console.print()

    def print_step_header(self, step_number: int, step_name: str, work_dir: str = None):
        title = f"[step]STEP {step_number}: {step_name}[/step]"
        content = ""
        if work_dir:
            content = f"Working Directory: [dim]{work_dir}[/dim]"
        else:
            content = "Running..."

        self.console.print()
        self.console.print(Panel(content, title=title, border_style="blue", expand=False))

    def print_assignment(self, role: str, tool: str, model: str):
        grid = Table.grid(expand=True)
        grid.add_column(justify="right", style="dim")
        grid.add_column(justify="left")

        grid.add_row("Role:", f"[role]{role}[/role]")
        grid.add_row("Tool:", f"[tool]{tool}[/tool]")
        grid.add_row("Model:", f"[dim]{model or 'Default'}[/dim]")

        self.console.print(Panel(grid, title="[bold]Task Assignment[/bold]", border_style="cyan", expand=False))

    def print_timeout(self, timeout_val: int):
        self.console.print(f"   [highlight]⏳ Timeout:[/highlight] [bold]{timeout_val}s[/bold]")

    def print_input_loading(self, input_key: str, path: str):
        self.console.print(f"   [dim]📥 Loading input[/dim] [bold]{input_key}[/bold] [dim]from[/dim] [file]{path}[/file]")

    def print_tool_start(self, step_name: str, tool_name: str):
        self.console.print(f"[bold green]🚀 Starting execution:[/bold green] [bold]{step_name}[/bold] [dim](via {tool_name})[/dim]...")
        self.console.print("[dim]   (Streaming output below)[/dim]")

    def start_spinner(self, message: str):
        self.status = self.console.status(message)
        self.status.start()

    def stop_spinner(self):
        if self.status:
            self.status.stop()
            self.status = None

    def print_output(self, step_name: str, output: dict):
        self.console.print(f"\n[success]--- Output from {step_name} ---[/success]")

        for key, val in output.items():
            self.console.print(f"[bold cyan]>> {key}[/bold cyan]")
            if isinstance(val, str):
                # Check if it is a JSON string
                stripped = val.strip()
                if (stripped.startswith("{") and stripped.endswith("}")) or \
                   (stripped.startswith("[") and stripped.endswith("]")):
                    try:
                        self.console.print_json(val)
                        self.console.print()
                        continue
                    except json.JSONDecodeError:
                        pass

                # Check if it looks like code (simple heuristic)
                if stripped.startswith(("def ", "class ", "import ", "from ", "<!DOCTYPE", "<html>")):
                     # Use 'python' as default guess, but rich can guess too if we pass no lexer?
                     # Syntax(val, lexer="python")
                     # Let's try to detect based on content or just use Markdown code blocks
                     self.console.print(Markdown(f"```\n{val}\n```"))
                else:
                    self.console.print(Markdown(val))
            elif isinstance(val, (dict, list)):
                 self.console.print_json(data=val)
            else:
                 self.console.print(str(val))
            self.console.print()

    def print_error(self, message: str):
        self.console.print(f"[error]Error:[/error] {message}")

    def print_warning(self, message: str):
        self.console.print(f"[warning]Warning:[/warning] {message}")

    def print_info(self, message: str):
        self.console.print(f"[info]{message}[/info]")

    def print_success(self, message: str):
        self.console.print(f"[success]{message}[/success]")

    def print_stream_line(self, line: str, source: str = "stdout"):
        style = "dim" if source == "stdout" else "red"
        # We use markup=False to prevent treating brackets as style tags.
        # This allows raw output (including ANSI codes if supported by the terminal) to be printed safely
        # without Rich trying to interpret it as Rich markup.
        self.console.print(line, style=style, markup=False, end="")

    def input(self, prompt: str):
        return self.console.input(f"[bold yellow]{prompt}[/bold yellow]")

    def print_user_intervention(self, step_name: str, files: list):
        self.console.print(Panel(
            f"Step '[bold]{step_name}[/bold]' is paused for user review.\n" +
            "Generated output files:\n" +
            "\n".join([f" - [cyan]{key}[/cyan]: {path}" for key, path in files]) +
            "\n\nYou may edit these files now. When you are ready to proceed, press Enter...",
            title="[bold yellow]USER INTERVENTION[/bold yellow]",
            border_style="yellow"
        ))

# For backward compatibility if needed, though we will refactor usage
UI = ConsoleUI
