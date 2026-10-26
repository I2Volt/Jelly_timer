import os
import sys
import math
from PIL import Image
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QImage, QPainter, QColor, QPen, QFont, QLinearGradient, QPainterPath, QPolygonF
)

# Import our actual widget and SVG renderer so the video captures 100% authentic UI & physics!
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jelly_timer import JellyTimerWidget, SpringValue

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def lerp(a, b, t):
    return a + (b - a) * t


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def draw_mock_desktop(painter: QPainter, W: int, H: int, active_tab: int = 0):
    """Draws a sleek dark desktop environment with a realistic browser & writer workspace."""
    # 1. Wallpaper gradient
    bg = QLinearGradient(0, 0, W, H)
    bg.setColorAt(0.0, QColor(15, 17, 23))
    bg.setColorAt(1.0, QColor(22, 24, 32))
    painter.fillRect(0, 0, W, H, bg)

    # 2. Browser Window Frame
    bx, by, bw, bh = 56, 36, W - 112, H - 84
    b_rect = QRectF(bx, by, bw, bh)
    path = QPainterPath()
    path.addRoundedRect(b_rect, 12, 12)
    painter.fillPath(path, QColor(20, 20, 23))
    painter.setPen(QPen(QColor(48, 48, 54), 1.2))
    painter.drawPath(path)

    # Browser Top Tab Bar
    tab_bar = QRectF(bx, by, bw, 42)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(14, 14, 17))
    painter.drawRoundedRect(tab_bar, 12, 12)
    painter.fillRect(QRectF(bx, by + 22, bw, 20), QColor(14, 14, 17))

    # Traffic lights / window dots
    for i, col in enumerate([(237, 106, 94), (245, 191, 79), (98, 197, 84)]):
        painter.setBrush(QColor(*col))
        painter.drawEllipse(QPointF(bx + 22 + i * 18, by + 21), 5.5, 5.5)

    # Browser Tabs
    tabs = ["Drafting_Article.md — Notion", "Research_Notes — Quran.com"]
    for i, title in enumerate(tabs):
        tx = bx + 90 + i * 210
        t_rect = QRectF(tx, by + 7, 200, 35)
        if i == active_tab:
            painter.setBrush(QColor(26, 26, 30))
            painter.drawRoundedRect(t_rect, 7, 7)
            painter.setPen(QColor(240, 240, 245))
        else:
            painter.setBrush(QColor(18, 18, 21))
            painter.drawRoundedRect(t_rect, 7, 7)
            painter.setPen(QColor(130, 130, 140))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        painter.drawText(t_rect.adjusted(12, 0, -8, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, title)

    # Document Content Area inside Browser
    doc_x = bx + 110
    doc_y = by + 84
    painter.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
    painter.setPen(QColor(235, 235, 240))
    if active_tab == 0:
        painter.drawText(QPointF(doc_x, doc_y), "Chapter 4: Deep Focus & Flow State")
        painter.setFont(QFont("Segoe UI", 11))
        painter.setPen(QColor(150, 150, 160))
        lines = [
            "Writing without distraction requires tools that stay out of your way.",
            "With global hotkeys bound to Right Ctrl & Right Alt, you never leave the keyboard.",
            "Drag the timer to any screen edge for magnetic snap and elastic jelly peel-off.",
        ]
    else:
        painter.drawText(QPointF(doc_x, doc_y), "Cross-Tab Synchronized Study Session")
        painter.setFont(QFont("Segoe UI", 11))
        painter.setPen(QColor(150, 150, 160))
        lines = [
            "Switched browser tab — the timer stays in the exact same position and keeps running!",
            "Works natively across Windows, macOS, Linux, and Chromium/Firefox browsers.",
            "Double-click the clock digits anytime to type a custom duration with arrow keys.",
        ]

    for idx, ln in enumerate(lines):
        painter.drawText(QPointF(doc_x, doc_y + 38 + idx * 28), ln)

    # Subtle decorative skeleton paragraph blocks
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(32, 32, 38))
    for r in range(5):
        w_bar = 480 if r % 2 == 0 else 390
        painter.drawRoundedRect(QRectF(doc_x, doc_y + 145 + r * 24, w_bar, 10), 4, 4)


