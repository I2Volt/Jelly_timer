(() => {
  if (window.__jellyTimerInjected) return;
  if (document.contentType && document.contentType.startsWith("image/")) return;
  window.__jellyTimerInjected = true;

  const I18N = {
    en: {
      timer: "Timer",
      stopwatch: "Stopwatch",
      start: "Start",
      pause: "Pause",
      settings: "Settings",
      shrink: "Smaller",
      grow: "Larger",
      hide: "Hide",
      min_short: "m",
      summon_label: "Focus / Summon key:",
      language_label: "Language / Тіл / Язык:",
      hint_html: "Press <b>Right Shift</b> or <b>Right Ctrl</b> to highlight the timer and control it with: <b>Space</b> (Start/Pause), <b>R</b> (Reset), <b>M</b> (Mode), <b>S</b> (Size), <b>Esc</b> (Exit).",
      presets_label: "Large mode presets (minutes, comma-separated):",
      opacity_label: "Opacity",
      sound_label: "Alarm sound:",
      test_sound: "Test sound",
      pro_btn: "✨ Plus Version (PRO)",
      save_btn: "Save",
      ctx_settings: "Settings (Hotkeys, Language, Presets)...",
      ctx_size_mini: "Size: Mini",
      ctx_size_med: "Size: Medium",
      ctx_size_large: "Size: Large",
      ctx_th_graphite: "Theme: Dark Graphite",
      ctx_th_espresso: "Theme: Warm Espresso",
      ctx_th_sage: "Theme: Soft Sage",
      ctx_hide: "Hide on this tab"
    },
    ru: {
      timer: "Таймер",
      stopwatch: "Секундомер",
      start: "Старт",
      pause: "Пауза",
      settings: "Настройки",
      shrink: "Уменьшить",
      grow: "Увеличить",
      hide: "Скрыть",
      min_short: "м",
      summon_label: "Вызвать / Выбрать таймер:",
      language_label: "Язык / Language / Тіл:",
      hint_html: "Нажмите <b>Right Shift</b> или <b>Right Ctrl</b> — таймер подсветится белой рамкой и перехватит кнопки: <b>Space</b> (Старт/Пауза), <b>R</b> (Сброс), <b>M</b> (Режим), <b>S</b> (Размер), <b>Esc</b> (Выход).",
      presets_label: "Пресеты большого режима (мин, через запятую):",
      opacity_label: "Прозрачность",
      sound_label: "Звуковой сигнал:",
      test_sound: "Проверить звук",
      pro_btn: "✨ Версия Plus (PRO)",
      save_btn: "Сохранить",
      ctx_settings: "Настройки (Клавиши, язык, пресеты)...",
      ctx_size_mini: "Размер: Мини",
      ctx_size_med: "Размер: Средний",
      ctx_size_large: "Размер: Большой",
      ctx_th_graphite: "Тема: Тёмный графит",
      ctx_th_espresso: "Тема: Тёплый эспрессо",
      ctx_th_sage: "Тема: Мягкий шалфей",
      ctx_hide: "Скрыть на вкладке"
    },
    kz: {
      timer: "Таймер",
      stopwatch: "Секундөлшегіш",
      start: "Бастау",
      pause: "Кідірту",
      settings: "Баптаулар",
      shrink: "Кішірейту",
      grow: "Үлкейту",
      hide: "Жасыру",
      min_short: "м",
      summon_label: "Таймерді шақыру пернесі:",
      language_label: "Тіл / Language / Язык:",
      hint_html: "<b>Right Shift</b> немесе <b>Right Ctrl</b> басыңыз — таймер ақ жиекпен белгіленіп, пернелерді басқарады: <b>Space</b> (Бастау/Кідірту), <b>R</b> (Қалпына келтіру), <b>M</b> (Режим), <b>S</b> (Өлшем), <b>Esc</b> (Шығу).",
      presets_label: "Үлкен режим пресеттері (мин, үтір арқылы):",
      opacity_label: "Мөлдірлік",
      sound_label: "Дыбыстық сигнал:",
      test_sound: "Дыбысты тексеру",
      pro_btn: "✨ Plus нұсқасы (PRO)",
      save_btn: "Сақтау",
      ctx_settings: "Баптаулар (Пернелер, тіл, пресеттер)...",
      ctx_size_mini: "Өлшем: Мини",
      ctx_size_med: "Өлшем: Орташа",
      ctx_size_large: "Өлшем: Үлкен",
      ctx_th_graphite: "Тақырып: Күңгірт графит",
      ctx_th_espresso: "Тақырып: Жылы эспрессо",
      ctx_th_sage: "Тақырып: Жұмсақ шалфей",
      ctx_hide: "Қойындыда жасыру"
    }
  };

  function detectDefaultLang() {
    const nav = ((navigator && navigator.language) || "en").toLowerCase();
    if (nav.startsWith("kk") || nav.startsWith("kz")) return "kz";
    if (nav.startsWith("ru")) return "ru";
    return "en";
  }

  function tr(key) {
    const lang = (state && state.lang && I18N[state.lang]) ? state.lang : detectDefaultLang();
    return (I18N[lang] && I18N[lang][key]) || I18N.en[key] || key;
  }

  const SIZES = {
    mini: { w: 208, h: 66 },
    medium: { w: 284, h: 138 },
    large: { w: 348, h: 195 }
  };

  const THEMES = {
    graphite: {
      bg: "24, 24, 27",
      border: "rgb(63, 63, 70)",
      primaryBg: "#F4F4F5",
      primaryFg: "#18181B",
      text: "#FAFAFA",
      muted: "#A1A1AA"
    },
    warm_espresso: {
      bg: "28, 25, 23",
      border: "rgb(68, 64, 60)",
      primaryBg: "#F5F5F4",
      primaryFg: "#1C1917",
      text: "#FAFAF9",
      muted: "#A8A29E"
    },
    soft_sage: {
      bg: "22, 27, 24",
      border: "rgb(55, 68, 60)",
      primaryBg: "#D7EBDE",
      primaryFg: "#141A16",
      text: "#F2F8F4",
      muted: "#94A89B"
    }
  };

  const SVGS = {
    play: `<svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="6 3 20 12 6 21 6 3"/></svg>`,
    pause: `<svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg>`,
    reset: `<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>`,
    timer: `<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 22h14"/><path d="M5 2h14"/><path d="M17 22v-4.172a2 2 0 0 0-.586-1.414L12 12l-4.414 4.414A2 2 0 0 0 7 17.828V22"/><path d="M7 2v4.172a2 2 0 0 0 .586 1.414L12 12l4.414-4.414A2 2 0 0 0 17 6.172V2"/></svg>`,
    stopwatch: `<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="10" x2="14" y1="2" y2="2"/><line x1="12" x2="15" y1="14" y2="11"/><circle cx="12" cy="14" r="8"/></svg>`,
    swap: `<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m7 15 5 5 5-5"/><path d="m7 9 5-5 5 5"/></svg>`,
    expand: `<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" x2="14" y1="3" y2="10"/><line x1="3" x2="10" y1="21" y2="14"/></svg>`,
    minus: `<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><line x1="5" y1="12" x2="19" y2="12"/></svg>`,
    plus: `<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>`,
    settings: `<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>`,
    close: `<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>`,
    opacity: `<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 18a6 6 0 0 0 0-12v12z" fill="currentColor"/></svg>`
  };

  class Spring {
    constructor(val, stiffness = 280, damping = 17) {
      this.value = val;
      this.target = val;
      this.velocity = 0;
      this.stiffness = stiffness;
      this.damping = damping;
    }
    step(dt) {
      dt = Math.min(dt, 0.04);
      const force = (this.target - this.value) * this.stiffness;
      this.velocity += force * dt;
      this.velocity *= Math.exp(-this.damping * dt);
      this.value += this.velocity * dt;
      if (Math.abs(this.target - this.value) < 0.0015 && Math.abs(this.velocity) < 0.015) {
        this.value = this.target;
        this.velocity = 0;
      }
    }
    setImmediate(val) {
      this.value = val;
      this.target = val;
      this.velocity = 0;
    }
  }

  let state = {
    visible: true,
    lang: detectDefaultLang(),
    mode: "timer",
    sizeMode: "medium",
    themeKey: "graphite",
    opacity: 0.88,
    snapEnabled: true,
    dockEdge: "top_right",
    rx: 0.82,
    ry: 0.06,
    timerTotal: 25 * 60,
    timerRemaining: 25 * 60,
    stopwatchElapsed: 0,
    isRunning: false,
    lastTimestamp: null,
    presets: [5, 15, 25, 45, 60],
    globalHotkeys: false,
    hotkeys: {
      summon: "ShiftRight",
      play_pause: "Space",
      reset: "KeyR",
      switch_mode: "KeyM",
      cycle_size: "KeyS"
    }
  };

  // Create Shadow DOM host
  const host = document.createElement("div");
  host.id = "jelly-timer-extension-host";
  host.style.cssText = "position:fixed;top:0;left:0;width:0;height:0;z-index:2147483647;pointer-events:none;";
  document.documentElement.appendChild(host);
  const shadow = host.attachShadow({ mode: "closed" });

  const style = document.createElement("style");
  style.textContent = `
    * { box-sizing: border-box; user-select: none; -webkit-user-select: none; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .snap-zone {
      position: fixed;
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.11);
      border: 1.5px solid rgba(255, 255, 255, 0.52);
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.14s ease, transform 0.14s ease;
      z-index: 2147483646;
    }
    .snap-zone.active { opacity: 1; }
    .card {
      position: fixed;
      border-radius: 14px;
      pointer-events: auto;
      cursor: grab;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 10px 12px;
      box-shadow: 0 10px 28px rgba(0,0,0,0.42);
      backdrop-filter: blur(10px);
      transform-origin: center center;
      z-index: 2147483647;
      overflow: hidden;
    }
    .card:active { cursor: grabbing; }
    .btn {
      border: none;
      outline: none;
      border-radius: 7px;
      background: rgba(255,255,255,0.06);
      color: #A1A1AA;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      font-size: 11.5px;
      font-weight: 600;
      padding: 4px 8px;
      transition: background 0.12s, color 0.12s;
    }
    .btn:hover { background: rgba(255,255,255,0.13); color: #FAFAFA; }
    .btn.primary { background: #F4F4F5; color: #18181B; }
    .btn.primary:hover { background: #FFFFFF; }
    .top-row, .bottom-row, .preset-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      gap: 5px;
    }
    .time-box {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      color: #FAFAFA;
      letter-spacing: -0.5px;
      line-height: 1;
      text-align: center;
      white-space: nowrap;
      border-radius: 6px;
    }
    .time-input {
      width: 90%;
      background: rgba(255,255,255,0.08);
      border: 1px dashed rgba(255,255,255,0.45);
      border-radius: 6px;
      color: #FAFAFA;
      font-weight: 600;
      text-align: center;
      outline: none;
      padding: 2px 4px;
    }
    .progress-track {
      position: absolute;
      bottom: 4px;
      left: 14px;
      right: 14px;
      height: 2px;
      background: rgba(255,255,255,0.08);
      border-radius: 1px;
      overflow: hidden;
    }
    .progress-fill {
      height: 100%;
      background: rgba(244,244,245,0.75);
      width: 100%;
    }
    .ctx-menu {
      position: fixed;
      background: #18181B;
      border: 1px solid #3F3F46;
      border-radius: 10px;
      padding: 6px;
      min-width: 215px;
      box-shadow: 0 12px 32px rgba(0,0,0,0.55);
      z-index: 2147483647;
      pointer-events: auto;
      display: none;
      flex-direction: column;
      gap: 2px;
    }
    .ctx-menu.open { display: flex; }
    .ctx-item {
      border: none;
      background: transparent;
      color: #F4F4F5;
      font-size: 12px;
      text-align: left;
      padding: 6px 10px;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .ctx-item:hover { background: #27272A; color: #FFFFFF; }
    .ctx-item.pro { color: #FAFAFA; font-weight: 600; background: rgba(255,255,255,0.05); }
    .ctx-item.pro:hover { background: rgba(255,255,255,0.12); }
    .ctx-sep { height: 1px; background: #27272A; margin: 3px 4px; }
    .ctx-meta {
      font-size: 10.5px;
      color: #71717A;
      padding: 4px 10px 2px;
    }
    .settings-modal {
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 390px;
      background: #18181B;
      border: 1px solid #3F3F46;
      border-radius: 14px;
      padding: 18px;
      color: #F4F4F5;
      box-shadow: 0 18px 48px rgba(0,0,0,0.65);
      z-index: 2147483647;
      pointer-events: auto;
      display: none;
      flex-direction: column;
      gap: 10px;
      font-size: 12px;
    }
    .settings-modal.open { display: flex; }
    .st-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .st-input {
      background: #27272A;
      border: 1px solid #3F3F46;
      border-radius: 6px;
      color: #FAFAFA;
      padding: 5px 8px;
      font-size: 12px;
      font-weight: 600;
      width: 100%;
      outline: none;
    }
    .st-hint {
      background: #222226;
      color: #D4D4D8;
      font-size: 11px;
      padding: 8px 10px;
      border-radius: 6px;
      line-height: 1.4;
    }
  `;
  shadow.appendChild(style);

  const snapZoneEl = document.createElement("div");
  snapZoneEl.className = "snap-zone";
  shadow.appendChild(snapZoneEl);

  const cardEl = document.createElement("div");
  cardEl.className = "card";
  shadow.appendChild(cardEl);

  const ctxMenuEl = document.createElement("div");
  ctxMenuEl.className = "ctx-menu";
  shadow.appendChild(ctxMenuEl);

  const settingsModalEl = document.createElement("div");
  settingsModalEl.className = "settings-modal";
  shadow.appendChild(settingsModalEl);

  // Physics springs
  const spX = new Spring(window.innerWidth - 300, 360, 29);
  const spY = new Spring(60, 360, 29);
  const spW = new Spring(284, 320, 26);
  const spH = new Spring(138, 320, 26);
  const spScaleX = new Spring(1.0, 280, 16.5);
  const spScaleY = new Spring(1.0, 280, 16.5);

  let isDragging = false;
  let dragOffsetX = 0;
  let dragOffsetY = 0;
  let detachingEdge = null;
  let detachAnchorX = 0;
  let detachAnchorY = 0;
  let editingTime = false;

  function sendMsg(msg) {
    try {
      chrome.runtime.sendMessage(msg);
    } catch (e) {}
  }

  function getLiveSeconds() {
    const now = Date.now();
    if (state.mode === "timer") {
      if (state.isRunning && state.lastTimestamp) {
        const dt = (now - state.lastTimestamp) / 1000.0;
        return Math.max(0, state.timerRemaining - dt);
      }
      return state.timerRemaining;
    } else {
      if (state.isRunning && state.lastTimestamp) {
        const dt = (now - state.lastTimestamp) / 1000.0;
        return state.stopwatchElapsed + dt;
      }
      return state.stopwatchElapsed;
    }
  }

  function formatSeconds(sec) {
    sec = Math.max(0, sec);
    const total = Math.floor(sec);
    let mins = Math.floor(total / 60);
    const secs = total % 60;
    const hrs = Math.floor(mins / 60);
    if (hrs > 0) {
      mins = mins % 60;
      return `${String(hrs).padStart(2, "0")}:${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
    }
    if (state.mode === "stopwatch") {
      const tenths = Math.floor((sec - total) * 10);
      return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}.${tenths}`;
    }
    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
  }

  function computeSnapCandidate(x, y, w, h, cx, cy) {
    if (!state.snapEnabled) return null;
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const snapDist = 48;
    const margin = 8;

    const nearLeft = (x <= snapDist) || (cx <= snapDist);
    const nearRight = (x + w >= vw - snapDist) || (cx >= vw - snapDist);
    const nearTop = (y <= snapDist) || (cy <= snapDist);
    const nearBottom = (y + h >= vh - snapDist) || (cy >= vh - snapDist);

    if (!nearLeft && !nearRight && !nearTop && !nearBottom) return null;

    let tx = Math.max(margin, Math.min(x, vw - w - margin));
    let ty = Math.max(margin, Math.min(y, vh - h - margin));
    let hEdge = null, vEdge = null;

    if (nearLeft) { tx = margin; hEdge = "left"; }
    else if (nearRight) { tx = vw - w - margin; hEdge = "right"; }

    if (nearTop) { ty = margin; vEdge = "top"; }
    else if (nearBottom) { ty = vh - h - margin; vEdge = "bottom"; }

    const edge = (vEdge && hEdge) ? `${vEdge}_${hEdge}` : (hEdge || vEdge);
    return { edge, x: tx, y: ty, w, h };
  }

  function applyDockedPositionFromState(snapImmediate = false) {
    const sz = SIZES[state.sizeMode] || SIZES.medium;
    spW.target = sz.w;
    spH.target = sz.h;
    if (snapImmediate) {
      spW.setImmediate(sz.w);
      spH.setImmediate(sz.h);
    }

    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const margin = 8;

    let tx = state.rx * Math.max(100, vw - sz.w);
    let ty = state.ry * Math.max(100, vh - sz.h);

    if (state.dockEdge) {
      if (state.dockEdge.includes("left")) tx = margin;
      else if (state.dockEdge.includes("right")) tx = vw - sz.w - margin;
      if (state.dockEdge.includes("top")) ty = margin;
      else if (state.dockEdge.includes("bottom")) ty = vh - sz.h - margin;
    }

    tx = Math.max(margin, Math.min(tx, vw - sz.w - margin));
    ty = Math.max(margin, Math.min(ty, vh - sz.h - margin));

    if (!isDragging) {
      spX.target = tx;
      spY.target = ty;
      if (snapImmediate) {
        spX.setImmediate(tx);
        spY.setImmediate(ty);
      }
    }
  }

  function rebuildDOM() {
    if (!state.visible) {
      cardEl.style.display = "none";
      return;
    }
    cardEl.style.display = "flex";
    const th = THEMES[state.themeKey] || THEMES.graphite;
    cardEl.style.background = `rgba(${th.bg}, ${state.opacity})`;
    cardEl.style.border = `1px solid ${th.border}`;

    const modeIcon = state.mode === "timer" ? SVGS.timer : SVGS.stopwatch;
    const modeLabel = state.mode === "timer" ? tr("timer") : tr("stopwatch");
    const playIcon = state.isRunning ? SVGS.pause : SVGS.play;
    const playLabel = state.isRunning ? tr("pause") : tr("start");
    const mShort = tr("min_short");
    const liveSec = getLiveSeconds();
    const showReset = state.isRunning || (state.mode === "timer" ? Math.abs(liveSec - state.timerTotal) > 0.1 : liveSec > 0.1);

    if (state.sizeMode === "mini") {
      cardEl.style.flexDirection = "row";
      cardEl.style.alignItems = "center";
      cardEl.style.padding = "6px 8px";
      cardEl.innerHTML = `
        <button class="btn" data-act="toggle_mode" style="width:28px;height:28px;padding:0;">${modeIcon}</button>
        <div class="time-box" data-act="time_box" style="font-size:18px;padding:0 6px;"></div>
        <button class="btn primary" data-act="play" style="width:28px;height:28px;padding:0;">${playIcon}</button>
        <button class="btn" data-act="cycle_size" style="width:22px;height:24px;padding:0;">${SVGS.expand}</button>
        ${state.mode === "timer" ? `<div class="progress-track"><div class="progress-fill"></div></div>` : ""}
      `;
    } else if (state.sizeMode === "medium") {
      cardEl.style.flexDirection = "column";
      cardEl.style.padding = "10px 10px 12px 10px";
      cardEl.innerHTML = `
        <div class="top-row">
          <button class="btn" data-act="toggle_mode" style="height:22px;">${modeIcon} <span>${modeLabel}</span> ${SVGS.swap}</button>
          <div style="display:flex;gap:4px;">
            <button class="btn" data-act="open_settings" title="${tr('settings')}" style="width:22px;height:22px;padding:0;">${SVGS.settings}</button>
            <button class="btn" data-act="shrink_size" title="${tr('shrink')}" style="width:22px;height:22px;padding:0;">${SVGS.minus}</button>
            <button class="btn" data-act="grow_size" title="${tr('grow')}" style="width:22px;height:22px;padding:0;">${SVGS.plus}</button>
            <button class="btn" data-act="close" title="${tr('hide')}" style="width:22px;height:22px;padding:0;">${SVGS.close}</button>
          </div>
        </div>
        <div class="time-box" data-act="time_box" style="font-size:32px;margin:2px 0;"></div>
        <div class="bottom-row" style="justify-content:center;">
          <button class="btn primary" data-act="play" style="height:26px;width:108px;">${playIcon} <span>${playLabel}</span></button>
          ${showReset ? `<button class="btn" data-act="reset" style="width:34px;height:26px;padding:0;">${SVGS.reset}</button>` : ""}
        </div>
        ${state.mode === "timer" ? `<div class="progress-track"><div class="progress-fill"></div></div>` : ""}
      `;
    } else {
      const presetList = (Array.isArray(state.presets) && state.presets.length) ? state.presets : [5, 15, 25, 45, 60];
      const presetBtns = presetList.map((m) => `<button class="btn" data-act="preset_${m}" style="flex:1;height:24px;">${m}${mShort}</button>`).join("");
      cardEl.style.flexDirection = "column";
      cardEl.style.padding = "12px 12px 14px 12px";
      cardEl.innerHTML = `
        <div class="top-row">
          <button class="btn" data-act="toggle_mode" style="height:24px;">${modeIcon} <span>${modeLabel}</span> ${SVGS.swap}</button>
          <div style="display:flex;gap:4px;">
            <button class="btn" data-act="open_settings" title="${tr('settings')}" style="width:24px;height:24px;padding:0;">${SVGS.settings}</button>
            <button class="btn" data-act="shrink_size" title="${tr('shrink')}" style="width:24px;height:24px;padding:0;">${SVGS.minus}</button>
            <button class="btn" data-act="grow_size" title="${tr('grow')}" style="width:24px;height:24px;padding:0;">${SVGS.plus}</button>
            <button class="btn" data-act="close" title="${tr('hide')}" style="width:24px;height:24px;padding:0;">${SVGS.close}</button>
          </div>
        </div>
        <div class="time-box" data-act="time_box" style="font-size:40px;margin:2px 0;"></div>
        ${state.mode === "timer" ? `<div class="preset-row">${presetBtns}</div>` : ""}
        <div class="bottom-row" style="justify-content:center;">
          ${state.mode === "timer" ? `
            <button class="btn" data-act="sub_5m" style="height:28px;">-5${mShort}</button>
            <button class="btn" data-act="sub_1m" style="height:28px;">-1${mShort}</button>
            <button class="btn primary" data-act="play" style="height:28px;flex:1;">${playIcon} <span>${playLabel}</span></button>
            ${showReset ? `<button class="btn" data-act="reset" style="width:36px;height:28px;padding:0;">${SVGS.reset}</button>` : ""}
            <button class="btn" data-act="add_1m" style="height:28px;">+1${mShort}</button>
            <button class="btn" data-act="add_5m" style="height:28px;">+5${mShort}</button>
          ` : `
            <button class="btn primary" data-act="play" style="height:28px;width:116px;">${playIcon} <span>${playLabel}</span></button>
            ${showReset ? `<button class="btn" data-act="reset" style="width:38px;height:28px;padding:0;">${SVGS.reset}</button>` : ""}
          `}
        </div>
        ${state.mode === "timer" ? `<div class="progress-track"><div class="progress-fill"></div></div>` : ""}
      `;
    }
    updateTimeText();
  }

  function updateTimeText() {
    if (editingTime) return;
    const tb = cardEl.querySelector('[data-act="time_box"]');
    if (!tb) return;
    const sec = getLiveSeconds();
    const txt = formatSeconds(sec);
    tb.textContent = txt;

    // Auto-scale font if hours are displayed in mini mode
    if (state.sizeMode === "mini") {
      tb.style.fontSize = txt.length > 7 ? "14.5px" : "18px";
    } else if (state.sizeMode === "medium") {
      tb.style.fontSize = txt.length > 7 ? "26px" : "31px";
    } else {
      tb.style.fontSize = txt.length > 7 ? "33px" : "40px";
    }

    const pf = cardEl.querySelector(".progress-fill");
    if (pf && state.mode === "timer" && state.timerTotal > 0) {
      const pct = Math.max(0, Math.min(100, (sec / state.timerTotal) * 100));
      pf.style.width = `${pct}%`;
    }
  }

  // Button clicks & double-click on time to edit
  cardEl.addEventListener("mousedown", (e) => {
    if (e.button !== 0) return;
    const btn = e.target.closest("button[data-act]");
    if (btn) {
      e.stopPropagation();
      const act = btn.getAttribute("data-act");
      handleAction(act);
      return;
    }
    if (e.target.tagName === "INPUT") return;

    // Start dragging
    isDragging = true;
    dragOffsetX = e.clientX - spX.value;
    dragOffsetY = e.clientY - spY.value;
    if (state.dockEdge) {
      detachingEdge = state.dockEdge;
      detachAnchorX = spX.value;
      detachAnchorY = spY.value;
    } else {
      detachingEdge = null;
    }
  });

  cardEl.addEventListener("dblclick", (e) => {
    const btn = e.target.closest("button[data-act]");
    if (btn) return;
    const tb = e.target.closest('[data-act="time_box"]');
    if (tb && state.mode === "timer") {
      startInlineEdit(tb);
    } else {
      cycleSize();
    }
  });

  // Mouse wheel: Ctrl + Wheel -> opacity (20%..100%), plain Wheel on paused timer -> +-1 min
  cardEl.addEventListener("wheel", (e) => {
    e.preventDefault();
    e.stopPropagation();
    const dir = e.deltaY < 0 ? 1 : -1;
    if (e.ctrlKey) {
      const nextOp = Math.max(0.2, Math.min(1.0, Math.round((state.opacity + dir * 0.05) * 100) / 100));
      sendMsg({ type: "PATCH_STATE", patch: { opacity: nextOp } });
    } else if (state.mode === "timer" && !state.isRunning) {
      sendMsg({ type: "ADJUST_TIMER", delta: dir * 60 });
    }
  }, { passive: false });

  function closeContextMenu() {
    ctxMenuEl.classList.remove("open");
  }

  let settingsOpen = false;
  function openSettingsModal() {
    settingsOpen = true;
    const ver = state.appVersion || "1.2.0";
    const exp = String(state.exportBuild || 4).padStart(2, "0");
    const presetStr = (Array.isArray(state.presets) && state.presets.length ? state.presets : [5, 15, 25, 45, 60]).join(", ");
    const curSummon = (state.hotkeys && state.hotkeys.summon) || "ShiftRight";
    const curLang = (state.lang && I18N[state.lang]) ? state.lang : detectDefaultLang();
    settingsModalEl.innerHTML = `
      <div class="st-row">
        <strong style="font-size:14px;color:#FAFAFA;">${tr("settings")} • v${ver} (Exp #${exp})</strong>
        <button class="btn" id="stCloseX" style="width:24px;height:24px;padding:0;">${SVGS.close}</button>
      </div>
      <div class="st-row">
        <span>${tr("language_label")}</span>
        <select id="stLang" class="st-input" style="width:155px;">
          <option value="en" ${curLang === "en" ? "selected" : ""}>English (EN)</option>
          <option value="ru" ${curLang === "ru" ? "selected" : ""}>Русский (RU)</option>
          <option value="kz" ${curLang === "kz" ? "selected" : ""}>Қазақша (KZ)</option>
        </select>
      </div>
      <div class="st-row">
        <span>${tr("summon_label")}</span>
        <select id="stSummonKey" class="st-input" style="width:155px;">
          <option value="ShiftRight" ${curSummon === "ShiftRight" ? "selected" : ""}>Right Shift</option>
          <option value="ControlRight" ${curSummon === "ControlRight" ? "selected" : ""}>Right Ctrl</option>
          <option value="AltRight" ${curSummon === "AltRight" ? "selected" : ""}>Right Alt</option>
        </select>
      </div>
      <div class="st-hint">${tr("hint_html")}</div>
      <div>
        <div style="color:#A1A1AA;margin-bottom:4px;">${tr("presets_label")}</div>
        <input id="stPresets" class="st-input" type="text" value="${presetStr}" />
      </div>
      <div class="st-row">
        <span>${tr("opacity_label")} (${Math.round(state.opacity * 100)}%):</span>
        <input id="stOpacity" type="range" min="20" max="100" value="${Math.round(state.opacity * 100)}" style="width:160px;" />
      </div>
      <div class="st-row">
        <span>${tr("sound_label")}</span>
        <button class="btn" id="stTestSound">${tr("test_sound")}</button>
      </div>
      <div class="st-row" style="margin-top:4px;">
        <button class="btn" id="stOpenPro" style="border:1px solid #52525B;color:#FAFAFA;">${tr("pro_btn")}</button>
        <button class="btn primary" id="stSaveBtn" style="flex:1;height:30px;">${tr("save_btn")}</button>
      </div>
    `;
    settingsModalEl.classList.add("open");

    settingsModalEl.querySelector("#stCloseX").onclick = () => {
      settingsOpen = false;
      settingsModalEl.classList.remove("open");
    };
    settingsModalEl.querySelector("#stLang").onchange = (ev) => {
      const nextLang = ev.target.value;
      state.lang = nextLang;
      sendMsg({ type: "PATCH_STATE", patch: { lang: nextLang } });
      openSettingsModal();
    };
    settingsModalEl.querySelector("#stTestSound").onclick = () => playWebAlarm();
    settingsModalEl.querySelector("#stOpenPro").onclick = () => {
      settingsOpen = false;
      settingsModalEl.classList.remove("open");
      sendMsg({ type: "OPEN_PRO_PAGE" });
    };
    settingsModalEl.querySelector("#stOpacity").oninput = (ev) => {
      const val = parseInt(ev.target.value, 10) / 100.0;
      sendMsg({ type: "PATCH_STATE", patch: { opacity: val } });
    };
    settingsModalEl.querySelector("#stSaveBtn").onclick = () => {
      const raw = settingsModalEl.querySelector("#stPresets").value.replace(/;/g, ",").split(",");
      const parsed = raw.map((x) => parseInt(x.trim(), 10)).filter((n) => !isNaN(n) && n > 0 && n <= 999).slice(0, 6);
      const summonVal = settingsModalEl.querySelector("#stSummonKey").value;
      const langVal = settingsModalEl.querySelector("#stLang").value;
      sendMsg({
        type: "PATCH_STATE",
        patch: {
          lang: langVal,
          presets: parsed.length ? parsed : [5, 15, 25, 45, 60],
          hotkeys: { ...(state.hotkeys || {}), summon: summonVal }
        }
      });
      settingsOpen = false;
      settingsModalEl.classList.remove("open");
    };
  }

  cardEl.addEventListener("contextmenu", (e) => {
    e.preventDefault();
    e.stopPropagation();
    const ver = state.appVersion || "1.2.0";
    const exp = String(state.exportBuild || 2).padStart(2, "0");
    const curLang = (state.lang && I18N[state.lang]) ? state.lang : detectDefaultLang();
    ctxMenuEl.innerHTML = `
      <div class="ctx-meta" style="display:flex;justify-content:space-between;align-items:center;">
        <span>Jelly Timer v${ver} (#${exp})</span>
        <span style="display:inline-flex;gap:3px;">
          <button class="btn" data-ctx="lang_en" style="padding:1px 5px;font-size:10px;${curLang==='en'?'color:#FAFAFA;background:rgba(255,255,255,0.16);':''}">EN</button>
          <button class="btn" data-ctx="lang_ru" style="padding:1px 5px;font-size:10px;${curLang==='ru'?'color:#FAFAFA;background:rgba(255,255,255,0.16);':''}">RU</button>
          <button class="btn" data-ctx="lang_kz" style="padding:1px 5px;font-size:10px;${curLang==='kz'?'color:#FAFAFA;background:rgba(255,255,255,0.16);':''}">KZ</button>
        </span>
      </div>
      <div class="ctx-sep"></div>
      <button class="ctx-item" data-ctx="mode_timer"><span>${tr("timer")}</span><span>${state.mode === "timer" ? "✓" : ""}</span></button>
      <button class="ctx-item" data-ctx="mode_sw"><span>${tr("stopwatch")}</span><span>${state.mode === "stopwatch" ? "✓" : ""}</span></button>
      <div class="ctx-sep"></div>
      <button class="ctx-item" data-ctx="open_settings"><span>${tr("ctx_settings")}</span><span>⚙</span></button>
      <div class="ctx-sep"></div>
      <button class="ctx-item" data-ctx="size_mini"><span>${tr("ctx_size_mini")}</span><span>${state.sizeMode === "mini" ? "✓" : ""}</span></button>
      <button class="ctx-item" data-ctx="size_medium"><span>${tr("ctx_size_med")}</span><span>${state.sizeMode === "medium" ? "✓" : ""}</span></button>
      <button class="ctx-item" data-ctx="size_large"><span>${tr("ctx_size_large")}</span><span>${state.sizeMode === "large" ? "✓" : ""}</span></button>
      <div class="ctx-sep"></div>
      <button class="ctx-item" data-ctx="th_graphite"><span>${tr("ctx_th_graphite")}</span><span>${state.themeKey === "graphite" ? "✓" : ""}</span></button>
      <button class="ctx-item" data-ctx="th_warm_espresso"><span>${tr("ctx_th_espresso")}</span><span>${state.themeKey === "warm_espresso" ? "✓" : ""}</span></button>
      <button class="ctx-item" data-ctx="th_soft_sage"><span>${tr("ctx_th_sage")}</span><span>${state.themeKey === "soft_sage" ? "✓" : ""}</span></button>
      <div class="ctx-sep"></div>
      <button class="ctx-item pro" data-ctx="open_pro"><span>✨ Jelly Timer Plus (PRO)</span><span>→</span></button>
      <button class="ctx-item" data-ctx="hide"><span>${tr("ctx_hide")}</span><span></span></button>
    `;
    const mw = 235;
    const mh = 340;
    const mx = Math.max(8, Math.min(e.clientX, window.innerWidth - mw - 8));
    const my = Math.max(8, Math.min(e.clientY, window.innerHeight - mh - 8));
    ctxMenuEl.style.left = `${mx}px`;
    ctxMenuEl.style.top = `${my}px`;
    ctxMenuEl.classList.add("open");
  });

  ctxMenuEl.addEventListener("mousedown", (e) => {
    e.stopPropagation();
    const item = e.target.closest("button[data-ctx]");
    if (!item) return;
    const act = item.getAttribute("data-ctx");
    closeContextMenu();
    if (act.startsWith("lang_")) sendMsg({ type: "PATCH_STATE", patch: { lang: act.replace("lang_", "") } });
    else if (act === "mode_timer") sendMsg({ type: "SWITCH_MODE", mode: "timer" });
    else if (act === "mode_sw") sendMsg({ type: "SWITCH_MODE", mode: "stopwatch" });
    else if (act === "open_settings") openSettingsModal();
    else if (act.startsWith("size_")) sendMsg({ type: "PATCH_STATE", patch: { sizeMode: act.replace("size_", "") } });
    else if (act.startsWith("th_")) sendMsg({ type: "PATCH_STATE", patch: { themeKey: act.replace("th_", "") } });
    else if (act === "open_pro") sendMsg({ type: "OPEN_PRO_PAGE" });
    else if (act === "hide") sendMsg({ type: "PATCH_STATE", patch: { visible: false } });
  });

  window.addEventListener("mousedown", () => closeContextMenu());

  function startInlineEdit(tb) {
    editingTime = true;
    const currentStr = formatSeconds(getLiveSeconds());
    tb.innerHTML = `<input class="time-input" type="text" value="${currentStr}" />`;
    const inp = tb.querySelector("input");
    inp.style.fontSize = tb.style.fontSize;
    inp.focus();
    inp.setSelectionRange(inp.value.length, inp.value.length);

    const commit = () => {
      if (!editingTime) return;
      editingTime = false;
      const raw = inp.value.trim();
      let total = 0;
      if (raw.includes(":")) {
        const parts = raw.split(":").map((p) => parseInt(p || "0", 10) || 0);
        if (parts.length === 2) total = parts[0] * 60 + parts[1];
        else if (parts.length >= 3) total = parts[0] * 3600 + parts[1] * 60 + parts[2];
      } else {
        total = (parseInt(raw, 10) || 0) * 60;
      }
      if (total > 0) {
        sendMsg({ type: "SET_TIMER", seconds: total });
      } else {
        rebuildDOM();
      }
    };

    inp.addEventListener("keydown", (ke) => {
      ke.stopPropagation();
      if (ke.key === "Enter") commit();
      else if (ke.key === "Escape") {
        editingTime = false;
        rebuildDOM();
      }
    });
    inp.addEventListener("blur", commit);
  }

  window.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    const rawX = e.clientX - dragOffsetX;
    const rawY = e.clientY - dragOffsetY;

    if (detachingEdge) {
      const dx = rawX - detachAnchorX;
      const dy = rawY - detachAnchorY;
      const dist = Math.hypot(dx, dy);
      const peelThreshold = 42;
      if (dist < peelThreshold) {
        const ratio = dist / peelThreshold;
        spX.setImmediate(detachAnchorX + dx * 0.25);
        spY.setImmediate(detachAnchorY + dy * 0.25);
        if (detachingEdge.includes("left") || detachingEdge.includes("right")) {
          spScaleX.setImmediate(1 + ratio * 0.16);
          spScaleY.setImmediate(1 - ratio * 0.1);
        } else {
          spScaleY.setImmediate(1 + ratio * 0.16);
          spScaleX.setImmediate(1 - ratio * 0.1);
        }
        return;
      } else {
        const released = detachingEdge;
        detachingEdge = null;
        spScaleX.target = 1.0;
        spScaleY.target = 1.0;
        if (released.includes("left") || released.includes("right")) {
          spScaleX.velocity -= 2.4;
          spScaleY.velocity += 1.8;
        } else {
          spScaleX.velocity += 1.8;
          spScaleY.velocity -= 2.4;
        }
      }
    }

    spX.setImmediate(rawX);
    spY.setImmediate(rawY);

    const cand = computeSnapCandidate(rawX, rawY, spW.value, spH.value, e.clientX, e.clientY);
    if (cand) {
      snapZoneEl.style.left = `${cand.x}px`;
      snapZoneEl.style.top = `${cand.y}px`;
      snapZoneEl.style.width = `${cand.w}px`;
      snapZoneEl.style.height = `${cand.h}px`;
      snapZoneEl.classList.add("active");
    } else {
      snapZoneEl.classList.remove("active");
    }
  });

  window.addEventListener("mouseup", (e) => {
    if (!isDragging) return;
    isDragging = false;
    snapZoneEl.classList.remove("active");

    if (detachingEdge) {
      spX.target = detachAnchorX;
      spY.target = detachAnchorY;
      spScaleX.target = 1.0;
      spScaleY.target = 1.0;
      detachingEdge = null;
      return;
    }

    const cand = computeSnapCandidate(spX.value, spY.value, spW.value, spH.value, e.clientX, e.clientY);
    let dockEdge = null;
    if (cand) {
      dockEdge = cand.edge;
      spX.target = cand.x;
      spY.target = cand.y;
      if (dockEdge.includes("left") || dockEdge.includes("right")) {
        spScaleX.velocity -= 2.0;
        spScaleY.velocity += 1.5;
      } else {
        spScaleX.velocity += 1.5;
        spScaleY.velocity -= 2.0;
      }
    } else {
      spX.target = spX.value;
      spY.target = spY.value;
    }

    const vw = Math.max(1, window.innerWidth - spW.value);
    const vh = Math.max(1, window.innerHeight - spH.value);
    sendMsg({
      type: "PATCH_STATE",
      patch: {
        dockEdge,
        rx: Math.max(0, Math.min(1, spX.target / vw)),
        ry: Math.max(0, Math.min(1, spY.target / vh))
      }
    });
  });

  function cycleSize() {
    const order = ["mini", "medium", "large"];
    const next = order[(order.indexOf(state.sizeMode) + 1) % order.length];
    sendMsg({ type: "PATCH_STATE", patch: { sizeMode: next } });
  }

  function handleAction(act) {
    if (act === "play") sendMsg({ type: "TOGGLE_PLAY" });
    else if (act === "reset") sendMsg({ type: "RESET" });
    else if (act === "toggle_mode") sendMsg({ type: "SWITCH_MODE" });
    else if (act === "cycle_size") cycleSize();
    else if (act === "shrink_size") {
      const next = state.sizeMode === "large" ? "medium" : "mini";
      sendMsg({ type: "PATCH_STATE", patch: { sizeMode: next } });
    } else if (act === "grow_size") {
      const next = state.sizeMode === "mini" ? "medium" : "large";
      sendMsg({ type: "PATCH_STATE", patch: { sizeMode: next } });
    } else if (act === "open_settings") {
      openSettingsModal();
    } else if (act === "opacity") {
      const presets = [0.95, 0.85, 0.6, 0.35];
      let idx = 0;
      let best = 999;
      presets.forEach((p, i) => {
        if (Math.abs(p - state.opacity) < best) { best = Math.abs(p - state.opacity); idx = i; }
      });
      sendMsg({ type: "PATCH_STATE", patch: { opacity: presets[(idx + 1) % presets.length] } });
    } else if (act === "sub_5m") sendMsg({ type: "ADJUST_TIMER", delta: -300 });
    else if (act === "sub_1m") sendMsg({ type: "ADJUST_TIMER", delta: -60 });
    else if (act === "add_1m") sendMsg({ type: "ADJUST_TIMER", delta: 60 });
    else if (act === "add_5m") sendMsg({ type: "ADJUST_TIMER", delta: 300 });
    else if (act.startsWith("preset_")) {
      const mins = parseInt(act.split("_")[1], 10);
      sendMsg({ type: "SET_TIMER", seconds: mins * 60 });
    } else if (act === "close") {
      sendMsg({ type: "PATCH_STATE", patch: { visible: false } });
    }
  }

  let summonedFocus = false;
  let alarmFlash = 0.0;
  let prevLiveSec = 25 * 60;

  function playWebAlarm() {
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      const ctx = new Ctx();
      const notes = [
        [783.99, 0.0, 0.14], [987.77, 0.15, 0.14], [1174.66, 0.30, 0.28],
        [783.99, 0.68, 0.14], [987.77, 0.83, 0.14], [1174.66, 0.98, 0.28],
        [783.99, 1.36, 0.14], [987.77, 1.51, 0.14], [1567.98, 1.66, 0.42]
      ];
      notes.forEach(([freq, startOffset, dur]) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "triangle";
        osc.frequency.value = freq;
        const t0 = ctx.currentTime + startOffset;
        gain.gain.setValueAtTime(0.001, t0);
        gain.gain.linearRampToValueAtTime(0.35, t0 + 0.01);
        gain.gain.exponentialRampToValueAtTime(0.001, t0 + dur);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(t0);
        osc.stop(t0 + dur + 0.02);
      });
    } catch (e) {}
  }

  // Summon hotkey (Right Shift / Right Ctrl) & exclusive key capture when summoned
  window.addEventListener("keydown", (e) => {
    if (editingTime || settingsOpen) return;
    const summonKey = (state.hotkeys && state.hotkeys.summon) || "ShiftRight";
    if ((e.code === summonKey || e.code === "ShiftRight" || e.code === "ControlRight") && !e.repeat) {
      summonedFocus = !summonedFocus;
      alarmFlash = 0;
      spScaleX.velocity += summonedFocus ? 1.4 : -1.1;
      spScaleY.velocity += summonedFocus ? -1.4 : 1.1;
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      return;
    }
    if (!summonedFocus) return;

    // Block all plain keys from reaching the open webpage while timer is summoned!
    if (!e.ctrlKey && !e.altKey && !e.metaKey) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
    }

    if (e.repeat) return;
    if (e.code === "Escape") {
      summonedFocus = false;
    } else if (e.code === "Space") {
      alarmFlash = 0;
      sendMsg({ type: "TOGGLE_PLAY" });
    } else if (e.code === "KeyR" || e.code === "AltRight") {
      alarmFlash = 0;
      sendMsg({ type: "RESET" });
    } else if (e.code === "KeyM") {
      sendMsg({ type: "SWITCH_MODE" });
    } else if (e.code === "KeyS") {
      cycleSize();
    }
  }, true);

  window.addEventListener("mousedown", (e) => {
    if (summonedFocus && e.target !== host) {
      summonedFocus = false;
    }
  }, true);

  // Load initial state & subscribe to cross-tab storage changes
  chrome.storage.local.get(["jellyState"], (res) => {
    if (res.jellyState) {
      state = { ...state, ...res.jellyState };
    }
    prevLiveSec = getLiveSeconds();
    applyDockedPositionFromState(true);
    rebuildDOM();
  });

  chrome.storage.onChanged.addListener((changes, area) => {
    if (area === "local" && changes.jellyState && changes.jellyState.newValue) {
      state = { ...state, ...changes.jellyState.newValue };
      applyDockedPositionFromState(false);
      rebuildDOM();
    }
  });

  window.addEventListener("resize", () => applyDockedPositionFromState(false));

  // 60 FPS Animation loop with dirty-checking (zero DOM mutations when idle)
  let lastFrame = performance.now();
  let lastGeomSig = "";
  let lastVisualSig = "";
  function tick(now) {
    const dt = (now - lastFrame) / 1000.0;
    lastFrame = now;

    if (!state.visible) {
      requestAnimationFrame(tick);
      return;
    }

    const curSec = getLiveSeconds();
    if (state.mode === "timer" && prevLiveSec > 0 && curSec <= 0) {
      alarmFlash = 6.0;
      spScaleX.velocity += 2.2;
      spScaleY.velocity -= 2.2;
      playWebAlarm();
    }
    prevLiveSec = curSec;

    let bgStr, brdStr;
    if (alarmFlash > 0) {
      alarmFlash = Math.max(0, alarmFlash - dt);
      const pulse = Math.sin(alarmFlash * 14.0) * 0.5 + 0.5;
      const th = THEMES[state.themeKey] || THEMES.graphite;
      const [br, bg, bb] = th.bg.split(",").map((v) => parseInt(v.trim(), 10));
      const mix = pulse * 0.88;
      const r = Math.round(br * (1 - mix) + 225 * mix);
      const g = Math.round(bg * (1 - mix) + 24 * mix);
      const b = Math.round(bb * (1 - mix) + 34 * mix);
      const a = Math.max(state.opacity, 0.96 * pulse);
      bgStr = `rgba(${r}, ${g}, ${b}, ${a})`;
      brdStr = `2.2px solid rgba(255, 95, 95, ${0.75 + 0.25 * pulse})`;
    } else {
      const th = THEMES[state.themeKey] || THEMES.graphite;
      bgStr = `rgba(${th.bg}, ${state.opacity})`;
      brdStr = summonedFocus ? "1.8px solid rgba(244, 244, 245, 0.95)" : `1px solid ${th.border}`;
    }

    const vSig = `${bgStr}|${brdStr}`;
    if (vSig !== lastVisualSig) {
      lastVisualSig = vSig;
      cardEl.style.background = bgStr;
      cardEl.style.border = brdStr;
    }

    spX.step(dt);
    spY.step(dt);
    spW.step(dt);
    spH.step(dt);
    spScaleX.step(dt);
    spScaleY.step(dt);

    const gSig = `${spX.value.toFixed(1)}|${spY.value.toFixed(1)}|${spW.value.toFixed(1)}|${spH.value.toFixed(1)}|${spScaleX.value.toFixed(3)}|${spScaleY.value.toFixed(3)}`;
    if (gSig !== lastGeomSig) {
      lastGeomSig = gSig;
      cardEl.style.left = `${spX.value.toFixed(1)}px`;
      cardEl.style.top = `${spY.value.toFixed(1)}px`;
      cardEl.style.width = `${spW.value.toFixed(1)}px`;
      cardEl.style.height = `${spH.value.toFixed(1)}px`;
      cardEl.style.transform = `scale(${spScaleX.value.toFixed(3)}, ${spScaleY.value.toFixed(3)})`;
    }

    if (state.isRunning || alarmFlash > 0) {
      updateTimeText();
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
