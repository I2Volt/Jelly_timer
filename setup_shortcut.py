import os
import sys
import stat
import platform
from PIL import Image, ImageDraw

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_ICO_PATH = os.path.join(PROJECT_DIR, "jelly_timer.ico")
ICON_PNG_PATH = os.path.join(PROJECT_DIR, "jelly_timer.png")
SCRIPT_PATH = os.path.join(PROJECT_DIR, "jelly_timer.pyw")

OS_NAME = platform.system()  # "Windows", "Darwin" (macOS), "Linux"
IS_WIN = (OS_NAME == "Windows")
IS_MAC = (OS_NAME == "Darwin")
IS_LINUX = (OS_NAME == "Linux")


def create_icon():
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Outer glowing rounded box
    draw.rounded_rectangle(
        [16, 16, size - 16, size - 16],
        radius=64,
        fill=(18, 24, 38, 255),
        outline=(0, 229, 255, 255),
        width=10,
    )
    # Inner accent ring
    draw.ellipse(
        [52, 58, size - 52, size - 46],
        outline=(110, 86, 255, 255),
        width=14,
    )
    # Clock hands
    cx, cy = size // 2, size // 2 + 6
    draw.line([(cx, cy), (cx, cy - 48)], fill=(0, 229, 255, 255), width=14)
    draw.line([(cx, cy), (cx + 38, cy + 16)], fill=(255, 255, 255, 255), width=12)
    # Top stopwatch crown
    draw.rounded_rectangle(
        [cx - 22, 30, cx + 22, 46], radius=6, fill=(0, 229, 255, 255)
    )

    img.save(ICON_ICO_PATH, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
    img.save(ICON_PNG_PATH, format="PNG")


def create_windows_shortcuts():
    import win32com.client

    python_exe = sys.executable
    pythonw_exe = os.path.join(os.path.dirname(python_exe), "pythonw.exe")
    if not os.path.exists(pythonw_exe):
        pythonw_exe = python_exe

    shell = win32com.client.Dispatch("WScript.Shell")

    # 1. Desktop shortcut
    desktop = shell.SpecialFolders("Desktop")
    shortcut1 = shell.CreateShortCut(os.path.join(desktop, "Jelly Timer.lnk"))
    shortcut1.Targetpath = pythonw_exe
    shortcut1.Arguments = f'"{SCRIPT_PATH}"'
    shortcut1.WorkingDirectory = PROJECT_DIR
    shortcut1.IconLocation = ICON_ICO_PATH
    shortcut1.Description = "Minimalist floating timer & stopwatch widget"
    shortcut1.save()

    # 2. Start Menu Programs shortcut
    start_menu = shell.SpecialFolders("Programs")
    shortcut2 = shell.CreateShortCut(os.path.join(start_menu, "Jelly Timer.lnk"))
    shortcut2.Targetpath = pythonw_exe
    shortcut2.Arguments = f'"{SCRIPT_PATH}"'
    shortcut2.WorkingDirectory = PROJECT_DIR
    shortcut2.IconLocation = ICON_ICO_PATH
    shortcut2.Description = "Minimalist floating timer & stopwatch widget"
    shortcut2.save()

    print(f"[Windows] Created Desktop shortcut: {os.path.join(desktop, 'Jelly Timer.lnk')}")
    print(f"[Windows] Created Start Menu shortcut: {os.path.join(start_menu, 'Jelly Timer.lnk')}")


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
    print(f"[Linux] Created application menu shortcut: {app_file}")

    desktop_dir = os.path.expanduser("~/Desktop")
    if os.path.isdir(desktop_dir):
        desk_file = os.path.join(desktop_dir, "Jelly Timer.desktop")
        with open(desk_file, "w", encoding="utf-8") as f:
            f.write(desktop_entry)
        os.chmod(desk_file, os.stat(desk_file).st_mode | stat.S_IEXEC)
        print(f"[Linux] Created Desktop shortcut: {desk_file}")


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
    print(f"[macOS] Created Desktop launcher: {cmd_file}")


def create_shortcuts():
    if IS_WIN:
        create_windows_shortcuts()
    elif IS_LINUX:
        create_linux_shortcuts()
    elif IS_MAC:
        create_macos_shortcuts()
    else:
        print(f"Unsupported OS for shortcut creation: {OS_NAME}")


if __name__ == "__main__":
    create_icon()
    create_shortcuts()
