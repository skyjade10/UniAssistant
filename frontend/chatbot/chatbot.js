const API_URL = `http://127.0.0.1:8765/api/chat/stream`;

if (window.lucide) {
    window.lucide.createIcons();
}

const chatClear = document.getElementById("chat-clear");

// ==========================================
// ZUT AI - PARTICLE BACKGROUND CONFIGURATION
// ==========================================


const PARTICLE_CONFIG = {
    brightness: 10,
    size: 10,
    connections: 10,
    density: 10,

    colors: [
        "0, 217, 255",   // Cyan
        "0, 191, 166",   // Turquoise
        "102, 217, 200"  // Soft teal
    ],

    mouseRadius: 145,
    movementSpeed: 0.45,
    mouseRepulsion: 1.8
};

// ==========================================
// PARTICLE SCALE VALUES
// ==========================================


const PARTICLE_SCALES = {
    brightness: [
        0.15, 0.25, 0.35, 0.45, 0.55,
        0.65, 0.75, 0.85, 0.95, 1.0
    ],

    size: [
        [0.8, 1.5],
        [1.0, 1.8],
        [1.2, 2.2],
        [1.5, 2.8],
        [1.8, 3.2],
        [2.0, 3.8],
        [2.3, 4.2],
        [2.6, 4.8],
        [3.0, 5.5],
        [3.5, 6.5]
    ],

    connections: [
        { opacity: 0.08, distance: 80, width: 0.5 },
        { opacity: 0.12, distance: 90, width: 0.6 },
        { opacity: 0.16, distance: 100, width: 0.7 },
        { opacity: 0.20, distance: 110, width: 0.8 },
        { opacity: 0.25, distance: 120, width: 0.9 },
        { opacity: 0.30, distance: 130, width: 1.0 },
        { opacity: 0.35, distance: 140, width: 1.1 },
        { opacity: 0.40, distance: 150, width: 1.2 },
        { opacity: 0.45, distance: 165, width: 1.3 },
        { opacity: 0.50, distance: 180, width: 1.5 }
    ],

    density: [
        { divisor: 25000, max: 70 },
        { divisor: 20000, max: 100 },
        { divisor: 16000, max: 130 },
        { divisor: 13000, max: 160 },
        { divisor: 11000, max: 190 },
        { divisor: 9000, max: 220 },
        { divisor: 8000, max: 250 },
        { divisor: 7000, max: 280 },
        { divisor: 6000, max: 320 },
        { divisor: 5000, max: 350 }
    ]
};


// ==========================================
// PARTICLE BACKGROUND
// ==========================================

const canvas = document.getElementById("particle-canvas");
const ctx = canvas ? canvas.getContext("2d") : null;

const reducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
).matches;

let width = 0;
let height = 0;
let particles = [];
let animationFrame = null;

const mouse = {
    x: null,
    y: null,
    radius: PARTICLE_CONFIG.mouseRadius
};

// Get the selected scale value
function getScale(category) {
    const value = PARTICLE_CONFIG[category];

    if (!Number.isInteger(value) || value < 1 || value > 10) {
        throw new Error(
            `Invalid particle ${category} value. Use a value between 1 and 10.`
        );
    }

    return value - 1;
}

// ==========================================
// RESIZE CANVAS
// ==========================================

function resizeCanvas() {
    if (!canvas || !ctx) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);

    width = window.innerWidth;
    height = window.innerHeight;

    canvas.width = width * dpr;
    canvas.height = height * dpr;

    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    createParticles();
}

// ==========================================
// CREATE PARTICLES
// ==========================================

function createParticles() {
    if (!canvas || !ctx) return;

    const density =
        PARTICLE_SCALES.density[getScale("density")];

    const count = Math.min(
        density.max,
        Math.max(40, Math.floor((width * height) / density.divisor))
    );

    const [minRadius, maxRadius] =
        PARTICLE_SCALES.size[getScale("size")];

    const brightness =
        PARTICLE_SCALES.brightness[getScale("brightness")];

    particles = [];

    for (let i = 0; i < count; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,

            vx: (Math.random() - 0.5) * PARTICLE_CONFIG.movementSpeed,
            vy: (Math.random() - 0.5) * PARTICLE_CONFIG.movementSpeed,

            radius:
                minRadius + Math.random() * (maxRadius - minRadius),

            opacity:
                brightness * (0.65 + Math.random() * 0.35),

            color:
                PARTICLE_CONFIG.colors[
                    Math.floor(Math.random() * PARTICLE_CONFIG.colors.length)
                ]
        });
    }
}

