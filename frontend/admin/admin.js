const API_BASE = `${window.location.origin}/api/admin`;

let adminApiKey = "";

const loginSection = document.getElementById("login-section");
const dashboardSection = document.getElementById("dashboard-section");

const loginForm = document.getElementById("login-form");
const loginError = document.getElementById("login-error");

const uploadForm = document.getElementById("upload-form");
const uploadButton = document.getElementById("upload-button");
const uploadMessage = document.getElementById("upload-message");

const documentList = document.getElementById("document-list");
const notification = document.getElementById("notification");

// Source library

const sourceList = document.getElementById("source-list");


async function apiRequest(endpoint, options = {}) {
    const headers = new Headers(options.headers || {});

    headers.set("Authorization", `Bearer ${adminApiKey}`);

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    const data = await response.json().catch(() => ({}));

    if (response.status === 401) {
        disconnectAdmin();
        throw new Error("Your admin session is no longer authorized.");
    }

    if (!response.ok) {
        throw new Error(data.detail || "The request failed.");
    }

    return data;
}


function showNotification(message) {
    notification.textContent = message;
    notification.classList.add("show");

    setTimeout(() => {
        notification.classList.remove("show");
    }, 3000);
}


function setConnectionStatus(connected) {
    const indicator = document.getElementById("connection-indicator");
    const text = document.getElementById("connection-text");

    indicator.classList.toggle("connected", connected);
    text.textContent = connected ? "Connected" : "Not connected";
}


function disconnectAdmin() {
    adminApiKey = null;

    loginSection.hidden = false;
    dashboardSection.hidden = true;

    document.getElementById("api-key").value = "";
    loginError.textContent = "";

    setConnectionStatus(false);
}


async function connectAdmin(apiKey) {
    adminApiKey = apiKey;

    try {
        await loadDashboard();

        loginSection.hidden = true;
        dashboardSection.hidden = false;

        setConnectionStatus(true);
        showNotification("Connected successfully.");

    } catch (error) {
        adminApiKey = null;
        loginError.textContent = error.message;
        setConnectionStatus(false);
    }
}


// Authentication

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const apiKey = document.getElementById("api-key").value.trim();

    if (!apiKey) {
        loginError.textContent = "Please enter your API key.";
        return;
    }

    loginError.textContent = "Connecting...";

    await connectAdmin(apiKey);
});


// Dashboard statistics

async function loadDashboard() {
    const data = await apiRequest("/dashboard");
    const stats = data.statistics;

    document.getElementById("total-documents").textContent =
        stats.total_documents ?? 0;

    document.getElementById("total-chunks").textContent =
        stats.total_chunks ?? 0;

    document.getElementById("indexed-documents").textContent =
        stats.indexed_documents ?? 0;

    document.getElementById("api-status").textContent =
        "Online";

    await loadDocuments();
    await loadSources();
}


// Source listing and deletion

async function loadSources() {
    const data = await apiRequest("/sources");
    const sources = data.sources || [];

    sourceList.replaceChildren();

    document.getElementById("source-count").textContent =
        `${sources.length} source${sources.length === 1 ? "" : "s"}`;

    if (sources.length === 0) {
        const empty = document.createElement("p");
        empty.className = "empty-state";
        empty.textContent = "No indexed sources found.";
        sourceList.appendChild(empty);
        return;
    }

    sources.forEach((source) => {
        const item = document.createElement("article");
        item.className = "document-item";

        const info = document.createElement("div");
        info.className = "document-info";

        const name = document.createElement("strong");
        name.textContent = source.source_url;

        const details = document.createElement("span");
        details.textContent = "Indexed website or PDF source";

        info.append(name, details);

        const deleteButton = document.createElement("button");
        deleteButton.className = "delete-button";
        deleteButton.textContent = "Delete";

        deleteButton.addEventListener("click", () => {
            deleteSource(source.source_url);
        });

        item.append(info, deleteButton);
        sourceList.appendChild(item);
    });
}

