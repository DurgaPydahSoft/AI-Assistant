# 🤖 MongoDB AI Assistant

A high-performance, modular, and intelligent chatbot designed to query MongoDB databases using natural language. Built with **OpenRouter (OLMo 32B)** and **FastAPI**.

## 🚀 Key Features

- **Natural Language to NoSQL**: Translates human questions into complex MongoDB queries.
- **Premium Vue Frontend**: Modern, glassmorphic UI with real-time streaming answers.
- **Lightning Fast Performance**:
    - **Single-Route Logic**: Merges routing and query generation.
    - **Streaming Responses**: Real-time output in both CLI and Web UI.
    - **Semantic Caching**: Instant answers for repeat questions.
    - **Schema Pruning**: Minimized context window for faster inference.
- **Modular Architecture**: Clearly separated `front-end` and `back-end`.

---

## 📂 Project Structure

```text
CHATBOT/
├── back-end/
│   ├── src/             # Core logic (cache, database, engine, etc.)
│   ├── app.py           # FastAPI Web API
│   ├── chat_cli.py      # Console Interface
│   ├── .env             # Backend secrets
│   └── requirements.txt # Python dependencies
├── front-end/
│   ├── src/             # Vue 3 components and logic
│   ├── .env             # Frontend config (VITE_API_URL)
│   └── package.json     # Node dependencies
└── README.md
```

---

## 🛠️ How to Start the Application

### 1. Start the Back-end
Open a terminal and run:
```bash
cd back-end
# Install dependencies if you haven't:
pip install -r requirements.txt
# Run the API:
python app.py
```
*The API will be available at `http://localhost:8000`*

### 2. Start the Front-end
Open a **second** terminal and run:
```bash
cd front-end
# Install dependencies if you haven't:
npm install
# Run the dev server:
npm run dev
```
*The UI will be available at `http://localhost:5173` (or similar, check terminal output)*

---

## ⚙️ Configuration
- **Back-end**: Edit `back-end/.env` for DB URI and API Keys.
- **Front-end**: Edit `front-end/.env` to point to the correct `VITE_API_URL`.
- **Logic**: Edit `back-end/src/config.py` to change models or cache times.
