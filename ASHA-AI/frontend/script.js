const API_URL = "http://127.0.0.1:5000/api";

let selectedMood = null;
let currentUser = null;


// ==========================================
// STORAGE
// ==========================================

function getToken() {
    return localStorage.getItem("asha_token");
}


function saveToken(token) {
    localStorage.setItem("asha_token", token);
}


function clearToken() {
    localStorage.removeItem("asha_token");
}


// ==========================================
// HELPERS
// ==========================================

function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text || "";

    return div.innerHTML;
}


function formatDate(value) {

    if (!value) {
        return "";
    }

    return new Date(value).toLocaleDateString(
        "en-IN",
        {
            day: "numeric",
            month: "short",
            year: "numeric"
        }
    );
}


function formatDateTime(value) {

    if (!value) {
        return "";
    }

    return new Date(value).toLocaleString(
        "en-IN",
        {
            day: "numeric",
            month: "short",
            hour: "numeric",
            minute: "2-digit"
        }
    );
}


// ==========================================
// API REQUEST
// ==========================================

async function apiRequest(endpoint, options = {}) {

    const token = getToken();

    const headers = {
        "Content-Type": "application/json"
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(
        `${API_URL}${endpoint}`,
        {
            ...options,
            headers: {
                ...headers,
                ...(options.headers || {})
            }
        }
    );

    let data = {};

    try {
        data = await response.json();
    } catch {
        data = {};
    }

    if (!response.ok) {

        if (response.status === 401) {
            clearToken();
            showLogin();
        }

        throw new Error(
            data.error ||
            data.msg ||
            "Request failed"
        );
    }

    return data;
}


// ==========================================
// AUTH SCREENS
// ==========================================

function showLogin() {

    document
        .getElementById("authScreen")
        .classList.remove("hidden");

    document
        .getElementById("registerScreen")
        .classList.add("hidden");

    document
        .getElementById("appScreen")
        .classList.add("hidden");
}


function showRegister() {

    document
        .getElementById("authScreen")
        .classList.add("hidden");

    document
        .getElementById("registerScreen")
        .classList.remove("hidden");

    document
        .getElementById("appScreen")
        .classList.add("hidden");
}


function showApp() {

    document
        .getElementById("authScreen")
        .classList.add("hidden");

    document
        .getElementById("registerScreen")
        .classList.add("hidden");

    document
        .getElementById("appScreen")
        .classList.remove("hidden");
}


// ==========================================
// REGISTER
// ==========================================

async function register(event) {

    event.preventDefault();

    const name =
        document
            .getElementById("registerName")
            .value
            .trim();

    const email =
        document
            .getElementById("registerEmail")
            .value
            .trim();

    const password =
        document
            .getElementById("registerPassword")
            .value;

    const message =
        document.getElementById(
            "registerMessage"
        );


    message.textContent =
        "Creating your account...";


    try {

        const data =
            await apiRequest(
                "/register",
                {
                    method: "POST",

                    body: JSON.stringify({
                        name,
                        email,
                        password
                    })
                }
            );


        console.log(
            "Registration:",
            data
        );


        message.textContent =
            "Account created successfully.";


        document
            .getElementById("registerForm")
            .reset();


        setTimeout(
            function() {

                showLogin();

                document
                    .getElementById("authMessage")
                    .textContent =
                    "Account created. Please sign in.";

            },
            1000
        );


    } catch (error) {

        console.error(
            "Registration error:",
            error
        );

        message.textContent =
            error.message;
    }
}


// ==========================================
// LOGIN
// ==========================================

async function login(event) {

    event.preventDefault();

    const email =
        document
            .getElementById("email")
            .value
            .trim();

    const password =
        document
            .getElementById("password")
            .value;

    const message =
        document.getElementById(
            "authMessage"
        );


    message.textContent =
        "Signing in...";


    try {

        const data =
            await apiRequest(
                "/login",
                {
                    method: "POST",

                    body: JSON.stringify({
                        email,
                        password
                    })
                }
            );


        if (!data.token) {

            throw new Error(
                "Login token was not returned by the server."
            );
        }


        saveToken(data.token);

        currentUser = data.user;

        message.textContent = "";

        showApp();

        await initialiseApp();


    } catch (error) {

        console.error(
            "Login error:",
            error
        );

        message.textContent =
            error.message;
    }
}


// ==========================================
// LOGOUT
// ==========================================

function logout() {

    clearToken();

    currentUser = null;

    showLogin();
}


// ==========================================
// USER
// ==========================================

async function loadUser() {

    const data =
        await apiRequest("/me");

    currentUser =
        data.user;

    if (!currentUser) {
        return;
    }


    const name =
        document.getElementById(
            "userName"
        );

    const email =
        document.getElementById(
            "userEmail"
        );

    const avatar =
        document.getElementById(
            "userAvatar"
        );


    if (name) {
        name.textContent =
            currentUser.name;
    }

    if (email) {
        email.textContent =
            currentUser.email;
    }

    if (avatar) {

        avatar.textContent =
            currentUser.name
                ? currentUser.name
                    .charAt(0)
                    .toUpperCase()
                : "A";
    }


    const greeting =
        document.getElementById(
            "greeting"
        );

    if (greeting) {

        greeting.textContent =
            `How are you feeling, ${currentUser.name}?`;
    }
}


// ==========================================
// NAVIGATION
// ==========================================

function showPage(pageName) {

    document
        .querySelectorAll(".page")
        .forEach(
            page => {
                page.classList.remove(
                    "active-page"
                );
            }
        );


    const page =
        document.getElementById(
            `${pageName}Page`
        );


    if (page) {

        page.classList.add(
            "active-page"
        );
    }


    document
        .querySelectorAll(
            ".nav-item[data-page]"
        )
        .forEach(
            button => {

                button.classList.remove(
                    "active"
                );

                if (
                    button.dataset.page ===
                    pageName
                ) {

                    button.classList.add(
                        "active"
                    );
                }
            }
        );


    if (pageName === "journal") {
        loadJournals();
    }

    if (pageName === "mood") {
        loadMoods();
    }

    if (pageName === "talk") {
        loadChatHistory();
    }

    if (pageName === "insights") {
        loadInsights();
    }
}


// ==========================================
// DATE
// ==========================================

function updateDate() {

    const element =
        document.getElementById(
            "todayDate"
        );

    if (!element) {
        return;
    }


    element.textContent =
        new Date().toLocaleDateString(
            "en-IN",
            {
                weekday: "long",
                day: "numeric",
                month: "long",
                year: "numeric"
            }
        );
}


// ==========================================
// JOURNAL
// ==========================================

async function saveJournal() {

    const title =
        document
            .getElementById("journalTitle")
            .value
            .trim();

    const content =
        document
            .getElementById("journalText")
            .value
            .trim();

    const message =
        document.getElementById(
            "journalMessage"
        );


    if (!content) {

        message.textContent =
            "Write something before saving.";

        return;
    }


    message.textContent =
        "Saving...";


    try {

        await apiRequest(
            "/journals",
            {
                method: "POST",

                body: JSON.stringify({
                    title,
                    content
                })
            }
        );


        document
            .getElementById("journalTitle")
            .value = "";

        document
            .getElementById("journalText")
            .value = "";

        document
            .getElementById("wordCount")
            .textContent =
            "0 words";


        message.textContent =
            "Entry saved ✓";


        await loadJournals();


    } catch (error) {

        message.textContent =
            error.message;
    }
}


async function loadJournals() {

    const list =
        document.getElementById(
            "journalList"
        );


    if (!list) {
        return;
    }


    list.innerHTML =
        `<p class="loading">
            Loading your entries...
        </p>`;


    try {

        const data =
            await apiRequest(
                "/journals"
            );

        const journals =
            data.journals || [];


        if (!journals.length) {

            list.innerHTML = `
                <div class="empty-state">

                    <div class="empty-icon">
                        ✎
                    </div>

                    <h3>
                        No journal entries yet
                    </h3>

                    <p>
                        Your saved reflections
                        will appear here.
                    </p>

                </div>
            `;

            return;
        }


        list.innerHTML =
            journals
                .map(
                    journal => `
                        <article
                            class="journal-entry"
                            data-id="${journal.id}"
                        >

                            <div class="journal-entry-header">

                                <div>

                                    <h3>
                                        ${escapeHtml(
                                            journal.title ||
                                            "Untitled entry"
                                        )}
                                    </h3>

                                    <small>
                                        ${formatDateTime(
                                            journal.created_at
                                        )}
                                    </small>

                                </div>

                                <div class="journal-actions-small">

                                    <button
                                        onclick="editJournal(${journal.id})"
                                    >
                                        Edit
                                    </button>

                                    <button
                                        onclick="deleteJournal(${journal.id})"
                                    >
                                        Delete
                                    </button>

                                </div>

                            </div>

                            <p>
                                ${escapeHtml(
                                    journal.content
                                )}
                            </p>

                        </article>
                    `
                )
                .join("");


    } catch (error) {

        list.innerHTML = `
            <div class="empty-state">

                <h3>
                    Couldn't load journals
                </h3>

                <p>
                    ${escapeHtml(
                        error.message
                    )}
                </p>

            </div>
        `;
    }
}


// ==========================================
// EDIT JOURNAL
// ==========================================

async function editJournal(id) {

    try {

        const data =
            await apiRequest(
                `/journals/${id}`
            );

        const journal =
            data.journal;


        document
            .getElementById("journalTitle")
            .value =
            journal.title || "";


        document
            .getElementById("journalText")
            .value =
            journal.content || "";


        document
            .getElementById("journalMessage")
            .textContent =
            "Editing this entry. Save it as a new entry for now.";


        showPage("journal");


    } catch (error) {

        alert(error.message);
    }
}


// ==========================================
// DELETE JOURNAL
// ==========================================

async function deleteJournal(id) {

    const confirmed =
        confirm(
            "Delete this journal entry?"
        );


    if (!confirmed) {
        return;
    }


    try {

        await apiRequest(
            `/journals/${id}`,
            {
                method: "DELETE"
            }
        );


        await loadJournals();


    } catch (error) {

        alert(error.message);
    }
}


// ==========================================
// WORD COUNT
// ==========================================

function updateWordCount() {

    const text =
        document
            .getElementById("journalText")
            .value
            .trim();

    const count =
        text
            ? text.split(/\s+/).length
            : 0;


    document
        .getElementById("wordCount")
        .textContent =
        `${count} ${count === 1 ? "word" : "words"}`;
}


// ==========================================
// MOOD
// ==========================================

function selectMood(value) {

    selectedMood =
        Number(value);


    document
        .querySelectorAll(
            ".mood-scale button"
        )
        .forEach(
            button => {

                button.classList.toggle(
                    "selected",
                    Number(
                        button.dataset.mood
                    ) === selectedMood
                );
            }
        );


    document
        .getElementById(
            "selectedMood"
        )
        .textContent =
        `You selected ${selectedMood}/10`;
}


async function saveMood() {

    if (!selectedMood) {

        alert(
            "Please select a mood first."
        );

        return;
    }


    const note =
        document
            .getElementById("moodNote")
            .value
            .trim();


    try {

        await apiRequest(
            "/moods",
            {
                method: "POST",

                body: JSON.stringify({
                    mood: selectedMood,
                    note
                })
            }
        );


        document
            .getElementById("moodNote")
            .value = "";


        document
            .getElementById("selectedMood")
            .textContent =
            "Check-in saved ✓";


        await loadMoods();


    } catch (error) {

        alert(error.message);
    }
}


async function loadMoods() {

    const history =
        document.getElementById(
            "moodHistory"
        );


    if (!history) {
        return;
    }


    try {

        const data =
            await apiRequest(
                "/moods"
            );

        const moods =
            data.moods || [];


        updateRecentMood(moods);


        if (!moods.length) {

            history.innerHTML = `
                <div class="empty-state">

                    <div class="empty-icon">
                        ♡
                    </div>

                    <h3>
                        No check-ins yet
                    </h3>

                    <p>
                        Your mood history
                        will appear here.
                    </p>

                </div>
            `;

            return;
        }


        history.innerHTML =
            moods
                .map(
                    item => `
                        <article class="mood-entry">

                            <div class="mood-score">
                                ${item.mood}
                            </div>

                            <div>

                                <strong>
                                    ${item.mood}/10
                                </strong>

                                ${
                                    item.note
                                        ? `<p>${escapeHtml(item.note)}</p>`
                                        : ""
                                }

                                <small>
                                    ${formatDateTime(
                                        item.created_at
                                    )}
                                </small>

                            </div>

                        </article>
                    `
                )
                .join("");


    } catch (error) {

        history.innerHTML = `
            <div class="empty-state">

                <h3>
                    Couldn't load mood history
                </h3>

                <p>
                    ${escapeHtml(
                        error.message
                    )}
                </p>

            </div>
        `;
    }
}


function updateRecentMood(moods) {

    const container =
        document.getElementById(
            "recentMood"
        );


    if (!container) {
        return;
    }


    if (!moods.length) {

        container.innerHTML =
            "<p>No mood check-ins yet.</p>";

        return;
    }


    const latest =
        moods[0];


    container.innerHTML = `
        <div class="recent-mood-content">

            <strong>
                ${latest.mood}/10
            </strong>

            <span>
                ${formatDateTime(
                    latest.created_at
                )}
            </span>

            ${
                latest.note
                    ? `<p>${escapeHtml(latest.note)}</p>`
                    : ""
            }

        </div>
    `;
}


// ==========================================
// CHAT
// ==========================================

async function sendMessage() {

    const input =
        document.getElementById(
            "chatInput"
        );

    const container =
        document.getElementById(
            "chatMessages"
        );


    const text =
        input.value.trim();


    if (!text) {
        return;
    }


    addChatMessage(
        "user",
        text
    );


    input.value = "";


    const thinking =
        document.createElement(
            "div"
        );

    thinking.className =
        "asha-message";

    thinking.innerHTML = `
        <div class="chat-avatar">
            A
        </div>

        <div class="chat-bubble">

            <strong>
                ASHA
            </strong>

            <p>
                Thinking...
            </p>

        </div>
    `;


    container.appendChild(
        thinking
    );


    scrollChat();


    try {

        const data =
            await apiRequest(
                "/chat",
                {
                    method: "POST",

                    body: JSON.stringify({
                        message: text
                    })
                }
            );


        thinking.remove();


        addChatMessage(
            "assistant",
            data.response ||
            "I'm here with you."
        );


    } catch (error) {

        thinking
            .querySelector("p")
            .textContent =
            error.message;
    }
}


function addChatMessage(
    role,
    content
) {

    const container =
        document.getElementById(
            "chatMessages"
        );


    if (role === "user") {

        container.innerHTML += `
            <div class="user-message">

                <div class="chat-bubble">
                    ${escapeHtml(content)}
                </div>

            </div>
        `;

    } else {

        container.innerHTML += `
            <div class="asha-message">

                <div class="chat-avatar">
                    A
                </div>

                <div class="chat-bubble">

                    <strong>
                        ASHA
                    </strong>

                    <p>
                        ${escapeHtml(content)}
                    </p>

                </div>

            </div>
        `;
    }


    scrollChat();
}


function scrollChat() {

    const container =
        document.getElementById(
            "chatMessages"
        );

    if (container) {

        container.scrollTop =
            container.scrollHeight;
    }
}


// ==========================================
// CHAT HISTORY
// ==========================================

async function loadChatHistory() {

    const container =
        document.getElementById(
            "chatMessages"
        );


    if (!container) {
        return;
    }


    try {

        const data =
            await apiRequest(
                "/messages"
            );

        const messages =
            data.messages || [];


        container.innerHTML = "";


        if (!messages.length) {

            addChatMessage(
                "assistant",
                "Hi. I'm ASHA. What's on your mind today?"
            );

            return;
        }


        messages.forEach(
            message => {

                addChatMessage(
                    message.role,
                    message.content
                );
            }
        );


    } catch (error) {

        console.error(
            "Chat history error:",
            error
        );
    }
}


// ==========================================
// INSIGHTS
// ==========================================

async function loadInsights() {

    try {

        const moodData =
            await apiRequest(
                "/moods"
            );

        const journalData =
            await apiRequest(
                "/journals"
            );


        const moods =
            moodData.moods || [];

        const journals =
            journalData.journals || [];


        document
            .getElementById(
                "checkinCount"
            )
            .textContent =
            moods.length;


        document
            .getElementById(
                "journalCount"
            )
            .textContent =
            journals.length;


        if (moods.length) {

            const total =
                moods.reduce(
                    (
                        sum,
                        item
                    ) =>
                        sum +
                        Number(item.mood),
                    0
                );


            const average =
                total /
                moods.length;


            document
                .getElementById(
                    "averageMood"
                )
                .textContent =
                average.toFixed(1) +
                "/10";


        } else {

            document
                .getElementById(
                    "averageMood"
                )
                .textContent =
                "—";
        }


        const timeline =
            document.getElementById(
                "moodTimeline"
            );


        if (!moods.length) {

            timeline.innerHTML =
                "<p>No mood data yet.</p>";

            return;
        }


        timeline.innerHTML =
            moods
                .slice(0, 10)
                .map(
                    item => `
                        <div class="timeline-item">

                            <strong>
                                ${item.mood}/10
                            </strong>

                            <span>
                                ${formatDate(
                                    item.created_at
                                )}
                            </span>

                        </div>
                    `
                )
                .join("");


    } catch (error) {

        console.error(
            "Insights error:",
            error
        );
    }
}


// ==========================================
// INITIALISE
// ==========================================

async function initialiseApp() {

    showApp();

    updateDate();

    await loadUser();

    await loadMoods();

    showPage("today");
}


// ==========================================
// EVENT LISTENERS
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        // Auth

        document
            .getElementById("showRegister")
            .addEventListener(
                "click",
                showRegister
            );


        document
            .getElementById("showLogin")
            .addEventListener(
                "click",
                showLogin
            );


        document
            .getElementById("loginForm")
            .addEventListener(
                "submit",
                login
            );


        document
            .getElementById("registerForm")
            .addEventListener(
                "submit",
                register
            );


        // Navigation

        document
            .querySelectorAll(
                ".nav-item[data-page]"
            )
            .forEach(
                button => {

                    button.addEventListener(
                        "click",
                        function() {

                            showPage(
                                button.dataset.page
                            );
                        }
                    );
                }
            );


        document
            .getElementById("logoutButton")
            .addEventListener(
                "click",
                logout
            );


        // Home

        document
            .getElementById("todayCheckin")
            .addEventListener(
                "click",
                () => showPage("mood")
            );


        document
            .getElementById("homeJournal")
            .addEventListener(
                "click",
                () => showPage("journal")
            );


        document
            .getElementById("homeChat")
            .addEventListener(
                "click",
                () => showPage("talk")
            );


        document
            .getElementById("viewMood")
            .addEventListener(
                "click",
                () => showPage("mood")
            );


        // Journal

        document
            .getElementById("saveJournal")
            .addEventListener(
                "click",
                saveJournal
            );


        document
            .getElementById("journalText")
            .addEventListener(
                "input",
                updateWordCount
            );


        // Mood

        document
            .querySelectorAll(
                ".mood-scale button"
            )
            .forEach(
                button => {

                    button.addEventListener(
                        "click",
                        function() {

                            selectMood(
                                button.dataset.mood
                            );
                        }
                    );
                }
            );


        document
            .getElementById("saveMood")
            .addEventListener(
                "click",
                saveMood
            );


        // Chat

        document
            .getElementById("chatForm")
            .addEventListener(
                "submit",
                function(event) {

                    event.preventDefault();

                    sendMessage();
                }
            );


        // Start

        if (getToken()) {

            initialiseApp();

        } else {

            showLogin();
        }
    }
);