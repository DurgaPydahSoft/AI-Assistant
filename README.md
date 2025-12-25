# 🤖 MongoDB AI Assistant

A high-performance, modular, and intelligent chatbot designed to query MongoDB databases using natural language. Built with **OpenRouter (OLMo 32B)** and **FastAPI**.

## 🚀 Key Features

- **Natural Language to NoSQL**: Translates human questions into complex MongoDB queries (find, count, aggregate).
- **Lightning Fast Performance**:
    - **Single-Route Architecture**: Merges routing and query generation to save round-trip time.
    - **Streaming Responses**: Real-time output in both CLI and Web API.
    - **Semantic Caching**: Instantly answers repeat or similar questions.
    - **Schema Pruning**: Minimized context window for faster inference and lower token costs.
- **Dynamic Adaptability**: Automatically detects your database collections and structure without hardcoding.
- **Modular & Clean Architecture**: Logic separated into specialized modules for maintainability.

---

## 🏗️ How It Works

1.  **Context Loading**: On startup, the system fetches all available collection names.
2.  **User Input**: User asks a question (e.g., "Find all users in NYC").
3.  **The Brain (Engine)**:
    - Checks the **Semantic Cache** for an existing answer.
    - If new, the LLM determines if it needs a collection's "map" (schema).
    - If needed, the system fetches a **pruned schema** (field names/types) and provides it to the AI.
4.  **Query Execution**: The AI generates a JSON query, the system executes it on MongoDB, and the AI formats the final human-readable answer.

---

## 📂 Project Structure

```text
CHATBOT/
├── src/
│   ├── cache.py       # Semantic and response caching
│   ├── config.py      # App configuration and constants
│   ├── database.py    # MongoDB connection management
│   ├── engine.py      # The "Brain" - Multi-step orchestration
│   ├── llm.py         # OpenRouter/OpenAI client wrappers
│   ├── models.py      # Pydantic data models
│   └── schema.py      # Dynamic schema analysis and caching
├── app.py             # FastAPI Web API (Entry point)
├── chat_cli.py        # Console Interface (Entry point)
├── .env               # Environment variables (GIT IGNORED)
├── .gitignore         # Version control hygiene
└── README.md          # You are here!
```

---

## 🛠️ Setup & Installation

1.  **Clone the project**
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure environment**: Create a `.env` file in the root:
    ```env
    MONGO_URI=mongodb://your_connection_string
    API_KEY=your_openrouter_api_key
    ```
4.  **Run the application**:
    - **Console**: `python chat_cli.py`
    - **Web API**: `python app.py` (Access docs at `http://localhost:8000/docs`)

---

## ⚙️ Configuration
You can tune the performance in `src/config.py`:
- `CACHE_TTL`: How long to remember database schemas (Default: 1 hour).
- `MODEL_NAME`: The OpenRouter model used (Default: `allenai/olmo-3.1-32b-think:free`).
- `MAX_STEPS`: Internal retry/thought loop limit.
