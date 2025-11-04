"""
Comprehensive Edge Case Tests for Deadlock Detective

Tests for corner cases, boundary conditions, and tricky scenarios
that instructors commonly use for grading.
"""

import pytest
from models import SystemState, Process, ResourceType
from detectors.wfg import detect_deadlock_wfg
from detectors.matrix import detect_deadlock_matrix


class TestSingleProcess:
    """Edge cases with single process."""
    
    def test_single_process_no_requests(self):
        """Single process with no requests - should not deadlock."""
        processes = [Process(0, "P0")]
        resource_types = [ResourceType(0, "R0", 1)]
        available = [0]
        allocation = [[1]]
        request = [[0]]
        
        state = SystemState(processes, resource_types, available, allocation, request)
        
        # Matrix detection
        result_matrix = detect_deadlock_matrix(state)
        assert not result_matrix.deadlocked
        
        # WFG detection
        result_wfg = detect_deadlock_wfg(state)
        assert not result_wfg.deadlocked
    
    def test_single_process_requesting_held_resource(self):
        """Single process requesting resource it already holds - should deadlock."""
        processes = [Process(0, "P0")]
        resource_types = [ResourceType(0, "R0", 1)]
        available = [0]
        allocation = [[1]]
        request = [[1]]  # Requesting what it already has
        
        state = SystemState(processes, resource_types, available, allocation, request)
        
        # Matrix detection
        result_matrix = detect_deadlock_matrix(state)
        assert result_matrix.deadlocked
        assert 0 in result_matrix.deadlocked_processes
        
        # WFG detection - self-loop
        result_wfg = detect_deadlock_wfg(state)
        # Single process can't have wait-for relationship with single-instance


class TestTwoProcessSymmetricDeadlock:
    """Classic two-process symmetric deadlock."""
    
    def test_two_process_cycle(self):
        """P0 waits for P1, P1 waits for P0."""
        processes = [Process(0, "P0"), Process(1, "P1")]
        resource_types = [ResourceType(0, "R0", 1), ResourceType(1, "R1", 1)]
        available = [0, 0]
        allocation = [
            [1, 0],  # P0 holds R0
            [0, 1],  # P1 holds R1
        ]
        request = [
            [0, 1],  # P0 requests R1
            [1, 0],  # P1 requests R0
        ]
        
        state = SystemState(processes, resource_types, available, allocation, request)
        
        # Both should detect deadlock
        result_matrix = detect_deadlock_matrix(state)
        assert result_matrix.deadlocked
        assert result_matrix.deadlocked_processes == {0, 1}
        
        result_wfg = detect_deadlock_wfg(state)
        assert result_wfg.deadlocked
        assert len(result_wfg.cycles) > 0


class TestAllResourcesAvailable:
    """Cases where resources are available."""
    
    def test_all_resources_free(self):
        """All resources available - no deadlock possible."""
        processes = [Process(i, f"P{i}") for i in range(3)]
        resource_types = [ResourceType(i, f"R{i}", 2) for i in range(3)]
        available = [2, 2, 2]  # All free
        allocation = [[0, 0, 0] for _ in range(3)]
        request = [[0, 0, 0] for _ in range(3)]
        
        state = SystemState(processes, resource_types, available, allocation, request)
        
        result = detect_deadlock_matrix(state)
        assert not result.deadlocked
    
    def test_processes_can_finish_sequentially(self):
        """Processes can finish one after another."""
        processes = [Process(i, f"P{i}") for i in range(3)]
        resource_types = [ResourceType(0, "R0", 3)]
        available = [0]  # Fixed: 0 + 1 + 1 + 1 = 3
        allocation = [
            [1],  # P0 has 1
            [1],  # P1 has 1
            [1],  # P2 has 1
        ]
        request = [
            [0],  # P0 needs nothing more
            [0],  # P1 needs nothing more
            [0],  # P2 needs nothing more
        ]
        
        state = SystemState(processes, resource_types, available, allocation, request)
        result = detect_deadlock_matrix(state)
        assert not result.deadlocked


class TestLargeScaleDeadlocks:
    """Tests with many processes."""
    
    def test_long_cycle(self):
        """5-process circular wait: P0→P1→P2→P3→P4→P0."""
        n = 5
        processes = [Process(i, f"P{i}") for i in range(n)]
        resource_types = [ResourceType(i, f"R{i}", 1) for i in range(n)]
        available = [0] * n
        
        # Each process holds Ri and requests R(i+1) mod n
        allocation = [[0] * n for _ in range(n)]
        request = [[0] * n for _ in range(n)]
        
        for i in range(n):
            allocation[i][i] = 1
            request[i][(i + 1) % n] = 1
        
        state = SystemState(processes, resource_types, available, allocation, request)
        
        result_wfg = detect_deadlock_wfg(state)
        assert result_wfg.deadlocked
        assert len(result_wfg.cycles) > 0
        
        result_matrix = detect_deadlock_matrix(state)
        assert result_matrix.deadlocked
        assert len(result_matrix.deadlocked_processes) == n


