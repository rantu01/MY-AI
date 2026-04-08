import time
import pyautogui

def type_text(text: str, press_enter: bool = False, interval: float = 0.02):
    """Type the given text into the active window. Optionally press Enter."""
    # small delay to give user time to focus desired window
    time.sleep(0.5)
    pyautogui.write(text, interval=interval)
    if press_enter:
        time.sleep(0.1)
        pyautogui.press('enter')
