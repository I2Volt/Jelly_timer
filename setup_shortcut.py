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
    """Minimalist Linear/Apple-style monochrome dark graphite jellyfish-clock icon."""
    from PyQt6.QtGui import QImage, QPainter, QColor, QPen, QPainterPath
    from PyQt6.QtCore import Qt, QRectF, QPointF

    base_size = 1024
    s = base_size / 256.0
    qimg = QImage(base_size, base_size, QImage.Format.Format_ARGB32)
    qimg.fill(Qt.GlobalColor.transparent)
    p = QPainter(qimg)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    p.setBrush(QColor(24, 24, 27))
    p.setPen(QPen(QColor(72, 72, 80), 6.0 * s))
    p.drawRoundedRect(QRectF(16 * s, 16 * s, 224 * s, 224 * s), 60 * s, 60 * s)

    cx, cy = 128.0, 111.0
    r = 62.0
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(QColor(135, 135, 148, 230), 7.2 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

    for sx, c1x, c1y, c2x, c2y, ex, ey in [
        (99, 88, 183, 105, 200, 93, 216),
        (128, 117, 191, 139, 207, 127, 224),
        (157, 147, 183, 165, 200, 153, 216),
    ]:
        sy = 173 if sx == 128 else 166
        path = QPainterPath(QPointF(sx * s, sy * s))
        path.cubicTo(QPointF(c1x * s, c1y * s), QPointF(c2x * s, c2y * s), QPointF(ex * s, ey * s))
        p.drawPath(path)

    p.setPen(QPen(QColor(170, 170, 180), 10.5 * s))
    p.drawEllipse(QPointF(cx * s, cy * s), r * s, r * s)

    p.setPen(QPen(QColor(161, 161, 170), 10.0 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawLine(QPointF(cx * s, cy * s), QPointF((cx + 33) * s, (cy + 16) * s))

    p.setPen(QPen(QColor(244, 244, 245), 12.0 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawLine(QPointF(cx * s, cy * s), QPointF(cx * s, (cy - 40) * s))

    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(244, 244, 245))
    p.drawEllipse(QPointF(cx * s, cy * s), 8.2 * s, 8.2 * s)
    p.end()

    q256 = qimg.scaled(256, 256, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    q256.save(ICON_PNG_PATH)
    img = Image.open(ICON_PNG_PATH).convert("RGBA")
    img.save(ICON_ICO_PATH, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    shutil.copy2(ICON_ICO_PATH, os.path.join(PROJECT_DIR, "jelly_timer_v2.ico"))


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
