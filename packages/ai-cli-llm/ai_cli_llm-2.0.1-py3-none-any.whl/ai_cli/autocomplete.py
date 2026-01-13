"""
Autocomplete suggestion engine for AI CLI.

Provides intelligent command suggestions as users type.
"""

from typing import List
import os
import sys

# Try to import readline for better autocomplete support
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False


class AutocompleteSuggestions:
    """Generate contextual suggestions for user input"""
    
    # Common command patterns users might start
    COMMAND_PATTERNS = {
        "list": ["list files", "list directories", "list all files", "list recent files"],
        "find": ["find files", "find directories", "find .py files", "find files larger than"],
        "create": ["create file", "create folder", "create directory", "create backup"],
        "delete": ["delete file", "delete folder", "delete all", "delete temporary"],
        "copy": ["copy file", "copy folder", "copy to", "copy and rename"],
        "move": ["move file", "move folder", "move to", "move and rename"],
        "rename": ["rename file", "rename folder", "rename all", "rename with pattern"],
        "show": ["show contents", "show file", "show directory", "show errors"],
        "compress": ["compress folder", "compress files", "compress and save", "create archive"],
        "extract": ["extract files", "extract archive", "extract to folder"],
        "search": ["search for text", "search files", "search recursively"],
        "backup": ["backup folder", "backup files", "backup to", "backup and compress"],
        "remove": ["remove file", "remove folder", "remove temporary", "remove all"],
        "cd": ["cd to", "change directory", "cd home", "cd desktop"],
        "make": ["make folder", "make directory", "make file"],
        "check": ["check file size", "check permissions", "check contents"],
    }
    
    # File operation suggestions based on context
    OPERATION_TYPES = [
        "file",
        "folder",
        "directory",
        "archive",
        "backup",
        "copy",
        "move",
        "delete",
        "create",
        "rename",
        "compress",
    ]
    
    # Common file patterns
    COMMON_PATTERNS = [
        ".py files",
        ".txt files",
        ".log files",
        ".json files",
        ".csv files",
        "larger than 10MB",
        "larger than 1MB",
        "modified today",
        "modified this week",
        "recursively",
    ]
    
    @staticmethod
    def get_suggestions(user_input: str, current_dir: str = ".") -> List[str]:
        """
        Get contextual suggestions for user input.
        
        Args:
            user_input: Partial user input
            current_dir: Current working directory
            
        Returns:
            List of suggested completions
        """
        suggestions = []
        user_lower = user_input.lower().strip()
        
        # If very short, don't suggest yet
        if len(user_lower) < 2:
            return suggestions
        
        # Check for matching command patterns
        for cmd, patterns in AutocompleteSuggestions.COMMAND_PATTERNS.items():
            if cmd.startswith(user_lower[:len(cmd)]):
                suggestions.extend(patterns[:2])  # Add top 2 for each match
        
        # If input contains operation type keywords, suggest file patterns
        for op_type in AutocompleteSuggestions.OPERATION_TYPES:
            if op_type in user_lower:
                # Suggest common patterns for this operation
                pattern_suggestions = [
                    f"{user_input} {pattern}" for pattern in AutocompleteSuggestions.COMMON_PATTERNS
                ]
                suggestions.extend(pattern_suggestions[:3])
        
        # Suggest files/folders in current directory if searching locally
        if "file" in user_lower or "folder" in user_lower or "directory" in user_lower:
            try:
                items = os.listdir(current_dir)
                # Filter to files if "file" mentioned, folders if "folder"/"directory" mentioned
                if "folder" in user_lower or "directory" in user_lower:
                    items = [f for f in items if os.path.isdir(os.path.join(current_dir, f))]
                elif "file" in user_lower:
                    items = [f for f in items if os.path.isfile(os.path.join(current_dir, f))]
                
                # Add directory items as suggestions (limit to 5)
                for item in items[:5]:
                    suggestions.append(f"{user_input} {item}")
            except (PermissionError, OSError):
                pass
        
        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique_suggestions.append(s)
        
        return unique_suggestions[:5]  # Return top 5 suggestions


class ReadlineCompleter:
    """Readline-based autocompletion for real-time suggestions"""
    
    def __init__(self, current_dir: str = "."):
        """Initialize completer with current directory context"""
        self.current_dir = current_dir
        self.matches = []
    
    def complete(self, text: str, state: int) -> str:
        """
        Autocomplete function for readline.
        This is called repeatedly by readline to get the next completion.
        
        Args:
            text: Current text being completed
            state: Index of completion (0 for first, 1 for second, etc.)
        
        Returns:
            Next completion or None
        """
        if state == 0:
            # First call - generate all matches
            self.matches = AutocompleteSuggestions.get_suggestions(text, self.current_dir)
        
        # Return the appropriate match or None
        if state < len(self.matches):
            return self.matches[state]
        return None
    
    def setup_readline(self):
        """Configure readline for autocomplete"""
        if not READLINE_AVAILABLE:
            return
        
        # Set up the completer
        readline.set_completer(self.complete)
        
        # Configure readline options
        readline.parse_and_bind('tab: complete')
        
        # Optional: Set delimiter to space for partial word completion
        readline.set_completer_delims(' \t\n')


def setup_autocomplete(current_dir: str = ".") -> None:
    """
    Set up autocomplete for the CLI session.
    
    Args:
        current_dir: Current working directory for context
    """
    if READLINE_AVAILABLE:
        completer = ReadlineCompleter(current_dir)
        completer.setup_readline()


def get_input_with_autocomplete(prompt: str, current_dir: str = ".") -> str:
    """
    Get input with autocomplete support.
    
    If readline is available, enables tab-completion.
    Otherwise, shows menu-based suggestions that user can select from.
    
    Args:
        prompt: Input prompt to display
        current_dir: Current working directory for suggestions
    
    Returns:
        User input string or selected suggestion
    """
    # Set up readline if available
    if READLINE_AVAILABLE:
        setup_autocomplete(current_dir)
    
    try:
        user_input = input(prompt).strip()
        
        # If no readline, show suggestions and allow selection
        if not READLINE_AVAILABLE and user_input and len(user_input) >= 3:
            suggestions = AutocompleteSuggestions.get_suggestions(user_input, current_dir)
            if suggestions:
                print(f"   💡 Did you mean:")
                for i, suggestion in enumerate(suggestions[:5], 1):
                    print(f"      {i}. {suggestion}")
                
                # Ask user to select
                try:
                    choice = input(f"   Select (1-{len(suggestions)}, or press Enter to use your input): ").strip()
                    if choice and choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(suggestions):
                            user_input = suggestions[idx]
                            print(f"   → Using: {user_input}\n")
                except (ValueError, IndexError):
                    pass  # Use original input
        
        return user_input
    except EOFError:
        return ""
    except KeyboardInterrupt:
        # Re-raise KeyboardInterrupt so main loop can handle it
        raise

