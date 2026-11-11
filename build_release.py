"""
Единый скрипт версионного контроля и сборки релизов/экспортов:
- Синхронизирует версию и номер экспорта (Export #XX) из version_info.json
  во все файлы: jelly_timer.py/.pyw, jelly_timer_pro.py/.pyw, browser_extension/*
- Генерирует метаданные Windows (file_version_info.txt) для .exe
- Собирает JellyTimerPlus.exe через PyInstaller
- Упаковывает готовый архив расширения для Chrome Web Store / Firefox Add-ons
- Обновляет папки в «Поделиться/», создаёт VERSION.txt и архивы с номером версии и экспорта.

Использование:
  python build_release.py                  # Собрать текущую версию из version_info.json
  python build_release.py --bump-export    # Увеличить номер экспорта (+1) и пересобрать всё
  python build_release.py --version 1.3.0  # Установить новую версию и пересобрать всё
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_JSON = os.path.join(ROOT_DIR, "version_info.json")


def load_version_info() -> dict:
    with open(VERSION_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_version_info(meta: dict):
    with open(VERSION_JSON, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)


def update_python_script_version(py_path: str, pyw_path: str, app_ver: str, exp_num: int, build_date: str):
    with open(py_path, "r", encoding="utf-8") as f:
        code = f.read()

    code = re.sub(r'APP_VERSION\s*=\s*"[^"]*"', f'APP_VERSION = "{app_ver}"', code)
    code = re.sub(r'EXPORT_BUILD\s*=\s*\d+', f'EXPORT_BUILD = {exp_num}', code)
    code = re.sub(r'BUILD_DATE\s*=\s*"[^"]*"', f'BUILD_DATE = "{build_date}"', code)

    with open(py_path, "w", encoding="utf-8") as f:
        f.write(code)
    shutil.copyfile(py_path, pyw_path)
    print(f"[OK] Синхронизированы {os.path.basename(py_path)} и {os.path.basename(pyw_path)} -> v{app_ver} (Exp #{exp_num:02d})")


def update_browser_extension_version(ext_ver: str, exp_num: int, build_date: str):
    manifest_path = os.path.join(ROOT_DIR, "browser_extension", "manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    manifest["version"] = ext_ver
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    bg_path = os.path.join(ROOT_DIR, "browser_extension", "background.js")
    with open(bg_path, "r", encoding="utf-8") as f:
        bg = f.read()
    bg = re.sub(r'const EXT_VERSION\s*=\s*"[^"]*";', f'const EXT_VERSION = "{ext_ver}";', bg)
    bg = re.sub(r'const EXPORT_BUILD\s*=\s*\d+;', f'const EXPORT_BUILD = {exp_num};', bg)
    bg = re.sub(r'const BUILD_DATE\s*=\s*"[^"]*";', f'const BUILD_DATE = "{build_date}";', bg)
    with open(bg_path, "w", encoding="utf-8") as f:
        f.write(bg)

    html_path = os.path.join(ROOT_DIR, "browser_extension", "pro_upgrade.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        html = re.sub(
            r'Package: v[0-9.]+ • Export #\d+ \([0-9-]+\)',
            f'Package: v{ext_ver} • Export #{exp_num:02d} ({build_date})',
            html
        )
        html = re.sub(
            r'v[0-9.]+ • Exp #\d+',
            f'v{ext_ver} • Exp #{exp_num:02d}',
            html
        )
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

    popup_path = os.path.join(ROOT_DIR, "browser_extension", "popup.html")
    if os.path.exists(popup_path):
        with open(popup_path, "r", encoding="utf-8") as f:
            phtml = f.read()
        phtml = re.sub(r'id="pBadge">v[0-9.]+<', f'id="pBadge">v{ext_ver}<', phtml)
        with open(popup_path, "w", encoding="utf-8") as f:
            f.write(phtml)

    pro_js_path = os.path.join(ROOT_DIR, "browser_extension", "pro_upgrade.js")
    if os.path.exists(pro_js_path):
        with open(pro_js_path, "r", encoding="utf-8") as f:
            pjs = f.read()
        pjs = re.sub(r'let bestExp = \d+;', f'let bestExp = {exp_num};', pjs)
        pjs = re.sub(r'let bestDate = "[^"]*";', f'let bestDate = "{build_date}";', pjs)
        with open(pro_js_path, "w", encoding="utf-8") as f:
            f.write(pjs)

    content_js_path = os.path.join(ROOT_DIR, "browser_extension", "content.js")
    if os.path.exists(content_js_path):
        with open(content_js_path, "r", encoding="utf-8") as f:
            cjs = f.read()
        cjs = re.sub(r'const ver = state\.appVersion \|\| "[^"]*";', f'const ver = state.appVersion || "{ext_ver}";', cjs)
        cjs = re.sub(r'const exp = String\(state\.exportBuild \|\| \d+\)', f'const exp = String(state.exportBuild || {exp_num})', cjs)
        with open(content_js_path, "w", encoding="utf-8") as f:
            f.write(cjs)

    docs_path = os.path.join(ROOT_DIR, "docs", "index.html")
    if os.path.exists(docs_path):
        with open(docs_path, "r", encoding="utf-8") as f:
            dhtml = f.read()
        dhtml = re.sub(r'id="verLabel">v[0-9.]+ • Exp #\d+<', f'id="verLabel">v{ext_ver} • Exp #{exp_num:02d}<', dhtml)
        dhtml = re.sub(r'id="specVerLabel">v[0-9.]+ • EN / RU / KZ<', f'id="specVerLabel">v{ext_ver} • EN / RU / KZ<', dhtml)
        dhtml = re.sub(r'id="remoteSyncNote">Build: v[0-9.]+ • Export #\d+<', f'id="remoteSyncNote">Build: v{ext_ver} • Export #{exp_num:02d}<', dhtml)
        dhtml = re.sub(r'let curSiteVer = "[^"]*";', f'let curSiteVer = "{ext_ver}";', dhtml)
        dhtml = re.sub(r'let curSiteExp = \d+;', f'let curSiteExp = {exp_num};', dhtml)
        with open(docs_path, "w", encoding="utf-8") as f:
            f.write(dhtml)

    print(f"[OK] Браузерное расширение и лендинг синхронизированы -> v{ext_ver} (Exp #{exp_num:02d})")


def generate_windows_version_file(app_ver: str, exp_num: int) -> str:
    parts = [int(x) for x in (app_ver.split(".") + ["0", "0", "0"])[:3]]
    v_tuple = f"({parts[0]}, {parts[1]}, {parts[2]}, {exp_num})"
    v_str = f"{app_ver}.{exp_num}"
    content = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={v_tuple},
    prodvers={v_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', 'Jelly Timer'),
        StringStruct('FileDescription', 'Jelly Timer Plus (PRO) — Floating Timer & Focus Tracker'),
        StringStruct('FileVersion', '{v_str} (Export #{exp_num:02d})'),
        StringStruct('InternalName', 'JellyTimerPlus'),
        StringStruct('LegalCopyright', 'MIT / Jelly Timer Plus'),
        StringStruct('OriginalFilename', 'JellyTimerPlus.exe'),
        StringStruct('ProductName', 'Jelly Timer Plus (PRO)'),
        StringStruct('ProductVersion', 'v{app_ver} (Export #{exp_num:02d})')])
      ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
    ver_file = os.path.join(ROOT_DIR, "file_version_info.txt")
    with open(ver_file, "w", encoding="utf-8") as f:
        f.write(content)
    return ver_file


def update_pyinstaller_spec():
    spec_path = os.path.join(ROOT_DIR, "JellyTimerPlus.spec")
    spec_content = """# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = []
