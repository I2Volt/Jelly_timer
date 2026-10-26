# Jelly Timer — Minimalist Floating Timer & Stopwatch

<p align="center">
  <img src="assets/demo.gif" alt="Jelly Timer Demo" width="840" />
</p>

<p align="center">
  <b>Always-on-top floating desktop & browser timer with magnetic edge-snap, elastic jelly peel-off physics, and writer-friendly global hotkeys.</b>
</p>

---

## ✨ Key Features (Free & Open-Source Edition)

- **🧲 Magnetic Edge-Snap & Elastic Jelly Peel-Off**  
  Throw the widget toward any screen border or corner (`left`, `right`, `top`, `bottom`, or all 4 corners) to preview the snap zone (just like Windows 11 Aero Snap). When pulling it away from a docked edge, it stretches elastically (`42px` peel threshold) and pops free with a crisp, unified spring recoil.
- **⌨️ Writer-Friendly Global Hotkeys (`Right Ctrl` / `Right Alt` / `Left` vs `Right` Modifiers)**  
  Control your timer while typing in Google Docs, Notion, or an IDE without ever leaving the keyboard or accidentally triggering shortcuts while typing normal words. Supports distinguishing **Left vs. Right** `Ctrl`, `Alt`, and `Shift` across Windows, macOS, and Linux.
- **✏️ Double-Click Inline Time Editing & Single-Click Drag**  
  Single-clicking anywhere on the widget (including directly on the digits) drags it smoothly. Double-clicking the timer digits opens an inline text cursor (`|`) with `←` / `→` / `Home` / `End` / `Backspace` / `Delete` / `Enter` navigation.
- **📐 Sticky Dock Resizing (`Mini` / `Medium` / `Large`)**  
  Switch between an ultra-compact pill (`Mini`, `208×66`), standard controller (`Medium`, `284×138`), and preset dashboard (`Large`, `348×195` with `5m / 15m / 25m / 45m / 60m` quick buttons). If docked to a screen edge or corner, resizing stays firmly anchored to that border.
- **🖱️ Mouse Wheel Controls & 3 Minimalist Themes**  
  Scroll the mouse wheel over a paused timer to adjust time by `±1 min`, or hold `Ctrl + Mouse Wheel` to smoothly adjust background opacity (`20%–100%`). Includes 3 clean dark themes: *Dark Graphite*, *Warm Espresso*, and *Soft Sage*.
- **🌐 Cross-Tab Synchronized Browser Extension (Manifest V3)**  
  Includes a ready-to-load Chromium / Firefox extension (`browser_extension/`) that synchronizes live countdowns, stopwatch state, position, dock edge, opacity, and size across all open browser tabs in real time using Shadow DOM isolation.

---

## 📸 Screenshots

| 1. Elastic Jelly Peel-Off | 2. Double-Click Inline Edit | 3. Sticky Mini Capsule & Sync |
| :---: | :---: | :---: |
| ![Peel](assets/shot_1_jelly_peel.png) | ![Edit](assets/shot_2_inline_edit.png) | ![Mini](assets/shot_3_mini_synced.png) |

---

## 🎮 Complete Controls & Shortcuts Reference

| Action | Mouse / UI Control | Default Hotkey (Customizable) |
| :--- | :--- | :--- |
| **Start / Pause** | Click `Старт / Пауза` button | `Space` (Desktop) / `Right Ctrl` (Browser) |
| **Reset Clock** | Click `↻` Reset button | `R` (Desktop) / `Right Alt` (Browser) |
| **Switch Timer ↔ Stopwatch** | Click top-left mode pill | `M` |
| **Cycle Size (`Mini`/`Med`/`Large`)** | Click `⤢` button or double-click background | `S` |
| **Inline Time Edit (`MM:SS`)** | **Double-click** directly on the timer digits | `Enter` to save, `Esc` to cancel |
| **Adjust Time (`±1 min`)** | Click `-1м` / `+1м` / `+5м` or **Scroll Wheel** | — |
| **Adjust Opacity (`20%–100%`)** | Click `◐` Opacity button or **`Ctrl + Scroll Wheel`** | — |
| **Context Menu & Themes** | **Right-click** anywhere on the desktop widget | — |

---

## 🚀 Quick Start (Desktop: Windows, macOS, Linux)

### 1. Run from Source
```bash
git clone https://github.com/I2Volt/Jelly_timer.git
cd Jelly_timer
pip install -r requirements.txt
python jelly_timer.pyw
```
To create a native Desktop / Application Menu shortcut on Windows (`.lnk`), Linux (`.desktop`), or macOS (`.command`):
```bash
python setup_shortcut.py
```

### 2. Build Standalone App (`.exe` / `.app` / Linux Binary)
```bash
pip install pyinstaller
pyinstaller --noconsole --windowed --onefile --name "JellyTimer" jelly_timer.pyw
```
Automated multi-OS builds are also configured via GitHub Actions in [`.github/workflows/release.yml`](.github/workflows/release.yml).

---

## 🌐 Install the Browser Extension (Chrome / Edge / Brave / Opera / Yandex)

1. Open `chrome://extensions/` in your browser.
2. Enable **Developer mode** (toggle in the top-right corner).
3. Click **Load unpacked** (`Загрузить распакованное расширение`) and select the [`browser_extension`](browser_extension) folder.
4. The floating timer will appear on your active tabs and stay synchronized in position and time across all tabs!

---

## 📄 License

Released under the [MIT License](LICENSE).
