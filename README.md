<div style="text-align: center;">
    <img src="assets/GenSec.png" alt="Logo" width="350"/>
</div>

GenSec Video Wall
====================
This application is a Python-based project that uses the PyQt5 GUI. It creates a video wall that displays the live feed from a Payday 2 in-game camera feed. By clicking rapidly through the camera feed, all guards will be highlighted in red, making it easier for teammates to spot them. While rapidly clicking through the camera feed, your screen will be a complete blur, so this application creates a video wall that parses out the images between clicks and displays the individual feeds in a grid. One of the video feeds is enlarged so as to be useful for the player, while the rest of the feeds are smaller.

How to Run
----------
To run this application, you need to have Python 11 installed on your machine along with the libraries mentioned in requirements.txt. See the [requirements](#requirements.txt) file for more information.

The following hotkeys are used to control the application:
- "[": start clicking (press once you are in the camera feed)
- "]" or "space": stop clicking
- "-": Scroll to previous camera
- "=": Scroll to next camera
- "0": Reset the displays
- arrow keys: move the OCR box (used for identifying cameras)
- shift + arrow keys: resize the OCR box

Example Video
-------------
[![GenSec Video Wall](https://img.youtube.com/vi/VOMTxYovzzY/0.jpg)](https://youtu.be/VOMTxYovzzY)