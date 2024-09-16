import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QComboBox)
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QPainter, QColor

class ClockWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clock")
        self.setGeometry(100, 100, 400, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.time_label = QLabel()
        self.layout.addWidget(self.time_label)

        self.combo_box = QComboBox()
        self.combo_box.addItems(["Digital", "Analog"])
        self.combo_box.currentIndexChanged.connect(self.update_display)
        self.layout.addWidget(self.combo_box)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second

        self.current_time = QTime.currentTime()
        self.update_time()

    def update_time(self):
        self.current_time = QTime.currentTime()
        self.update_display()

    def update_display(self):
        if self.combo_box.currentText() == "Digital":
            self.time_label.setText(self.current_time.toString("hh:mm:ss"))
            self.time_label.setStyleSheet("font-size: 30px;")
            self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.time_label.setVisible(True)
            self.update()  # Trigger a repaint for the analog clock
        else:
            self.time_label.setVisible(False)
            self.update()  # Trigger a repaint for the analog clock

    def paintEvent(self, event):
        if self.combo_box.currentText() == "Analog":
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Draw clock face
            rect = self.rect()
            radius = min(rect.width(), rect.height()) // 2 - 10
            center = rect.center()
            painter.setBrush(QColor(255, 255, 255))
            painter.drawEllipse(center, radius, radius)

            # Draw hour hand
            hour_angle = (self.current_time.hour() % 12 + self.current_time.minute() / 60) * 30
            self.draw_hand(painter, hour_angle, radius * 0.5, QColor(0, 0, 0), 6)

            # Draw minute hand
            minute_angle = (self.current_time.minute() + self.current_time.second() / 60) * 6
            self.draw_hand(painter, minute_angle, radius * 0.8, QColor(0, 0, 0), 4)

            # Draw second hand
            second_angle = self.current_time.second() * 6
            self.draw_hand(painter, second_angle, radius * 0.9, QColor(255, 0, 0), 2)

    def draw_hand(self, painter, angle, length, color, width):
        painter.save()
        painter.setPen(QColor(color))
        painter.setBrush(QColor(color))
        painter.translate(self.rect().center())
        painter.rotate(angle)
        painter.drawRect(-width // 2, -length, width, length)
        painter.restore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    clock = ClockWidget()
    clock.show()
    sys.exit(app.exec())