import os
import sys
import math
from PIL import Image
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QImage, QPainter, QColor, QPen, QFont, QLinearGradient, QPainterPath, QPolygonF
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jelly_timer import JellyTimerWidget

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
STORE_ASSETS_DIR = os.path.join(ROOT_DIR, "dist", "chrome_web_store_assets")
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(STORE_ASSETS_DIR, exist_ok=True)


def lerp(a, b, t):
    return a + (b - a) * t


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def draw_windows_controls(painter: QPainter, right_x: float, top_y: float, h: float = 32.0):
    """Draws standard Windows minimize (—), maximize (□), and close (×) buttons on the top-right."""
    painter.save()
    pen = QPen(QColor(175, 175, 185), 1.3)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    cy = top_y + h * 0.5
    # Minimize (—)
    cx1 = right_x - 96
    painter.drawLine(QPointF(cx1 - 5, cy), QPointF(cx1 + 5, cy))
    # Maximize (□)
    cx2 = right_x - 56
    painter.drawRect(QRectF(cx2 - 4.5, cy - 4.5, 9, 9))
    # Close (×)
    cx3 = right_x - 18
    painter.drawLine(QPointF(cx3 - 4.5, cy - 4.5), QPointF(cx3 + 4.5, cy + 4.5))
    painter.drawLine(QPointF(cx3 + 4.5, cy - 4.5), QPointF(cx3 - 4.5, cy + 4.5))
    painter.restore()


