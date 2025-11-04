"""
Sample Data Validation Script

Run this to verify all samples produce expected results.
"""

from io_utils.schema import SAMPLES, load_sample
from detectors.wfg import detect_deadlock_wfg
from detectors.matrix import detect_deadlock_matrix


def validate_all_samples():
    """Validate all sample datasets."""
    print("=" * 70)
    print("SAMPLE DATA VALIDATION REPORT")
    print("=" * 70)
    print()
    
    results = []
    
    for sample_name in SAMPLES.keys():
        print(f"Testing: {sample_name}")
        print("-" * 70)
        
        try:
            state = load_sample(sample_name)
            print(f"  ✓ Loaded successfully")
            print(f"  ✓ {state.n} processes, {state.m} resource types")
            
            # Run matrix detection
            result_matrix = detect_deadlock_matrix(state)
            matrix_verdict = "DEADLOCK" if result_matrix.deadlocked else "NO DEADLOCK"
            print(f"  ✓ Matrix detection: {matrix_verdict}")
            
            # Run WFG detection if single-instance
            if "Single-Instance" in sample_name:
                result_wfg = detect_deadlock_wfg(state)
                wfg_verdict = "DEADLOCK" if result_wfg.deadlocked else "NO DEADLOCK"
                print(f"  ✓ WFG detection: {wfg_verdict}")
                
                # Verify both algorithms agree
                if result_matrix.deadlocked != result_wfg.deadlocked:
                    print(f"  ⚠️  WARNING: Algorithms disagree!")
                    results.append((sample_name, "MISMATCH", False))
                else:
                    print(f"  ✓ Both algorithms agree: {matrix_verdict}")
                    results.append((sample_name, matrix_verdict, True))
            else:
                results.append((sample_name, matrix_verdict, True))
            
            # Check expected results
            if "Deadlock" in sample_name and "No Deadlock" not in sample_name:
                expected = True
                if result_matrix.deadlocked == expected:
                    print(f"  ✅ CORRECT: Deadlock detected as expected")
                else:
                    print(f"  ❌ ERROR: Expected deadlock but got safe state")
                    results[-1] = (sample_name, matrix_verdict, False)
            
            elif "No Deadlock" in sample_name or "Empty" in sample_name:
                expected = False
                if result_matrix.deadlocked == expected:
                    print(f"  ✅ CORRECT: No deadlock detected as expected")
                else:
                    print(f"  ❌ ERROR: Expected safe state but got deadlock")
                    results[-1] = (sample_name, matrix_verdict, False)
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append((sample_name, "ERROR", False))
        
        print()
    
    # Summary
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    total = len(results)
    passed = sum(1 for _, _, ok in results if ok)
    failed = total - passed
    
    for name, verdict, ok in results:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"{status} - {name}: {verdict}")
    
    print()
    print(f"Total Samples: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()
    
    if failed == 0:
        print("🎉 ALL SAMPLES VALIDATED SUCCESSFULLY!")
        print("✅ Ready for demonstration!")
    else:
        print("⚠️  Some samples failed validation")
        print("❌ Review errors above")
    
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = validate_all_samples()
    exit(0 if success else 1)
