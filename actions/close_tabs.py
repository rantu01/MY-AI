import time
import pyautogui

def close_all_tabs(repeat: int = 12, delay: float = 0.25):
    """Close tabs in the active browser by sending Ctrl+W multiple times."""
    time.sleep(0.5)
    for _ in range(repeat):
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(delay)
