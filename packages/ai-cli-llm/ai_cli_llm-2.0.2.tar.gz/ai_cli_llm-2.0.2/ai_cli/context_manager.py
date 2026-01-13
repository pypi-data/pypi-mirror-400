"""
Context Manager

Tracks execution context to provide intelligent, context-aware command generation:
- Current working directory
- Recent command history
- Recent errors
- Directory contents
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple
from collections import deque
from dataclasses import dataclass


@dataclass
class CommandHistoryEntry:
    """Represents a command in history"""
    user_input: str
    generated_command: str
    success: bool
    error_message: Optional[str] = None


class ContextManager:
    """
    Manages execution context for intelligent command generation.
    Tracks history and environment state.
    """
    
    # Maximum items to track
    MAX_COMMAND_HISTORY = 5
    MAX_ERROR_HISTORY = 3
    
    def __init__(self, initial_directory: Optional[str] = None):
        """
        Initialize context manager.
        
        Args:
            initial_directory: Starting working directory
        """
        self.current_directory = initial_directory or os.getcwd()
        self.command_history: deque = deque(maxlen=self.MAX_COMMAND_HISTORY)
        self.error_history: deque = deque(maxlen=self.MAX_ERROR_HISTORY)
    
    def update_directory(self, new_directory: str):
        """Update current working directory"""
        if os.path.isdir(new_directory):
            self.current_directory = os.path.abspath(new_directory)
    
    def add_command(self, user_input: str, generated_command: str, success: bool, 
                   error_message: Optional[str] = None):
        """
        Add a command to history.
        
        Args:
            user_input: Natural language input from user
            generated_command: Generated shell command
            success: Whether command succeeded
            error_message: Error message if failed
        """
        entry = CommandHistoryEntry(
            user_input=user_input,
            generated_command=generated_command,
            success=success,
            error_message=error_message
        )
        self.command_history.append(entry)
        
        # Track errors separately
        if not success and error_message:
            self.error_history.append({
                'command': generated_command,
                'error': error_message[:200]  # Truncate long errors
            })
    
    def get_recent_commands(self, n: Optional[int] = None) -> List[CommandHistoryEntry]:
        """
        Get recent command history.
        
        Args:
            n: Number of commands to retrieve (defaults to all)
            
        Returns:
            List of recent commands
        """
        if n is None:
            return list(self.command_history)
        return list(self.command_history)[-n:]
    
    def get_recent_errors(self, n: Optional[int] = None) -> List[dict]:
        """
        Get recent errors.
        
        Args:
            n: Number of errors to retrieve (defaults to all)
            
        Returns:
            List of recent errors
        """
        if n is None:
            return list(self.error_history)
        return list(self.error_history)[-n:]
    
    def get_directory_contents(self, max_items: int = 10) -> List[str]:
        """
        Get contents of current directory.
        
        Args:
            max_items: Maximum number of items to return
            
        Returns:
            List of file/folder names in current directory
        """
        try:
            items = []
            with os.scandir(self.current_directory) as entries:
                for entry in entries:
                    if not entry.name.startswith('.'):  # Skip hidden files
                        suffix = '/' if entry.is_dir() else ''
                        items.append(f"{entry.name}{suffix}")
                    if len(items) >= max_items:
                        break
            return items
        except Exception:
            return []
    
    def format_for_llm(self) -> str:
        """
        Format context information for LLM prompt.
        
        Returns:
            Formatted context string to include in LLM prompt
        """
        lines = []
        
        # Current directory
        dir_name = os.path.basename(self.current_directory) or self.current_directory
        lines.append(f"Current Directory: {dir_name}")
        
        # Directory contents (if available)
        contents = self.get_directory_contents(max_items=8)
        if contents:
            lines.append(f"Contents: {', '.join(contents[:8])}")
            if len(contents) > 8:
                lines.append(f"  (and {len(contents) - 8} more...)")
        
        # Recent commands
        recent = self.get_recent_commands(n=3)
        if recent:
            lines.append("\nRecent Commands:")
            for i, entry in enumerate(recent, 1):
                status = "✓" if entry.success else "✗"
                lines.append(f"  {i}. {status} \"{entry.user_input}\" → {entry.generated_command[:40]}...")
        
        # Recent errors
        errors = self.get_recent_errors(n=2)
        if errors:
            lines.append("\nRecent Errors:")
            for err in errors:
                lines.append(f"  • {err['command'][:40]}... → {err['error'][:60]}...")
        
        return "\n".join(lines)
    
    def format_compact(self) -> str:
        """
        Format context in compact form for shorter prompts.
        
        Returns:
            Compact context string
        """
        dir_name = os.path.basename(self.current_directory) or self.current_directory
        context_parts = [f"CWD: {dir_name}"]
        
        # Add recent successful command if exists
        recent = self.get_recent_commands(n=1)
        if recent and recent[0].success:
            context_parts.append(f"Last: {recent[0].generated_command[:30]}...")
        
        return " | ".join(context_parts)
    
    def clear_history(self):
        """Clear command and error history"""
        self.command_history.clear()
        self.error_history.clear()
    
    def get_context_summary(self) -> dict:
        """
        Get context as dictionary for debugging/logging.
        
        Returns:
            Dictionary with context information
        """
        return {
            'current_directory': self.current_directory,
            'command_count': len(self.command_history),
            'error_count': len(self.error_history),
            'recent_commands': [
                {
                    'input': e.user_input,
                    'command': e.generated_command,
                    'success': e.success
                }
                for e in self.get_recent_commands(n=3)
            ]
        }
