"""
Data Models for Deadlock Detective

This module defines the core data structures used in deadlock detection:
- Process: Represents a process in the system
- ResourceType: Represents a resource type with instance count
- SystemState: Contains the complete system state (Available, Allocation, Request matrices)

All notation follows standard OS textbook conventions.
"""

from dataclasses import dataclass, field
from typing import List, Dict
import copy


@dataclass
class Process:
    """
    Represents a process in the system.
    
    Attributes:
        pid: Process ID (e.g., 0 for P0, 1 for P1)
        name: Human-readable name (e.g., "P0", "P1")
    """
    pid: int
    name: str
    
    def __post_init__(self):
        if self.pid < 0:
            raise ValueError(f"Process ID must be non-negative, got {self.pid}")


@dataclass
class ResourceType:
    """
    Represents a resource type with instance count.
    
    Attributes:
        rid: Resource ID (e.g., 0 for R0, 1 for R1)
        name: Human-readable name (e.g., "R0", "R1")
        instances: Total number of instances of this resource type
    """
    rid: int
    name: str
    instances: int
    
    def __post_init__(self):
        if self.rid < 0:
            raise ValueError(f"Resource ID must be non-negative, got {self.rid}")
        if self.instances < 0:
            raise ValueError(f"Instance count must be non-negative, got {self.instances}")


@dataclass
class SystemState:
    """
    Complete system state for deadlock detection.
    
    Follows textbook notation:
    - n processes: P0, P1, ..., P(n-1)
    - m resource types: R0, R1, ..., R(m-1)
    - Available[m]: vector of available instances for each resource type
    - Allocation[n][m]: matrix where Allocation[i][j] = instances of Rj allocated to Pi
    - Request[n][m]: matrix where Request[i][j] = instances of Rj requested by Pi
    
    Invariant: For each resource type j:
        Available[j] + sum(Allocation[i][j] for all i) == ResourceTypes[j].instances
    """
    processes: List[Process]
    resource_types: List[ResourceType]
    available: List[int]  # Available[m]
    allocation: List[List[int]]  # Allocation[n][m]
    request: List[List[int]]  # Request[n][m]
    
    def __post_init__(self):
        """Validate the system state."""
        n = len(self.processes)
        m = len(self.resource_types)
        
        # Validate dimensions
        if len(self.available) != m:
            raise ValueError(f"Available vector must have {m} elements, got {len(self.available)}")
        
        if len(self.allocation) != n:
            raise ValueError(f"Allocation matrix must have {n} rows, got {len(self.allocation)}")
        
        if len(self.request) != n:
            raise ValueError(f"Request matrix must have {n} rows, got {len(self.request)}")
        
        for i, alloc_row in enumerate(self.allocation):
            if len(alloc_row) != m:
                raise ValueError(f"Allocation[{i}] must have {m} columns, got {len(alloc_row)}")
        
        for i, req_row in enumerate(self.request):
            if len(req_row) != m:
                raise ValueError(f"Request[{i}] must have {m} columns, got {len(req_row)}")
        
        # Validate non-negative values
        for i, val in enumerate(self.available):
            if val < 0:
                raise ValueError(f"Available[{i}] must be non-negative, got {val}")
        
        for i in range(n):
            for j in range(m):
                if self.allocation[i][j] < 0:
                    raise ValueError(f"Allocation[{i}][{j}] must be non-negative")
                if self.request[i][j] < 0:
                    raise ValueError(f"Request[{i}][{j}] must be non-negative")
        
        # Validate resource conservation
        for j in range(m):
            total_allocated = sum(self.allocation[i][j] for i in range(n))
            total = self.available[j] + total_allocated
            if total != self.resource_types[j].instances:
                raise ValueError(
                    f"Resource R{j}: Available ({self.available[j]}) + "
                    f"Allocated ({total_allocated}) != Total instances ({self.resource_types[j].instances})"
                )
        
        # Validate requests don't exceed total instances
        for i in range(n):
            for j in range(m):
                if self.request[i][j] > self.resource_types[j].instances:
                    raise ValueError(
                        f"Request[{i}][{j}] = {self.request[i][j]} exceeds "
                        f"total instances of R{j} = {self.resource_types[j].instances}"
                    )
    
    @property
    def n(self) -> int:
        """Number of processes."""
        return len(self.processes)
    
    @property
    def m(self) -> int:
        """Number of resource types."""
        return len(self.resource_types)
    
    def is_single_instance(self) -> bool:
        """
        Check if all resource types have exactly one instance.
        
        Returns:
            True if all resource types have exactly 1 instance (can use WFG),
            False otherwise (must use matrix detection)
        """
        return all(rt.instances == 1 for rt in self.resource_types)
    
    def clone(self) -> 'SystemState':
        """Create a deep copy of this system state."""
        return SystemState(
            processes=[Process(p.pid, p.name) for p in self.processes],
            resource_types=[ResourceType(rt.rid, rt.name, rt.instances) for rt in self.resource_types],
            available=self.available[:],
            allocation=[row[:] for row in self.allocation],
            request=[row[:] for row in self.request]
        )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"SystemState(n={self.n}, m={self.m}, "
            f"Available={self.available}, "
            f"Allocation={self.allocation}, "
            f"Request={self.request})"
        )


def create_empty_system_state(num_processes: int, num_resources: int) -> SystemState:
    """
    Create an empty system state with specified dimensions.
    
    Args:
        num_processes: Number of processes (n)
        num_resources: Number of resource types (m)
    
    Returns:
        SystemState with all zeros and single-instance resources
    """
    processes = [Process(i, f"P{i}") for i in range(num_processes)]
    resource_types = [ResourceType(j, f"R{j}", 1) for j in range(num_resources)]
    available = [1] * num_resources
    allocation = [[0] * num_resources for _ in range(num_processes)]
    request = [[0] * num_resources for _ in range(num_processes)]
    
    return SystemState(processes, resource_types, available, allocation, request)
