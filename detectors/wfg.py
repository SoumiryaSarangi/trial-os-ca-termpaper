"""
Wait-For Graph (WFG) Deadlock Detector

This module implements deadlock detection for single-instance resources using
a wait-for graph approach. A cycle in the WFG indicates deadlock.

Wait-For Graph Construction:
- Nodes: Processes (P0, P1, ..., Pn-1)
- Directed edge Pi → Pj: Pi is waiting for a resource currently held by Pj

Algorithm:
1. Build wait-for graph from Allocation and Request matrices
2. Use DFS to detect cycles (Tarjan's algorithm variant)
3. Extract all processes involved in cycles

Theory Note:
A cycle in a resource allocation graph implies deadlock ONLY if every resource
type has exactly one instance. For multi-instance resources, a cycle indicates
POSSIBLE deadlock, but matrix-based detection must be used for correctness.
"""

from typing import List, Set, Dict, Tuple, Optional
from dataclasses import dataclass
from models import SystemState


@dataclass
class WaitForEdge:
    """
    Represents a directed edge in the wait-for graph.
    
    Attributes:
        from_pid: Source process ID (Pi waits for Pj)
        to_pid: Destination process ID
        resource_id: The resource Pj holds that Pi wants
    """
    from_pid: int
    to_pid: int
    resource_id: int
    
    def __repr__(self) -> str:
        return f"P{self.from_pid} → P{self.to_pid} (R{self.resource_id})"


@dataclass
class CycleInfo:
    """
    Information about a detected cycle.
    
    Attributes:
        processes: List of process IDs in the cycle
        edges: List of edges forming the cycle
    """
    processes: List[int]
    edges: List[WaitForEdge]
    
    def __repr__(self) -> str:
        cycle_str = " → ".join(f"P{pid}" for pid in self.processes)
        if self.processes:
            cycle_str += f" → P{self.processes[0]}"  # Close the cycle
        return f"Cycle: {cycle_str}"


@dataclass
class WFGDetectionResult:
    """
    Result of wait-for graph deadlock detection.
    
    Attributes:
        deadlocked: Whether deadlock was detected
        deadlocked_processes: Set of process IDs involved in deadlock
        cycles: List of all cycles detected
        wait_for_edges: All edges in the wait-for graph
        trace: Step-by-step explanation of the detection process
    """
    deadlocked: bool
    deadlocked_processes: Set[int]
    cycles: List[CycleInfo]
    wait_for_edges: List[WaitForEdge]
    trace: List[str]


def build_wait_for_graph(state: SystemState) -> Tuple[Dict[int, Set[int]], List[WaitForEdge]]:
    """
    Build a wait-for graph from the system state.
    
    For each process Pi that requests a resource Rj:
    - Find all processes that currently hold Rj
    - Add edge Pi → Pk for each holder Pk
    
    Args:
        state: Current system state
    
    Returns:
        Tuple of (adjacency_list, edge_list)
        - adjacency_list: Dict mapping pid to set of pids it waits for
        - edge_list: List of WaitForEdge objects
    """
    adjacency: Dict[int, Set[int]] = {i: set() for i in range(state.n)}
    edges: List[WaitForEdge] = []
    
    # For each process Pi
    for i in range(state.n):
        # For each resource Rj that Pi requests
        for j in range(state.m):
            if state.request[i][j] > 0:
                # Find processes that hold Rj
                for k in range(state.n):
                    if k != i and state.allocation[k][j] > 0:
                        # Pi waits for Pk (Pk holds Rj that Pi wants)
                        adjacency[i].add(k)
                        edges.append(WaitForEdge(i, k, j))
    
    return adjacency, edges


