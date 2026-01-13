from typing import List, Optional
from .base import BaseCLIWrapper

class OpenCodeCLIWrapper(BaseCLIWrapper):
    """
    Wrapper for the OpenCode CLI tool.
    Uses 'opencode run' and '-c' for context continuation.
    """

    def __init__(self, command: str = "opencode", auto_approve: bool = True, model: Optional[str] = None, work_dir: Optional[str] = None, read_only: bool = False, sandbox_manager=None):
        super().__init__(command, auto_approve, model, work_dir, read_only=read_only, sandbox_manager=sandbox_manager)
        self._has_started = False

    def _construct_command(self, prompt_text: str) -> List[str]:
        cmd_args = self.command.split() + ["run"]
        
        if self.model:
            cmd_args.extend(["-m", self.model])
        
        if self.session_id:
            cmd_args.extend(["-s", self.session_id])
        elif self._has_started:
            cmd_args.append("-c")
            
        cmd_args.append(prompt_text)
        return cmd_args

    def _parse_output(self, stdout: str) -> str:
        self._has_started = True
        return stdout.strip()