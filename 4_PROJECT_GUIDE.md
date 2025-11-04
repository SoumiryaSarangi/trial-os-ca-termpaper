# 🖥️ Project Guide - Understanding the Code

## 📁 Project Structure (What Each File Does)

```
Deadlock Detective/
│
├── 📄 app.py                    → Main file - Run this to start!
├── 📄 models.py                 → Data structures (Process, Resource, State)
├── 📄 requirements.txt          → List of packages needed
│
├── 📁 detectors/               → Detection algorithms folder
│   ├── wfg.py                  → Wait-For Graph detection
│   └── matrix.py               → Matrix detection (Banker's algorithm)
│
├── 📁 io_utils/                → Input/Output folder
│   └── schema.py               → Load/save data, sample datasets
│
├── 📁 strategies/              → Recovery solutions folder
│   └── recovery.py             → Generate fix suggestions
│
├── 📁 ui/                      → User Interface folder
│   ├── main_window.py          → Main app window
│   ├── input_tab.py            → Tab for entering data
│   ├── graph_tab.py            → Tab for viewing graph
│   └── results_tab.py          → Tab for viewing results
│
├── 📁 tests/                   → Testing folder
│   ├── test_wfg.py             → Tests for WFG algorithm
│   ├── test_matrix.py          → Tests for Matrix algorithm
│   ├── test_schema.py          → Tests for data loading
│   └── test_edge_cases.py      → Tests for special cases
│
└── 📁 Documentation/
    ├── 1_UNDERSTANDING_DEADLOCKS.md
    ├── 2_PROBLEM_STATEMENT.md
    ├── 3_DETECTION_ALGORITHMS.md
    ├── 4_PROJECT_GUIDE.md (this file)
    └── 5_USER_GUIDE.md
```

---

## 🎯 How the Project Works (Big Picture)

```
┌─────────────┐
│    USER     │
│  (You!)     │
└──────┬──────┘
       │ Enters data about processes and resources
       ↓
┌─────────────────────────────────┐
│   INPUT TAB (ui/input_tab.py)  │
│   • Edit tables                 │
│   • Load samples                │
└─────────┬───────────────────────┘
          │ Sends data to...
          ↓
┌──────────────────────────────────┐
│  DETECTION ALGORITHMS            │
│  • detectors/wfg.py              │
│  • detectors/matrix.py           │
│  (Does the math calculations!)   │
└─────────┬────────────────────────┘
          │ Returns results...
          ↓
┌──────────────────────────────────┐
│  RESULTS TAB (ui/results_tab.py)│
│  • Shows: Deadlock? YES/NO       │
│  • Shows: Step-by-step trace     │
│  • Shows: Recovery strategies    │
└──────────────────────────────────┘
          │ Also creates...
          ↓
┌──────────────────────────────────┐
│  GRAPH TAB (ui/graph_tab.py)    │
│  • Draws visual graph            │
│  • Red = Deadlocked              │
│  • Blue = Safe                   │
└──────────────────────────────────┘
```

---

## 📄 File Explanations (For Beginners)

### 1. **app.py** - The Starting Point

**What it does:** Starts the application

**Simple explanation:**

```python
# This file is like the "ON" button
# It creates the main window and shows it to you
```

**Key code:**

```python
if __name__ == "__main__":
    app = QApplication([])           # Create the application
    window = MainWindow()            # Create main window
    window.show()                    # Show it on screen
    app.exec()                       # Keep it running
```

**When to look at it:** When you want to understand how the app starts

---

### 2. **models.py** - Data Structures

**What it does:** Defines how we store information about processes and resources

**Think of it as:** The blueprint/template for our data

**Three main classes:**

#### Class 1: Process

```python
class Process:
    pid: int        # Process ID (like 0, 1, 2)
    name: str       # Process name (like "P0", "P1")
```

**Example:**

```python
p0 = Process(0, "P0")  # Create process 0 named "P0"
```

#### Class 2: ResourceType

```python
class ResourceType:
    rid: int          # Resource ID
    name: str         # Resource name
    instances: int    # How many copies exist
```

**Example:**

```python
r0 = ResourceType(0, "R0", 5)  # R0 with 5 instances
```

#### Class 3: SystemState

```python
class SystemState:
    processes: List[Process]          # All processes
    resource_types: List[ResourceType]  # All resources
    available: List[int]              # Free resources
    allocation: List[List[int]]       # Who has what
    request: List[List[int]]          # Who wants what
```

**This is the MAIN data structure** - holds everything!

---

### 3. **detectors/wfg.py** - Wait-For Graph Algorithm

**What it does:** Checks for deadlock using cycle detection

**Main function:**

```python
def detect_deadlock_wfg(state: SystemState) -> WFGDetectionResult
```

**How it works (simplified code flow):**

