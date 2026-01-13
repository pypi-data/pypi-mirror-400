import json
from typing import List, Optional, Callable
from .base import BaseCLIWrapper

class GeminiCLIWrapper(BaseCLIWrapper):
    """
    Wrapper for the Gemini CLI tool using stream-json output.
    """

    def __init__(self, command: str = "gemini", auto_approve: bool = True, model: Optional[str] = None, work_dir: Optional[str] = None, read_only: bool = False, sandbox_manager=None):
        super().__init__(command, auto_approve, model, work_dir, read_only=read_only, sandbox_manager=sandbox_manager)

    def _construct_command(self, prompt_text: str) -> List[str]:
        cmd_args = self.command.split() + ["-o", "stream-json"]
        
        if self.auto_approve and not self.read_only:
            cmd_args.append("--yolo")
        
        if self.model:
            cmd_args.extend(["--model", self.model])
        
        if self.session_id:
            cmd_args.extend(["--resume", self.session_id])
            
        cmd_args.append(prompt_text)
        return cmd_args

    def _process_stream_line(self, line: str, source: str, callback: Callable[[str, str], None]) -> None:
        if source == "stderr":
            callback(line, source)
            return

        # For stdout, parse JSON
        line = line.strip()
        if not line:
            return

        try:
            if not line.startswith("{"):
                return
            data = json.loads(line)
            if data.get("type") == "message" and data.get("role") == "assistant":
                content = data.get("content", "")
                if content:
                    callback(content, source)
        except json.JSONDecodeError:
            pass

    def _parse_output(self, stdout: str) -> str:
        output_lines = stdout.splitlines()
        response_content = []
        
        for line in output_lines:
            line = line.strip()
            if not line:
                continue
                
            try:
                if not line.startswith("{"):
                    continue
                    
                data = json.loads(line)
                
                # Capture session ID
                if data.get("type") == "init" and "session_id" in data:
                    if not self.session_id:
                        self.session_id = data["session_id"]
                
                # Collect assistant messages
                if data.get("type") == "message" and data.get("role") == "assistant":
                    content = data.get("content", "")
                    if content:
                        response_content.append(content)
                        
            except json.JSONDecodeError:
                continue

        return "".join(response_content).strip()
