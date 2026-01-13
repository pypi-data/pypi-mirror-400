import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
from rich.align import Align

LOGO = r"""
   _____       ______
  / ___/____  / __/ /__      ______  ________
  \__ \/ __ \/ /_/ __/ | /| / / __ \/ ___/ _ \
 ___/ / /_/ / __/ /_ | |/ |/ / /_/ / /  /  __/
/____/\____/_/  \__/ |__/|__/\__,_/_/   \___/

   ______
  / ____/___  ____ ___  ____  ____ _____  __  __
 / /   / __ \/ __ `__ \/ __ \/ __ `/ __ \/ / / /
/ /___/ /_/ / / / / / / /_/ / /_/ / / / / /_/ /
\____/\____/_/ /_/ /_/ .___/\__,_/_/ /_/\__, /
                    /_/                /____/
"""

class RichArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def print_help(self, file=None):
        if file is None:
            file = sys.stdout

        # 1. Logo
        self.console.print(Align.center(Text(LOGO, style="bold cyan")))

        # 2. Description
        if self.description:
            self.console.print(Align.center(Text(self.description, style="white")))
        self.console.print()

        # 3. Arguments Table (No Usage, No Categories)
        table = Table(show_header=True, header_style="bold magenta", box=None, expand=True, padding=(0, 2))
        table.add_column("Options/Arguments", style="bold cyan", ratio=1)
        table.add_column("Description", style="white", ratio=2)
        table.add_column("Default", style="dim", ratio=1)

        for group in self._action_groups:
            actions = [a for a in group._group_actions if a.help != argparse.SUPPRESS]
            if not actions:
                continue

            # Skip adding group title (Categories)

            for action in actions:
                flags, help_text, default = self._format_action_row(action)
                table.add_row(flags, help_text, default)

            # Optional: Add a subtle separator between groups if desired, but user asked to remove categories.
            # We'll just let them flow.

        self.console.print(table)
        self.console.print()

        # 4. Examples
        examples = """
[bold yellow]Examples:[/bold yellow]

  [dim]# Start a new task with a prompt[/dim]
  [green]software-company[/green] "Build a snake game in python"

  [dim]# Use a specific template[/dim]
  [green]software-company[/green] --template planning "Create a todo app"

  [dim]# List available tools[/dim]
  [green]software-company[/green] --list-tools

  [dim]# Resume a specific task[/dim]
  [green]software-company[/green] --id 20231027_100000_abc123

  [dim]# Revert the last step of a task[/dim]
  [green]software-company[/green] --revert --id 20231027_100000_abc123
        """
        self.console.print(Panel(Text.from_markup(examples.strip()), title="[bold]Quick Start[/bold]", border_style="cyan"))

    def _format_action_row(self, action):
        # Flags
        if action.option_strings:
            flags = ", ".join(action.option_strings)
            if action.nargs != 0 and action.dest:
                 metavar = action.metavar or action.dest.upper()
                 if action.nargs == '+':
                     flags += f" [{metavar} ...]"
                 elif action.nargs == '*':
                     flags += f" [{metavar} ...]"
                 elif action.nargs == '?':
                     flags += f" [{metavar}]"
                 else:
                     flags += f" {metavar}"

        else:
            # Positional
            flags = action.metavar or action.dest

        # Help
        help_text = action.help if action.help else ""

        # Default
        default = ""
        if action.default != argparse.SUPPRESS and action.default is not None:
             default = str(action.default)

        return flags, help_text, default