```python
Step 1: Build the graph
    for each process:
        if process wants a resource:
            find who has that resource
            add edge: this_process → holder

Step 2: Find cycles using DFS
    for each process:
        start_path = []
        follow edges and mark visited
        if we visit a node already in path:
            CYCLE FOUND!

Step 3: Return result
    return WFGDetectionResult(
        deadlocked = cycles found,
        cycles = list of cycles,
        trace = explanation
    )
```

**Example output:**

```
WFGDetectionResult:
  deadlocked = True
  cycles = [[0, 1, 2, 0]]  # P0→P1→P2→P0
  trace = ["Building graph...", "Checking P0...", ...]
```

---

### 4. **detectors/matrix.py** - Matrix Detection Algorithm

**What it does:** Uses Work-Finish algorithm for multi-instance resources

**Main function:**

```python
def detect_deadlock_matrix(state: SystemState) -> MatrixDetectionResult
```

**How it works (simplified code flow):**

```python
Step 1: Initialize
    work = available[:]           # Copy available resources
    finish = [False] * n          # Nobody finished yet

Step 2: Find processes that can finish
    while True:
        found_any = False
        for each process i:
            if not finish[i]:
                if request[i] <= work:  # Can this process proceed?
                    finish[i] = True
                    work = work + allocation[i]  # Release resources
                    found_any = True

        if not found_any:
            break  # No more can finish

Step 3: Check results
    if all finish[i] == True:
        NO DEADLOCK!
    else:
        DEADLOCK! (processes with finish[i] == False are deadlocked)
```

**Key helper functions:**

```python
def vector_less_equal(a, b):
    """Check if a <= b for vectors"""
    return all(a[i] <= b[i] for all i)

def vector_add(a, b):
    """Add two vectors"""
    return [a[i] + b[i] for all i]
```

---

### 5. **io_utils/schema.py** - Data Loading

**What it does:** Provides sample datasets and save/load functions

**Why it's useful:** You don't have to type data manually!

**Sample datasets included:**

```python
1. Single-Instance: Deadlock (Cycle)
   → 3 processes in circular wait

2. Single-Instance: No Deadlock
   → Some processes can finish

3. Multi-Instance: Deadlock
   → All processes blocked

4. Multi-Instance: No Deadlock
   → Safe sequence exists

5. Empty Template
   → Blank slate for your own data
```

**How samples work:**

```python
def get_sample_single_instance_deadlock():
    processes = [Process(0, "P0"), Process(1, "P1"), Process(2, "P2")]
    resource_types = [ResourceType(0, "R0", 1), ...]
    # ... set up allocation and request ...
    return SystemState(...)
```

---

### 6. **strategies/recovery.py** - Recovery Suggestions

**What it does:** Suggests ways to fix deadlock

**Two strategies:**

#### Strategy 1: Process Termination

```python
def find_minimal_termination_set(state):
    """Find smallest set of processes to kill"""
    # Try killing 1 process, then 2, then 3...
    # Return the smallest set that breaks deadlock
```

**Example output:**

```
Option 1: Kill {P0}
Option 2: Kill {P1}
Option 3: Kill {P0, P2}
```

#### Strategy 2: Resource Preemption

```python
def suggest_preemption_targets(state):
    """Suggest which resources to take from which processes"""
    # Find resources that would help most if released
```

**Example output:**

```
Preempt R1 from P2 → Give to P0
P0 can finish, releases all resources
Then P2 can get R1 back
```

---

### 7. **ui/main_window.py** - Main Application Window

**What it does:** Creates the main app window with menu and tabs

**Structure:**

```python
class MainWindow:
    def __init__():
        # Create 3 tabs:
        self.input_tab = InputTab()
        self.graph_tab = GraphTab()
        self.results_tab = ResultsTab()

        # Create menu:
        File menu → Save, Load, Exit
        Samples menu → Load sample datasets
        Help menu → About, Theory
```

**Key method:**

```python
def run_detection(self, use_wfg: bool):
    """Run detection when user clicks button"""
    # Get data from input tab
    state = self.input_tab.get_state()

    # Run algorithm
    if use_wfg:
        result = detect_deadlock_wfg(state)
    else:
        result = detect_deadlock_matrix(state)

    # Show results
    self.results_tab.update_results(result)
    self.graph_tab.draw_graph(state, result)
```

---

### 8. **ui/input_tab.py** - Input Interface

**What it does:** Tables where you enter data

**Components:**

```python
1. Mode selector
   → Single-Instance or Multi-Instance

2. System size controls
   → Spinboxes: Number of processes (1-20)
   → Spinboxes: Number of resources (1-20)

3. Resource Types table
   → Columns: Resource name, Total instances

4. Available vector table
   → How many of each resource are free

5. Allocation matrix table
   → Rows: Processes
   → Columns: Resources
   → Values: How many each process has

6. Request matrix table
   → Rows: Processes
   → Columns: Resources
   → Values: How many each process wants

7. Run Detection button
   → Triggers the algorithm
```

