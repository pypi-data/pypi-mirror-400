import os
from typing import List, Optional
from .base import BaseCLIWrapper
from .utils import strip_ansi_codes

class AiderCLIWrapper(BaseCLIWrapper):
    """
    Wrapper for the Aider CLI tool.
    """

    def __init__(self, command: str = "aider", auto_approve: bool = True, model: Optional[str] = None, work_dir: Optional[str] = None, read_only: bool = False, sandbox_manager=None):
        super().__init__(command, auto_approve, model, work_dir, read_only=read_only, sandbox_manager=sandbox_manager)

    def _construct_command(self, prompt_text: str) -> List[str]:
        cmd_args = self.command.split()

        # Non-interactive flags
        # We allow streaming to support real-time feedback (handled by BaseCLIWrapper)
        # cmd_args.append("--no-stream")
        cmd_args.append("--no-auto-commits")

        if self.auto_approve:
            cmd_args.append("--yes")

        if self.model:
            cmd_args.extend(["--model", self.model])

        if self.read_only:
             # If read-only, ensure we are strict in prompt.
             # Note: We still pass --yes to prevent blocking on confirmations,
             # but we rely on the prompt instructions to prevent edits.
             prompt_text = "READ-ONLY MODE: DO NOT EDIT FILES. " + prompt_text

        cmd_args.extend(["--message", prompt_text])
        return cmd_args

    def _parse_output(self, stdout: str) -> str:
        clean_output = strip_ansi_codes(stdout)
        return clean_output.strip()
