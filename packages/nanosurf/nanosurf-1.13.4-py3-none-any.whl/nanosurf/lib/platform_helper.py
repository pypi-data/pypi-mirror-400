import platform
import os

def is_headless() -> bool:
    """Detects if the system likely has no GUI."""
    if platform.system() == "Linux":
        return not any(k in os.environ for k in ("DISPLAY", "WAYLAND_DISPLAY"))
    elif platform.system() == "Windows":
        # crude heuristic: no desktop session
        return os.environ.get("SESSIONNAME") in (None, "Services")
    elif platform.system() == "Darwin":
        return False
    return True

def has_graphic_output() -> bool:
    """ Returns True if running platform the possibility of graphical output.
        If True packages like PySide6 or matplotlib are usable
    """
    return not is_headless()

def get_platform_name() -> str:
    """ Returns the name of the running operating system"""
    try:
        os_release = platform.freedesktop_os_release()
        return os_release.get('PRETTY_NAME', '')
    except Exception :
        pass
    return ""

def is_Nanosurf_Linux() -> bool:
    """ Returns True if Nanosurf's embedded Linux is detected as running platform"""
    return get_platform_name().lower().find("nanosurf") >= 0
