import webbrowser
import time

def open_pew_and_whatsapp():
    """Open a search for 'pew chat' and open WhatsApp Web in the default browser.

    Returns after opening the pages; caller should handle user confirmation for sending messages.
    """
    # Open a search for Pew chat (placeholder) so user can click appropriate result
    webbrowser.open('https://www.google.com/search?q=pew+chat')
    time.sleep(1)
    # Open WhatsApp Web
    webbrowser.open('https://web.whatsapp.com/')
    return True
