# 🤖 MongoDB AI Assistant

A high-performance, **asynchronous**, and intelligent chatbot designed to manage MongoDB databases using natural language. Built with a modular **FastAPI** backend and a premium **Vue 3** frontend.

## 🚀 Key Features

- **Full AI-Powered CRUD**:
    - **Create**: Add records via natural language ("Add a user named Satya").
    - **Read**: Dynamic querying with fuzzy field mapping.
    - **Update**: Precise data modification ("Change the status of student X to graduated").
    - **Delete**: Safely remove records using precise AI-generated filters.
- **Search Intelligence (Dynamic Few-Shot)**:
    - Automatically injects high-quality query patterns based on your question.
    - Handles field ambiguity (searching names across `name`, `username`, and `email` simultaneously).
- **Strict Truth Policy**:
    - Zero Hallucination: The AI is forbidden from inventing data or using placeholders.
    - Verified Results: Only answers based on real database records.
- **Scalable Async Architecture**:
    - **FastAPI / Motor**: Fully non-blocking I/O for high concurrency.
    - **Streaming API**: Real-time response generation with internal logs suppressed for a clean UI.
- **Performance Optimizations**:
    - **Semantic Caching**: Instant sub-millisecond responses for repeated questions.
    - **Dynamic Limits**: Configurable result caps (defaulting to 50) for fast, safe data retrieval.

---

## 📂 Project Structure

```text
CHATBOT/
├── back-end/
│   ├── src/             # Core Logic
│   │   ├── config.py    # Global settings & Model Selection
│   │   ├── database.py  # Async MongoDB Connection
│   │   ├── engine.py    # Prompt Orchestrator (The "Brain")
│   │   ├── examples.py  # Few-Shot Pattern Library
│   │   └── schema.py    # Dynamic Schema Analysis
│   ├── app.py           # FastAPI Web API (Streaming)
│   ├── chat_cli.py      # Console Interface
│   └── .env             # Backend secrets (API Keys, URI)
├── front-end/
│   ├── src/             # Vue 3 / Vite UI components
│   └── .env             # Frontend config (VITE_API_URL)
└── README.md
```

---

## 🛠️ Getting Started

### 1. Backend Setup
```bash
cd back-end
pip install -r requirements.txt
python app.py
```
*The API streams at `http://localhost:8000`*

### 2. Frontend Setup
```bash
cd front-end
npm install
npm run dev
```
*The UI will be standardly available at `http://localhost:5173`*

---

## ⚙️ Advanced Configuration (src/config.py)

- **MODEL_NAME**: Switch between models (Mimo, Olmo, etc.) via OpenRouter.
- **DEFAULT_LIMIT**: Controls how many records are returned (set to 50 by default).
- **CACHE_TTL**: Adjust how long semantic answers stay in memory.
- **MAX_STEPS**: Controls the maximum recursion for complex multi-step queries.

---

## 🛡️ Safety & Consistency
- **Precision First**: Update and Delete operations require a specific filter to prevent accidental bulk database changes.
- **Clean UI**: Technical JSON orchestration blocks are logged to the backend console rather than cluttering the user's chat.
