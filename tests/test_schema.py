"""
Unit tests for schema I/O and samples.
"""

import pytest
import tempfile
import os
from models import SystemState, Process, ResourceType
from io_utils.schema import (
    system_state_to_dict, dict_to_system_state,
    save_system_state, load_system_state,
    get_sample_names, load_sample,
    get_sample_single_instance_deadlock,
    get_sample_multi_instance_deadlock
)


def test_system_state_to_dict():
    """Test serialization of SystemState to dict."""
    processes = [Process(0, "P0"), Process(1, "P1")]
    resource_types = [ResourceType(0, "R0", 3), ResourceType(1, "R1", 2)]
    available = [1, 0]
    allocation = [[1, 1], [1, 1]]
    request = [[0, 1], [1, 0]]
    
    state = SystemState(processes, resource_types, available, allocation, request)
    data = system_state_to_dict(state)
    
    assert "schema_version" in data
    assert len(data["processes"]) == 2
    assert len(data["resource_types"]) == 2
    assert data["available"] == [1, 0]
    assert data["allocation"] == [[1, 1], [1, 1]]
    assert data["request"] == [[0, 1], [1, 0]]


def test_dict_to_system_state():
    """Test deserialization of dict to SystemState."""
    data = {
        "schema_version": "1.0",
        "processes": [
            {"pid": 0, "name": "P0"},
            {"pid": 1, "name": "P1"}
        ],
        "resource_types": [
            {"rid": 0, "name": "R0", "instances": 3},
            {"rid": 1, "name": "R1", "instances": 2}
        ],
        "available": [1, 0],
        "allocation": [[1, 1], [1, 1]],
        "request": [[0, 1], [1, 0]]
    }
    
    state = dict_to_system_state(data)
    
    assert state.n == 2
    assert state.m == 2
    assert state.available == [1, 0]
    assert state.allocation == [[1, 1], [1, 1]]
    assert state.request == [[0, 1], [1, 0]]


def test_save_and_load_system_state():
    """Test saving and loading SystemState to/from file."""
    processes = [Process(0, "P0"), Process(1, "P1")]
    resource_types = [ResourceType(0, "R0", 3), ResourceType(1, "R1", 2)]
    available = [1, 0]
    allocation = [[1, 1], [1, 1]]
    request = [[0, 1], [1, 0]]
    
    state = SystemState(processes, resource_types, available, allocation, request)
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        filepath = f.name
    
    try:
        save_system_state(state, filepath)
        
        # Load back
        loaded_state = load_system_state(filepath)
        
        assert loaded_state.n == state.n
        assert loaded_state.m == state.m
        assert loaded_state.available == state.available
        assert loaded_state.allocation == state.allocation
        assert loaded_state.request == state.request
    finally:
        os.unlink(filepath)


def test_get_sample_names():
    """Test getting list of sample names."""
    names = get_sample_names()
    
    assert len(names) > 0
    assert "Single-Instance: Deadlock (Cycle)" in names
    assert "Multi-Instance: Deadlock" in names


def test_load_sample():
    """Test loading a sample by name."""
    state = load_sample("Single-Instance: Deadlock (Cycle)")
    
    assert state.n == 3
    assert state.m == 3
    assert state.is_single_instance()


def test_sample_single_instance_deadlock():
    """Test single-instance deadlock sample is valid."""
    state = get_sample_single_instance_deadlock()
    
    assert state.n == 3
    assert state.m == 3
    assert state.is_single_instance()
    
    # All resources allocated
    assert state.available == [0, 0, 0]
    
    # Each process holds one resource and requests another
    assert sum(state.allocation[0]) == 1
    assert sum(state.allocation[1]) == 1
    assert sum(state.allocation[2]) == 1


def test_sample_multi_instance_deadlock():
    """Test multi-instance deadlock sample is valid."""
    state = get_sample_multi_instance_deadlock()
    
    assert state.n == 3
    assert state.m == 3
    
    # Has multi-instance resources
    assert any(rt.instances > 1 for rt in state.resource_types)
    
    # Verify it actually detects deadlock
    from detectors.matrix import detect_deadlock_matrix
    result = detect_deadlock_matrix(state)
    assert result.deadlocked, "Multi-instance deadlock sample should detect deadlock"
    assert len(result.deadlocked_processes) == 3, "All 3 processes should be deadlocked"


def test_invalid_sample_name():
    """Test loading invalid sample name raises error."""
    with pytest.raises(KeyError):
        load_sample("Non-Existent Sample")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
