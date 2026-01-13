from typing import List, Optional, Callable
from .base import BaseCLIWrapper
from .utils import strip_ansi_codes

class GitHubCopilotCLIWrapper(BaseCLIWrapper):
    """
    Wrapper for the GitHub Copilot CLI (gh copilot).
    Uses 'gh copilot explain' for interactions.
    """

    def __init__(self, command: str = "gh", auto_approve: bool = True, model: Optional[str] = None, work_dir: Optional[str] = None, read_only: bool = False, sandbox_manager=None):
        """
        Args:
            command (str): The base command (defaults to 'gh').
            auto_approve (bool): Whether to auto-approve tool calls (not used for Copilot currently).
            model (str, optional): Not typically used for Copilot CLI, but kept for consistency.
            work_dir (str, optional): The working directory.
            read_only (bool): Whether to run in read-only mode (default: False).
            sandbox_manager (SandboxManager, optional): Manager for Docker sandbox execution.
        """
        super().__init__(command, auto_approve, model, work_dir, read_only=read_only, sandbox_manager=sandbox_manager)

    def _construct_command(self, prompt_text: str) -> List[str]:
        # 'gh copilot explain' is used for general queries and code explanations
        # It handles natural language prompts well.
        cmd_args = self.command.split() + ["copilot", "explain", prompt_text]
        return cmd_args

    def _process_stream_line(self, line: str, source: str, callback: Callable[[str, str], None]) -> None:
        # Strip ANSI codes from streaming output
        clean_line = strip_ansi_codes(line)
        callback(clean_line, source)

    def _parse_output(self, stdout: str) -> str:
        # Strip ANSI codes from final output
        return strip_ansi_codes(stdout).strip()