def draw_cursor(painter: QPainter, x: float, y: float, pressed: bool = False):
    painter.save()
    painter.translate(x, y)
    if pressed:
        painter.setPen(QPen(QColor(255, 255, 255, 160), 2.0))
        painter.setBrush(QColor(255, 255, 255, 45))
        painter.drawEllipse(QPointF(0, 0), 16, 16)

    poly = QPolygonF([
        QPointF(0, 0),
        QPointF(0, 19),
        QPointF(5.5, 14.5),
        QPointF(9.5, 22),
        QPointF(12.5, 20.5),
        QPointF(8.5, 13),
        QPointF(15, 13),
    ])
    painter.setPen(QPen(QColor(15, 15, 18), 1.6))
    painter.setBrush(QColor(250, 250, 252))
    painter.drawPolygon(poly)
    painter.restore()


def draw_caption_banner(painter: QPainter, W: int, H: int, title: str, badge: str = ""):
    painter.save()
    # Bottom HUD pill
    bw = 540
    bh = 40
    bx = (W - bw) / 2
    by = H - 54
    rect = QRectF(bx, by, bw, bh)

    painter.setPen(QPen(QColor(75, 75, 85, 200), 1.0))
    painter.setBrush(QColor(18, 18, 22, 230))
    painter.drawRoundedRect(rect, 20, 20)

    painter.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
    painter.setPen(QColor(245, 245, 247))
    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, title)

    if badge:
        # Floating keystroke badge on top-left of screen
        kr = QRectF(82, 100, 210, 34)
        painter.setPen(QPen(QColor(244, 244, 245, 190), 1.2))
        painter.setBrush(QColor(28, 28, 34, 235))
        painter.drawRoundedRect(kr, 8, 8)
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor(250, 250, 252))
        painter.drawText(kr, Qt.AlignmentFlag.AlignCenter, f"⌨  {badge}")

    painter.restore()


