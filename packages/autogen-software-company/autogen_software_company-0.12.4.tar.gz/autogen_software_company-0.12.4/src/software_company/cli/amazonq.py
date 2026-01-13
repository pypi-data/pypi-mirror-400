import re
from typing import List, Optional, Callable
from .base import BaseCLIWrapper
from .utils import strip_ansi_codes

class AmazonQCLIWrapper(BaseCLIWrapper):
    """
    Wrapper for the Amazon Q CLI (typically 'q').
    Supports session resumption via CWD context and auto-approval of tools.
    """

    def __init__(self, command: str = "q", auto_approve: bool = True, model: Optional[str] = None, work_dir: Optional[str] = None, read_only: bool = False, sandbox_manager=None):
        super().__init__(command, auto_approve, model, work_dir, read_only=read_only, sandbox_manager=sandbox_manager)
        # We track if a session has started to know when to pass -r
        self._has_started = False

    def _construct_command(self, prompt_text: str) -> List[str]:
        cmd_args = self.command.split()
        cmd_args.append("chat")
        cmd_args.append("--no-interactive")
        cmd_args.append("--wrap")
        cmd_args.append("never")
        
        if self.auto_approve and not self.read_only:
            cmd_args.append("--trust-all-tools")
            
        if self.model:
            cmd_args.extend(["--model", self.model])
            
        if self._has_started:
            cmd_args.append("-r")
            
        cmd_args.append(prompt_text)
        return cmd_args

    def _process_stream_line(self, line: str, source: str, callback: Callable[[str, str], None]) -> None:
        """
        Strip ANSI codes from streamed output for cleaner display.
        """
        clean_line = strip_ansi_codes(line)
        callback(clean_line, source)

    def _parse_output(self, stdout: str) -> str:
        self._has_started = True
        
        # Strip ANSI codes first!
        clean_stdout = strip_ansi_codes(stdout)

        separator_regex = re.compile(r"━{10,}")
        parts = separator_regex.split(clean_stdout)
        
        if len(parts) > 1:
            content = parts[-1]
        else:
            content = clean_stdout

        lines = content.splitlines()
        cleaned_lines = []
        
        ignore_patterns = [
            re.compile(r"^🤖 You are chatting with"),
            re.compile(r"^Checkpoints are not available"),
            re.compile(r"^Picking up where we left off"),
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            should_ignore = False
            for pattern in ignore_patterns:
                if pattern.search(line):
                    should_ignore = True
                    break
            
            if not should_ignore:
                if line.startswith("> "):
                    line = line[2:]
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()