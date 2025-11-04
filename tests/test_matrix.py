"""
Unit tests for matrix-based deadlock detector.
"""

import pytest
from models import SystemState, Process, ResourceType
from detectors.matrix import detect_deadlock_matrix, vector_less_equal, vector_add


def test_vector_operations():
    """Test vector utility functions."""
    assert vector_less_equal([1, 0, 2], [1, 1, 2])
    assert vector_less_equal([0, 0, 0], [1, 1, 1])
    assert not vector_less_equal([2, 0, 0], [1, 1, 1])
    
    assert vector_add([1, 2, 3], [4, 5, 6]) == [5, 7, 9]
    assert vector_add([0, 0, 0], [1, 2, 3]) == [1, 2, 3]


def test_matrix_no_deadlock():
    """Test matrix detection with no deadlock."""
    # Classic safe state
    processes = [Process(i, f"P{i}") for i in range(5)]
    resource_types = [
        ResourceType(0, "R0", 10),
        ResourceType(1, "R1", 5),
        ResourceType(2, "R2", 7),
    ]
    
    available = [3, 3, 2]
    allocation = [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2],
    ]
    request = [
        [0, 0, 0],
        [1, 0, 2],
        [0, 0, 0],
        [1, 0, 0],
        [0, 0, 2],
    ]
    
    state = SystemState(processes, resource_types, available, allocation, request)
    result = detect_deadlock_matrix(state)
    
    assert not result.deadlocked
    assert len(result.deadlocked_processes) == 0
    assert all(result.finish)  # All processes finished


def test_matrix_with_deadlock():
    """Test matrix detection with deadlock."""
    # Scenario with true deadlock - all processes blocked
    processes = [Process(i, f"P{i}") for i in range(3)]
    resource_types = [
        ResourceType(0, "R0", 2),
        ResourceType(1, "R1", 2),
        ResourceType(2, "R2", 2),
    ]
    
    available = [0, 0, 0]  # Nothing available
    allocation = [
        [1, 0, 1],  # P0 holds 1 R0, 1 R2
        [1, 1, 0],  # P1 holds 1 R0, 1 R1
        [0, 1, 1],  # P2 holds 1 R1, 1 R2
    ]
    request = [
        [1, 1, 0],  # P0 requests 1 R0, 1 R1 (CANNOT get)
        [0, 1, 1],  # P1 requests 1 R1, 1 R2 (CANNOT get)
        [1, 0, 1],  # P2 requests 1 R0, 1 R2 (CANNOT get)
    ]
    
    state = SystemState(processes, resource_types, available, allocation, request)
    result = detect_deadlock_matrix(state)
    
    assert result.deadlocked, "Should detect deadlock"
    assert len(result.deadlocked_processes) == 3, "All 3 processes should be deadlocked"
    assert result.deadlocked_processes == {0, 1, 2}


def test_matrix_all_processes_can_finish():
    """Test that all processes can finish when sufficient resources available."""
    processes = [Process(i, f"P{i}") for i in range(3)]
    resource_types = [
        ResourceType(0, "R0", 10),
        ResourceType(1, "R1", 10),
    ]
    
    available = [5, 5]
    allocation = [
        [2, 1],
        [1, 2],
        [2, 2],
    ]
    request = [
        [1, 1],
        [2, 1],
        [1, 1],
    ]
    
    state = SystemState(processes, resource_types, available, allocation, request)
    result = detect_deadlock_matrix(state)
    
    assert not result.deadlocked
    assert len(result.execution_order) == 3


def test_matrix_single_instance():
    """Test matrix detection with single-instance resources."""
    # Should work correctly for single-instance too
    processes = [Process(i, f"P{i}") for i in range(3)]
    resource_types = [ResourceType(i, f"R{i}", 1) for i in range(3)]
    
    # Deadlock cycle
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
    result = detect_deadlock_matrix(state)
    
    assert result.deadlocked
    assert len(result.deadlocked_processes) == 3


def test_matrix_no_requests():
    """Test matrix detection when no process has requests."""
    processes = [Process(i, f"P{i}") for i in range(3)]
    resource_types = [
        ResourceType(0, "R0", 5),
        ResourceType(1, "R1", 5),
    ]
    
    available = [1, 1]
    allocation = [
        [2, 1],
        [1, 2],
        [1, 1],
    ]
    request = [
        [0, 0],
        [0, 0],
        [0, 0],
    ]
    
    state = SystemState(processes, resource_types, available, allocation, request)
    result = detect_deadlock_matrix(state)
    
    assert not result.deadlocked
    assert all(result.finish)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
