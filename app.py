#!/usr/bin/env python3
"""
Deadlock Detective - Main Entry Point
A production-ready PySide6 application for detecting deadlocks in simulated OS processes.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow


def main():
    """Launch the Deadlock Detective application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Deadlock Detective")
    app.setOrganizationName("OS Arkja's")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
