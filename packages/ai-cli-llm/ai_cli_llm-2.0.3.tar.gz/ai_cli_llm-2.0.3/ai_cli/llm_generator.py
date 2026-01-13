"""
LLM Command Generator (Proposal Mode Only)

This module interfaces with an LLM to generate command proposals.
❌ LLM NEVER executes commands
✅ LLM ONLY suggests commands

Supports multiple backends:
- Google Gemini API
- Local LLM via Ollama
"""

import json
import os
import platform
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env from project root
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# Try to import google generativeai, but make it optional
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Try to import requests for Ollama
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class CommandProposal:
    """Structured command proposal from LLM"""
    command: str
    risk_level: str  # low, medium, high, critical
    explanation: str
    raw_response: Optional[str] = None
    error: Optional[str] = None


class LLMCommandGenerator:
    """
    LLM-based command generator that ONLY proposes commands.
    Never executes anything - that's the executor's job after user confirmation.
    """
    
    SYSTEM_PROMPT = """You are a command-line assistant. Your ONLY job is to translate natural language requests into shell commands.

RULES:
1. Output ONLY valid JSON with this exact structure:
   {
     "command": "<the shell command>",
     "risk_level": "<low|medium|high|critical>",
     "explanation": "<brief explanation of what the command does>"
   }

2. Risk Level Guidelines:
   - low: read-only commands (ls, cat, pwd, echo, find without -exec)
   - medium: creates/modifies files but recoverable (mkdir, cp, touch, tar)
   - high: deletes files or modifies system (rm, mv to overwrite, chmod)
   - critical: recursive delete, system commands, format, shutdown

3. CURRENT SYSTEM INFO:
   - OS: {os_info}
   - Shell: {shell_info}
   
4. Generate commands appropriate for this OS/shell.

5. If the request is unclear or dangerous, still provide a command but set appropriate risk_level and explain concerns in the explanation.

6. NEVER include markdown formatting. ONLY output raw JSON.

7. For PowerShell, always generate single-line commands using pipes (|) for file search/output tasks. Do not use variables for multi-step operations. For example, use:
   Get-ChildItem -Recurse -File | Where-Object { $_.Length -gt 10MB } | Out-File -FilePath "large_files.txt"
   instead of using variables like $largeFiles in multiple steps.
"""

    def __init__(self, backend: str = "gemini", model: str = None, api_key: str = None, base_url: str = None, context_manager=None):
        """
        Initialize the LLM generator.
        
        Args:
            backend: "gemini" or "ollama"
            model: Model name (default: gemini-1.5-flash for gemini, llama2 for ollama)
            api_key: API key (reads from .env GEMINI_API_KEY if not provided)
            base_url: Custom base URL (for Ollama: http://localhost:11434)
            context_manager: Optional ContextManager instance for context-aware prompts
        """
        self.backend = backend
        
        # Load API key from .env file (already loaded via load_dotenv at module level)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.base_url = base_url
        self.context_manager = context_manager
        
        # Set default models per backend
        if model:
            self.model = model
        elif backend == "gemini":
            self.model = "gemini-2.5-flash"
        elif backend == "ollama":
            self.model = "llama2"
        else:
            self.model = "gemini-2.5-flash"
        
        # Get system info for context
        self.os_info = f"{platform.system()} {platform.release()}"
        self.shell_info = "PowerShell" if platform.system() == "Windows" else os.getenv("SHELL", "/bin/bash")
        
        # Initialize Gemini if using that backend
        if self.backend == "gemini" and GEMINI_AVAILABLE and self.api_key:
            genai.configure(api_key=self.api_key)
    
    def _get_system_prompt(self) -> str:
        """Generate system prompt with current OS info"""
        return self.SYSTEM_PROMPT.format(
            os_info=self.os_info,
            shell_info=self.shell_info
        )
    
    def _call_gemini(self, user_input: str) -> str:
        """Call Google Gemini API"""
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        
        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY environment variable.")
        
        try:
            # Configure the model - with specific settings to get complete JSON
            # Use Gemini 1.5 Flash which is more reliable for JSON output
            model = genai.GenerativeModel(
                model_name=self.model,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 2048,  # Increased to 2048 for longer commands
                    "top_p": 0.95,
                }
            )
            
            # Emphasize brevity and simplicity
            full_prompt = f"""Output ONLY valid JSON on a single line. Keep commands SHORT and SIMPLE.

{{"command":"<SHORT shell command>","risk_level":"<low|medium|high|critical>","explanation":"<brief>"}}

IMPORTANT: Use the SIMPLEST possible command. Avoid complex piping or multi-line expressions.

Shell: {self.shell_info} ({self.os_info})"""
            
            # Add context if available
            if self.context_manager:
                context = self.context_manager.format_compact()
                full_prompt += f"\nContext: {context}"
            
            full_prompt += f"\n\nUser request: {user_input}"
            
            full_prompt += """

Examples of GOOD simple commands:
- "Get-PSDrive -PSProvider FileSystem"
- "Get-Volume"
- "wmic logicaldisk get size,freespace,caption"

Keep it SHORT!"""
            
            # Generate response
            response = model.generate_content(full_prompt)
            text = response.text.strip()
            
            # Check if response was truncated
            if hasattr(response, 'candidates') and len(response.candidates) > 0:
                finish_reason = response.candidates[0].finish_reason
                if finish_reason == "MAX_TOKENS":
                    # Response was cut off - return error JSON instead of incomplete command
                    return '{"command":"echo \'Response truncated\'","risk_level":"medium","explanation":"LLM response was cut off. Try rephrasing your request."}'
            
            return text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                raise Exception("⚠️  Gemini API rate limit exceeded. Please wait a moment and try again.")
            raise
    
    def _call_ollama(self, user_input: str) -> str:
        """Call local Ollama API"""
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests package not installed. Run: pip install requests")
        
        url = self.base_url or "http://localhost:11434"
        
        response = requests.post(
            f"{url}/api/generate",
            json={
                "model": self.model,
                "prompt": f"{self._get_system_prompt()}\n\nUser request: {user_input}",
                "stream": False,
                "options": {
                    "temperature": 0.1
                }
            },
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.text}")
        
        return response.json().get("response", "")
    
    def _parse_llm_response(self, response: str) -> CommandProposal:
        """Parse LLM JSON response into CommandProposal with multiple fallback strategies"""
        import re
        import json as json_module
        
        debug = False  # Set to True to see raw responses during debugging
        
        if debug:
            print(f"\nDEBUG: Raw response length: {len(response)}")
            print(f"DEBUG: Response content: {response[:300]}")
        
        try:
            # Strategy 1: Clean and parse JSON directly
            cleaned = response.strip()
            
            # Remove markdown code blocks
            if "```" in cleaned:
                match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned)
                if match:
                    cleaned = match.group(1)
                else:
                    cleaned = cleaned.replace("```json", "").replace("```", "").strip()
            
            # Extract JSON object
            start_idx = cleaned.find("{")
            end_idx = cleaned.rfind("}")
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                cleaned = cleaned[start_idx:end_idx + 1]
            
            # Try parse
            try:
                data = json_module.loads(cleaned)
                return CommandProposal(
                    command=data.get("command", ""),
                    risk_level=data.get("risk_level", "medium").lower(),
                    explanation=data.get("explanation", "No explanation provided"),
                    raw_response=response
                )
            except json_module.JSONDecodeError as e:
                if debug:
                    print(f"DEBUG: Strategy 1 failed: {str(e)[:100]}")
                pass  # Fall through to next strategy
            
            # Strategy 2: Remove trailing commas and try again
            cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
            try:
                data = json_module.loads(cleaned)
                return CommandProposal(
                    command=data.get("command", ""),
                    risk_level=data.get("risk_level", "medium").lower(),
                    explanation=data.get("explanation", "No explanation provided"),
                    raw_response=response
                )
            except json_module.JSONDecodeError:
                if debug:
                    print(f"DEBUG: Strategy 2 failed")
                pass
            
            # Strategy 3: Handle single quotes instead of double quotes
            try:
                test_cleaned = re.sub(r"'command'", '"command"', cleaned)
                test_cleaned = re.sub(r"'risk_level'", '"risk_level"', test_cleaned)
                test_cleaned = re.sub(r"'explanation'", '"explanation"', test_cleaned)
                data = json_module.loads(test_cleaned)
                return CommandProposal(
                    command=data.get("command", ""),
                    risk_level=data.get("risk_level", "medium").lower(),
                    explanation=data.get("explanation", "No explanation provided"),
                    raw_response=response
                )
            except json_module.JSONDecodeError:
                if debug:
                    print(f"DEBUG: Strategy 3 failed")
                pass
            
            # Strategy 4: Aggressive regex extraction - handles truncated/malformed JSON
            if debug:
                print(f"DEBUG: Trying regex extraction...")
            
            command = None
            
            # Try multiple patterns for command extraction
            # KEY: Match everything until we hit an unescaped quote OR end of string
            patterns = [
                r'"command"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"',  # Properly handles escapes
                r'"command"\s*:\s*"([^"]*)"',  # Simple quoted (fallback)
                r"'command'\s*:\s*'([^']*)'",  # Single quoted
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response, re.DOTALL)
                if match:
                    command = match.group(1)
                    # Unescape common escapes
                    command = command.replace('\\\\', '\\').replace('\\"', '"').replace('\\/', '/')
                    if debug:
                        print(f"DEBUG: Pattern '{pattern[:30]}...' matched!")
                        print(f"DEBUG: Extracted command: {command[:100]}")
                    break
            
            # If still no match and response looks truncated (ends without }, but has {), extract what we can
            if not command and '{' in response and '}' not in response:
                if debug:
                    print(f"DEBUG: Response appears truncated, attempting partial extraction...")
                # Try to get everything after "command":"
                match = re.search(r'"command"\s*:\s*"([^"]*(?:\\.[^"]*)*)', response)
                if match:
                    command = match.group(1)
                    command = command.replace('\\\\', '\\').replace('\\"', '"').replace('\\/', '/')
                    if debug:
                        print(f"DEBUG: Partial extraction succeeded: {command[:100]}")
            
            if command:
                # Try to get risk level and explanation
                risk_match = re.search(r'"risk_level"\s*:\s*"(\w+)"', response)
                risk = risk_match.group(1) if risk_match else "medium"
                
                exp_match = re.search(r'"explanation"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', response, re.DOTALL)
                explanation = exp_match.group(1) if exp_match else "Extracted via regex fallback"
                explanation = explanation.replace('\\"', '"').replace('\\/', '/')
                
                return CommandProposal(
                    command=command,
                    risk_level=risk.lower(),
                    explanation=explanation,
                    raw_response=response
                )
            
            # Strategy 5: Last resort - just extract the value after "command":"
            if '"command":"' in response:
                # Find everything after "command":"
                idx = response.find('"command":"')
                if idx >= 0:
                    rest = response[idx + len('"command":"'):]
                    # Find the next quote
                    end_idx = rest.find('"')
                    if end_idx > 0:
                        command = rest[:end_idx].replace('\\"', '"').replace('\\/', '/')
                        if debug:
                            print(f"DEBUG: Strategy 5 extracted: {command}")
                        return CommandProposal(
                            command=command,
                            risk_level="medium",
                            explanation="Extracted from malformed response",
                            raw_response=response
                        )
            
            if debug:
                print(f"DEBUG: Failed to parse response")
            
            return CommandProposal(
                command="",
                risk_level="critical",
                explanation="Failed to parse LLM response - malformed JSON",
                raw_response=response,
                error="Could not extract command from response"
            )
            
        except Exception as e:
            if debug:
                print(f"DEBUG: Parsing exception: {str(e)}")
            
            return CommandProposal(
                command="",
                risk_level="critical",
                explanation=f"Error parsing LLM response: {str(e)[:50]}",
                raw_response=response,
                error=str(e)
            )
    
    def _enhance_file_search_command(self, proposal: CommandProposal) -> CommandProposal:
        """
        Post-process commands to add -Recurse flag for file searches.
        
        Args:
            proposal: CommandProposal to enhance
            
        Returns:
            Enhanced CommandProposal with -Recurse added if needed
        """
        import re
        
        command = proposal.command
        
        # Patterns that indicate recursive file searches should be used
        search_keywords = [
            r"Get-ChildItem.*Where-Object.*\$_\.Length",  # File size searches
            r"Get-ChildItem.*Where-Object.*\$_\.Name",    # File name searches  
            r"find.*\-name",                                # Unix find command
            r"ls.*recursive",                               # Recursive listing
            r"list files.*larger",                          # Common natural language
            r"list files.*more than",                       # Common natural language
        ]
        
        # Check if this looks like a file search and is missing -Recurse
        is_file_search = any(re.search(pattern, command, re.IGNORECASE) for pattern in search_keywords)
        
        if is_file_search and "-Recurse" not in command:
            # Add -Recurse after Get-ChildItem
            if "Get-ChildItem" in command:
                command = command.replace("Get-ChildItem", "Get-ChildItem -Recurse", 1)
                proposal.explanation += " [Auto-enhanced with -Recurse for subdirectories]"
        
        return CommandProposal(
            command=command,
            risk_level=proposal.risk_level,
            explanation=proposal.explanation,
            raw_response=proposal.raw_response,
            error=proposal.error
        )
    
    def generate_command(self, user_input: str) -> CommandProposal:
        """
        Generate a command proposal from natural language input.
        
        ❌ Does NOT execute anything
        ✅ Only returns a proposal for user review
        
        Args:
            user_input: Natural language command request
            
        Returns:
            CommandProposal with command, risk level, and explanation
        """
        try:
            if self.backend == "gemini":
                response = self._call_gemini(user_input)
            elif self.backend == "ollama":
                response = self._call_ollama(user_input)
            else:
                return CommandProposal(
                    command="",
                    risk_level="critical",
                    explanation=f"Unknown backend: {self.backend}",
                    error=f"Unsupported backend: {self.backend}"
                )
            
            proposal = self._parse_llm_response(response)
            
            # Post-process to enhance file search commands
            proposal = self._enhance_file_search_command(proposal)
            
            return proposal
            
        except Exception as e:
            return CommandProposal(
                command="",
                risk_level="critical",
                explanation="LLM request failed",
                error=str(e)
            )
    
    def generate_plan(self, user_input: str):
        """
        Generate a multi-step execution plan for complex requests.
        
        Args:
            user_input: Natural language command request
            
        Returns:
            Plan object with steps, or None if not a complex request
        """
        try:
            if self.backend == "gemini":
                response = self._call_gemini_plan(user_input)
            else:
                # Fallback to single command for other backends
                return None
            
            return self._parse_plan_response(response)
            
        except Exception as e:
            print(f"⚠️  Plan generation failed: {e}")
            return None
    
    def _call_gemini_plan(self, user_input: str) -> str:
        """Call Gemini for multi-step plan generation"""
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not available")
        
        if not self.api_key:
            raise ValueError("Gemini API key not found")
        
        try:
            model = genai.GenerativeModel(
                model_name=self.model,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 4096,
                    "top_p": 0.9,
                }
            )
            
            prompt = f"""Break down this request into a step-by-step plan. Output ONLY valid JSON with no additional text.

Format (be very precise with JSON syntax):
{{
  "description": "<overall goal>",
  "steps": [
    {{"step": 1, "command": "<simple command>", "risk_level": "low", "explanation": "<what>", "depends_on": []}},
    {{"step": 2, "command": "<next command>", "risk_level": "medium", "explanation": "<what>", "depends_on": [1]}}
  ]
}}

Shell: {self.shell_info} ({self.os_info})"""
            
            if self.context_manager:
                context = self.context_manager.format_compact()
                prompt += f"\nContext: {context}"
            
            prompt += f"\n\nUser request: {user_input}\n\nJSON plan:"
            
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            raise Exception(f"Gemini plan generation failed: {e}")
    
    def _parse_plan_response(self, response: str):
        """Parse plan JSON response into Plan object"""
        import json as json_module
        import re
        from .planner import Plan, PlanStep, StepStatus
        
        try:
            # Clean response
            cleaned = response.strip()
            if "```" in cleaned:
                match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned)
                if match:
                    cleaned = match.group(1)
            
            # Extract JSON
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start >= 0 and end > start:
                cleaned = cleaned[start:end+1]
            
            # Fix invalid escape sequences (e.g., \$ should be \\$, \C should be \\C)
            # This handles Windows paths and special characters
            cleaned = re.sub(r'\\([^"\\bfnrtu/])', r'\\\\\1', cleaned)
            
            data = json_module.loads(cleaned)
            
            # Create PlanStep objects
            steps = []
            max_risk = "low"
            risk_order = ["low", "medium", "high", "critical"]
            
            for step_data in data.get("steps", []):
                risk = step_data.get("risk_level", "medium").lower()
                if risk_order.index(risk) > risk_order.index(max_risk):
                    max_risk = risk
                
                steps.append(PlanStep(
                    step_number=step_data.get("step", len(steps) + 1),
                    command=step_data.get("command", ""),
                    risk_level=risk,
                    explanation=step_data.get("explanation", ""),
                    depends_on=step_data.get("depends_on", []),
                    status=StepStatus.PENDING
                ))
            
            return Plan(
                description=data.get("description", "Multi-step plan"),
                steps=steps,
                total_risk=max_risk
            )
            
        except Exception as e:
            print(f"⚠️  Failed to parse plan: {e}")
            return None


