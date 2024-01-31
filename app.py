import pyautogui
from PIL import Image
import keyboard
import time
import math
from pynput.mouse import Controller, Button
import threading
import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QMetaObject, pyqtSlot, QTimer, QObject
import win32con
import win32api


class VideoWall(QtWidgets.QWidget):
    display_updated = pyqtSignal(QtGui.QImage, int)

    def __init__(self):
        super(VideoWall, self).__init__()

        self.num_displays = 9
        self.is_clicking = False
        self.thread = None
        self.mutex = threading.Lock()
        self.current_display = 0
        self.screenshot_pixmap = None
        scale_factor = 0.9
        self.target_width = int(1920 * scale_factor)
        self.target_height = int(1080 * scale_factor)
        self.interval = 0.03

        self.initUI()

        self.start_hotkey = '['
        self.stop_hotkey = ']'
        self.increase_hotkey = '='
        self.decrease_hotkey = '-'

        keyboard.add_hotkey(self.start_hotkey, self.start_clicks)
        keyboard.add_hotkey(self.stop_hotkey, self.stop_clicks)
        keyboard.add_hotkey(self.increase_hotkey, self.increase_displays)
        keyboard.add_hotkey(self.decrease_hotkey, self.decrease_displays)

    def initUI(self):
        self.setGeometry(1930, 35, self.target_width, self.target_height)
        self.setWindowTitle('GenSec Video Wall')

        self.setLayout(QtWidgets.QGridLayout())
        self.setup_displays()

        self.display_updated.connect(self.update_display)

        self.show()

        self.mouse = Controller()

    @pyqtSlot()
    def setup_displays_in_main_thread(self):
        self.setup_displays()

    def setup_displays(self):
        # Clear the layouts and widgets
        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().setParent(None)

        # Calculate the number of rows and columns for the grid layout
        num_rows = int(math.sqrt(self.num_displays))
        num_cols = math.ceil(self.num_displays / num_rows)
        widget_width = int((self.target_width-30) / num_cols)
        widget_height = int((self.target_height-30) / num_rows)

        # Create display widgets and add them to the layout
        for i in range(self.num_displays):
            display_widget = QtWidgets.QLabel(self)
            display_widget.setAlignment(Qt.AlignCenter)
            display_widget.setStyleSheet("border: 1px solid black;")
            display_widget.setFixedSize(widget_width, widget_height)
            self.layout().addWidget(display_widget, i // num_cols, i % num_cols)

        # Update the layout
        self.layout().update()

    def start_clicks(self):
        if not self.is_clicking:
            self.is_clicking = True
            self.thread = threading.Thread(target=self.run_clicks)
            self.thread.start()

    def stop_clicks(self):
        if self.is_clicking:
            self.is_clicking = False
            self.thread.join()

    def increase_displays(self):
        self.num_displays += 1
        QTimer.singleShot(0, self.setup_displays_in_main_thread)

    def decrease_displays(self):
        if self.num_displays > 1:
            self.num_displays -= 1
            QTimer.singleShot(0, self.setup_displays_in_main_thread)

    def run_clicks(self):
        while self.is_clicking:
            with self.mutex:
                # For demonstration, take a screenshot and display it
                screenshot = pyautogui.screenshot()
                print('screenshot')

                screenshot = screenshot.convert("RGB")

                # screenshot = screenshot.resize((target_width, target_height), Image.NEAREST)
                screenshot = QtGui.QImage(screenshot.tobytes(), screenshot.width, screenshot.height, QtGui.QImage.Format_RGB888)

                i = int(self.current_display)
                self.display_updated.emit(screenshot, i)
                # self.update_display(screenshot)
                self.current_display = (self.current_display + 1) % self.num_displays

                # Perform click actions here
                # time.sleep(self.interval)
                # self.mouse.click(Button.left)
                # pyautogui.click()
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0) # Press the left mouse button
                time.sleep(self.interval / 2) # Wait half the interval before releasing the button
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0) # Release the left mouse button
                time.sleep(self.interval / 2) # Wait the other half of the interval before performing the next click
                print('click')

                # time.sleep(self.interval)

    @pyqtSlot(QtGui.QImage, int)
    def update_display(self, screenshot, display_index):
        layout_item = self.layout().itemAt(display_index)

        if layout_item is not None:
            label = layout_item.widget()

            if label is not None:
                # Calculate the target size while preserving the aspect ratio
                target_width = label.width()
                target_height = label.height()

                screenshot = screenshot.scaled(target_width, target_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                label.setPixmap(QtGui.QPixmap.fromImage(screenshot))
                label.update()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = VideoWall()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
