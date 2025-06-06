import ctypes
import os
import platform
import subprocess
import tempfile
import urllib.request


def vc_runtime_installed():
    """Return True if the Microsoft Visual C++ runtime is available."""
    if platform.system().lower() != "windows":
        return True
    for dll in ("vcruntime140.dll", "vcruntime140_1.dll"):
        try:
            ctypes.WinDLL(dll)
            return True
        except OSError:
            continue
    return False


def install_vc_runtime():
    """Download and silently install the Microsoft Visual C++ runtime."""
    if platform.system().lower() != "windows":
        return False

    url = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
    tmp_dir = tempfile.gettempdir()
    installer = os.path.join(tmp_dir, "vc_redist.x64.exe")

    urllib.request.urlretrieve(url, installer)

    try:
        subprocess.run([installer, "/quiet", "/norestart"], check=True)
    finally:
        if os.path.exists(installer):
            os.remove(installer)

    return vc_runtime_installed()
