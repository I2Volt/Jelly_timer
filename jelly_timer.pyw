import sys
import math
import json
import os
import io
import wave
import struct
import time
import platform
import subprocess
import threading
import tempfile
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMenu, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QCheckBox, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QByteArray, pyqtSignal, QObject
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QFont, QFontMetricsF, QPainterPath, QKeySequence, QPixmap
)
from PyQt6.QtSvg import QSvgRenderer

OS_NAME = platform.system()  # "Windows", "Darwin" (macOS), "Linux"
IS_WIN = (OS_NAME == "Windows")
IS_MAC = (OS_NAME == "Darwin")
IS_LINUX = (OS_NAME == "Linux")

try:
    if IS_WIN:
        import pynput.keyboard._win32  # Explicit import for PyInstaller
    from pynput import keyboard as pynput_kb
    HAS_PYNPUT = True
except Exception:
    HAS_PYNPUT = False

if IS_WIN:
    import ctypes
    import winsound
    HWND_TOPMOST = -1
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_NOACTIVATE = 0x0010
    SWP_SHOWWINDOW = 0x0040

UI_FONT = "SF Pro Display" if IS_MAC else ("Ubuntu" if IS_LINUX else "Segoe UI")

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

_ALARM_WAV_CACHE = None


def _build_alarm_wav_bytes() -> bytes:
    """Synthesizes a clear, loud 44.1 kHz 16-bit PCM WAV triple-chime in memory."""
    global _ALARM_WAV_CACHE
    if _ALARM_WAV_CACHE is not None:
        return _ALARM_WAV_CACHE

    sr = 44100
    buf = io.BytesIO()
    notes = [
        (783.99, 0.14), (987.77, 0.14), (1174.66, 0.28), (0.0, 0.10),
        (783.99, 0.14), (987.77, 0.14), (1174.66, 0.28), (0.0, 0.10),
        (783.99, 0.14), (987.77, 0.14), (1567.98, 0.42),
    ]
    samples = []
    for freq, dur in notes:
        n = int(sr * dur)
        for i in range(n):
            if freq <= 0.0:
                samples.append(0)
            else:
                t = i / sr
                attack = min(1.0, i / (sr * 0.008))
                decay = math.exp(-3.0 * t / dur)
                env = attack * decay
                val = (
                    0.65 * math.sin(2.0 * math.pi * freq * t)
                    + 0.25 * math.sin(2.0 * math.pi * (freq * 2.0) * t)
                    + 0.10 * math.sin(2.0 * math.pi * (freq * 3.0) * t)
                )
                s = int(max(-32767, min(32767, val * env * 30000)))
                samples.append(s)

    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(struct.pack("<" + "h" * len(samples), *samples))

    _ALARM_WAV_CACHE = buf.getvalue()
    return _ALARM_WAV_CACHE


