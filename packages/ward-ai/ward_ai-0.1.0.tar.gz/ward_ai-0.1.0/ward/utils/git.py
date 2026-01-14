"""Git operations helper utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import structlog

logger = structlog.get_logger()


class GitHelper:
    """Helper class for Git operations in sandbox environments."""
    
    def __init__(self, repo_path: Path):
        """
        Initialize Git helper.
        
        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = repo_path
        self._repo: Optional[object] = None
    
    @property
    def repo(self):
        """Lazy-load git repository object."""
        if self._repo is None:
            try:
                import git
                self._repo = git.Repo(self.repo_path)
            except ImportError:
                raise RuntimeError("GitPython not installed. Run: pip install GitPython")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize git repository: {e}")
        return self._repo
    
    def is_git_repository(self) -> bool:
        """Check if path is a valid git repository."""
        try:
            import git
            git.Repo(self.repo_path)
            return True
        except (ImportError, Exception):
            return False
    
    def get_current_branch(self) -> str:
        """Get current branch name."""
        try:
            return self.repo.active_branch.name
        except Exception as e:
            logger.warning("Failed to get current branch", error=str(e))
            return "unknown"
    
    def get_current_commit(self) -> str:
        """Get current commit hash."""
        try:
            return self.repo.head.commit.hexsha
        except Exception as e:
            logger.warning("Failed to get current commit", error=str(e))
            return "unknown"
    
    def create_branch(self, branch_name: str, from_commit: Optional[str] = None) -> bool:
        """
        Create a new branch.
        
        Args:
            branch_name: Name of the new branch
            from_commit: Commit to branch from (default: HEAD)
            
        Returns:
            True if branch was created successfully
        """
        try:
            if from_commit:
                commit = self.repo.commit(from_commit)
                self.repo.create_head(branch_name, commit)
            else:
                self.repo.create_head(branch_name)
            
            logger.info("Created git branch", branch_name=branch_name)
            return True
            
        except Exception as e:
            logger.error("Failed to create branch", branch_name=branch_name, error=str(e))
            return False
    
    def checkout_branch(self, branch_name: str) -> bool:
        """
        Checkout a branch.
        
        Args:
            branch_name: Name of the branch to checkout
            
        Returns:
            True if checkout was successful
        """
        try:
            self.repo.heads[branch_name].checkout()
            logger.info("Checked out branch", branch_name=branch_name)
            return True
            
        except Exception as e:
            logger.error("Failed to checkout branch", branch_name=branch_name, error=str(e))
            return False
    
    def delete_branch(self, branch_name: str, force: bool = False) -> bool:
        """
        Delete a branch.
        
        Args:
            branch_name: Name of the branch to delete
            force: Force delete even if not merged
            
        Returns:
            True if branch was deleted successfully
        """
        try:
            self.repo.delete_head(branch_name, force=force)
            logger.info("Deleted git branch", branch_name=branch_name)
            return True
            
        except Exception as e:
            logger.error("Failed to delete branch", branch_name=branch_name, error=str(e))
            return False
    
    def add_files(self, file_patterns: list[str] | None = None) -> bool:
        """
        Add files to git index.
        
        Args:
            file_patterns: List of file patterns to add (default: all files)
            
        Returns:
            True if files were added successfully
        """
        try:
            if file_patterns:
                self.repo.index.add(file_patterns)
            else:
                self.repo.git.add(A=True)  # Add all files
            
            logger.info("Added files to git index", patterns=file_patterns or ["all"])
            return True
            
        except Exception as e:
            logger.error("Failed to add files", error=str(e))
            return False
    
    def commit_changes(
        self,
        message: str,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
    ) -> Optional[str]:
        """
        Commit staged changes.
        
        Args:
            message: Commit message
            author_name: Author name (optional)
            author_email: Author email (optional)
            
        Returns:
            Commit hash if successful, None otherwise
        """
        try:
            # Check if there are changes to commit
            if not self.repo.is_dirty(staged=True):
                logger.info("No staged changes to commit")
                return None
            
            # Set author if provided
            if author_name and author_email:
                actor = f"{author_name} <{author_email}>"
                commit = self.repo.index.commit(message, author=actor)
            else:
                commit = self.repo.index.commit(message)
            
            logger.info("Committed changes", commit_hash=commit.hexsha, message=message)
            return commit.hexsha
            
        except Exception as e:
            logger.error("Failed to commit changes", error=str(e))
            return None
    
    def get_diff(self, commit1: Optional[str] = None, commit2: Optional[str] = None) -> str:
        """
        Get diff between commits or working directory.
        
        Args:
            commit1: First commit (default: HEAD)
            commit2: Second commit (default: working directory)
            
        Returns:
            Diff as string
        """
        try:
            if commit1 and commit2:
                diff = self.repo.git.diff(commit1, commit2)
            elif commit1:
                diff = self.repo.git.diff(commit1)
            else:
                diff = self.repo.git.diff()
            
            return diff
            
        except Exception as e:
            logger.error("Failed to get diff", error=str(e))
            return f"Error getting diff: {e}"
    
    def get_status(self) -> dict[str, list[str]]:
        """
        Get repository status.
        
        Returns:
            Dictionary with file status categories
        """
        try:
            status = {
                "staged": [],
                "modified": [],
                "untracked": [],
                "deleted": [],
            }
            
            # Get staged files
            staged_files = self.repo.git.diff("--cached", "--name-only").splitlines()
            status["staged"] = [f for f in staged_files if f]
            
            # Get modified files
            modified_files = self.repo.git.diff("--name-only").splitlines()
            status["modified"] = [f for f in modified_files if f]
            
            # Get untracked files
            untracked_files = self.repo.untracked_files
            status["untracked"] = untracked_files
            
            return status
            
        except Exception as e:
            logger.error("Failed to get status", error=str(e))
            return {"error": [str(e)]}
    
    def reset_hard(self, commit: Optional[str] = None) -> bool:
        """
        Reset repository to a specific commit (hard reset).
        
        Args:
            commit: Commit to reset to (default: HEAD)
            
        Returns:
            True if reset was successful
        """
        try:
            if commit:
                self.repo.git.reset("--hard", commit)
            else:
                self.repo.git.reset("--hard", "HEAD")
            
            logger.info("Hard reset completed", commit=commit or "HEAD")
            return True
            
        except Exception as e:
            logger.error("Failed to reset", error=str(e))
            return False
    
    def clean_untracked(self, force: bool = True) -> bool:
        """
        Clean untracked files and directories.
        
        Args:
            force: Force clean without confirmation
            
        Returns:
            True if clean was successful
        """
        try:
            if force:
                self.repo.git.clean("-fd")
            else:
                self.repo.git.clean("-d")
            
            logger.info("Cleaned untracked files")
            return True
            
        except Exception as e:
            logger.error("Failed to clean untracked files", error=str(e))
            return False
    
    def create_worktree(self, path: Path, branch_name: str) -> bool:
        """
        Create a git worktree.
        
        Args:
            path: Path for the new worktree
            branch_name: Branch name for the worktree
            
        Returns:
            True if worktree was created successfully
        """
        try:
            self.repo.git.worktree("add", str(path), branch_name)
            logger.info("Created git worktree", path=str(path), branch=branch_name)
            return True
            
        except Exception as e:
            logger.error("Failed to create worktree", error=str(e))
            return False
    
    def remove_worktree(self, path: Path, force: bool = True) -> bool:
        """
        Remove a git worktree.
        
        Args:
            path: Path of the worktree to remove
            force: Force removal
            
        Returns:
            True if worktree was removed successfully
        """
        try:
            if force:
                self.repo.git.worktree("remove", str(path), "--force")
            else:
                self.repo.git.worktree("remove", str(path))
            
            logger.info("Removed git worktree", path=str(path))
            return True
            
        except Exception as e:
            logger.error("Failed to remove worktree", error=str(e))
            return False
    
    def get_repository_info(self) -> dict[str, str]:
        """Get general repository information."""
        try:
            return {
                "current_branch": self.get_current_branch(),
                "current_commit": self.get_current_commit(),
                "repo_path": str(self.repo_path),
                "is_dirty": str(self.repo.is_dirty()),
                "has_staged": str(self.repo.is_dirty(staged=True)),
                "remote_url": self.repo.remotes.origin.url if self.repo.remotes else "none",
            }
        except Exception as e:
            logger.error("Failed to get repository info", error=str(e))
            return {"error": str(e)}