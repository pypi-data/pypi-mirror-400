"""
Multi-Step Command Planner

Breaks down complex requests into sequential steps with dependency tracking.
Allows execution of multi-step workflows with progress tracking.
"""

from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class StepStatus(Enum):
    """Status of a plan step"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PlanStep:
    """Represents a single step in a multi-step plan"""
    step_number: int
    command: str
    risk_level: str  # low, medium, high, critical
    explanation: str
    depends_on: List[int]  # Step numbers this depends on (empty = no dependencies)
    status: StepStatus = StepStatus.PENDING
    error_message: Optional[str] = None
    
    def can_execute(self, completed_steps: List[int]) -> bool:
        """Check if this step can be executed based on dependencies"""
        if not self.depends_on:
            return True
        return all(dep in completed_steps for dep in self.depends_on)


@dataclass
class Plan:
    """Represents a complete multi-step execution plan"""
    description: str
    steps: List[PlanStep]
    total_risk: str  # Highest risk level among all steps
    
    def get_pending_steps(self) -> List[PlanStep]:
        """Get steps that are pending execution"""
        return [s for s in self.steps if s.status == StepStatus.PENDING]
    
    def get_completed_steps(self) -> List[int]:
        """Get list of completed step numbers"""
        return [s.step_number for s in self.steps if s.status == StepStatus.COMPLETED]
    
    def get_next_step(self) -> Optional[PlanStep]:
        """Get next executable step based on dependencies"""
        completed = self.get_completed_steps()
        for step in self.steps:
            if step.status == StepStatus.PENDING and step.can_execute(completed):
                return step
        return None
    
    def is_complete(self) -> bool:
        """Check if all steps are completed or skipped"""
        return all(s.status in [StepStatus.COMPLETED, StepStatus.SKIPPED] for s in self.steps)
    
    def has_failed(self) -> bool:
        """Check if any step has failed"""
        return any(s.status == StepStatus.FAILED for s in self.steps)


class CommandPlanner:
    """
    Generates and executes multi-step command plans.
    Handles complex workflows that require multiple operations.
    """
    
    def __init__(self, llm_generator, safety_checker, executor):
        """
        Initialize command planner.
        
        Args:
            llm_generator: LLM command generator instance
            safety_checker: Safety checker instance
            executor: Command executor instance
        """
        self.llm_generator = llm_generator
        self.safety_checker = safety_checker
        self.executor = executor
    
    def display_plan(self, plan: Plan):
        """
        Display plan overview to user.
        
        Args:
            plan: The execution plan to display
        """
        print("\n" + "="*70)
        print(f"📋 MULTI-STEP PLAN: {plan.description}")
        print("="*70)
        
        # Show total risk
        risk_emoji = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🟠',
            'critical': '🔴'
        }
        print(f"\nOverall Risk: {risk_emoji.get(plan.total_risk, '⚪')} {plan.total_risk.upper()}")
        
        print(f"\nSteps ({len(plan.steps)} total):")
        print("-"*70)
        
        for step in plan.steps:
            # Risk indicator
            risk = risk_emoji.get(step.risk_level, '⚪')
            
            # Dependencies
            deps = ""
            if step.depends_on:
                deps = f" [depends on step(s): {', '.join(map(str, step.depends_on))}]"
            
            print(f"\n{step.step_number}. {risk} {step.explanation}{deps}")
            print(f"   Command: {step.command}")
        
        print("\n" + "="*70)
    
    def confirm_plan(self, plan: Plan) -> bool:
        """
        Ask user to confirm plan execution.
        
        Args:
            plan: The plan to confirm
            
        Returns:
            True if user approves, False otherwise
        """
        while True:
            response = input("\n▶ Execute this plan? (yes/no/review): ").strip().lower()
            
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            elif response in ['review', 'r']:
                self.display_plan(plan)
            else:
                print("Please enter 'yes', 'no', or 'review'")
    
    def execute_plan(self, plan: Plan, confirm_each_step: bool = False) -> bool:
        """
        Execute a multi-step plan.
        
        Args:
            plan: The plan to execute
            confirm_each_step: If True, ask for confirmation before each step
            
        Returns:
            True if plan completed successfully, False if any step failed
        """
        print(f"\n🚀 Executing plan: {plan.description}")
        print("="*70)
        
        completed_steps = []
        
        while not plan.is_complete() and not plan.has_failed():
            step = plan.get_next_step()
            
            if not step:
                # No more executable steps (might have skipped dependencies)
                break
            
            # Display step
            print(f"\n📌 Step {step.step_number}/{len(plan.steps)}: {step.explanation}")
            print(f"   Command: {step.command}")
            print(f"   Risk: {step.risk_level.upper()}")
            
            # Confirm if requested
            if confirm_each_step:
                response = input("   ▶ Execute this step? (yes/no/skip): ").strip().lower()
                if response in ['no', 'n']:
                    print("   🛑 Plan execution cancelled")
                    return False
                elif response in ['skip', 's']:
                    step.status = StepStatus.SKIPPED
                    print("   ⏭️  Step skipped")
                    continue
            
            # Execute step
            step.status = StepStatus.IN_PROGRESS
            result = self.executor.execute(step.command)
            
            if result.success:
                step.status = StepStatus.COMPLETED
                completed_steps.append(step.step_number)
                print(f"   ✅ Step {step.step_number} completed")
                
                # Show output if not too long
                if result.stdout and len(result.stdout) < 200:
                    print(f"   Output: {result.stdout.strip()}")
            else:
                step.status = StepStatus.FAILED
                step.error_message = result.error
                print(f"   ❌ Step {step.step_number} failed")
                if result.error:
                    print(f"   Error: {result.error[:200]}")
                
                # Ask if user wants to continue or abort
                response = input("\n   Continue with remaining steps? (yes/no): ").strip().lower()
                if response not in ['yes', 'y']:
                    print("   🛑 Plan execution aborted")
                    return False
        
        # Summary
        print("\n" + "="*70)
        print("📊 PLAN EXECUTION SUMMARY")
        print("="*70)
        
        completed = [s for s in plan.steps if s.status == StepStatus.COMPLETED]
        failed = [s for s in plan.steps if s.status == StepStatus.FAILED]
        skipped = [s for s in plan.steps if s.status == StepStatus.SKIPPED]
        
        print(f"✅ Completed: {len(completed)}/{len(plan.steps)}")
        if skipped:
            print(f"⏭️  Skipped: {len(skipped)}")
        if failed:
            print(f"❌ Failed: {len(failed)}")
            for step in failed:
                print(f"   Step {step.step_number}: {step.explanation}")
        
        return len(failed) == 0
    
    @staticmethod
    def is_complex_request(user_input: str) -> bool:
        """
        Detect if user input is a complex multi-step request.
        
        Args:
            user_input: Natural language input from user
            
        Returns:
            True if likely a complex request, False otherwise
        """
        # Keywords that suggest multi-step operations
        multi_step_keywords = [
            'and then',
            'after that',
            'followed by',
            'and also',
            'backup and',
            'archive and',
            'find and',
            'search and',
            'cleanup',
            'clean up',
            'organize',
            'prepare',
            'setup',
            'set up',
            'all.*and.*',
        ]
        
        user_lower = user_input.lower()
        
        # Check for multiple action verbs
        action_verbs = ['find', 'search', 'list', 'create', 'delete', 'move', 'copy', 
                       'compress', 'archive', 'backup', 'clean', 'remove', 'install']
        verb_count = sum(1 for verb in action_verbs if verb in user_lower)
        
        # Check for multi-step keywords
        has_multi_keyword = any(keyword in user_lower for keyword in multi_step_keywords)
        
        return verb_count >= 2 or has_multi_keyword
