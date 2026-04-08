import time
import pyautogui
import pyperclip
try:
    import pygetwindow as gw
except Exception:
    gw = None


def _activate_whatsapp_window(timeout=8.0) -> bool:
    if not gw:
        return False
    end = time.time() + timeout
    while time.time() < end:
        wins = gw.getWindowsWithTitle('WhatsApp') + gw.getWindowsWithTitle('Chrome')
        if wins:
            try:
                wins[0].activate()
                return True
            except Exception:
                pass
        time.sleep(0.3)
    return False


def send_whatsapp_message(message: str, wait_before_typing: float = 6.0):
    """Bring WhatsApp Web to front, paste message and press Enter.

    If the WhatsApp chat isn't selected, the user must select it first.
    """
    # try to activate WhatsApp window
    _activate_whatsapp_window()
    # wait for page to be ready
    time.sleep(wait_before_typing)
    try:
        pyperclip.copy(message)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)
        pyautogui.press('enter')
        return True
    except Exception:
        try:
            # fallback to typing
            pyautogui.write(message, interval=0.03)
            time.sleep(0.1)
            pyautogui.press('enter')
            return True
        except Exception:
            return False
