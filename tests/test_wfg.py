"""
Unit tests for Wait-For Graph deadlock detector.
"""

import pytest
from models import SystemState, Process, ResourceType
from detectors.wfg import detect_deadlock_wfg, build_wait_for_graph


def test_wfg_no_deadlock():
    """Test WFG detection with no deadlock."""
    # P0 holds R0, requests R1
    # P1 holds R1, no requests (can finish)
    # P2 holds R2, no requests (can finish)
    
    processes = [Process(i, f"P{i}") for i in range(3)]
    resource_types = [ResourceType(i, f"R{i}", 1) for i in range(3)]
    
    available = [0, 0, 0]
    allocation = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]
    request = [
        [0, 1, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]
    
    state = SystemState(processes, resource_types, available, allocation, request)
    result = detect_deadlock_wfg(state)
    
    assert not result.deadlocked
    assert len(result.deadlocked_processes) == 0
    assert len(result.cycles) == 0


def test_wfg_simple_cycle():
    """Test WFG detection with simple 2-process cycle."""
    # P0 holds R0, requests R1
    # P1 holds R1, requests R0
    # Forms cycle: P0 → P1 → P0
    
    processes = [Process(i, f"P{i}") for i in range(2)]
    resource_types = [ResourceType(i, f"R{i}", 1) for i in range(2)]
    
    available = [0, 0]
    allocation = [
        [1, 0],
        [0, 1],
    ]
    request = [
        [0, 1],
        [1, 0],
    ]
    
    state = SystemState(processes, resource_types, available, allocation, request)
    result = detect_deadlock_wfg(state)
    
    assert result.deadlocked
    assert len(result.deadlocked_processes) == 2
    assert 0 in result.deadlocked_processes
    assert 1 in result.deadlocked_processes
    assert len(result.cycles) >= 1


def test_wfg_three_process_cycle():
    """Test WFG detection with 3-process cycle."""
    # P0 holds R0, requests R1
    # P1 holds R1, requests R2
    # P2 holds R2, requests R0
    # Forms cycle: P0 → P1 → P2 → P0
    
    processes = [Process(i, f"P{i}") for i in range(3)]
    resource_types = [ResourceType(i, f"R{i}", 1) for i in range(3)]
    
    available = [0, 0, 0]
    allocation = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]
    request = [
        [0, 1, 0],
        [0, 0, 1],
        [1, 0, 0],
    ]
    
    state = SystemState(processes, resource_types, available, allocation, request)
    result = detect_deadlock_wfg(state)
    
    assert result.deadlocked
    assert len(result.deadlocked_processes) == 3
    assert result.deadlocked_processes == {0, 1, 2}
    assert len(result.cycles) >= 1


def test_wfg_no_requests():
    """Test WFG with no requests (no deadlock possible)."""
    processes = [Process(i, f"P{i}") for i in range(3)]
    resource_types = [ResourceType(i, f"R{i}", 1) for i in range(3)]
    
    available = [0, 0, 0]
    allocation = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]
    request = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]
    
    state = SystemState(processes, resource_types, available, allocation, request)
    result = detect_deadlock_wfg(state)
    
    assert not result.deadlocked
    assert len(result.wait_for_edges) == 0


def test_build_wait_for_graph():
    """Test wait-for graph construction."""
    # P0 holds R0, requests R1
    # P1 holds R1, requests R2
    
    processes = [Process(i, f"P{i}") for i in range(3)]
    resource_types = [ResourceType(i, f"R{i}", 1) for i in range(3)]
    
    available = [0, 0, 1]
    allocation = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 0],
    ]
    request = [
        [0, 1, 0],
        [0, 0, 1],
        [0, 0, 0],
    ]
    
    state = SystemState(processes, resource_types, available, allocation, request)
    adjacency, edges = build_wait_for_graph(state)
    
    # P0 waits for P1 (P1 holds R1)
    # P1 waits for nobody (R2 is available)
    assert 1 in adjacency[0]
    assert len(edges) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
