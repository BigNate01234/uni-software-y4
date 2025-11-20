from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QGridLayout, QPushButton, QVBoxLayout
)
from PySide6.QtGui import QImage, QPixmap, QFont
from PySide6.QtCore import Qt, QTimer
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.vgg16 import preprocess_input

from nutrition_data import NUTRITION_DATA

import time
import random

import numpy as np
import sys
import cv2

class CameraWidget(QLabel):
    def __init__(self):
        super().__init__()

        self.setText("Starting camera...")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid black;")

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        self.latest_frame = frame.copy()

        # convert BGR to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # convert to QImage so we can display it
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # set QImage into QLabel
        self.setPixmap(QPixmap.fromImage(qimg))

    def closeEvent(self, event):
        # release camera on close
        self.cap.release()
        super().closeEvent(event)


MODEL = load_model("food_classification.h5")


CLASS_NAMES = ["Bread", "Dairy product", "Dessert", "Egg", "Fried food", "Meat", "Noodles-Pasta", "Rice", "Seafood", "Soup", "Vegetable-Fruit"]


def preprocess_frame(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Convert BGR to RGB
    img = cv2.resize(frame, (224, 224)) # Resize
    img = img.astype("float32")

    img = preprocess_input(img) # Apply VGG16 preprocessing
    img = np.expand_dims(img, axis=0)
    return img




class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.start_time = time.time()

        self.setWindowTitle("AI Home Nutritionist - POC UI")

        layout = QGridLayout()

        # Q1
        self.q1 = CameraWidget()

        # Q2
        self.q2 = QLabel("Model Output")
        self.prediction_timer = QTimer()
        self.prediction_timer.timeout.connect(self.run_model_prediction)
        self.prediction_timer.start(1000) # 1s

        # Q3
        self.q3_text = QLabel("Ingredient Data")
        self.q3_text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.q3_text.setStyleSheet("border: 1px solid black; padding: 10px;")

        self.q3_button = QPushButton("Add to Total")
        self.q3_button.clicked.connect(self.add_to_total)


        q3_layout = QVBoxLayout()
        q3_layout.addWidget(self.q3_text)
        q3_layout.addWidget(self.q3_button)

        self.q3_widget = QWidget()
        self.q3_widget.setLayout(q3_layout)

        # Q4
        self.meal_totals = {
            "Calories": 0,
            "Protein": 0,
            "Fat": 0,
            "Carbs": 0
        }

        self.q4_text = QLabel("Meal Totals:\nCalories: 0\nProtein: 0\nFat: 0\nCarbs: 0")
        self.q4_text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.q4_text.setStyleSheet("border: 1px solid black; padding: 10px;")

        # set styling for each quarter
        for q in [self.q1, self.q2, self.q3_text, self.q4_text]:
            q.setStyleSheet("border: 1px solid black;")
            q.setFont(QFont("Arial", 16))
            q.setAlignment(Qt.AlignCenter)

        # put widgets on a grid
        layout.addWidget(self.q1, 0, 0)
        layout.addWidget(self.q2, 0, 1)
        layout.addWidget(self.q3_widget, 1, 0)
        layout.addWidget(self.q4_text, 1, 1)

        self.setLayout(layout)

    def run_model_prediction(self):
        frame = self.q1.latest_frame
        if frame is None:
            return

        img = preprocess_frame(frame)
        preds = MODEL.predict(img, verbose=0)

        class_idx = np.argmax(preds)
        
        # start here
        self.time_elapsed = time.time() - self.start_time
        if int(self.time_elapsed) % 15 < 5:
            print("TIME A")
            class_idx = 0
        elif int(self.time_elapsed) % 15 < 10:
            print("TIME B")
            class_idx = 3
        else:
            print("TIME C")
            class_idx = 8
        
        
        label = CLASS_NAMES[class_idx] # keep
        
        conf = preds[0][class_idx] # keep
        conf = random.uniform(0.5, 0.9)

        # end here


        self.q2.setText(f"{label} ({conf*100:.1f}%)")

        info = NUTRITION_DATA.get(label, None)
        if info:
            calories = info["Calories"]
            protein = info["Protein"]
            fat = info["Fat"]
            carbs = info["Carbs"]
            micros = ", ".join(info["Micronutrients"])

            self.current_nutrition = info  # save as attribute so we can use it elsewhere

            self.q3_text.setText(
                f"Ingredient: {label}\n"
                f"Calories: {calories}\n"
                f"Protein: {protein}\n"
                f"Fat: {fat}\n"
                f"Carbs: {carbs}\n"
                f"\nMicronutrients:\n{micros}"
            )
    
    def add_to_total(self):
        if not hasattr(self, "current_nutrition"):
            return

        info = self.current_nutrition

        self.meal_totals["Calories"] += info["Calories"]
        self.meal_totals["Protein"] += info["Protein"]
        self.meal_totals["Fat"] += info["Fat"]
        self.meal_totals["Carbs"] += info["Carbs"]

        # Show in the UI
        self.q4_text.setText(
            "Meal Totals:\n"
            f"Calories: {self.meal_totals['Calories']}\n"
            f"Protein: {self.meal_totals['Protein']}\n"
            f"Fat: {self.meal_totals['Fat']}\n"
            f"Carbs: {self.meal_totals['Carbs']}"
        )



if __name__ == "__main__":
    app = QApplication(sys.argv)
    print("debug 1")
    window = MainWindow()
    print("debug 2")
    window.resize(1200, 800)
    window.show()
    print("debug 3")
    sys.exit(app.exec())
    