# AI Software Engineering Agent

A lightweight AI software engineering agent built in Python. The agent can inspect and modify a repository, execute commands, retrieve relevant codebase context using local RAG, and interact with Gemini through LangChain and LangGraph, with Ollama available as a local fallback.

## Architecture

The agent uses **LangChain** for LLM and tool integration, **LangGraph** for stateful agent workflow orchestration, **RAG** for repository context retrieval, and **LangSmith** for evaluation and observability support.

```text
User Task
   ↓
LangGraph Agent
   ↓
Retrieve Repository Context
   │
   ├── Repository Indexer
   ├── Code Chunker
   ├── Local Embeddings
   ├── SQLite Storage
   └── Similarity-based Retriever
   ↓
LLM via LangChain
   │
   └── Gemini
   ↓
Tool Decision
   │
   ├── No tool required
   │      ↓
   │     END
   │
   └── Tool required
          ↓
       LangGraph ToolNode
          │
          ├── scan_repository
          ├── read_file
          ├── write_file
          ├── edit_file
          └── run_command
          ↓
       Tool Result
          ↓
       LLM
          ↓
       END / Another Tool
```

### Framework Responsibilities

**LangChain**

* Integrates the application with the LLM.
* Defines repository tools using LangChain's `@tool`.
* Handles tool binding and tool calls.
* Provides standardized message abstractions.

**LangGraph**

* Defines the agent state.
* Orchestrates the RAG → LLM → Tool workflow.
* Handles conditional routing between the LLM and tools.
* Supports iterative tool execution through the graph.

**LangSmith**

* Provides an evaluation workflow for the agent.
* Stores evaluation datasets and examples.
* Runs the agent against the evaluation dataset.
* Supports experiment tracking and evaluation results.

**RAG**

* Indexes repository source code.
* Generates local embeddings.
* Stores code chunks and embeddings in SQLite.
* Retrieves relevant repository context for user tasks.

## Features

* LangChain-based LLM and tool integration.
* LangGraph-based stateful agent workflow.
* LangSmith evaluation dataset and evaluation pipeline.
* Repository scanning and file inspection.
* File creation and editing through tools.
* Python subprocess command execution.
* Tool error recovery.
* Maximum-iteration protection in the original agent loop.
* Local code RAG using Sentence Transformers and SQLite.
* Cosine-similarity based retrieval.
* Configurable `top_k` and `min_score` retrieval filtering.
* Graceful fallback when RAG retrieval fails.
* Gemini as the primary LLM.
* Ollama as a local fallback for the initial agent interaction.
* Dockerized application.
* Automated testing with pytest.
* MCP server integration.

## Tech Stack

| Component           | Technology                                 |
| ------------------- | ------------------------------------------ |
| Language            | Python 3.14                                |
| Primary LLM         | Gemini                                     |
| Fallback LLM        | Ollama (`qwen3:8b`)                        |
| LLM Framework       | LangChain                                  |
| Agent Orchestration | LangGraph                                  |
| Agent Evaluation    | LangSmith                                  |
| Code Execution      | Python subprocess                          |
| Testing             | pytest                                     |
| Version Control     | Git                                        |
| Repository Hosting  | GitHub                                     |
| Database            | SQLite                                     |
| RAG                 | Local RAG pipeline                         |
| Embeddings          | Sentence Transformers (`all-MiniLM-L6-v2`) |
| IDE                 | VS Code                                    |
| Containers          | Docker                                     |
| MCP                 | Python MCP server                          |

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
Context is constructed
   ↓
Repository context is added to the agent state
   ↓
LangGraph sends the enriched state to the LLM
```

## LangChain Integration

LangChain is used as the integration layer between the application, LLM, and repository tools.

### LangChain LLM

The project uses LangChain's chat model abstraction to initialize Gemini.

```text
Application
    ↓
LangChain Chat Model
    ↓
Gemini
```

The project also binds the repository tools to the LangChain model so the model can request tool execution.

### LangChain Tools

The existing application tools are exposed through LangChain wrappers:

```text
Existing ToolExecutor
        ↑
        │
LangChain Tool Wrappers
        │
        ├── lc_scan_repository
        ├── lc_read_file
        ├── lc_write_file
        ├── lc_edit_file
        └── lc_run_command
