"""
JSON Schema and I/O for System States

This module handles loading and saving system states from/to JSON files.
Includes sample datasets for demonstration.
"""

import json
from typing import Dict, Any, List
from pathlib import Path
from models import SystemState, Process, ResourceType


# JSON Schema for validation
SCHEMA_VERSION = "1.0"


def system_state_to_dict(state: SystemState) -> Dict[str, Any]:
    """
    Convert SystemState to dictionary for JSON serialization.
    
    Args:
        state: SystemState to convert
    
    Returns:
        Dictionary representation
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "processes": [
            {"pid": p.pid, "name": p.name}
            for p in state.processes
        ],
        "resource_types": [
            {"rid": r.rid, "name": r.name, "instances": r.instances}
            for r in state.resource_types
        ],
        "available": state.available,
        "allocation": state.allocation,
        "request": state.request
    }


def dict_to_system_state(data: Dict[str, Any]) -> SystemState:
    """
    Convert dictionary to SystemState.
    
    Args:
        data: Dictionary from JSON
    
    Returns:
        SystemState object
    
    Raises:
        ValueError: If data is invalid
    """
    # Validate schema version
    if "schema_version" not in data:
        raise ValueError("Missing schema_version in JSON")
    
    # Parse processes
    processes = [
        Process(p["pid"], p["name"])
        for p in data["processes"]
    ]
    
    # Parse resource types
    resource_types = [
        ResourceType(r["rid"], r["name"], r["instances"])
        for r in data["resource_types"]
    ]
    
    # Create system state (validation happens in __post_init__)
    return SystemState(
        processes=processes,
        resource_types=resource_types,
        available=data["available"],
        allocation=data["allocation"],
        request=data["request"]
    )


def save_system_state(state: SystemState, filepath: str) -> None:
    """
    Save system state to JSON file.
    
    Args:
        state: SystemState to save
        filepath: Path to output file
    """
    data = system_state_to_dict(state)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_system_state(filepath: str) -> SystemState:
    """
    Load system state from JSON file.
    
    Args:
        filepath: Path to input file
    
    Returns:
        SystemState object
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON is invalid
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    return dict_to_system_state(data)


# ============================================================================
# Sample Datasets
# ============================================================================

def get_sample_single_instance_deadlock() -> SystemState:
    """
    Sample: Single-instance resources with deadlock (classic cycle).
    
    Scenario:
    - P0 holds R0, requests R1
    - P1 holds R1, requests R2
    - P2 holds R2, requests R0
    
    Forms cycle: P0 → P1 → P2 → P0
    """
    processes = [Process(i, f"P{i}") for i in range(3)]
    resource_types = [ResourceType(i, f"R{i}", 1) for i in range(3)]
    
    available = [0, 0, 0]  # All resources allocated
    
    allocation = [
        [1, 0, 0],  # P0 holds R0
        [0, 1, 0],  # P1 holds R1
        [0, 0, 1],  # P2 holds R2
    ]
    
    request = [
        [0, 1, 0],  # P0 requests R1
        [0, 0, 1],  # P1 requests R2
        [1, 0, 0],  # P2 requests R0
    ]
    
    return SystemState(processes, resource_types, available, allocation, request)


def get_sample_single_instance_no_deadlock() -> SystemState:
    """
    Sample: Single-instance resources without deadlock.
    
    Scenario:
    - P0 holds R0, requests R1
    - P1 holds R1, no requests
    - P2 holds R2, no requests
    
    P1 and P2 can finish, then P0 can get R1.
    """
    processes = [Process(i, f"P{i}") for i in range(3)]
    resource_types = [ResourceType(i, f"R{i}", 1) for i in range(3)]
    
    available = [0, 0, 0]
    
    allocation = [
        [1, 0, 0],  # P0 holds R0
        [0, 1, 0],  # P1 holds R1
        [0, 0, 1],  # P2 holds R2
    ]
    
    request = [
        [0, 1, 0],  # P0 requests R1
        [0, 0, 0],  # P1 no requests
        [0, 0, 0],  # P2 no requests
    ]
    
    return SystemState(processes, resource_types, available, allocation, request)


