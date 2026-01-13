"""
Safety Layer for AI CLI

🔐 Defense-in-depth safety checks:
1. Blacklist - Block known dangerous patterns
2. Allowlist - Only permit safe command categories (optional strict mode)
3. Path validation - Prevent traversal attacks
4. Risk assessment - Categorize command danger level

LLM output ≠ trusted input
Even after user confirmation, we validate everything.
"""

import re
import os
import platform
from dataclasses import dataclass
from typing import Tuple, List, Optional
from enum import Enum


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    BLOCKED = "blocked"


@dataclass
class SafetyResult:
    """Result of safety check"""
    is_safe: bool
    risk_level: RiskLevel
    reason: str
    warnings: List[str]


class SafetyChecker:
    """
    Comprehensive safety checker for command execution.
    
    Defense layers:
    1. BLACKLIST - Absolute blocks (never execute)
    2. HIGH_RISK - Patterns that need extra scrutiny
    3. PATH_VALIDATION - Prevent directory traversal
    4. ALLOWLIST - Optional strict mode (only whitelisted commands)
    """
    
    # ═══════════════════════════════════════════════════════════════════
    # BLACKLIST - Commands that are NEVER allowed
    # ═══════════════════════════════════════════════════════════════════
    BLACKLIST_PATTERNS = [
        # Recursive force delete (catastrophic)
        r"rm\s+(-[rf]+\s+)*(/|~|\$HOME|\.\.)$",
        r"rm\s+-rf\s+/",
        r"rm\s+-rf\s+\*",
        r"rm\s+-rf\s+~",
        r"del\s+/s\s+/q\s+[cC]:\\",
        r"rd\s+/s\s+/q\s+[cC]:\\",
        r"rmdir\s+/s\s+/q",
        
        # System destruction
        r"format\s+[cCdD]:",
        r"mkfs\.",
        r"dd\s+.*of=/dev/[hs]d",
        r":(){ :|:& };:",  # Fork bomb
        r">\s*/dev/sd[a-z]",
        
        # Shutdown/reboot without confirmation path
        r"shutdown\s+(-h|-r|/s|/r)",
        r"reboot",
        r"init\s+[0-6]",
        r"systemctl\s+(poweroff|reboot|halt)",
        
        # Privilege escalation attempts
        r"chmod\s+777\s+/",
        r"chmod\s+-R\s+777",
        r"chown\s+-R\s+.*\s+/",
        
        # Network exfiltration
        r"curl.*\|\s*(ba)?sh",
        r"wget.*\|\s*(ba)?sh",
        r"nc\s+-e",
        r"bash\s+-i\s+>&\s+/dev/tcp",
        
        # Windows specific dangers
        r"reg\s+delete\s+HKLM",
        r"reg\s+delete\s+HKCU",
        r"bcdedit",
        r"diskpart",
        
        # Clear all history (anti-forensics)
        r"history\s+-c.*&&.*rm.*history",
        r"shred.*\.bash_history",
    ]
    
    # ═══════════════════════════════════════════════════════════════════
    # HIGH RISK - Not blocked but flagged for extra confirmation
    # ═══════════════════════════════════════════════════════════════════
    HIGH_RISK_PATTERNS = [
        (r"rm\s+", "Delete command detected"),
        (r"del\s+", "Delete command detected"),
        (r"rmdir", "Remove directory command"),
        (r"rd\s+", "Remove directory command"),
        (r">\s+", "Output redirection (may overwrite files)"),
        (r"mv\s+.*\s+/", "Moving to root directory"),
        (r"chmod\s+", "Permission change"),
        (r"chown\s+", "Ownership change"),
        (r"sudo\s+", "Elevated privileges"),
        (r"runas\s+", "Elevated privileges"),
        (r"pip\s+install", "Package installation"),
        (r"npm\s+install", "Package installation"),
        (r"apt\s+install", "Package installation"),
        (r"brew\s+install", "Package installation"),
    ]
    
    # ═══════════════════════════════════════════════════════════════════
    # ALLOWLIST - Safe commands for strict mode
    # ═══════════════════════════════════════════════════════════════════
    ALLOWED_COMMANDS = {
        # Navigation & listing
        "ls", "dir", "pwd", "cd", "tree", "find", "where", "which",
        # Reading
        "cat", "type", "head", "tail", "less", "more", "grep", "findstr",
        # File info
        "stat", "file", "wc",
        # Safe creation
        "mkdir", "touch", "echo",
        # Safe copy
        "cp", "copy",
        # Safe move (non-destructive context)
        "mv", "move",
        # Compression
        "tar", "zip", "unzip", "gzip", "gunzip",
        # Git (read operations)
        "git status", "git log", "git diff", "git branch",
        # System info
        "date", "whoami", "hostname", "uname", "systeminfo",
        # Python/Node (running scripts)
        "python", "python3", "node",
    }
    
    # ═══════════════════════════════════════════════════════════════════
    # DANGEROUS PATHS - Paths that should never be targets
    # ═══════════════════════════════════════════════════════════════════
    DANGEROUS_PATHS = [
        "/", "/bin", "/boot", "/dev", "/etc", "/lib", "/proc", "/root",
        "/sbin", "/sys", "/usr", "/var",
        "C:\\Windows", "C:\\Program Files", "C:\\System32",
        "~", "$HOME", "%USERPROFILE%",
    ]
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize safety checker.
        
        Args:
            strict_mode: If True, only allowlisted commands are permitted
        """
        self.strict_mode = strict_mode
        self.is_windows = platform.system() == "Windows"
        
        # Compile regex patterns for efficiency
        self.blacklist_compiled = [re.compile(p, re.IGNORECASE) for p in self.BLACKLIST_PATTERNS]
        self.high_risk_compiled = [(re.compile(p, re.IGNORECASE), msg) for p, msg in self.HIGH_RISK_PATTERNS]
    
    def check_command(self, command: str) -> SafetyResult:
        """
        Perform comprehensive safety check on a command.
        
        Args:
            command: The command string to validate
            
        Returns:
            SafetyResult with is_safe, risk_level, reason, and warnings
        """
        warnings = []
        
        # ─────────────────────────────────────────────────────────────
        # Layer 1: BLACKLIST CHECK
        # ─────────────────────────────────────────────────────────────
        for pattern in self.blacklist_compiled:
            if pattern.search(command):
                return SafetyResult(
                    is_safe=False,
                    risk_level=RiskLevel.BLOCKED,
                    reason=f"🚨 BLOCKED: Matches dangerous pattern",
                    warnings=["This command pattern is absolutely forbidden"]
                )
        
        # ─────────────────────────────────────────────────────────────
        # Layer 2: STRICT MODE ALLOWLIST
        # ─────────────────────────────────────────────────────────────
        if self.strict_mode:
            cmd_base = command.split()[0].lower() if command.split() else ""
            if not any(cmd_base.startswith(allowed.lower()) for allowed in self.ALLOWED_COMMANDS):
                return SafetyResult(
                    is_safe=False,
                    risk_level=RiskLevel.BLOCKED,
                    reason=f"🚫 BLOCKED: '{cmd_base}' not in allowlist (strict mode)",
                    warnings=["Strict mode only allows pre-approved commands"]
                )
        
        # ─────────────────────────────────────────────────────────────
        # Layer 3: PATH VALIDATION
        # ─────────────────────────────────────────────────────────────
        for dangerous_path in self.DANGEROUS_PATHS:
            # Check if command targets dangerous paths with destructive intent
            if dangerous_path in command:
                destructive = any(d in command.lower() for d in ["rm ", "del ", "rmdir", "rd "])
                if destructive:
                    return SafetyResult(
                        is_safe=False,
                        risk_level=RiskLevel.BLOCKED,
                        reason=f"🚨 BLOCKED: Destructive operation on system path '{dangerous_path}'",
                        warnings=["Cannot delete or modify system directories"]
                    )
                warnings.append(f"⚠️  Command references sensitive path: {dangerous_path}")
        
        # ─────────────────────────────────────────────────────────────
        # Layer 4: HIGH RISK DETECTION
        # ─────────────────────────────────────────────────────────────
        risk_level = RiskLevel.LOW
        
        for pattern, message in self.high_risk_compiled:
            if pattern.search(command):
                risk_level = RiskLevel.HIGH
                warnings.append(f"⚠️  {message}")
        
        # Check for pipe to shell (medium risk)
        if re.search(r"\|\s*(ba)?sh", command):
            risk_level = RiskLevel.HIGH
            warnings.append("⚠️  Piping to shell detected")
        
        # Check for multiple commands chained
        if "&&" in command or ";" in command:
            if risk_level == RiskLevel.LOW:
                risk_level = RiskLevel.MEDIUM
            warnings.append("⚠️  Multiple chained commands")
        
        # ─────────────────────────────────────────────────────────────
        # FINAL RESULT
        # ─────────────────────────────────────────────────────────────
        return SafetyResult(
            is_safe=True,
            risk_level=risk_level,
            reason="✅ Command passed safety checks",
            warnings=warnings
        )
    
    def get_risk_display(self, risk_level: RiskLevel) -> str:
        """Get colored/formatted risk level for display"""
        displays = {
            RiskLevel.LOW: "🟢 LOW",
            RiskLevel.MEDIUM: "🟡 MEDIUM",
            RiskLevel.HIGH: "🟠 HIGH",
            RiskLevel.CRITICAL: "🔴 CRITICAL",
            RiskLevel.BLOCKED: "⛔ BLOCKED",
        }
        return displays.get(risk_level, "❓ UNKNOWN")
    
    def combine_risk_levels(self, llm_risk: str, safety_risk: RiskLevel) -> RiskLevel:
        """Combine LLM-assessed risk with safety check risk (take higher)"""
        risk_order = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL, RiskLevel.BLOCKED]
        
        # Convert LLM string risk to enum
        llm_risk_enum = {
            "low": RiskLevel.LOW,
            "medium": RiskLevel.MEDIUM,
            "high": RiskLevel.HIGH,
            "critical": RiskLevel.CRITICAL,
        }.get(llm_risk.lower(), RiskLevel.MEDIUM)
        
        # Return the higher risk level
        llm_idx = risk_order.index(llm_risk_enum) if llm_risk_enum in risk_order else 1
        safety_idx = risk_order.index(safety_risk) if safety_risk in risk_order else 1
        
        return risk_order[max(llm_idx, safety_idx)]


# ═══════════════════════════════════════════════════════════════════════
# Legacy function for backward compatibility
# ═══════════════════════════════════════════════════════════════════════
def is_safe(command: str) -> bool:
    """
    Legacy safety check function.
    Returns True if command is safe, False otherwise.
    """
    checker = SafetyChecker(strict_mode=False)
    result = checker.check_command(command)
    return result.is_safe


# Create default instance
default_checker = SafetyChecker(strict_mode=False)