```

The `lc_*` tools reuse the existing `ToolExecutor`, allowing the LangChain integration to preserve the original tool implementation.

## LangGraph Integration

LangGraph is used to orchestrate the agent workflow.

The graph contains three main nodes:

```text
START
  ↓
retrieve_context
  ↓
llm
  ↓
tool required?
  ├── No → END
  │
  └── Yes
       ↓
     tools
       ↓
      llm
       ↓
     END / tools
```

### Agent State

The graph maintains:

```text
AgentState
├── task
└── messages
```

Messages are accumulated throughout the workflow, allowing the LLM and tools to communicate through the graph.

### Conditional Routing

After the LLM executes, the graph checks whether the response contains tool calls.

```text
LLM
 │
 ├── tool_calls present → ToolNode
 │
 └── no tool_calls       → END
```

After a tool executes, the result is returned to the LLM for the next decision.

## LangSmith Evaluation

LangSmith is used to evaluate the agent against a small evaluation dataset.

The project contains:

```text
create_langsmith_dataset.py
evaluate_agent.py
```

### Evaluation Dataset

The dataset contains examples covering:

* Repository file listing.
* Tool execution explanation.
* RAG repository-context explanation.

### Evaluation Flow

```text
LangSmith Dataset
       ↓
evaluate_agent.py
       ↓
LangGraph Agent
       ↓
Agent Output
       ↓
Evaluator
       ↓
Evaluation Result
```

The current evaluator performs a basic relevance check by comparing meaningful keywords from the expected output with the generated response.

This provides a starting point for evaluation and can later be extended with more robust LLM-based evaluators and task-specific metrics.

## LLM Fallback

Gemini is used as the primary model in the original agent flow. If the initial Gemini interaction raises an error, the application can fall back to the local Ollama model.

```text
Agent
  ↓
Gemini
  │
  ├── success → response
  │
  └── error
       ↓
    Ollama qwen3:8b
       ↓
    response
```

The Ollama server must be running locally for the fallback to work.

## Tools

The agent currently provides these application tools:

| Tool              | Purpose                                    |
| ----------------- | ------------------------------------------ |
| `scan_repository` | Discover files in a repository             |
| `read_file`       | Read repository files safely               |
| `write_file`      | Create or overwrite files                  |
| `edit_file`       | Modify existing files                      |
| `run_command`     | Execute commands through Python subprocess |

These tools are also exposed to LangChain through the `lc_*` wrappers.

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
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py
│   │   ├── nodes.py
│   │   ├── graph.py
│   │   └── run.py
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── gemini_client.py
│   │   ├── ollama_client.py
│   │   └── langchain_model.py
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
│       ├── schemas.py
│       └── langchain_tools.py
│
├── Dockerfile
├── .dockerignore
├── main.py
├── requirements.txt
├── create_langsmith_dataset.py
├── evaluate_agent.py
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

## LangSmith Setup

Configure the required LangSmith environment variables before using the evaluation scripts.

The LangSmith API key should be stored in `.env` rather than committed to Git.

The evaluation dataset can be created with:

```bash
python create_langsmith_dataset.py
```

Run the evaluation with:

```bash
python evaluate_agent.py
```

The evaluation script executes the LangGraph agent against the LangSmith dataset and reports the evaluation results.

## Testing

Run the complete test suite:

```bash
python -m pytest
```

The current test suite contains **64 passing tests**.

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
* LangChain wrappers reuse the existing application `ToolExecutor`.
* LangGraph orchestrates the RAG, LLM, and tool execution workflow.
* LangSmith is used for dataset-based agent evaluation.
* The current LangSmith evaluator is intentionally simple and can be extended with stronger evaluation methods.
* MCP integration is available as part of the project tooling.

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
LangChain               ✅
LangGraph               ✅
LangSmith               ✅
Application Test        ✅
Docker                  ✅
Docker End-to-End Test  ✅
Pytest                  ✅ 64/64
MCP                     ✅
```

## Future Improvements

Potential future improvements include:

* More advanced LangSmith evaluators.
* Automated evaluation datasets with larger task coverage.
* LLM-as-a-judge evaluation.
* Agent trajectory evaluation.
* Better tool-call failure recovery.
* More robust agent loop limits and retry policies.
* Improved observability and tracing.
* More advanced RAG retrieval and reranking.
* Additional MCP-based tools.
* Production deployment and monitoring.