# Fallback rule-based generator for offline/no-API scenarios
class FallbackCommandGenerator:
    """
    Simple rule-based fallback when LLM is unavailable.
    Uses pattern matching for common commands.
    """
    
    PATTERNS = {
        "list": {"win": "dir", "unix": "ls -la"},
        "show files": {"win": "dir", "unix": "ls -la"},
        "current directory": {"win": "cd", "unix": "pwd"},
        "where am i": {"win": "cd", "unix": "pwd"},
        "make folder": {"win": "mkdir", "unix": "mkdir"},
        "create folder": {"win": "mkdir", "unix": "mkdir"},
        "create directory": {"win": "mkdir", "unix": "mkdir"},
        "make directory": {"win": "mkdir", "unix": "mkdir"},
        "create file": {"win": "type nul >", "unix": "touch"},
        "make file": {"win": "type nul >", "unix": "touch"},
        "delete": {"win": "del", "unix": "rm"},
        "remove": {"win": "del", "unix": "rm"},
        "copy": {"win": "copy", "unix": "cp"},
        "move": {"win": "move", "unix": "mv"},
        "read": {"win": "type", "unix": "cat"},
        "show content": {"win": "type", "unix": "cat"},
    }
    
    # Words to remove when extracting the actual argument
    NOISE_WORDS = [
        "create", "make", "new", "folder", "directory", "file", 
        "named", "called", "a", "the", "please", "can", "you",
        "delete", "remove", "read", "show", "content", "of",
        "copy", "move", "rename", "to", "from", "list", "all", "files"
    ]
    
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
    
    def _extract_argument(self, user_input: str, pattern: str) -> str:
        """Extract the actual argument (filename/foldername) from user input"""
        input_lower = user_input.lower()
        
        # Handle "to" for copy/move operations
        if " to " in input_lower and pattern in ["copy", "move"]:
            parts = input_lower.split(" to ")
            source = self._clean_argument(parts[0], pattern)
            dest = self._clean_argument(parts[1], pattern)
            return f"{source} {dest}"
        
        return self._clean_argument(input_lower, pattern)
    
    def _clean_argument(self, text: str, pattern: str) -> str:
        """Remove noise words and return clean argument"""
        words = text.split()
        # Remove pattern words and noise words
        clean_words = []
        for word in words:
            if word.lower() not in self.NOISE_WORDS and word.lower() not in pattern.split():
                clean_words.append(word)
        return " ".join(clean_words).strip()
    
    def generate_command(self, user_input: str) -> CommandProposal:
        """Generate command using simple pattern matching"""
        input_lower = user_input.lower()
        
        # Special pattern for 'find files larger than X and save to file'
        import re
        match = re.search(r'find files larger than (\d+)([kmg]b)?', input_lower)
        if match and ("save" in input_lower or "output" in input_lower or "list" in input_lower):
            size = match.group(1)
            unit = match.group(2) or "MB"
            size_str = f"{size}{unit.upper()}"
            command = f"Get-ChildItem -Recurse -File | Where-Object {{ $_.Length -gt {size_str} }} | Out-File -FilePath 'large_files.txt'"
            return CommandProposal(
                command=command,
                risk_level="low",
                explanation=f"Finds all files larger than {size_str} and saves the list to large_files.txt."
            )
        
        for pattern, commands in self.PATTERNS.items():
            if pattern in input_lower:
                base_cmd = commands["win"] if self.is_windows else commands["unix"]
                
                # Extract the actual argument (folder name, file name, etc.)
                arg = self._extract_argument(user_input, pattern)
                
                # Build final command
                if arg:
                    command = f"{base_cmd} {arg}"
                else:
                    command = base_cmd
                
                # Determine risk level
                risk = "low" if base_cmd in ["dir", "ls", "ls -la", "cd", "pwd", "type", "cat"] else "medium"
                if base_cmd in ["del", "rm"]:
                    risk = "high"
                
                return CommandProposal(
                    command=command,
                    risk_level=risk,
                    explanation=f"Pattern-matched command for '{pattern}'"
                )
        
        return CommandProposal(
            command="",
            risk_level="low",
            explanation="Could not understand the request",
            error="No matching pattern found"
        )


def create_generator(use_llm: bool = True, **kwargs) -> LLMCommandGenerator | FallbackCommandGenerator:
    """
    Factory function to create appropriate generator.
    
    Args:
        use_llm: Whether to use LLM (True) or fallback (False)
        **kwargs: Arguments passed to LLMCommandGenerator
    """
    if use_llm:
        return LLMCommandGenerator(**kwargs)
    return FallbackCommandGenerator()
