# 🧮 Detection Algorithms - Step by Step Calculations

## 🎯 Two Detection Methods

We use TWO different algorithms:

1. **Wait-For Graph (WFG)** - For single-instance resources
2. **Matrix Detection** - For multi-instance resources

Let's learn both with simple examples!

---

## 📊 Method 1: Wait-For Graph (Simple Resources)

**Use When:** Each resource has only 1 copy (like 1 printer, 1 file)

### How It Works (5 Simple Steps):

#### Step 1: List what each process has and wants

**Example:**

```
P0 has R0, wants R1
P1 has R1, wants R2
P2 has R2, wants R0
```

#### Step 2: Draw arrows showing "who waits for whom"

**Rule:** If P0 wants R1, and P1 has R1, then P0 waits for P1

```
P0 → P1  (P0 waits for P1)
P1 → P2  (P1 waits for P2)
P2 → P0  (P2 waits for P0)
```

#### Step 3: Draw the graph

```
    P0
   ↙  ↖
  P2   P1
   ↘  ↗
```

#### Step 4: Check for cycles (circles)

**Question:** Can you start at any process and come back to it by following arrows?

**Answer:** YES!

```
Start at P0 → P1 → P2 → P0 (back to start!)
```

#### Step 5: Conclusion

**Cycle found = DEADLOCK!**

---

### 🔢 Detailed Example with Numbers

Let's work through a complete example:

**Given:**

```
3 Processes: P0, P1, P2
3 Resources: R0, R1, R2 (each has 1 instance)

Available: [0, 0, 0]

Allocation (who has what):
       R0  R1  R2
P0  [  1,  0,  0 ]  ← P0 has R0
P1  [  0,  1,  0 ]  ← P1 has R1
P2  [  0,  0,  1 ]  ← P2 has R2

Request (who wants what):
       R0  R1  R2
P0  [  0,  1,  0 ]  ← P0 wants R1
P1  [  0,  0,  1 ]  ← P1 wants R2
P2  [  1,  0,  0 ]  ← P2 wants R0
```

**Step-by-Step Detection:**

1. **Build wait-for relationships:**

   ```
   P0 wants R1, R1 is held by P1
   → P0 waits for P1

   P1 wants R2, R2 is held by P2
   → P1 waits for P2

   P2 wants R0, R0 is held by P0
   → P2 waits for P0
   ```

2. **Check for cycles using DFS (Depth-First Search):**

   ```
   Start at P0:
   P0 → P1 (mark P1 as visiting)
   P1 → P2 (mark P2 as visiting)
   P2 → P0 (P0 already visiting!)

   CYCLE DETECTED: P0 → P1 → P2 → P0
   ```

3. **Result:**
   ```
   DEADLOCK DETECTED
   Processes in deadlock: {P0, P1, P2}
   Cycle: P0 → P1 → P2 → P0
   ```

---

## 🧮 Method 2: Matrix Detection (Multiple Copies)

**Use When:** Resources can have multiple copies (like 5 printers, 3 files)

This is called the **Banker's Algorithm** or **Work-Finish Algorithm**

### How It Works (Simple Explanation):

**Main Idea:** Try to find processes that can finish, let them finish and release resources, repeat until all finish OR some are stuck.

### The Algorithm (Step by Step):

#### Step 1: Initialize

```
Work = Available  (resources we have free)
Finish = [False, False, False, ...]  (nobody finished yet)
```

#### Step 2: Find a process that can finish

**Question:** Can this process get what it wants with what's available?

**Check:** Request[i] ≤ Work?

**Meaning:** Does this process want less than or equal to what we have?

#### Step 3: Let that process finish

```
Mark Finish[i] = True
Add its resources back: Work = Work + Allocation[i]
```

#### Step 4: Repeat Step 2-3

Keep finding processes that can finish until:

- All finished (NO DEADLOCK)
- OR Some can't finish (DEADLOCK)

---

### 🔢 Detailed Example with Math

**Given:**

```
3 Processes: P0, P1, P2
3 Resources: R0, R1, R2
R0 has 2 instances
R1 has 2 instances
R2 has 2 instances

Available: [0, 0, 0]

Allocation (what each has):
       R0  R1  R2
P0  [  1,  0,  1 ]
P1  [  1,  1,  0 ]
P2  [  0,  1,  1 ]

Request (what each wants):
       R0  R1  R2
P0  [  1,  1,  0 ]
P1  [  0,  1,  1 ]
P2  [  1,  0,  1 ]
```

**Step-by-Step Calculation:**

#### Iteration 1:

```
Work = [0, 0, 0]
Finish = [False, False, False]

Check P0: Does P0's request [1, 1, 0] ≤ Work [0, 0, 0]?
  Request[0] = 1, Work[0] = 0 → 1 > 0 ✗ NO

Check P1: Does P1's request [0, 1, 1] ≤ Work [0, 0, 0]?
  Request[0] = 0, Work[0] = 0 → 0 ≤ 0 ✓
  Request[1] = 1, Work[1] = 0 → 1 > 0 ✗ NO

Check P2: Does P2's request [1, 0, 1] ≤ Work [0, 0, 0]?
  Request[0] = 1, Work[0] = 0 → 1 > 0 ✗ NO

No process can proceed!
```

#### Final Check:

```
Finish = [False, False, False]
All are False → ALL PROCESSES DEADLOCKED!

Result: DEADLOCK DETECTED
Deadlocked processes: {P0, P1, P2}
```

---

