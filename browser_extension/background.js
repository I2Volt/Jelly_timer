const DEFAULT_STATE = {
  visible: true,
  mode: "timer",          // "timer" | "stopwatch"
  sizeMode: "medium",     // "mini" | "medium" | "large"
  themeKey: "graphite",   // "graphite" | "warm_espresso" | "soft_sage"
  opacity: 0.88,
  snapEnabled: true,
  dockEdge: "top_right",  // null | "left" | "right" | "top" | "bottom" | corners
  rx: 0.82,               // relative X (0..1) so position adapts across window sizes
  ry: 0.06,               // relative Y (0..1)
  timerTotal: 25 * 60,    // seconds
  timerRemaining: 25 * 60,
  stopwatchElapsed: 0,
  isRunning: false,
  lastTimestamp: null,    // Date.now() in ms when running
  hotkeys: {
    play_pause: "ControlRight",
    reset: "AltRight",
    switch_mode: "KeyM",
    cycle_size: "KeyS"
  }
};

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get(["jellyState"], (res) => {
    if (!res.jellyState) {
      chrome.storage.local.set({ jellyState: DEFAULT_STATE });
    }
  });
});

// Toggle widget visibility when clicking the extension toolbar icon
chrome.action.onClicked.addListener(() => {
  chrome.storage.local.get(["jellyState"], (res) => {
    const st = res.jellyState || DEFAULT_STATE;
    st.visible = !st.visible;
    chrome.storage.local.set({ jellyState: st });
  });
});

// Handle atomic time/state updates from any tab
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  chrome.storage.local.get(["jellyState"], (res) => {
    let st = { ...DEFAULT_STATE, ...(res.jellyState || {}) };
    const now = Date.now();

    // First synchronize live running clock before applying action
    if (st.isRunning && st.lastTimestamp) {
      const dt = (now - st.lastTimestamp) / 1000.0;
      if (st.mode === "timer") {
        st.timerRemaining = Math.max(0, st.timerRemaining - dt);
        if (st.timerRemaining <= 0) {
          st.isRunning = false;
          st.lastTimestamp = null;
        } else {
          st.lastTimestamp = now;
        }
      } else {
        st.stopwatchElapsed += dt;
        st.lastTimestamp = now;
      }
    }

    if (msg.type === "TOGGLE_PLAY") {
      if (st.mode === "timer" && st.timerRemaining <= 0) {
        st.timerRemaining = st.timerTotal;
      }
      st.isRunning = !st.isRunning;
      st.lastTimestamp = st.isRunning ? now : null;
    } else if (msg.type === "RESET") {
      st.isRunning = false;
      st.lastTimestamp = null;
      if (st.mode === "timer") {
        st.timerRemaining = st.timerTotal;
      } else {
        st.stopwatchElapsed = 0;
      }
    } else if (msg.type === "SWITCH_MODE") {
      st.isRunning = false;
      st.lastTimestamp = null;
      st.mode = msg.mode || (st.mode === "timer" ? "stopwatch" : "timer");
    } else if (msg.type === "ADJUST_TIMER") {
      st.mode = "timer";
      st.timerRemaining = Math.max(0, Math.min(999 * 3600, st.timerRemaining + msg.delta));
      if (!st.isRunning || st.timerRemaining > st.timerTotal) {
        st.timerTotal = Math.max(1, st.timerRemaining);
      }
    } else if (msg.type === "SET_TIMER") {
      st.mode = "timer";
      st.isRunning = false;
      st.lastTimestamp = null;
      st.timerTotal = Math.max(1, Math.min(999 * 3600, msg.seconds));
      st.timerRemaining = st.timerTotal;
    } else if (msg.type === "PATCH_STATE") {
      st = { ...st, ...msg.patch };
    }

    chrome.storage.local.set({ jellyState: st }, () => {
      sendResponse({ ok: true, state: st });
    });
  });
  return true;
});
