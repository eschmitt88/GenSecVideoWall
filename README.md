GenSec Video Wall
====================

This application is a Python-based project that uses PyQt5 for its GUI and several other libraries for its functionality. The main class in this application is `VideoWall`.

Libraries Used
--------------

- `pyautogui`: This library allows the program to programmatically control the mouse and keyboard.
- `PIL`: The Python Imaging Library (PIL) adds image processing capabilities to your Python interpreter.
- `keyboard`: This library is used for controlling and reading the state of the keyboard.
- `time`: This library is used for handling time-related tasks.
- `math`: This library provides mathematical functions.
- `pynput`: This library allows control and monitoring of input devices.
- `threading`: This module constructs higher-level threading interfaces on top of the lower level `_thread` module.
- `sys`: This module provides access to some variables used or maintained by the Python interpreter and to functions that interact strongly with the interpreter.
- `PyQt5`: This set of Python bindings for The Qt Company’s Qt application framework and runs on all platforms supported by Qt including Windows, OS X, Linux, iOS, and Android.
- `win32con`, `win32api`: These libraries provide certain functions for interacting with the Windows operating system.

Class Description
-----------------

The `VideoWall` class is a `QWidget` that represents a video wall. It has several attributes:

- `num_displays`: The number of displays in the video wall.
- `is_clicking`: A boolean indicating whether the video wall is currently being clicked.
- `thread`: A `threading.Thread` object for running tasks in the background.
- `mutex`: A `threading.Lock` object for ensuring thread safety.
- `current_display`: The current display being shown on the video wall.
- `screenshot_pixmap`: The current screenshot being displayed.
- `target_width`, `target_height`: The target dimensions for the video wall.
- `interval`: The interval at which the video wall updates.
- `start_hotkey`: The hotkey to start the video wall.

The `VideoWall` class also has a `display_updated` signal that emits a `QImage` and an integer whenever the display is updated.

How to Run
----------

To run this application, you need to have Python installed on your machine along with the libraries mentioned above. You can then run the `app.py` file using the Python interpreter.