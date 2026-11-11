(() => {
  const I18N = {
    en: {
      title: "Welcome to Jelly Timer!",
      desc1: "<strong>Jelly Timer</strong> works on any webpage, except a few system pages restricted by the browser's security policy.",
      desc2: "Blank startup tabs (New Tab), browser settings, and extension store pages are protected from floating widgets by Chrome.",
      desc3: "Switch to any website or click below to start working with the timer right away:",
      btnWorkspace: "Open Jelly Timer Workspace →",
      btnExample: "Try on a regular webpage (Google)"
    },
    ru: {
      title: "Jelly Timer готов к работе!",
      desc1: "<strong>Jelly Timer</strong> работает на любых веб-сайтах, за исключением нескольких страниц, защищённых политикой безопасности самого браузера.",
      desc2: "На пустой начальной вкладке («Новая вкладка»), в настройках браузера и в магазине расширений показ плавающих виджетов заблокирован браузером.",
      desc3: "Перейдите на любой сайт или нажмите кнопку ниже, чтобы сразу запустить таймер:",
      btnWorkspace: "Открыть рабочую вкладку с таймером →",
      btnExample: "Попробовать на обычной странице (Google)"
    },
    kz: {
      title: "Jelly Timer жұмысқа дайын!",
      desc1: "<strong>Jelly Timer</strong> браузердің қауіпсіздік саясатымен қорғалған жүйелік беттерден басқа кез келген веб-сайтта жұмыс істейді.",
      desc2: "Бос бастапқы бетте («Жаңа қойынды»), браузер баптауларында және кеңейтімдер дүкенінде қалқымалы виджеттерге браузер рұқсат бермейді.",
      desc3: "Таймерді бірден іске қосу үшін кез келген сайтты ашыңыз немесе төмендегі батырманы басыңыз:",
      btnWorkspace: "Таймері бар жұмыс бетін ашу →",
      btnExample: "Қалыпты бетте тексеру (Google)"
    }
  };

  function detectLang() {
    const nav = ((navigator && navigator.language) || "en").toLowerCase();
    if (nav.startsWith("kk") || nav.startsWith("kz")) return "kz";
    if (nav.startsWith("ru")) return "ru";
    return "en";
  }

  function applyLang(lang) {
    const t = I18N[lang] || I18N.en;
    document.getElementById("pTitle").textContent = t.title;
    document.getElementById("pDesc1").innerHTML = t.desc1;
    document.getElementById("pDesc2").textContent = t.desc2;
    document.getElementById("pDesc3").textContent = t.desc3;
    document.getElementById("btnOpenWorkspace").textContent = t.btnWorkspace;
    document.getElementById("btnTryExample").textContent = t.btnExample;
  }

  applyLang(detectLang());

  document.getElementById("btnOpenWorkspace").addEventListener("click", () => {
    chrome.tabs.create({ url: chrome.runtime.getURL("pro_upgrade.html") });
    window.close();
  });

  document.getElementById("btnTryExample").addEventListener("click", () => {
    chrome.tabs.create({ url: "https://www.wikipedia.org/" });
    window.close();
  });

  chrome.storage.local.get(["jellyState"], (res) => {
    const st = (res && res.jellyState) ? res.jellyState : { visible: true };
    if (st.lang && I18N[st.lang]) {
      applyLang(st.lang);
    }
    if (st.appVersion) {
      const exp = st.exportBuild ? ` • #${String(st.exportBuild).padStart(2, "0")}` : "";
      document.getElementById("pBadge").textContent = `v${st.appVersion}${exp}`;
    }

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs && tabs[0];
      if (!tab || typeof tab.id !== "number") {
        document.body.classList.add("show-notice");
        return;
      }

      try {
        chrome.tabs.sendMessage(tab.id, { type: "PING_ACTIVE_TAB" }, (resp) => {
          const err = chrome.runtime.lastError;
          if (!err && resp && resp.ok) {
            // Content script is active on this webpage -> toggle widget visibility and close popup immediately
            st.visible = !st.visible;
            chrome.storage.local.set({ jellyState: st }, () => {
              window.close();
            });
          } else {
            // Restricted browser page (chrome://newtab, Chrome Web Store, etc.) -> ensure visible=true and show explanation card!
            st.visible = true;
            chrome.storage.local.set({ jellyState: st });
            document.body.classList.add("show-notice");
          }
        });
      } catch (e) {
        st.visible = true;
        chrome.storage.local.set({ jellyState: st });
        document.body.classList.add("show-notice");
      }
    });
  });
})();
