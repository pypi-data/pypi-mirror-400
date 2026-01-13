
"""
AI CLI - Clean LLM + Confirmation Flow

High-Level Pipeline:
    User Input (Natural Language)
            ↓
    LLM (Command Proposal Only)
            ↓
    Command Preview + Risk Label
            ↓
    User Confirmation (YES / NO)
            ↓
    Safety Filters (Blacklist / Allowlist)
            ↓
    Local Command Execution

🔐 Security Design:
    ❌ LLM NEVER executes commands
    ✅ LLM ONLY suggests commands
    ✅ Human-in-the-loop approval
    ✅ Deterministic final execution
    ✅ No silent destructive commands

🎯 Advanced Features:
    ✅ Undo/rollback for file operations
    ✅ Context-aware command generation
    ✅ Multi-step planning for complex tasks
"""

import sys
import io

# Fix encoding issues on Windows when output is piped
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import os
from .llm_generator import LLMCommandGenerator, FallbackCommandGenerator, CommandProposal
from .safety import SafetyChecker, RiskLevel
from .executor import CommandExecutor
from .context_manager import ContextManager
from .undo_manager import UndoManager
from .planner import CommandPlanner
from .autocomplete import AutocompleteSuggestions, get_input_with_autocomplete


# ═══════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════
CONFIG = {
    "use_llm": True,                    # True for LLM, False for fallback
    "llm_backend": "gemini",            # gemini, ollama
    "llm_model": None,                  # None = use default for backend (gemini-1.5-flash)
    "strict_mode": False,               # True = only allowlisted commands
    "auto_confirm_low_risk": False,     # True = skip confirmation for low risk
    "timeout": 60,                      # Command execution timeout (seconds) - increased for large operations
}


# ═══════════════════════════════════════════════════════════════════════
# DISPLAY HELPERS
# ═══════════════════════════════════════════════════════════════════════
def print_banner():
    """Print welcome banner"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║              🤖 AI CLI Assistant v2.0                      ║")
    print("║         Natural Language → Shell Commands                   ║")
    print("║                                                             ║")
    print("║  🔐 LLM proposes commands, YOU approve execution           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()


def print_help():
    """Print help message with full capabilities"""
    print("""
📚 AI CLI Help - Full Capabilities
══════════════════════════════════════════════════════════════

🤖 NATURAL LANGUAGE COMMANDS
   Just speak naturally - AI converts to shell commands!
   
   Examples:
   • "list all files in current directory"
   • "create a folder called projects"
   • "find all .py files"
   • "delete temp.txt"
   • "copy config.txt to backup/"
   • "show me the contents of readme.md"
   • "compress this folder and save as backup.zip"
   • "find files larger than 10MB"
   • "move all .log files to logs folder"

📊 MULTI-STEP OPERATIONS
   AI automatically detects complex tasks and breaks them into steps:
   • "find all log files and archive them"
   • "backup my project folder and remove temporary files"
   • "list files larger than 10MB and save to report"

🎯 ADVANCED FEATURES
   ✅ Context-aware generation (remembers your directory)
   ✅ Undo/Rollback (reverses file operations instantly)
   ✅ Risk Assessment (shows danger level before execution)
   ✅ Command history (learns from your patterns)
   ✅ File search enhancement (auto-adds -Recurse)
   ✅ Safety gates (blocks dangerous commands)

⚙️  SETTINGS COMMANDS
   • /mode llm       - Use Gemini LLM (default)
   • /mode fallback  - Use pattern matching (offline)
   • /strict on|off  - Toggle strict allowlist mode
   • /config         - Show current configuration

🔧 SYSTEM COMMANDS
   • help            - Show this help message
   • ?               - Quick help alias
   • undo            - Undo last file operation
   • undo list       - Show all undoable operations
   • exit, quit      - Exit the CLI

📋 COMMAND TYPES SUPPORTED
   File Operations:    create, delete, copy, move, rename
   Directory Ops:      mkdir, rmdir, cd, navigate
   Text Files:         cat, echo, grep, find, search
   Archives:           zip, tar, compress, extract
   Permissions:        chmod, chown, attrib
   Information:        ls, dir, file size, search