def detect_cycles_dfs(adjacency: Dict[int, Set[int]], n: int) -> List[CycleInfo]:
    """
    Detect all cycles in the wait-for graph using DFS.
    
    Uses a modified DFS that tracks the current path to detect and extract cycles.
    
    Args:
        adjacency: Adjacency list representation of the graph
        n: Number of nodes (processes)
    
    Returns:
        List of CycleInfo objects, one for each cycle found
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n
    parent = [-1] * n
    cycles = []
    
    def dfs(node: int, path: List[int]) -> None:
        """DFS helper that detects cycles."""
        color[node] = GRAY
        path.append(node)
        
        for neighbor in adjacency[node]:
            if color[neighbor] == GRAY:
                # Back edge found - cycle detected!
                # Extract cycle from path
                cycle_start_idx = path.index(neighbor)
                cycle_nodes = path[cycle_start_idx:] + [neighbor]
                
                # Create edges for the cycle
                cycle_edges = []
                for i in range(len(cycle_nodes) - 1):
                    from_pid = cycle_nodes[i]
                    to_pid = cycle_nodes[i + 1]
                    # Find the resource causing this edge (simplified - take first match)
                    cycle_edges.append(WaitForEdge(from_pid, to_pid, -1))
                
                cycles.append(CycleInfo(
                    processes=path[cycle_start_idx:],
                    edges=cycle_edges
                ))
            elif color[neighbor] == WHITE:
                parent[neighbor] = node
                dfs(neighbor, path)
        
        color[node] = BLACK
        path.pop()
    
    # Run DFS from each unvisited node
    for i in range(n):
        if color[i] == WHITE:
            dfs(i, [])
    
    return cycles


def detect_deadlock_wfg(state: SystemState) -> WFGDetectionResult:
    """
    Detect deadlock using wait-for graph cycle detection.
    
    This method is correct ONLY for single-instance resources.
    
    Algorithm:
    1. Build wait-for graph from Allocation and Request matrices
    2. Detect cycles using DFS
    3. All processes in cycles are deadlocked
    
    Args:
        state: Current system state
    
    Returns:
        WFGDetectionResult with deadlock information and trace
    """
    trace = []
    trace.append("=== Wait-For Graph Deadlock Detection ===")
    trace.append(f"System: {state.n} processes, {state.m} resource types")
    trace.append("")
    
    # Validate single-instance assumption
    if not state.is_single_instance():
        trace.append("WARNING: Not all resources have single instance!")
        trace.append("Wait-for graph cycle detection may give incorrect results.")
        trace.append("Use matrix-based detection for multi-instance resources.")
        trace.append("")
    
    # Build wait-for graph
    trace.append("Step 1: Building Wait-For Graph")
    adjacency, edges = build_wait_for_graph(state)
    
    if not edges:
        trace.append("  No wait-for edges found (no process is waiting).")
        trace.append("")
        trace.append("Result: NO DEADLOCK")
        return WFGDetectionResult(
            deadlocked=False,
            deadlocked_processes=set(),
            cycles=[],
            wait_for_edges=[],
            trace=trace
        )
    
    trace.append("  Wait-for edges:")
    for edge in edges:
        trace.append(f"    {edge}")
    trace.append("")
    
    # Detect cycles
    trace.append("Step 2: Detecting Cycles using DFS")
    cycles = detect_cycles_dfs(adjacency, state.n)
    
    if not cycles:
        trace.append("  No cycles found in wait-for graph.")
        trace.append("")
        trace.append("Result: NO DEADLOCK")
        return WFGDetectionResult(
            deadlocked=False,
            deadlocked_processes=set(),
            cycles=[],
            wait_for_edges=edges,
            trace=trace
        )
    
    # Extract deadlocked processes
    deadlocked_pids = set()
    for cycle in cycles:
        deadlocked_pids.update(cycle.processes)
        trace.append(f"  {cycle}")
    
    trace.append("")
    trace.append(f"Step 3: Deadlocked Processes")
    trace.append(f"  Processes in cycles: {{{', '.join(f'P{pid}' for pid in sorted(deadlocked_pids))}}}")
    trace.append("")
    trace.append("Result: DEADLOCK DETECTED")
    
    return WFGDetectionResult(
        deadlocked=True,
        deadlocked_processes=deadlocked_pids,
        cycles=cycles,
        wait_for_edges=edges,
        trace=trace
    )


def get_wait_for_graph_for_visualization(state: SystemState) -> Tuple[List[Tuple[int, int]], Set[int]]:
    """
    Get wait-for graph data for visualization.
    
    Args:
        state: Current system state
    
    Returns:
        Tuple of (edges, deadlocked_nodes)
        - edges: List of (from_pid, to_pid) tuples
        - deadlocked_nodes: Set of process IDs involved in deadlock
    """
    result = detect_deadlock_wfg(state)
    edge_tuples = [(e.from_pid, e.to_pid) for e in result.wait_for_edges]
    return edge_tuples, result.deadlocked_processes
