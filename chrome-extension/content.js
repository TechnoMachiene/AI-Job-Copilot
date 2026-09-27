chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "extractPageText") {
        // Grabbing all inner text bypasses HTML formatting and gets pure content for the LLM
        sendResponse({ text: document.body.innerText });
    }
});