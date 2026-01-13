import subprocess
import shutil
import os
import threading
import queue
from typing import Optional, List, Callable
from abc import ABC, abstractmethod

class BaseCLIWrapper(ABC):
    """
    Abstract base class for interactive CLI agent wrappers.
    Handles process execution and lifecycle.
    """

    def __init__(self, command: str, auto_approve: bool = True, model: Optional[str] = None, work_dir: Optional[str] = None, read_only: bool = False, sandbox_manager=None):
        """
        Args:
            command (str): The base command to run.
            auto_approve (bool): Whether to auto-approve tool calls (if supported).
            model (str, optional): The model ID/name to use.
            work_dir (str, optional): The working directory for the CLI process.
            read_only (bool): Whether to run in read-only mode (default: False).
            sandbox_manager (SandboxManager, optional): Manager for Docker sandbox execution.
        """
        self.command = command
        self.auto_approve = auto_approve
        self.model = model
        self.work_dir = work_dir
        self.read_only = read_only
        self.sandbox_manager = sandbox_manager
        self.session_id: Optional[str] = None
        
        # Verify command exists (only if not sandboxed)
        if not (self.sandbox_manager and self.sandbox_manager.is_active()):
            executable = self.command.split()[0]
            if not shutil.which(executable):
                raise FileNotFoundError(f"Command '{executable}' not found in PATH.")

            # Verify work_dir if provided
            if self.work_dir and not os.path.isdir(self.work_dir):
                raise NotADirectoryError(f"Working directory '{self.work_dir}' does not exist.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def ask(self, prompt_text: str, timeout: int = 120, stream_callback: Optional[Callable[[str, str], None]] = None) -> str:
        """
        Sends a message to the CLI and returns the processed response.

        Args:
            prompt_text (str): The input to send to the CLI.
            timeout (int): Timeout in seconds.
            stream_callback (Callable): Optional callback(text, source) for real-time output.
        """
        cmd_args = self._construct_command(prompt_text)
        cwd = self.work_dir

        if self.sandbox_manager and self.sandbox_manager.is_active():
            cmd_args = self.sandbox_manager.wrap_command(cmd_args, work_dir=self.work_dir)
            cwd = None # docker exec handles working directory

        if os.getenv("DEBUG_CLI_WRAPPER"):
            print(f"[DEBUG_CLI] Executing: {' '.join(cmd_args)}")
            print(f"[DEBUG_CLI] CWD: {cwd or os.getcwd()}")

        try:
            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                cwd=cwd, # Execute in the specified directory
                bufsize=1 # Line buffered
            )
        except Exception as e:
            raise RuntimeError(f"Failed to execute {self.command}: {e}")

        # Queues to store output for final aggregation
        stdout_queue = queue.Queue()
        stderr_queue = queue.Queue()

        full_stdout = []
        full_stderr = []

        def reader(pipe, q, source):
            try:
                for line in pipe:
                    q.put(line)
                    if stream_callback:
                        self._process_stream_line(line, source, stream_callback)
            except ValueError:
                # Handle case where pipe is closed/invalid
                pass
            finally:
                pipe.close()

        t_stdout = threading.Thread(target=reader, args=(process.stdout, stdout_queue, "stdout"))
        t_stderr = threading.Thread(target=reader, args=(process.stderr, stderr_queue, "stderr"))

        t_stdout.start()
        t_stderr.start()

        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            t_stdout.join()
            t_stderr.join()

            # Collect whatever we got so far
            while not stdout_queue.empty(): full_stdout.append(stdout_queue.get())
            while not stderr_queue.empty(): full_stderr.append(stderr_queue.get())

            stdout_str = "".join(full_stdout)
            stderr_str = "".join(full_stderr)

            print(f"[WARN] Command timed out after {timeout}s")
            raise RuntimeError(f"{self.command} timed out after {timeout}s\nStdout: {stdout_str}\nStderr: {stderr_str}")

        t_stdout.join()
        t_stderr.join()

        while not stdout_queue.empty(): full_stdout.append(stdout_queue.get())
        while not stderr_queue.empty(): full_stderr.append(stderr_queue.get())

        stdout_str = "".join(full_stdout)
        stderr_str = "".join(full_stderr)

        if process.returncode != 0:
            err_msg = stderr_str if stderr_str else "(no stderr)"
            # Some CLIs use non-zero exit codes for "soft" errors which we might want to parse.
            # But generally it's an error.
            raise RuntimeError(f"{self.command} exited with code {process.returncode}:\n{err_msg}\nStdout: {stdout_str}")

        return self._parse_output(stdout_str)

    def _process_stream_line(self, line: str, source: str, callback: Callable[[str, str], None]) -> None:
        """
        Process a single line of streamed output.
        Subclasses can override this to handle JSON streams or other formats.
        """
        callback(line, source)

    @abstractmethod
    def _construct_command(self, prompt_text: str) -> List[str]:
        """
        Builds the full command list [cmd, arg1, arg2...]
        """
        pass

    @abstractmethod
    def _parse_output(self, stdout: str) -> str:
        """
        Parses the raw stdout string into a clean response.
        Should also handle session ID extraction if applicable.
        """
        pass

    def close(self) -> None:
        """Resets session state."""
        self.session_id = None
