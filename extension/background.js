const BACKEND_URL = "https://phishguard-backend-upyk.onrender.com/analyze";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "ANALYZE_URL") {
    fetch(BACKEND_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url: message.url })
    })
      .then(res => res.json())
      .then(data => {
        sendResponse({ success: true, data });
      })
      .catch(err => {
        sendResponse({
          success: false,
          error: err.toString()
        });
      });

    // 🔴 REQUIRED: async response
    return true;
  }
});