def draw_browser_environment(painter: QPainter, W: int, H: int, active_tab: int = 0):
    """
    Draws a realistic Windows Chrome/Edge browser window with:
    - Tab bar (with favicons, close '×' buttons, '+' new tab, and Windows — □ × controls on right)
    - Address bar / Omnibox (← → ↻, lock icon + real URL matching the tab, and pinned Jelly Timer extension icon)
    - Rich, distinct webpage content for Tab 0 (DocSpace) and Tab 1 (CodeHub)
    """
    # 1. Subtle desktop backdrop
    bg = QLinearGradient(0, 0, W, H)
    bg.setColorAt(0.0, QColor(12, 13, 18))
    bg.setColorAt(1.0, QColor(18, 20, 27))
    painter.fillRect(0, 0, W, H, bg)

    # 2. Browser Window Frame
    bx, by, bw, bh = 28, 18, W - 56, H - 72
    b_rect = QRectF(bx, by, bw, bh)
    path = QPainterPath()
    path.addRoundedRect(b_rect, 10, 10)
    painter.fillPath(path, QColor(22, 23, 28))
    painter.setPen(QPen(QColor(52, 54, 64), 1.2))
    painter.drawPath(path)

    # 3. Top Tab Strip (y: by .. by+38)
    tab_strip = QRectF(bx, by, bw, 38)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(15, 16, 20))
    painter.drawRoundedRect(tab_strip, 10, 10)
    painter.fillRect(QRectF(bx, by + 18, bw, 20), QColor(15, 16, 20))

    tabs = [
        ("DocSpace — Product_Spec_2026", QColor(96, 165, 250)),
        ("CodeHub — pull-request #18", QColor(74, 222, 128)),
        ("BoardFlow — Sprint Q4", QColor(251, 191, 36)),
    ]
    for i, (title, fav_col) in enumerate(tabs):
        tx = bx + 14 + i * 226
        tw = 218
        t_rect = QRectF(tx, by + 6, tw, 32)
        if i == active_tab:
            painter.setBrush(QColor(28, 30, 36))
            painter.drawRoundedRect(t_rect, 7, 7)
            painter.fillRect(QRectF(tx, by + 26, tw, 12), QColor(28, 30, 36))
            txt_col = QColor(244, 244, 248)
        else:
            painter.setBrush(QColor(20, 21, 26))
            painter.drawRoundedRect(t_rect, 7, 7)
            txt_col = QColor(145, 148, 160)

        # Favicon badge
        painter.setBrush(fav_col)
        painter.drawRoundedRect(QRectF(tx + 10, by + 15, 12, 12), 3, 3)

        # Tab title
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        painter.setPen(txt_col)
        painter.drawText(t_rect.adjusted(28, 0, -24, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, title)

        # Tab close '×'
        painter.setPen(QPen(QColor(130, 132, 142), 1.2))
        cx_t = tx + tw - 14
        cy_t = by + 21
        painter.drawLine(QPointF(cx_t - 3, cy_t - 3), QPointF(cx_t + 3, cy_t + 3))
        painter.drawLine(QPointF(cx_t + 3, cy_t - 3), QPointF(cx_t - 3, cy_t + 3))
        painter.setPen(Qt.PenStyle.NoPen)

    # '+' New Tab icon
    plus_x = bx + 14 + len(tabs) * 226 + 10
    painter.setPen(QPen(QColor(160, 162, 172), 1.5))
    painter.drawLine(QPointF(plus_x - 4, by + 21), QPointF(plus_x + 4, by + 21))
    painter.drawLine(QPointF(plus_x, by + 17), QPointF(plus_x, by + 25))

    # Windows window controls (— □ ×) on top-right
    draw_windows_controls(painter, bx + bw, by, 36)

    # 4. Browser Navigation / Omnibox Bar (y: by+38 .. by+76)
    nav_y = by + 38
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(28, 30, 36))
    painter.fillRect(QRectF(bx + 1, nav_y, bw - 2, 38), QColor(28, 30, 36))
    painter.setPen(QPen(QColor(44, 46, 56), 1.0))
    painter.drawLine(QPointF(bx, nav_y + 38), QPointF(bx + bw, nav_y + 38))

    # Back / Forward / Reload icons
    painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
    painter.setPen(QColor(175, 178, 190))
    painter.drawText(QRectF(bx + 14, nav_y, 76, 38), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "←   →   ↻")

    # Address Bar (Omnibox)
    omni_rect = QRectF(bx + 98, nav_y + 6, bw - 210, 26)
    painter.setPen(QPen(QColor(56, 58, 70), 1.0))
    painter.setBrush(QColor(18, 19, 24))
    painter.drawRoundedRect(omni_rect, 13, 13)

    url_str = (
        "🔒  https://app.docspace.io/workspace/product-spec-2026"
        if active_tab == 0
        else "🔒  https://codehub.dev/core/jelly-ui/pull/18"
    )
    painter.setFont(QFont("Segoe UI", 8))
    painter.setPen(QColor(210, 212, 222))
    painter.drawText(omni_rect.adjusted(14, 0, -14, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, url_str)

    # Extension Toolbar Icon on right of Omnibox (Jelly Timer badge)
    ext_x = bx + bw - 96
    ext_rect = QRectF(ext_x, nav_y + 6, 82, 26)
    painter.setPen(QPen(QColor(72, 74, 86), 1.0))
    painter.setBrush(QColor(36, 38, 46))
    painter.drawRoundedRect(ext_rect, 7, 7)
    painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
    painter.setPen(QColor(244, 244, 245))
    painter.drawText(ext_rect, Qt.AlignmentFlag.AlignCenter, "⏱ Jelly Ext")

    # 5. Webpage Viewport Content (y: by+77 .. by+bh)
    vp_y = nav_y + 39
    vp_h = bh - 77

    if active_tab == 0:
        # TAB 0: DocSpace Workspace (Sidebar + Structured Spec Document + Task Table)
        side_w = 185
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(20, 21, 26))
        painter.fillRect(QRectF(bx + 1, vp_y, side_w, vp_h - 8), QColor(20, 21, 26))
        painter.setPen(QPen(QColor(40, 42, 50), 1.0))
        painter.drawLine(QPointF(bx + side_w, vp_y), QPointF(bx + side_w, vp_y + vp_h))

        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.setPen(QColor(140, 145, 160))
        painter.drawText(QPointF(bx + 18, vp_y + 26), "DOCSPACE WORKSPACE")

        nav_items = [
            ("📄  Product_Spec_2026", True),
            ("📐  UI_Spring_Physics", False),
            ("🗂  Q4_Roadmap_Board", False),
            ("📊  Focus_Metrics_Report", False),
            ("⚙  Team_Settings", False),
        ]
        for idx, (label, is_sel) in enumerate(nav_items):
            iy = vp_y + 40 + idx * 30
            ir = QRectF(bx + 10, iy, side_w - 20, 25)
            if is_sel:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(38, 42, 54))
                painter.drawRoundedRect(ir, 5, 5)
                painter.setPen(QColor(245, 246, 250))
            else:
                painter.setPen(QColor(150, 154, 168))
            painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold if is_sel else QFont.Weight.Normal))
            painter.drawText(ir.adjusted(8, 0, 0, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, label)

        # Main Document Canvas
        dx = bx + side_w + 34
        dy = vp_y + 34
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.setPen(QColor(242, 244, 248))
        painter.drawText(QPointF(dx, dy), "Product Specification — Release v1.2")

        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor(155, 160, 175))
        painter.drawText(QPointF(dx, dy + 24), "Updated today in DocSpace • Status: Ready for Review")

        # Checklist Cards inside DocSpace
        tasks = [
            ("✓", QColor(74, 222, 128), "Magnetic edge-snap & elastic jelly peel-off physics (60 FPS)"),
            ("✓", QColor(74, 222, 128), "Cross-tab real-time state sync across all open browser tabs"),
            ("✓", QColor(74, 222, 128), "Writer-friendly Summon hotkey (Right Shift) & Mouse Wheel controls"),
        ]
        for idx, (chk, col, text_line) in enumerate(tasks):
            cy_row = dy + 44 + idx * 34
            row_r = QRectF(dx, cy_row, 500, 28)
            painter.setPen(QPen(QColor(44, 46, 56), 1.0))
            painter.setBrush(QColor(28, 30, 37))
            painter.drawRoundedRect(row_r, 6, 6)
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            painter.setPen(col)
            painter.drawText(QRectF(dx + 10, cy_row, 20, 28), Qt.AlignmentFlag.AlignCenter, chk)
            painter.setFont(QFont("Segoe UI", 9))
            painter.setPen(QColor(220, 222, 230))
            painter.drawText(row_r.adjusted(34, 0, -10, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text_line)

        # Sprint Milestone Table
        ty_start = dy + 162
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor(200, 204, 216))
        painter.drawText(QPointF(dx, ty_start), "Sprint Milestones & Deliverables")

        table_rows = [
            ("Module", "Owner", "Progress", "Target"),
            ("Spring Physics Engine", "Core UI", "100% Complete", "v1.2"),
            ("Shadow DOM Isolation", "Browser Ext", "100% Verified", "v1.2"),
            ("Cross-Tab Storage Sync", "State Sync", "Active", "v1.2"),
        ]
        for r_idx, row_vals in enumerate(table_rows):
            ry = ty_start + 12 + r_idx * 26
            bg_c = QColor(32, 34, 42) if r_idx == 0 else QColor(25, 27, 33)
            painter.setPen(QPen(QColor(42, 44, 54), 1.0))
            painter.setBrush(bg_c)
            painter.drawRect(QRectF(dx, ry, 500, 26))
            painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold if r_idx == 0 else QFont.Weight.Normal))
            painter.setPen(QColor(170, 175, 190) if r_idx == 0 else QColor(215, 218, 226))
            col_offsets = [12, 185, 305, 435]
            for c_idx, val in enumerate(row_vals):
                painter.drawText(QRectF(dx + col_offsets[c_idx], ry, 160, 26), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, val)

    else:
        # TAB 1: CodeHub Pull Request Diff Viewer (completely different layout & content!)
        dx = bx + 32
        dy = vp_y + 28
        painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        painter.setPen(QColor(242, 244, 248))
        painter.drawText(QPointF(dx, dy), "core / jelly-ui  —  Pull Request #18: Spring physics & tab sync")

        # Open PR badge
        badge_r = QRectF(dx, dy + 12, 86, 22)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(22, 163, 74))
        painter.drawRoundedRect(badge_r, 11, 11)
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.setPen(QColor(250, 250, 252))
        painter.drawText(badge_r, Qt.AlignmentFlag.AlignCenter, "● Open PR")

        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        painter.setPen(QColor(160, 165, 180))
        painter.drawText(QPointF(dx + 102, dy + 27), "Conversation (3)     Commits (4)     Files changed (2)")

        # Code Diff Box
        diff_box = QRectF(dx, dy + 46, bw - 64, vp_h - 92)
        painter.setPen(QPen(QColor(48, 52, 64), 1.0))
        painter.setBrush(QColor(16, 18, 23))
        painter.drawRoundedRect(diff_box, 8, 8)

        # File header inside diff box
        painter.setBrush(QColor(26, 29, 37))
        painter.drawRoundedRect(QRectF(dx + 1, dy + 47, bw - 66, 28), 7, 7)
        painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        painter.setPen(QColor(200, 206, 220))
        painter.drawText(QPointF(dx + 14, dy + 65), "src/spring_controller.ts   (+18 -4)")

        diff_lines = [
            (" 41", "  export class SpringController {", None),
            (" 42", "-   private stiffness = 180;", QColor(120, 28, 36, 95)),
            (" 43", "+   private stiffness = 360; // Snappy magnetic dock response", QColor(22, 101, 52, 95)),
            (" 44", "+   private damping = 29;    // Zero-overshoot equilibrium", QColor(22, 101, 52, 95)),
            (" 45", "    public step(dt: number): number {", None),
            (" 46", "      const force = (this.target - this.value) * this.stiffness;", None),
            (" 47", "+     this.velocity = (this.velocity + force * dt) * Math.exp(-this.damping * dt);", QColor(22, 101, 52, 95)),
            (" 48", "      return (this.value += this.velocity * dt);", None),
            (" 49", "    }", None),
            (" 50", "  }", None),
        ]
        painter.setFont(QFont("Consolas", 8))
        for idx, (lnum, code_txt, row_bg) in enumerate(diff_lines):
            ly = dy + 80 + idx * 22
            if row_bg:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(row_bg)
                painter.drawRect(QRectF(dx + 2, ly, bw - 68, 21))
            painter.setPen(QColor(100, 106, 122))
            painter.drawText(QPointF(dx + 10, ly + 15), lnum)
            if code_txt.startswith("+"):
                painter.setPen(QColor(134, 239, 172))
            elif code_txt.startswith("-"):
                painter.setPen(QColor(252, 165, 165))
            else:
                painter.setPen(QColor(212, 216, 228))
            painter.drawText(QPointF(dx + 44, ly + 15), code_txt)


