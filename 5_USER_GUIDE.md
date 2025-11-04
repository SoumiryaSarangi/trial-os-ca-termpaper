# 🚀 User Guide - How to Use the Application

## 🎯 Quick Start (3 Easy Steps)

### Step 1: Open the Application

```bash
python app.py
```

✅ Application window opens!

### Step 2: Load a Sample

Click: **Samples** → **Single-Instance: Deadlock (Cycle)**

### Step 3: Run Detection

Click the big green **▶ Run Detection** button

**That's it!** You'll see if there's a deadlock! 🎉

---

## 📖 Complete User Guide

### 🖥️ Understanding the Interface

When you open the app, you see **3 tabs**:

```
┌────────────────────────────────────────┐
│  Input  │  Graph  │  Results          │
├────────────────────────────────────────┤
│                                        │
│         Main Content Area              │
│                                        │
└────────────────────────────────────────┘
```

#### Tab 1: Input

- Where you enter or edit data
- Has tables for processes and resources

#### Tab 2: Graph

- Visual picture of wait-for relationships
- Red = Deadlock, Blue = Safe

#### Tab 3: Results

- Shows algorithm results
- "DEADLOCK DETECTED" or "NO DEADLOCK"
- Shows recovery strategies

---

## 📊 Input Tab - Detailed Guide

### Section 1: Detection Mode

```
Detection Mode: [Single-Instance (Wait-For Graph) ▼]
```

**Two options:**

1. **Single-Instance** - Each resource has 1 copy
2. **Multi-Instance** - Resources can have multiple copies

**How to choose:**

- Use **Single-Instance** if: Each resource type has only 1 instance (like 1 printer)
- Use **Multi-Instance** if: Resource types have multiple instances (like 5 printers)

---

### Section 2: System Size

```
System Size:  Processes: [3] ↑↓  Resources: [3] ↑↓
```

**What it means:**

- **Processes** = How many programs (P0, P1, P2...)
- **Resources** = How many resource types (R0, R1, R2...)

**How to change:**

- Click ↑ to increase
- Click ↓ to decrease
- Range: 1 to 20

---

### Section 3: Resource Types Table

```
┌──────────┬──────────────────┐
│ Resource │ Total Instances  │
├──────────┼──────────────────┤
│ R0       │ 1                │
│ R1       │ 1                │
│ R2       │ 1                │
└──────────┴──────────────────┘
```

**What it means:**

- **Resource** = Name (R0, R1, etc.) - Can't change
- **Total Instances** = How many copies exist - **You can edit this!**

**Example:**

```
R0: 1  → Only 1 printer exists
R1: 5  → 5 files exist
R2: 2  → 2 memory blocks exist
```

---

### Section 4: Available Vector

```
┌────┬────┬────┐
│ R0 │ R1 │ R2 │
├────┼────┼────┤
│ 0  │ 0  │ 0  │
└────┴────┴────┘
```

**What it means:**

- How many of each resource are **FREE** right now
- Not being used by any process

**Example:**

```
R0: 0  → No free printers (all being used)
R1: 2  → 2 files are free
R2: 1  → 1 memory block is free
```

**Important:** Available + Allocated = Total Instances

---

### Section 5: Allocation Matrix

```
Allocation Matrix (Currently Allocated)
┌────┬────┬────┬────┐
│    │ R0 │ R1 │ R2 │
├────┼────┼────┼────┤
│ P0 │ 1  │ 0  │ 0  │
│ P1 │ 0  │ 1  │ 0  │
│ P2 │ 0  │ 0  │ 1  │
└────┴────┴────┴────┘
```

**What it means:**

- Shows what each process **currently has**
- Row = Process (P0, P1, P2...)
- Column = Resource (R0, R1, R2...)
- Value = How many of that resource

**Reading example:**

```
P0 row: [1, 0, 0]
→ P0 has 1 of R0, 0 of R1, 0 of R2

P1 row: [0, 1, 0]
→ P1 has 0 of R0, 1 of R1, 0 of R2
```

---

### Section 6: Request Matrix

```
Request Matrix (Currently Requested)
┌────┬────┬────┬────┐
│    │ R0 │ R1 │ R2 │
├────┼────┼────┼────┤
│ P0 │ 0  │ 1  │ 0  │
│ P1 │ 0  │ 0  │ 1  │
│ P2 │ 1  │ 0  │ 0  │
└────┴────┴────┴────┘
```

**What it means:**

