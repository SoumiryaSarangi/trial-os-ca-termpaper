"""
Matrix-Based Deadlock Detector

This module implements the detection algorithm for multi-instance resources
using the Work/Finish approach with Available, Allocation, and Request matrices.

Algorithm (from OS textbooks):
1. Initialize Work = Available (work vector tracks available resources)
2. Initialize Finish[i] = False for all processes
3. Find a process Pi where:
   - Finish[i] == False
   - Request[i] ≤ Work (Pi can complete with available resources)
4. If found:
   - Set Finish[i] = True
   - Work = Work + Allocation[i] (Pi releases its resources)
   - Go to step 3
5. If no such process exists:
   - Deadlocked processes = {Pi | Finish[i] == False}

Theory Note:
This algorithm is correct for both single-instance and multi-instance resources.
For single-instance resources, the wait-for graph method is simpler but equivalent.
"""

from typing import List, Set, Tuple
from dataclasses import dataclass
from models import SystemState


@dataclass
class MatrixDetectionResult:
    """
    Result of matrix-based deadlock detection.
    
    Attributes:
        deadlocked: Whether deadlock was detected
        deadlocked_processes: Set of process IDs that are deadlocked
        finish: Final Finish vector (True if process can complete)
        execution_order: List of process IDs in order they were marked finished
        trace: Step-by-step explanation of the detection algorithm
    """
    deadlocked: bool
    deadlocked_processes: Set[int]
    finish: List[bool]
    execution_order: List[int]
    trace: List[str]


def vector_less_equal(req: List[int], work: List[int]) -> bool:
    """
    Check if request vector ≤ work vector (component-wise).
    
    Args:
        req: Request vector
        work: Work (available) vector
    
    Returns:
        True if req[i] ≤ work[i] for all i
    """
    return all(r <= w for r, w in zip(req, work))


def vector_add(a: List[int], b: List[int]) -> List[int]:
    """
    Add two vectors component-wise.
    
    Args:
        a: First vector
        b: Second vector
    
    Returns:
        New vector where result[i] = a[i] + b[i]
    """
    return [x + y for x, y in zip(a, b)]


def vector_to_string(vec: List[int]) -> str:
    """Format a vector as a string for display."""
    return "[" + ", ".join(str(x) for x in vec) + "]"