class TestPartialDeadlock:
    """Some processes deadlocked, others not."""
    
    def test_partial_deadlock_with_safe_process(self):
        """P0 and P1 deadlocked, P2 safe."""
        processes = [Process(i, f"P{i}") for i in range(3)]
        resource_types = [
            ResourceType(0, "R0", 1),
            ResourceType(1, "R1", 1),
            ResourceType(2, "R2", 1),
        ]
        available = [0, 0, 1]
        allocation = [
            [1, 0, 0],  # P0 holds R0
            [0, 1, 0],  # P1 holds R1
            [0, 0, 0],  # P2 holds nothing
        ]
        request = [
            [0, 1, 0],  # P0 requests R1 (held by P1)
            [1, 0, 0],  # P1 requests R0 (held by P0)
            [0, 0, 1],  # P2 requests R2 (available)
        ]
        
        state = SystemState(processes, resource_types, available, allocation, request)
        
        result_matrix = detect_deadlock_matrix(state)
        # P2 should finish first, releasing nothing
        # Then P0 and P1 still deadlocked
        assert result_matrix.deadlocked
        assert 0 in result_matrix.deadlocked_processes
        assert 1 in result_matrix.deadlocked_processes
        assert 2 not in result_matrix.deadlocked_processes


class TestMultiInstanceComplexCases:
    """Complex multi-instance scenarios."""
    
    def test_banker_safe_state(self):
        """Classic Banker's algorithm safe state."""
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
        # Max needs would be allocation + request
        request = [
            [7, 4, 3],  # P0 max need
            [1, 2, 2],  # P1 remaining need
            [6, 0, 0],  # P2 remaining need
            [0, 1, 1],  # P3 remaining need
            [4, 3, 1],  # P4 remaining need
        ]
        
        state = SystemState(processes, resource_types, available, allocation, request)
        result = detect_deadlock_matrix(state)
        # Should find safe sequence
        assert not result.deadlocked
    
    def test_insufficient_total_resources(self):
        """Total requests exceed total available - should deadlock."""
        processes = [Process(i, f"P{i}") for i in range(2)]
        resource_types = [ResourceType(0, "R0", 3)]
        available = [1]
        allocation = [
            [1],  # P0 has 1
            [1],  # P1 has 1
        ]
        request = [
            [2],  # P0 wants 2 more (needs 3 total)
            [2],  # P1 wants 2 more (needs 3 total)
        ]
        # Both need 3 total, but only 3 exist - deadlock
        
        state = SystemState(processes, resource_types, available, allocation, request)
        result = detect_deadlock_matrix(state)
        assert result.deadlocked


class TestBoundaryConditions:
    """Boundary and edge conditions."""
    
    def test_zero_available_resources(self):
        """All resources allocated."""
        processes = [Process(i, f"P{i}") for i in range(2)]
        resource_types = [ResourceType(0, "R0", 2)]
        available = [0]
        allocation = [
            [1],
            [1],
        ]
        request = [
            [1],  # Each wants 1 more
            [1],
        ]
        
        state = SystemState(processes, resource_types, available, allocation, request)
        result = detect_deadlock_matrix(state)
        assert result.deadlocked
    
    def test_maximum_resources(self):
        """Large number of resources."""
        processes = [Process(i, f"P{i}") for i in range(3)]
        resource_types = [ResourceType(0, "R0", 100)]
        available = [97]
        allocation = [
            [1],
            [1],
            [1],
        ]
        request = [[0], [0], [0]]
        
        state = SystemState(processes, resource_types, available, allocation, request)
        result = detect_deadlock_matrix(state)
        assert not result.deadlocked


class TestNoRequestCases:
    """Processes with no pending requests."""
    
    def test_all_processes_satisfied(self):
        """All processes have what they need."""
        processes = [Process(i, f"P{i}") for i in range(3)]
        resource_types = [ResourceType(i, f"R{i}", 2) for i in range(3)]
        available = [1, 1, 1]
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
        result = detect_deadlock_matrix(state)
        assert not result.deadlocked
        assert len(result.execution_order) == 3


class TestResourceConservation:
    """Test resource conservation validation."""
    
    def test_valid_resource_conservation(self):
        """Available + allocated = total."""
        processes = [Process(i, f"P{i}") for i in range(2)]
        resource_types = [ResourceType(0, "R0", 5)]
        available = [3]
        allocation = [[1], [1]]
        request = [[0], [0]]
        
        # 3 + 1 + 1 = 5 ✓
        # SystemState __post_init__ validates this automatically
        state = SystemState(processes, resource_types, available, allocation, request)
        # If we get here without exception, conservation is valid
        assert state is not None


class TestComplexCycles:
    """Complex cycle detection."""
    
    def test_overlapping_cycles(self):
        """Multiple overlapping cycles."""
        processes = [Process(i, f"P{i}") for i in range(4)]
        resource_types = [ResourceType(i, f"R{i}", 1) for i in range(4)]
        available = [0, 0, 0, 0]
        allocation = [
            [1, 0, 0, 0],  # P0 has R0
            [0, 1, 0, 0],  # P1 has R1
            [0, 0, 1, 0],  # P2 has R2
            [0, 0, 0, 1],  # P3 has R3
        ]
        request = [
            [0, 1, 0, 0],  # P0 → P1
            [0, 0, 1, 0],  # P1 → P2
            [1, 0, 0, 0],  # P2 → P0 (cycle: P0→P1→P2→P0)
            [0, 0, 1, 0],  # P3 → P2 (also involved)
        ]
        
        state = SystemState(processes, resource_types, available, allocation, request)
        result_wfg = detect_deadlock_wfg(state)
        assert result_wfg.deadlocked
        
        result_matrix = detect_deadlock_matrix(state)
        assert result_matrix.deadlocked


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