def get_sample_multi_instance_deadlock() -> SystemState:
    """
    Sample: Multi-instance resources with deadlock.
    
    Scenario:
    - 3 processes (P0, P1, P2)
    - 3 resource types (R0: 2 instances, R1: 2 instances, R2: 2 instances)
    
    Each process holds some resources and requests others, creating deadlock:
    - P0 holds [1, 0, 1], requests [1, 1, 0] (needs 1 R0, 1 R1)
    - P1 holds [1, 1, 0], requests [0, 1, 1] (needs 1 R1, 1 R2)
    - P2 holds [0, 1, 1], requests [1, 0, 1] (needs 1 R0, 1 R2)
    
    Available = [0, 0, 0] - nothing available
    
    No process can proceed:
    - P0 needs R0 (none available) and R1 (none available)
    - P1 needs R1 (none available) and R2 (none available)
    - P2 needs R0 (none available) and R2 (none available)
    
    All processes are deadlocked.
    """
    processes = [Process(i, f"P{i}") for i in range(3)]
    resource_types = [
        ResourceType(0, "R0", 2),
        ResourceType(1, "R1", 2),
        ResourceType(2, "R2", 2),
    ]
    
    available = [0, 0, 0]
    
    allocation = [
        [1, 0, 1],  # P0 holds 1 R0, 1 R2
        [1, 1, 0],  # P1 holds 1 R0, 1 R1
        [0, 1, 1],  # P2 holds 1 R1, 1 R2
    ]
    
    request = [
        [1, 1, 0],  # P0 requests 1 R0, 1 R1 (CANNOT: all allocated)
        [0, 1, 1],  # P1 requests 1 R1, 1 R2 (CANNOT: all allocated)
        [1, 0, 1],  # P2 requests 1 R0, 1 R2 (CANNOT: all allocated)
    ]
    
    return SystemState(processes, resource_types, available, allocation, request)


def get_sample_multi_instance_no_deadlock() -> SystemState:
    """
    Sample: Multi-instance resources without deadlock.
    
    All processes can eventually finish in some order.
    """
    processes = [Process(i, f"P{i}") for i in range(5)]
    resource_types = [
        ResourceType(0, "R0", 10),
        ResourceType(1, "R1", 5),
        ResourceType(2, "R2", 7),
    ]
    
    available = [3, 3, 2]
    
    allocation = [
        [0, 1, 0],  # P0
        [2, 0, 0],  # P1
        [3, 0, 2],  # P2
        [2, 1, 1],  # P3
        [0, 0, 2],  # P4
    ]
    
    request = [
        [0, 0, 0],  # P0 no requests
        [1, 0, 2],  # P1
        [0, 0, 0],  # P2 no requests
        [1, 0, 0],  # P3
        [0, 0, 2],  # P4
    ]
    
    return SystemState(processes, resource_types, available, allocation, request)


def get_sample_empty() -> SystemState:
    """
    Empty template: 3 processes, 3 resource types (single instance).
    """
    processes = [Process(i, f"P{i}") for i in range(3)]
    resource_types = [ResourceType(i, f"R{i}", 1) for i in range(3)]
    
    available = [1, 1, 1]
    allocation = [[0, 0, 0] for _ in range(3)]
    request = [[0, 0, 0] for _ in range(3)]
    
    return SystemState(processes, resource_types, available, allocation, request)


# Sample dataset registry
SAMPLES = {
    "Single-Instance: Deadlock (Cycle)": get_sample_single_instance_deadlock,
    "Single-Instance: No Deadlock": get_sample_single_instance_no_deadlock,
    "Multi-Instance: Deadlock": get_sample_multi_instance_deadlock,
    "Multi-Instance: No Deadlock": get_sample_multi_instance_no_deadlock,
    "Empty Template": get_sample_empty,
}


def get_sample_names() -> List[str]:
    """Get list of available sample names."""
    return list(SAMPLES.keys())


def load_sample(name: str) -> SystemState:
    """
    Load a sample by name.
    
    Args:
        name: Sample name from get_sample_names()
    
    Returns:
        SystemState for the sample
    
    Raises:
        KeyError: If sample name not found
    """
    if name not in SAMPLES:
        raise KeyError(f"Sample '{name}' not found. Available: {get_sample_names()}")
    return SAMPLES[name]()
