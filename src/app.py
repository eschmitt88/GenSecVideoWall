import pyautogui
from PIL import Image
import keyboard
import time
import math
from pynput.mouse import Controller, Button
import threading
import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QMetaObject, pyqtSlot, QTimer, QObject, QCoreApplication
import win32con
import win32api
from src.camera_id import screenshot_to_ID
from src.utils.FlowLayout import FlowLayout
from src.utils.best_fit import best_fit


class VideoWall(QtWidgets.QWidget):
    create_display_signal = pyqtSignal(str)
    setup_mini_displays_signal = pyqtSignal()
    update_mini_displays_signal = pyqtSignal()

    class DisplayObject(QtWidgets.QLabel):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            self.setStyleSheet("border: 1px solid black;")
            self.setAlignment(Qt.AlignCenter)
            self.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(192, 108, QtGui.QImage.Format_RGB888)))

        @pyqtSlot(QtGui.QImage)
        def update_image(self, screenshot):
            target_width = self.width()-2
            target_height = self.height()-2
            screenshot = screenshot.scaled(target_width, target_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(QtGui.QPixmap.fromImage(screenshot))
            self.update()

    def __init__(self):
        super(VideoWall, self).__init__()

        self.is_clicking = False
        self.thread = None
        self.mutex = threading.Lock()
        self.target_width = 1900
        self.target_height = 970
        self.interval = 0.03
        self.displays = {}
        self.main_camera_id = None
        self.main_display = self.DisplayObject()

        self.initUI()

        self.start_hotkey = '['
        self.stop_hotkey = ']'
        self.increase_hotkey = '='
        self.decrease_hotkey = '-'

        keyboard.add_hotkey(self.start_hotkey, self.start_clicks)
        keyboard.add_hotkey(self.stop_hotkey, self.stop_clicks)
        keyboard.add_hotkey(self.increase_hotkey, self.next_camera)
        keyboard.add_hotkey(self.decrease_hotkey, self.prev_camera)

    def initUI(self):
        self.setGeometry(1930, 35, self.target_width, self.target_height)
        self.setWindowTitle('GenSec Video Wall')
        self.setup_top_level()

        self.create_display_signal.connect(self.create_display)
        self.setup_mini_displays_signal.connect(self.setup_mini_displays)
        self.update_mini_displays_signal.connect(self.update_mini_displays)

        self.show()

        self.right_shape = (self.right_frame.width(), self.right_frame.height())

        self.mouse = Controller()

    def setup_top_level(self):
        self.setLayout(QtWidgets.QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().setColumnStretch(0, 3)
        self.layout().setColumnStretch(1, 1)
        self.setStyleSheet("background-color: black;")

        # create left frame
        self.layout().addWidget(self.main_display, 0, 0)

        # create right frame
        self.right_frame = QtWidgets.QFrame(self)
        self.right_frame.setStyleSheet("border: 1px solid black;")
        self.right_frame.setLayout(QtWidgets.QGridLayout())
        self.right_frame.layout().setContentsMargins(0, 0, 0, 0)
        self.right_frame.layout().setSpacing(0)
        self.layout().addWidget(self.right_frame, 0, 1)

    @pyqtSlot()
    def setup_mini_displays(self):
        # Clear the layouts and widgets
        for i in reversed(range(self.right_frame.layout().count())):
            self.right_frame.layout().itemAt(i).widget().setParent(None)

        # Calculate the number of rows and columns for the grid layout
        (width, height), (cols, rows) = best_fit(self.right_shape, (1920, 1080), len(self.displays))
        widget_width = int(width)
        widget_height = int(height)

        # Create display widgets and add them to the layout
        keys = sorted(self.displays.keys())
        for i, key in enumerate(keys):
            self.displays[key].setFixedSize(widget_width, widget_height)
            r = i // cols
            c = i % cols
            self.right_frame.layout().addWidget(self.displays[key], r, c)

        # Update the layout
        self.right_frame.layout().update()

    # @pyqtSlot(QtGui.QImage)
    def update_main_display(self, screenshot):
        self.main_display.update_image(screenshot)

    @pyqtSlot(str)
    def create_display(self, display_id):
        self.displays[display_id] = self.DisplayObject()
        self.setup_mini_displays_signal.emit()

    def start_clicks(self):
        if not self.is_clicking:
            self.is_clicking = True
            self.thread = threading.Thread(target=self.run_clicks)
            self.thread.start()

    def stop_clicks(self):
        if self.is_clicking:
            self.is_clicking = False
            self.thread.join()

    @pyqtSlot()
    def update_mini_displays(self):
        for key in self.displays:
            if key == self.main_camera_id:
                self.displays[key].setStyleSheet("border: 4px solid limegreen;")
            else:
                self.displays[key].setStyleSheet("border: 1px solid black;")

    def next_camera(self):
        keys = sorted(self.displays.keys())
        if self.main_camera_id is None:
            self.main_camera_id = keys[0]
        else:
            index = keys.index(self.main_camera_id)
            index = (index + 1) % len(keys)
            self.main_camera_id = keys[index]
            self.update_mini_displays_signal.emit()

    def prev_camera(self):
        keys = sorted(self.displays.keys())
        if self.main_camera_id is None:
            self.main_camera_id = keys[0]
        else:
            index = keys.index(self.main_camera_id)
            index = (index - 1) % len(keys)
            self.main_camera_id = keys[index]
            self.update_mini_displays_signal.emit()

    def run_clicks(self):
        while self.is_clicking:
            with self.mutex:
                # Take a screenshot and display it
                screenshot = pyautogui.screenshot()

                # Extract the camera number from the screenshot
                try:
                    current_id = screenshot_to_ID(screenshot, typ='str')
                except Exception as e:
                    print(e)
                    time.sleep(0.2)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0) # Press the left mouse button
                    time.sleep(self.interval / 2) # Wait half the interval before releasing the button
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0) # Release the left mouse button
                    time.sleep(self.interval / 2) # Wait the other half of the interval before performing the next click
                    continue

                if current_id not in self.displays:
                    self.create_display_signal.emit(current_id)
                    print(f"New camera found: {current_id}")
                    if self.main_camera_id is None:
                        self.main_camera_id = current_id
                        self.update_mini_displays_signal.emit()

                screenshot = screenshot.convert("RGB")
                screenshot = QtGui.QImage(screenshot.tobytes(), screenshot.width, screenshot.height, QtGui.QImage.Format_RGB888)

                if current_id == self.main_camera_id:
                    self.update_main_display(screenshot)

                self.displays[current_id].update_image(screenshot)
                self.layout().update()

                # Perform click actions here to click on the screen, which will progress to the next display
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0) # Press the left mouse button
                time.sleep(self.interval / 2) # Wait half the interval before releasing the button
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0) # Release the left mouse button
                time.sleep(self.interval / 2) # Wait the other half of the interval before performing the next click


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = VideoWall()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
