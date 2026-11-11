(() => {
  const REMOTE_VERSION_URL = "https://raw.githubusercontent.com/I2Volt/Jelly_timer/main/version_info.json";
  const checkoutBtnEl = document.getElementById("proCheckoutBtn");
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
      r2: "Customizable hotkeys & summon key",
      r3: "Floats over all Windows & macOS applications outside browser",
      r4: "Pomodoro & Flowtime (smart 1/5 break calculation)",
      r5: "Auto-start & auto-pause by active window title",
      r6: "7-day focus chart & active application tracker",
      cta_h: "Jelly Timer Plus (PRO) — Includes Desktop PRO Version",
      cta_p: "The extension works inside your browser; when you get PRO, you also receive the standalone Desktop PRO Version for your PC/MacBook.",
      cta_buy_btn: "Get PRO →",
      cta_sup_btn: "Support Form",
      cta_free_btn: "GitHub Releases",
      f_title: "Support & Feedback Form",
      f_sub: "Fill out the form below — your response will be recorded directly without needing an email app.",
      f_contact: "Your Name or Contact (Telegram / handle, optional)",
      f_topic: "Category",
      f_opt_pro: "Question about PRO / Desktop Version",
      f_opt_bug: "Bug Report / Technical Issue",
      f_opt_idea: "Feature Request / Idea",
      f_opt_refund: "Order / Refund Inquiry",
      f_msg: "Your Question or Description *",
      f_submit: "Submit Form",
      f_done_title: "Your response has been recorded!",
      f_again: "Submit another response"
    },
    ru: {
      h1: "Десктопный таймер поверх всех программ, Помодоро, Flowtime и аналитика.",
      sub: "Браузерное расширение работает внутри вкладок одного браузера, а при приобретении Jelly Timer Plus (PRO) вам также отправляется полная Десктоп PRO-версия для ноутбука и ПК (поверх всех окон, IDE, документов и таблиц).",
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
      r2: "Полная настройка всех горячих клавиш",
      r3: "Работа поверх всех программ Windows / macOS вне браузера",
      r4: "Режимы Помодоро и Flowtime (умный перерыв 1/5)",
      r5: "Авто-старт и авто-пауза при открытии рабочих окон",
      r6: "Статистика концентрации за 7 дней + трекер активных окон",
      cta_h: "Jelly Timer Plus (PRO) — Десктоп PRO-версия в комплекте",
      cta_p: "В браузере мы работаем в рамках вкладок, а при покупке PRO вам отправляется полная Десктоп PRO-версия для Windows и macOS.",
      cta_buy_btn: "Получить PRO →",
      cta_sup_btn: "Форма поддержки",
      cta_free_btn: "GitHub Releases",
      f_title: "Форма поддержки и обратной связи",
      f_sub: "Заполните форму ниже — ваш ответ запишется напрямую без открытия почтовых программ.",
      f_contact: "Ваше имя или контакт для связи (Telegram / ник, необязательно)",
      f_topic: "Категория обращения",
      f_opt_pro: "Вопрос по PRO / Десктоп-версии",
      f_opt_bug: "Сообщить об ошибке / Баг",
      f_opt_idea: "Предложение или идея",
      f_opt_refund: "Вопрос по заказу / Возврату",
      f_msg: "Описание вопроса или проблемы *",
      f_submit: "Отправить ответ",
      f_done_title: "Ответ записан! Спасибо за обращение.",
      f_again: "Отправить ещё один ответ"
    },
    kz: {
      h1: "Барлық бағдарламалардың үстінде тұратын таймер, Помодоро, Flowtime және аналитика.",
      sub: "Браузер кеңейтімі қойындылар ішінде жұмыс істейді, ал Jelly Timer Plus (PRO) сатып алғанда сізге ноутбук пен ДК үшін толық Десктоп PRO-нұсқасы қоса жіберіледі.",
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
      r2: "Барлық пернелерді еркін баптау",
      r3: "Браузерден тыс барлық Windows / macOS терезелерінің үстінде тұру",
      r4: "Помодоро және Flowtime режимдері (1/5 үзіліс)",
      r5: "Жұмыс терезелерін ашқанда авто-қосылу және авто-кідірту",
      r6: "7 күндік статистика + белсенді терезелер трекері",
      cta_h: "Jelly Timer Plus (PRO) — Десктоп PRO-нұсқасы бірге беріледі",
      cta_p: "PRO сатып алғанда сізге Windows және macOS үшін толық Десктоп PRO-нұсқасы жіберіледі.",
      cta_buy_btn: "PRO алу →",
      cta_sup_btn: "Қолдау формасы",
      cta_free_btn: "GitHub Releases",
      f_title: "Қолдау қызметі және кері байланыс формасы",
      f_sub: "Төмендегі форманы толтырыңыз — жауабыңыз поштасыз тікелей тіркеледі.",
      f_contact: "Атыңыз немесе байланыс (Telegram / ник, міндетті емес)",
      f_topic: "Санат",
      f_opt_pro: "PRO / Десктоп нұсқасы бойынша сұрақ",
      f_opt_bug: "Қате туралы хабарлау (Баг)",
      f_opt_idea: "Ұсыныс немесе идея",
      f_opt_refund: "Тапсырыс / Қайтару сұрағы",
      f_msg: "Сұрағыңыз немесе сипаттама *",
      f_submit: "Жауапты жіберу",
      f_done_title: "Жауап жазылды! Рақмет.",
      f_again: "Тағы бір жауап жіберу"
    }
  };

  let curLang = "en";
  function detectLang() {
    const nav = ((navigator && navigator.language) || "en").toLowerCase();
    if (nav.startsWith("kk") || nav.startsWith("kz")) return "kz";
    if (nav.startsWith("ru")) return "ru";
    return "en";
  }

  function applyLang(lang) {
    const c = DICT[lang] ? lang : "en";
    curLang = c;
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

  // Dynamic version resolution: always pick the NEWEST between installed manifest and remote JSON
  const manifestVer = (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.getManifest)
    ? (chrome.runtime.getManifest().version || "1.2.1")
    : "1.2.1";
  let bestVer = manifestVer;
  let bestExp = 7;
  let bestDate = "2026-11-08";
  let webhookUrl = "";

  function parseVerTuple(v) {
    return String(v || "0.0.0").split(".").map((n) => parseInt(n, 10) || 0);
  }

  function isNewerRelease(candVer, candExp, curVer, curExp) {
    const a = parseVerTuple(candVer);
    const b = parseVerTuple(curVer);
    for (let i = 0; i < 3; i++) {
      if ((a[i] || 0) > (b[i] || 0)) return true;
      if ((a[i] || 0) < (b[i] || 0)) return false;
    }
    return (parseInt(candExp, 10) || 0) >= (parseInt(curExp, 10) || 0);
  }

  function renderVersionLabels() {
    const expStr = String(bestExp).padStart(2, "0");
    if (badgeEl) badgeEl.textContent = `v${bestVer} • Exp #${expStr}`;
    if (buildInfoEl) buildInfoEl.textContent = `Package: v${bestVer} • Export #${expStr} (${bestDate})`;
  }

  renderVersionLabels();

  function applyMeta(meta) {
    if (!meta) return;
    const rVer = meta.extension_version || meta.app_version || bestVer;
    const rExp = parseInt(meta.export_build || bestExp, 10);
    if (isNewerRelease(rVer, rExp, bestVer, bestExp)) {
      bestVer = rVer;
      bestExp = rExp;
      bestDate = meta.build_date || bestDate;
    }
    renderVersionLabels();
    if (checkoutBtnEl) {
      checkoutBtnEl.href = meta.pro_checkout_url || meta.pro_landing_url || "https://i2volt.github.io/Jelly_timer/#editions";
    }
    if (meta.support_webhook_url) {
      webhookUrl = meta.support_webhook_url;
    }
  }

  if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
    chrome.storage.local.get(["jellyRemoteMeta", "jellyState"], (res) => {
      if (res && res.jellyState) {
        if (res.jellyState.lang) applyLang(res.jellyState.lang);
        if (res.jellyState.exportBuild && res.jellyState.exportBuild > bestExp) {
          bestExp = res.jellyState.exportBuild;
          renderVersionLabels();
        }
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
        const expStr = String(bestExp).padStart(2, "0");
        if (syncStatusEl) {
          syncStatusEl.textContent = `Latest release: v${bestVer} (Exp #${expStr})`;
        }
        if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
          chrome.storage.local.set({ jellyRemoteMeta: data });
        }
      }
    })
    .catch(() => {});

  // Classic Embedded Support Form Handler (No Email Client)
  const formEl = document.getElementById("proSupportForm");
  const formWrapEl = document.getElementById("proSupportFormWrap");
  const doneEl = document.getElementById("proSupportDone");
  const ticketMetaEl = document.getElementById("proTicketMeta");
  const resetBtnEl = document.getElementById("proResetFormBtn");

  if (formEl) {
    formEl.addEventListener("submit", (e) => {
      e.preventDefault();
      const contact = (document.getElementById("pfContact").value || "").trim();
      const topic = document.getElementById("pfTopic").value;
      const msg = (document.getElementById("pfMsg").value || "").trim();
      if (!msg) return;

      const ticketId = "JT-" + Math.floor(1000 + Math.random() * 9000);
      const entry = {
        ticketId,
        contact: contact || "Anonymous",
        topic,
        message: msg,
        version: `v${bestVer} (Exp #${String(bestExp).padStart(2, "0")})`,
        timestamp: new Date().toISOString()
      };

      if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
        chrome.storage.local.get(["jellySupportTickets"], (res) => {
          const list = Array.isArray(res.jellySupportTickets) ? res.jellySupportTickets : [];
          list.push(entry);
          chrome.storage.local.set({ jellySupportTickets: list });
        });
      }

      if (webhookUrl) {
        fetch(webhookUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(entry)
        }).catch(() => {});
      }

      if (ticketMetaEl) {
        ticketMetaEl.textContent = curLang === "ru"
          ? `Номер обращения: #${ticketId} • Версия: v${bestVer}`
          : (curLang === "kz" ? `Өтініш нөмірі: #${ticketId} • v${bestVer}` : `Ticket ID: #${ticketId} • Version: v${bestVer}`);
      }
      if (formWrapEl) formWrapEl.style.display = "none";
      if (doneEl) doneEl.classList.add("active");
      formEl.reset();
    });
  }

  if (resetBtnEl) {
    resetBtnEl.addEventListener("click", () => {
      if (doneEl) doneEl.classList.remove("active");
      if (formWrapEl) formWrapEl.style.display = "block";
    });
  }
})();
