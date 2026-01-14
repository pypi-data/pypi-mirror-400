"""Sandbox lifecycle management for AI Sandbox Orchestrator."""

from __future__ import annotations

import shutil
import tempfile
from enum import Enum
from pathlib import Path
from typing import Optional

import structlog

logger = structlog.get_logger()


class SandboxType(str, Enum):
    """Types of sandbox environments."""
    GIT_WORKTREE = "git_worktree"
    FILE_COPY = "file_copy"
    SYMLINK = "symlink"


class SandboxManager:
    """
    Manages sandbox environment lifecycle.
    
    Responsibilities:
    1. Create isolated sandbox environments
    2. Initialize sandbox with main codebase content
    3. Manage sandbox cleanup
    4. Handle different sandbox types (git worktree, file copy, etc.)
    """
    
    def __init__(self, base_dir: Path, main_codebase: Path):
        """
        Initialize sandbox manager.
        
        Args:
            base_dir: Base directory for all sandboxes
            main_codebase: Path to the main codebase to protect
        """
        self.base_dir = base_dir
        self.main_codebase = main_codebase
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            "Sandbox manager initialized",
            base_dir=str(base_dir),
            main_codebase=str(main_codebase),
        )
    
    async def create_sandbox(
        self,
        session_id: str,
        sandbox_type: SandboxType = SandboxType.GIT_WORKTREE,
        branch_name: Optional[str] = None,
    ) -> Path:
        """
        Create a new sandbox environment.
        
        Args:
            session_id: Unique session identifier
            sandbox_type: Type of sandbox to create
            branch_name: Git branch name (for git worktree type)
            
        Returns:
            Path to the created sandbox directory
            
        Raises:
            RuntimeError: If sandbox creation fails
        """
        sandbox_path = self.base_dir / f"session_{session_id}"
        
        # Remove existing sandbox if it exists
        if sandbox_path.exists():
            await self.cleanup_sandbox(sandbox_path)
        
        try:
            if sandbox_type == SandboxType.GIT_WORKTREE:
                await self._create_git_worktree(sandbox_path, branch_name or f"sandbox-{session_id}")
            elif sandbox_type == SandboxType.FILE_COPY:
                await self._create_file_copy(sandbox_path)
            elif sandbox_type == SandboxType.SYMLINK:
                await self._create_symlink(sandbox_path)
            else:
                raise ValueError(f"Unsupported sandbox type: {sandbox_type}")
            
            logger.info(
                "Sandbox created successfully",
                session_id=session_id,
                sandbox_path=str(sandbox_path),
                sandbox_type=sandbox_type.value,
            )
            
            return sandbox_path
            
        except Exception as e:
            logger.error(
                "Failed to create sandbox",
                session_id=session_id,
                sandbox_type=sandbox_type.value,
                error=str(e),
            )
            # Cleanup on failure
            if sandbox_path.exists():
                await self.cleanup_sandbox(sandbox_path)
            raise RuntimeError(f"Failed to create sandbox: {e}") from e
    
    async def _create_git_worktree(self, sandbox_path: Path, branch_name: str) -> None:
        """Create sandbox using git worktree."""
        try:
            import git
            
            # Check if main codebase is a git repository
            try:
                repo = git.Repo(self.main_codebase)
            except git.InvalidGitRepositoryError:
                logger.warning(
                    "Main codebase is not a git repository, falling back to file copy",
                    main_codebase=str(self.main_codebase),
                )
                await self._create_file_copy(sandbox_path)
                return
            
            # Create a new branch for the sandbox
            try:
                # Create branch from current HEAD
                sandbox_branch = repo.create_head(branch_name)
                sandbox_branch.checkout()
                
                # Create worktree
                repo.git.worktree("add", str(sandbox_path), branch_name)
                
                logger.info(
                    "Git worktree created",
                    branch_name=branch_name,
                    sandbox_path=str(sandbox_path),
                )
                
            except git.GitCommandError as e:
                if "already exists" in str(e):
                    # Branch exists, try to use it
                    repo.git.worktree("add", str(sandbox_path), branch_name)
                else:
                    raise
                    
        except ImportError:
            logger.warning("GitPython not available, falling back to file copy")
            await self._create_file_copy(sandbox_path)
        except Exception as e:
            logger.error("Git worktree creation failed", error=str(e))
            raise
    
    async def _create_file_copy(self, sandbox_path: Path) -> None:
        """Create sandbox by copying files."""
        try:
            # Copy entire codebase to sandbox
            shutil.copytree(
                self.main_codebase,
                sandbox_path,
                ignore=shutil.ignore_patterns(
                    '.git', '__pycache__', '*.pyc', '.pytest_cache',
                    'node_modules', '.venv', 'venv', '.env'
                ),
                dirs_exist_ok=True,
            )
            
            logger.info(
                "File copy sandbox created",
                sandbox_path=str(sandbox_path),
                source=str(self.main_codebase),
            )
            
        except Exception as e:
            logger.error("File copy creation failed", error=str(e))
            raise
    
    async def _create_symlink(self, sandbox_path: Path) -> None:
        """Create sandbox using symlinks (read-only)."""
        try:
            sandbox_path.mkdir(parents=True, exist_ok=True)
            
            # Create symlinks for all files and directories
            for item in self.main_codebase.iterdir():
                if item.name.startswith('.'):
                    continue  # Skip hidden files
                
                target = sandbox_path / item.name
                target.symlink_to(item)
            
            logger.info(
                "Symlink sandbox created",
                sandbox_path=str(sandbox_path),
                source=str(self.main_codebase),
            )
            
        except Exception as e:
            logger.error("Symlink creation failed", error=str(e))
            raise
    
    async def cleanup_sandbox(self, sandbox_path: Path) -> bool:
        """
        Clean up a sandbox environment.
        
        Args:
            sandbox_path: Path to the sandbox to clean up
            
        Returns:
            True if cleanup was successful
        """
        try:
            if not sandbox_path.exists():
                return True
            
            # Check if this is a git worktree
            if await self._is_git_worktree(sandbox_path):
                await self._cleanup_git_worktree(sandbox_path)
            else:
                # Regular directory cleanup
                shutil.rmtree(sandbox_path, ignore_errors=True)
            
            logger.info("Sandbox cleaned up", sandbox_path=str(sandbox_path))
            return True
            
        except Exception as e:
            logger.error(
                "Failed to cleanup sandbox",
                sandbox_path=str(sandbox_path),
                error=str(e),
            )
            return False
    
    async def _is_git_worktree(self, sandbox_path: Path) -> bool:
        """Check if path is a git worktree."""
        try:
            import git
            repo = git.Repo(sandbox_path)
            return repo.git_dir != str(sandbox_path / '.git')
        except (ImportError, git.InvalidGitRepositoryError):
            return False
    
    async def _cleanup_git_worktree(self, sandbox_path: Path) -> None:
        """Clean up git worktree and associated branch."""
        try:
            import git
            
            # Get the main repository
            repo = git.Repo(self.main_codebase)
            
            # Remove worktree
            repo.git.worktree("remove", str(sandbox_path), force=True)
            
            # Extract branch name from path
            branch_name = f"sandbox-{sandbox_path.name.replace('session_', '')}"
            
            # Delete the branch if it exists
            try:
                repo.delete_head(branch_name, force=True)
                logger.info("Deleted sandbox branch", branch_name=branch_name)
            except git.GitCommandError:
                # Branch might not exist or already deleted
                pass
                
        except Exception as e:
            logger.error("Git worktree cleanup failed", error=str(e))
            # Fallback to regular directory removal
            if sandbox_path.exists():
                shutil.rmtree(sandbox_path, ignore_errors=True)
    
    def get_sandbox_info(self, sandbox_path: Path) -> dict[str, str]:
        """Get information about a sandbox."""
        if not sandbox_path.exists():
            return {"status": "not_found"}
        
        info = {
            "path": str(sandbox_path),
            "exists": True,
            "type": "unknown",
        }
        
        # Determine sandbox type
        if (sandbox_path / '.git').exists():
            info["type"] = "git_worktree" if self._is_git_worktree(sandbox_path) else "git_clone"
        elif any(item.is_symlink() for item in sandbox_path.iterdir() if item.exists()):
            info["type"] = "symlink"
        else:
            info["type"] = "file_copy"
        
        # Get size information
        try:
            total_size = sum(
                f.stat().st_size for f in sandbox_path.rglob('*') if f.is_file()
            )
            info["size_bytes"] = total_size
            info["size_mb"] = round(total_size / (1024 * 1024), 2)
        except Exception:
            info["size_bytes"] = 0
            info["size_mb"] = 0
        
        return info
    
    def list_sandboxes(self) -> list[dict[str, str]]:
        """List all existing sandboxes."""
        sandboxes = []
        
        if not self.base_dir.exists():
            return sandboxes
        
        for item in self.base_dir.iterdir():
            if item.is_dir() and item.name.startswith("session_"):
                info = self.get_sandbox_info(item)
                info["session_id"] = item.name.replace("session_", "")
                sandboxes.append(info)
        
        return sandboxes
    
    async def cleanup_old_sandboxes(self, max_age_hours: int = 24) -> int:
        """Clean up old sandbox environments."""
        from datetime import datetime, timedelta
        
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        cleaned = 0
        
        for sandbox_info in self.list_sandboxes():
            sandbox_path = Path(sandbox_info["path"])
            
            # Check modification time
            try:
                mtime = datetime.fromtimestamp(sandbox_path.stat().st_mtime)
                if mtime < cutoff:
                    if await self.cleanup_sandbox(sandbox_path):
                        cleaned += 1
            except Exception as e:
                logger.error(
                    "Failed to check sandbox age",
                    sandbox_path=str(sandbox_path),
                    error=str(e),
                )
        
        logger.info("Cleaned up old sandboxes", count=cleaned, max_age_hours=max_age_hours)
        return cleaned