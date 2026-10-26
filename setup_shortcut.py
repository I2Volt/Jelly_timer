import os
import sys
import stat
import shutil
import platform
from PIL import Image, ImageDraw

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_ICO_PATH = os.path.join(PROJECT_DIR, "jelly_timer.ico")
ICON_PNG_PATH = os.path.join(PROJECT_DIR, "jelly_timer.png")
SCRIPT_PY = os.path.join(PROJECT_DIR, "jelly_timer.py")
SCRIPT_PATH = os.path.join(PROJECT_DIR, "jelly_timer.pyw")

OS_NAME = platform.system()
IS_WIN = (OS_NAME == "Windows")
IS_MAC = (OS_NAME == "Darwin")
IS_LINUX = (OS_NAME == "Linux")


def create_icon():
    """Minimalist Linear/Apple-style monochrome dark graphite icon."""
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Matte zinc squircle (#18181B) with subtle hairline border (#3F3F46)
    draw.rounded_rectangle(
        [16, 16, size - 16, size - 16],
        radius=60,
        fill=(24, 24, 27, 255),
        outline=(63, 63, 70, 255),
        width=6,
    )
    # Clean muted dial ring (#52525B)
    draw.ellipse(
        [56, 56, size - 56, size - 56],
        outline=(82, 82, 91, 255),
        width=10,
    )
    # Minimalist crisp off-white hands (#F4F4F5)
    cx, cy = size // 2, size // 2
    draw.line([(cx, cy), (cx, cy - 44)], fill=(244, 244, 245, 255), width=12)
    draw.line([(cx, cy), (cx + 34, cy + 16)], fill=(161, 161, 170, 255), width=10)
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(244, 244, 245, 255))

    img.save(ICON_ICO_PATH, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    img.save(ICON_PNG_PATH, format="PNG")


def create_windows_shortcuts():
    import win32com.client

    python_exe = sys.executable
    pythonw_exe = os.path.join(os.path.dirname(python_exe), "pythonw.exe")
    if not os.path.exists(pythonw_exe):
        pythonw_exe = python_exe

    shell = win32com.client.Dispatch("WScript.Shell")

    desktop = shell.SpecialFolders("Desktop")
    shortcut1 = shell.CreateShortCut(os.path.join(desktop, "Jelly Timer.lnk"))
    shortcut1.Targetpath = pythonw_exe
    shortcut1.Arguments = f'"{SCRIPT_PATH}"'
    shortcut1.WorkingDirectory = PROJECT_DIR
    shortcut1.IconLocation = ICON_ICO_PATH
    shortcut1.Description = "Minimalist floating timer & stopwatch widget"
    shortcut1.save()

    start_menu = shell.SpecialFolders("Programs")
    shortcut2 = shell.CreateShortCut(os.path.join(start_menu, "Jelly Timer.lnk"))
    shortcut2.Targetpath = pythonw_exe
    shortcut2.Arguments = f'"{SCRIPT_PATH}"'
    shortcut2.WorkingDirectory = PROJECT_DIR
    shortcut2.IconLocation = ICON_ICO_PATH
    shortcut2.Description = "Minimalist floating timer & stopwatch widget"
    shortcut2.save()

    print(f"[Windows] Updated Desktop & Start Menu shortcuts for Jelly Timer")


def create_linux_shortcuts():
    desktop_entry = f"""[Desktop Entry]
Type=Application
Name=Jelly Timer
Comment=Minimalist floating timer & stopwatch widget
Exec="{sys.executable}" "{SCRIPT_PATH}"
Path={PROJECT_DIR}
Icon={ICON_PNG_PATH}
Terminal=false
Categories=Utility;Clock;
StartupNotify=false
"""
    apps_dir = os.path.expanduser("~/.local/share/applications")
    os.makedirs(apps_dir, exist_ok=True)
    app_file = os.path.join(apps_dir, "jelly-timer.desktop")
    with open(app_file, "w", encoding="utf-8") as f:
        f.write(desktop_entry)
    os.chmod(app_file, os.stat(app_file).st_mode | stat.S_IEXEC)


def create_macos_shortcuts():
    desktop_dir = os.path.expanduser("~/Desktop")
    cmd_file = os.path.join(desktop_dir, "Jelly Timer.command")
    script_content = f"""#!/bin/bash
cd "{PROJECT_DIR}"
nohup "{sys.executable}" "{SCRIPT_PATH}" >/dev/null 2>&1 &
"""
    with open(cmd_file, "w", encoding="utf-8") as f:
        f.write(script_content)
    os.chmod(cmd_file, os.stat(cmd_file).st_mode | stat.S_IEXEC)


def create_shortcuts():
    if os.path.exists(SCRIPT_PY):
        shutil.copyfile(SCRIPT_PY, SCRIPT_PATH)
    if IS_WIN:
        create_windows_shortcuts()
    elif IS_LINUX:
        create_linux_shortcuts()
    elif IS_MAC:
        create_macos_shortcuts()


if __name__ == "__main__":
    create_icon()
    create_shortcuts()
