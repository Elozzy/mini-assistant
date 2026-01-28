# Mini Assistant (Tarnished)

**Tarnished** is a text-based personal AI that acts as a lightweight “operating system” for your machine. Instead of casual chat, it analyzes your intent and produces **structured actions**—like opening apps, searching files, or fetching system info—then executes them via a local agent on your Mac.

---

## What It Does

- **Intent → Actions**: You send a natural-language message (e.g. *"Open Safari"* or *"Search for PDFs on my Desktop"*). The AI returns a JSON response with a friendly summary and a list of **actions** (tool + device + args).
- **Memory**: Short-term (in-memory conversation history) and long-term (ChromaDB vector store with Ollama embeddings) so past context can influence replies.
- **Execution**: The backend sends those actions to a **macOS agent** (Go service on port 8081), which runs them locally—e.g. `open -a Safari`, `find ~/Desktop -name "*.pdf"`, or `sw_vers`.
- **Tools**: `filesystem.search`, `filesystem.open`, `apps.open`, `system.info` (see [AgentResponse schema](#api) and executor implementation).

So in practice: *"What’s my Mac’s OS version?"* → LLM returns `system.info` → agent runs `sw_vers` → you get the output in the API response.

---

## Architecture

```
┌─────────────┐     POST /chat      ┌──────────────────────────────────────────┐
│   Client    │ ──────────────────► │  Backend (FastAPI, default :8000)       │
│  (e.g. UI   │                     │  - Ollama (generate + embeddings)       │
│   or curl)  │ ◄────────────────── │  - Short-term + long-term memory       │
└─────────────┘   JSON response     │  - Parses JSON, then calls agent         │
                                    └─────────────────────┬───────────────────┘
                                                          │ POST /execute
                                                          ▼
                                    ┌──────────────────────────────────────────┐
                                    │  macOS Agent (Gin, :8081)                │
                                    │  - Runs tools: apps.open, find, sw_vers  │
                                    │  - Returns results per action           │
                                    └──────────────────────────────────────────┘
```

- **Backend**: Python (FastAPI), uses Ollama for generation and embeddings, ChromaDB for vector memory.
- **Agent**: Go (Gin), receives a list of actions and runs them via `exec` and shell commands.

---

## Prerequisites

- **Python 3.9+** (for backend)
- **Go 1.25+** (for macOS agent)
- **Ollama** installed and running:
  - [Install Ollama](https://ollama.com)
  - Pull the chat model: `ollama pull llama3.1`
  - Pull the embedding model: `ollama pull nomic-embed-text`
- **macOS** (the agent’s tools are written for macOS: `open`, `find`, `sw_vers`).

---

## Quick Start

### 1. Clone and enter the project

```bash
git clone <repo-url>
cd mini-assistant
```

### 2. Backend (Python)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install chromadb      # used for long-term memory
```

Create a `.env` in `backend/` (optional; defaults work if Ollama is on `localhost`):

```env
OLLAMA_URL=XXX_XXX_XXX
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

Run the API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `GET http://localhost:8000/health`

### 3. macOS Agent (Go)

In another terminal:

```bash
cd agents/macos
go mod download
go run .
```

Agent listens on **http://localhost:8081** (`GET /ping`, `POST /execute`).

### 4. Try the chat API

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Open Safari"}'
```

Or ask for system info:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What macOS version am I running?"}'
```

---

## API

### `POST /chat`

**Request**

```json
{
  "message": "Open Safari"
}
```

**Response (success)**

```json
{
  "response": {
    "message": "Opened Safari.",
    "actions": [
      {
        "tool": "apps.open",
        "device": "MacBook Pro",
        "args": { "app_name": "Safari" }
      }
    ]
  },
  "execution_results": [
    {
      "tool": "apps.open",
      "device": "MacBook Pro",
      "status": "success",
      "output": "Safari opened successfully"
    }
  ]
}
```

If the LLM returns invalid JSON, you get `error`, `raw_output`, and `details` instead. If the agent is unreachable, `execution_results` will contain `"Agent error: ..."` per action.

### Agent: `POST /execute`

The backend calls this internally. Body:

```json
{
  "actions": [
    { "tool": "apps.open", "device": "MacBook Pro", "args": { "app_name": "Safari" } }
  ]
}
```

Response: `{ "results": [ { "tool", "device", "status", "output" }, ... ] }`.

---

## Project Layout

```
mini-assistant/
├── backend/                    # Python FastAPI app
│   ├── app/
│   │   ├── api/
│   │   │   └── chat.py         # POST /chat, calls Ollama + agent
│   │   ├── agent/
│   │   │   ├── long_term_memory.py  # ChromaDB + Ollama embeddings
│   │   │   ├── memory.py       # In-memory short-term history
│   │   │   ├── prompt.py       # System prompt for Tarnished
│   │   │   └── schemas.py      # Action, AgentResponse, TOOLS
│   │   ├── core/
│   │   │   ├── config.py       # OLLAMA_*, env loading
│   │   │   └── ollama.py       # generate(), get_embedding()
│   │   └── main.py             # FastAPI app, mounts chat router
│   ├── requirements.txt
│   └── .env                    # optional
├── agents/
│   └── macos/
│       ├── main.go             # Gin server, /ping, /execute
│       ├── tools/
│       │   └── executor.go     # apps.open, filesystem.search, system.info
│       └── go.mod
└── README.md
```

---

## Environment variables (backend)

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_URL` | Ollama generate API URL | Must be set (e.g. `http://localhost:11434/api/generate`) |
| `OLLAMA_EMBEDDING_MODEL` | Model used for embeddings | `nomic-embed-text` |

The chat model is fixed in code as `llama3.1`; the agent URL is `http://localhost:8081/execute` in `chat.py`.

---

## Tools (macOS agent)

| Tool | Description | Example args |
|------|-------------|--------------|
| `apps.open` | Open an app by name | `{ "app_name": "Safari" }` |
| `filesystem.search` | Search files (e.g. Desktop) | `{ "extension": "pdf" }` |
| `system.info` | macOS version info | `{}` |

`filesystem.open` is defined in the schema but not yet implemented in `executor.go`.

---

## Contributing

1. Backend: add or change tools in `app/agent/schemas.py` and in the system prompt in `app/agent/prompt.py`; keep `AgentResponse` and action shapes in sync.
2. Agent: implement or extend tools in `agents/macos/tools/executor.go` and handle new tools in `Execute()`.
3. Ensure Ollama is running and the correct models are pulled before testing chat and memory.

---

## License

See the repository’s license file (if present).