def draw_desktop_two_apps(painter: QPainter, W: int, H: int, active_app: int = 0):
    """
    Draws a realistic Windows Desktop with 2 distinct applications open (no Mac dots!):
    - App 0 (Left): DevStudio IDE — app_controller.py (Code editor + file tree + terminal)
    - App 1 (Right): WritePad — Заметки_проекта.md (Notes & task editor)
    - Bottom Windows Taskbar
    """
    # 1. Desktop Wallpaper
    bg = QLinearGradient(0, 0, W, H)
    bg.setColorAt(0.0, QColor(14, 18, 26))
    bg.setColorAt(1.0, QColor(22, 28, 40))
    painter.fillRect(0, 0, W, H, bg)

    # 2. App 0 Window (Left: DevStudio IDE)
    w1_rect = QRectF(24, 20, 520, H - 92)
    brd1 = QColor(82, 130, 220) if active_app == 0 else QColor(52, 56, 68)
    painter.setPen(QPen(brd1, 1.5 if active_app == 0 else 1.0))
    painter.setBrush(QColor(19, 21, 27))
    painter.drawRoundedRect(w1_rect, 9, 9)

    # Titlebar App 0
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(14, 15, 20))
    painter.drawRoundedRect(QRectF(24, 20, 520, 32), 9, 9)
    painter.fillRect(QRectF(24, 38, 520, 14), QColor(14, 15, 20))
    painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
    painter.setPen(QColor(235, 238, 245) if active_app == 0 else QColor(145, 150, 162))
    painter.drawText(QRectF(38, 20, 320, 32), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "💻  DevStudio IDE — app_controller.py")
    draw_windows_controls(painter, 24 + 520, 20, 32)

    # Sidebar + Code inside App 0
    painter.fillRect(QRectF(25, 52, 120, H - 125), QColor(16, 17, 22))
    painter.setFont(QFont("Segoe UI", 8))
    painter.setPen(QColor(140, 146, 160))
    for idx, fn in enumerate(["📁 src", "  🐍 main.py", "  🐍 physics.py", "  🐍 timer_ui.py", "  ⚙ config.json"]):
        painter.drawText(QPointF(34, 76 + idx * 22), fn)

    code_lines = [
        ("class FocusController:", QColor(147, 197, 253)),
        ("    def __init__(self, duration_min=25):", QColor(212, 216, 228)),
        ("        self.remaining = duration_min * 60.0", QColor(167, 243, 208)),
        ("        self.stopwatch = 0.0", QColor(167, 243, 208)),
        ("        self.always_on_top = True", QColor(253, 224, 71)),
        ("", QColor(200, 200, 200)),
        ("    def tick_frame(self, dt: float):", QColor(147, 197, 253)),
        ("        # Smooth 60 FPS spring step", QColor(115, 122, 140)),
        ("        self.spring_x.step(dt)", QColor(212, 216, 228)),
        ("        self.spring_y.step(dt)", QColor(212, 216, 228)),
    ]
    painter.setFont(QFont("Consolas", 8))
    for idx, (ln, col) in enumerate(code_lines):
        painter.setPen(col)
        painter.drawText(QPointF(158, 78 + idx * 21), ln)

    # Terminal panel at bottom of App 0
    term_y = H - 158
    painter.fillRect(QRectF(145, term_y, 398, 84), QColor(13, 14, 18))
    painter.setPen(QPen(QColor(40, 44, 54), 1.0))
    painter.drawLine(QPointF(145, term_y), QPointF(543, term_y))
    painter.setFont(QFont("Consolas", 8))
    painter.setPen(QColor(74, 222, 128))
    painter.drawText(QPointF(158, term_y + 24), "PS C:\\project> python main.py --verify")
    painter.setPen(QColor(180, 185, 198))
    painter.drawText(QPointF(158, term_y + 44), "[OK] Build verified in 0.42s • 0 warnings")

    # 3. App 1 Window (Right: WritePad — Заметки_проекта.md)
    w2_rect = QRectF(488, 42, W - 512, H - 114)
    brd2 = QColor(82, 130, 220) if active_app == 1 else QColor(52, 56, 68)
    painter.setPen(QPen(brd2, 1.6 if active_app == 1 else 1.0))
    painter.setBrush(QColor(23, 25, 31))
    painter.drawRoundedRect(w2_rect, 9, 9)

    # Titlebar App 1
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(16, 18, 23))
    painter.drawRoundedRect(QRectF(488, 42, W - 512, 32), 9, 9)
    painter.fillRect(QRectF(488, 60, W - 512, 14), QColor(16, 18, 23))
    painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
    painter.setPen(QColor(240, 242, 248) if active_app == 1 else QColor(150, 154, 166))
    painter.drawText(QRectF(502, 42, 280, 32), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "📝  WritePad — Заметки_проекта.md")
    draw_windows_controls(painter, W - 24, 42, 32)

    # Notes content inside App 1
    nx = 510
    ny = 102
    painter.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
    painter.setPen(QColor(240, 242, 248))
    painter.drawText(QPointF(nx, ny), "План релиза и задачи на день")

    note_items = [
        "• Таймер и Секундомер поверх любых программ",
        "• Упругое прилипание к краям и углам экрана",
        "• Вызов клавишей Right Shift без отрыва от текста",
        "• Быстрое переключение: Таймер ⇄ Секундомер",
        "• 3 удобных размера: Мини, Средний и Большой",
    ]
    painter.setFont(QFont("Segoe UI", 9))
    painter.setPen(QColor(185, 190, 205))
    for idx, item in enumerate(note_items):
        painter.drawText(QPointF(nx, ny + 32 + idx * 28), item)

    # Active indicator pill inside App 1
    status_r = QRectF(nx, ny + 185, 310, 32)
    painter.setPen(QPen(QColor(60, 64, 78), 1.0))
    painter.setBrush(QColor(30, 33, 42))
    painter.drawRoundedRect(status_r, 7, 7)
    painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
    painter.setPen(QColor(215, 220, 232))
    painter.drawText(
        status_r,
        Qt.AlignmentFlag.AlignCenter,
        "Активное окно: WritePad" if active_app == 1 else "Фоновое окно: WritePad"
    )


