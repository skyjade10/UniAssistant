const API_URL = `http://127.0.0.1:8765/api/chat/stream`;

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
// DISPLAY CHAT MESSAGES
// ==========================================

function addMessage(message, sender) {
    if (!chatMessages) return null;

    const messageElement = document.createElement("div");

    messageElement.classList.add("message", sender);

    // Use textContent to prevent HTML injection
    messageElement.textContent = message;

    chatMessages.appendChild(messageElement);

    chatMessages.scrollTop = chatMessages.scrollHeight;

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
    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || "Unable to process your question.");
        }

        if (!response.body) {
            throw new Error("Streaming is not supported by this browser.");
        }

        loadingMessage?.remove();

        const assistantMessage = addMessage("", "assistant");
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            assistantMessage.textContent += decoder.decode(value, { stream: true });
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        const trailingText = decoder.decode();
        if (trailingText) {
            assistantMessage.textContent += trailingText;
        }

        if (!assistantMessage.textContent.trim()) {
            throw new Error("The assistant returned an empty response.");
        }

    } catch (error) {
        console.error("Chat error:", error);
        loadingMessage?.remove();
        addMessage(
            "Sorry, I couldn't process your question right now. Please try again.",
            "assistant"
        );
    }
}