**Key method:**

```python
def get_state(self) -> SystemState:
    """Read all tables and create SystemState"""
    # Read resource types table
    # Read available table
    # Read allocation matrix
    # Read request matrix
    # Validate and return SystemState
```

---

### 9. **ui/graph_tab.py** - Visual Graph Display

**What it does:** Draws a picture of the wait-for graph

**How it draws:**

```python
Step 1: Position processes in a circle
    angle = (2 * π * i) / n  # Evenly spaced
    x = center_x + radius * cos(angle)
    y = center_y + radius * sin(angle)

Step 2: Draw process nodes
    if process is deadlocked:
        color = RED
    else:
        color = BLUE
    draw_circle(x, y, radius, color)

Step 3: Draw arrows (edges)
    for each wait-for relationship:
        if edge is in cycle:
            color = RED
        else:
            color = GRAY
        draw_arrow(from_process, to_process, color)
```

---

### 10. **ui/results_tab.py** - Results Display

**What it does:** Shows detection results and recovery strategies

**Three sections:**

```python
Section 1: Algorithm Trace
    → Scrollable text showing step-by-step
    → Example:
      "Step 1: Initialize Work = [0, 0, 0]"
      "Step 2: Checking P0..."
      "DEADLOCK DETECTED"

Section 2: Recovery Strategies
    → Process termination options
    → Resource preemption suggestions

Section 3: Verdict
    → Big text: "DEADLOCK DETECTED" (red)
    → Or "NO DEADLOCK" (green)
```

---

## 🧪 Testing Files

### tests/test_wfg.py

- Tests Wait-For Graph detection
- 5 test cases covering cycles, no cycles, etc.

### tests/test_matrix.py

- Tests Matrix detection
- 6 test cases covering various scenarios

### tests/test_schema.py

- Tests data loading/saving
- 8 test cases for sample datasets

### tests/test_edge_cases.py

- Tests special situations
- 14 test cases for edge conditions

---

## 🔄 Complete Flow Example

Let's trace what happens when you use the app:

```
1. User starts app
   → app.py runs
   → Creates MainWindow
   → Shows 3 tabs

2. User loads "Single-Instance: Deadlock" sample
   → Samples menu clicked
   → io_utils/schema.py loads sample data
   → input_tab.py fills tables with data

3. User clicks "Run Detection"
   → input_tab.py reads all tables
   → Creates SystemState object (models.py)
   → Checks mode: Single-Instance
   → Calls detectors/wfg.py

4. WFG algorithm runs
   → Builds wait-for graph
   → Finds cycles using DFS
   → Returns WFGDetectionResult

5. Results displayed
   → results_tab.py shows trace
   → graph_tab.py draws visual graph
   → Red nodes = deadlocked
   → Red arrows = cycle edges

6. Recovery strategies generated
   → strategies/recovery.py runs
   → Suggests process termination
   → Suggests resource preemption
   → results_tab.py displays options
```

---

## 💻 Key Python Concepts Used

### 1. **Classes and Objects**

```python
class Process:
    def __init__(self, pid, name):
        self.pid = pid
        self.name = name

p = Process(0, "P0")  # Create object
print(p.name)  # Access property
```

### 2. **Lists (Arrays)**

```python
allocation = [
    [1, 0, 0],  # P0's resources
    [0, 1, 0],  # P1's resources
    [0, 0, 1],  # P2's resources
]

# Access: allocation[row][column]
print(allocation[0][0])  # → 1
```

### 3. **Loops**

```python
for i in range(n):  # Loop through processes
    if request[i] <= work:
        # Process i can proceed
```

### 4. **Functions**

```python
def detect_deadlock(state):
    # ... algorithm ...
    return result

result = detect_deadlock(my_state)
```

### 5. **GUI (PySide6)**

```python
button = QPushButton("Click me")
button.clicked.connect(my_function)  # When clicked, run my_function
```

---

## 🎓 For Programming Beginners

**Don't worry if you don't understand every line!**

**Key things to know:**

1. **app.py** starts everything
2. **detectors/** does the math (algorithms)
3. **ui/** creates the visual interface
4. **models.py** defines data structure
5. **Tests** verify everything works

**To modify the project:**

- Change UI? → Edit files in `ui/`
- Add new algorithm? → Create new file in `detectors/`
- Add new sample? → Edit `io_utils/schema.py`
- Fix a bug? → Check relevant file based on where error occurs

---

## 🚀 Next Steps

Now you understand the code structure! Learn how to use it:
→ See `5_USER_GUIDE.md`

---

**Remember:** You don't need to understand every single line of code. Understanding the BIG PICTURE (how files work together) is more important! 🎯
