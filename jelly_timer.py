import sys
import math
import json
import os
import time
import platform
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMenu, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QByteArray, pyqtSignal, QObject
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QFont, QFontMetricsF, QPainterPath, QKeySequence, QPixmap
)
from PyQt6.QtSvg import QSvgRenderer

try:
    from pynput import keyboard as pynput_kb
    HAS_PYNPUT = True
except Exception:
    HAS_PYNPUT = False

OS_NAME = platform.system()  # "Windows", "Darwin" (macOS), "Linux"
IS_WIN = (OS_NAME == "Windows")
IS_MAC = (OS_NAME == "Darwin")
IS_LINUX = (OS_NAME == "Linux")

if IS_WIN:
    import ctypes
    import winsound
    HWND_TOPMOST = -1
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_NOACTIVATE = 0x0010
    SWP_SHOWWINDOW = 0x0040

# System-native clean UI font family
UI_FONT = "SF Pro Display" if IS_MAC else ("Ubuntu" if IS_LINUX else "Segoe UI")

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def play_system_alarm():
    """Cross-platform non-blocking alarm sound for Windows, macOS, and Linux."""
    if IS_WIN:
        try:
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
            return
        except Exception:
            pass
    elif IS_MAC:
        try:
            subprocess.Popen(["afplay", "/System/Library/Sounds/Glass.aiff"])
            return
        except Exception:
            pass
    elif IS_LINUX:
        for cmd in (
            ["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
            ["aplay", "/usr/share/sounds/alsa/Front_Center.wav"],
        ):
            try:
                subprocess.Popen(cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                return
            except Exception:
                pass
    QApplication.beep()


# Standard Lucide SVG vector paths (24x24 viewBox)
LUCIDE_SVGS = {
    "play": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="6 3 20 12 6 21 6 3"/></svg>',
    "pause": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg>',
    "reset": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>',
    "timer": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 22h14"/><path d="M5 2h14"/><path d="M17 22v-4.172a2 2 0 0 0-.586-1.414L12 12l-4.414 4.414A2 2 0 0 0 7 17.828V22"/><path d="M7 2v4.172a2 2 0 0 0 .586 1.414L12 12l4.414-4.414A2 2 0 0 0 17 6.172V2"/></svg>',
    "stopwatch": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="10" x2="14" y1="2" y2="2"/><line x1="12" x2="15" y1="14" y2="11"/><circle cx="12" cy="14" r="8"/></svg>',
    "swap": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m7 15 5 5 5-5"/><path d="m7 9 5-5 5 5"/></svg>',
    "expand": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" x2="14" y1="3" y2="10"/><line x1="3" x2="10" y1="21" y2="14"/></svg>',
    "close": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>',
    "opacity": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 18a6 6 0 0 0 0-12v12z" fill="{color}"/></svg>',
    "keyboard": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="M6 8h.01"/><path d="M10 8h.01"/><path d="M14 8h.01"/><path d="M18 8h.01"/><path d="M8 12h.01"/><path d="M12 12h.01"/><path d="M16 12h.01"/><path d="M7 16h10"/></svg>',
}

_svg_cache = {}


def render_svg_icon(painter: QPainter, name: str, rect: QRectF, color: QColor):
    svg_template = LUCIDE_SVGS.get(name)
    if not svg_template:
        return
    hex_col = color.name(QColor.NameFormat.HexRgb)
    key = (name, hex_col)
    if key not in _svg_cache:
        xml = svg_template.format(color=hex_col).encode("utf-8")
        _svg_cache[key] = QSvgRenderer(QByteArray(xml))

    painter.save()
    painter.setOpacity(color.alphaF())
    _svg_cache[key].render(painter, rect)
    painter.restore()


class CrossPlatformHotkeyMonitor(QObject):
    """
    Universal background hotkey listener supporting Windows, macOS, and Linux.
    Works even when browser or another fullscreen app is focused!
    """
    hotkey_triggered = pyqtSignal(str)

    def __init__(self, widget):
        super().__init__(widget)
        self.w = widget
        self.held_tokens = set()
        self.listener = None

        if not IS_WIN and HAS_PYNPUT:
            try:
                self.listener = pynput_kb.Listener(
                    on_press=self._on_pynput_press,
                    on_release=self._on_pynput_release
                )
                self.listener.daemon = True
                self.listener.start()
            except Exception:
                self.listener = None

    def _normalize_pynput_key(self, key):
        try:
            if isinstance(key, pynput_kb.Key):
                name_map = {
                    pynput_kb.Key.space: "Space",
                    pynput_kb.Key.enter: "Enter",
                    pynput_kb.Key.tab: "Tab",
                    pynput_kb.Key.backspace: "Backspace",
                    pynput_kb.Key.esc: "Esc",
                    pynput_kb.Key.up: "Up",
                    pynput_kb.Key.down: "Down",
                    pynput_kb.Key.left: "Left",
                    pynput_kb.Key.right: "Right",
                    pynput_kb.Key.shift_l: "Left Shift",
                    pynput_kb.Key.shift_r: "Right Shift",
                    pynput_kb.Key.ctrl_l: "Left Ctrl",
                    pynput_kb.Key.ctrl_r: "Right Ctrl",
                    pynput_kb.Key.alt_l: "Left Alt",
                    pynput_kb.Key.alt_r: "Right Alt",
                    pynput_kb.Key.alt_gr: "Right Alt",
                    pynput_kb.Key.cmd_l: "Left Cmd",
                    pynput_kb.Key.cmd_r: "Right Cmd",
                }
                if key in name_map:
                    return name_map[key]
                if key.name and key.name.startswith("f") and key.name[1:].isdigit():
                    return key.name.upper()
            elif hasattr(key, "char") and key.char:
                return key.char.upper()
        except Exception:
            pass
        return None

    def _on_pynput_press(self, key):
        if self.w.editing_time:
            return
        if not self.w.global_hotkeys and not (self.w.underMouse() or self.w.isActiveWindow()):
            return
        token = self._normalize_pynput_key(key)
        if not token or token in self.held_tokens:
            return
        self.held_tokens.add(token)

        # Prevent combos like Alt+Tab or Cmd+Tab from firing single-key hotkeys
        mod_tokens = {"Left Shift", "Right Shift", "Left Ctrl", "Right Ctrl", "Left Alt", "Right Alt", "Left Cmd", "Right Cmd"}
        other_mods = (self.held_tokens & mod_tokens) - {token}
        if other_mods:
            return

        for action_key, hk in self.w.hotkeys.items():
            if hk.get("name", "").upper() == token.upper():
                self.hotkey_triggered.emit(action_key)

    def _on_pynput_release(self, key):
        token = self._normalize_pynput_key(key)
        if token and token in self.held_tokens:
            self.held_tokens.discard(token)


class SpringValue:
    def __init__(self, value=0.0, stiffness=260.0, damping=20.0):
        self.value = float(value)
        self.target = float(value)
        self.velocity = 0.0
        self.stiffness = stiffness
        self.damping = damping

    def step(self, dt):
        dt = min(dt, 0.04)
        force = (self.target - self.value) * self.stiffness
        self.velocity += force * dt
        self.velocity *= math.exp(-self.damping * dt)
        self.value += self.velocity * dt
        if abs(self.target - self.value) < 0.0015 and abs(self.velocity) < 0.015:
            self.value = self.target
            self.velocity = 0.0

    def set_immediate(self, val):
        self.value = float(val)
        self.target = float(val)
        self.velocity = 0.0


class SnapPreviewWindow(QWidget):
    """Subtle desktop snap zone indicator when dragging near edges."""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        self.sp_x = SpringValue(0, 340, 26)
        self.sp_y = SpringValue(0, 340, 26)
        self.sp_w = SpringValue(100, 340, 26)
        self.sp_h = SpringValue(100, 340, 26)
        self.sp_alpha = SpringValue(0.0, 280, 24)
        self.active = False

    def show_zone(self, rect: QRectF):
        if not self.active:
            self.active = True
            cx, cy = rect.center().x(), rect.center().y()
            self.sp_x.set_immediate(cx - rect.width() * 0.4)
            self.sp_y.set_immediate(cy - rect.height() * 0.4)
            self.sp_w.set_immediate(rect.width() * 0.8)
            self.sp_h.set_immediate(rect.height() * 0.8)
            self.show()

        self.sp_x.target = rect.x()
        self.sp_y.target = rect.y()
        self.sp_w.target = rect.width()
        self.sp_h.target = rect.height()
        self.sp_alpha.target = 1.0

    def hide_zone(self):
        self.active = False
        self.sp_alpha.target = 0.0

    def step_animation(self, dt):
        self.sp_x.step(dt)
        self.sp_y.step(dt)
        self.sp_w.step(dt)
        self.sp_h.step(dt)
        self.sp_alpha.step(dt)

        if self.sp_alpha.value < 0.02 and not self.active:
            if self.isVisible():
                self.hide()
            return

        pad = 10
        gx = int(self.sp_x.value - pad)
        gy = int(self.sp_y.value - pad)
        gw = int(max(20, self.sp_w.value + pad * 2))
        gh = int(max(20, self.sp_h.value + pad * 2))
        self.setGeometry(gx, gy, gw, gh)
        self.update()

    def paintEvent(self, event):
        a = max(0.0, min(1.0, self.sp_alpha.value))
        if a <= 0.01:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        pad = 10
        rect = QRectF(pad, pad, self.width() - pad * 2, self.height() - pad * 2)
        radius = min(14.0, rect.height() * 0.28)

        fill_color = QColor(255, 255, 255, int(28 * a))
        border_color = QColor(255, 255, 255, int(130 * a))

        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        painter.fillPath(path, fill_color)

        pen = QPen(border_color, 1.5, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawPath(path)


class KeyCaptureButton(QPushButton):
    QT_KEY_TO_VK = {
        Qt.Key.Key_Space: (0x20, "Space"),
        Qt.Key.Key_Return: (0x0D, "Enter"),
        Qt.Key.Key_Enter: (0x0D, "Enter"),
        Qt.Key.Key_Tab: (0x09, "Tab"),
        Qt.Key.Key_Backtab: (0x09, "Tab"),
        Qt.Key.Key_Backspace: (0x08, "Backspace"),
        Qt.Key.Key_Escape: (0x1B, "Esc"),
        Qt.Key.Key_Insert: (0x2D, "Insert"),
        Qt.Key.Key_Delete: (0x2E, "Delete"),
        Qt.Key.Key_Home: (0x24, "Home"),
        Qt.Key.Key_End: (0x23, "End"),
        Qt.Key.Key_PageUp: (0x21, "PageUp"),
        Qt.Key.Key_PageDown: (0x22, "PageDown"),
        Qt.Key.Key_Up: (0x26, "Up"),
        Qt.Key.Key_Down: (0x28, "Down"),
        Qt.Key.Key_Left: (0x25, "Left"),
        Qt.Key.Key_Right: (0x27, "Right"),
        Qt.Key.Key_Plus: (0xBB, "+"),
        Qt.Key.Key_Equal: (0xBB, "="),
        Qt.Key.Key_Minus: (0xBD, "-"),
    }

    def __init__(self, vk_code, key_name, parent=None):
        super().__init__(key_name, parent)
        self.vk_code = vk_code
        self.key_name = key_name
        self.listening = False
        self.pending_modifier_vk = None
        self.clicked.connect(self.start_listening)
        self.update_style()

    def update_style(self):
        if self.listening:
            self.setText("Нажмите клавишу...")
            self.setStyleSheet("""
                QPushButton {
                    background-color: #E4E4E7;
                    color: #18181B;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: 600;
                }
            """)
        else:
            self.setText(self.key_name)
            self.setStyleSheet("""
                QPushButton {
                    background-color: #27272A;
                    color: #F4F4F5;
                    border: 1px solid #3F3F46;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #3F3F46;
                }
            """)

    def start_listening(self):
        self.listening = True
        self.pending_modifier_vk = None
        self.update_style()
        self.setFocus()

    def detect_exact_modifier_vk(self, qt_key, event):
        """Detects exact Left or Right Ctrl/Alt/Shift across Windows, macOS, and Linux."""
        if IS_WIN:
            u32 = ctypes.windll.user32
            if qt_key == Qt.Key.Key_Control:
                if u32.GetAsyncKeyState(0xA3) & 0x8000:
                    return 0xA3, "Right Ctrl"
                return 0xA2, "Left Ctrl"
            if qt_key == Qt.Key.Key_Alt:
                if u32.GetAsyncKeyState(0xA5) & 0x8000:
                    return 0xA5, "Right Alt"
                return 0xA4, "Left Alt"
            if qt_key == Qt.Key.Key_Shift:
                if u32.GetAsyncKeyState(0xA1) & 0x8000:
                    return 0xA1, "Right Shift"
                return 0xA0, "Left Shift"
        else:
            # macOS / Linux native scan codes / virtual keys
            sc = event.nativeScanCode()
            vk = event.nativeVirtualKey()
            if qt_key == Qt.Key.Key_Control:
                if sc in (105, 62) or vk in (0xFFE4, 62):
                    return 0xA3, "Right Ctrl"
                return 0xA2, "Left Ctrl"
            if qt_key in (Qt.Key.Key_Alt, Qt.Key.Key_AltGr):
                if qt_key == Qt.Key.Key_AltGr or sc in (108, 61) or vk in (0xFFEA, 0xFE03, 61):
                    return 0xA5, "Right Alt"
                return 0xA4, "Left Alt"
            if qt_key == Qt.Key.Key_Shift:
                if sc in (62, 60) or vk in (0xFFE2, 60):
                    return 0xA1, "Right Shift"
                return 0xA0, "Left Shift"
        return None, None

    def keyPressEvent(self, event):
        if not self.listening:
            super().keyPressEvent(event)
            return

        key = event.key()
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_AltGr, Qt.Key.Key_Shift):
            vk, name = self.detect_exact_modifier_vk(key, event)
            if vk:
                self.pending_modifier_vk = (vk, name)
            return

        if key == Qt.Key.Key_Meta:
            return

        self.pending_modifier_vk = None
        vk = None
        name = None
        if key in self.QT_KEY_TO_VK:
            vk, name = self.QT_KEY_TO_VK[key]
        elif Qt.Key.Key_F1 <= key <= Qt.Key.Key_F12:
            idx = key - Qt.Key.Key_F1
            vk = 0x70 + idx
            name = f"F{idx + 1}"
        elif Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            vk = int(key)
            name = chr(vk)
        elif Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
            vk = int(key)
            name = chr(vk)
        else:
            native_vk = event.nativeVirtualKey()
            if native_vk > 0:
                vk = native_vk
                name = QKeySequence(key).toString() or f"VK_{vk}"

        if vk:
            self.vk_code = vk
            self.key_name = name
        self.listening = False
        self.update_style()

    def keyReleaseEvent(self, event):
        if self.listening and self.pending_modifier_vk:
            key = event.key()
            if key in (Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_AltGr, Qt.Key.Key_Shift):
                self.vk_code, self.key_name = self.pending_modifier_vk
                self.pending_modifier_vk = None
                self.listening = False
                self.update_style()
                return
        super().keyReleaseEvent(event)


class SettingsDialog(QDialog):
    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.w = parent_widget
        self.setWindowTitle("Настройки")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowCloseButtonHint)
        self.setFixedSize(350, 320)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #18181B;
                color: #F4F4F5;
                font-family: '{UI_FONT}';
            }}
            QLabel {{
                color: #D4D4D8;
                font-size: 13px;
            }}
            QCheckBox {{
                color: #E4E4E7;
                font-size: 12px;
                spacing: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Горячие клавиши")
        title.setStyleSheet("font-size: 14px; font-weight: 600; color: #FAFAFA;")
        layout.addWidget(title)

        self.buttons = {}
        rows = [
            ("play_pause", "Старт / Пауза:"),
            ("reset", "Сброс:"),
            ("switch_mode", "Таймер / Секундомер:"),
            ("cycle_size", "Размер окна:"),
        ]

        for k, label_text in rows:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            hk = self.w.hotkeys[k]
            btn = KeyCaptureButton(hk["vk"], hk["name"], self)
            btn.setFixedWidth(135)
            self.buttons[k] = btn
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(btn)
            layout.addLayout(row)

        self.global_cb = QCheckBox("Работать поверх любых окон (в браузере и играх)")
        self.global_cb.setChecked(self.w.global_hotkeys)
        layout.addWidget(self.global_cb)

        op_row = QHBoxLayout()
        op_lbl = QLabel("Прозрачность:")
        self.op_slider = QSlider(Qt.Orientation.Horizontal)
        self.op_slider.setRange(20, 100)
        self.op_slider.setValue(int(self.w.bg_opacity * 100))
        self.op_slider.valueChanged.connect(self.on_opacity_change)
        op_row.addWidget(op_lbl)
        op_row.addWidget(self.op_slider)
        layout.addLayout(op_row)

        layout.addStretch()

        save_btn = QPushButton("Сохранить")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #F4F4F5;
                color: #18181B;
                font-weight: 600;
                font-size: 13px;
                border-radius: 6px;
                padding: 7px;
            }
            QPushButton:hover {
                background-color: #FFFFFF;
            }
        """)
        save_btn.clicked.connect(self.save_and_close)
        layout.addWidget(save_btn)

    def on_opacity_change(self, val):
        self.w.bg_opacity = val / 100.0
        self.w.save_config()

    def save_and_close(self):
        for k, btn in self.buttons.items():
            self.w.hotkeys[k] = {"vk": btn.vk_code, "name": btn.key_name}
        self.w.global_hotkeys = self.global_cb.isChecked()
        self.w.save_config()
        self.accept()


class JellyTimerWidget(QWidget):
    SIZES = {
        "mini":   (208, 66),
        "medium": (284, 138),
        "large":  (348, 195),
    }

    THEMES = {
        "graphite": {
            "name": "Тёмный графит",
            "bg": (24, 24, 27),
            "border": (63, 63, 70),
            "primary_bg": (244, 244, 245),
            "primary_fg": (24, 24, 27),
            "text": (250, 250, 250),
            "muted": (161, 161, 170),
        },
        "warm_espresso": {
            "name": "Тёплый эспрессо",
            "bg": (28, 25, 23),
            "border": (68, 64, 60),
            "primary_bg": (245, 245, 244),
            "primary_fg": (28, 25, 23),
            "text": (250, 250, 249),
            "muted": (168, 162, 158),
        },
        "soft_sage": {
            "name": "Мягкий шалфей",
            "bg": (22, 27, 24),
            "border": (55, 68, 60),
            "primary_bg": (215, 235, 222),
            "primary_fg": (20, 26, 22),
            "text": (242, 248, 244),
            "muted": (148, 168, 155),
        },
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Timer")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.mode = "timer"
        self.size_mode = "medium"
        self.theme_key = "graphite"
        self.bg_opacity = 0.88
        self.snap_enabled = True
        # Enabled by default so hotkeys work immediately even when browser tab is focused!
        self.global_hotkeys = True

        self.hotkeys = {
            "play_pause":  {"vk": 0x20, "name": "Space"},
            "reset":       {"vk": 0x52, "name": "R"},
            "switch_mode": {"vk": 0x4D, "name": "M"},
            "cycle_size":  {"vk": 0x53, "name": "S"},
        }
        self.prev_vk_state = {}

        self.timer_total = 25 * 60.0
        self.timer_remaining = 25 * 60.0
        self.stopwatch_elapsed = 0.0
        self.is_running = False
        self.last_tick_time = time.perf_counter()
        self.alarm_flash = 0.0

        self.editing_time = False
        self.edit_text = ""
        self.edit_cursor = 0
        self.time_display_rect = QRectF()

        self.load_config()
        if self.theme_key not in self.THEMES:
            self.theme_key = "graphite"

        self.canvas_pad = 34
        w, h = self.SIZES[self.size_mode]

        screen = QApplication.primaryScreen().availableGeometry()
        init_x = getattr(self, "saved_x", float(screen.right() - w - 12))
        init_y = getattr(self, "saved_y", float(screen.top() + 60))

        self.sp_x = SpringValue(init_x, stiffness=380.0, damping=30.0)
        self.sp_y = SpringValue(init_y, stiffness=380.0, damping=30.0)
        self.sp_w = SpringValue(w, stiffness=320.0, damping=26.0)
        self.sp_h = SpringValue(h, stiffness=320.0, damping=26.0)

        self.sp_scale_x = SpringValue(1.0, stiffness=280.0, damping=16.5)
        self.sp_scale_y = SpringValue(1.0, stiffness=280.0, damping=16.5)

        self.dock_edge = self.compute_snap_candidate(init_x, init_y, w, h)[0]
        self.detaching_from_edge = None
        self.detach_anchor_pos = QPointF(init_x, init_y)

        self.snap_preview = SnapPreviewWindow()

        self.dragging = False
        self.drag_offset = QPointF(0, 0)
        self.hovered_btn = None
        self.interactive_rects = {}
        self.topmost_counter = 0

        # Cross-platform background hotkey listener (macOS / Linux via pynput, Windows via Win32)
        self.hk_monitor = CrossPlatformHotkeyMonitor(self)
        self.hk_monitor.hotkey_triggered.connect(self.execute_hotkey_action)

        self.update_window_geometry(force=True)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.on_frame)
        self.anim_timer.start(16)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.mode = data.get("mode", self.mode)
                self.size_mode = data.get("size_mode", self.size_mode)
                self.theme_key = data.get("theme_key", self.theme_key)
                self.bg_opacity = float(data.get("bg_opacity", self.bg_opacity))
                self.snap_enabled = bool(data.get("snap_enabled", self.snap_enabled))
                # Migrate to True unless explicitly disabled in new config version
                if "global_hotkeys_v2" in data:
                    self.global_hotkeys = bool(data["global_hotkeys_v2"])
                else:
                    self.global_hotkeys = True
                self.timer_total = float(data.get("timer_total", self.timer_total))
                self.timer_remaining = self.timer_total
                if "hotkeys" in data:
                    for k, v in data["hotkeys"].items():
                        if k in self.hotkeys and "vk" in v and "name" in v:
                            if k == "switch_mode" and v.get("vk") == 0x09:
                                continue
                            self.hotkeys[k] = v
                if "x" in data and "y" in data:
                    self.saved_x = float(data["x"])
                    self.saved_y = float(data["y"])
            except Exception:
                pass

    def save_config(self):
        try:
            data = {
                "mode": self.mode,
                "size_mode": self.size_mode,
                "theme_key": self.theme_key,
                "bg_opacity": self.bg_opacity,
                "snap_enabled": self.snap_enabled,
                "global_hotkeys_v2": self.global_hotkeys,
                "hotkeys": self.hotkeys,
                "timer_total": self.timer_total,
                "x": self.sp_x.target,
                "y": self.sp_y.target,
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def enforce_topmost_crossplatform(self):
        """Keeps widget above fullscreen/active browsers across Windows, macOS, and Linux."""
        if IS_WIN:
            try:
                hwnd = int(self.winId())
                ctypes.windll.user32.SetWindowPos(
                    hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
                )
            except Exception:
                pass
        else:
            # On macOS / Linux X11/Wayland, raise_() on a WindowStaysOnTopHint Tool window keeps it elevated
            self.raise_()

    def trigger_jelly(self, vx=0.0, vy=0.0):
        self.sp_scale_x.velocity += vx
        self.sp_scale_y.velocity += vy

    def compute_snap_candidate(self, x, y, w, h, cursor_pt=None):
        if not self.snap_enabled:
            return None, None

        ref_pt = cursor_pt.toPoint() if cursor_pt is not None else QPointF(x + w / 2, y + h / 2).toPoint()
        screen = QApplication.screenAt(ref_pt)
        if not screen:
            screen = QApplication.primaryScreen()
        sg = screen.availableGeometry()

        snap_dist = 48
        margin = 8

        cx = cursor_pt.x() if cursor_pt is not None else (x + w / 2)
        cy = cursor_pt.y() if cursor_pt is not None else (y + h / 2)

        near_left = (x <= sg.left() + snap_dist) or (cx <= sg.left() + snap_dist)
        near_right = (x + w >= sg.right() - snap_dist) or (cx >= sg.right() - snap_dist)
        near_top = (y <= sg.top() + snap_dist) or (cy <= sg.top() + snap_dist)
        near_bottom = (y + h >= sg.bottom() - snap_dist) or (cy >= sg.bottom() - snap_dist)

        if not (near_left or near_right or near_top or near_bottom):
            return None, None

        tx = max(sg.left() + margin, min(x, sg.right() - w - margin))
        ty = max(sg.top() + margin, min(y, sg.bottom() - h - margin))

        h_edge = None
        v_edge = None

        if near_left:
            tx = sg.left() + margin
            h_edge = "left"
        elif near_right:
            tx = sg.right() - w - margin
            h_edge = "right"

        if near_top:
            ty = sg.top() + margin
            v_edge = "top"
        elif near_bottom:
            ty = sg.bottom() - h - margin
            v_edge = "bottom"

        if v_edge and h_edge:
            edge = f"{v_edge}_{h_edge}"
        else:
            edge = h_edge or v_edge

        return edge, QRectF(tx, ty, w, h)

    def get_docked_target_pos(self, edge, cur_x, cur_y, old_w, old_h, new_w, new_h):
        screen = QApplication.screenAt(QPointF(cur_x + old_w / 2, cur_y + old_h / 2).toPoint())
        if not screen:
            screen = QApplication.primaryScreen()
        sg = screen.availableGeometry()
        margin = 8

        tx = cur_x + (old_w - new_w) / 2.0
        ty = cur_y + (old_h - new_h) / 2.0

        if "left" in edge:
            tx = sg.left() + margin
        elif "right" in edge:
            tx = sg.right() - new_w - margin

        if "top" in edge:
            ty = sg.top() + margin
        elif "bottom" in edge:
            ty = sg.bottom() - new_h - margin

        tx = max(sg.left() + margin, min(tx, sg.right() - new_w - margin))
        ty = max(sg.top() + margin, min(ty, sg.bottom() - new_h - margin))
        return tx, ty

    def is_other_modifier_pressed_win32(self, allowed_vk):
        u32 = ctypes.windll.user32
        mod_groups = [
            (0xA0, 0xA1, 0x10),
            (0xA2, 0xA3, 0x11),
            (0xA4, 0xA5, 0x12),
            (0x5B, 0x5C),
        ]
        for group in mod_groups:
            if allowed_vk in group:
                continue
            for m_vk in group[:2]:
                if (u32.GetAsyncKeyState(m_vk) & 0x8000) != 0:
                    return True
        return False

    def poll_hotkeys_win32(self):
        if not IS_WIN:
            return
        if self.editing_time:
            self.prev_vk_state.clear()
            return

        active_ok = self.global_hotkeys or self.underMouse() or self.isActiveWindow()
        if not active_ok:
            self.prev_vk_state.clear()
            return

        u32 = ctypes.windll.user32
        for action_key, hk in self.hotkeys.items():
            vk = hk.get("vk", 0)
            if not vk:
                continue
            state = u32.GetAsyncKeyState(vk)
            is_down = (state & 0x8000) != 0
            was_down = self.prev_vk_state.get(vk, False)

            if is_down and not was_down:
                if not self.is_other_modifier_pressed_win32(vk):
                    self.execute_hotkey_action(action_key)
            self.prev_vk_state[vk] = is_down

    def execute_hotkey_action(self, action_key):
        if action_key == "play_pause":
            self.toggle_play()
        elif action_key == "reset":
            self.reset_clock()
        elif action_key == "switch_mode":
            self.switch_mode()
        elif action_key == "cycle_size":
            self.cycle_size()

    def on_frame(self):
        now = time.perf_counter()
        real_dt = now - self.last_tick_time
        self.last_tick_time = now

        self.topmost_counter += 1
        if self.topmost_counter >= 90:
            self.topmost_counter = 0
            self.enforce_topmost_crossplatform()

        if IS_WIN:
            self.poll_hotkeys_win32()

        if self.is_running:
            if self.mode == "timer":
                self.timer_remaining -= real_dt
                if self.timer_remaining <= 0.0:
                    self.timer_remaining = 0.0
                    self.is_running = False
                    self.alarm_flash = 4.0
                    play_system_alarm()
            else:
                self.stopwatch_elapsed += real_dt

        if self.alarm_flash > 0:
            self.alarm_flash = max(0.0, self.alarm_flash - real_dt)

        phys_dt = min(real_dt, 0.035)
        self.sp_x.step(phys_dt)
        self.sp_y.step(phys_dt)
        self.sp_w.step(phys_dt)
        self.sp_h.step(phys_dt)
        self.sp_scale_x.step(phys_dt)
        self.sp_scale_y.step(phys_dt)
        self.snap_preview.step_animation(phys_dt)

        self.update_window_geometry()
        self.update()

    def update_window_geometry(self, force=False):
        pad = self.canvas_pad
        win_x = int(round(self.sp_x.value - pad))
        win_y = int(round(self.sp_y.value - pad))
        win_w = int(round(self.sp_w.value + pad * 2))
        win_h = int(round(self.sp_h.value + pad * 2))

        if force or self.x() != win_x or self.y() != win_y or self.width() != win_w or self.height() != win_h:
            self.setGeometry(win_x, win_y, win_w, win_h)

    def set_size_mode(self, mode):
        if mode not in self.SIZES:
            return
        old_w, old_h = self.sp_w.target, self.sp_h.target
        self.size_mode = mode
        w, h = self.SIZES[mode]
        self.sp_w.target = w
        self.sp_h.target = h
        if self.dock_edge:
            tx, ty = self.get_docked_target_pos(
                self.dock_edge, self.sp_x.target, self.sp_y.target, old_w, old_h, w, h
            )
            self.sp_x.target = tx
            self.sp_y.target = ty
        self.save_config()

    def switch_mode(self, new_mode=None):
        self.commit_time_edit()
        if new_mode is None:
            self.mode = "stopwatch" if self.mode == "timer" else "timer"
        else:
            self.mode = new_mode
        self.is_running = False
        self.save_config()

    def adjust_timer(self, delta_seconds):
        self.commit_time_edit()
        if self.mode != "timer":
            self.switch_mode("timer")
        self.timer_remaining = max(0.0, min(999 * 3600.0, self.timer_remaining + delta_seconds))
        if not self.is_running or self.timer_remaining > self.timer_total:
            self.timer_total = max(1.0, self.timer_remaining)
        self.save_config()

    def reset_clock(self):
        self.editing_time = False
        self.edit_text = ""
        self.edit_cursor = 0
        self.time_display_rect = QRectF()
        self.is_running = False
        self.alarm_flash = 0.0
        if self.mode == "timer":
            self.timer_remaining = self.timer_total
        else:
            self.stopwatch_elapsed = 0.0

    def toggle_play(self):
        if self.editing_time:
            self.commit_time_edit()
        if self.mode == "timer" and self.timer_remaining <= 0:
            self.timer_remaining = self.timer_total
        self.is_running = not self.is_running
        self.last_tick_time = time.perf_counter()
        self.alarm_flash = 0.0

    def start_time_edit(self, click_x_in_rect=None):
        if self.mode != "timer":
            return
        self.is_running = False
        self.editing_time = True
        self.edit_text = self._seconds_to_str(self.timer_remaining)
        self.edit_cursor = len(self.edit_text)
        self.activateWindow()
        self.setFocus()

    def commit_time_edit(self):
        if not self.editing_time:
            return
        self.editing_time = False
        raw = self.edit_text.strip()
        if not raw:
            return

        total = 0.0
        try:
            if ":" in raw:
                parts = [int(p) if p.strip() else 0 for p in raw.split(":")]
                if len(parts) == 2:
                    total = float(parts[0] * 60 + parts[1])
                elif len(parts) >= 3:
                    total = float(parts[0] * 3600 + parts[1] * 60 + parts[2])
            else:
                # Plain number = minutes (e.g. "25" -> 25:00)
                total = float(int(raw) * 60)
        except Exception:
            total = 0.0

        if total > 0:
            self.timer_total = min(999 * 3600.0, total)
            self.timer_remaining = self.timer_total
            self.save_config()

    def cancel_time_edit(self):
        self.editing_time = False

    def keyPressEvent(self, event):
        if self.editing_time:
            key = event.key()
            text = event.text()

            if key == Qt.Key.Key_Left:
                self.edit_cursor = max(0, self.edit_cursor - 1)
                return
            elif key == Qt.Key.Key_Right:
                self.edit_cursor = min(len(self.edit_text), self.edit_cursor + 1)
                return
            elif key == Qt.Key.Key_Home:
                self.edit_cursor = 0
                return
            elif key == Qt.Key.Key_End:
                self.edit_cursor = len(self.edit_text)
                return
            elif key == Qt.Key.Key_Backspace:
                if self.edit_cursor > 0:
                    self.edit_text = self.edit_text[:self.edit_cursor - 1] + self.edit_text[self.edit_cursor:]
                    self.edit_cursor -= 1
                return
            elif key == Qt.Key.Key_Delete:
                if self.edit_cursor < len(self.edit_text):
                    self.edit_text = self.edit_text[:self.edit_cursor] + self.edit_text[self.edit_cursor + 1:]
                return
            elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.commit_time_edit()
                return
            elif key == Qt.Key.Key_Escape:
                self.cancel_time_edit()
                return
            elif text and (text.isdigit() or text == ":"):
                if len(self.edit_text) < 9:
                    self.edit_text = self.edit_text[:self.edit_cursor] + text + self.edit_text[self.edit_cursor:]
                    self.edit_cursor += 1
                return
            return

        super().keyPressEvent(event)

    def _seconds_to_str(self, seconds):
        seconds = max(0.0, seconds)
        total_sec = int(seconds)
        mins = total_sec // 60
        secs = total_sec % 60
        hrs = mins // 60
        if hrs > 0:
            mins = mins % 60
            return f"{hrs:02d}:{mins:02d}:{secs:02d}"
        if self.mode == "stopwatch":
            tenths = int((seconds - total_sec) * 10)
            return f"{mins:02d}:{secs:02d}.{tenths}"
        return f"{mins:02d}:{secs:02d}"

    def format_time(self, seconds):
        if self.editing_time and self.mode == "timer":
            return self.edit_text
        return self._seconds_to_str(seconds)

    def draw_fitted_time(self, painter: QPainter, rect: QRectF, text_str: str, max_pt: int, color: QColor, align=Qt.AlignmentFlag.AlignCenter, show_caret=False):
        painter.save()
        pt = max_pt
        font = QFont(UI_FONT, pt, QFont.Weight.DemiBold)
        fm = QFontMetricsF(font)
        avail_w = rect.width() - 6.0

        while pt > 10 and fm.horizontalAdvance(text_str) > avail_w:
            pt -= 1
            font.setPointSize(pt)
            fm = QFontMetricsF(font)

        painter.setFont(font)
        painter.setPen(color)
        painter.drawText(rect, align, text_str)

        if show_caret:
            # Draw blinking text cursor at self.edit_cursor position
            if int(time.perf_counter() * 2.2) % 2 == 0:
                total_w = fm.horizontalAdvance(text_str)
                start_x = rect.center().x() - total_w / 2.0
                prefix_w = fm.horizontalAdvance(text_str[:self.edit_cursor])
                caret_x = start_x + prefix_w
                caret_h = fm.height() * 0.68
                cy = rect.center().y()
                painter.setPen(QPen(color, 1.8))
                painter.drawLine(QPointF(caret_x, cy - caret_h / 2), QPointF(caret_x, cy + caret_h / 2))

        painter.restore()

    def draw_mode_pill(self, painter: QPainter, rect: QRectF, theme):
        self.interactive_rects["toggle_mode"] = rect
        hovered = (self.hovered_btn == "toggle_mode")

        painter.save()
        r = 6.0
        bg = QColor(255, 255, 255, 28 if hovered else 14)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg)
        painter.drawRoundedRect(rect, r, r)

        fg_col = QColor(*theme["text"]) if hovered else QColor(*theme["muted"])
        icon_name = "timer" if self.mode == "timer" else "stopwatch"
        ic_left = QRectF(rect.x() + 7, rect.center().y() - 6.5, 13, 13)
        render_svg_icon(painter, icon_name, ic_left, fg_col)

        label = "Таймер" if self.mode == "timer" else "Секундомер"
        font = QFont(UI_FONT, 9, QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.setPen(fg_col)
        text_rect = rect.adjusted(24, 0, -18, 0)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, label)

        ic_right = QRectF(rect.right() - 16, rect.center().y() - 5.5, 11, 11)
        render_svg_icon(painter, "swap", ic_right, QColor(*theme["muted"], 200 if hovered else 130))
        painter.restore()

    def draw_icon_btn(self, painter: QPainter, key: str, rect: QRectF, icon_name: str, theme, is_primary=False):
        self.interactive_rects[key] = rect
        hovered = (self.hovered_btn == key)

        painter.save()
        r = 7.0
        if is_primary:
            p_bg = theme["primary_bg"]
            bg = QColor(p_bg[0], p_bg[1], p_bg[2], 255 if hovered else 230)
            fg = QColor(*theme["primary_fg"])
        else:
            bg = QColor(255, 255, 255, 32 if hovered else 15)
            fg = QColor(*theme["text"]) if hovered else QColor(*theme["muted"])

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg)
        painter.drawRoundedRect(rect, r, r)

        s = min(rect.width(), rect.height()) * 0.52
        ic_rect = QRectF(rect.center().x() - s / 2, rect.center().y() - s / 2, s, s)
        render_svg_icon(painter, icon_name, ic_rect, fg)
        painter.restore()

    def draw_text_btn(self, painter: QPainter, key: str, rect: QRectF, label: str, theme, is_primary=False, font_size=9, icon_name=None):
        self.interactive_rects[key] = rect
        hovered = (self.hovered_btn == key)

        painter.save()
        r = 7.0
        if is_primary:
            p_bg = theme["primary_bg"]
            bg = QColor(p_bg[0], p_bg[1], p_bg[2], 255 if hovered else 232)
            fg = QColor(*theme["primary_fg"])
        else:
            bg = QColor(255, 255, 255, 32 if hovered else 15)
            fg = QColor(*theme["text"]) if hovered else QColor(*theme["muted"])

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg)
        painter.drawRoundedRect(rect, r, r)

        font = QFont(UI_FONT, font_size, QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.setPen(fg)

        if icon_name:
            s = 12.0
            fm = painter.fontMetrics()
            tw = fm.horizontalAdvance(label)
            total_w = s + 6 + tw
            start_x = rect.center().x() - total_w / 2
            ic_rect = QRectF(start_x, rect.center().y() - s / 2, s, s)
            render_svg_icon(painter, icon_name, ic_rect, fg)
            t_rect = QRectF(start_x + s + 6, rect.y(), tw + 4, rect.height())
            painter.drawText(t_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, label)
        else:
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)

        painter.restore()

    def render_card_contents(self, painter: QPainter, w: float, h: float, theme: dict):
        bg_rgb = theme["bg"]
        brd_rgb = theme["border"]

        card_rect = QRectF(0, 0, w, h)
        radius = 14.0

        flash = 0
        if self.alarm_flash > 0:
            flash = int((math.sin(self.alarm_flash * 12.0) * 0.5 + 0.5) * 45)

        alpha_bg = int(max(0.18, min(1.0, self.bg_opacity)) * 255)
        bg_color = QColor(
            min(255, bg_rgb[0] + flash),
            min(255, bg_rgb[1] + flash // 2),
            min(255, bg_rgb[2] + flash // 2),
            alpha_bg
        )

        path = QPainterPath()
        path.addRoundedRect(card_rect, radius, radius)
        painter.fillPath(path, bg_color)

        painter.setPen(QPen(QColor(brd_rgb[0], brd_rgb[1], brd_rgb[2], 160), 1.0))
        painter.drawPath(path)

        if self.mode == "timer" and self.timer_total > 0:
            prog = max(0.0, min(1.0, self.timer_remaining / self.timer_total))
            bar_margin = 14
            bar_w = w - bar_margin * 2
            bar_y = h - 5.0
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, 20))
            painter.drawRoundedRect(QRectF(bar_margin, bar_y, bar_w, 2.0), 1.0, 1.0)
            if prog > 0:
                painter.setBrush(QColor(*theme["primary_bg"], 180))
                painter.drawRoundedRect(QRectF(bar_margin, bar_y, bar_w * prog, 2.0), 1.0, 1.0)

        self.interactive_rects.clear()

        if self.size_mode == "mini":
            self.draw_mini_layout(painter, w, h, theme)
        elif self.size_mode == "medium":
            self.draw_medium_layout(painter, w, h, theme)
        else:
            self.draw_large_layout(painter, w, h, theme)

    def paintEvent(self, event):
        w = max(40, int(round(self.sp_w.value)))
        h = max(30, int(round(self.sp_h.value)))
        pad = self.canvas_pad

        theme = self.THEMES.get(self.theme_key, self.THEMES["graphite"])

        dpr = self.devicePixelRatioF()
        buf = QPixmap(int(w * dpr), int(h * dpr))
        buf.setDevicePixelRatio(dpr)
        buf.fill(Qt.GlobalColor.transparent)

        buf_painter = QPainter(buf)
        buf_painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        buf_painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        buf_painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.render_card_contents(buf_painter, float(w), float(h), theme)
        buf_painter.end()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        cx = pad + w / 2.0
        cy = pad + h / 2.0

        painter.save()
        painter.translate(cx, cy)
        painter.scale(self.sp_scale_x.value, self.sp_scale_y.value)
        painter.translate(-w / 2.0, -h / 2.0)
        painter.drawPixmap(0, 0, buf)
        painter.restore()

    def draw_time_box(self, painter: QPainter, rect: QRectF, max_pt: int, theme: dict, align=Qt.AlignmentFlag.AlignCenter):
        # Store time display rect separately so single-click on it still drags the window!
        self.time_display_rect = QRectF(rect)

        val = self.timer_remaining if self.mode == "timer" else self.stopwatch_elapsed
        time_str = self.format_time(val)

        is_ed = (self.editing_time and self.mode == "timer")
        if is_ed:
            painter.save()
            painter.setPen(QPen(QColor(*theme["primary_bg"], 120), 1.0, Qt.PenStyle.DashLine))
            painter.setBrush(QColor(255, 255, 255, 16))
            painter.drawRoundedRect(rect.adjusted(4, 2, -4, -2), 6.0, 6.0)
            painter.restore()
            col = QColor(*theme["primary_bg"])
        else:
            col = QColor(*theme["text"])

        self.draw_fitted_time(painter, rect, time_str, max_pt, col, align=align, show_caret=is_ed)

    def draw_mini_layout(self, painter, w, h, theme):
        self.draw_icon_btn(
            painter, "toggle_mode", QRectF(8, (h - 28) / 2, 28, 28),
            "timer" if self.mode == "timer" else "stopwatch", theme
        )

        time_rect = QRectF(42, 0, w - 110, h - 2)
        self.draw_time_box(painter, time_rect, 18, theme, align=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)

        self.draw_icon_btn(painter, "play", QRectF(w - 62, (h - 28) / 2, 28, 28), "pause" if self.is_running else "play", theme, is_primary=True)
        self.draw_icon_btn(painter, "cycle_size", QRectF(w - 30, (h - 24) / 2, 22, 24), "expand", theme)

    def draw_medium_layout(self, painter, w, h, theme):
        pill_w = 92 if self.mode == "timer" else 116
        self.draw_mode_pill(painter, QRectF(10, 10, pill_w, 22), theme)

        self.draw_icon_btn(painter, "settings", QRectF(w - 104, 10, 22, 22), "keyboard", theme)
        self.draw_icon_btn(painter, "opacity_down", QRectF(w - 79, 10, 22, 22), "opacity", theme)
        self.draw_icon_btn(painter, "cycle_size", QRectF(w - 54, 10, 22, 22), "expand", theme)
        self.draw_icon_btn(painter, "close", QRectF(w - 29, 10, 22, 22), "close", theme)

        clock_rect = QRectF(12, 34, w - 24, 56)
        self.draw_time_box(painter, clock_rect, 31, theme, align=Qt.AlignmentFlag.AlignCenter)

        y_btn = h - 38
        play_lbl = "Пауза" if self.is_running else "Старт"
        play_ic = "pause" if self.is_running else "play"

        if self.mode == "timer":
            self.draw_text_btn(painter, "sub_1m", QRectF(10, y_btn, 40, 26), "-1м", theme, font_size=8)
            self.draw_text_btn(painter, "play", QRectF(55, y_btn, 88, 26), play_lbl, theme, is_primary=True, font_size=9, icon_name=play_ic)
            self.draw_icon_btn(painter, "reset", QRectF(148, y_btn, 32, 26), "reset", theme)
            self.draw_text_btn(painter, "add_1m", QRectF(185, y_btn, 42, 26), "+1м", theme, font_size=8)
            self.draw_text_btn(painter, "add_5m", QRectF(232, y_btn, 42, 26), "+5м", theme, font_size=8)
        else:
            self.draw_text_btn(painter, "play", QRectF(w / 2 - 64, y_btn, 88, 26), play_lbl, theme, is_primary=True, font_size=9, icon_name=play_ic)
            self.draw_icon_btn(painter, "reset", QRectF(w / 2 + 30, y_btn, 34, 26), "reset", theme)

    def draw_large_layout(self, painter, w, h, theme):
        pill_w = 94 if self.mode == "timer" else 118
        self.draw_mode_pill(painter, QRectF(12, 12, pill_w, 24), theme)

        self.draw_icon_btn(painter, "settings", QRectF(w - 108, 12, 24, 24), "keyboard", theme)
        self.draw_icon_btn(painter, "opacity_down", QRectF(w - 80, 12, 24, 24), "opacity", theme)
        self.draw_icon_btn(painter, "cycle_size", QRectF(w - 52, 12, 24, 24), "expand", theme)
        self.draw_icon_btn(painter, "close", QRectF(w - 28, 12, 20, 24), "close", theme)

        clock_rect = QRectF(14, 42, w - 28, 64)
        self.draw_time_box(painter, clock_rect, 40, theme, align=Qt.AlignmentFlag.AlignCenter)

        if self.mode == "timer":
            y_p = 112
            presets = [("5м", 5), ("15м", 15), ("25м", 25), ("45м", 45), ("60м", 60)]
            pw = (w - 24 - (len(presets) - 1) * 6) / len(presets)
            for i, (lbl, mins) in enumerate(presets):
                px = 12 + i * (pw + 6)
                self.draw_text_btn(painter, f"preset_{mins}", QRectF(px, y_p, pw, 24), lbl, theme, font_size=8)

        y_btn = h - 42
        play_lbl = "Пауза" if self.is_running else "Старт"
        play_ic = "pause" if self.is_running else "play"

        if self.mode == "timer":
            self.draw_text_btn(painter, "sub_1m", QRectF(12, y_btn, 52, 28), "-1 мин", theme, font_size=8)
            self.draw_text_btn(painter, "play", QRectF(72, y_btn, 124, 28), play_lbl, theme, is_primary=True, font_size=9, icon_name=play_ic)
            self.draw_icon_btn(painter, "reset", QRectF(204, y_btn, 42, 28), "reset", theme)
            self.draw_text_btn(painter, "add_1m", QRectF(254, y_btn, 82, 28), "+1 мин", theme, font_size=8)
        else:
            self.draw_text_btn(painter, "play", QRectF(w / 2 - 74, y_btn, 104, 28), play_lbl, theme, is_primary=True, font_size=9, icon_name=play_ic)
            self.draw_icon_btn(painter, "reset", QRectF(w / 2 + 38, y_btn, 38, 28), "reset", theme)

    def card_pos_from_event(self, event):
        pos = event.position()
        return QPointF(pos.x() - self.canvas_pad, pos.y() - self.canvas_pad)

    def hit_test_button(self, card_pt):
        for key, rect in self.interactive_rects.items():
            if rect.contains(card_pt):
                return key
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            card_pt = self.card_pos_from_event(event)
            hit = self.hit_test_button(card_pt)
            if hit:
                if hit != "time_display" and self.editing_time:
                    self.commit_time_edit()
                self.handle_button_click(hit)
                return

            if self.editing_time:
                self.commit_time_edit()

            self.dragging = True
            global_pt = event.globalPosition()
            self.drag_offset = QPointF(global_pt.x() - self.sp_x.value, global_pt.y() - self.sp_y.value)

            if self.dock_edge:
                self.detaching_from_edge = self.dock_edge
                self.detach_anchor_pos = QPointF(self.sp_x.value, self.sp_y.value)
            else:
                self.detaching_from_edge = None

    def mouseMoveEvent(self, event):
        card_pt = self.card_pos_from_event(event)
        if not self.dragging:
            hit = self.hit_test_button(card_pt)
            if hit != self.hovered_btn:
                self.hovered_btn = hit
                if hit == "time_display" and self.mode == "timer":
                    self.setCursor(Qt.CursorShape.IBeamCursor)
                elif hit:
                    self.setCursor(Qt.CursorShape.PointingHandCursor)
                else:
                    self.setCursor(Qt.CursorShape.ArrowCursor)
            return

        self.setCursor(Qt.CursorShape.SizeAllCursor)
        global_pt = event.globalPosition()
        raw_x = global_pt.x() - self.drag_offset.x()
        raw_y = global_pt.y() - self.drag_offset.y()

        if self.detaching_from_edge:
            dx = raw_x - self.detach_anchor_pos.x()
            dy = raw_y - self.detach_anchor_pos.y()
            dist = math.hypot(dx, dy)
            peel_threshold = 42.0

            if dist < peel_threshold:
                pull_ratio = dist / peel_threshold
                self.sp_x.set_immediate(self.detach_anchor_pos.x() + dx * 0.25)
                self.sp_y.set_immediate(self.detach_anchor_pos.y() + dy * 0.25)

                if "left" in self.detaching_from_edge or "right" in self.detaching_from_edge:
                    self.sp_scale_x.set_immediate(1.0 + pull_ratio * 0.16)
                    self.sp_scale_y.set_immediate(1.0 - pull_ratio * 0.10)
                else:
                    self.sp_scale_y.set_immediate(1.0 + pull_ratio * 0.16)
                    self.sp_scale_x.set_immediate(1.0 - pull_ratio * 0.10)
                return
            else:
                edge_released = self.detaching_from_edge
                self.detaching_from_edge = None
                self.dock_edge = None
                self.sp_scale_x.target = 1.0
                self.sp_scale_y.target = 1.0
                if "left" in edge_released or "right" in edge_released:
                    self.trigger_jelly(vx=-2.4, vy=1.8)
                else:
                    self.trigger_jelly(vx=1.8, vy=-2.4)

        self.sp_x.set_immediate(raw_x)
        self.sp_y.set_immediate(raw_y)

        edge, snap_rect = self.compute_snap_candidate(raw_x, raw_y, self.sp_w.value, self.sp_h.value, cursor_pt=global_pt)
        if edge and snap_rect:
            self.snap_preview.show_zone(snap_rect)
        else:
            self.snap_preview.hide_zone()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            self.dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.snap_preview.hide_zone()

            if self.detaching_from_edge:
                self.sp_x.target = self.detach_anchor_pos.x()
                self.sp_y.target = self.detach_anchor_pos.y()
                self.sp_scale_x.target = 1.0
                self.sp_scale_y.target = 1.0
                self.detaching_from_edge = None
                return

            edge, snap_rect = self.compute_snap_candidate(
                self.sp_x.value, self.sp_y.value, self.sp_w.value, self.sp_h.value, cursor_pt=event.globalPosition()
            )
            self.dock_edge = edge
            if edge and snap_rect:
                self.sp_x.target = snap_rect.x()
                self.sp_y.target = snap_rect.y()
                if "left" in edge or "right" in edge:
                    self.trigger_jelly(vx=-2.0, vy=1.5)
                else:
                    self.trigger_jelly(vx=1.5, vy=-2.0)
            else:
                self.sp_x.target = self.sp_x.value
                self.sp_y.target = self.sp_y.value

            self.save_config()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            card_pt = self.card_pos_from_event(event)
            hit = self.hit_test_button(card_pt)
            if hit:
                self.handle_button_click(hit)
                return
            # Double-clicking the timer digits opens text editing mode!
            if self.mode == "timer" and self.time_display_rect.contains(card_pt):
                self.dragging = False
                self.start_time_edit()
                return
            self.cycle_size()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta == 0:
            return
        step = 1 if delta > 0 else -1
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.bg_opacity = max(0.20, min(1.0, self.bg_opacity + step * 0.06))
            self.save_config()
        else:
            if self.mode == "timer" and not self.is_running:
                self.adjust_timer(step * 60)

    def cycle_size(self):
        order = ["mini", "medium", "large"]
        idx = (order.index(self.size_mode) + 1) % len(order)
        self.set_size_mode(order[idx])

    def open_settings_dialog(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def handle_button_click(self, key):
        if key == "time_display":
            self.start_time_edit()
        elif key == "play":
            self.toggle_play()
        elif key == "reset":
            self.reset_clock()
        elif key == "toggle_mode":
            self.switch_mode()
        elif key == "cycle_size":
            self.cycle_size()
        elif key == "settings":
            self.open_settings_dialog()
        elif key == "opacity_down":
            presets = [0.95, 0.85, 0.60, 0.35]
            closest = min(range(len(presets)), key=lambda i: abs(presets[i] - self.bg_opacity))
            self.bg_opacity = presets[(closest + 1) % len(presets)]
            self.save_config()
        elif key == "add_1m":
            self.adjust_timer(60)
        elif key == "add_5m":
            self.adjust_timer(300)
        elif key == "sub_1m":
            self.adjust_timer(-60)
        elif key.startswith("preset_"):
            mins = int(key.split("_")[1])
            self.is_running = False
            self.timer_total = mins * 60.0
            self.timer_remaining = self.timer_total
            self.save_config()
        elif key == "close":
            self.save_config()
            self.snap_preview.close()
            QApplication.quit()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: #18181B;
                color: #F4F4F5;
                border: 1px solid #3F3F46;
                border-radius: 8px;
                padding: 5px;
                font-family: '{UI_FONT}';
                font-size: 12px;
            }}
            QMenu::item {{
                padding: 6px 18px;
                border-radius: 5px;
            }}
            QMenu::item:selected {{
                background-color: #3F3F46;
                color: #FFFFFF;
            }}
            QMenu::separator {{
                height: 1px;
                background: #27272A;
                margin: 4px 6px;
            }}
        """)

        act_timer = menu.addAction("Таймер" + (" ✓" if self.mode == "timer" else ""))
        act_sw = menu.addAction("Секундомер" + (" ✓" if self.mode == "stopwatch" else ""))
        if self.mode == "timer":
            act_edit = menu.addAction("Ввести время с клавиатуры")
        else:
            act_edit = None
        menu.addSeparator()

        act_keys = menu.addAction("Горячие клавиши и прозрачность...")
        act_global_hk = menu.addAction("Глобальные клавиши (в браузере/играх)" + (" ✓" if self.global_hotkeys else ""))
        menu.addSeparator()

        size_menu = menu.addMenu("Размер")
        act_s_mini = size_menu.addAction("Мини" + (" ✓" if self.size_mode == "mini" else ""))
        act_s_med = size_menu.addAction("Средний" + (" ✓" if self.size_mode == "medium" else ""))
        act_s_lrg = size_menu.addAction("Большой" + (" ✓" if self.size_mode == "large" else ""))

        th_menu = menu.addMenu("Оттенок фона")
        th_actions = {}
        for k, v in self.THEMES.items():
            mark = " ✓" if self.theme_key == k else ""
            th_actions[th_menu.addAction(v["name"] + mark)] = k

        menu.addSeparator()
        act_snap = menu.addAction("Прилипание к краям" + (" ✓" if self.snap_enabled else ""))
        menu.addSeparator()
        act_quit = menu.addAction("Закрыть")

        chosen = menu.exec(event.globalPos())
        if not chosen:
            return
        if chosen == act_timer:
            self.switch_mode("timer")
        elif chosen == act_sw:
            self.switch_mode("stopwatch")
        elif act_edit and chosen == act_edit:
            self.start_time_edit()
        elif chosen == act_keys:
            self.open_settings_dialog()
        elif chosen == act_global_hk:
            self.global_hotkeys = not self.global_hotkeys
            self.save_config()
        elif chosen == act_s_mini:
            self.set_size_mode("mini")
        elif chosen == act_s_med:
            self.set_size_mode("medium")
        elif chosen == act_s_lrg:
            self.set_size_mode("large")
        elif chosen in th_actions:
            self.theme_key = th_actions[chosen]
            self.save_config()
        elif chosen == act_snap:
            self.snap_enabled = not self.snap_enabled
            self.save_config()
        elif chosen == act_quit:
            self.save_config()
            self.snap_preview.close()
            QApplication.quit()


def main():
    app = QApplication(sys.argv)
    widget = JellyTimerWidget()
    widget.show()
    widget.enforce_topmost_crossplatform()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
