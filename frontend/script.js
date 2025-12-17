const API_URL = "http://127.0.0.1:8000/analyze";

document.getElementById("generateBtn").addEventListener("click", generateWorkflow);

async function generateWorkflow() {
    const promptInput = document.getElementById("prompt");
    const summaryEl = document.getElementById("summary");
    const categorizeEl = document.getElementById("prompt-categorize");

    const prompt = promptInput.value.trim();

    if (!prompt) {
        alert("Please enter a workflow prompt.");
        return;
    }

    summaryEl.textContent = "Processing...";
    categorizeEl.textContent = "Processing...";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ prompt })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Backend error");
        }

        const data = await response.json();

        summaryEl.textContent = JSON.stringify(data, null, 2);
        categorizeEl.textContent = JSON.stringify(
            data.techniques || [],
            null,
            2
        );

    } catch (error) {
        summaryEl.textContent = "Error occurred.";
        categorizeEl.textContent = "-";
        alert(error.message);
    }
}
