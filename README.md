# AGENTIS: AI Engineering Assistant with MCP, LangGraph & GraphRAG

## Overview

Scout is an AI-powered engineering assistant built using **LangGraph**, **Model Context Protocol (MCP)**, **Neo4j GraphRAG**, and **OpenAI GPT-4.1-mini**.

Scout combines conversational reasoning, tool usage, engineering memory, and autonomous reflection to assist developers with software engineering, deployment, debugging, infrastructure management, and project development tasks.

Unlike traditional chatbots, Scout can:

- Use tools from multiple MCP servers
- Learn from past engineering experiences
- Build and query a knowledge graph of debugging sessions
- Reflect on execution outcomes and generate lessons learned
- Retrieve historical solutions to recurring problems

---

## Architecture

```
              User Query
                   │
                   ▼
            LangGraph Agent
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
   GPT-4.1     MCP Tools   GraphRAG
       │           │           │
       ▼           ▼           ▼
  Reasoning    Tool Usage   Knowledge Retrieval
       │           │           │
       └───────────┼───────────┘
                   ▼
            Final Response
                   │
                   ▼
        Engineering Reflection
                   │
                   ▼
             Memory Update
```

---

## Key Features

### AI Engineering Assistant

Scout acts as an engineering copilot capable of:

- Debugging code
- Troubleshooting deployments
- Managing infrastructure
- Performing repository operations
- Answering engineering questions
- Executing tool-based workflows

### MCP Integration

Scout communicates with multiple MCP servers through the Model Context Protocol.

Supported capabilities include:

- File system operations
- GitHub interactions
- Command execution
- Data processing
- Custom engineering tools
- Infrastructure management

### LangGraph Orchestration

Scout uses LangGraph to manage:

- Conversation state
- Tool execution
- Multi-step reasoning
- Agent workflows
- Reflection cycles

### Engineering Memory System

Scout maintains a persistent engineering memory containing:

- Deployment issues
- Root causes
- Fixes
- Best practices
- Infrastructure knowledge
- Lessons learned

### GraphRAG Knowledge Graph

Scout automatically converts engineering experiences into a Neo4j knowledge graph.

Knowledge categories include:

- Docker
- FastAPI
- GitHub Actions
- AWS EC2
- Python
- MCP Integrations
- CI/CD Pipelines

### Autonomous Reflection System

Scout includes a reflection engine that analyzes:

- Tool execution results
- Failures
- Deployment outcomes
- Debugging sessions

The reflection system generates engineering insights and stores them as future knowledge.

---

## Project Structure

```
mcp-intro/
│
├── scout/
│   ├── graph.py
│   ├── client.py
│   ├── reflection.py
│   ├── graphdb.py
│   ├── graphtest.py
│   ├── agent_memory.txt
│   │
│   └── my_mcp/
│       ├── config.py
│       ├── mcp_config.json
│       └── local_servers/
│
├── docker-compose.yml
├── .env.example
├── README.md
└── keys/
```

---

## Technology Stack

### AI & Agents

| Component | Technology |
|-----------|-----------|
| LLM | OpenAI GPT-4.1-mini |
| Agent Framework | LangChain / LangGraph |
| Knowledge Graph | Neo4j AuraDB + GraphRAG |
| Graph Querying | GraphCypherQAChain, LLMGraphTransformer |

### MCP Ecosystem

- Model Context Protocol (MCP)
- Custom MCP Servers
- Filesystem MCP
- GitHub MCP

### Backend

- Python 3.13
- UV Package Manager
- Docker

---

## Quick Start

### Prerequisites

Install [Docker Desktop](https://www.docker.com/products/docker-desktop/):

- Windows (WSL2 enabled)
- macOS
- Linux (Docker Engine + Docker Compose)

Verify installation:

```bash
docker --version
docker compose version
```

### Download Configuration Files

```bash
curl -O https://raw.githubusercontent.com/sudeepK0714U/mcp-intro/main/.env.example
curl -O https://raw.githubusercontent.com/sudeepK0714U/mcp-intro/main/docker-compose.yml
```

### Create Required Directories

**Linux/macOS:**
```bash
mkdir projects
mkdir keys
```

**Windows PowerShell:**
```powershell
mkdir projects
mkdir keys
```

### Configure Environment Variables

Rename the example environment file.

**Linux/macOS:**
```bash
mv .env.example .env
```

**Windows PowerShell:**
```powershell
Rename-Item .env.example .env
```

Edit `.env` and provide your credentials:

```env
OPENAI_API_KEY=

NEO4J_URI=
NEO4J_USERNAME=
NEO4J_PASSWORD=
NEO4J_DATABASE=

GITHUB_PERSONAL_ACCESS_TOKEN=

EC2_HOST=
EC2_USER=
```

### Optional: EC2 Deployment Support

Place your EC2 PEM key inside:

```
keys/
└── my-key.pem
```

The container automatically mounts this directory to `/app/keys`.

### Optional: Project Analysis Support

Place any projects you want Scout to analyze inside `projects/`. The container automatically mounts this directory to `/app/projects`.

---

## Running Scout

### Pull Latest Image

```bash
docker compose pull
```

### Start Scout

```bash
docker compose run --rm scout
```

**Expected output:**

```
USER:
```

**Example interactions:**

```
USER: Analyze my project
USER: Create a Dockerfile for this repository
USER: Help me deploy to EC2
USER: What deployment issues have occurred previously?
USER: quit
```

### Updating Scout

```bash
docker compose pull
docker compose run --rm scout
```

## Future Enhancements

### Hybrid GraphRAG

Combine Neo4j Graph Search, Vector Search, and Semantic Retrieval for improved answer quality.

### Multi-Agent Architecture

Introduce specialized agents for:

- Deployment
- Infrastructure
- Development
- Security

### Automated Knowledge Generation

Automatically generate memory entries from tool executions, logs, deployment reports, and reflection outputs.

### MCP Marketplace Integration

Support dynamic discovery and loading of MCP servers.

---

## Vision

Scout aims to become a **persistent AI Engineering Copilot** that remembers every debugging session, deployment issue, architectural decision, and engineering lesson — transforming engineering experience into searchable organizational knowledge.
