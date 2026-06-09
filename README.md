# Scout: AI Engineering Assistant with MCP, LangGraph & GraphRAG

## Overview

Scout is an AI-powered engineering assistant built using LangGraph, Model Context Protocol (MCP), Neo4j GraphRAG, and OpenAI GPT-4.1-mini.

Scout combines conversational reasoning, tool usage, engineering memory, and autonomous reflection to assist developers with software engineering, deployment, debugging, infrastructure management, and project development tasks.

Unlike traditional chatbots, Scout can:

* Use tools from multiple MCP servers
* Learn from past engineering experiences
* Build and query a knowledge graph of debugging sessions
* Reflect on execution outcomes and generate lessons learned
* Retrieve historical solutions to recurring problems

---

## Architecture

```text
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

* Debugging code
* Troubleshooting deployments
* Managing infrastructure
* Performing repository operations
* Answering engineering questions
* Executing tool-based workflows

---

### MCP Integration

Scout communicates with multiple MCP servers through the Model Context Protocol.

Supported capabilities include:

* File system operations
* GitHub interactions
* Command execution
* Data processing
* Custom engineering tools
* Infrastructure management

New MCP servers can be added without modifying Scout's core architecture.

---

### LangGraph Orchestration

Scout uses LangGraph to manage:

* Conversation state
* Tool execution
* Multi-step reasoning
* Agent workflows
* Reflection cycles

This enables more reliable and controllable agent behavior than traditional chatbot architectures.

---

### Engineering Memory System

Scout maintains a persistent engineering memory containing:

* Deployment issues
* Root causes
* Fixes
* Best practices
* Infrastructure knowledge
* Lessons learned

Knowledge is stored in narrative form and transformed into a graph structure for retrieval.

---

### GraphRAG Knowledge Graph

Scout automatically converts engineering experiences into a Neo4j knowledge graph.

Knowledge categories include:

* Docker
* FastAPI
* GitHub Actions
* AWS EC2
* Python
* MCP Integrations
* CI/CD Pipelines

The graph enables semantic retrieval of previous solutions.

Example questions:

```text
How was uvicorn_not_found resolved?

What deployment mistakes have occurred before?

What Docker best practices were learned?

Which AWS issues have already been solved?
```

---

### Autonomous Reflection System

Scout includes a reflection engine that analyzes:

* Tool execution results
* Failures
* Deployment outcomes
* Debugging sessions

The reflection system generates engineering insights and stores them as future knowledge.

This allows Scout to continuously improve its engineering memory.

---

## Project Structure

```text
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
├── requirements.txt
├── .env
└── README.md
```

---

## Technology Stack

### AI & Agents

* OpenAI GPT-4.1-mini
* LangChain
* LangGraph

### GraphRAG

* Neo4j AuraDB
* GraphCypherQAChain
* LLMGraphTransformer

### MCP Ecosystem

* Model Context Protocol (MCP)
* Custom MCP Servers
* Filesystem MCP
* GitHub MCP

### Backend

* Python 3.13
* UV Package Manager

---

## Installation

### Clone Repository

```bash
git clone <repository-url>

cd mcp-intro
```

### Create Virtual Environment

```bash
uv venv

source .venv/bin/activate
```

### Install Dependencies

```bash
uv sync
```

---

## Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=

NEO4J_URI=
NEO4J_USERNAME=
NEO4J_PASSWORD=
NEO4J_DATABASE=
```

---

## MCP Configuration

Configure MCP servers in:

```text
scout/my_mcp/mcp_config.json
```

Example:

```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem"]
  }
}
```

---

## Running Scout

Start the assistant:

```bash
python scout/client.py
```

Exit using:

```text
quit
```

or

```text
exit
```

---

## Building the Knowledge Graph

Generate a Neo4j knowledge graph from engineering memory:

```bash
python scout/graphdb.py
```

This pipeline:

1. Loads engineering memory
2. Chunks narrative experiences
3. Extracts entities and relationships
4. Creates graph documents
5. Stores them in Neo4j

---

## Testing the Graph

```bash
python scout/graphtest.py
```

Validation includes:

* Schema inspection
* Node counts
* Relationship counts
* Graph retrieval tests
* GraphCypherQAChain testing

---

## Example Use Cases

### Debugging

```text
Why is my Docker container failing to start?
```

### Deployment

```text
How was ERR_CONNECTION_REFUSED fixed on EC2?
```

### Knowledge Retrieval

```text
What lessons were learned from GitHub Actions?
```

### Infrastructure

```text
What AWS deployment issues have occurred previously?
```

### MCP Tool Usage

```text
Use the filesystem MCP server to inspect this project.
```

---

## Future Enhancements

### Hybrid GraphRAG

Combine:

* Neo4j Graph Search
* Vector Search
* Semantic Retrieval

for improved answer quality.

### Multi-Agent Architecture

Introduce specialized agents for:

* Deployment
* Infrastructure
* Development
* Security

### Automated Knowledge Generation

Automatically generate memory entries from:

* Tool executions
* Logs
* Deployment reports
* Reflection outputs

### MCP Marketplace Integration

Support dynamic discovery and loading of MCP servers.

---

## Vision

Scout aims to become a persistent AI Engineering Copilot that remembers every debugging session, deployment issue, architectural decision, and engineering lesson, transforming engineering experience into searchable organizational knowledge.
