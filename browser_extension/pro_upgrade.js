(() => {
  const REMOTE_VERSION_URL = "https://raw.githubusercontent.com/I2Volt/Jelly_timer/main/version_info.json";
  const linkEl = document.getElementById("proExternalLink");
  const badgeEl = document.getElementById("versionBadge");
  const buildInfoEl = document.getElementById("buildInfoText");
  const syncStatusEl = document.getElementById("syncStatusText");

  const DICT = {
    en: {
      h1: "Always-on-top desktop timer, Pomodoro, Flowtime & focus analytics.",
      sub: "While the browser extension stays inside your web tabs, Jelly Timer Plus (PRO) runs natively above all Windows and macOS applications — IDEs, Figma, Notion, spreadsheets, and documents.",
      c1_t: "Pomodoro & Flowtime",
      c1_p: "Automated work/break intervals and uninterrupted Flowtime mode that calculates a smart 1/5 break duration based on your actual focus time.",
      c2_t: "Auto-Focus by Active Window",
      c2_p: "Automatically resumes your timer when you switch into work applications (VS Code, Word, Figma, Docs) and pauses when you switch away.",
      c3_t: "7-Day Focus Analytics",
      c3_p: "Visual 7-day bar chart of deep focus minutes, completed session counter, and automatic log of top applications used during focus.",
      c4_t: "528 Hz Zen & Chime Audio",
      c4_p: "Choose between classic alarm, soft harmonic Chime chord, and 528 Hz Zen tone, plus Deep Obsidian and Slate Titanium themes.",
      cmp_title: "Edition Comparison",
      th_f: "Feature",
      th_ext: "Browser Extension",
      th_pro: "Jelly Timer Plus (PRO)",
      r1: "Magnetic edge-snap & spring peel-off physics",
      r2: "Writer-friendly focus key (Right Shift / Right Ctrl)",
      r3: "Floats over all Windows & macOS applications outside browser",
      r4: "Pomodoro & Flowtime (smart 1/5 break calculation)",
      r5: "Auto-start & auto-pause by active window title",
      r6: "7-day focus chart & active application tracker",
      cta_h: "Jelly Timer Plus (PRO) — Desktop Edition",
      cta_p: "Explore specifications and download builds for Windows and macOS.",
      cta_btn: "Open Jelly Timer Plus Page →"
    },
    ru: {
      h1: "Десктопный таймер поверх всех программ, Помодоро, Flowtime и аналитика.",
      sub: "Браузерное расширение работает внутри вкладок, а десктопная версия Jelly Timer Plus (PRO) живёт поверх любых программ Windows и macOS — IDE, Figma, Notion, таблиц и документов.",
      c1_t: "Помодоро и Flowtime",
      c1_p: "Автоматические циклы работы и отдыха и режим свободного потока Flowtime (умный перерыв 1/5 от времени вашей реальной концентрации).",
      c2_t: "Авто-фокус по активному окну",
      c2_p: "Таймер сам продолжает отсчёт, когда вы открываете рабочую программу (VS Code, Word, Figma, Docs), и ставится на паузу при отвлечении.",
      c3_t: "Статистика за 7 дней и топ окон",
      c3_p: "Наглядный график минут глубокого фокуса по дням и автоматический учёт программ, в которых вы реально работали.",
      c4_t: "Синтезатор звука (528 Гц Zen и Chime)",
      c4_p: "Выбор между классическим сигналом, мягким аккордом Chime и частотой 528 Гц, плюс темы «Глубокий оникс» и «Холодный титан».",
      cmp_title: "Сравнение версий",
      th_f: "Возможность",
      th_ext: "Расширение браузера",
      th_pro: "Jelly Timer Plus (PRO)",
      r1: "Магнитные края и упругая желейная физика отрыва",
      r2: "Удобные клавиши без отрыва от печати (Right Shift / Right Ctrl)",
      r3: "Работа поверх всех программ Windows / macOS вне браузера",
      r4: "Режимы Помодоро и Flowtime (умный перерыв 1/5)",
      r5: "Авто-старт и авто-пауза при открытии рабочих окон",
      r6: "Статистика концентрации за 7 дней + трекер активных окон",
      cta_h: "Jelly Timer Plus (PRO) — Десктопная версия",
      cta_p: "Узнайте подробности и скачайте актуальную сборку для Windows и macOS.",
      cta_btn: "Открыть страницу Jelly Timer Plus →"
    },
    kz: {
      h1: "Барлық бағдарламалардың үстінде тұратын таймер, Помодоро, Flowtime және аналитика.",
      sub: "Браузер кеңейтімі қойындылар ішінде жұмыс істесе, Jelly Timer Plus (PRO) десктоп нұсқасы Windows және macOS-тағы кез келген бағдарламаның (IDE, Figma, Notion, құжаттар) үстінде жұмыс істейді.",
      c1_t: "Помодоро және Flowtime",
      c1_p: "Автоматты жұмыс/демалыс циклдері және еркін ағын Flowtime режимі (нақты жұмыс уақытының 1/5 бөлігіне тең үзіліс).",
      c2_t: "Белсенді терезе бойынша авто-фокус",
      c2_p: "Жұмыс бағдарламасын (VS Code, Word, Figma, Docs) ашқанда таймер өздігінен қосылып, басқа терезеге ауысқанда кідіреді.",
      c3_t: "7 күндік фокус статистикасы",
      c3_p: "Күндер бойынша терең фокус минуттарының графигі және сіз жұмыс істеген негізгі бағдарламалар тізімі.",
      c4_t: "528 Гц Zen және Chime дыбыстары",
      c4_p: "Классикалық сигнал, жұмсақ Chime аккорды және 528 Гц жиілігі, сондай-ақ «Оникс» пен «Титан» тақырыптары.",
      cmp_title: "Нұсқаларды салыстыру",
      th_f: "Мүмкіндік",
      th_ext: "Браузер кеңейтімі",
      th_pro: "Jelly Timer Plus (PRO)",
      r1: "Магнитті жиектер және серпімді физика",
      r2: "Мәтін теруден қол үзбей басқару (Right Shift / Right Ctrl)",
      r3: "Браузерден тыс барлық Windows / macOS терезелерінің үстінде тұру",
      r4: "Помодоро және Flowtime режимдері (1/5 үзіліс)",
      r5: "Жұмыс терезелерін ашқанда авто-қосылу және авто-кідірту",
      r6: "7 күндік статистика + белсенді терезелер трекері",
      cta_h: "Jelly Timer Plus (PRO) — Десктоп нұсқасы",
      cta_p: "Толық ақпаратпен танысып, Windows және macOS жинақтарын жүктеп алыңыз.",
      cta_btn: "Jelly Timer Plus бетін ашу →"
    }
  };

  function detectLang() {
    const nav = ((navigator && navigator.language) || "en").toLowerCase();
    if (nav.startsWith("kk") || nav.startsWith("kz")) return "kz";
    if (nav.startsWith("ru")) return "ru";
    return "en";
  }

  function applyLang(lang) {
    const c = DICT[lang] ? lang : "en";
    document.documentElement.lang = c;
    document.querySelectorAll(".pill-btn[data-lang]").forEach((b) => {
      b.classList.toggle("active", b.getAttribute("data-lang") === c);
    });
    const d = DICT[c];
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const k = el.getAttribute("data-i18n");
      if (d[k]) el.textContent = d[k];
    });
  }

  document.querySelectorAll(".pill-btn[data-lang]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const next = btn.getAttribute("data-lang");
      applyLang(next);
      if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
        chrome.storage.local.get(["jellyState"], (res) => {
          if (res && res.jellyState) {
            chrome.storage.local.set({ jellyState: { ...res.jellyState, lang: next } });
          }
        });
      }
    });
  });

  applyLang(detectLang());

  function applyMeta(meta) {
    if (!meta) return;
    const ver = meta.app_version || "1.2.0";
    const exp = String(meta.export_build || 5).padStart(2, "0");
    const dt = meta.build_date || "2026-11-05";
    if (badgeEl) badgeEl.textContent = `v${ver} • Exp #${exp}`;
    if (buildInfoEl) buildInfoEl.textContent = `Package: v${ver} • Export #${exp} (${dt})`;
    if (linkEl && meta.pro_landing_url) {
      linkEl.href = meta.pro_landing_url;
    }
  }

  if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
    chrome.storage.local.get(["jellyRemoteMeta", "jellyState"], (res) => {
      if (res && res.jellyState && res.jellyState.lang) {
        applyLang(res.jellyState.lang);
      }
      if (res && res.jellyRemoteMeta) {
        applyMeta(res.jellyRemoteMeta);
      }
    });
  }

  fetch(REMOTE_VERSION_URL, { cache: "no-store" })
    .then((r) => (r.ok ? r.json() : null))
    .then((data) => {
      if (data) {
        applyMeta(data);
        if (syncStatusEl) {
          syncStatusEl.textContent = `Latest release: v${data.app_version} (Exp #${String(data.export_build || 5).padStart(2, "0")})`;
        }
        if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
          chrome.storage.local.set({ jellyRemoteMeta: data });
        }
      }
    })
    .catch(() => {});
})();
