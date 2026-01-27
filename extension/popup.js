const API_BASE = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
  const scanBtn = document.getElementById("scanBtn");
  const clearBtn = document.getElementById("clearBtn");

  const verdictEl = document.getElementById("verdict");
  const scoreEl = document.getElementById("riskScore");
  const reasonsEl = document.getElementById("reasons");
  const historyList = document.getElementById("historyList");

  function badgeClass(verdict) {
    if (!verdict) return "badge unknown";
    const v = verdict.toLowerCase();
    if (v === "safe") return "badge safe";
    if (v === "suspicious") return "badge suspicious";
    if (v === "phishing") return "badge phishing";
    return "badge unknown";
  }

  function setResultUI(verdict, score, reasons) {
    verdictEl.textContent = verdict ?? "Unknown";
    scoreEl.textContent = `${score ?? 0}/100`;

    if (Array.isArray(reasons)) {
      reasonsEl.textContent = reasons.length ? reasons.join(", ") : "No reasons returned.";
    } else {
      reasonsEl.textContent = reasons ?? "No reasons returned.";
    }
  }

  async function loadHistory() {
    try {
      const res = await fetch(`${API_BASE}/history`);
      const data = await res.json();

      historyList.innerHTML = "";

      if (!Array.isArray(data) || data.length === 0) {
        historyList.innerHTML = `<div class="history-empty">No scans yet.</div>`;
        return;
      }

      data.slice(0, 10).forEach((item) => {
        const url = item.url ?? "Unknown URL";
        const verdict = item.result?.verdict ?? "Unknown";
        const mode = item.used_ai ? "AI" : "Manual";

        const row = document.createElement("div");
        row.className = "history-item";

        row.innerHTML = `
          <div class="history-url" title="${url}">${url}</div>
          <div class="history-right">
            <span class="mini-tag">${mode}</span>
            <span class="${badgeClass(verdict)}">${verdict}</span>
          </div>
        `;

        historyList.appendChild(row);
      });
    } catch (err) {
      console.error("History load failed:", err);
      historyList.innerHTML = `<div class="history-empty">Backend not reachable</div>`;
    }
  }

  async function scanCurrentTab() {
    try {
      scanBtn.disabled = true;
      scanBtn.textContent = "SCANNING...";

      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const currentUrl = tab?.url;

      if (!currentUrl) {
        setResultUI("Unknown", 0, ["Could not read current tab URL"]);
        return;
      }

      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: currentUrl })
      });

      const data = await res.json();

      // IMPORTANT: Always show final result (AI if available, manual only if AI failed)
      const verdict = data?.result?.verdict;
      const riskScore = data?.result?.risk_score;
      const reasons = data?.result?.reasons;

      setResultUI(verdict, riskScore, reasons);
      await loadHistory();
    } catch (err) {
      console.error("Scan failed:", err);
      setResultUI("Error", 0, ["Backend not reachable. Start backend: python main.py"]);
    } finally {
      scanBtn.disabled = false;
      scanBtn.textContent = "SCAN CURRENT SITE";
    }
  }

  async function clearHistory() {
    try {
      clearBtn.disabled = true;
      clearBtn.textContent = "CLEARING...";

      await fetch(`${API_BASE}/history`, { method: "DELETE" });

      setResultUI("---", 0, "---");
      await loadHistory();
    } catch (err) {
      console.error("Clear history failed:", err);
    } finally {
      clearBtn.disabled = false;
      clearBtn.textContent = "CLEAR HISTORY";
    }
  }

  scanBtn.addEventListener("click", scanCurrentTab);
  clearBtn.addEventListener("click", clearHistory);

  loadHistory();
});
