# Technical Documentation: MongoDB AI Agent

## 1. System Overview
The **MongoDB AI Agent** is a hybrid "Agentic" application that combinse natural language processing with database management and frontend automation. Unlike traditional chatbots that only generate text, this system can:
1.  **Read/Write Database Records**: Securely query and modify MongoDB data.
2.  **Control the UI**: autonomously click buttons and fill forms on the host application.
3.  **Embed Anywhere**: Run as a framework-agnostic Web Component in any third-party app.

## 2. High-Level Architecture

```mermaid
graph TD
    User[End User] -->|Interacts| Widget[<ai-chatbot> Widget]
    
    subgraph "Frontend (Host App)"
        Widget -->|Shadow DOM| VueApp[Vue 3 Application]
        VueApp -->|Render| ChatUI[Floating Chat Interface]
        VueApp -->|DOM Actions| HostPage[Host Page (Buttons/Forms)]
    end
    
    subgraph "Backend (API)"
        ChatUI -->|POST /chat| FastAPI[FastAPI Server]
        FastAPI -->|Prompt| Engine[Engine.py (Logic)]
        Engine -->|Context| Mongo[MongoDB]
        Engine -->|Inference| LLM[LLM Cloud (OpenAI/Compatible)]
    end
```

## 3. Core Concepts

### A. The "Embeddable Widget" (Frontend)
Instead of a standalone website, the frontend is built as a **Web Component** (`customElement`).
-   **Technology**: Vue 3 + Vite Library Mode.
-   **Encapsulation**: Uses **Shadow DOM** to prevent CSS conflicts. The chatbot's styles don't bleed into the host app, and the host app's styles don't break the chatbot.
-   **Bundling**: All CSS is bundled directly into the JavaScript (`chatbot.js`), making integration a single-line copy-paste.

### B. The "Agentic Protocol" (Communication)
The backend doesn't just send text. It streams a mixed HTTP/2 stream containing both **Conversational Text** and **Structured Commands**.

*Example Stream:*
```text
Sure, I can help with that.
[DOM_ACTION]{"type": "click", "target": "#approve-btn"}[/DOM_ACTION]
I have clicked the approve button for you.
```
-   **Text**: Rendered immediately to the user.
-   **[DOM_ACTION]**: Intercepted by the `useChat.js` composable, parsed, and executed against the browser DOM.

### C. Dynamic Context Injection
To allow the "Brain" (Backend) to control the "Body" (Frontend), the backend needs to know what buttons exist.
-   **Mechanism**: The frontend (or host app) sends a `ui_context` payload or the backend uses a generic "blind" mode.
-   **Decoupling**: The backend logic (`engine.py`) is generic. It doesn't hardcode `#btn-1`. It relies on the context provided at runtime or in the system configuration.

## 4. Detailed Data Flow

### Scenario: "Register a new user named John"

1.  **User Input**: User types "Register John" in the `<ai-chatbot>`.
2.  **Request**: `useChat.js` sends payload to `https://api.../chat`.
3.  **Prompt Engineering (`engine.py`)**:
    -   System constructs a prompt: *"You are an assistant. Available tools: MongoDB (Insert, Query), UI (Click, Type)."*
    -   It injects **Few-Shot Examples** relevant to "Register" (CRUD operations).
4.  **LLM Reasoning**:
    -   The LLM thinks: *"I need to fill the name field and click register."*
    -   LLM generates: ```json {"action": "dom_interaction", "target": "#input-name", "type": "type", "value": "John"}```
5.  **Execution Loop (`app.py`)**:
    -   The backend parses this JSON.
    -   It recognizes it as a `dom_interaction`.
    -   It wraps it in `[DOM_ACTION]...[/DOM_ACTION]` tags.
6.  **Streaming Response**:
    -   The backend streams this tag to the frontend.
7.  **Client Action**:
    -   `useChat.js` detects the tag.
    -   It executes `document.querySelector('#input-name').value = 'John'`.
    -   It visualizes a "Ghost Cursor" moving to the element for user feedback.
8.  **Completion**: The loop continues until the task is done (e.g., clicking the Submit button).

## 5. File Structure & Responsibilities

| File | Component | Responsibility |
| :--- | :--- | :--- |
| **Frontend** | | |
| `main.js` | Entry | Defines the `<ai-chatbot>` custom element and injects styles. |
| `useChat.js` | Logic | Manages state, API streaming, and parses `[DOM_ACTION]` tags. |
| `FloatingChat.vue` | UI | The visual interface (bubbles, input) rendered inside Shadow DOM. |
| **Backend** | | |
| `app.py` | API | FastAPI routes, CORS, and the main event loop. |
| `engine.py` | Intelligence | Constructs prompts, selects examples, and executes DB queries. |
| `database.py` | Persistence | Async connection to MongoDB. |

## 6. Security Model
-   **Database**: The Frontend **NEVER** accesses the DB directly. All queries go through the Backend API.
-   **DOM Control**: The Agent can only interact with the page the Widget is embedded on. It runs with the same permissions as the user.
-   **XSS Protection**: The `[DOM_ACTION]` parser uses `JSON.parse` strictly and requires explicit selectors, minimizing injection risks.
