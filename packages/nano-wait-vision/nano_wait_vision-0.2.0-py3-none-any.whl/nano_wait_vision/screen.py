import cv2
import numpy as np
import pyautogui


def capture_screen(gray: bool = False):
    """
    Capture the current screen and return it as a numpy array.
    """
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    if gray:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    return frame
