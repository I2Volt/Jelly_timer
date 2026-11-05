(() => {
  const REMOTE_VERSION_URL = "https://raw.githubusercontent.com/I2Volt/Jelly_timer/main/version_info.json";
  const linkEl = document.getElementById("proExternalLink");
  const badgeEl = document.getElementById("versionBadge");
  const buildInfoEl = document.getElementById("buildInfoText");
  const syncStatusEl = document.getElementById("syncStatusText");

  function applyMeta(meta) {
    if (!meta) return;
    const ver = meta.app_version || "1.2.0";
    const exp = String(meta.export_build || 1).padStart(2, "0");
    const dt = meta.build_date || "2026-11-04";
    if (badgeEl) badgeEl.textContent = `✨ Jelly Timer Plus (PRO) • v${ver}`;
    if (buildInfoEl) buildInfoEl.textContent = `Версия пакета: v${ver} • Export #${exp} (${dt})`;
    if (linkEl && meta.pro_landing_url) {
      linkEl.href = meta.pro_landing_url;
    }
  }

  if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
    chrome.storage.local.get(["jellyRemoteMeta"], (res) => {
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
          syncStatusEl.textContent = `Актуальная версия на сервере: v${data.app_version} (Exp #${String(data.export_build || 1).padStart(2, "0")})`;
        }
        if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
          chrome.storage.local.set({ jellyRemoteMeta: data });
        }
      }
    })
    .catch(() => {});
})();
