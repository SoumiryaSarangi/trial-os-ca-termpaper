"""
Main Window for Deadlock Detective

This is the main application window with tabs for Input, Graph, and Results.
Includes menu bar for loading/saving and accessing samples.
"""

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QMessageBox, QFileDialog,
    QWidget, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from models import SystemState, create_empty_system_state
from io_utils.schema import (
    load_system_state, save_system_state,
    get_sample_names, load_sample
)
from ui.input_tab import InputTab
from ui.graph_tab import GraphTab
from ui.results_tab import ResultsTab


class MainWindow(QMainWindow):
    """
    Main application window.
    
    Contains three tabs:
    - Input: Edit system state (Available, Allocation, Request matrices)
    - Graph: Visualize wait-for graph
    - Results: Show deadlock detection results and recovery suggestions
    """
    
    # Signal emitted when detection should run
    detection_requested = Signal(bool)  # bool = use_wfg
    
    def __init__(self):
        super().__init__()
        
        # Initial system state
        self.current_state = create_empty_system_state(3, 3)
        
        self.setup_ui()
        self.setup_menu()
        self.setup_connections()
        
        # Load initial state into tabs
        self.load_state_into_ui(self.current_state)
    
    def setup_ui(self):
        """Set up the main UI components."""
        self.setWindowTitle("Deadlock Detective - OS Deadlock Detection Simulator")
        self.setMinimumSize(1000, 700)
        
        # Create central widget with tab widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.input_tab = InputTab()
        self.graph_tab = GraphTab()
        self.results_tab = ResultsTab()
        
        self.tab_widget.addTab(self.input_tab, "📝 Input")
        self.tab_widget.addTab(self.graph_tab, "📊 Graph")
        self.tab_widget.addTab(self.results_tab, "📋 Results")
    
    def setup_menu(self):
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Samples menu
        samples_menu = menubar.addMenu("&Samples")
        
        for sample_name in get_sample_names():
            action = QAction(sample_name, self)
            action.triggered.connect(lambda checked=False, name=sample_name: self.load_sample(name))
            samples_menu.addAction(action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        theory_action = QAction("&Theory", self)
        theory_action.triggered.connect(self.show_theory)
        help_menu.addAction(theory_action)
    
    def setup_connections(self):
        """Set up signal/slot connections."""
        # When user clicks Run Detection in input tab
        self.input_tab.run_detection_requested.connect(self.run_detection)
        
        # When state changes in input tab
        self.input_tab.state_changed.connect(self.on_state_changed)
    
    def load_state_into_ui(self, state: SystemState):
        """Load a system state into all tabs."""
        self.current_state = state
        self.input_tab.load_state(state)
        self.graph_tab.clear()
        self.results_tab.clear()
    
    def run_detection(self, use_wfg: bool):
        """
        Run deadlock detection with current state.
        
        Args:
            use_wfg: If True, use wait-for graph; else use matrix detection
        """
        try:
            # Get current state from input tab
            state = self.input_tab.get_state()
            self.current_state = state
            
            # Update graph tab
            self.graph_tab.update_graph(state, use_wfg)
            
            # Update results tab
            self.results_tab.update_results(state, use_wfg)
            
            # Switch to results tab to show results
            self.tab_widget.setCurrentWidget(self.results_tab)
            
        except ValueError as e:
            QMessageBox.critical(self, "Invalid Input", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{str(e)}")
    
    def on_state_changed(self):
        """Called when state changes in input tab."""
        # If auto-run is enabled, we would run detection here
        pass
    
    def new_file(self):
        """Create a new empty system state."""
        reply = QMessageBox.question(
            self,
            "New File",
            "Create new empty system state? Current data will be lost.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            state = create_empty_system_state(3, 3)
            self.load_state_into_ui(state)
    
    def open_file(self):
        """Open a system state from JSON file."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open System State",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                state = load_system_state(filename)
                self.load_state_into_ui(state)
                QMessageBox.information(self, "Success", "File loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
    
    def save_file(self):
        """Save current system state to JSON file."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save System State",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                state = self.input_tab.get_state()
                save_system_state(state, filename)
                QMessageBox.information(self, "Success", "File saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
    
    def load_sample(self, sample_name: str):
        """Load a sample dataset."""
        try:
            state = load_sample(sample_name)
            self.load_state_into_ui(state)
            QMessageBox.information(
                self,
                "Sample Loaded",
                f"Loaded sample: {sample_name}\n\n"
                f"Click 'Run Detection' in the Input tab to analyze."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load sample:\n{str(e)}")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Deadlock Detective",
            "<h2>Deadlock Detective v1.0</h2>"
            "<p>A production-ready OS deadlock detection simulator.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Single-Instance Mode: Wait-for graph cycle detection</li>"
            "<li>Multi-Instance Mode: Matrix-based Work/Finish algorithm</li>"
            "<li>Recovery strategy suggestions</li>"
            "<li>Visual graph representation</li>"
            "</ul>"
            "<p><b>Author:</b> OS Arkja's</p>"
            "<p><b>Course:</b> Operating Systems (B.Tech)</p>"
        )
    
    def show_theory(self):
        """Show theory explanation dialog."""
        theory_text = """
<h3>Deadlock Detection Theory</h3>

<p><b>Single-Instance Resources (Wait-For Graph):</b></p>
<ul>
<li>Each resource type has exactly 1 instance</li>
<li>Build wait-for graph: Pi → Pj if Pi waits for resource held by Pj</li>
<li>Cycle in wait-for graph ⇒ Deadlock</li>
<li>Detection: DFS cycle detection (O(n²))</li>
</ul>

<p><b>Multi-Instance Resources (Matrix Detection):</b></p>
<ul>
<li>Resources can have multiple instances</li>
<li>Uses Available[m], Allocation[n][m], Request[n][m]</li>
<li>Algorithm: Work = Available, Finish[i] = False</li>
<li>Iteratively find Pi where Request[i] ≤ Work</li>
<li>Mark Finish[i] = True, add Allocation[i] to Work</li>
<li>Remaining unfinished processes are deadlocked</li>
</ul>

<p><b>Important Note:</b></p>
<p>A cycle in a resource allocation graph implies deadlock <b>only</b> if 
every resource type has exactly one instance. Otherwise, a cycle indicates 
<i>possible</i> deadlock, and matrix detection must be used for correctness.</p>

<p><b>Recovery Strategies:</b></p>
<ul>
<li>Process Termination: Kill minimal set of processes</li>
<li>Resource Preemption: Take resources from processes (requires rollback)</li>
</ul>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Deadlock Detection Theory")
        msg.setTextFormat(Qt.RichText)
        msg.setText(theory_text)
        msg.exec()