def draw_cursor(painter: QPainter, x: float, y: float, pressed: bool = False):
    painter.save()
    painter.translate(x, y)
    if pressed:
        painter.setPen(QPen(QColor(255, 255, 255, 175), 2.0))
        painter.setBrush(QColor(255, 255, 255, 50))
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
    bw = 620
    bh = 38
    bx = (W - bw) / 2
    by = H - 46
    rect = QRectF(bx, by, bw, bh)

    painter.setPen(QPen(QColor(82, 84, 96, 210), 1.0))
    painter.setBrush(QColor(16, 17, 22, 238))
    painter.drawRoundedRect(rect, 19, 19)

    painter.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
    painter.setPen(QColor(245, 245, 248))
    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, title)

    if badge:
        kr = QRectF(56, H - 102, 315, 34)
        painter.setPen(QPen(QColor(244, 244, 245, 200), 1.2))
        painter.setBrush(QColor(26, 28, 35, 240))
        painter.drawRoundedRect(kr, 8, 8)
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(QColor(250, 250, 252))
        painter.drawText(kr, Qt.AlignmentFlag.AlignCenter, f"⌨  {badge}")

    painter.restore()


def render_widget_onto_frame(painter: QPainter, widget: JellyTimerWidget):
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

    painter.save()
    cx = widget.sp_x.value + cw / 2.0
    cy = widget.sp_y.value + ch / 2.0
    painter.translate(cx, cy)
    painter.scale(widget.sp_scale_x.value, widget.sp_scale_y.value)
    painter.translate(-cw / 2.0, -ch / 2.0)
    painter.drawImage(0, 0, card_img)
    painter.restore()