def generate_demo():
    app = QApplication(sys.argv)
    W, H = 960, 540
    fps = 30
    dt = 1.0 / fps
    total_frames = 240  # 8.0 seconds loop at 30 FPS

    widget = JellyTimerWidget()
    widget.mode = "timer"
    widget.size_mode = "medium"
    widget.theme_key = "graphite"
    widget.bg_opacity = 0.90
    widget.timer_total = 25 * 60.0
    widget.timer_remaining = 25 * 60.0
    widget.is_running = False

    # Position widget docked at top-right of our 960x540 virtual screen
    w_med, h_med = widget.SIZES["medium"]
    dock_x = W - w_med - 14
    dock_y = 52
    widget.sp_x.set_immediate(dock_x)
    widget.sp_y.set_immediate(dock_y)
    widget.sp_w.set_immediate(w_med)
    widget.sp_h.set_immediate(h_med)
    widget.dock_edge = "right"

    frames_pil = []

    cursor_x, cursor_y = W * 0.5, H * 0.5
    mouse_down = False
    active_tab = 0
    caption = ""
    badge = ""
    show_snap_zone = False
    snap_rect = QRectF(dock_x, dock_y, w_med, h_med)

    for f in range(total_frames):
        t = f / float(fps)

        # SCENE 1 (0.0s - 2.6s): Grab docked widget -> Elastic Jelly Peel-Off -> Snap back to edge with zone preview
        if t < 2.6:
            caption = "1. Magnetic Edge Snap & Elastic Jelly Peel-Off"
            badge = ""
            if t < 0.5:
                p = smoothstep(t / 0.5)
                cursor_x = lerp(W * 0.55, dock_x + w_med * 0.5, p)
                cursor_y = lerp(H * 0.5, dock_y + h_med * 0.5, p)
                mouse_down = False
            elif t < 1.25:
                # Pulling away from right edge -> stretches until peel threshold then pops free!
                mouse_down = True
                p = smoothstep((t - 0.5) / 0.75)
                pull_dx = -lerp(0, 175, p)
                pull_dy = lerp(0, 65, p)
                cursor_x = dock_x + w_med * 0.5 + pull_dx
                cursor_y = dock_y + h_med * 0.5 + pull_dy

                dist = math.hypot(pull_dx, pull_dy)
                if dist < 44.0:
                    ratio = dist / 44.0
                    widget.sp_x.set_immediate(dock_x + pull_dx * 0.25)
                    widget.sp_y.set_immediate(dock_y + pull_dy * 0.25)
                    widget.sp_scale_x.set_immediate(1.0 + ratio * 0.18)
                    widget.sp_scale_y.set_immediate(1.0 - ratio * 0.11)
                else:
                    if widget.dock_edge is not None:
                        widget.dock_edge = None
                        widget.sp_scale_x.target = 1.0
                        widget.sp_scale_y.target = 1.0
                        widget.trigger_jelly(vx=-2.8, vy=2.0)
                    widget.sp_x.set_immediate(dock_x + pull_dx)
                    widget.sp_y.set_immediate(dock_y + pull_dy)
            elif t < 1.9:
                # Drag back toward right edge -> show snap preview zone
                mouse_down = True
                p = smoothstep((t - 1.25) / 0.65)
                cur_x = lerp(dock_x - 175, dock_x - 12, p)
                cur_y = lerp(dock_y + 65, dock_y, p)
                cursor_x = cur_x + w_med * 0.5
                cursor_y = cur_y + h_med * 0.5
                widget.sp_x.set_immediate(cur_x)
                widget.sp_y.set_immediate(cur_y)
                show_snap_zone = (p > 0.45)
                snap_rect = QRectF(dock_x, dock_y, widget.sp_w.value, widget.sp_h.value)
            else:
                # Release mouse -> snap into place with short 1.2s jelly bounce
                if mouse_down:
                    mouse_down = False
                    show_snap_zone = False
                    widget.dock_edge = "right"
                    widget.sp_x.target = dock_x
                    widget.sp_y.target = dock_y
                    widget.trigger_jelly(vx=-2.2, vy=1.6)

        # SCENE 2 (2.6s - 5.2s): Double-click to edit time with cursor -> Press Right Ctrl to Start!
        elif t < 5.2:
            caption = "2. Double-Click Text Edit & Writer Hotkeys (Right Ctrl)"
            if t < 3.1:
                p = smoothstep((t - 2.6) / 0.5)
                cursor_x = lerp(cursor_x, dock_x + w_med * 0.5, p)
                cursor_y = lerp(cursor_y, dock_y + h_med * 0.48, p)
                if t > 2.95 and not widget.editing_time:
                    mouse_down = True
                    widget.editing_time = True
                    widget.edit_text = "25:00"
                    widget.edit_cursor = 2
                    badge = "Double-Click → Edit"
            elif t < 4.0:
                mouse_down = False
                if t > 3.25 and widget.edit_text == "25:00":
                    widget.edit_text = "45:00"
                    widget.edit_cursor = 2
                    badge = "Typed: 45:00"
                if t > 3.75 and widget.editing_time:
                    widget.commit_time_edit()
                    badge = "Enter → Saved 45:00"
            else:
                # Move cursor away to document and press Right Ctrl global hotkey!
                p = smoothstep((t - 4.0) / 0.45)
                cursor_x = lerp(dock_x + w_med * 0.5, 320, p)
                cursor_y = lerp(dock_y + h_med * 0.48, 260, p)
                if t > 4.25 and not widget.is_running:
                    widget.is_running = True
                badge = "Right Ctrl → Start (Global)"

        # SCENE 3 (5.2s - 8.0s): Switch to Mini capsule while docked & switch browser tab!
        else:
            caption = "3. Sticky Dock Resize & Cross-Tab Browser Sync"
            badge = ""
            if t < 5.8:
                p = smoothstep((t - 5.2) / 0.5)
                # Move to expand/size icon
                cursor_x = lerp(320, widget.sp_x.value + widget.sp_w.value - 43, p)
                cursor_y = lerp(260, widget.sp_y.value + 21, p)
            elif t < 6.3:
                if widget.size_mode != "mini":
                    mouse_down = True
                    widget.size_mode = "mini"
                    w_mini, h_mini = widget.SIZES["mini"]
                    widget.sp_w.target = w_mini
                    widget.sp_h.target = h_mini
                    # Keep docked to right edge!
                    widget.sp_x.target = W - w_mini - 14
                    widget.trigger_jelly(vx=-1.8, vy=1.4)
                else:
                    mouse_down = False
            else:
                # Move cursor to 2nd Browser Tab and click it -> widget stays synced!
                p = smoothstep((t - 6.3) / 0.5)
                cursor_x = lerp(cursor_x, 56 + 90 + 210 + 95, p)
                cursor_y = lerp(cursor_y, 36 + 24, p)
                if t > 6.85:
                    active_tab = 1
                    badge = "Tab Switched → Synced!"

        # Advance timer countdown if running
        if widget.is_running:
            widget.timer_remaining -= dt * 12.0  # slightly accelerated so viewers see seconds ticking

        # Step physics springs
        widget.sp_x.step(dt)
        widget.sp_y.step(dt)
        widget.sp_w.step(dt)
        widget.sp_h.step(dt)
        widget.sp_scale_x.step(dt)
        widget.sp_scale_y.step(dt)

        # Render full frame onto QImage
        qimg = QImage(W, H, QImage.Format.Format_RGBA8888)
        qimg.fill(Qt.GlobalColor.transparent)

        p = QPainter(qimg)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        draw_mock_desktop(p, W, H, active_tab=active_tab)

        # Draw snap preview zone if active
        if show_snap_zone:
            p.save()
            p.setPen(QPen(QColor(255, 255, 255, 135), 1.5))
            p.setBrush(QColor(255, 255, 255, 28))
            p.drawRoundedRect(snap_rect, 14, 14)
            p.restore()

        # Render the JellyTimerWidget card onto our frame at (sp_x, sp_y) with jelly scale
        cw = max(40, int(round(widget.sp_w.value)))
        ch = max(30, int(round(widget.sp_h.value)))
        card_img = QImage(cw, ch, QImage.Format.Format_RGBA8888)
        card_img.fill(Qt.GlobalColor.transparent)
        cp = QPainter(card_img)
        cp.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        cp.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        theme = widget.THEMES["graphite"]
        widget.render_card_contents(cp, float(cw), float(ch), theme)
        cp.end()

        p.save()
        cx = widget.sp_x.value + cw / 2.0
        cy = widget.sp_y.value + ch / 2.0
        p.translate(cx, cy)
        p.scale(widget.sp_scale_x.value, widget.sp_scale_y.value)
        p.translate(-cw / 2.0, -ch / 2.0)
        p.drawImage(0, 0, card_img)
        p.restore()

        draw_cursor(p, cursor_x, cursor_y, pressed=mouse_down)
        draw_caption_banner(p, W, H, caption, badge=badge)
        p.end()

        # Convert QImage to PIL Image
        ptr = qimg.bits()
        ptr.setsize(W * H * 4)
        pil_img = Image.frombytes("RGBA", (W, H), bytes(ptr), "raw", "RGBA").convert("RGB")
        frames_pil.append(pil_img)

    gif_path = os.path.join(ASSETS_DIR, "demo.gif")
    # Save optimized high-fps animated GIF (every 2nd frame = 15fps smooth lightweight GIF for GitHub README)
    gif_frames = frames_pil[::2]
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=int(1000 / 15),
        loop=0,
        optimize=True
    )
    print(f"Saved animated demo GIF: {gif_path} ({os.path.getsize(gif_path) // 1024} KB)")

    # Save crisp hero screenshots of the 3 scenes for README / Product Hunt gallery
    frames_pil[28].save(os.path.join(ASSETS_DIR, "shot_1_jelly_peel.png"))
    frames_pil[105].save(os.path.join(ASSETS_DIR, "shot_2_inline_edit.png"))
    frames_pil[215].save(os.path.join(ASSETS_DIR, "shot_3_mini_synced.png"))
    print("Saved 3 hero screenshots in assets/")


if __name__ == "__main__":
    generate_demo()
