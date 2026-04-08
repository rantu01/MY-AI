import os
import sys
import time
import subprocess

BROWSER_PROCESSES = [
    "chrome.exe",
    "msedge.exe",
    "firefox.exe",
    "iexplore.exe",
    "brave.exe",
    "opera.exe",
]


def _terminate_with_psutil(names):
    import psutil
    terminated = []
    for proc in psutil.process_iter(['name', 'pid']):
        try:
            pname = proc.info.get('name') or ''
            if pname.lower() in names:
                try:
                    proc.terminate()
                    terminated.append((pname, proc.pid))
                except Exception:
                    try:
                        proc.kill()
                        terminated.append((pname, proc.pid))
                    except Exception:
                        pass
        except Exception:
            continue
    return terminated


def _terminate_with_taskkill(names):
    terminated = []
    for n in names:
        try:
            # /T kills child processes, /F forces
            subprocess.run(["taskkill", "/F", "/IM", n], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            terminated.append((n, None))
        except Exception:
            pass
    return terminated


def close_browsers():
    """Attempt to close common browser processes gracefully.
    Returns a list of (process_name, pid) terminated or attempted.
    """
    names = [n.lower() for n in BROWSER_PROCESSES]
    try:
        import psutil  # try to use psutil if available
        return _terminate_with_psutil(names)
    except Exception:
        # fallback to taskkill on Windows
        if os.name == 'nt':
            return _terminate_with_taskkill(names)
        return []


def close_and_shutdown(say_func=None, delay=5):
    """Close browsers and then shutdown the system.

    - say_func: optional callable(text) to announce shutdown before executing.
    - delay: seconds before shutdown (Windows `shutdown /s /t` uses seconds).
    """
    if say_func:
        try:
            say_func("Closing open tabs and shutting down the computer.")
        except Exception:
            pass
    # Close browsers
    try:
        close_browsers()
    except Exception:
        pass

    # Wait a moment to let TTS finish
    time.sleep(1)

    # Issue shutdown command depending on platform
    try:
        if os.name == 'nt':
            # Windows
            # use timeout to give user a few seconds to cancel if needed
            subprocess.run(["shutdown", "/s", "/t", str(max(5, int(delay)))])
        else:
            # Unix-like
            subprocess.run(["sudo", "shutdown", "-h", "+0"])
    except Exception:
        # fallback os.system
        try:
            if os.name == 'nt':
                os.system(f"shutdown /s /t {max(5, int(delay))}")
            else:
                os.system("sudo shutdown -h now")
        except Exception:
            pass


if __name__ == '__main__':
    print('Closing browsers and shutting down in 5 seconds...')
    close_and_shutdown()
