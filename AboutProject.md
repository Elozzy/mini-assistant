# Tarnished OS Portfolio Project

> A text-based AI personal assistant that understands, remembers, and acts.

---

## Project Vision

**TarnishedOS** is a **text-based AI personal operating system** designed to showcase senior-level backend engineering and AI integration skills. It demonstrates:

1. **Natural language understanding** — Parse user intent and produce structured actions.
2. **Memory systems** — Short-term (session) and long-term (vector embeddings) memory for context-aware responses.
3. **Safe system execution** — MacOS agent executes commands locally (open apps, search files, fetch system info).
4. **Multi-step reasoning** — Plan and execute sequences of actions (e.g., open Notes → search files → summarize content).
5. **Extensible architecture** — Designed for future multi-device support (phone, tablet, web clients).

---

## Skills Demonstrated

| Skill Area | What This Project Shows |
|------------|------------------------|
| **Backend Engineering** | FastAPI, REST API design, error handling, Pydantic validation |
| **AI / LLM Integration** | Prompt engineering, tool schemas, structured JSON outputs |
| **Systems Programming** | Go daemon, process execution, macOS system commands |
| **Memory & Embeddings** | Vector search, ChromaDB, Ollama embeddings, semantic retrieval |
| **Architecture Design** | Multi-service communication, agent pattern, extensible device model |
| **DevOps Ready** | Environment configuration, modular structure, clear documentation |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | Python, FastAPI | REST API, request handling, orchestration |
| **AI / LLM** | Ollama (llama3.1) | Text generation, intent parsing |
| **Embeddings** | Ollama (nomic-embed-text) | Semantic memory vectors |
| **Short-term Memory** | In-memory (Python) | Session conversation history |
| **Long-term Memory** | ChromaDB | Persistent vector storage for past interactions |
| **Agent / Execution** | Go, Gin | MacOS daemon executing system commands |
| **Frontend** | React + Tailwind *(optional)* | Chat UI, action logs, memory visualization |
| **Database** | SQLite/Postgres *(optional)* | User logs, action history |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                   USER                                      │
│                            (CLI, curl, or UI)                               │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ POST /chat
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND (:8000)                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Chat Endpoint                                 │   │
│  │  1. Add message to short-term memory                                │   │
│  │  2. Query long-term memory (vector search)                          │   │
│  │  3. Build prompt with context                                       │   │
│  │  4. Call Ollama LLM                                                 │   │
│  │  5. Parse structured JSON response                                  │   │
│  │  6. Execute actions via MacOS agent                                 │   │
│  │  7. Return results to user                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                  │                                          │
│          ┌───────────────────────┼───────────────────────┐                 │
│          ▼                       ▼                       ▼                 │
│  ┌──────────────┐       ┌──────────────┐       ┌──────────────┐           │
│  │  Short-term  │       │  Long-term   │       │   Ollama     │           │
│  │   Memory     │       │   Memory     │       │    LLM       │           │
│  │  (in-memory) │       │  (ChromaDB)  │       │  (:11434)    │           │
│  └──────────────┘       └──────────────┘       └──────────────┘           │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ POST /execute
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MACOS AGENT (:8081)                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Tool Executor                                 │   │
│  │  • apps.open      → open -a "AppName"                               │   │
│  │  • filesystem.search → find ~/Desktop -name "*.pdf"                 │   │
│  │  • system.info    → sw_vers                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
Tarnishedos/
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   └── chat.py               # Main chat endpoint
│   │   ├── agent/
│   │   │   ├── memory.py             # Short-term memory (in-memory)
│   │   │   ├── long_term_memory.py   # Long-term memory (ChromaDB + embeddings)
│   │   │   ├── prompt.py             # System prompt for LLM
│   │   │   └── schemas.py            # Pydantic models, tool definitions
│   │   ├── core/
│   │   │   ├── config.py             # Environment configuration
│   │   │   └── ollama.py             # Ollama API client (generate + embed)
│   │   └── main.py                   # FastAPI app entry point
│   ├── requirements.txt
│   └── .env
├── agents/
│   └── macos/                        # Go agent for macOS
│       ├── main.go                   # Gin server, /execute endpoint
│       ├── tools/
│       │   └── executor.go           # Tool implementations
│       └── go.mod
├── frontend/                         # Optional React frontend
│   ├── src/
│   │   ├── App.tsx
│   │   └── components/
│   │       └── ChatBox.tsx
│   └── package.json
├── README.md                         # Quick start guide
└── AboutProject.md                   # This file
```

---

## Key Features

### Backend (Python/FastAPI)

| Feature | Description |
|---------|-------------|
| **Chat Endpoint** | Single `/chat` endpoint handles all user interactions |
| **Short-term Memory** | In-memory conversation history for session context |
| **Long-term Memory** | ChromaDB vector store with Ollama embeddings for semantic search |
| **Multi-action Responses** | LLM returns multiple actions in a single response |
| **Automatic Execution** | Actions are sent to MacOS agent and executed |
| **Schema Validation** | Pydantic models enforce JSON structure |
| **Graceful Error Handling** | Handles invalid LLM output, connection failures |

### MacOS Agent (Go/Gin)

| Feature | Description |
|---------|-------------|
| **Lightweight Daemon** | Minimal Go server running on port 8081 |
| **Safe Execution** | Only whitelisted tools can run |
| **Extensible** | Easy to add new tools (clipboard, notifications, etc.) |
| **Result Reporting** | Returns execution status and output for each action |

### AI / LLM Features

| Feature | Description |
|---------|-------------|
| **Prompt Engineering** | System prompt enforces JSON schema and tool usage |
| **Tool Schema Design** | Structured actions with `tool`, `device`, `args` |
| **Multi-step Reasoning** | LLM can plan sequences of actions |
| **Memory-aware Responses** | Past context influences current responses |

---

## Implemented Tools

| Tool | Description | Example |
|------|-------------|---------|
| `apps.open` | Open an application by name | `{ "app_name": "Safari" }` |
| `filesystem.search` | Search for files by extension | `{ "extension": "pdf" }` |
| `system.info` | Get macOS version info | `{}` |
| `filesystem.open` | Open a file *(schema defined, not yet implemented)* | `{ "path": "/path/to/file" }` |

---

## Sample Interaction

**User:**
```
"Open Safari and tell me my macOS version"
```

**LLM Response:**
```json
{
  "message": "Opening Safari and fetching your macOS version.",
  "actions": [
    { "tool": "apps.open", "device": "MacBook Pro", "args": { "app_name": "Safari" } },
    { "tool": "system.info", "device": "MacBook Pro", "args": {} }
  ]
}
```

**Execution Results:**
```json
{
  "message": "Opening Safari and fetching your macOS version.",
  "actions": [...],
  "execution_results": [
    { "tool": "apps.open", "status": "success", "output": "Safari opened successfully" },
    { "tool": "system.info", "status": "success", "output": "ProductName: macOS\nProductVersion: 14.0\n..." }
  ]
}
```

---

## Optional Enhancements

### Frontend (High Impact for Portfolio)

- Chat UI with message bubbles
- Action log showing what TarnishedOS executed
- Memory visualization (retrieved context)
- Responsive design (mobile + desktop)

### Multi-device Support

- Same backend serves multiple clients
- Device registry for laptop, phone, tablet
- Future: mobile app, browser extension

### Persistent Logging

- SQLite/Postgres for action history
- User analytics and debugging
- Audit trail for executed commands

### Security Layer

- API key authentication between backend and agent
- Rate limiting on chat endpoint
- Sandboxed execution environment

---

## Portfolio Presentation

### Demo Materials

1. **Screenshots / GIFs:**
   - Sending a command → app opens
   - Memory retrieval in action
   - Multi-step reasoning example

2. **Architecture Diagram:**
   - Visual flow from user to execution

3. **Code Highlights:**
   - Prompt engineering in `prompt.py`
   - Go executor in `executor.go`
   - Vector memory in `long_term_memory.py`

### Talking Points

> "I built a multi-step AI assistant that understands natural language, remembers past interactions using vector embeddings, and executes safe commands on macOS through a Go daemon."

- **AI Integration:** "Custom prompt engineering to enforce structured JSON outputs"
- **Systems Programming:** "Go daemon executes macOS commands with proper error handling"
- **Memory Systems:** "Semantic search over past conversations using ChromaDB + Ollama embeddings"
- **Fullstack Design:** "Clean separation of concerns: Python backend, Go agent, optional React frontend"

---

## Development Milestones

| Phase | Milestone | Status |
|-------|-----------|--------|
| 1 | Basic chat endpoint with Ollama | ✅ Complete |
| 2 | Short-term + long-term memory | ✅ Complete |
| 3 | MacOS agent integration | ✅ Complete |
| 4 | Error handling + graceful degradation | ✅ Complete |
| 5 | React frontend (optional) | 🔲 Planned |
| 6 | Documentation + demo video | 🔲 Planned |

---

## Running Locally

### Prerequisites

- Python 3.9+
- Go 1.20+
- Ollama installed and running
- macOS (for agent execution)

### Quick Start

```bash
# 1. Start Ollama
ollama serve

# 2. Pull required models
ollama pull llama3.1
ollama pull nomic-embed-text

# 3. Start backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && pip install chromadb
uvicorn app.main:app --reload --port 8000

# 4. Start macOS agent (new terminal)
cd agents/macos
go run .

# 5. Test it
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Open Safari"}'
```

---

## Future Roadmap

- [ ] React chat frontend with action visualization
- [ ] Clipboard tool (`clipboard.read`, `clipboard.write`)
- [ ] Notification tool (`notification.send`)
- [ ] Multi-device registry and routing
- [ ] User authentication and session management
- [ ] Persistent action logging (SQLite/Postgres)
- [ ] Docker Compose for easy deployment
- [ ] Demo video and portfolio page

---

## License

MIT License — See [LICENSE](./LICENSE) for details.

---

*Built as a portfolio project demonstrating AI integration, systems programming, and fullstack architecture.*
