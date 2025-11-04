"""
Input Tab - System State Editor

This tab allows users to edit the system state:
- Choose detection mode (Single-Instance vs Multi-Instance)
- Edit Available vector
- Edit Allocation and Request matrices
- Adjust number of processes and resources
- Run detection
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QComboBox, QSpinBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from models import SystemState, Process, ResourceType


class InputTab(QWidget):
    """
    Input tab for editing system state.
    
    Signals:
        run_detection_requested: Emitted when user clicks Run Detection (bool = use_wfg)
        state_changed: Emitted when any value in the state changes
    """
    
    run_detection_requested = Signal(bool)
    state_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.current_state = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Header with mode selection
        header_layout = QHBoxLayout()
        
        mode_label = QLabel("Detection Mode:")
        mode_label.setFont(QFont("Arial", 10, QFont.Bold))
        header_layout.addWidget(mode_label)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Single-Instance (Wait-For Graph)")
        self.mode_combo.addItem("Multi-Instance (Matrix Detection)")
        self.mode_combo.setMinimumWidth(300)
        header_layout.addWidget(self.mode_combo)
        
        header_layout.addStretch()
        
        # System size controls
        size_label = QLabel("System Size:")
        size_label.setFont(QFont("Arial", 10, QFont.Bold))
        header_layout.addWidget(size_label)
        
        header_layout.addWidget(QLabel("Processes:"))
        self.num_processes_spin = QSpinBox()
        self.num_processes_spin.setRange(1, 20)
        self.num_processes_spin.setValue(3)
        self.num_processes_spin.valueChanged.connect(self.resize_tables)
        header_layout.addWidget(self.num_processes_spin)
        
        header_layout.addWidget(QLabel("Resources:"))
        self.num_resources_spin = QSpinBox()
        self.num_resources_spin.setRange(1, 20)
        self.num_resources_spin.setValue(3)
        self.num_resources_spin.valueChanged.connect(self.resize_tables)
        header_layout.addWidget(self.num_resources_spin)
        
        layout.addLayout(header_layout)
        
        # Resource Types group
        resource_group = QGroupBox("Resource Types (Total Instances)")
        resource_layout = QVBoxLayout(resource_group)
        
        self.resource_table = QTableWidget()
        self.resource_table.setColumnCount(2)
        self.resource_table.setHorizontalHeaderLabels(["Resource", "Total Instances"])
        self.resource_table.horizontalHeader().setStretchLastSection(True)
        self.resource_table.setMaximumHeight(150)
        resource_layout.addWidget(self.resource_table)
        
        layout.addWidget(resource_group)
        
        # Available vector group
        available_group = QGroupBox("Available Vector (Current Available Instances)")
        available_layout = QVBoxLayout(available_group)
        
        self.available_table = QTableWidget()
        self.available_table.setRowCount(1)
        self.available_table.setVerticalHeaderLabels(["Available"])
        self.available_table.setMaximumHeight(80)
        available_layout.addWidget(self.available_table)
        
        layout.addWidget(available_group)
        
        # Matrices group
        matrices_layout = QHBoxLayout()
        
        # Allocation matrix
        allocation_group = QGroupBox("Allocation Matrix (Currently Allocated)")
        allocation_layout = QVBoxLayout(allocation_group)
        
        self.allocation_table = QTableWidget()
        allocation_layout.addWidget(self.allocation_table)
        
        matrices_layout.addWidget(allocation_group)
        
        # Request matrix
        request_group = QGroupBox("Request Matrix (Currently Requested)")
        request_layout = QVBoxLayout(request_group)
        
        self.request_table = QTableWidget()
        request_layout.addWidget(self.request_table)
        
        matrices_layout.addWidget(request_group)
        
        layout.addLayout(matrices_layout)
        
        # Run button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.run_button = QPushButton("▶ Run Detection")
        self.run_button.setMinimumSize(150, 40)
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.run_button.clicked.connect(self.on_run_detection)
        button_layout.addWidget(self.run_button)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Initialize tables with default values
        self.resize_tables()
    
    def resize_tables(self):
        """Resize tables when number of processes/resources changes."""
        n = self.num_processes_spin.value()
        m = self.num_resources_spin.value()
        
        # Resource types table
        self.resource_table.setRowCount(m)
        for i in range(m):
            name_item = QTableWidgetItem(f"R{i}")
            name_item.setFlags(Qt.ItemIsEnabled)
            self.resource_table.setItem(i, 0, name_item)
            
            if not self.resource_table.item(i, 1):
                self.resource_table.setItem(i, 1, QTableWidgetItem("1"))
        
        # Available table
        self.available_table.setColumnCount(m)
        self.available_table.setHorizontalHeaderLabels([f"R{i}" for i in range(m)])
        for j in range(m):
            if not self.available_table.item(0, j):
                self.available_table.setItem(0, j, QTableWidgetItem("0"))
        
        # Allocation table
        self.allocation_table.setRowCount(n)
        self.allocation_table.setColumnCount(m)
        self.allocation_table.setVerticalHeaderLabels([f"P{i}" for i in range(n)])
        self.allocation_table.setHorizontalHeaderLabels([f"R{i}" for i in range(m)])
        for i in range(n):
            for j in range(m):
                if not self.allocation_table.item(i, j):
                    self.allocation_table.setItem(i, j, QTableWidgetItem("0"))
        
        # Request table
        self.request_table.setRowCount(n)
        self.request_table.setColumnCount(m)
        self.request_table.setVerticalHeaderLabels([f"P{i}" for i in range(n)])
        self.request_table.setHorizontalHeaderLabels([f"R{i}" for i in range(m)])
        for i in range(n):
            for j in range(m):
                if not self.request_table.item(i, j):
                    self.request_table.setItem(i, j, QTableWidgetItem("0"))
    
    def load_state(self, state: SystemState):
        """Load a system state into the tables."""
        self.current_state = state
        
        # Set dimensions (this triggers resize_tables)
        self.num_processes_spin.setValue(state.n)
        self.num_resources_spin.setValue(state.m)
        
        # Set mode based on resource instances
        if state.is_single_instance():
            self.mode_combo.setCurrentIndex(0)
        else:
            self.mode_combo.setCurrentIndex(1)
        
        # Load resource types
        for i, rt in enumerate(state.resource_types):
            item = self.resource_table.item(i, 1)
            if item is None:
                item = QTableWidgetItem(str(rt.instances))
                self.resource_table.setItem(i, 1, item)
            else:
                item.setText(str(rt.instances))
        
        # Load available
        for j in range(state.m):
            item = self.available_table.item(0, j)
            if item is None:
                item = QTableWidgetItem(str(state.available[j]))
                self.available_table.setItem(0, j, item)
            else:
                item.setText(str(state.available[j]))
        
        # Load allocation
        for i in range(state.n):
            for j in range(state.m):
                item = self.allocation_table.item(i, j)
                if item is None:
                    item = QTableWidgetItem(str(state.allocation[i][j]))
                    self.allocation_table.setItem(i, j, item)
                else:
                    item.setText(str(state.allocation[i][j]))
        
        # Load request
        for i in range(state.n):
            for j in range(state.m):
                item = self.request_table.item(i, j)
                if item is None:
                    item = QTableWidgetItem(str(state.request[i][j]))
                    self.request_table.setItem(i, j, item)
                else:
                    item.setText(str(state.request[i][j]))
    
    def get_state(self) -> SystemState:
        """
        Get current system state from the tables.
        
        Returns:
            SystemState object
        
        Raises:
            ValueError: If inputs are invalid
        """
        n = self.num_processes_spin.value()
        m = self.num_resources_spin.value()
        
        # Parse resource types
        resource_types = []
        for i in range(m):
            try:
                instances = int(self.resource_table.item(i, 1).text())
                resource_types.append(ResourceType(i, f"R{i}", instances))
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid instance count for R{i}")
        
        # Parse available
        available = []
        for j in range(m):
            try:
                val = int(self.available_table.item(0, j).text())
                available.append(val)
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid value in Available[{j}]")
        
        # Parse allocation
        allocation = []
        for i in range(n):
            row = []
            for j in range(m):
                try:
                    val = int(self.allocation_table.item(i, j).text())
                    row.append(val)
                except (ValueError, AttributeError):
                    raise ValueError(f"Invalid value in Allocation[{i}][{j}]")
            allocation.append(row)
        
        # Parse request
        request = []
        for i in range(n):
            row = []
            for j in range(m):
                try:
                    val = int(self.request_table.item(i, j).text())
                    row.append(val)
                except (ValueError, AttributeError):
                    raise ValueError(f"Invalid value in Request[{i}][{j}]")
            request.append(row)
        
        # Create processes
        processes = [Process(i, f"P{i}") for i in range(n)]
        
        # Create and validate system state
        return SystemState(processes, resource_types, available, allocation, request)
    
    def on_run_detection(self):
        """Handle Run Detection button click."""
        try:
            # Validate current state
            state = self.get_state()
            
            # Determine which mode to use
            use_wfg = self.mode_combo.currentIndex() == 0
            
            # Emit signal
            self.run_detection_requested.emit(use_wfg)
            
        except ValueError as e:
            QMessageBox.critical(self, "Invalid Input", str(e))