async function deleteSource(sourceUrl) {
    const confirmed = confirm(
        `Delete this source and all of its indexed chunks?\n\n${sourceUrl}`
    );

    if (!confirmed) return;

    try {
        await apiRequest(
            `/sources?source_url=${encodeURIComponent(sourceUrl)}`,
            { method: "DELETE" }
        );

        showNotification("Source deleted.");
        await loadDashboard();

    } catch (error) {
        showNotification(error.message);
    }
}


// Document library

async function loadDocuments() {
    const data = await apiRequest("/documents");

    const documents = data.documents || [];

    documentList.replaceChildren();

    document.getElementById("document-count").textContent =
        `${documents.length} document${documents.length === 1 ? "" : "s"}`;

    if (documents.length === 0) {
        const empty = document.createElement("p");
        empty.className = "empty-state";
        empty.textContent = "No documents have been uploaded yet.";

        documentList.appendChild(empty);
        return;
    }

    documents.forEach((document) => {
        const item = document.createElement("article");
        item.className = "document-item";

        const info = document.createElement("div");
        info.className = "document-info";

        const name = document.createElement("strong");
        name.textContent = document.filename || "Unnamed document";

        const details = document.createElement("span");

        const fileType = document.file_type || "Unknown type";
        const chunks = document.chunks ?? 0;
        const uploaded = document.uploaded_at
            ? new Date(document.uploaded_at).toLocaleString()
            : "Unknown date";

        details.textContent =
            `${fileType} · ${chunks} chunks · ${uploaded}`;

        info.append(name, details);

        const deleteButton = document.createElement("button");
        deleteButton.className = "delete-button";
        deleteButton.textContent = "Delete";

        deleteButton.addEventListener("click", () => {
            deleteDocument(document.document_id, document.filename);
        });

        item.append(info, deleteButton);
        documentList.appendChild(item);
    });
}


async function deleteDocument(documentId, filename) {
    const confirmed = confirm(
        `Delete "${filename}"?\n\nThis removes the document and its indexed chunks.`
    );

    if (!confirmed) return;

    try {
        await apiRequest(
            `/documents/${encodeURIComponent(documentId)}`,
            { method: "DELETE" }
        );

        showNotification("Document deleted.");

        await loadDashboard();

    } catch (error) {
        showNotification(error.message);
    }
}


// Document upload

uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const fileInput = document.getElementById("document-file");
    const file = fileInput.files[0];

    if (!file) {
        uploadMessage.textContent = "Select a document first.";
        return;
    }

    const allowedExtensions = [".pdf", ".txt", ".docx"];

    const extension = file.name
        .slice(file.name.lastIndexOf("."))
        .toLowerCase();

    if (!allowedExtensions.includes(extension)) {
        uploadMessage.textContent = "Unsupported file format.";
        return;
    }

    if (file.size > 15 * 1024 * 1024) {
        uploadMessage.textContent = "File must be 15 MB or smaller.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    uploadButton.disabled = true;
    uploadButton.textContent = "Uploading...";
    uploadMessage.textContent = "Processing document...";

    try {
        const result = await apiRequest("/documents/upload", {
            method: "POST",
            body: formData
        });

        uploadMessage.textContent = result.message;

        uploadForm.reset();

        showNotification("Document uploaded successfully.");

        await loadDashboard();

    } catch (error) {
        uploadMessage.textContent = error.message;
    } finally {
        uploadButton.disabled = false;
        uploadButton.textContent = "Upload document";
    }
});


// Refresh dashboard

document.getElementById("refresh-button").addEventListener(
    "click",
    async () => {
        try {
            await loadDashboard();
            showNotification("Dashboard refreshed.");
        } catch (error) {
            showNotification(error.message);
        }
    }
);


// Disconnect

document.getElementById("logout-button").addEventListener(
    "click",
    disconnectAdmin
);
