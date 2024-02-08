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
from src.camera_id import screenshot_to_ID, write_id_to_image
from src.utils.FlowLayout import FlowLayout
from src.utils.best_fit import best_fit
import numpy as np


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
            self.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(160, 90, QtGui.QImage.Format_RGB888)))
            self.last_update = time.time()
            self.n_updates = 0
            self.update_span = 0
            self.update_span_filt = 10

        def update_image(self, screenshot):
            target_width = self.width()-2
            target_height = self.height()-2
            screenshot = screenshot.scaled(target_width, target_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(QtGui.QPixmap.fromImage(screenshot))
            self.update()
            self.n_updates += 1
            self.update_span = time.time() - self.last_update
            self.update_span_filt = 0.9 * self.update_span_filt + 0.1 * self.update_span
            self.last_update = time.time()

        def resizeEvent(self, event):
            self.update_image(self.pixmap().toImage())

    def __init__(self):
        super(VideoWall, self).__init__()

        self.is_clicking = False
        self.thread = None
        self.mutex = threading.Lock()
        self.target_width = 1900
        self.target_height = 970
        self.interval = 0.03
        self.displays = {}
        self.shown_displays = []
        self.main_camera_id = None
        self.main_display = self.DisplayObject()
        self.n_iterations = 0
        self.average_span = 10

        self.initUI()

        self.start_hotkey = '['
        self.stop_hotkey = ']'
        self.increase_hotkey = '='
        self.decrease_hotkey = '-'
        self.reset_hotkey = '0'

        keyboard.add_hotkey(self.start_hotkey, self.start_clicks)
        keyboard.add_hotkey(self.stop_hotkey, self.stop_clicks)
        keyboard.add_hotkey(self.increase_hotkey, self.next_camera)
        keyboard.add_hotkey(self.decrease_hotkey, self.prev_camera)
        keyboard.add_hotkey('space', self.stop_clicks)
        keyboard.add_hotkey(self.reset_hotkey, self.reset)


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
        """Set up the mini displays in the right frame. This function is called when a new display is created."""
        # Clear the layouts and widgets
        for i in reversed(range(self.right_frame.layout().count())):
            self.right_frame.layout().itemAt(i).widget().setParent(None)

        # Prune the displays to only show the most updated ones
        self.calc_average_span()
        self.shown_displays = []
        keys = sorted(self.displays.keys())
        for key in keys:
            if self.displays[key].update_span_filt < 1.1*self.average_span:
                self.shown_displays.append(key)

        # Calculate the number of rows and columns for the grid layout
        (width, height), (cols, rows) = best_fit(self.right_shape, (1920, 1080), len(self.shown_displays))
        widget_width = int(width)
        widget_height = int(height)

        # Create display widgets and add them to the layout
        for i, key in enumerate(self.shown_displays):
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
                self.displays[key].setStyleSheet("border: 3px solid limegreen;")
            else:
                self.displays[key].setStyleSheet("border: 1px solid black;")

    def next_camera(self):
        keys = self.shown_displays
        if self.main_camera_id is None:
            self.main_camera_id = keys[0]
        else:
            index = keys.index(self.main_camera_id)
            index = (index + 1) % len(keys)
            self.main_camera_id = keys[index]
            self.update_mini_displays_signal.emit()
            self.main_display.update_image(self.displays[self.main_camera_id].pixmap().toImage())

    def prev_camera(self):
        keys = self.shown_displays
        if self.main_camera_id is None:
            self.main_camera_id = keys[0]
        else:
            index = keys.index(self.main_camera_id)
            index = (index - 1) % len(keys)
            self.main_camera_id = keys[index]
            self.update_mini_displays_signal.emit()
            self.main_display.update_image(self.displays[self.main_camera_id].pixmap().toImage())

    def calc_average_span(self):
        self.average_span = np.mean([self.displays[key].update_span_filt for key in self.displays])

    def run_clicks(self):
        while self.is_clicking:
            with self.mutex:
                self.n_iterations += 1
                # Take a screenshot and display it
                screenshot = pyautogui.screenshot()
                screenshot_np = np.array(screenshot)

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

                # If the camera is not already in the list of displays, add it
                if current_id not in self.displays and self.n_iterations < 1000:
                    self.create_display_signal.emit(current_id)
                    print(f"New camera found: {current_id}")
                    if self.main_camera_id is None:
                        self.main_camera_id = current_id
                        self.update_mini_displays_signal.emit()

                # prune displays every 100 iterations
                if self.n_iterations % 100 == 0:
                    self.setup_mini_displays_signal.emit()

                # Convert the screenshot to a QImage and update the relevant display(s)
                # Main display
                if current_id == self.main_camera_id:
                    screenshot = screenshot.convert("RGB")
                    screenshot = QtGui.QImage(screenshot.tobytes(), screenshot.width, screenshot.height, QtGui.QImage.Format_RGB888)
                    self.update_main_display(screenshot)
                # Mini display
                screenshot_np = write_id_to_image(screenshot_np, current_id)
                screenshot_PIL = Image.fromarray(screenshot_np)
                screenshot = QtGui.QImage(screenshot_PIL.tobytes(), screenshot_PIL.width, screenshot_PIL.height, QtGui.QImage.Format_RGB888)
                self.displays[current_id].update_image(screenshot)

                # Perform clicks, which will progress to the next display
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0) # Press the left mouse button
                time.sleep(self.interval / 2)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0) # Release the left mouse button
                time.sleep(self.interval / 2)

    def reset(self):
        self.stop_clicks()
        self.displays = {}
        self.shown_displays = []
        self.main_camera_id = None
        self.main_display.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(160, 90, QtGui.QImage.Format_RGB888)))
        self.n_iterations = 0
        self.average_span = 10
        self.setup_mini_displays_signal.emit()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = VideoWall()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
