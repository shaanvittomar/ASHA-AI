# ASHA-AI 🤖

**ASHA-AI** is an AI-powered mental wellness and personal support web application designed to provide users with a safe space for conversation, mood tracking, journaling, and AI-assisted support.

> **ASHA** — *AI Support & Holistic Assistance*

The project combines a Python/Flask backend with a lightweight web frontend and Google's Gemini AI to provide conversational assistance while maintaining user data and personal journal entries.

---

## ✨ Features

- 🤖 **AI Chat Assistant** — Conversational AI support powered by Gemini
- 💬 **Chat History** — Stores previous conversations for continuity
- 😊 **Mood Tracking** — Record and monitor moods over time
- 📔 **Digital Journal** — Create, update, view, and delete journal entries
- 🔐 **User Authentication** — Secure registration and login using JWT
- 🛡️ **Safety Layer** — Additional safety handling for sensitive conversations
- 🌐 **REST API** — Flask-based backend API
- 💾 **Database Storage** — Persistent storage for users, chats, moods, and journals
- 📱 **Responsive Web Interface** — Simple and accessible frontend

---

## 🏗️ Project Structure

```text
ASHA-AI/
│
├── backend/
│   ├── app.py
│   ├── ai.py
│   ├── database.py
│   ├── safety.py
│   ├── requirements.py
│   ├── .gitignore
│   └── ...
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
└── README.md
```

---

## 🛠️ Tech Stack

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- Flask
- Flask-CORS
- Flask-JWT-Extended

### AI

- Google Gemini API
- Google GenAI Python SDK

### Database

- SQLite

### Authentication

- JSON Web Tokens (JWT)

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/shaanvittomar/ASHA-AI.git
cd ASHA-AI
```

---

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

Activate it:

**macOS / Linux**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

---

### 3. Install dependencies

Navigate to the backend:

```bash
cd backend
```

Install the required packages:

```bash
pip install -r requirements.txt
```

---

### 4. Configure environment variables

Create a `.env` file inside the backend directory:

```env
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET_KEY=your_secret_key
```

⚠️ **Never commit your `.env` file or API keys to GitHub.**

---

### 5. Run the backend

From the `backend` directory:

```bash
python app.py
```

The Flask server should start locally.

---

### 6. Run the frontend

Open:

```text
frontend/index.html
```

in your browser, or serve the frontend using a local development server.

---

## 🔑 API Configuration

ASHA-AI uses Google's Gemini API for AI-powered conversations.

You will need a Gemini API key and should store it in your `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

Do not hard-code API keys directly into the source code.

---

## 🔐 Security

The project uses JWT-based authentication for protected API routes.

Sensitive configuration should be stored using environment variables rather than committed to the repository.

Recommended `.gitignore`:

```gitignore
venv/
.env
__pycache__/
*.pyc
*.db
.DS_Store
```

---

## 🧠 How It Works

```text
                  ┌─────────────────┐
                  │     User        │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │    Frontend     │
                  │ HTML/CSS/JS     │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Flask Backend   │
                  │     REST API    │
                  └───────┬─────────┘
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
       ┌──────────┐ ┌───────────┐ ┌──────────┐
       │  SQLite  │ │  Gemini   │ │  Safety  │
       │ Database │ │    AI     │ │  Layer   │
       └──────────┘ └───────────┘ └──────────┘
```

---

## 📌 Current Capabilities

ASHA-AI currently provides:

- User registration and authentication
- JWT-based session management
- AI-powered conversations
- Persistent chat history
- Mood logging
- Journal management
- Safety-focused response handling
- RESTful backend architecture

---

## 🔮 Future Improvements

Possible future enhancements include:

- 📊 Mood analytics and visualization
- 🔔 Personalized reminders
- 🎙️ Voice-based conversations
- 🧠 Improved conversation memory
- 📱 Mobile application
- 🔒 Enhanced security and encryption
- ☁️ Cloud database integration
- 🚀 Production deployment
- 👤 Personalized AI assistance
- 📈 Mental wellness progress dashboard

---

## ⚠️ Disclaimer

ASHA-AI is an educational and software development project intended to provide AI-assisted support and personal wellness tools.

It is **not a replacement for professional medical, psychological, or emergency services**.

If someone is experiencing a mental health emergency or is in immediate danger, they should contact appropriate emergency services or a qualified professional.

---

## 👨‍💻 Author

**Shaanvit**

BTech Student & Developer

GitHub:  
https://github.com/shaanvittomar

---

## ⭐ Contributing

Contributions, suggestions, and improvements are welcome.

1. Fork the repository
2. Create a new branch

```bash
git checkout -b feature/your-feature
```

3. Make your changes
4. Commit your changes

```bash
git commit -m "Add your feature"
```

5. Push your branch

```bash
git push origin feature/your-feature
```

6. Open a Pull Request

---

## 📄 License

This project currently does not specify a license.