// ==========================================
// DRAW PARTICLES
// ==========================================

function drawParticles() {
    if (!canvas || !ctx) return;

    ctx.clearRect(0, 0, width, height);

    const connection =
        PARTICLE_SCALES.connections[getScale("connections")];

    const connectionDistance = connection.distance;

    // Draw and move particles
    particles.forEach(particle => {
        particle.x += particle.vx;
        particle.y += particle.vy;

        // Bounce off screen edges
        if (particle.x < 0 || particle.x > width) {
            particle.vx *= -1;
        }

        if (particle.y < 0 || particle.y > height) {
            particle.vy *= -1;
        }

        // Mouse interaction: repel particles
        if (mouse.x !== null && mouse.y !== null) {
            const dx = particle.x - mouse.x;
            const dy = particle.y - mouse.y;

            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < mouse.radius && distance > 0) {
                const force =
                    (mouse.radius - distance) / mouse.radius;

                particle.x +=
                    (dx / distance) *
                    force *
                    PARTICLE_CONFIG.mouseRepulsion;

                particle.y +=
                    (dy / distance) *
                    force *
                    PARTICLE_CONFIG.mouseRepulsion;
            }
        }

        // Draw particle
        ctx.beginPath();

        ctx.arc(
            particle.x,
            particle.y,
            particle.radius,
            0,
            Math.PI * 2
        );

        ctx.fillStyle =
            `rgba(${particle.color}, ${particle.opacity})`;

        ctx.fill();
    });

    // ======================================
    // CONNECT PARTICLES TO EACH OTHER
    // ======================================

    for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
            const p1 = particles[i];
            const p2 = particles[j];

            const dx = p1.x - p2.x;
            const dy = p1.y - p2.y;

            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < connectionDistance) {
                const opacity =
                    1 - distance / connectionDistance;

                ctx.beginPath();

                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);

                ctx.strokeStyle =
                    `rgba(0, 217, 255, ${opacity * connection.opacity})`;

                ctx.lineWidth = connection.width;

                ctx.stroke();
            }
        }
    }

    // ======================================
    // CONNECT PARTICLES TO MOUSE
    // ======================================

    if (mouse.x !== null && mouse.y !== null) {
        particles.forEach(particle => {
            const dx = particle.x - mouse.x;
            const dy = particle.y - mouse.y;

            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < mouse.radius) {
                const opacity =
                    1 - distance / mouse.radius;

                ctx.beginPath();

                ctx.moveTo(particle.x, particle.y);
                ctx.lineTo(mouse.x, mouse.y);

                ctx.strokeStyle =
                    `rgba(0, 217, 255, ${opacity * 0.45})`;

                ctx.lineWidth = 1;

                ctx.stroke();
            }
        });
    }
}

// ==========================================
// ANIMATION LOOP
// ==========================================

function animateParticles() {
    drawParticles();

    if (!reducedMotion) {
        animationFrame = requestAnimationFrame(animateParticles);
    }
}

// ==========================================
// MOUSE AND TOUCH INTERACTION
// ==========================================

window.addEventListener("pointermove", event => {
    mouse.x = event.clientX;
    mouse.y = event.clientY;
}, { passive: true });

window.addEventListener("pointerout", event => {
    if (!event.relatedTarget) {
        mouse.x = null;
        mouse.y = null;
    }
}, { passive: true });

window.addEventListener("pointerdown", event => {
    if (event.pointerType === "touch") {
        mouse.x = event.clientX;
        mouse.y = event.clientY;
    }
}, { passive: true });

window.addEventListener("pointerup", event => {
    if (event.pointerType === "touch") {
        mouse.x = null;
        mouse.y = null;
    }
}, { passive: true });

window.addEventListener("resize", resizeCanvas);

// Start particle background
if (canvas && ctx) {
    resizeCanvas();
    animateParticles();
}

//======================================
// CHAT HISTORY MANAGEMENT
//======================================

const CHAT_HISTORY_KEY = "uniassist_chat_history";
const MAX_HISTORY_MESSAGES = 100;

function saveChatHistory() {
    const messages = [...chatMessages.querySelectorAll(".message")];

    const history = messages
        .map(message => ({
            sender: message.classList.contains("user")
                ? "user"
                : "assistant",
            content: message.dataset.rawText || ""
        }))
        .filter(message => message.content.trim() !== "")
        .slice(-MAX_HISTORY_MESSAGES);

    try {
        localStorage.setItem(
            CHAT_HISTORY_KEY,
            JSON.stringify(history)
        );
    } catch (error) {
        console.warn("Could not save chat history:", error);
    }
}

