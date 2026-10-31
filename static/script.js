const promptInput = document.getElementById("prompt");
const languageSelect = document.getElementById("language");
const resultElement = document.getElementById("result");
const statusElement = document.getElementById("status");
const buttons = document.querySelectorAll("[data-action]");

buttons.forEach((button) => {
button.addEventListener("click", async () => {
const prompt = promptInput.value.trim();
const language = languageSelect.value;
const action = button.dataset.action;

    if (!prompt) {
        statusElement.textContent = "Please enter a coding request.";
        promptInput.focus();
        return;
    }

    buttons.forEach((item) => {
        item.disabled = true;
    });

    statusElement.textContent = "AI is processing your request...";
    resultElement.textContent = "";

    try {
        const response = await fetch("/test", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                prompt: prompt,
                language: language,
                action: action
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Something went wrong.");
        }

        resultElement.textContent = data.result;
        statusElement.textContent = "Response generated successfully!";
    } catch (error) {
        statusElement.textContent = "Request failed: " + error.message;
    } finally {
        buttons.forEach((item) => {
            item.disabled = false;
        });
    }
});


});
