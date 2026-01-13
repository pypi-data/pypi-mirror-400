import os
import subprocess
import time
from typing import Dict, Any, List, Optional

class SandboxManager:
    """
    Manages the lifecycle of a Docker container for sandboxed execution.
    """

    def __init__(self, config: Dict[str, Any], task_id: str, work_dir: str):
        self.config = config.get("sandbox", {})
        self.task_id = task_id
        self.work_dir = os.path.abspath(work_dir)
        self.enabled = self.config.get("enabled", False)
        self.image = self.config.get("image", "python:3.11-slim")
        self.mount_path = self.config.get("mount_path", "/workspace")
        self.container_name = f"autogen_sandbox_{self.task_id}"

    def is_active(self) -> bool:
        """Returns true if sandboxing is enabled."""
        return self.enabled

    def start(self) -> None:
        """
        Starts the Docker container in detached mode with volume mounts.
        Idempotent: if container already exists and is running, does nothing.
        If it exists but is stopped, restarts it.
        """
        if not self.enabled:
            return

        # Check if container exists
        status = self._get_container_status()

        if status == "running":
            return

        if status == "exited" or status == "created":
            self._run_cmd(["docker", "start", self.container_name])
            return

        # Clean up if it exists in some other state (e.g. paused/dead?)
        # For now, if it's not running/exited/created, we assume we need to create it.
        # But to be safe, we can try to remove it first if it exists.
        if status:
             self._run_cmd(["docker", "rm", "-f", self.container_name])

        uid = os.getuid()
        gid = os.getgid()

        cmd = [
            "docker", "run", "-d", "--rm",
            "--name", self.container_name,
            "-v", f"{self.work_dir}:{self.mount_path}",
            "-w", self.mount_path,
            "-u", f"{uid}:{gid}",
            self.image,
            "tail", "-f", "/dev/null"
        ]

        print(f"[Sandbox] Starting container {self.container_name}...")
        self._run_cmd(cmd)

        # Wait a moment for it to be ready?
        time.sleep(1)

    def stop(self) -> None:
        """Stops and removes the Docker container."""
        if not self.enabled:
            return

        status = self._get_container_status()
        if status:
            print(f"[Sandbox] Stopping container {self.container_name}...")
            # We used --rm, so stopping it should remove it.
            # But using -f to be sure.
            self._run_cmd(["docker", "rm", "-f", self.container_name])

    def wrap_command(self, command: List[str], work_dir: Optional[str] = None) -> List[str]:
        """
        Prefixes the command with 'docker exec ...' logic.

        Args:
            command: The command and arguments as a list.
            work_dir: Optional working directory INSIDE the container.
                      If None, uses the mount_path.
        """
        if not self.enabled:
            return command

        # We need to map the host work_dir to the container path if provided
        # If the provided work_dir is absolute path on host, we need to convert it to container path
        # Assumption: work_dir is a subdirectory of self.work_dir (host project root)

        container_cwd = self.mount_path
        if work_dir:
            # Normalize paths
            host_root = self.work_dir
            target_path = os.path.abspath(work_dir)

            if target_path.startswith(host_root):
                rel_path = os.path.relpath(target_path, host_root)
                if rel_path != ".":
                    container_cwd = f"{self.mount_path}/{rel_path}".replace("\\", "/")

        exec_cmd = [
            "docker", "exec", "-i",
            "-w", container_cwd,
            self.container_name
        ]

        return exec_cmd + command

    def _get_container_status(self) -> Optional[str]:
        """Returns the status of the container or None if not found."""
        try:
            result = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.Status}}", self.container_name],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except FileNotFoundError:
             # Docker not installed or not in PATH
             print("[Sandbox] Warning: Docker command not found.")
             return None

    def _run_cmd(self, cmd: List[str]) -> None:
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"[Sandbox] Error running docker command: {e}")
            if e.stderr:
                print(f"[Sandbox] Stderr: {e.stderr.decode()}")
            raise