function restoreChatHistory() {
    try {
        const saved = localStorage.getItem(CHAT_HISTORY_KEY);

        if (!saved) return;

        const history = JSON.parse(saved);

        if (!Array.isArray(history)) return;

        chatMessages.innerHTML = "";

        history.forEach(message => {
            if (
                typeof message.content === "string" &&
                ["user", "assistant"].includes(message.sender)
            ) {
                renderSavedMessage(message.content, message.sender);
            }
        });

        chatMessages.scrollTop = chatMessages.scrollHeight;

    } catch (error) {
        console.warn("Could not restore chat history:", error);
        localStorage.removeItem(CHAT_HISTORY_KEY);
    }
}

function renderSavedMessage(content, sender) {
    const message = document.createElement("div");

    message.className = `message ${sender}`;
    message.dataset.rawText = content;

    if (sender === "assistant") {
        message.innerHTML = formatAssistantMessage(content);
    } else {
        message.textContent = content;
    }

    chatMessages.appendChild(message);
}


// ==========================================
// ZUT AI CHAT FUNCTIONALITY
// ==========================================


const chatToggle = document.getElementById("chat-toggle");
const chatWidget = document.getElementById("chat-widget");
const chatClose = document.getElementById("chat-close");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatMessages = document.getElementById("chat-messages");
const heroChatButton = document.getElementById("hero-chat-button");

// ==========================================
// OPEN CHAT
// ==========================================

function openChat() {
    if (!chatWidget) return;

    chatWidget.hidden = false;

    if (chatToggle) {
        chatToggle.setAttribute("aria-expanded", "true");
    }

    if (chatInput) {
        chatInput.focus();
    }
}

// ==========================================
// CLOSE CHAT
// ==========================================

function closeChat() {
    if (!chatWidget) return;

    chatWidget.hidden = true;

    if (chatToggle) {
        chatToggle.setAttribute("aria-expanded", "false");
        chatToggle.focus();
    }
}

// ==========================================
// CHAT EVENT LISTENERS
// ==========================================

chatToggle?.addEventListener("click", openChat);

chatClose?.addEventListener("click", closeChat);

heroChatButton?.addEventListener("click", openChat);

document.addEventListener("keydown", event => {
    if (event.key === "Escape" && chatWidget && !chatWidget.hidden) {
        closeChat();
    }
});

 // ==========================================
 // MARKDOWN CONFIGURATION
 // ==========================================

marked.setOptions({
    gfm: true,
    breaks: true
});

function formatAssistantMessage(text) {
    const html = marked.parse(text || "");

    return DOMPurify.sanitize(html);
}

// ==========================================
// DISPLAY CHAT MESSAGES
// ==========================================


function addMessage(message, sender, persist = true) {
    const messageElement = document.createElement("div");

    messageElement.className = `message ${sender}`;
    messageElement.dataset.rawText = message;

    if (sender === "assistant") {
        messageElement.innerHTML = formatAssistantMessage(message);
    } else {
        messageElement.textContent = message;
    }

    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    if (persist) {
        saveChatHistory();
    }

    return messageElement;
}


// ==========================================
// SEND QUESTION TO BACKEND
// ==========================================

