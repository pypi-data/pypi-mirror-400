"""
Local Command Executor

Executes validated commands via subprocess.
This is the ONLY place where commands are actually run.

Features:
- Captures stdout and stderr
- Timeout protection
- Working directory support
- Output formatting
- PowerShell support on Windows
- Undo tracking for file operations
"""

import subprocess
import os
import platform
from typing import Optional
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    """Result of command execution"""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    command: str
    error: Optional[str] = None


class CommandExecutor:
    """
    Safe command executor with output capture and timeout.
    
    ⚠️  This class EXECUTES commands. It should only be called
    AFTER user confirmation and safety checks.
    """
    
    def __init__(self, timeout: int = 30, working_dir: Optional[str] = None, undo_manager=None):
        """
        Initialize executor.
        
        Args:
            timeout: Maximum seconds to wait for command completion
            working_dir: Working directory for command execution
            undo_manager: Optional UndoManager instance for tracking file operations
        """
        self.timeout = timeout
        self.working_dir = working_dir or os.getcwd()
        self.is_windows = platform.system() == "Windows"
        self.undo_manager = undo_manager
    
    def execute(self, command: str) -> ExecutionResult:
        """
        Execute a command and return the result.
        
        Args:
            command: The command string to execute
            
        Returns:
            ExecutionResult with success status, output, and error info
        """
        try:
            # On Windows, use PowerShell to execute commands
            if self.is_windows:
                # Wrap command for PowerShell execution
                full_command = ["powershell", "-NoProfile", "-Command", command]
                result = subprocess.run(
                    full_command,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=self.working_dir
                )
            else:
                # On Unix, use shell=True
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=self.working_dir
                )
            
            # After successful execution, check if this was a directory change command
            if result.returncode == 0:
                self._update_working_dir(command)
                
                # Track operation for undo if undo_manager is available
                if self.undo_manager:
                    self.undo_manager.track_operation(command, self.working_dir, success=True)
            
            return ExecutionResult(
                success=result.returncode == 0,
                stdout=result.stdout.strip(),
                stderr=result.stderr.strip(),
                return_code=result.returncode,
                command=command
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                command=command,
                error=f"⏱️  Command timed out after {self.timeout} seconds"
            )
        except FileNotFoundError as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                command=command,
                error=f"🔍 Command not found: {str(e)}"
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                command=command,
                error=f"❌ Execution failed: {str(e)}"
            )
    
    def _update_working_dir(self, command: str) -> None:
        """
        Update the working directory if command was a cd/Set-Location command.
        
        Tracks directory changes across subprocess calls.
        """
        import re
        
        command_lower = command.lower().strip()
        
        # PowerShell: Set-Location -Path "path" or Set-Location "path" or cd "path"
        # Match patterns like:
        #  - Set-Location -Path "ai_cli"
        #  - Set-Location "ai_cli"
        #  - cd "ai_cli"
        #  - cd ai_cli
        
        # Try Set-Location with -Path parameter
        pwd_match = re.search(r'set-location\s+-path\s+["\']?([^\s"\']+)["\']?', command_lower)
        
        # Try Set-Location without -Path parameter  
        if not pwd_match:
            pwd_match = re.search(r'set-location\s+["\']?([^\s"\']+)["\']?', command_lower)
        
        # Try cd command
        if not pwd_match:
            pwd_match = re.search(r'cd\s+["\']?([^\s"\']+)["\']?', command_lower)
        
        if pwd_match:
            new_dir = pwd_match.group(1).strip().strip('"').strip("'")
            try:
                # Handle relative paths
                if os.path.isabs(new_dir):
                    full_path = new_dir
                else:
                    full_path = os.path.join(self.working_dir, new_dir)
                
                # Normalize the path
                full_path = os.path.abspath(full_path)
                
                # Verify the directory exists
                if os.path.isdir(full_path):
                    self.working_dir = full_path
                    print(f"📁 Changed directory to: {full_path}")
            except Exception as e:
                pass  # If path resolution fails, keep the old directory
            except Exception:
                pass  # If path resolution fails, keep the old directory
    
    def format_output(self, result: ExecutionResult) -> str:
        """Format execution result for display"""
        output_parts = []
        
        if result.error:
            output_parts.append(result.error)
        elif result.success:
            if result.stdout:
                output_parts.append(result.stdout)
            else:
                output_parts.append("✅ Command completed successfully (no output)")
        else:
            if result.stderr:
                output_parts.append(f"❌ Error:\n{result.stderr}")
            elif result.stdout:
                output_parts.append(result.stdout)
            else:
                output_parts.append(f"❌ Command failed with exit code {result.return_code}")
        
        return "\n".join(output_parts)


# ═══════════════════════════════════════════════════════════════════════
# Legacy function for backward compatibility
# ═══════════════════════════════════════════════════════════════════════
def execute(command: str) -> str:
    """
    Legacy execution function.
    Execute a command and return output string.
    """
    executor = CommandExecutor()
    result = executor.execute(command)
    return executor.format_output(result)


# Create default instance
default_executor = CommandExecutor()