def detect_deadlock_matrix(state: SystemState) -> MatrixDetectionResult:
    """
    Detect deadlock using matrix-based algorithm with Work and Finish vectors.
    
    This is the standard detection algorithm for multi-instance resources.
    
    Algorithm:
    1. Work = Available, Finish[i] = False for all i
    2. Find process Pi where Finish[i] == False and Request[i] ≤ Work
    3. Mark Finish[i] = True, add Allocation[i] to Work
    4. Repeat step 2-3 until no such process exists
    5. Remaining unfinished processes are deadlocked
    
    Args:
        state: Current system state
    
    Returns:
        MatrixDetectionResult with deadlock information and detailed trace
    """
    n = state.n
    m = state.m
    
    trace = []
    trace.append("=== Matrix-Based Deadlock Detection ===")
    trace.append(f"System: {n} processes, {m} resource types")
    trace.append("")
    
    # Display initial state
    trace.append("Initial State:")
    trace.append(f"  Available: {vector_to_string(state.available)}")
    trace.append("")
    trace.append("  Allocation Matrix:")
    for i in range(n):
        trace.append(f"    P{i}: {vector_to_string(state.allocation[i])}")
    trace.append("")
    trace.append("  Request Matrix:")
    for i in range(n):
        trace.append(f"    P{i}: {vector_to_string(state.request[i])}")
    trace.append("")
    
    # Step 1: Initialize Work and Finish
    trace.append("Step 1: Initialize")
    work = state.available[:]  # Copy available vector
    finish = [False] * n
    execution_order = []
    
    trace.append(f"  Work = Available = {vector_to_string(work)}")
    trace.append(f"  Finish = [False, False, ..., False] (all {n} processes)")
    trace.append("")
    
    # Step 2-4: Iteratively find processes that can finish
    trace.append("Step 2-4: Find processes that can complete")
    iteration = 1
    
    while True:
        # Find a process that can finish
        found = False
        for i in range(n):
            if not finish[i] and vector_less_equal(state.request[i], work):
                # Process Pi can finish
                found = True
                finish[i] = True
                execution_order.append(i)
                
                trace.append(f"  Iteration {iteration}:")
                trace.append(f"    Found P{i}: Request[{i}] = {vector_to_string(state.request[i])} ≤ Work = {vector_to_string(work)}")
                
                # Release resources
                old_work = work[:]
                work = vector_add(work, state.allocation[i])
                trace.append(f"    P{i} finishes and releases Allocation[{i}] = {vector_to_string(state.allocation[i])}")
                trace.append(f"    Work = {vector_to_string(old_work)} + {vector_to_string(state.allocation[i])} = {vector_to_string(work)}")
                trace.append(f"    Finish[{i}] = True")
                trace.append("")
                
                iteration += 1
                break  # Start over from the beginning
        
        if not found:
            # No process can finish
            break
    
    # Step 5: Check for deadlock
    trace.append("Step 5: Check for Deadlock")
    deadlocked_pids = {i for i in range(n) if not finish[i]}
    
    if deadlocked_pids:
        trace.append(f"  Processes that cannot finish (Finish[i] = False):")
        for i in sorted(deadlocked_pids):
            trace.append(f"    P{i}: Request = {vector_to_string(state.request[i])}, Work = {vector_to_string(work)}")
            trace.append(f"          Request[{i}] > Work (cannot be satisfied)")
        trace.append("")
        trace.append(f"Result: DEADLOCK DETECTED")
        trace.append(f"  Deadlocked processes: {{{', '.join(f'P{i}' for i in sorted(deadlocked_pids))}}}")
    else:
        trace.append("  All processes finished successfully (Finish[i] = True for all i)")
        trace.append("")
        trace.append("Result: NO DEADLOCK")
        if execution_order:
            trace.append(f"  Safe execution sequence: {' → '.join(f'P{i}' for i in execution_order)}")
    
    return MatrixDetectionResult(
        deadlocked=len(deadlocked_pids) > 0,
        deadlocked_processes=deadlocked_pids,
        finish=finish,
        execution_order=execution_order,
        trace=trace
    )


def can_system_recover(state: SystemState, terminated_pids: Set[int]) -> Tuple[bool, List[str]]:
    """
    Check if system can recover if specified processes are terminated.
    
    When processes are terminated, their allocated resources are released.
    
    Args:
        state: Current system state
        terminated_pids: Set of process IDs to terminate
    
    Returns:
        Tuple of (can_recover, trace)
        - can_recover: True if remaining processes can all finish
        - trace: Explanation of the recovery check
    """
    trace = []
    trace.append(f"Checking recovery by terminating: {{{', '.join(f'P{i}' for i in sorted(terminated_pids))}}}")
    
    # Create modified state
    new_available = state.available[:]
    for pid in terminated_pids:
        new_available = vector_add(new_available, state.allocation[pid])
    
    trace.append(f"  Released resources: {vector_to_string(new_available)}")
    
    # Create new system state with terminated processes removed
    remaining_pids = [i for i in range(state.n) if i not in terminated_pids]
    if not remaining_pids:
        trace.append("  All processes terminated.")
        return True, trace
    
    # Build reduced system
    new_processes = [state.processes[i] for i in remaining_pids]
    new_allocation = [state.allocation[i] for i in remaining_pids]
    new_request = [state.request[i] for i in remaining_pids]
    
    reduced_state = SystemState(
        processes=new_processes,
        resource_types=state.resource_types,
        available=new_available,
        allocation=new_allocation,
        request=new_request
    )
    
    # Run detection on reduced system
    result = detect_deadlock_matrix(reduced_state)
    
    if not result.deadlocked:
        trace.append("  Remaining processes can all finish!")
        trace.append(f"  Execution order: {' → '.join(f'P{remaining_pids[i]}' for i in result.execution_order)}")
        return True, trace
    else:
        trace.append("  Remaining processes still deadlocked.")
        return False, trace