- Shows what each process **wants** (but doesn't have yet)
- Same format as Allocation Matrix

**Reading example:**

```
P0 row: [0, 1, 0]
→ P0 wants 0 of R0, 1 of R1, 0 of R2
→ "P0 is requesting R1"

P2 row: [1, 0, 0]
→ P2 wants 1 of R0
→ "P2 is requesting R0"
```

---

### Section 7: Run Detection Button

```
┌──────────────────────────┐
│    ▶ Run Detection       │
└──────────────────────────┘
```

**What happens when you click:**

1. Application reads all tables
2. Validates data (checks for errors)
3. Runs the detection algorithm
4. Switches to Results tab
5. Shows if deadlock exists

---

## 🎨 Graph Tab - Visual Display

### What You See:

```
         P0 (Blue)
        /  \
       ↓    ↓
   P2 (Blue) P1 (Red)
       ↖    ↙
         P3 (Red)
```

**Color Meanings:**

- 🔵 **Blue circle** = Safe process (can finish)
- 🔴 **Red circle** = Deadlocked process (stuck)
- ⚫ **Gray arrow** = Normal dependency
- 🔴 **Red arrow** = Part of deadlock cycle

**Reading the graph:**

- Arrow from P0 to P1 = "P0 waits for P1"
- Circle means cycle/deadlock

**Example interpretation:**

```
If you see: P0 → P1 → P2 → P0 (all red)
Meaning: P0 waits for P1, P1 waits for P2, P2 waits for P0
Result: Circular wait = DEADLOCK!
```

---

## 📋 Results Tab - Understanding Output

### Section 1: Algorithm Trace

**Shows step-by-step what the algorithm did:**

```
=== Matrix-Based Deadlock Detection ===
System: 3 processes, 3 resource types

Initial State:
  Available: [0, 0, 0]

  Allocation Matrix:
    P0: [1, 0, 0]
    P1: [0, 1, 0]
    P2: [0, 0, 1]

  Request Matrix:
    P0: [0, 1, 0]
    P1: [0, 0, 1]
    P2: [1, 0, 0]

Step 1: Initialize
  Work = Available = [0, 0, 0]
  Finish = [False, False, False]

Step 2-4: Find processes that can complete
  Checking P0: Request[0] = [0, 1, 0] > Work = [0, 0, 0] ✗
  Checking P1: Request[1] = [0, 0, 1] > Work = [0, 0, 0] ✗
  Checking P2: Request[2] = [1, 0, 0] > Work = [0, 0, 0] ✗

  No process can proceed!

Step 5: Check for Deadlock
  Finish = [False, False, False]

Result: DEADLOCK DETECTED
  Deadlocked processes: {P0, P1, P2}
```

**How to read:**

- ✓ = Process can proceed
- ✗ = Process is blocked
- Numbers in [brackets] are vectors

---

### Section 2: Recovery Strategies

**Two types of suggestions:**

#### Option 1: Process Termination

```
Recovery Strategy 1: Process Termination

Terminate one of these minimal sets:
  • Kill {P0} → P1 and P2 can proceed
  • Kill {P1} → P0 and P2 can proceed
  • Kill {P2} → P0 and P1 can proceed

Impact: Terminated process loses all progress
```

**Meaning:** Kill (forcefully stop) one of these processes to break the deadlock

#### Option 2: Resource Preemption

```
Recovery Strategy 2: Resource Preemption

Preempt (temporarily take away) resources:
  • Take R1 from P1, give to P0
    → P0 finishes and releases R0
    → P2 can get R0 and finish
    → Give R1 back to P1
```

**Meaning:** Temporarily take a resource from one process and give it to another

---

### Section 3: Verdict

**Large text showing final result:**

```
╔══════════════════════════╗
║   DEADLOCK DETECTED!     ║ (Red text)
╚══════════════════════════╝

OR

╔══════════════════════════╗
║      NO DEADLOCK         ║ (Green text)
╚══════════════════════════╝
```

---

## 🎮 Using Samples

### How to Load a Sample:

1. Click **Samples** menu at top
2. Choose one:

   - **Single-Instance: Deadlock (Cycle)** ← Good starting point!
   - **Single-Instance: No Deadlock**
   - **Multi-Instance: Deadlock**
   - **Multi-Instance: No Deadlock**
   - **Empty Template**

3. Tables automatically fill with sample data
4. Click **Run Detection**

### Sample Descriptions:

#### 1. Single-Instance: Deadlock (Cycle)

```
Scenario: 3 processes, 3 resources (1 instance each)
P0 holds R0, wants R1
P1 holds R1, wants R2
P2 holds R2, wants R0
Result: DEADLOCK! (circular wait)
```

#### 2. Single-Instance: No Deadlock

```
Scenario: 3 processes, 3 resources
P0 holds R0, wants R1
P1 holds R1, wants nothing ← Can finish!
P2 holds R2, wants nothing ← Can finish!
Result: NO DEADLOCK (safe sequence exists)
```

#### 3. Multi-Instance: Deadlock

```
Scenario: 3 processes, multiple instances
All processes blocked, none can proceed
Result: DEADLOCK!
```

#### 4. Multi-Instance: No Deadlock

```
Scenario: 5 processes, enough resources
Safe sequence: P0 → P2 → P1 → P3 → P4
Result: NO DEADLOCK
```

#### 5. Empty Template

```
Blank slate for creating your own scenario
All values set to safe defaults
```

---

## ✏️ Creating Your Own Scenario

### Example: Creating a Simple 2-Process Deadlock

**Step 1:** Set system size

```
Processes: 2
Resources: 2
```

**Step 2:** Set resource instances

```
R0: 1 instance
R1: 1 instance
```

**Step 3:** Set available

```
Available: [0, 0]  (all allocated)
```

**Step 4:** Set allocation

```
P0: [1, 0]  (P0 has R0)
P1: [0, 1]  (P1 has R1)
```

**Step 5:** Set request

```
P0: [0, 1]  (P0 wants R1)
P1: [1, 0]  (P1 wants R0)
```

**Step 6:** Click Run Detection

**Result:** DEADLOCK! P0 ⟷ P1 circular wait

---

## 💾 Saving and Loading

### To Save Your Scenario:

1. Click **File** menu
2. Click **Save State**
3. Choose location and filename
4. File saved as `.json`

### To Load Saved Scenario:

1. Click **File** menu
2. Click **Load State**
3. Select your `.json` file
4. Data loads into tables

---

## ❌ Common Errors and Solutions

### Error: "Invalid Input"

**Cause:** Data validation failed

**Common reasons:**

1. **Resource conservation violated**

   ```
   Error: "Available (3) + Allocated (5) != Total (7)"
   Solution: Fix the numbers so they add up
   ```

2. **Negative numbers**

   ```
   Error: "Instance count must be non-negative"
   Solution: All numbers must be ≥ 0
   ```

3. **Empty table cells**
   ```
   Error: "Invalid value in Allocation[0][1]"
   Solution: Fill all cells with numbers
   ```

### Error: "Invalid instance count for R0"

**Cause:** Resource Types table has empty or invalid value

**Solution:**

- Click on the cell
- Enter a valid number (1 or more)

### Graph Not Showing

**Cause:** Using Multi-Instance mode

**Solution:**

- Wait-For Graph only works in Single-Instance mode
- Switch mode to "Single-Instance" to see graph

---

## 🎯 Tips for Beginners

### Tip 1: Start with Samples

- Don't create your own scenarios right away
- Load and run all 5 samples first
- Understand what makes a deadlock

### Tip 2: Keep It Simple

- Start with 2 processes, 2 resources
- Gradually increase complexity

### Tip 3: Check Resource Conservation

```
Important formula:
Available + (Sum of Allocations) = Total Instances

Example:
Available: [1, 2]
P0 has: [2, 0]
P1 has: [1, 1]
Total should be: [1+2+1, 2+0+1] = [4, 3]
```

### Tip 4: Read the Trace

- Don't just look at the verdict
- Read the step-by-step trace
- Understand WHY it's a deadlock (or not)

### Tip 5: Use the Graph

- Visual learner? Focus on Graph tab
- Look for circles = deadlock
- Blue = safe, Red = deadlocked

---

## 📱 Keyboard Shortcuts

```
Tab       → Move to next table cell
Enter     → Move to next row
Ctrl+S    → Save state (if file menu open)
Ctrl+O    → Open state (if file menu open)
```

---

## 🎓 Practice Exercises

### Exercise 1: Spot the Deadlock

Load "Single-Instance: Deadlock" and answer:

- How many processes are deadlocked?
- What's the cycle?
- How would you fix it?

### Exercise 2: Create No Deadlock

Modify the deadlock sample to create NO deadlock:

- Change ONE process's request to [0, 0, 0]
- Run detection
- Verify NO DEADLOCK

### Exercise 3: Your Own Scenario

Create a 3-process deadlock where:

- P0 waits for P1
- P1 waits for P2
- P2 waits for P0

---

## ❓ Frequently Asked Questions

**Q: How do I know which detection mode to use?**
A: If all resources have instances=1, use Single-Instance. If any have >1, use Multi-Instance.

**Q: What if I want to see the graph but use Multi-Instance?**
A: Graph only works for Single-Instance mode. It shows wait-for relationships.

**Q: Can I have 0 processes?**
A: No, minimum is 1 process.

**Q: What's the maximum number of processes/resources?**
A: 20 each (set by spinbox range).

**Q: Do I need to fill every cell?**
A: Yes, every cell in Allocation and Request matrices must have a number.

**Q: Can Available be higher than Total Instances?**
A: No, it will give an error. Available + Allocated must equal Total.

---

## 🚀 Summary

**To use the app:**

1. Load a sample OR enter your own data
2. Click Run Detection
3. Check Results tab for verdict
4. Check Graph tab for visual
5. Read recovery strategies

**Remember:**

- 🔵 Blue = Safe
- 🔴 Red = Deadlocked
- Circle/Cycle = Deadlock
- No cycle = Safe

**Have fun detecting deadlocks!** 🎉

---

## 📚 Related Documentation

- Understanding basics → `1_UNDERSTANDING_DEADLOCKS.md`
- Problem statement → `2_PROBLEM_STATEMENT.md`
- How algorithms work → `3_DETECTION_ALGORITHMS.md`
- How code works → `4_PROJECT_GUIDE.md`
