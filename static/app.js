async function deploy() {
    const repo = document.getElementById("repo").value;
    const name = document.getElementById("name").value;
    const logs = document.getElementById("logs");
    const successPanel = document.getElementById("successPanel");
    const liveUrl = document.getElementById("liveUrl");
    const statusBadge = document.getElementById("statusBadge");

    const btn = document.getElementById("deployBtn");
    const btnText = document.getElementById("btnText");
    const btnIcon = document.getElementById("btnIcon");

    logs.innerText = "";
    successPanel.classList.add("hidden");

    // 🔵 Button state
    btn.disabled = true;
    btn.classList.add("deploying");
    btnIcon.className = "fa-solid fa-spinner fa-spin";
    btnText.innerText = "Deploying";

    // 🔵 Badge state
    statusBadge.innerText = "Deploying";
    statusBadge.className = "badge deploying";

    const response = await fetch("/deploy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ github_url: repo, project_name: name })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let finalUrl = "";

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        logs.innerText += chunk;
        logs.scrollTop = logs.scrollHeight;

        if (chunk.includes("Building Docker")) {
            statusBadge.innerText = "Building";
        }

        if (chunk.includes("Deploying to Kubernetes")) {
            statusBadge.innerText = "Deploying";
        }

        if (chunk.includes("URL:")) {
            finalUrl = chunk.split("URL:")[1].trim();
        }
    }

    // 🔵 Reset button
    btn.disabled = false;
    btn.classList.remove("deploying");
    btnIcon.className = "fa-solid fa-rocket";
    btnText.innerText = "Deploy";

    if (finalUrl) {
        statusBadge.innerText = "Live";
        statusBadge.className = "badge success";

        liveUrl.innerText = finalUrl;
        liveUrl.href = finalUrl;
        successPanel.classList.remove("hidden");
    }
}

function copyUrl() {
    const text = document.getElementById("liveUrl").innerText;
    const copyText = document.getElementById("copyText");
    const copyBtn = document.getElementById("copyBtn");

    if (!text) return;

    navigator.clipboard.writeText(text).then(() => {
        copyText.innerText = "Copied!";
        copyBtn.classList.add("copied");

        setTimeout(() => {
            copyText.innerText = "Copy";
            copyBtn.classList.remove("copied");
        }, 1500);
    });
}

function fallbackCopy(text) {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
    showCopySuccess();
}

function showCopySuccess() {
    const btn = document.querySelector(".result-url button");
    btn.innerText = "Copied!";
    setTimeout(() => {
        btn.innerText = "Copy";
    }, 1500);
}