### 🟢 Example with NO Deadlock

**Given:**

```
3 Processes
3 Resources

Available: [3, 3, 2]

Allocation:
       R0  R1  R2
P0  [  0,  1,  0 ]
P1  [  2,  0,  0 ]
P2  [  3,  0,  2 ]

Request:
       R0  R1  R2
P0  [  0,  0,  0 ]  ← P0 wants nothing!
P1  [  1,  0,  2 ]
P2  [  0,  0,  0 ]  ← P2 wants nothing!
```

**Calculation:**

#### Iteration 1:

```
Work = [3, 3, 2]

Check P0: Request [0, 0, 0] ≤ Work [3, 3, 2]?
  All zeros ≤ anything → YES! ✓

P0 can finish!
Finish[0] = True
P0 releases: Work = [3, 3, 2] + [0, 1, 0] = [3, 4, 2]
```

#### Iteration 2:

```
Work = [3, 4, 2]

Check P2: Request [0, 0, 0] ≤ Work [3, 4, 2]?
  All zeros → YES! ✓

P2 can finish!
Finish[2] = True
P2 releases: Work = [3, 4, 2] + [3, 0, 2] = [6, 4, 4]
```

#### Iteration 3:

```
Work = [6, 4, 4]

Check P1: Request [1, 0, 2] ≤ Work [6, 4, 4]?
  1 ≤ 6 ✓
  0 ≤ 4 ✓
  2 ≤ 4 ✓
  YES! ✓

P1 can finish!
Finish[1] = True
```

#### Final:

```
Finish = [True, True, True]
All True → NO DEADLOCK!

Safe sequence: P0 → P2 → P1
```

---

## 📐 Vector Comparison (Math Part)

**Question:** How do we check if Request ≤ Work?

**Rule:** Compare each element

```
Example:
Request = [1, 2, 0]
Work    = [2, 3, 1]

Compare:
Position 0: 1 ≤ 2? YES ✓
Position 1: 2 ≤ 3? YES ✓
Position 2: 0 ≤ 1? YES ✓

All YES → Request ≤ Work!
```

**Another Example:**

```
Request = [2, 1, 3]
Work    = [1, 2, 4]

Compare:
Position 0: 2 ≤ 1? NO ✗

At least one NO → Request > Work!
```

---

## 🧮 Simple Math Examples

### Addition of Vectors:

```
Work = [3, 2, 1]
Allocation = [1, 0, 2]

Work + Allocation:
[3, 2, 1] + [1, 0, 2] = [3+1, 2+0, 1+2] = [4, 2, 3]
```

### Subtraction:

```
Total = [5, 3, 4]
Allocated = [2, 1, 1]

Available = Total - Allocated:
[5, 3, 4] - [2, 1, 1] = [5-2, 3-1, 4-1] = [3, 2, 3]
```

---

## 🎯 Quick Reference: When to Use Which Algorithm?

| Scenario                       | Algorithm        | Why                   |
| ------------------------------ | ---------------- | --------------------- |
| All resources have 1 copy      | Wait-For Graph   | Simpler, faster       |
| Resources have multiple copies | Matrix Detection | Handles quantities    |
| Want visual cycle              | Wait-For Graph   | Shows arrows/graph    |
| Want safe sequence             | Matrix Detection | Shows execution order |

---

## 📊 Summary Table

| Algorithm            | Input                          | Output               | Complexity |
| -------------------- | ------------------------------ | -------------------- | ---------- |
| **Wait-For Graph**   | Allocation, Request            | Cycles found         | O(n²)      |
| **Matrix Detection** | Available, Allocation, Request | Deadlocked processes | O(m×n²)    |

Where:

- n = number of processes
- m = number of resource types

---

## 💡 Practice Problems

### Problem 1: Is there a deadlock?

```
2 Processes
Available: [0, 0]
Allocation: P0=[1,0], P1=[0,1]
Request: P0=[0,1], P1=[1,0]
```

**Answer:** YES! P0→P1, P1→P0 (cycle)

---

### Problem 2: Is there a deadlock?

```
2 Processes
Available: [1, 0]
Allocation: P0=[1,0], P1=[0,1]
Request: P0=[0,0], P1=[0,0]
```

**Answer:** NO! Both processes want nothing, can finish immediately.

---

### Problem 3: Is there a deadlock?

```
3 Processes
Available: [1, 0, 0]
Allocation: P0=[1,0,0], P1=[0,1,0], P2=[0,0,1]
Request: P0=[0,0,0], P1=[0,0,1], P2=[1,0,0]
```

**Answer:** Let's trace:

- P0 wants nothing → P0 finishes, releases [1,0,0]
- Work = [1,0,0] + [1,0,0] = [2,0,0]
- P2 wants [1,0,0] ≤ [2,0,0] → P2 finishes, releases [0,0,1]
- Work = [2,0,0] + [0,0,1] = [2,0,1]
- P1 wants [0,0,1] ≤ [2,0,1] → P1 finishes
- **NO DEADLOCK!** Safe sequence: P0→P2→P1

---

## 🚀 Next Steps

Now you understand the math! Let's see:

1. **How This is Coded** → See `4_PROJECT_GUIDE.md`
2. **How to Use the Application** → See `5_USER_GUIDE.md`

---

**Key Takeaway:**

- **Wait-For Graph:** Find cycles in who-waits-for-whom
- **Matrix Detection:** See if all processes can finish one by one

Both are just different ways to answer: "Is anyone stuck?" 🔍
