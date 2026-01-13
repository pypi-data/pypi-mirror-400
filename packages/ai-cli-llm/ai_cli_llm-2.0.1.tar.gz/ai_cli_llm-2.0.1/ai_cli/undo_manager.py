"""
Undo/Rollback Manager

Tracks file operations and provides undo capability for:
- Move/Rename operations
- Copy operations
- Delete operations (moves to trash)
- Directory creation
"""

import os
import re
import json
import shutil
import platform
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from collections import deque


@dataclass
class FileOperation:
    """Represents a tracked file operation that can be undone"""
    timestamp: str
    operation_type: str  # 'move', 'copy', 'delete', 'mkdir', 'unknown'
    command: str
    working_dir: str
    source_paths: List[str]
    dest_paths: List[str]
    metadata: Dict[str, Any]  # Additional info like file sizes, hashes
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FileOperation':
        """Create from dictionary"""
        return cls(**data)


class UndoManager:
    """
    Manages undo stack for file operations.
    Provides rollback capability for supported commands.
    """
    
    # Maximum number of operations to keep in undo stack
    MAX_UNDO_STACK = 20
    
    # Platform-specific command patterns
    WINDOWS_PATTERNS = {
        'move': [
            # Move-Item with named parameters
            r'move-item\s+-path\s+["\']?([^\s"\']+)["\']?\s+-destination\s+["\']?([^\s"\']+)["\']?',
            # Move-Item with positional arguments
            r'move-item\s+["\']?([^\s"\']+)["\']?\s+["\']?([^\s"\']+)["\']?',
            # move with positional arguments
            r'move\s+["\']?([^\s"\']+)["\']?\s+["\']?([^\s"\']+)["\']?',
            # mv with positional arguments
            r'mv\s+["\']?([^\s"\']+)["\']?\s+["\']?([^\s"\']+)["\']?',
            # rename-item with named parameters
            r'rename-item\s+-path\s+["\']?([^\s"\']+)["\']?\s+-newname\s+["\']?([^\s"\']+)["\']?',
            # rename-item with positional arguments
            r'rename-item\s+["\']?([^\s"\']+)["\']?\s+["\']?([^\s"\']+)["\']?',
        ],
        'copy': [
            # Copy-Item with named parameters
            r'copy-item\s+-path\s+["\']?([^\s"\']+)["\']?\s+-destination\s+["\']?([^\s"\']+)["\']?',
            # Copy-Item with positional arguments
            r'copy-item\s+["\']?([^\s"\']+)["\']?\s+["\']?([^\s"\']+)["\']?',
            # copy with positional arguments
            r'copy\s+["\']?([^\s"\']+)["\']?\s+["\']?([^\s"\']+)["\']?',
            # cp with positional arguments
            r'cp\s+["\']?([^\s"\']+)["\']?\s+["\']?([^\s"\']+)["\']?',
        ],
        'delete': [
            # Remove-Item with named parameters
            r'remove-item\s+-path\s+["\']?([^\s"\']+)["\']?',
            # Remove-Item with positional arguments
            r'remove-item\s+["\']?([^\s"\']+)["\']?',
            # del with positional arguments
            r'del\s+["\']?([^\s"\']+)["\']?',
            # rm with positional arguments
            r'rm\s+["\']?([^\s"\']+)["\']?',
        ],
        'mkdir': [
            # New-Item with named parameters
            r'new-item\s+-path\s+["\']?([^\s"\']+)["\']?\s+-itemtype\s+directory',
            # New-Item with positional arguments
            r'new-item\s+["\']?([^\s"\']+)["\']?\s+-itemtype\s+directory',
            # mkdir with positional arguments
            r'mkdir\s+["\']?([^\s"\']+)["\']?',
        ],
    }
    
    UNIX_PATTERNS = {
        'move': [
            r'mv\s+["\']?([^\s"\']+)["\']?\s+["\']?([^\s"\']+)["\']?',
        ],
        'copy': [
            r'cp\s+(?:-r\s+)?["\']?([^\s"\']+)["\']?\s+["\']?([^\s"\']+)["\']?',
        ],
        'delete': [
            r'rm\s+(?:-rf?\s+)?["\']?([^\s"\']+)["\']?',
        ],
        'mkdir': [
            r'mkdir\s+(?:-p\s+)?["\']?([^\s"\']+)["\']?',
        ],
    }
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize undo manager.
        
        Args:
            config_dir: Directory to store undo stack and trash. Defaults to ~/.ai_cli
        """
        self.config_dir = config_dir or Path.home() / '.ai_cli'
        self.trash_dir = self.config_dir / 'trash'
        self.undo_stack_file = self.config_dir / 'undo_stack.json'
        
        # Create directories if they don't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.trash_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize undo stack
        self.undo_stack: deque = deque(maxlen=self.MAX_UNDO_STACK)
        self._load_stack()
        
        # Determine platform patterns
        self.is_windows = platform.system() == 'Windows'
        self.patterns = self.WINDOWS_PATTERNS if self.is_windows else self.UNIX_PATTERNS
    
    def _load_stack(self):
        """Load undo stack from disk"""
        if self.undo_stack_file.exists():
            try:
                with open(self.undo_stack_file, 'r') as f:
                    data = json.load(f)
                    self.undo_stack = deque(
                        [FileOperation.from_dict(op) for op in data],
                        maxlen=self.MAX_UNDO_STACK
                    )
            except Exception as e:
                print(f"⚠️  Failed to load undo stack: {e}")
                self.undo_stack = deque(maxlen=self.MAX_UNDO_STACK)
    
    def _save_stack(self):
        """Save undo stack to disk"""
        try:
            with open(self.undo_stack_file, 'w') as f:
                json.dump([op.to_dict() for op in self.undo_stack], f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save undo stack: {e}")
    
    def parse_command(self, command: str, working_dir: str) -> Optional[FileOperation]:
        """
        Parse command to detect file operations.
        
        Args:
            command: The shell command to parse
            working_dir: Current working directory
            
        Returns:
            FileOperation if detected, None otherwise
        """
        command_lower = command.lower().strip()
        
        # Try to match each operation type
        for op_type, pattern_list in self.patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, command_lower, re.IGNORECASE)
                if match:
                    # Extract paths
                    groups = match.groups()
                    
                    if op_type in ['move', 'copy']:
                        # Two paths: source and destination
                        source = self._resolve_path(groups[0], working_dir)
                        dest = self._resolve_path(groups[1], working_dir)
                        
                        return FileOperation(
                            timestamp=datetime.now().isoformat(),
                            operation_type=op_type,
                            command=command,
                            working_dir=working_dir,
                            source_paths=[source],
                            dest_paths=[dest],
                            metadata=self._capture_metadata([source])
                        )
                    
                    elif op_type in ['delete', 'mkdir']:
                        # One path
                        path = self._resolve_path(groups[0], working_dir)
                        
                        return FileOperation(
                            timestamp=datetime.now().isoformat(),
                            operation_type=op_type,
                            command=command,
                            working_dir=working_dir,
                            source_paths=[path],
                            dest_paths=[],
                            metadata=self._capture_metadata([path]) if op_type == 'delete' else {}
                        )
        
        return None
    
    def _resolve_path(self, path: str, working_dir: str) -> str:
        """Convert relative path to absolute path"""
        path = path.strip('"').strip("'")
        if not os.path.isabs(path):
            path = os.path.join(working_dir, path)
        return os.path.normpath(path)
    
    def _capture_metadata(self, paths: List[str]) -> Dict[str, Any]:
        """Capture file metadata for verification"""
        metadata = {}
        for path in paths:
            if os.path.exists(path):
                stat = os.stat(path)
                metadata[path] = {
                    'exists': True,
                    'is_dir': os.path.isdir(path),
                    'size': stat.st_size if not os.path.isdir(path) else 0,
                    'mtime': stat.st_mtime,
                }
            else:
                metadata[path] = {'exists': False}
        return metadata
    
    def track_operation(self, command: str, working_dir: str, success: bool):
        """
        Track a command execution for potential undo.
        
        Args:
            command: The executed command
            working_dir: Working directory at execution time
            success: Whether the command succeeded
        """
        if not success:
            return  # Don't track failed operations
        
        operation = self.parse_command(command, working_dir)
        if operation:
            self.undo_stack.append(operation)
            self._save_stack()
        # Debug: Log operations that couldn't be parsed
        # (comment out in production)
        # else:
        #     print(f"[DEBUG] Undo: No match for: {command[:50]}")
    
    def can_undo(self) -> bool:
        """Check if there are operations to undo"""
        return len(self.undo_stack) > 0
    
    def get_undo_stack(self) -> List[FileOperation]:
        """Get list of operations that can be undone"""
        return list(self.undo_stack)
    
    def rollback_last(self) -> bool:
        """
        Undo the last file operation.
        
        Returns:
            True if undo succeeded, False otherwise
        """
        if not self.can_undo():
            print("❌ No operations to undo")
            return False
        
        operation = self.undo_stack.pop()
        success = self._perform_undo(operation)
        
        if success:
            self._save_stack()
            print(f"✅ Undone: {operation.operation_type} operation")
            print(f"   Command: {operation.command[:60]}...")
        else:
            # Put it back if undo failed
            self.undo_stack.append(operation)
            print(f"❌ Failed to undo operation")
        
        return success
    
    def _perform_undo(self, operation: FileOperation) -> bool:
        """Execute the undo operation"""
        try:
            if operation.operation_type == 'move':
                # Move back from dest to source
                source = operation.source_paths[0]
                dest = operation.dest_paths[0]
                
                # Handle case where destination is a directory
                # If original move was to a directory, the actual file is inside it
                actual_dest = dest
                if os.path.isdir(dest) and not os.path.isfile(dest):
                    # File is inside the directory with its original name
                    actual_dest = os.path.join(dest, os.path.basename(source))
                
                if os.path.exists(actual_dest) and not os.path.exists(source):
                    shutil.move(actual_dest, source)
                    print(f"   Moved back: {actual_dest} → {source}")
                    return True
                else:
                    if not os.path.exists(actual_dest):
                        print(f"   ⚠️  Cannot undo: file not found at {actual_dest}")
                    else:
                        print(f"   ⚠️  Cannot undo: source already exists at {source}")
                    return False
            
            elif operation.operation_type == 'copy':
                # Delete the copied file
                dest = operation.dest_paths[0]
                
                if os.path.exists(dest):
                    if os.path.isdir(dest):
                        shutil.rmtree(dest)
                    else:
                        os.remove(dest)
                    print(f"   Removed copy: {dest}")
                    return True
                else:
                    print(f"   ⚠️  Copy already removed")
                    return False
            
            elif operation.operation_type == 'delete':
                # Restore from trash
                source = operation.source_paths[0]
                trash_name = f"{datetime.fromisoformat(operation.timestamp).strftime('%Y%m%d_%H%M%S')}_{os.path.basename(source)}"
                trash_path = self.trash_dir / trash_name
                
                if trash_path.exists() and not os.path.exists(source):
                    shutil.move(str(trash_path), source)
                    print(f"   Restored: {source}")
                    return True
                else:
                    print(f"   ⚠️  Cannot restore: file not in trash or already exists")
                    return False
            
            elif operation.operation_type == 'mkdir':
                # Remove the created directory (if empty)
                path = operation.source_paths[0]
                
                if os.path.exists(path) and os.path.isdir(path):
                    if not os.listdir(path):  # Only delete if empty
                        os.rmdir(path)
                        print(f"   Removed directory: {path}")
                        return True
                    else:
                        print(f"   ⚠️  Directory not empty, cannot undo")
                        return False
                else:
                    print(f"   ⚠️  Directory already removed")
                    return False
            
            return False
            
        except Exception as e:
            print(f"   ❌ Undo error: {e}")
            return False
    
    def show_undo_stack(self):
        """Display the undo stack to user"""
        if not self.can_undo():
            print("📋 Undo stack is empty")
            return
        
        print(f"📋 Undo Stack ({len(self.undo_stack)} operations):")
        print("─" * 60)
        
        for i, op in enumerate(reversed(list(self.undo_stack)), 1):
            time_str = datetime.fromisoformat(op.timestamp).strftime('%H:%M:%S')
            print(f"{i}. [{time_str}] {op.operation_type.upper()}")
            print(f"   {op.command[:55]}...")
            if op.source_paths:
                print(f"   From: {op.source_paths[0]}")
            if op.dest_paths:
                print(f"   To: {op.dest_paths[0]}")
            print()