def generate_extension_video_and_store_shots():
    """Generates Video #1 (Browser Extension Demo) + 1280x800 Chrome Web Store screenshots."""
    W, H = 960, 540
    fps = 30
    dt = 1.0 / fps
    total_frames = 240

    widget = JellyTimerWidget()
    widget.mode = "timer"
    widget.size_mode = "medium"
    widget.theme_key = "graphite"
    widget.bg_opacity = 0.92
    widget.timer_total = 25 * 60.0
    widget.timer_remaining = 25 * 60.0
    widget.is_running = False
    widget.summoned_focus = False

    w_med, h_med = widget.SIZES["medium"]
    dock_x = W - w_med - 42
    dock_y = 106
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

        # SCENE 1 (0.0s - 2.6s): Magnetic Edge-Snap & Elastic Jelly Peel-Off inside DocSpace tab
        if t < 2.6:
            caption = "1. Браузерное расширение: магнитные края и упругий желейный отрыв"
            badge = ""
            active_tab = 0
            if t < 0.45:
                p = smoothstep(t / 0.45)
                cursor_x = lerp(W * 0.52, dock_x + w_med * 0.5, p)
                cursor_y = lerp(H * 0.52, dock_y + h_med * 0.5, p)
                mouse_down = False
            elif t < 1.25:
                mouse_down = True
                p = smoothstep((t - 0.45) / 0.8)
                pull_dx = -lerp(0, 175, p)
                pull_dy = lerp(0, 58, p)
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
                mouse_down = True
                p = smoothstep((t - 1.25) / 0.65)
                cur_x = lerp(dock_x - 175, dock_x - 10, p)
                cur_y = lerp(dock_y + 58, dock_y, p)
                cursor_x = cur_x + w_med * 0.5
                cursor_y = cur_y + h_med * 0.5
                widget.sp_x.set_immediate(cur_x)
                widget.sp_y.set_immediate(cur_y)
                show_snap_zone = (p > 0.4)
                snap_rect = QRectF(dock_x, dock_y, widget.sp_w.value, widget.sp_h.value)
            else:
                if mouse_down:
                    mouse_down = False
                    show_snap_zone = False
                    widget.dock_edge = "right"
                    widget.sp_x.target = dock_x
                    widget.sp_y.target = dock_y
                    widget.trigger_jelly(vx=-2.2, vy=1.6)

        # SCENE 2 (2.6s - 5.2s): Double-click inline time edit & Right Shift Summon + Space Start
        elif t < 5.2:
            caption = "2. Двойной клик для ввода времени и вызов клавишей Right Shift"
            if t < 3.1:
                p = smoothstep((t - 2.6) / 0.5)
                cursor_x = lerp(cursor_x, dock_x + w_med * 0.5, p)
                cursor_y = lerp(cursor_y, dock_y + h_med * 0.48, p)
                if t > 2.95 and not widget.editing_time:
                    mouse_down = True
                    widget.editing_time = True
                    widget.edit_text = "25:00"
                    widget.edit_cursor = 2
                    badge = "Двойной клик → Ввод"
            elif t < 4.0:
                mouse_down = False
                if t > 3.25 and widget.edit_text == "25:00":
                    widget.edit_text = "15:00"
                    widget.edit_cursor = 2
                    badge = "Введено: 15:00"
                if t > 3.75 and widget.editing_time:
                    widget.commit_time_edit()
                    badge = "Enter → Сохранено 15:00"
            else:
                p = smoothstep((t - 4.0) / 0.45)
                cursor_x = lerp(dock_x + w_med * 0.5, 340, p)
                cursor_y = lerp(dock_y + h_med * 0.48, 250, p)
                widget.summoned_focus = True
                if t > 4.25 and not widget.is_running:
                    widget.is_running = True
                badge = "Right Shift + Space → Старт"

        # SCENE 3 (5.2s - 8.0s): Shrink to Mini capsule & switch browser tab (DocSpace -> CodeHub)
        else:
            caption = "3. Компактная мини-пилюля и синхронизация между вкладками браузера"
            widget.summoned_focus = False
            badge = ""
            if t < 5.75:
                p = smoothstep((t - 5.2) / 0.5)
                cursor_x = lerp(340, widget.sp_x.value + widget.sp_w.value - 66, p)
                cursor_y = lerp(250, widget.sp_y.value + 21, p)
            elif t < 6.25:
                if widget.size_mode != "mini":
                    mouse_down = True
                    widget.size_mode = "mini"
                    w_mini, h_mini = widget.SIZES["mini"]
                    widget.sp_w.target = w_mini
                    widget.sp_h.target = h_mini
                    widget.sp_x.target = W - w_mini - 42
                    widget.trigger_jelly(vx=-1.8, vy=1.4)
                else:
                    mouse_down = False
            else:
                # Move cursor to 2nd Browser Tab ("CodeHub — pull-request #18") and click it
                p = smoothstep((t - 6.25) / 0.5)
                cursor_x = lerp(cursor_x, 28 + 14 + 226 + 105, p)
                cursor_y = lerp(cursor_y, 18 + 22, p)
                if t > 6.8:
                    active_tab = 1
                    badge = "Смена вкладки → Таймер синхронизирован!"

        if widget.is_running:
            widget.timer_remaining -= dt * 10.0

        widget.sp_x.step(dt)
        widget.sp_y.step(dt)
        widget.sp_w.step(dt)
        widget.sp_h.step(dt)
        widget.sp_scale_x.step(dt)
        widget.sp_scale_y.step(dt)

        qimg = QImage(W, H, QImage.Format.Format_RGBA8888)
        qimg.fill(Qt.GlobalColor.transparent)
        p = QPainter(qimg)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        draw_browser_environment(p, W, H, active_tab=active_tab)

        if show_snap_zone:
            p.save()
            p.setPen(QPen(QColor(255, 255, 255, 145), 1.5))
            p.setBrush(QColor(255, 255, 255, 30))
            p.drawRoundedRect(snap_rect, 14, 14)
            p.restore()

        render_widget_onto_frame(p, widget)
        draw_cursor(p, cursor_x, cursor_y, pressed=mouse_down)
        draw_caption_banner(p, W, H, caption, badge=badge)
        p.end()

        ptr = qimg.bits()
        ptr.setsize(W * H * 4)
        pil_img = Image.frombytes("RGBA", (W, H), bytes(ptr), "raw", "RGBA").convert("RGB")
        frames_pil.append(pil_img)

    ext_gif = os.path.join(ASSETS_DIR, "demo_extension.gif")
    gif_frames = frames_pil[::2]
    gif_frames[0].save(
        ext_gif,
        save_all=True,
        append_images=gif_frames[1:],
        duration=int(1000 / 15),
        loop=0,
        optimize=True,
    )
    print(f"[OK] Saved Browser Extension demo GIF: {ext_gif} ({os.path.getsize(ext_gif) // 1024} KB)")

    # Save 3 extension screenshots (both 960x540 in assets/ and 1280x800 in dist/chrome_web_store_assets/)
    shot_indices = [28, 105, 218]
    for idx, f_idx in enumerate(shot_indices, 1):
        shot_rgb = frames_pil[f_idx]
        shot_rgb.save(os.path.join(ASSETS_DIR, f"ext_shot_{idx}.png"), format="PNG")

        scaled = shot_rgb.resize((1200, 675), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (1280, 800), (12, 13, 18))
        canvas.paste(scaled, ((1280 - 1200) // 2, (800 - 675) // 2))
        canvas.save(os.path.join(STORE_ASSETS_DIR, f"store_screenshot_{idx}_1280x800.png"), format="PNG")
    print("[OK] Saved 1280x800 Chrome Web Store screenshots in dist/chrome_web_store_assets/")


def generate_desktop_video_and_shots():
    """
    Generates Video #2 (Desktop App Demo) + screenshots showing:
    - 2 different Windows programs (DevStudio IDE & WritePad) without Mac buttons
    - Both skills: Countdown Timer AND Stopwatch (00:00.0) staying Always-On-Top across both apps!
    """
    W, H = 960, 540
    fps = 30
    dt = 1.0 / fps
    total_frames = 240

    widget = JellyTimerWidget()
    widget.mode = "timer"
    widget.size_mode = "medium"
    widget.theme_key = "graphite"
    widget.bg_opacity = 0.92
    widget.timer_total = 25 * 60.0
    widget.timer_remaining = 25 * 60.0
    widget.stopwatch_elapsed = 0.0
    widget.is_running = True
    widget.summoned_focus = False

    w_med, h_med = widget.SIZES["medium"]
    dock_x = W - w_med - 36
    dock_y = 82
    widget.sp_x.set_immediate(dock_x)
    widget.sp_y.set_immediate(dock_y)
    widget.sp_w.set_immediate(w_med)
    widget.sp_h.set_immediate(h_med)
    widget.dock_edge = "right"

    frames_pil = []
    cursor_x, cursor_y = W * 0.45, H * 0.5
    mouse_down = False
    active_app = 0
    caption = ""
    badge = ""
    show_snap_zone = False
    snap_rect = QRectF(dock_x, dock_y, w_med, h_med)

    for f in range(total_frames):
        t = f / float(fps)

        # SCENE 1 (0.0s - 2.6s): Over DevStudio IDE -> Elastic Jelly Peel-Off & Snap Back while Timer runs
        if t < 2.6:
            caption = "1. Десктоп: поверх всех программ, магнитные края и желейная физика"
            badge = ""
            active_app = 0
            if t < 0.45:
                p = smoothstep(t / 0.45)
                cursor_x = lerp(W * 0.45, dock_x + w_med * 0.5, p)
                cursor_y = lerp(H * 0.5, dock_y + h_med * 0.5, p)
                mouse_down = False
            elif t < 1.25:
                mouse_down = True
                p = smoothstep((t - 0.45) / 0.8)
                pull_dx = -lerp(0, 185, p)
                pull_dy = lerp(0, 62, p)
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
                mouse_down = True
                p = smoothstep((t - 1.25) / 0.65)
                cur_x = lerp(dock_x - 185, dock_x - 10, p)
                cur_y = lerp(dock_y + 62, dock_y, p)
                cursor_x = cur_x + w_med * 0.5
                cursor_y = cur_y + h_med * 0.5
                widget.sp_x.set_immediate(cur_x)
                widget.sp_y.set_immediate(cur_y)
                show_snap_zone = (p > 0.4)
                snap_rect = QRectF(dock_x, dock_y, widget.sp_w.value, widget.sp_h.value)
            else:
                if mouse_down:
                    mouse_down = False
                    show_snap_zone = False
                    widget.dock_edge = "right"
                    widget.sp_x.target = dock_x
                    widget.sp_y.target = dock_y
                    widget.trigger_jelly(vx=-2.2, vy=1.6)

        # SCENE 2 (2.6s - 5.2s): Switch active program to WritePad + Double-click edit & Right Shift Summon
        elif t < 5.2:
            caption = "2. Работа поверх разных программ (IDE / WritePad) и горячие клавиши"
            if t < 3.1:
                p = smoothstep((t - 2.6) / 0.5)
                cursor_x = lerp(cursor_x, 620, p)
                cursor_y = lerp(cursor_y, 260, p)
                if t > 2.9:
                    active_app = 1
                    badge = "Переключили окно → Таймер поверх!"
            elif t < 3.9:
                p = smoothstep((t - 3.1) / 0.45)
                cursor_x = lerp(620, dock_x + w_med * 0.5, p)
                cursor_y = lerp(260, dock_y + h_med * 0.48, p)
                if t > 3.55 and not widget.editing_time:
                    widget.is_running = False
                    widget.editing_time = True
                    widget.edit_text = "45:00"
                    widget.edit_cursor = 2
                    badge = "Двойной клик → 45:00"
            else:
                if widget.editing_time:
                    widget.commit_time_edit()
                widget.summoned_focus = True
                widget.is_running = True
                badge = "Right Shift → Вызов с клавиатуры"

        # SCENE 3 (5.2s - 8.0s): Switch Mode (Таймер -> Секундомер) & Resize to Mini Capsule
        else:
            caption = "3. Два режима в одном: Таймер обратного отсчёта и точный Секундомер"
            widget.summoned_focus = False
            if t < 5.75:
                p = smoothstep((t - 5.2) / 0.5)
                # Move cursor to top-left Mode Pill ("Таймер ⇅")
                cursor_x = lerp(cursor_x, widget.sp_x.value + 52, p)
                cursor_y = lerp(cursor_y, widget.sp_y.value + 21, p)
            elif t < 6.9:
                if widget.mode != "stopwatch":
                    mouse_down = True
                    widget.mode = "stopwatch"
                    widget.stopwatch_elapsed = 12.4
                    widget.is_running = True
                    widget.trigger_jelly(vx=1.6, vy=-1.4)
                else:
                    mouse_down = False
                badge = "Режим: Секундомер (00:12.4+)"
            else:
                # Also show compact Mini mode with Stopwatch running
                if widget.size_mode != "mini":
                    widget.size_mode = "mini"
                    w_mini, h_mini = widget.SIZES["mini"]
                    widget.sp_w.target = w_mini
                    widget.sp_h.target = h_mini
                    widget.sp_x.target = W - w_mini - 36
                    widget.trigger_jelly(vx=-1.8, vy=1.4)
                badge = "Секундомер в Мини-режиме"

        if widget.is_running:
            if widget.mode == "timer":
                widget.timer_remaining -= dt * 10.0
            else:
                widget.stopwatch_elapsed += dt * 4.5

        widget.sp_x.step(dt)
        widget.sp_y.step(dt)
        widget.sp_w.step(dt)
        widget.sp_h.step(dt)
        widget.sp_scale_x.step(dt)
        widget.sp_scale_y.step(dt)

        qimg = QImage(W, H, QImage.Format.Format_RGBA8888)
        qimg.fill(Qt.GlobalColor.transparent)
        p = QPainter(qimg)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        draw_desktop_two_apps(p, W, H, active_app=active_app)

        if show_snap_zone:
            p.save()
            p.setPen(QPen(QColor(255, 255, 255, 145), 1.5))
            p.setBrush(QColor(255, 255, 255, 30))
            p.drawRoundedRect(snap_rect, 14, 14)
            p.restore()

        render_widget_onto_frame(p, widget)
        draw_cursor(p, cursor_x, cursor_y, pressed=mouse_down)
        draw_caption_banner(p, W, H, caption, badge=badge)
        p.end()

        ptr = qimg.bits()
        ptr.setsize(W * H * 4)
        pil_img = Image.frombytes("RGBA", (W, H), bytes(ptr), "raw", "RGBA").convert("RGB")
        frames_pil.append(pil_img)

    for gif_name in ("demo_desktop.gif", "demo.gif"):
        gif_path = os.path.join(ASSETS_DIR, gif_name)
        gif_frames = frames_pil[::2]
        gif_frames[0].save(
            gif_path,
            save_all=True,
            append_images=gif_frames[1:],
            duration=int(1000 / 15),
            loop=0,
            optimize=True,
        )
    print(f"[OK] Saved Desktop demo GIF: assets/demo_desktop.gif & assets/demo.gif")

    frames_pil[28].save(os.path.join(ASSETS_DIR, "shot_1_jelly_peel.png"), format="PNG")
    frames_pil[112].save(os.path.join(ASSETS_DIR, "shot_2_inline_edit.png"), format="PNG")
    frames_pil[195].save(os.path.join(ASSETS_DIR, "shot_3_mini_synced.png"), format="PNG")
    print("[OK] Saved 3 Desktop screenshots in assets/")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    generate_extension_video_and_store_shots()
    generate_desktop_video_and_shots()
