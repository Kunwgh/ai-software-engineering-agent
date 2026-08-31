# AI Software Engineering Agent

A lightweight AI software engineering agent built in Python. The agent can inspect and modify a repository, execute commands, use local RAG context from the codebase, and interact with Gemini with an Ollama fallback.

## Architecture

```text
User Task
   ↓
SoftwareEngineeringAgent
   ├── RAG
   │    ├── Repository Indexer
   │    ├── Code Chunker
   │    ├── Local Embeddings
   │    ├── SQLite Storage
   │    └── Similarity-based Retriever
   │
   ├── Tools
   │    ├── scan_repository
   │    ├── read_file
   │    ├── write_file
   │    ├── edit_file
   │    └── run_command
   │
   └── LLM
        ├── Gemini (primary)
        └── Ollama / qwen3:8b (fallback)
```

## Features

* Lightweight custom agent loop without an external agent framework.
* Repository scanning and file inspection.
* File creation and editing through tools.
* Python subprocess command execution.
* Tool error recovery.
* Maximum-iteration protection.
* Local code RAG using Sentence Transformers and SQLite.
* Cosine-similarity based retrieval.
* Configurable `top_k` and `min_score` retrieval filtering.
* Graceful fallback to the original task when RAG retrieval fails.
* Gemini as the primary LLM.
* Ollama as a local fallback when the initial Gemini interaction fails.
* Dockerized application.
* Automated testing with pytest.

## Tech Stack

| Component          | Technology                                 |
| ------------------ | ------------------------------------------ |
| Language           | Python                                     |
| Primary LLM        | Gemini Free Tier                           |
| Fallback LLM       | Ollama (`qwen3:8b`)                        |
| Agent framework    | Custom lightweight agent loop              |
| Code execution     | Python subprocess                          |
| Testing            | pytest                                     |
| Version control    | Git                                        |
| Repository hosting | GitHub                                     |
| Database           | SQLite                                     |
| RAG                | Local                                      |
| Embeddings         | Sentence Transformers (`all-MiniLM-L6-v2`) |
| IDE                | VS Code                                    |
| Containers         | Docker                                     |
| MCP                | Planned for later                          |

## RAG Pipeline

```text
Repository
   ↓
Indexer discovers source files
   ↓
Code is split into chunks
   ↓
Local embedding model creates embeddings
   ↓
Chunks + embeddings are stored in SQLite
   ↓
User query is embedded
   ↓
Cosine similarity is calculated
   ↓
Low-score results can be filtered
   ↓
Top relevant chunks are selected
   ↓
Context is added to the agent prompt
   ↓
Agent sends the enriched task to the LLM
```

## LLM Fallback

Gemini is used as the primary model. If the initial Gemini interaction raises an error, the agent falls back to the local Ollama model.

```text
Agent
  ↓
Gemini
  ├── success → response
  └── error   → Ollama qwen3:8b → response
```

The Ollama server must be running locally for the fallback to work.

## Tools

The agent currently provides these tools:

| Tool              | Purpose                                    |
| ----------------- | ------------------------------------------ |
| `scan_repository` | Discover files in a repository             |
| `read_file`       | Read repository files safely               |
| `write_file`      | Create/write files                         |
| `edit_file`       | Modify existing files                      |
| `run_command`     | Execute commands through Python subprocess |

## Project Structure

```text
.
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── agent.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── repository.py
│   │   └── schema.py
│   │
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── embedder.py
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── gemini_client.py
│   │   └── ollama_client.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── context.py
│   │   ├── indexer.py
│   │   └── retriever.py
│   │
│   └── tools/
│       ├── __init__.py
│       ├── executor.py
│       ├── registry.py
│       ├── repository.py
│       └── schemas.py
│
├── Dockerfile
├── .dockerignore
├── main.py
├── requirements.txt
├── manual_file_agent.py
├── manual_repository_agent.py
│
├── test_agent_tools.py
├── test_chunker.py
├── test_context.py
├── test_database_chunks.py
├── test_edit_file.py
├── test_embedder.py
├── test_executor.py
├── test_gemini_client.py
├── test_indexer.py
├── test_read_file.py
├── test_repository.py
├── test_retriever.py
├── test_run_command.py
├── test_schemas.py
└── test_write_file.py
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Kunwgh/ai-software-engineering-agent.git
cd ai-software-engineering-agent
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

### 5. Start Ollama

Install Ollama and make sure it is running.

Pull the fallback model:

```bash
ollama pull qwen3:8b
```

Start the server when needed:

```bash
ollama serve
```

### 6. Run the agent

```bash
python main.py
```

Enter a software-engineering task when prompted.

Type:

```text
exit
```

to stop the application.

## Testing

Run the complete test suite:

```bash
python -m pytest
```

The current test suite contains **62 passing tests**.

The two manual Gemini scripts are intentionally named so pytest does not collect and execute them automatically:

```text
manual_file_agent.py
manual_repository_agent.py
```

## Docker

Build the Docker image:

```bash
docker build -t ai-software-engineering-agent .
```

Run the container interactively:

```bash
docker run --rm -it \
  --add-host=host.docker.internal:host-gateway \
  -e GEMINI_API_KEY="$(grep '^GEMINI_API_KEY=' .env | cut -d '=' -f2-)" \
  ai-software-engineering-agent
```

The host gateway configuration allows the Docker container to reach an Ollama server running on the host machine.

### Docker Database Note

The current `Dockerfile` copies the local `agent.db` into the image.

`agent.db` is intentionally ignored by Git, so a Docker build requires an existing local `agent.db` file.

## Development Notes

* Gemini Free Tier limits can be reached during development.
* Ollama provides a local fallback for the initial agent interaction.
* The RAG embedding model is downloaded locally when it is first needed.
* Gemini API keys are kept outside the Docker image and supplied at runtime.
* MCP integration is planned as a future extension.

## Current Status

The core AI software engineering agent is implemented and tested.

```text
Agent Loop              ✅
Repository Tools        ✅
Tool Error Recovery     ✅
SQLite                  ✅
RAG                     ✅
Local Embeddings        ✅
Gemini                  ✅
Ollama Fallback         ✅
Application Test        ✅
Docker                  ✅
Docker End-to-End Test   ✅
Pytest                  ✅ 62/62
