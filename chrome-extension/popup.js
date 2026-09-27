const SERVER_URL = "http://127.0.0.1:8000";

document.getElementById('generateBtn').addEventListener('click', async () => {
    const statusEl = document.getElementById('status');
    statusEl.innerText = "Extracting job details...";

    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
    }, () => {
        chrome.tabs.sendMessage(tab.id, { action: "extractPageText" }, async (response) => {
            if (!response || !response.text) {
                statusEl.innerText = "Error: Could not read page text.";
                return;
            }

            statusEl.innerText = "Sending to local AI Agent...";

            try {
                const apiRes = await fetch(`${SERVER_URL}/api/tailor-resume`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        url: tab.url,
                        description: response.text
                    })
                });

                const data = await apiRes.json();
                if (apiRes.ok && data.filename) {
                    // Clean absolute target URL
                    const targetUrl = `${SERVER_URL}/outputs/${data.filename}`;

                    statusEl.innerHTML = `
                        <p style="color: green; margin-bottom: 8px;"><strong>Resume Ready!</strong></p>
                        <button id="openPdfBtn" style="background: #16a34a; width: 100%; padding: 8px; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
                            View Resume
                        </button>
                    `;

                    const openTab = () => {
                        chrome.tabs.create({ url: targetUrl, active: true });
                    };

                    document.getElementById('openPdfBtn').addEventListener('click', openTab);
                    
                    // Auto-open in new tab
                    openTab();
                } else {
                    statusEl.innerText = "API Error: " + (data.detail || "Generation failed");
                }
            } catch (err) {
                statusEl.innerText = "Connection failed. Is Uvicorn running on port 8000?";
            }
        });
    });
});