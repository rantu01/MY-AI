import webbrowser
import time
import os
import subprocess


def _open_in_chrome(url: str) -> bool:
    # try common Chrome paths on Windows
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                subprocess.Popen([p, url], shell=False)
                return True
            except Exception:
                pass
    return False


def open_pew_and_whatsapp():
    """Open a Google search for 'pew chat' and WhatsApp Web (prefer Chrome).

    Returns True if opening was attempted.
    """
    search_url = 'https://www.google.com/search?q=pew+chat'
    wa_url = 'https://web.whatsapp.com/'

    opened = False
    if not _open_in_chrome(search_url):
        webbrowser.open(search_url)
    else:
        opened = True
    time.sleep(1)
    if not _open_in_chrome(wa_url):
        webbrowser.open(wa_url)
    else:
        opened = True

    return opened
