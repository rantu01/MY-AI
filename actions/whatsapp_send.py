import time
import pyautogui

def send_whatsapp_message(message: str, wait_before_typing: float = 6.0):
    """Assumes WhatsApp Web is open and the desired chat is active.

    Types the message and presses Enter.
    """
    # give browser time to be ready
    time.sleep(wait_before_typing)
    pyautogui.write(message, interval=0.03)
    time.sleep(0.1)
    pyautogui.press('enter')
