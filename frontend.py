from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QGridLayout
)
from PySide6.QtGui import QImage, QPixmap, QFont
from PySide6.QtCore import Qt, QTimer
from tensorflow.keras.models import load_model
import numpy as np
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

        # saving this because we're gonna be using it elsewhere
        self.latest_frame = frame.copy()

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


MODEL = load_model("your_model.h5")

CLASS_NAMES = ["class 0", "class 1", "class 2", "class 3", "class 4", "class 5", "class 6", "class 7", "class 8", "class 9", "class 10"]


def preprocess_frame(frame):
    img = cv2.resize(frame, (224, 224))
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)
    return img



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Home Nutritionist - POC UI")

        layout = QGridLayout()

        # Q1 = live camera feed
        q1 = CameraWidget()

        q2 = QLabel("Model Output")
        self.prediction_timer = QTimer()
        self.prediction_timer.timeout.connect(self.run_model_prediction)
        self.prediction_timer.start(1000) # 1s


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

    def run_model_prediction(self):
        frame = self.q1.latest_frame
        if frame is None:
            return

        img = preprocess_frame(frame)
        preds = MODEL.predict(img, verbose=0)

        class_idx = np.argmax(preds)
        label = CLASS_NAMES[class_idx]
        conf = preds[0][class_idx]

        self.q2.setText(f"{label} ({conf*100:.1f}%)")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())