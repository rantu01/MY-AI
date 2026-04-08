import time
import pyautogui
import pyperclip
try:
    import pygetwindow as gw
except Exception:
    gw = None


def _bring_window_with_title(substring: str, timeout=6.0) -> bool:
    """Try to find a window whose title contains `substring` and activate it."""
    if not gw:
        return False
    end = time.time() + timeout
    while time.time() < end:
        wins = gw.getWindowsWithTitle(substring)
        if wins:
            try:
                w = wins[0]
                w.activate()
                return True
            except Exception:
                pass
        time.sleep(0.3)
    return False


def type_text(text: str, press_enter: bool = False, interval: float = 0.02, focus_title: str = None):
    """Type the given text into the active window. Optionally press Enter.

    For reliability we copy to clipboard and paste (Ctrl+V). Optionally try to
    focus a window whose title contains `focus_title` before typing.
    """
    if focus_title:
        _bring_window_with_title(focus_title)

    time.sleep(0.4)
    # use clipboard paste to avoid typing issues
    try:
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
    except Exception:
        # fallback to typing
        pyautogui.write(text, interval=interval)

    if press_enter:
        time.sleep(0.1)
        pyautogui.press('enter')
