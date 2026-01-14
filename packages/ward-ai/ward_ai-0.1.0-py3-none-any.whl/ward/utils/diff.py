"""Advanced diff generation utilities."""

from __future__ import annotations

import difflib
from pathlib import Path
from typing import Any

from ..core.session import FileChange, Session


class DiffGenerator:
    """Advanced diff generation for session changes."""
    
    @staticmethod
    def generate_unified_diff(file_change: FileChange) -> str:
        """Generate unified diff for a single file change."""
        if file_change.operation == "delete":
            return f"--- {file_change.path} (deleted)\n+++ /dev/null\n"
        
        if file_change.operation == "create":
            if not file_change.new_content:
                return f"--- /dev/null\n+++ {file_change.path} (empty file)\n"
            
            lines = []
            for i, line in enumerate(file_change.new_content.splitlines(), 1):
                lines.append(f"+{i:4d}: {line}")
            return f"--- /dev/null\n+++ {file_change.path}\n" + "\n".join(lines)
        
        # Modify operation
        if not file_change.original_content or not file_change.new_content:
            return f"--- {file_change.path} (binary or empty)\n+++ {file_change.path}\n"
        
        original_lines = file_change.original_content.splitlines(keepends=True)
        new_lines = file_change.new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            new_lines,
            fromfile=f"a/{file_change.path}",
            tofile=f"b/{file_change.path}",
            lineterm="",
        )
        
        return "\n".join(diff)
    
    @staticmethod
    def generate_side_by_side_diff(file_change: FileChange, width: int = 80) -> str:
        """Generate side-by-side diff for a file change."""
        if file_change.operation == "delete":
            return f"File deleted: {file_change.path}"
        
        if file_change.operation == "create":
            return f"File created: {file_change.path}\n" + (file_change.new_content or "")
        
        if not file_change.original_content or not file_change.new_content:
            return f"Binary or empty file: {file_change.path}"
        
        original_lines = file_change.original_content.splitlines()
        new_lines = file_change.new_content.splitlines()
        
        # Use difflib's side-by-side formatter
        differ = difflib.HtmlDiff()
        html_diff = differ.make_table(
            original_lines,
            new_lines,
            fromdesc=f"Original {file_change.path}",
            todesc=f"Modified {file_change.path}",
        )
        
        # Convert HTML to text (simplified)
        # In a real implementation, you might want to use a proper HTML-to-text converter
        return html_diff.replace("<", "&lt;").replace(">", "&gt;")
    
    @staticmethod
    def generate_summary_diff(session: Session) -> dict[str, Any]:
        """Generate summary statistics for session changes."""
        if not session.file_changes:
            return {
                "total_files": 0,
                "files_created": 0,
                "files_modified": 0,
                "files_deleted": 0,
                "total_lines_added": 0,
                "total_lines_removed": 0,
                "net_lines_changed": 0,
                "files": [],
            }
        
        files_created = 0
        files_modified = 0
        files_deleted = 0
        total_lines_added = 0
        total_lines_removed = 0
        
        file_summaries = []
        
        for fc in session.file_changes:
            if fc.operation == "create":
                files_created += 1
            elif fc.operation == "modify":
                files_modified += 1
            elif fc.operation == "delete":
                files_deleted += 1
            
            lines_added = fc.lines_added
            lines_removed = fc.lines_removed
            
            total_lines_added += lines_added
            total_lines_removed += lines_removed
            
            file_summaries.append({
                "path": str(fc.path),
                "operation": fc.operation,
                "lines_added": lines_added,
                "lines_removed": lines_removed,
                "net_change": lines_added - lines_removed,
                "timestamp": fc.timestamp.isoformat(),
            })
        
        return {
            "total_files": len(session.file_changes),
            "files_created": files_created,
            "files_modified": files_modified,
            "files_deleted": files_deleted,
            "total_lines_added": total_lines_added,
            "total_lines_removed": total_lines_removed,
            "net_lines_changed": total_lines_added - total_lines_removed,
            "files": file_summaries,
        }
    
    @staticmethod
    def generate_git_style_diff(session: Session) -> str:
        """Generate git-style diff for all changes in session."""
        if not session.file_changes:
            return "No changes in this session."
        
        diff_parts = []
        
        # Add header
        diff_parts.append(f"Session: {session.id}")
        diff_parts.append(f"Task: {session.task_description}")
        diff_parts.append(f"Files changed: {len(session.file_changes)}")
        diff_parts.append("")
        
        # Add individual file diffs
        for fc in session.file_changes:
            file_diff = DiffGenerator.generate_unified_diff(fc)
            diff_parts.append(file_diff)
            diff_parts.append("")
        
        return "\n".join(diff_parts)
    
    @staticmethod
    def generate_markdown_diff(session: Session) -> str:
        """Generate markdown-formatted diff report."""
        if not session.file_changes:
            return "## No Changes\n\nNo files were modified in this session."
        
        summary = DiffGenerator.generate_summary_diff(session)
        
        md_parts = [
            f"# Session Changes: {session.task_description}",
            "",
            "## Summary",
            "",
            f"- **Files changed:** {summary['total_files']}",
            f"- **Created:** {summary['files_created']}",
            f"- **Modified:** {summary['files_modified']}",
            f"- **Deleted:** {summary['files_deleted']}",
            f"- **Lines added:** +{summary['total_lines_added']}",
            f"- **Lines removed:** -{summary['total_lines_removed']}",
            f"- **Net change:** {summary['net_lines_changed']:+d}",
            "",
            "## File Changes",
            "",
        ]
        
        for fc in session.file_changes:
            md_parts.extend([
                f"### {fc.operation.title()}: `{fc.path}`",
                "",
                f"- **Operation:** {fc.operation}",
                f"- **Lines added:** +{fc.lines_added}",
                f"- **Lines removed:** -{fc.lines_removed}",
                f"- **Timestamp:** {fc.timestamp.isoformat()}",
                "",
            ])
            
            if fc.operation != "delete" and fc.new_content:
                # Add code block with changes
                md_parts.extend([
                    "```diff",
                    DiffGenerator.generate_unified_diff(fc),
                    "```",
                    "",
                ])
        
        return "\n".join(md_parts)
    
    @staticmethod
    def generate_compact_diff(session: Session, max_lines: int = 50) -> str:
        """Generate compact diff suitable for AI feedback."""
        if not session.file_changes:
            return "No changes made."
        
        summary = DiffGenerator.generate_summary_diff(session)
        
        # Start with summary
        compact = [
            f"📊 {summary['total_files']} files: "
            f"+{summary['files_created']} "
            f"~{summary['files_modified']} "
            f"-{summary['files_deleted']} "
            f"({summary['net_lines_changed']:+d} lines)"
        ]
        
        # Add file list
        for fc in session.file_changes[:5]:  # Limit to first 5 files
            op_emoji = {"create": "➕", "modify": "📝", "delete": "❌"}
            emoji = op_emoji.get(fc.operation, "📄")
            compact.append(f"{emoji} {fc.path} ({fc.lines_added:+d}/-{fc.lines_removed})")
        
        if len(session.file_changes) > 5:
            compact.append(f"... and {len(session.file_changes) - 5} more files")
        
        return "\n".join(compact)