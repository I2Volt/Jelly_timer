const EXT_VERSION = "1.2.2";
const EXPORT_BUILD = 7;
const BUILD_DATE = "2026-11-08";
const REMOTE_VERSION_URL = "https://raw.githubusercontent.com/I2Volt/Jelly_timer/main/version_info.json";

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
  presets: [5, 15, 25, 45, 60],
  globalHotkeys: false,
  appVersion: EXT_VERSION,
  exportBuild: EXPORT_BUILD,
  buildDate: BUILD_DATE,
  hotkeys: {
    summon: "ShiftRight",
    play_pause: "Space",
    reset: "KeyR",
    switch_mode: "KeyM",
    cycle_size: "KeyS"
  }
};

function syncRemoteVersionMeta(callback) {
  fetch(REMOTE_VERSION_URL, { cache: "no-store" })
    .then((r) => (r.ok ? r.json() : null))
    .then((data) => {
      if (data) {
        chrome.storage.local.set({ jellyRemoteMeta: data }, () => {
          if (callback) callback(data);
        });
      } else if (callback) {
        callback(null);
      }
    })
    .catch(() => {
      if (callback) callback(null);
    });
}

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get(["jellyState"], (res) => {
    const merged = {
      ...DEFAULT_STATE,
      ...(res.jellyState || {}),
      visible: true,
      appVersion: EXT_VERSION,
      exportBuild: EXPORT_BUILD,
      buildDate: BUILD_DATE
    };
    chrome.storage.local.set({ jellyState: merged });
  });
  syncRemoteVersionMeta();
});

// Toggle widget visibility when clicking the extension toolbar icon
// If clicked on a restricted page (chrome://newtab, Chrome Web Store, etc.) where content scripts are blocked,
// ensure visible=true and open the built-in Jelly Timer workspace page where the floating timer is active.
chrome.action.onClicked.addListener((tab) => {
  chrome.storage.local.get(["jellyState"], (res) => {
    const st = { ...DEFAULT_STATE, ...(res.jellyState || {}) };
    if (tab && typeof tab.id === "number") {
      try {
        chrome.tabs.sendMessage(tab.id, { type: "PING_ACTIVE_TAB" }, (resp) => {
          const err = chrome.runtime.lastError;
          if (!err && resp && resp.ok) {
            st.visible = !st.visible;
            chrome.storage.local.set({ jellyState: st });
          } else {
            st.visible = true;
            chrome.storage.local.set({ jellyState: st }, () => {
              chrome.tabs.create({ url: chrome.runtime.getURL("pro_upgrade.html") });
            });
          }
        });
      } catch (e) {
        st.visible = true;
        chrome.storage.local.set({ jellyState: st }, () => {
          chrome.tabs.create({ url: chrome.runtime.getURL("pro_upgrade.html") });
        });
      }
    } else {
      st.visible = !st.visible;
      chrome.storage.local.set({ jellyState: st });
    }
  });
});

// Handle atomic time/state updates from any tab
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "OPEN_PRO_PAGE") {
    chrome.tabs.create({ url: chrome.runtime.getURL("pro_upgrade.html") });
    sendResponse({ ok: true });
    return true;
  }

  if (msg.type === "CHECK_UPDATES") {
    syncRemoteVersionMeta((meta) => {
      sendResponse({ ok: true, meta, localVersion: EXT_VERSION, localExport: EXPORT_BUILD });
    });
    return true;
  }

  chrome.storage.local.get(["jellyState"], (res) => {
    let st = {
      ...DEFAULT_STATE,
      ...(res.jellyState || {}),
      appVersion: EXT_VERSION,
      exportBuild: EXPORT_BUILD,
      buildDate: BUILD_DATE
    };
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
      if (st.timerRemaining <= 0) {
        st.isRunning = false;
        st.lastTimestamp = null;
      }
      if ((!st.isRunning || st.timerRemaining > st.timerTotal) && st.timerRemaining > 0) {
        st.timerTotal = st.timerRemaining;
      }
    } else if (msg.type === "TIMER_FINISHED") {
      st.isRunning = false;
      st.lastTimestamp = null;
      st.timerRemaining = 0;
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
