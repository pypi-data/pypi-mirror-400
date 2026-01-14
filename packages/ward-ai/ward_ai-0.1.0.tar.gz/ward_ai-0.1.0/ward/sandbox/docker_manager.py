"""Docker-based sandbox management with Windows-first design."""

from __future__ import annotations

import asyncio
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

import docker
import structlog
from docker.errors import DockerException, NotFound

from ..core.config import SandboxConfig

logger = structlog.get_logger()


class DockerManager:
    """Manages Docker-based sandbox environments with Windows-first approach."""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.client: Optional[docker.DockerClient] = None
        self.containers: Dict[str, Any] = {}
        
    async def initialize(self) -> bool:
        """Initialize Docker client and verify availability."""
        try:
            self.client = docker.from_env()
            
            # Test Docker connectivity
            self.client.ping()
            
            # Check if we can run containers
            test_container = self.client.containers.run(
                "hello-world",
                remove=True,
                detach=False
            )
            
            logger.info("Docker initialized successfully", 
                       platform=platform.system(),
                       docker_version=self.client.version()["Version"])
            return True
            
        except DockerException as e:
            logger.warning("Docker not available", error=str(e))
            return False
        except Exception as e:
            logger.error("Failed to initialize Docker", error=str(e))
            return False
    
    def is_docker_available(self) -> bool:
        """Check if Docker is available and running."""
        try:
            if not self.client:
                return False
            self.client.ping()
            return True
        except Exception:
            return False
    
    def detect_docker_desktop_windows(self) -> bool:
        """Detect if Docker Desktop is running on Windows."""
        if platform.system() != "Windows":
            return False
            
        try:
            # Check if Docker Desktop service is running
            result = subprocess.run(
                ["powershell", "-Command", "Get-Service", "com.docker.service"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "Running" in result.stdout:
                logger.info("Docker Desktop detected on Windows")
                return True
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logger.debug("Failed to detect Docker Desktop", error=str(e))
            
        return False
    
    async def create_sandbox_container(
        self, 
        session_id: str, 
        project_path: Path,
        base_image: str = "python:3.11-slim"
    ) -> Optional[str]:
        """Create a new sandbox container for the session."""
        if not self.client:
            logger.error("Docker client not initialized")
            return None
            
        try:
            # Prepare container configuration
            container_name = f"ward-sandbox-{session_id[:8]}"
            
            # Windows-specific volume mounting
            if platform.system() == "Windows":
                # Convert Windows path to Docker-compatible format
                host_path = str(project_path).replace("\\", "/")
                if host_path[1] == ":":
                    # Convert C:\path to /c/path format for Docker Desktop
                    host_path = f"/{host_path[0].lower()}{host_path[2:]}"
            else:
                host_path = str(project_path)
            
            # Container configuration
            container_config = {
                "image": base_image,
                "name": container_name,
                "working_dir": "/workspace",
                "volumes": {
                    host_path: {"bind": "/workspace", "mode": "rw"}
                },
                "environment": {
                    "WARD_SESSION_ID": session_id,
                    "WARD_PROJECT_PATH": "/workspace",
                    "PYTHONPATH": "/workspace",
                },
                "detach": True,
                "tty": True,
                "stdin_open": True,
                "network_mode": "none",  # Isolated network for security
                "mem_limit": "1g",  # Memory limit
                "cpu_quota": 50000,  # CPU limit (50% of one core)
            }
            
            # Pull image if not available
            try:
                self.client.images.get(base_image)
            except NotFound:
                logger.info("Pulling Docker image", image=base_image)
                self.client.images.pull(base_image)
            
            # Create and start container
            container = self.client.containers.run(**container_config)
            
            # Store container reference
            self.containers[session_id] = container
            
            logger.info("Sandbox container created", 
                       session_id=session_id,
                       container_id=container.id[:12],
                       container_name=container_name)
            
            return container.id
            
        except DockerException as e:
            logger.error("Failed to create sandbox container", 
                        session_id=session_id, 
                        error=str(e))
            return None
    
    async def execute_command(
        self, 
        session_id: str, 
        command: str,
        working_dir: str = "/workspace"
    ) -> tuple[int, str, str]:
        """Execute a command in the sandbox container."""
        container = self.containers.get(session_id)
        if not container:
            raise ValueError(f"No container found for session {session_id}")
        
        try:
            # Execute command in container
            exec_result = container.exec_run(
                cmd=["bash", "-c", f"cd {working_dir} && {command}"],
                stdout=True,
                stderr=True,
                tty=False
            )
            
            return_code = exec_result.exit_code
            stdout = exec_result.output.decode() if exec_result.output else ""
            stderr = ""  # exec_run combines stdout and stderr
            
            logger.debug("Command executed in container",
                        session_id=session_id,
                        command=command,
                        return_code=return_code)
            
            return return_code, stdout, stderr
            
        except Exception as e:
            logger.error("Failed to execute command in container",
                        session_id=session_id,
                        command=command,
                        error=str(e))
            raise
    
    async def sync_files_to_host(self, session_id: str, target_path: Path) -> bool:
        """Sync files from container back to host (if needed)."""
        # With bind mounts, files are automatically synced
        # This method is for future use with copy-based approaches
        return True
    
    async def cleanup_container(self, session_id: str) -> bool:
        """Clean up and remove the sandbox container."""
        container = self.containers.get(session_id)
        if not container:
            logger.warning("No container to cleanup", session_id=session_id)
            return True
        
        try:
            # Stop and remove container
            container.stop(timeout=10)
            container.remove()
            
            # Remove from tracking
            del self.containers[session_id]
            
            logger.info("Sandbox container cleaned up", 
                       session_id=session_id,
                       container_id=container.id[:12])
            return True
            
        except Exception as e:
            logger.error("Failed to cleanup container", 
                        session_id=session_id, 
                        error=str(e))
            return False
    
    async def get_container_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get resource usage statistics for the container."""
        container = self.containers.get(session_id)
        if not container:
            return None
        
        try:
            stats = container.stats(stream=False)
            
            # Extract useful metrics
            cpu_usage = stats["cpu_stats"]["cpu_usage"]["total_usage"]
            memory_usage = stats["memory_stats"]["usage"]
            memory_limit = stats["memory_stats"]["limit"]
            
            return {
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "memory_limit": memory_limit,
                "memory_percent": (memory_usage / memory_limit) * 100,
            }
            
        except Exception as e:
            logger.error("Failed to get container stats", 
                        session_id=session_id, 
                        error=str(e))
            return None
    
    async def cleanup_all_containers(self) -> int:
        """Clean up all Ward containers (emergency cleanup)."""
        cleaned = 0
        
        try:
            # Find all Ward containers
            containers = self.client.containers.list(
                all=True,
                filters={"name": "ward-sandbox-"}
            )
            
            for container in containers:
                try:
                    container.stop(timeout=5)
                    container.remove()
                    cleaned += 1
                    logger.info("Cleaned up orphaned container", 
                               container_id=container.id[:12])
                except Exception as e:
                    logger.warning("Failed to cleanup container", 
                                  container_id=container.id[:12], 
                                  error=str(e))
            
            # Clear tracking
            self.containers.clear()
            
        except Exception as e:
            logger.error("Failed to cleanup all containers", error=str(e))
        
        return cleaned


class VenvFallbackManager:
    """Fallback isolation using Python virtual environments when Docker unavailable."""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.venvs: Dict[str, Path] = {}
    
    async def create_venv_sandbox(self, session_id: str, project_path: Path) -> Optional[Path]:
        """Create a Python virtual environment for isolation."""
        try:
            # Create venv in temp directory
            import tempfile
            temp_dir = Path(tempfile.mkdtemp(prefix=f"ward-venv-{session_id[:8]}-"))
            venv_path = temp_dir / "venv"
            
            # Create virtual environment
            subprocess.run([
                "python", "-m", "venv", str(venv_path)
            ], check=True)
            
            # Copy project files to temp directory
            project_copy = temp_dir / "project"
            shutil.copytree(project_path, project_copy)
            
            # Store paths
            self.venvs[session_id] = temp_dir
            
            logger.info("Venv sandbox created", 
                       session_id=session_id,
                       venv_path=str(venv_path),
                       project_copy=str(project_copy))
            
            return project_copy
            
        except Exception as e:
            logger.error("Failed to create venv sandbox", 
                        session_id=session_id, 
                        error=str(e))
            return None
    
    async def execute_command(
        self, 
        session_id: str, 
        command: str
    ) -> tuple[int, str, str]:
        """Execute command in the venv environment."""
        venv_dir = self.venvs.get(session_id)
        if not venv_dir:
            raise ValueError(f"No venv found for session {session_id}")
        
        venv_path = venv_dir / "venv"
        project_path = venv_dir / "project"
        
        # Determine activation script based on platform
        if platform.system() == "Windows":
            activate_script = venv_path / "Scripts" / "activate.bat"
            shell_command = f'"{activate_script}" && cd "{project_path}" && {command}'
            shell = True
        else:
            activate_script = venv_path / "bin" / "activate"
            shell_command = f'source "{activate_script}" && cd "{project_path}" && {command}'
            shell = True
        
        try:
            result = subprocess.run(
                shell_command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            logger.error("Command timed out in venv", session_id=session_id)
            return 1, "", "Command timed out"
        except Exception as e:
            logger.error("Failed to execute command in venv", 
                        session_id=session_id, 
                        error=str(e))
            return 1, "", str(e)
    
    async def cleanup_venv(self, session_id: str) -> bool:
        """Clean up the venv sandbox."""
        venv_dir = self.venvs.get(session_id)
        if not venv_dir:
            return True
        
        try:
            shutil.rmtree(venv_dir)
            del self.venvs[session_id]
            
            logger.info("Venv sandbox cleaned up", 
                       session_id=session_id,
                       venv_dir=str(venv_dir))
            return True
            
        except Exception as e:
            logger.error("Failed to cleanup venv", 
                        session_id=session_id, 
                        error=str(e))
            return False