🔐 SAFETY GUARANTEES
   ✓ LLM ONLY proposes, never executes
   ✓ You must confirm every command
   ✓ Dangerous commands automatically blocked
   ✓ Deletions move to trash, not permanent
   ✓ All operations reversible via 'undo'

💡 TIPS & TRICKS
   • Be specific: "create folder named 'projects'" works better than "create folder"
   • Use 'undo' after any file operation to revert
   • Type '/config' to see current settings
   • Commands work on Windows (PowerShell) and Unix (bash)
""")


def print_config():
    """Print current configuration"""
    print("\n⚙️  Current Configuration:")
    print(f"   • LLM Mode: {'Enabled' if CONFIG['use_llm'] else 'Disabled (Fallback)'}")
    print(f"   • Backend: {CONFIG['llm_backend']}")
    print(f"   • Model: {CONFIG['llm_model'] or 'default'}")
    print(f"   • Strict Mode: {'ON' if CONFIG['strict_mode'] else 'OFF'}")
    print(f"   • Auto-confirm Low Risk: {'ON' if CONFIG['auto_confirm_low_risk'] else 'OFF'}")
    print(f"   • Timeout: {CONFIG['timeout']}s")
    print()


def print_proposal(proposal: CommandProposal, safety_risk: RiskLevel):
    """Print command proposal with formatting"""
    risk_display = {
        RiskLevel.LOW: "🟢 LOW",
        RiskLevel.MEDIUM: "🟡 MEDIUM", 
        RiskLevel.HIGH: "🟠 HIGH",
        RiskLevel.CRITICAL: "🔴 CRITICAL",
        RiskLevel.BLOCKED: "⛔ BLOCKED",
    }.get(safety_risk, "❓ UNKNOWN")
    
    print()
    print("┌─────────────────────────────────────────────────────────────┐")
    print("│                   📋 COMMAND PROPOSAL                       │")
    print("├─────────────────────────────────────────────────────────────┤")
    print(f"│ Command:                                                    │")
    print(f"│   {proposal.command:<57} │")
    print(f"├─────────────────────────────────────────────────────────────┤")
    print(f"│ Risk Level: {risk_display:<47} │")
    print(f"├─────────────────────────────────────────────────────────────┤")
    print(f"│ Explanation:                                                │")
    # Word wrap explanation
    exp = proposal.explanation
    while exp:
        print(f"│   {exp[:55]:<55} │")
        exp = exp[55:]
    print("└─────────────────────────────────────────────────────────────┘")


def show_command_suggestions(user_input: str = ""):
    """Display contextual command suggestions based on user input"""
    print("\n💡 Did you mean:")
    
    if user_input:
        # Generate contextual suggestions based on what user typed
        suggestions = AutocompleteSuggestions.get_suggestions(user_input, os.getcwd())
        
        if suggestions:
            for i, suggestion in enumerate(suggestions[:5], 1):
                print(f"      {i}. {suggestion}")
        else:
            # Default suggestions if no matches
            _show_default_suggestions()
    else:
        _show_default_suggestions()
    print()


def _show_default_suggestions():
    """Show default command suggestions"""
    defaults = [
        "create folder <name>",
        "show files",
        "read <filename>",
        "delete <filename>",
        "copy <src> to <dest>"
    ]
    for i, suggestion in enumerate(defaults, 1):
        print(f"      {i}. {suggestion}")


def get_confirmation(safety_risk: RiskLevel, user_input: str = "") -> bool:
    """Get user confirmation for command execution with optional help"""
    
    # Auto-confirm for low risk if configured
    if CONFIG['auto_confirm_low_risk'] and safety_risk == RiskLevel.LOW:
        print("   [Auto-confirmed: Low risk]")
        return True
    
    # Extra warning for high/critical risk
    if safety_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        print("\n⚠️  WARNING: This is a high-risk command!")
    
    while True:
        try:
            response = input("\n▶ Execute this command? (yes/no/help): ").strip().lower()
            
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            elif response in ['help', '?']:
                show_command_suggestions(user_input)
                continue
            else:
                print("   Please enter 'yes', 'no', or 'help'")
                continue
                
        except (EOFError, KeyboardInterrupt):
            return False


# ═══════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════
def process_settings_command(user_input: str) -> bool:
    """
    Process settings commands (return True if handled)
    """
    parts = user_input.lower().split()
    
    if parts[0] == '/mode':
        if len(parts) > 1:
            if parts[1] == 'llm':
                CONFIG['use_llm'] = True
                print("✅ Switched to LLM mode")
            elif parts[1] == 'fallback':
                CONFIG['use_llm'] = False
                print("✅ Switched to fallback mode (offline)")
            else:
                print(f"❌ Unknown mode: {parts[1]}")
        else:
            print(f"Current mode: {'LLM' if CONFIG['use_llm'] else 'Fallback'}")
        return True
    
    if parts[0] == '/strict':
        if len(parts) > 1:
            CONFIG['strict_mode'] = parts[1] in ['on', 'true', '1']
            print(f"✅ Strict mode: {'ON' if CONFIG['strict_mode'] else 'OFF'}")
        else:
            print(f"Strict mode: {'ON' if CONFIG['strict_mode'] else 'OFF'}")
        return True
    
    if parts[0] == '/config':
        print_config()
        return True
    
    return False


def main():
    """Main entry point"""
    
    # Initialize components
    generator = None
    safety_checker = SafetyChecker(strict_mode=CONFIG['strict_mode'])
    
    # Initialize context manager for intelligent command generation
    context_manager = ContextManager(initial_directory=os.getcwd())
    
    # Initialize undo manager for rollback support
    undo_manager = UndoManager()
    
    # Initialize executor with undo tracking
    executor = CommandExecutor(timeout=CONFIG['timeout'], undo_manager=undo_manager)
    
    # Initialize planner (will be created after generator)
    planner = None
    
    # Handle single command from arguments
    single_command = len(sys.argv) > 1
    if single_command:
        user_input = " ".join(sys.argv[1:])
    else:
        print_banner()
    
    while True:
        # Get input with autocomplete
        if single_command:
            single_command = False  # Only run once
        else:
            try:
                # Show current directory in prompt
                cwd_display = executor.working_dir.split('\\')[-1] or executor.working_dir
                prompt = f"AI-CLI [{cwd_display}]> "
                
                # Get input with autocomplete support
                user_input = get_input_with_autocomplete(prompt, executor.working_dir)
                
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                return
        
        # Skip empty input
        if not user_input:
            continue
        
        # ─────────────────────────────────────────────────────────────
        # Handle special commands FIRST (before LLM)
        # ─────────────────────────────────────────────────────────────
        user_lower = user_input.lower().strip()
        
        if user_lower in ['exit', 'quit', 'bye', '/exit', '/quit']:
            print("👋 Goodbye!")
            return
        
        if user_lower in ['help', '/help', '?']:
            print_help()
            continue
        
        # Undo command - MUST be checked before LLM processing
        if user_lower in ['undo', '/undo']:
            if undo_manager.can_undo():
                undo_manager.rollback_last()
            else:
                print("❌ No operations to undo")
            continue
        
        # Show undo stack
        if user_lower in ['undo list', '/undo list', 'undo stack']:
            undo_manager.show_undo_stack()
            continue
        
        if user_input.startswith('/'):
            if process_settings_command(user_input):
                continue
        
        # ─────────────────────────────────────────────────────────────
        # STEP 1: Check if multi-step planning is needed
        # ─────────────────────────────────────────────────────────────
        if CONFIG['use_llm'] and CommandPlanner.is_complex_request(user_input):
            # Multi-step workflow
            print("\n🔄 Analyzing complex request...")
            print("   Detected multi-step operation - generating plan...\n")
            
            # Lazy-initialize generator with context
            if not isinstance(generator, LLMCommandGenerator):
                try:
                    generator = LLMCommandGenerator(
                        backend=CONFIG['llm_backend'],
                        model=CONFIG['llm_model'],
                        context_manager=context_manager
                    )
                except Exception as e:
                    print(f"⚠️  LLM initialization failed: {e}")
                    print("   Falling back to single command mode...")
                    generator = FallbackCommandGenerator()
            
            # Initialize planner if needed
            if not planner:
                planner = CommandPlanner(generator, safety_checker, executor)
            
            # Generate plan
            plan = generator.generate_plan(user_input)
            
            if plan and plan.steps:
                # Display and execute plan
                planner.display_plan(plan)
                
                if planner.confirm_plan(plan):
                    # Execute with step-by-step confirmation for high-risk plans
                    confirm_each = plan.total_risk in ['high', 'critical']
                    success = planner.execute_plan(plan, confirm_each_step=confirm_each)
                    
                    # Update context with plan results
                    for step in plan.steps:
                        context_manager.add_command(
                            user_input=user_input,
                            generated_command=step.command,
                            success=(step.status.value == "completed"),
                            error_message=step.error_message
                        )
                else:
                    print("🚫 Plan cancelled.")
                
                # Update working directory context
                context_manager.update_directory(executor.working_dir)
                continue
            else:
                print("   ⚠️  Failed to generate plan, falling back to single command...")
        
        # ─────────────────────────────────────────────────────────────
        # STEP 2: LLM Command Generation (Single Command)
        # ─────────────────────────────────────────────────────────────
        print("\n🔄 Generating command proposal...")
        
        # Lazy-initialize generator (allows mode switching)
        if CONFIG['use_llm']:
            if not isinstance(generator, LLMCommandGenerator):
                try:
                    generator = LLMCommandGenerator(
                        backend=CONFIG['llm_backend'],
                        model=CONFIG['llm_model'],
                        context_manager=context_manager
                    )
                except Exception as e:
                    print(f"⚠️  LLM initialization failed: {e}")
                    print("   Falling back to pattern matching...")
                    generator = FallbackCommandGenerator()
        else:
            if not isinstance(generator, FallbackCommandGenerator):
                generator = FallbackCommandGenerator()
        
        # Generate command proposal
        proposal = generator.generate_command(user_input)
        
        # Check for generation errors
        if proposal.error:
            print(f"\n❌ Generation failed: {proposal.error}")
            if "API key" in proposal.error:
                print("   Set OPENAI_API_KEY environment variable or use /mode fallback")
            continue
        
        if not proposal.command:
            print("\n❌ Could not generate a command for this request.")
            print("   Try rephrasing or use more specific language.")
            continue
        
        # ─────────────────────────────────────────────────────────────
        # STEP 2: Safety Check
        # ─────────────────────────────────────────────────────────────
        safety_checker.strict_mode = CONFIG['strict_mode']
        safety_result = safety_checker.check_command(proposal.command)
        
        # Combine LLM risk assessment with safety check
        final_risk = safety_checker.combine_risk_levels(
            proposal.risk_level, 
            safety_result.risk_level
        )
        
        # ─────────────────────────────────────────────────────────────
        # STEP 3: Display Proposal
        # ─────────────────────────────────────────────────────────────
        print_proposal(proposal, final_risk)
        
        # Show safety warnings
        if safety_result.warnings:
            print("\n⚠️  Safety Warnings:")
            for warning in safety_result.warnings:
                print(f"   {warning}")
        
        # Block if safety check failed
        if not safety_result.is_safe:
            print(f"\n🚨 {safety_result.reason}")
            print("   This command cannot be executed.")
            continue
        
        # ─────────────────────────────────────────────────────────────
        # STEP 4: User Confirmation (MANDATORY)
        # ─────────────────────────────────────────────────────────────
        if not get_confirmation(final_risk, user_input):
            print("🚫 Command cancelled.")
            continue
        
        # ─────────────────────────────────────────────────────────────
        # STEP 5: Execute Command
        # ─────────────────────────────────────────────────────────────
        print(f"\n⚡ Executing: {proposal.command}")
        print("─" * 60)
        
        result = executor.execute(proposal.command)
        output = executor.format_output(result)
        
        print(output)
        print("─" * 60)
        
        if result.success:
            print("✅ Command completed successfully")
        else:
            print(f"❌ Command failed (exit code: {result.return_code})")
        
        # ─────────────────────────────────────────────────────────────
        # STEP 6: Update Context
        # ─────────────────────────────────────────────────────────────
        # Track command in history for context-aware future commands
        context_manager.add_command(
            user_input=user_input,
            generated_command=proposal.command,
            success=result.success,
            error_message=result.error if not result.success else None
        )
        
        # Update working directory context
        context_manager.update_directory(executor.working_dir)

if __name__ == "__main__":
    main()
