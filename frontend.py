from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QGridLayout
)
from PySide6.QtGui import QImage, QPixmap, QFont
from PySide6.QtCore import Qt, QTimer
import sys
import cv2

class CameraWidget(QLabel):
    def __init__(self):
        super().__init__()

        self.setText("Starting camera...")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid black;")

        # Start webcam
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        # Timer to grab frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)     # ~30 FPS

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # Convert BGR (OpenCV) to RGB (Qt)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert to QImage
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Set QImage into QLabel
        self.setPixmap(QPixmap.fromImage(qimg))

    def closeEvent(self, event):
        # Release camera on close
        self.cap.release()
        super().closeEvent(event)



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Home Nutritionist - POC UI")

        layout = QGridLayout()

        # Q1 = live camera feed
        q1 = CameraWidget()

        # placeholders
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