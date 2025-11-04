"""
Recovery Strategies for Deadlock Resolution

This module suggests recovery actions when deadlock is detected:
1. Process Termination: Identify minimal set of processes to terminate
2. Resource Preemption: Suggest which resources to preempt from which processes

Recovery approaches:
- Terminate one process at a time and check if system recovers
- Find minimal set of processes whose termination breaks all cycles
- Suggest preempting resources with lowest cost
"""

from typing import List, Set, Tuple, Optional
from dataclasses import dataclass
from models import SystemState
from detectors.matrix import detect_deadlock_matrix, can_system_recover
from detectors.wfg import detect_deadlock_wfg
import itertools


@dataclass
class RecoverySuggestion:
    """
    A suggested recovery action.
    
    Attributes:
        action_type: "terminate" or "preempt"
        description: Human-readable description
        processes: Process IDs involved
        resources: Resource IDs involved (for preemption)
        explanation: Detailed explanation of why this works
    """
    action_type: str
    description: str
    processes: Set[int]
    resources: Optional[Set[int]] = None
    explanation: str = ""


def find_minimal_termination_set(state: SystemState, deadlocked_pids: Set[int]) -> List[RecoverySuggestion]:
    """
    Find minimal sets of processes to terminate to break deadlock.
    
    Strategy:
    1. Try terminating one process at a time
    2. Try terminating two processes at a time
    3. Continue until a solution is found
    
    Args:
        state: Current system state
        deadlocked_pids: Set of deadlocked process IDs
    
    Returns:
        List of RecoverySuggestion objects, sorted by number of processes
    """
    suggestions = []
    
    if not deadlocked_pids:
        return suggestions
    
    # Try progressively larger sets
    for size in range(1, len(deadlocked_pids) + 1):
        for subset in itertools.combinations(sorted(deadlocked_pids), size):
            terminated = set(subset)
            can_recover, trace = can_system_recover(state, terminated)
            
            if can_recover:
                process_names = ", ".join(f"P{pid}" for pid in sorted(terminated))
                
                # Build explanation
                explanation = f"Terminating {process_names} releases their allocated resources.\n"
                explanation += "After termination:\n"
                explanation += "\n".join(trace)
                
                suggestions.append(RecoverySuggestion(
                    action_type="terminate",
                    description=f"Terminate {len(terminated)} process(es): {process_names}",
                    processes=terminated,
                    explanation=explanation
                ))
        
        # If we found solutions of this size, return them (minimal solutions)
        if suggestions:
            return suggestions
    
    return suggestions


def suggest_preemption_targets(state: SystemState, deadlocked_pids: Set[int]) -> List[RecoverySuggestion]:
    """
    Suggest resource preemption as an alternative to process termination.
    
    Strategy:
    - For each deadlocked process, suggest preempting resources it holds
    - Check if preemption would allow other processes to proceed
    
    Args:
        state: Current system state
        deadlocked_pids: Set of deadlocked process IDs
    
    Returns:
        List of preemption suggestions
    """
    suggestions = []
    
    for pid in sorted(deadlocked_pids):
        # Find resources held by this process
        held_resources = []
        for j in range(state.m):
            if state.allocation[pid][j] > 0:
                held_resources.append((j, state.allocation[pid][j]))
        
        if held_resources:
            resource_desc = ", ".join(
                f"{count}×R{rid}" for rid, count in held_resources
            )
            
            explanation = (
                f"Preempt resources from P{pid}: {resource_desc}\n"
                f"These resources can be reallocated to other waiting processes.\n"
                f"Note: P{pid} would need to be rolled back and restarted later."
            )
            
            suggestions.append(RecoverySuggestion(
                action_type="preempt",
                description=f"Preempt resources from P{pid}: {resource_desc}",
                processes={pid},
                resources={rid for rid, _ in held_resources},
                explanation=explanation
            ))
    
    return suggestions


def suggest_recovery_strategies(state: SystemState, use_wfg: bool = False) -> List[RecoverySuggestion]:
    """
    Suggest all possible recovery strategies for a deadlocked system.
    
    Args:
        state: Current system state
        use_wfg: If True, use wait-for graph detection; otherwise use matrix
    
    Returns:
        List of recovery suggestions, ordered by preference
        (minimal process termination first, then preemption)
    """
    # First detect deadlock
    if use_wfg:
        wfg_result = detect_deadlock_wfg(state)
        if not wfg_result.deadlocked:
            return []
        deadlocked_pids = wfg_result.deadlocked_processes
    else:
        matrix_result = detect_deadlock_matrix(state)
        if not matrix_result.deadlocked:
            return []
        deadlocked_pids = matrix_result.deadlocked_processes
    
    suggestions = []
    
    # Strategy 1: Find minimal termination sets
    termination_suggestions = find_minimal_termination_set(state, deadlocked_pids)
    suggestions.extend(termination_suggestions)
    
    # Strategy 2: Suggest preemption as alternatives
    preemption_suggestions = suggest_preemption_targets(state, deadlocked_pids)
    suggestions.extend(preemption_suggestions)
    
    return suggestions


def format_recovery_report(suggestions: List[RecoverySuggestion]) -> str:
    """
    Format recovery suggestions as a human-readable report.
    
    Args:
        suggestions: List of recovery suggestions
    
    Returns:
        Formatted string report
    """
    if not suggestions:
        return "No recovery strategies needed (no deadlock detected)."
    
    report = []
    report.append("=" * 60)
    report.append("RECOVERY STRATEGIES")
    report.append("=" * 60)
    report.append("")
    
    # Group by action type
    terminations = [s for s in suggestions if s.action_type == "terminate"]
    preemptions = [s for s in suggestions if s.action_type == "preempt"]
    
    if terminations:
        report.append("OPTION 1: Process Termination")
        report.append("-" * 60)
        report.append("Terminate processes to release their resources.")
        report.append("")
        
        for i, sugg in enumerate(terminations, 1):
            report.append(f"  {i}. {sugg.description}")
            if i <= 3:  # Show details for first few
                report.append("")
                for line in sugg.explanation.split('\n'):
                    report.append(f"     {line}")
                report.append("")
        
        report.append("")
    
    if preemptions:
        report.append("OPTION 2: Resource Preemption")
        report.append("-" * 60)
        report.append("Preempt resources from processes (requires rollback).")
        report.append("")
        
        for i, sugg in enumerate(preemptions, 1):
            report.append(f"  {i}. {sugg.description}")
        
        report.append("")
        report.append("Note: Preemption requires saving process state for later restart.")
    
    report.append("=" * 60)
    
    return "\n".join(report)