def play_system_alarm():
    """Plays synthesized WAV alarm through primary audio output on Windows, macOS, and Linux."""
    def _worker():
        try:
            wav_bytes = _build_alarm_wav_bytes()
            if IS_WIN:
                winsound.PlaySound(wav_bytes, winsound.SND_MEMORY)
                return
            wav_path = os.path.join(tempfile.gettempdir(), "jelly_timer_alarm.wav")
            if not os.path.exists(wav_path):
                with open(wav_path, "wb") as f:
                    f.write(wav_bytes)
            if IS_MAC:
                subprocess.Popen(["afplay", wav_path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                return
            elif IS_LINUX:
                for cmd in (["paplay", wav_path], ["aplay", wav_path]):
                    try:
                        subprocess.Popen(cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                        return
                    except Exception:
                        pass
        except Exception:
            pass
    threading.Thread(target=_worker, daemon=True).start()


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
    """Universal background hotkey listener with OS-level key suppression when summoned."""
    hotkey_triggered = pyqtSignal(str)

    MOD_VKS = {0xA0, 0xA1, 0x10, 0xA2, 0xA3, 0x11, 0xA4, 0xA5, 0x12, 0x5B, 0x5C}
    MOD_GROUPS = (
        {0xA0, 0xA1, 0x10},
        {0xA2, 0xA3, 0x11},
        {0xA4, 0xA5, 0x12},
        {0x5B, 0x5C},
    )

    def __init__(self, widget):
        super().__init__(widget)
        self.w = widget
        self.held_tokens = set()
        self.held_vks = set()
        self.suppressed_vks = set()
        self._suppress_mac_event = False
        self.listener = None

        if HAS_PYNPUT:
            try:
                if IS_WIN:
                    self.listener = pynput_kb.Listener(
                        win32_event_filter=self._win32_event_filter
                    )
                elif IS_MAC:
                    self.listener = pynput_kb.Listener(
                        on_press=self._on_pynput_press,
                        on_release=self._on_pynput_release,
                        darwin_intercept=self._darwin_intercept
                    )
                else:
                    self.listener = pynput_kb.Listener(
                        on_press=self._on_pynput_press,
                        on_release=self._on_pynput_release
                    )
                self.listener.daemon = True
                self.listener.start()
            except Exception:
                self.listener = None

    def _has_other_win_modifier(self, allowed_vk: int) -> bool:
        for grp in self.MOD_GROUPS:
            if allowed_vk in grp:
                continue
            if self.held_vks & grp:
                return True
        return False

    def _suppress_win_vk(self, vk: int, is_press: bool):
        if is_press:
            self.suppressed_vks.add(vk)
        else:
            self.suppressed_vks.discard(vk)
        if self.listener is not None:
            self.listener.suppress_event()

    def _win32_event_filter(self, msg, data):
        # Ignore injected events
        if getattr(data, "flags", 0) & 0x10:
            return True

        if getattr(self.w, "settings_open", False) or self.w.editing_time:
            self.held_vks.clear()
            self.suppressed_vks.clear()
            return True

        vk = int(data.vkCode)
        is_press = msg in (0x0100, 0x0104)    # WM_KEYDOWN, WM_SYSKEYDOWN
        is_release = msg in (0x0101, 0x0105)  # WM_KEYUP, WM_SYSKEYUP
        if not (is_press or is_release):
            return True

        if is_press:
            first_press = (vk not in self.held_vks)
            self.held_vks.add(vk)
        else:
            first_press = False
            self.held_vks.discard(vk)
            if vk in self.suppressed_vks:
                self._suppress_win_vk(vk, False)
                return False

        has_other_mod = self._has_other_win_modifier(vk)

        # 1. Check Summon hotkey globally
        summon_vk = self.w.hotkeys.get("summon", {}).get("vk", 0)
        if summon_vk and vk == summon_vk and not has_other_mod:
            if is_press and first_press:
                self.hotkey_triggered.emit("summon")
            if vk not in self.MOD_VKS:
                self._suppress_win_vk(vk, is_press)
            return False

        # If another standalone modifier (e.g. Right Shift for PRO) is pressed while summoned, yield focus cleanly
        if self.w.summoned_focus and vk in self.MOD_VKS and vk != summon_vk and is_press and first_press:
            self.hotkey_triggered.emit("unsummon")
            return False

        # 2. When Timer is Summoned: intercept and BLOCK keys from reaching the open desktop tab!
        if self.w.summoned_focus:
            if vk == 0x1B:  # Esc
                if is_press and first_press:
                    self.hotkey_triggered.emit("unsummon")
                self._suppress_win_vk(vk, is_press)
                return False

            for action_key, hk in self.w.hotkeys.items():
                if action_key == "summon":
                    continue
                hk_vk = hk.get("vk", 0)
                if hk_vk and vk == hk_vk and not has_other_mod:
                    if is_press and first_press:
                        self.hotkey_triggered.emit(action_key)
                    if vk not in self.MOD_VKS:
                        self._suppress_win_vk(vk, is_press)
                    return False

            # Suppress any other plain key while summoned so the background window never reacts
            if vk not in self.MOD_VKS and not has_other_mod:
                self._suppress_win_vk(vk, is_press)
            return False

        # 3. Optional "always listen to all keys" mode
        if self.w.global_hotkeys:
            for action_key, hk in self.w.hotkeys.items():
                if action_key == "summon":
                    continue
                hk_vk = hk.get("vk", 0)
                if hk_vk and vk == hk_vk and not has_other_mod:
                    if is_press and first_press:
                        self.hotkey_triggered.emit(action_key)
                    if vk not in self.MOD_VKS:
                        self._suppress_win_vk(vk, is_press)
                    return False

        return False

    def _darwin_intercept(self, event_type, event):
        if self._suppress_mac_event:
            self._suppress_mac_event = False
            return None
        return event

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
        if getattr(self.w, "settings_open", False) or self.w.editing_time:
            return
        token = self._normalize_pynput_key(key)
        if not token:
            return
        first_press = (token not in self.held_tokens)
        self.held_tokens.add(token)

        mod_tokens = {"Left Shift", "Right Shift", "Left Ctrl", "Right Ctrl", "Left Alt", "Right Alt", "Left Cmd", "Right Cmd"}
        other_mods = (self.held_tokens & mod_tokens) - {token}
        if other_mods:
            return

        summon_hk = self.w.hotkeys.get("summon", {})
        if summon_hk.get("name", "").upper() == token.upper():
            if first_press:
                self.hotkey_triggered.emit("summon")
            if token not in mod_tokens:
                self._suppress_mac_event = True
            return

        if self.w.summoned_focus:
            if token == "Esc":
                if first_press:
                    self.hotkey_triggered.emit("unsummon")
                self._suppress_mac_event = True
                return
            for action_key, hk in self.w.hotkeys.items():
                if action_key == "summon":
                    continue
                if hk.get("name", "").upper() == token.upper():
                    if first_press:
                        self.hotkey_triggered.emit(action_key)
                    if token not in mod_tokens:
                        self._suppress_mac_event = True
                    return
            if token not in mod_tokens:
                self._suppress_mac_event = True
            return

        if self.w.global_hotkeys:
            for action_key, hk in self.w.hotkeys.items():
                if action_key == "summon":
                    continue
                if hk.get("name", "").upper() == token.upper():
                    if first_press:
                        self.hotkey_triggered.emit(action_key)
                    if token not in mod_tokens:
                        self._suppress_mac_event = True
                    return

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
        self.setMinimumWidth(430)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #18181B;
                color: #F4F4F5;
                font-family: '{UI_FONT}';
            }}
            QLabel {{
                color: #D4D4D8;
                font-size: 12px;
            }}
            QCheckBox {{
                color: #E4E4E7;
                font-size: 12px;
                spacing: 8px;
            }}
            QLineEdit {{
                background-color: #27272A;
                color: #FAFAFA;
                border: 1px solid #3F3F46;
                border-radius: 6px;
                padding: 5px 8px;
                font-size: 12px;
                font-weight: 600;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        title = QLabel("Горячие клавиши")
        title.setStyleSheet("font-size: 14px; font-weight: 600; color: #FAFAFA;")
        layout.addWidget(title)

        self.buttons = {}
        rows = [
            ("summon", "Вызвать / Выбрать таймер:"),
            ("play_pause", "Старт / Пауза:"),
            ("reset", "Сброс:"),
            ("switch_mode", "Таймер / Секундомер:"),
            ("cycle_size", "Размер окна:"),
        ]

        for k, label_text in rows:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            if k == "summon":
                lbl.setStyleSheet("color: #FAFAFA; font-weight: 600;")
            hk = self.w.hotkeys[k]
            btn = KeyCaptureButton(hk["vk"], hk["name"], self)
            btn.setFixedWidth(135)
            self.buttons[k] = btn
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(btn)
            layout.addLayout(row)

        summon_hint = QLabel(
            "Нажмите клавишу вызова в любой момент — таймер подсветится белой рамкой и начнёт слушать кнопки управления. "
            "Нажмите её повторно или кликните мышкой в другое окно, чтобы отключить перехват клавиш."
        )
        summon_hint.setWordWrap(True)
        summon_hint.setMinimumHeight(56)
        summon_hint.setStyleSheet("color: #D4D4D8; font-size: 11.5px; background: #222226; padding: 8px 10px; border-radius: 6px;")
        layout.addWidget(summon_hint)

        self.global_cb = QCheckBox("Слушать все клавиши всегда (даже без вызова таймера)")
        self.global_cb.setChecked(self.w.global_hotkeys)
        layout.addWidget(self.global_cb)

        presets_lbl = QLabel("Пресеты большого режима (мин, через запятую):")
        presets_lbl.setStyleSheet("font-size: 12px; color: #A1A1AA; margin-top: 2px;")
        layout.addWidget(presets_lbl)

        self.presets_edit = QLineEdit(", ".join(str(m) for m in self.w.presets))
        layout.addWidget(self.presets_edit)

        snd_row = QHBoxLayout()
        snd_row.addWidget(QLabel("Звуковой сигнал:"))
        snd_test_btn = QPushButton("Проверить звук")
        snd_test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        snd_test_btn.setStyleSheet("""
            QPushButton {
                background-color: #27272A;
                color: #F4F4F5;
                border: 1px solid #3F3F46;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3F3F46;
            }
        """)
        snd_test_btn.clicked.connect(play_system_alarm)
        snd_row.addStretch()
        snd_row.addWidget(snd_test_btn)
        layout.addLayout(snd_row)

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

        raw_presets = self.presets_edit.text().replace(";", ",").split(",")
        parsed = []
        for item in raw_presets:
            item = item.strip()
            if item.isdigit():
                val = max(1, min(999, int(item)))
                parsed.append(val)
        if parsed:
            self.w.presets = parsed[:6]

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
        self.global_hotkeys = False
        self.summoned_focus = False
        self.prev_foreground_hwnd = 0
        self.presets = [5, 15, 25, 45, 60]

        self.hotkeys = {
            "summon":      {"vk": 0xA3, "name": "Right Ctrl"},
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
                self.global_hotkeys = bool(data.get("global_hotkeys_v3", False))
                if isinstance(data.get("presets"), list) and data["presets"]:
                    self.presets = [int(x) for x in data["presets"] if int(x) > 0][:6]
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
                "global_hotkeys_v3": self.global_hotkeys,
                "presets": self.presets,
                "hotkeys": self.hotkeys,
                "timer_total": self.timer_total,
                "x": self.sp_x.target,
                "y": self.sp_y.target,
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def is_reset_available(self) -> bool:
        if self.is_running:
            return True
        if self.mode == "timer":
            return abs(self.timer_remaining - self.timer_total) > 0.05
        else:
            return self.stopwatch_elapsed > 0.05

    def toggle_summon_focus(self):
        """Toggles active focus state of the widget via the Summon hotkey."""
        if self.summoned_focus:
            self.summoned_focus = False
            self.clearFocus()
            self.trigger_jelly(vx=-1.1, vy=1.1)
        else:
            self.summoned_focus = True
            self.alarm_flash = 0.0
            self.raise_()
            self.trigger_jelly(vx=1.4, vy=-1.4)

    def focusOutEvent(self, event):
        if not IS_WIN:
            self.summoned_focus = False
        super().focusOutEvent(event)

    def enforce_topmost_crossplatform(self):
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

        edge = f"{v_edge}_{h_edge}" if (v_edge and h_edge) else (h_edge or v_edge)
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

        u32 = ctypes.windll.user32

        # Automatically clear summoned_focus if user clicked into another application window
        if self.summoned_focus:
            fg = u32.GetForegroundWindow()
            if fg and fg != int(self.winId()) and not self.underMouse():
                self.summoned_focus = False

        # 1. Always check the Summon hotkey globally
        summon_hk = self.hotkeys.get("summon", {})
        summon_vk = summon_hk.get("vk", 0)
        if summon_vk:
            st = u32.GetAsyncKeyState(summon_vk)
            is_down = (st & 0x8000) != 0
            was_down = self.prev_vk_state.get(summon_vk, False)
            self.prev_vk_state[summon_vk] = is_down
            if is_down and not was_down:
                if not self.is_other_modifier_pressed_win32(summon_vk):
                    self.toggle_summon_focus()
                    return

        # 2. Check other hotkeys only when summoned, under mouse, active window, or global_hotkeys is enabled
        active_ok = self.global_hotkeys or self.summoned_focus or self.underMouse() or self.isActiveWindow()
        if not active_ok:
            for action_key, hk in self.hotkeys.items():
                if action_key != "summon":
                    self.prev_vk_state[hk.get("vk", 0)] = False
            return

        for action_key, hk in self.hotkeys.items():
            if action_key == "summon":
                continue
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
        if action_key == "summon":
            self.toggle_summon_focus()
        elif action_key == "unsummon":
            if self.summoned_focus:
                self.toggle_summon_focus()
        elif action_key == "play_pause":
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
            if not HAS_PYNPUT:
                self.poll_hotkeys_win32()
            elif self.summoned_focus:
                # Clear summoned_focus immediately if the user clicks anywhere outside the timer widget
                u32 = ctypes.windll.user32
                mouse_down = (
                    (u32.GetAsyncKeyState(0x01) & 0x8000) != 0
                    or (u32.GetAsyncKeyState(0x02) & 0x8000) != 0
                    or (u32.GetAsyncKeyState(0x04) & 0x8000) != 0
                )
                if mouse_down and not self.underMouse():
                    self.summoned_focus = False

        if self.is_running:
            if self.mode == "timer":
                self.timer_remaining -= real_dt
                if self.timer_remaining <= 0.0:
                    self.timer_remaining = 0.0
                    self.is_running = False
                    self.alarm_flash = 6.0
                    self.trigger_jelly(vx=2.2, vy=-2.2)
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
        sig = (
            self.format_time(self.timer_remaining if self.mode == "timer" else self.stopwatch_elapsed),
            self.mode,
            self.size_mode,
            self.theme_key,
            round(self.bg_opacity, 3),
            self.is_running,
            self.hovered_btn,
            self.summoned_focus,
            self.editing_time,
            self.edit_cursor,
            int(time.perf_counter() * 2.2) % 2 if self.editing_time else 0,
            round(self.alarm_flash, 2),
            round(self.sp_w.value, 1),
            round(self.sp_h.value, 1),
            round(self.sp_scale_x.value, 3),
            round(self.sp_scale_y.value, 3),
            tuple(self.presets),
        )
        if sig != getattr(self, "_last_paint_sig", None):
            self._last_paint_sig = sig
            self.update()

    def update_window_geometry(self, force=False):
        pad = self.canvas_pad
        win_x = int(round(self.sp_x.value - pad))
        win_y = int(round(self.sp_y.value - pad))
        win_w = int(round(self.sp_w.value + pad * 2))
        win_h = int(round(self.sp_h.value + pad * 2))

        if force or self.width() != win_w or self.height() != win_h:
            self.setGeometry(win_x, win_y, win_w, win_h)
        elif self.x() != win_x or self.y() != win_y:
            self.move(win_x, win_y)

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

        if event.key() == Qt.Key.Key_Escape and self.summoned_focus:
            self.toggle_summon_focus()
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

        alpha_bg = int(max(0.18, min(1.0, self.bg_opacity)) * 255)
        if self.alarm_flash > 0:
            pulse = math.sin(self.alarm_flash * 14.0) * 0.5 + 0.5
            mix = pulse * 0.88
            r_col = int(bg_rgb[0] * (1.0 - mix) + 225 * mix)
            g_col = int(bg_rgb[1] * (1.0 - mix) + 24 * mix)
            b_col = int(bg_rgb[2] * (1.0 - mix) + 34 * mix)
            alpha_bg = max(alpha_bg, int(248 * pulse))
            bg_color = QColor(r_col, g_col, b_col, alpha_bg)
        else:
            bg_color = QColor(bg_rgb[0], bg_rgb[1], bg_rgb[2], alpha_bg)

        path = QPainterPath()
        path.addRoundedRect(card_rect, radius, radius)
        painter.fillPath(path, bg_color)

        if self.alarm_flash > 0:
            pulse = math.sin(self.alarm_flash * 14.0) * 0.5 + 0.5
            painter.setPen(QPen(QColor(255, 95, 95, int(190 + 65 * pulse)), 2.2))
        elif self.summoned_focus:
            painter.setPen(QPen(QColor(244, 244, 245, 235), 1.8))
        else:
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
        self.draw_time_box(painter, clock_rect, 32, theme, align=Qt.AlignmentFlag.AlignCenter)

        y_btn = h - 38
        play_lbl = "Пауза" if self.is_running else "Старт"
        play_ic = "pause" if self.is_running else "play"

        if self.is_reset_available():
            self.draw_text_btn(painter, "play", QRectF(w / 2 - 70, y_btn, 100, 26), play_lbl, theme, is_primary=True, font_size=9, icon_name=play_ic)
            self.draw_icon_btn(painter, "reset", QRectF(w / 2 + 36, y_btn, 34, 26), "reset", theme)
        else:
            self.draw_text_btn(painter, "play", QRectF(w / 2 - 56, y_btn, 112, 26), play_lbl, theme, is_primary=True, font_size=9, icon_name=play_ic)

    def draw_large_layout(self, painter, w, h, theme):
        pill_w = 94 if self.mode == "timer" else 118
        self.draw_mode_pill(painter, QRectF(12, 12, pill_w, 24), theme)

        self.draw_icon_btn(painter, "settings", QRectF(w - 108, 12, 24, 24), "keyboard", theme)
        self.draw_icon_btn(painter, "opacity_down", QRectF(w - 80, 12, 24, 24), "opacity", theme)
        self.draw_icon_btn(painter, "cycle_size", QRectF(w - 52, 12, 24, 24), "expand", theme)
        self.draw_icon_btn(painter, "close", QRectF(w - 28, 12, 20, 24), "close", theme)

        clock_rect = QRectF(14, 42, w - 28, 64)
        self.draw_time_box(painter, clock_rect, 40, theme, align=Qt.AlignmentFlag.AlignCenter)

        if self.mode == "timer" and self.presets:
            y_p = 112
            n = len(self.presets)
            pw = (w - 24 - (n - 1) * 6) / n
            for i, mins in enumerate(self.presets):
                px = 12 + i * (pw + 6)
                self.draw_text_btn(painter, f"preset_{mins}", QRectF(px, y_p, pw, 24), f"{mins}м", theme, font_size=8)

        y_btn = h - 42
        play_lbl = "Пауза" if self.is_running else "Старт"
        play_ic = "pause" if self.is_running else "play"
        show_reset = self.is_reset_available()

        if self.mode == "timer":
            self.draw_text_btn(painter, "sub_5m", QRectF(12, y_btn, 38, 28), "-5м", theme, font_size=8)
            self.draw_text_btn(painter, "sub_1m", QRectF(54, y_btn, 38, 28), "-1м", theme, font_size=8)
            if show_reset:
                self.draw_text_btn(painter, "play", QRectF(98, y_btn, 108, 28), play_lbl, theme, is_primary=True, font_size=9, icon_name=play_ic)
                self.draw_icon_btn(painter, "reset", QRectF(212, y_btn, 36, 28), "reset", theme)
            else:
                self.draw_text_btn(painter, "play", QRectF(98, y_btn, 150, 28), play_lbl, theme, is_primary=True, font_size=9, icon_name=play_ic)
            self.draw_text_btn(painter, "add_1m", QRectF(254, y_btn, 38, 28), "+1м", theme, font_size=8)
            self.draw_text_btn(painter, "add_5m", QRectF(296, y_btn, 40, 28), "+5м", theme, font_size=8)
        else:
            if show_reset:
                self.draw_text_btn(painter, "play", QRectF(w / 2 - 74, y_btn, 104, 28), play_lbl, theme, is_primary=True, font_size=9, icon_name=play_ic)
                self.draw_icon_btn(painter, "reset", QRectF(w / 2 + 36, y_btn, 38, 28), "reset", theme)
            else:
                self.draw_text_btn(painter, "play", QRectF(w / 2 - 60, y_btn, 120, 28), play_lbl, theme, is_primary=True, font_size=9, icon_name=play_ic)

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
        self.update_window_geometry()

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
        self.summoned_focus = False
        self.settings_open = True
        try:
            dlg = SettingsDialog(self)
            dlg.exec()
        finally:
            self.settings_open = False

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
        elif key == "sub_5m":
            self.adjust_timer(-300)
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

        act_keys = menu.addAction("Настройки (Клавиша вызова, пресеты)...")
        act_global_hk = menu.addAction("Слушать все клавиши всегда" + (" ✓" if self.global_hotkeys else ""))
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


def _ensure_single_instance(lock_name: str):
    pid_file = os.path.join(tempfile.gettempdir(), lock_name)
    if os.path.exists(pid_file):
        try:
            with open(pid_file, "r", encoding="utf-8") as f:
                old_pid = int(f.read().strip())
            if old_pid != os.getpid():
                if IS_WIN:
                    subprocess.run(["taskkill", "/F", "/PID", str(old_pid)], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                else:
                    import signal
                    os.kill(old_pid, signal.SIGTERM)
        except Exception:
            pass
    try:
        with open(pid_file, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass


def main():
    _ensure_single_instance("jelly_timer_free.pid")
    app = QApplication(sys.argv)
    widget = JellyTimerWidget()
    widget.show()
    widget.enforce_topmost_crossplatform()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
