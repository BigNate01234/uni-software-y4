from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QGridLayout
)
from PySide6.QtGui import QFont
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Home Nutritionist - POC UI")

        layout = QGridLayout()

        # Create 4 placeholder quadrants
        q1 = QLabel("Camera Feed")
        q2 = QLabel("Model Output")
        q3 = QLabel("Ingredient Data")
        q4 = QLabel("Meal Totals")

        for q in [q1, q2, q3, q4]:
            q.setStyleSheet("border: 1px solid black;")
            q.setFont(QFont("Arial", 16))
            q.setAlignment(Qt.AlignCenter)

        # Add widgets to grid
        layout.addWidget(q1, 0, 0)
        layout.addWidget(q2, 0, 1)
        layout.addWidget(q3, 1, 0)
        layout.addWidget(q4, 1, 1)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())