hiddenimports += collect_submodules('pynput')

excludes = [
    'tkinter', 'unittest', 'pydoc', 'pdb', 'difflib', 'doctest',
    'PyQt6.QtNetwork', 'PyQt6.QtQml', 'PyQt6.QtQuick', 'PyQt6.QtSql',
    'PyQt6.QtTest', 'PyQt6.QtXml', 'PyQt6.QtOpenGL', 'PyQt6.QtPdf',
    'PyQt6.QtBluetooth', 'PyQt6.QtDBus', 'PyQt6.QtDesigner', 'PyQt6.QtHelp',
    'PyQt6.QtMultimedia', 'PyQt6.QtMultimediaWidgets', 'PyQt6.QtNfc',
    'PyQt6.QtPositioning', 'PyQt6.QtPrintSupport', 'PyQt6.QtRemoteObjects',
    'PyQt6.QtSensors', 'PyQt6.QtSerialPort', 'PyQt6.QtSpatialAudio',
    'PyQt6.QtStateMachine', 'PyQt6.QtTextToSpeech', 'PyQt6.QtWebChannel',
    'PyQt6.QtWebSockets'
]

a = Analysis(
    ['jelly_timer_pro.pyw'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='JellyTimerPlus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='file_version_info.txt',
    icon=['jelly_timer_pro.ico'],
)
"""
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(spec_content)


def package_browser_extension(ext_ver: str, exp_num: int) -> str:
    dist_dir = os.path.join(ROOT_DIR, "dist")
    os.makedirs(dist_dir, exist_ok=True)
    zip_name = f"JellyTimer_BrowserExtension_v{ext_ver}_exp{exp_num:02d}.zip"
    zip_path = os.path.join(dist_dir, zip_name)
    ext_dir = os.path.join(ROOT_DIR, "browser_extension")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(ext_dir):
            for file in files:
                full = os.path.join(root, file)
                rel = os.path.relpath(full, ext_dir)
                zf.write(full, rel)
    print(f"[OK] Пакет расширения для Chrome Web Store / Firefox готов: dist/{zip_name}")
    return zip_path


def package_shareable_exports(meta: dict):
    app_ver = meta["app_version"]
    exp_num = int(meta["export_build"])
    build_date = meta["build_date"]
    notes = meta.get("release_notes", [])

    share_dir = os.path.join(ROOT_DIR, "Поделиться")
    win_dir = os.path.join(share_dir, "Для_Windows_Знакомым")
    mac_dir = os.path.join(share_dir, "Для_MacBook_Мамы")
    os.makedirs(win_dir, exist_ok=True)
    os.makedirs(mac_dir, exist_ok=True)

    exe_src = os.path.join(ROOT_DIR, "dist", "JellyTimerPlus.exe")
    if os.path.exists(exe_src):
        shutil.copy2(exe_src, os.path.join(win_dir, "JellyTimerPlus.exe"))

    shutil.copy2(os.path.join(ROOT_DIR, "jelly_timer_pro.pyw"), os.path.join(mac_dir, "jelly_timer_pro.pyw"))
    if os.path.exists(os.path.join(ROOT_DIR, "jelly_timer_pro.png")):
        shutil.copy2(os.path.join(ROOT_DIR, "jelly_timer_pro.png"), os.path.join(mac_dir, "jelly_timer_pro.png"))

    version_txt = (
        f"Продукт: Jelly Timer Plus (PRO)\n"
        f"Версия программы: v{app_ver}\n"
        f"Номер экспортной сборки: Export #{exp_num:02d}\n"
        f"Дата сборки: {build_date}\n\n"
        f"Что нового в этой сборке:\n"
        + "\n".join(f"  • {n}" for n in notes)
        + "\n"
    )

    for folder in (win_dir, mac_dir):
        with open(os.path.join(folder, "VERSION.txt"), "w", encoding="utf-8") as f:
            f.write(version_txt)

    # Remove old .zip archives in Поделиться/ so only the current clearly-versioned exports remain
    for item in os.listdir(share_dir):
        if item.lower().endswith(".zip"):
            try:
                os.remove(os.path.join(share_dir, item))
            except Exception:
                pass

    win_zip = os.path.join(share_dir, f"JellyTimerPlus_v{app_ver}_exp{exp_num:02d}_Windows.zip")
    mac_zip = os.path.join(share_dir, f"JellyTimerPlus_v{app_ver}_exp{exp_num:02d}_MacBook.zip")

    with zipfile.ZipFile(win_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(win_dir):
            for file in files:
                full = os.path.join(root, file)
                rel = os.path.relpath(full, share_dir)
                zf.write(full, rel)

    with zipfile.ZipFile(mac_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(mac_dir):
            for file in files:
                full = os.path.join(root, file)
                rel = os.path.relpath(full, share_dir)
                zf.write(full, rel)

    print(f"[OK] Экспортные архивы обновлены:\n     • {os.path.basename(win_zip)}\n     • {os.path.basename(mac_zip)}")


def main():
    parser = argparse.ArgumentParser(description="Build & Version Controller for Jelly Timer")
    parser.add_argument("--bump-export", action="store_true", help="Increment export_build number by 1")
    parser.add_argument("--version", type=str, help="Set new app_version (e.g. 1.3.0)")
    parser.add_argument("--skip-exe", action="store_true", help="Skip PyInstaller .exe compilation")
    args = parser.parse_args()

    meta = load_version_info()
    if args.version:
        meta["app_version"] = args.version.strip()
        meta["extension_version"] = args.version.strip()
    if args.bump_export:
        meta["export_build"] = int(meta.get("export_build", 1)) + 1
    meta["build_date"] = datetime.date.today().isoformat()
    save_version_info(meta)

    app_ver = meta["app_version"]
    ext_ver = meta["extension_version"]
    exp_num = int(meta["export_build"])
    build_date = meta["build_date"]

    update_python_script_version(
        os.path.join(ROOT_DIR, "jelly_timer.py"),
        os.path.join(ROOT_DIR, "jelly_timer.pyw"),
        app_ver, exp_num, build_date
    )
    update_python_script_version(
        os.path.join(ROOT_DIR, "jelly_timer_pro.py"),
        os.path.join(ROOT_DIR, "jelly_timer_pro.pyw"),
        app_ver, exp_num, build_date
    )
    update_browser_extension_version(ext_ver, exp_num, build_date)
    generate_windows_version_file(app_ver, exp_num)
    update_pyinstaller_spec()

    if not args.skip_exe:
        print("[..] Сборка JellyTimerPlus.exe через PyInstaller...")
        subprocess.run([sys.executable, "-m", "PyInstaller", "JellyTimerPlus.spec", "--noconfirm"], check=True)
        exe_path = os.path.join(ROOT_DIR, "dist", "JellyTimerPlus.exe")
        if os.path.exists(exe_path):
            mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"[OK] Сборка JellyTimerPlus.exe завершена ({mb:.1f} МБ)")

    package_browser_extension(ext_ver, exp_num)
    package_shareable_exports(meta)


if __name__ == "__main__":
    main()
