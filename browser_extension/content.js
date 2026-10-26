(() => {
  if (window.__jellyTimerInjected) return;
  window.__jellyTimerInjected = true;

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
    hotkeys: {
      play_pause: "ControlRight",
      reset: "AltRight",
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
  `;
  shadow.appendChild(style);

  const snapZoneEl = document.createElement("div");
  snapZoneEl.className = "snap-zone";
  shadow.appendChild(snapZoneEl);

  const cardEl = document.createElement("div");
  cardEl.className = "card";
  shadow.appendChild(cardEl);

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
    const modeLabel = state.mode === "timer" ? "Таймер" : "Секундомер";
    const playIcon = state.isRunning ? SVGS.pause : SVGS.play;
    const playLabel = state.isRunning ? "Пауза" : "Старт";

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
            <button class="btn" data-act="opacity" style="width:22px;height:22px;padding:0;">${SVGS.opacity}</button>
            <button class="btn" data-act="cycle_size" style="width:22px;height:22px;padding:0;">${SVGS.expand}</button>
            <button class="btn" data-act="close" style="width:22px;height:22px;padding:0;">${SVGS.close}</button>
          </div>
        </div>
        <div class="time-box" data-act="time_box" style="font-size:31px;margin:2px 0;"></div>
        <div class="bottom-row" style="justify-content:center;">
          ${state.mode === "timer" ? `
            <button class="btn" data-act="sub_1m" style="height:26px;">-1м</button>
            <button class="btn primary" data-act="play" style="height:26px;flex:1;">${playIcon} <span>${playLabel}</span></button>
            <button class="btn" data-act="reset" style="width:32px;height:26px;padding:0;">${SVGS.reset}</button>
            <button class="btn" data-act="add_1m" style="height:26px;">+1м</button>
            <button class="btn" data-act="add_5m" style="height:26px;">+5м</button>
          ` : `
            <button class="btn primary" data-act="play" style="height:26px;width:96px;">${playIcon} <span>${playLabel}</span></button>
            <button class="btn" data-act="reset" style="width:34px;height:26px;padding:0;">${SVGS.reset}</button>
          `}
        </div>
        ${state.mode === "timer" ? `<div class="progress-track"><div class="progress-fill"></div></div>` : ""}
      `;
    } else {
      cardEl.style.flexDirection = "column";
      cardEl.style.padding = "12px 12px 14px 12px";
      cardEl.innerHTML = `
        <div class="top-row">
          <button class="btn" data-act="toggle_mode" style="height:24px;">${modeIcon} <span>${modeLabel}</span> ${SVGS.swap}</button>
          <div style="display:flex;gap:4px;">
            <button class="btn" data-act="opacity" style="width:24px;height:24px;padding:0;">${SVGS.opacity}</button>
            <button class="btn" data-act="cycle_size" style="width:24px;height:24px;padding:0;">${SVGS.expand}</button>
            <button class="btn" data-act="close" style="width:24px;height:24px;padding:0;">${SVGS.close}</button>
          </div>
        </div>
        <div class="time-box" data-act="time_box" style="font-size:40px;margin:2px 0;"></div>
        ${state.mode === "timer" ? `
          <div class="preset-row">
            <button class="btn" data-act="preset_5" style="flex:1;height:24px;">5м</button>
            <button class="btn" data-act="preset_15" style="flex:1;height:24px;">15м</button>
            <button class="btn" data-act="preset_25" style="flex:1;height:24px;">25м</button>
            <button class="btn" data-act="preset_45" style="flex:1;height:24px;">45м</button>
            <button class="btn" data-act="preset_60" style="flex:1;height:24px;">60м</button>
          </div>
        ` : ""}
        <div class="bottom-row" style="justify-content:center;">
          ${state.mode === "timer" ? `
            <button class="btn" data-act="sub_1m" style="height:28px;">-1 мин</button>
            <button class="btn primary" data-act="play" style="height:28px;flex:1;">${playIcon} <span>${playLabel}</span></button>
            <button class="btn" data-act="reset" style="width:40px;height:28px;padding:0;">${SVGS.reset}</button>
            <button class="btn" data-act="add_1m" style="height:28px;">+1 мин</button>
          ` : `
            <button class="btn primary" data-act="play" style="height:28px;width:110px;">${playIcon} <span>${playLabel}</span></button>
            <button class="btn" data-act="reset" style="width:38px;height:28px;padding:0;">${SVGS.reset}</button>
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
    else if (act === "opacity") {
      const presets = [0.95, 0.85, 0.6, 0.35];
      let idx = 0;
      let best = 999;
      presets.forEach((p, i) => {
        if (Math.abs(p - state.opacity) < best) { best = Math.abs(p - state.opacity); idx = i; }
      });
      sendMsg({ type: "PATCH_STATE", patch: { opacity: presets[(idx + 1) % presets.length] } });
    } else if (act === "sub_1m") sendMsg({ type: "ADJUST_TIMER", delta: -60 });
    else if (act === "add_1m") sendMsg({ type: "ADJUST_TIMER", delta: 60 });
    else if (act === "add_5m") sendMsg({ type: "ADJUST_TIMER", delta: 300 });
    else if (act.startsWith("preset_")) {
      const mins = parseInt(act.split("_")[1], 10);
      sendMsg({ type: "SET_TIMER", seconds: mins * 60 });
    } else if (act === "close") {
      sendMsg({ type: "PATCH_STATE", patch: { visible: false } });
    }
  }

  // Writer-friendly hotkeys on page (Right Ctrl = Play/Pause, Right Alt = Reset)
  window.addEventListener("keydown", (e) => {
    if (editingTime) return;
    if (e.code === state.hotkeys.play_pause && !e.repeat) {
      sendMsg({ type: "TOGGLE_PLAY" });
    } else if (e.code === state.hotkeys.reset && !e.repeat) {
      sendMsg({ type: "RESET" });
    }
  });

  // Load initial state & subscribe to cross-tab storage changes
  chrome.storage.local.get(["jellyState"], (res) => {
    if (res.jellyState) {
      state = { ...state, ...res.jellyState };
    }
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

  // 60 FPS Animation loop
  let lastFrame = performance.now();
  function tick(now) {
    const dt = (now - lastFrame) / 1000.0;
    lastFrame = now;

    spX.step(dt);
    spY.step(dt);
    spW.step(dt);
    spH.step(dt);
    spScaleX.step(dt);
    spScaleY.step(dt);

    cardEl.style.left = `${spX.value}px`;
    cardEl.style.top = `${spY.value}px`;
    cardEl.style.width = `${spW.value}px`;
    cardEl.style.height = `${spH.value}px`;
    cardEl.style.transform = `scale(${spScaleX.value}, ${spScaleY.value})`;

    updateTimeText();
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
