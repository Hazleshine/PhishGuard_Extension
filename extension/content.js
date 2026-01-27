// ===============================
// PhishGuard AI - content.js
// Gmail-safe banner injection
// NO direct backend fetch (background.js handles it)
// ===============================

let lastUrl = location.href;

// -------------------------------
// Create & inject banner
// -------------------------------
function injectBanner(verdict) {
  // Avoid duplicate banners
  const existing = document.getElementById("phishguard-banner");
  if (existing) existing.remove();

  const banner = document.createElement("div");
  banner.id = "phishguard-banner";

  banner.style.position = "fixed";
  banner.style.top = "0";
  banner.style.left = "0";
  banner.style.width = "100%";
  banner.style.zIndex = "2147483647";
  banner.style.padding = "10px";
  banner.style.fontSize = "14px";
  banner.style.fontWeight = "bold";
  banner.style.textAlign = "center";
  banner.style.fontFamily = "Arial, sans-serif";
  banner.style.color = "#ffffff";

  if (verdict === "Safe") {
    banner.style.backgroundColor = "#16a34a";
    banner.innerText = "✅ PhishGuard AI: This page appears SAFE";
  } else if (verdict === "Suspicious") {
    banner.style.backgroundColor = "#f59e0b";
    banner.innerText = "⚠️ PhishGuard AI: This page looks SUSPICIOUS";
  } else if (verdict === "Phishing") {
    banner.style.backgroundColor = "#dc2626";
    banner.innerText = "🚨 PhishGuard AI: PHISHING RISK DETECTED";
  } else {
    banner.style.backgroundColor = "#6b7280";
    banner.innerText = "ℹ️ PhishGuard AI: Unable to determine risk";
  }

  // 🔥 CRITICAL: attach to documentElement (works on Gmail)
  document.documentElement.appendChild(banner);
}

// -------------------------------
// Ask background.js to analyze URL
// -------------------------------
function analyzePage() {
  chrome.runtime.sendMessage(
    {
      type: "ANALYZE_URL",
      url: location.href
    },
    (response) => {
      if (!response) {
        console.error("PhishGuard: No response from background script");
        return;
      }

      if (!response.success) {
        console.error("PhishGuard background error:", response.error);
        return;
      }

      const verdict = response?.data?.result?.verdict;
      if (verdict) {
        injectBanner(verdict);
      }
    }
  );
}

// -------------------------------
// Gmail SPA URL change watcher
// -------------------------------
const observer = new MutationObserver(() => {
  if (location.href !== lastUrl) {
    lastUrl = location.href;

    const oldBanner = document.getElementById("phishguard-banner");
    if (oldBanner) oldBanner.remove();

    // Wait for Gmail DOM to stabilize
    setTimeout(analyzePage, 1500);
  }
});

// Start observing Gmail DOM
observer.observe(document, {
  childList: true,
  subtree: true
});

// Initial scan (after page load)
setTimeout(analyzePage, 2000);
