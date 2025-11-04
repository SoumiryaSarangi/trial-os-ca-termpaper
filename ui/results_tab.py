"""
Results Tab - Detection Results and Recovery Suggestions

This tab displays:
- Deadlock detection results
- Detailed trace of the detection algorithm
- Recovery strategy suggestions
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLabel, QSplitter
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor

from models import SystemState
from detectors.wfg import detect_deadlock_wfg
from detectors.matrix import detect_deadlock_matrix
from strategies.recovery import suggest_recovery_strategies, format_recovery_report


class ResultsTab(QWidget):
    """
    Results display tab.
    
    Shows:
    - Detection algorithm trace
    - Deadlocked processes
    - Recovery strategy suggestions
    """
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Detection Results and Recovery Strategies")
        header_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Splitter for trace and recovery
        splitter = QSplitter(Qt.Vertical)
        
        # Detection trace
        trace_label = QLabel("Detection Algorithm Trace:")
        trace_label.setFont(QFont("Arial", 10, QFont.Bold))
        
        self.trace_text = QTextEdit()
        self.trace_text.setReadOnly(True)
        self.trace_text.setFont(QFont("Consolas", 9))
        
        trace_widget = QWidget()
        trace_layout = QVBoxLayout(trace_widget)
        trace_layout.addWidget(trace_label)
        trace_layout.addWidget(self.trace_text)
        trace_layout.setContentsMargins(0, 0, 0, 0)
        
        splitter.addWidget(trace_widget)
        
        # Recovery suggestions
        recovery_label = QLabel("Recovery Strategies:")
        recovery_label.setFont(QFont("Arial", 10, QFont.Bold))
        
        self.recovery_text = QTextEdit()
        self.recovery_text.setReadOnly(True)
        self.recovery_text.setFont(QFont("Consolas", 9))
        
        recovery_widget = QWidget()
        recovery_layout = QVBoxLayout(recovery_widget)
        recovery_layout.addWidget(recovery_label)
        recovery_layout.addWidget(self.recovery_text)
        recovery_layout.setContentsMargins(0, 0, 0, 0)
        
        splitter.addWidget(recovery_widget)
        
        # Set initial sizes (60% trace, 40% recovery)
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)
        
        layout.addWidget(splitter)
    
    def clear(self):
        """Clear the results display."""
        self.trace_text.clear()
        self.recovery_text.clear()
        self.trace_text.setPlainText("Run detection to see results.")
        self.recovery_text.setPlainText("Recovery strategies will appear here if deadlock is detected.")
    
    def update_results(self, state: SystemState, use_wfg: bool):
        """
        Update the results display.
        
        Args:
            state: Current system state
            use_wfg: If True, use wait-for graph; else use matrix detection
        """
        # Run detection
        if use_wfg:
            result = detect_deadlock_wfg(state)
            trace = result.trace
            deadlocked = result.deadlocked
        else:
            result = detect_deadlock_matrix(state)
            trace = result.trace
            deadlocked = result.deadlocked
        
        # Display trace
        trace_text = "\n".join(trace)
        self.trace_text.setPlainText(trace_text)
        
        # Highlight result
        if deadlocked:
            self.highlight_deadlock_in_trace()
        
        # Display recovery strategies
        if deadlocked:
            suggestions = suggest_recovery_strategies(state, use_wfg)
            recovery_text = format_recovery_report(suggestions)
            self.recovery_text.setPlainText(recovery_text)
        else:
            self.recovery_text.setPlainText(
                "=" * 60 + "\n"
                "NO DEADLOCK DETECTED\n"
                "=" * 60 + "\n\n"
                "The system is in a safe state.\n"
                "All processes can complete without deadlock.\n\n"
                "No recovery strategies are needed."
            )
    
    def highlight_deadlock_in_trace(self):
        """Highlight the deadlock result in the trace text."""
        # This is a simple approach - find "DEADLOCK DETECTED" and color it red
        cursor = self.trace_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        # Find and highlight "DEADLOCK DETECTED"
        text = self.trace_text.toPlainText()
        if "DEADLOCK DETECTED" in text:
            index = text.index("DEADLOCK DETECTED")
            cursor.setPosition(index)
            cursor.setPosition(index + len("DEADLOCK DETECTED"), QTextCursor.MoveMode.KeepAnchor)
            
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(255, 0, 0))
            fmt.setFontWeight(QFont.Bold)
            cursor.setCharFormat(fmt)
