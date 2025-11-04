"""
Graph Tab - Wait-For Graph Visualization

This tab visualizes the wait-for graph for deadlock detection.
Nodes represent processes, edges represent wait-for relationships.
Cycles are highlighted in red.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGraphicsScene, QGraphicsView,
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem,
    QLabel
)
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QFont, QPolygonF

import math
from typing import List, Tuple, Set

from models import SystemState
from detectors.wfg import get_wait_for_graph_for_visualization


class ArrowItem(QGraphicsLineItem):
    """A line with an arrowhead."""
    
    def __init__(self, x1, y1, x2, y2, color=Qt.black):
        super().__init__(x1, y1, x2, y2)
        self.color = color
        self.setZValue(1)
        
        # Set pen
        pen = QPen(color, 2)
        self.setPen(pen)
    
    def paint(self, painter, option, widget):
        """Draw line with arrowhead."""
        super().paint(painter, option, widget)
        
        # Draw arrowhead
        line = self.line()
        
        # Calculate arrow angle
        angle = math.atan2(-line.dy(), line.dx())
        
        arrow_size = 10
        arrow_p1 = line.p2() - QPointF(
            math.cos(angle + math.pi / 6) * arrow_size,
            math.sin(angle + math.pi / 6) * arrow_size
        )
        arrow_p2 = line.p2() - QPointF(
            math.cos(angle - math.pi / 6) * arrow_size,
            math.sin(angle - math.pi / 6) * arrow_size
        )
        
        arrow_head = QPolygonF([line.p2(), arrow_p1, arrow_p2])
        
        painter.setBrush(QBrush(self.color))
        painter.drawPolygon(arrow_head)


class GraphTab(QWidget):
    """
    Graph visualization tab.
    
    Displays wait-for graph with:
    - Circular nodes for processes
    - Directed edges for wait-for relationships
    - Red highlighting for cycles (deadlocked processes)
    """
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.current_state = None
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Header label
        self.header_label = QLabel("Wait-For Graph Visualization")
        self.header_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.header_label)
        
        # Info label
        self.info_label = QLabel("Run detection to see the wait-for graph.")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)
        
        # Graphics view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        layout.addWidget(self.view)
    
    def clear(self):
        """Clear the graph."""
        self.scene.clear()
        self.info_label.setText("Run detection to see the wait-for graph.")
        self.current_state = None
    
    def update_graph(self, state: SystemState, use_wfg: bool):
        """
        Update the graph visualization.
        
        Args:
            state: Current system state
            use_wfg: If True, show wait-for graph; else show message
        """
        self.current_state = state
        self.scene.clear()
        
        if not use_wfg:
            # Show message for matrix mode
            self.info_label.setText(
                "Wait-for graph visualization is only available in Single-Instance mode.\n"
                "Switch to Single-Instance mode to see the graph."
            )
            
            text = self.scene.addText(
                "Wait-for graph is only meaningful for single-instance resources.\n\n"
                "For multi-instance resources, use the Results tab to see\n"
                "the matrix-based detection algorithm output.",
                QFont("Arial", 12)
            )
            text.setPos(-200, -50)
            return
        
        # Get graph data
        edges, deadlocked = get_wait_for_graph_for_visualization(state)
        
        if not edges:
            self.info_label.setText("No wait-for edges (no process is waiting).")
            text = self.scene.addText(
                "No wait-for relationships detected.\n\n"
                "All processes can proceed without waiting.",
                QFont("Arial", 12)
            )
            text.setPos(-150, -30)
            return
        
        # Update info label
        if deadlocked:
            deadlocked_names = ", ".join(f"P{pid}" for pid in sorted(deadlocked))
            self.info_label.setText(f"Deadlock detected! Deadlocked processes: {deadlocked_names}")
        else:
            self.info_label.setText("No deadlock detected (no cycles in wait-for graph).")
        
        # Draw graph
        self.draw_graph(state.n, edges, deadlocked)
    
    def draw_graph(self, num_processes: int, edges: List[Tuple[int, int]], deadlocked: Set[int]):
        """
        Draw the wait-for graph.
        
        Args:
            num_processes: Number of processes
            edges: List of (from_pid, to_pid) tuples
            deadlocked: Set of deadlocked process IDs
        """
        # Calculate node positions in a circle
        radius = 150
        center_x = 0
        center_y = 0
        
        positions = {}
        for i in range(num_processes):
            angle = 2 * math.pi * i / num_processes - math.pi / 2  # Start from top
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions[i] = (x, y)
        
        # Draw edges
        for from_pid, to_pid in edges:
            x1, y1 = positions[from_pid]
            x2, y2 = positions[to_pid]
            
            # Offset edge endpoints to node boundary
            node_radius = 30
            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx * dx + dy * dy)
            
            if length > 0:
                # Normalize and scale
                dx /= length
                dy /= length
                
                x1 += dx * node_radius
                y1 += dy * node_radius
                x2 -= dx * node_radius
                y2 -= dy * node_radius
            
            # Color based on deadlock
            if from_pid in deadlocked and to_pid in deadlocked:
                color = QColor(255, 0, 0)  # Red for deadlock
            else:
                color = QColor(0, 0, 0)  # Black for normal
            
            arrow = ArrowItem(x1, y1, x2, y2, color)
            self.scene.addItem(arrow)
        
        # Draw nodes
        for pid in range(num_processes):
            x, y = positions[pid]
            
            # Node circle
            node_radius = 30
            
            if pid in deadlocked:
                brush = QBrush(QColor(255, 200, 200))  # Light red
                pen = QPen(QColor(255, 0, 0), 3)  # Red border
            else:
                brush = QBrush(QColor(200, 220, 255))  # Light blue
                pen = QPen(QColor(0, 0, 0), 2)  # Black border
            
            circle = QGraphicsEllipseItem(
                x - node_radius, y - node_radius,
                2 * node_radius, 2 * node_radius
            )
            circle.setBrush(brush)
            circle.setPen(pen)
            circle.setZValue(2)
            self.scene.addItem(circle)
            
            # Node label
            label = QGraphicsTextItem(f"P{pid}")
            label.setFont(QFont("Arial", 14, QFont.Bold))
            label.setDefaultTextColor(QColor(0, 0, 0))
            label.setPos(x - 12, y - 12)
            label.setZValue(3)
            self.scene.addItem(label)
        
        # Fit view to scene
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