async function sendMessage(question) {
    try {
        const response = await fetch(API_URL, {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(
                data.detail || "Unable to process your question."
            );
        }

        if (!data.answer) {
            throw new Error("The assistant returned an empty response.");
        }

        // Display only the answer.
        // Sources remain available to the backend.
        addMessage(data.answer, "assistant");

    } catch (error) {
        console.error("Chat error:", error);

        addMessage(
            "Sorry, I couldn't process your question right now. Please try again.",
            "assistant"
        );
    }
}

// ==========================================
// CHAT FORM SUBMISSION
// ==========================================

chatForm?.addEventListener("submit", async event => {
    event.preventDefault();

    const question = chatInput?.value.trim();

    if (!question) return;

    // Display user's question
    addMessage(question, "user");

    chatInput.value = "";

    // Temporary loading message
    const loadingMessage = addMessage(
        "One moment, please...",
        "assistant"
    );

    if (chatInput) {
        chatInput.disabled = true;
    }

    const submitButton = chatForm.querySelector(
        'button[type="submit"]'
    );

    if (submitButton) {
        submitButton.disabled = true;
    }

    try {
        // Remove loading message before displaying the response
        await sendMessageWithLoading(question, loadingMessage);
    } finally {
        if (chatInput) {
            chatInput.disabled = false;
            chatInput.focus();
        }

        if (submitButton) {
            submitButton.disabled = false;
        }
    }
});


 // ==========================================
 // SEND MESSAGE WITH LOADING INDICATOR
 // ==========================================

async function sendMessageWithLoading(question, loadingMessage) {

    let assistantMessage = null;

    try {

        const response = await fetch(API_URL, {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({ question })
        });

        if (!response.ok) {
            throw new Error(getFriendlyError(response));
        }

        if (!response.body) {
            throw new Error(
                "Streaming is not supported by this browser."
            );
        }

        loadingMessage?.remove();

        assistantMessage = addMessage("", "assistant");

        assistantMessage.classList.add("is-streaming");

        assistantMessage.dataset.rawText = "";

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {

            const { done, value } = await reader.read();

            if (done) break;

            const chunk = decoder.decode(value, {
                stream: true
            });

            assistantMessage.dataset.rawText += chunk;

            assistantMessage.innerHTML = formatAssistantMessage(
                assistantMessage.dataset.rawText
            );

            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        // Process any remaining decoder content.
        const trailingText = decoder.decode();

        if (trailingText) {

            assistantMessage.dataset.rawText += trailingText;
        }

        const finalText = assistantMessage.dataset.rawText;

        if (!finalText.trim()) {

            throw new Error(
                "The assistant returned an empty response."
            );
        }

        // Render the complete final response.
        assistantMessage.innerHTML = formatAssistantMessage(finalText);

        assistantMessage.classList.remove("is-streaming");

        chatMessages.scrollTop = chatMessages.scrollHeight;

    } catch (error) {

        console.error("Chat error:", error);

        const errorMessage = error.message || getNetworkError(error);

        if (loadingMessage) {
            loadingMessage.remove();
        }

        addMessage(errorMessage, "assistant");
    }
}

// ==========================================
// ERROR HANDLING
// ==========================================

function getFriendlyError(response) {
    switch (response.status) {
        case 400:
            return "I couldn't understand that request. Please try rephrasing your question.";

        case 401:
            return "Your session could not be verified. Please refresh the page and try again.";

        case 403:
            return "You don't currently have permission to perform that action.";

        case 404:
            return "The chat service could not be found. Please try again later.";

        case 408:
            return "The request took too long. Please try again.";

        case 429:
            return "I'm receiving too many requests right now. Please wait a moment and try again.";

        case 500:
            return "Something went wrong while preparing your answer. Please try again.";

        case 502:
        case 503:
        case 504:
            return "The AI service is temporarily unavailable. Please try again shortly.";

        default:
            return "Something went wrong. Please try again.";
    }
}

function getNetworkError(error) {
    if (error.name === "AbortError") {
        return "The request took too long. Please try again.";
    }

    if (!navigator.onLine) {
        return "You appear to be offline. Check your internet connection and try again.";
    }

    return "I couldn't connect to the university assistant. Please check that the server is running.";
}

// ==========================================
// CLEAR CHAT HISTORY
// ==========================================

function clearChatHistory() {
    chatMessages.innerHTML = "";

    localStorage.removeItem(CHAT_HISTORY_KEY);

    addMessage(
        "Hello! Welcome to UniAssist. How can I help you today?",
        "assistant"
    );
}

restoreChatHistory();

// ==========================================
// CLEAR CHAT BUTTON
// ==========================================

const clearChatDialog = document.getElementById("clear-chat-dialog");
const cancelClearChat = document.getElementById("cancel-clear-chat");
const confirmClearChat = document.getElementById("confirm-clear-chat");

chatClear.addEventListener("click", () => {
    if (typeof clearChatDialog.showModal === "function") {
        clearChatDialog.showModal();
    }
});

cancelClearChat.addEventListener("click", () => {
    clearChatDialog.close();
});

confirmClearChat.addEventListener("click", () => {
    clearChatHistory();
    clearChatDialog.close();
});

clearChatDialog.addEventListener("click", (event) => {
    if (event.target === clearChatDialog) {
        clearChatDialog.close();
    }
});

function clearChatHistory() {
    chatMessages.innerHTML = "";

    localStorage.removeItem(CHAT_HISTORY_KEY);

    addMessage(
        "Hello! Welcome to UniAssist. How can I help you today?",
        "assistant"
    );
}
