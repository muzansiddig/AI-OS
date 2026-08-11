# AI-OS

### Local-First AI Agent Operating System

AI-OS is a modular, local-first AI agent orchestration platform designed to provide a unified interface for multiple specialized AI agents.

Instead of depending on a single AI agent, AI-OS acts as an orchestration layer that receives a user request, determines the required capability, plans the execution path, and dispatches the task to the appropriate agent service.

The system is designed around **local AI inference**, **service isolation**, **centralized configuration**, and **extensible agent routing**.

---

## Architecture

```text
                         ┌─────────────────────┐
                         │       User          │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   AI-OS Gateway      │
                         │      :8000           │
                         └──────────┬──────────┘
                                    │
                   ┌────────────────┼────────────────┐
                   │                │                │
                   ▼                ▼                ▼
             Classifier          Planner         Registry
                   │                │                │
                   └────────────────┼────────────────┘
                                    │
                                    ▼
                              Dispatcher
                                    │
          ┌─────────────────┬───────┼────────┬─────────────────┐
          │                 │       │        │                 │
          ▼                 ▼       ▼        ▼                 ▼
      Open          Browser      OpenHands  CrewAI           AutoGPT
   Interpreter       Use
      :8101          :8102        :8103      :8104             :8105
          │             │            │          │                 │
          └─────────────┴────────────┴──────────┴─────────────────┘
                                    │
                                    ▼
                              Local AI Layer
                                  Ollama
                                :11434
                                    │
                                    ▼
                              Local LLM Model
```

---

# Core Idea

AI-OS provides a single gateway for interacting with multiple AI agents.

A user does not need to know which agent should handle a task.

For example:

```text
"Open a terminal and run this command"
              ↓
       Intent Classifier
              ↓
       terminal_command
              ↓
      Open Interpreter
              ↓
             Ollama
```

A software-development request can follow another route:

```text
"Build a React application"
              ↓
       Intent Classifier
              ↓
       code_generation
              ↓
          OpenHands
              ↓
             Ollama
```

A web task can be routed to Browser Use:

```text
"Browse GitHub and inspect this repository"
              ↓
       Intent Classifier
              ↓
        web_browsing
              ↓
         Browser Use
              ↓
             Ollama
```

The goal is to make the individual agents implementation details rather than something the user has to manage manually.

---

# Current Services

| Service          |  Port | Primary Responsibility                        |
| ---------------- | ----: | --------------------------------------------- |
| Gateway          |  8000 | Routing, orchestration and service management |
| Open Interpreter |  8101 | Terminal and computer execution               |
| Browser Use      |  8102 | Browser automation and web interaction        |
| OpenHands        |  8103 | Software engineering and codebase tasks       |
| CrewAI           |  8104 | Multi-agent workflows                         |
| AutoGPT          |  8105 | Autonomous planning and research tasks        |
| Ollama           | 11434 | Local LLM inference                           |

---

# Gateway

The Gateway is the central control plane of AI-OS.

It is responsible for:

* Receiving user requests
* Intent classification
* Task planning
* Service discovery
* Service selection
* HTTP dispatching
* Aggregating service results
* Health monitoring
* Returning normalized responses

The primary request flow is:

```text
User Request
     ↓
Gateway
     ↓
Classifier
     ↓
Planner
     ↓
Service Registry
     ↓
Dispatcher
     ↓
HTTP Client
     ↓
Agent Service
     ↓
Ollama
```

---

# Service Registry

The Service Registry is the single source of truth for registered AI services.

It stores information such as:

* Service name
* Service URL
* Port
* Enabled state
* Workspace
* Service capability

Example:

```python
{
    "open_interpreter": {
        "url": "http://127.0.0.1:8101",
        "enabled": True
    }
}
```

This prevents different parts of the Gateway from maintaining conflicting service definitions.

---

# Intent Classification

The Gateway currently supports the following primary intent categories:

```text
terminal_command
code_generation
web_browsing
multi_agent_workflow
autonomous_task
general_task
```

Example:

```text
open terminal and run command
→ terminal_command
→ open_interpreter
```

```text
browse github repository website
→ web_browsing
→ browser_use
```

```text
build react application code
→ code_generation
→ openhands
```

```text
run multi agent crewai workflow
→ multi_agent_workflow
→ crewai
```

```text
execute autonomous research goal
→ autonomous_task
→ autogpt
```

The classifier uses explicit matching rules and word-boundary matching to reduce accidental substring matches.

---

# Centralized AI Configuration

AI-OS uses a centralized configuration strategy.

The default configuration is defined through environment variables.

Example:

```env
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3:8b
```

Services can override the default model when required:

```env
OPENHANDS_MODEL=${OLLAMA_MODEL}
OPENINTERPRETER_MODEL=${OLLAMA_MODEL}
BROWSER_USE_MODEL=${OLLAMA_MODEL}
CREWAI_MODEL=${OLLAMA_MODEL}
AUTOGPT_MODEL=${OLLAMA_MODEL}
```

The intended configuration hierarchy is:

```text
Central Default
      ↓
Service Override
      ↓
Runtime Configuration
```

This allows the system to start with one model while remaining flexible enough to use specialized models later.

---

# Ollama

AI-OS is designed around local inference using Ollama.

The default local Ollama API is:

```text
http://127.0.0.1:11434
```

Example configuration:

```env
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3:8b
```

Ollama exposes a local API for programmatic model interaction, including chat and generation endpoints.

Official documentation:

https://docs.ollama.com/

---

# API Contract

All agent services follow a common HTTP contract.

## Health

```http
GET /health
```

Example:

```json
{
  "status": "healthy",
  "service": "open_interpreter"
}
```

## Chat

```http
POST /chat
```

Example request:

```json
{
  "prompt": "Reply with exactly: AI_OS_OK"
}
```

Services return structured JSON responses.

The common interface makes it possible to add or replace agents without redesigning the Gateway.

---

# Gateway API

## Health

```http
GET /health
```

Checks the Gateway itself.

---

## Service Discovery

```http
GET /services
```

Returns the registered services.

---

## Aggregated Service Health

```http
GET /services/health
```

Checks the health of the registered agent services.

This provides a single system-level health view.

---

## Chat

```http
POST /chat
```

Example:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"open terminal and run command"}'
```

The Gateway determines the appropriate execution route.

---

# Example End-to-End Flow

A request such as:

```text
build a React application
```

can follow:

```text
POST /chat
      ↓
Gateway :8000
      ↓
Classifier
      ↓
code_generation
      ↓
Planner
      ↓
OpenHands
      ↓
:8103
      ↓
Ollama
      ↓
Local LLM
```

The user interacts with the Gateway rather than directly managing every agent.

---

# Verified Integration

The current implementation has been tested through an end-to-end Gateway pipeline.

The verified path is:

```text
Gateway :8000
      ↓
Classifier
      ↓
Planner
      ↓
Registry
      ↓
Dispatcher
      ↓
Open Interpreter :8101
      ↓
Ollama :11434
```

The reported E2E test result was:

```text
Gateway Service Discovery      PASS
Open Interpreter Health        PASS
Gateway → Open Interpreter     PASS
Open Interpreter → Ollama      PASS
HTTP Status                    200
```

The five-service verification also reported successful health checks and intent routing for:

```text
terminal_command       → open_interpreter
web_browsing            → browser_use
code_generation         → openhands
multi_agent_workflow    → crewai
autonomous_task         → autogpt
```

These results establish that the orchestration and service-routing layer has been integrated successfully in the tested local environment.

---

# Project Structure

The project is organized as a modular multi-service system.

Conceptually:

```text
AI-OS/
│
├── gateway/
│   ├── app/
│   │   ├── services/
│   │   │   ├── classifier.py
│   │   │   ├── client.py
│   │   │   ├── dispatcher.py
│   │   │   └── registry.py
│   │   │
│   │   ├── supervisor/
│   │   │   ├── planner.py
│   │   │   └── supervisor.py
│   │   │
│   │   ├── config.py
│   │   └── ...
│   │
│   └── pyproject.toml
│
├── services/
│   ├── open-interpreter/
│   ├── browser-use/
│   ├── openhands/
│   ├── crewai/
│   └── autogpt/
│
├── scripts/
│   ├── test_e2e_gateway.py
│   └── verify_all_services.py
│
├── workspace/
│   ├── projects/
│   ├── downloads/
│   ├── temp/
│   └── outputs/
│
├── .env.example
├── .gitignore
└── README.md
```

The exact directory structure may evolve as individual agent integrations mature.

---

# Technology Stack

## Core

* Python
* FastAPI
* Uvicorn
* HTTPX
* Pydantic
* `uv`

## AI

* Ollama
* Local LLMs
* LiteLLM where required by individual integrations

## Agent Engines

* Open Interpreter
* Browser Use
* OpenHands
* CrewAI
* AutoGPT

## Architecture

* HTTP microservices
* Service Registry
* Intent Classification
* Task Planning
* Dispatcher
* Local-first execution
* Workspace isolation

---

# Local-First Design

AI-OS is designed to minimize dependency on external AI APIs.

The intended architecture is:

```text
AI-OS
  ↓
Local Agent Services
  ↓
Ollama
  ↓
Local Models
```

This provides:

* Local inference
* Reduced external API dependency
* Better control over data
* Offline-capable components where supported
* Ability to switch models without redesigning the Gateway

Ollama's local API does not require authentication when accessed locally.

---

# Installation

## Requirements

Recommended environment:

* Windows / Linux / macOS
* Python 3.11+
* `uv`
* Ollama
* Git

Some individual agent services may have additional requirements.

---

## Clone

```bash
git clone https://github.com/muzansiddig/AI-OS.git
cd AI-OS
```

---

## Install Ollama

Install Ollama for your operating system and verify:

```bash
ollama --version
```

Then pull the configured model:

```bash
ollama pull qwen3:8b
```

Verify available models:

```bash
ollama list
```

The Ollama API can also be queried directly:

```bash
curl http://127.0.0.1:11434/api/tags
```

---

# Environment Configuration

Create `.env` from `.env.example`.

Example:

```env
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3:8b

OPENHANDS_MODEL=${OLLAMA_MODEL}
OPENINTERPRETER_MODEL=${OLLAMA_MODEL}
BROWSER_USE_MODEL=${OLLAMA_MODEL}
CREWAI_MODEL=${OLLAMA_MODEL}
AUTOGPT_MODEL=${OLLAMA_MODEL}
```

Do not commit `.env` if it contains secrets.

---

# Running the System

Start Ollama first:

```bash
ollama serve
```

Then start the individual services.

Example:

```bash
cd services/open-interpreter
uv run python -m app.main
```

Start the Gateway:

```bash
cd gateway
uv run python -m app.main
```

The exact startup commands may differ between agent implementations.

---

# Verify Gateway

```bash
curl http://127.0.0.1:8000/health
```

Then:

```bash
curl http://127.0.0.1:8000/services
```

And:

```bash
curl http://127.0.0.1:8000/services/health
```

---

# Test Chat

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Reply with exactly: AI_OS_GATEWAY_OK"}'
```

---

# Testing

AI-OS includes integration-oriented verification scripts.

Gateway E2E:

```bash
uv run python scripts/test_e2e_gateway.py
```

Full service verification:

```bash
uv run python scripts/verify_all_services.py
```

The verification suite checks:

```text
Service availability
       ↓
Health endpoints
       ↓
Gateway discovery
       ↓
Aggregated health
       ↓
Intent classification
       ↓
Planner
       ↓
Service routing
```

---

# Important Current Status

AI-OS currently has a functioning orchestration foundation and verified local integration paths.

However, **passing health checks and E2E routing tests does not mean every agent is production-ready for arbitrary real-world tasks**.

Individual agents may still have limitations related to:

* Browser reliability
* Long-running tasks
* Model quality
* Tool execution
* Context management
* Recovery from failures
* Concurrent requests
* Authentication
* Resource consumption
* Sandboxing
* Permission management

The current milestone should therefore be considered:

```text
Functional Multi-Agent Orchestration Platform
```

rather than:

```text
Fully Production-Hardened Autonomous AI OS
```

---

# Roadmap

## Phase 1 — Core Infrastructure

* [x] Gateway
* [x] Service Registry
* [x] Dispatcher
* [x] Intent Classifier
* [x] Planner
* [x] Central configuration
* [x] Ollama integration
* [x] Standard service contract

---

## Phase 2 — Agent Integration

* [x] Open Interpreter
* [x] Browser Use
* [x] OpenHands
* [x] CrewAI
* [x] AutoGPT
* [x] Health checks
* [x] Service discovery
* [x] Multi-service verification

---

## Phase 3 — Reliability Infrastructure

Planned:

* [ ] Redis
* [ ] Async job queue
* [ ] Background workers
* [ ] Job IDs
* [ ] Job status API
* [ ] Cancellation
* [ ] Retry policies
* [ ] Exponential backoff
* [ ] Dead-letter queue
* [ ] Persistent execution state

---

## Phase 4 — Persistence

Planned:

* [ ] PostgreSQL
* [ ] User sessions
* [ ] Conversation history
* [ ] Task history
* [ ] Agent execution records
* [ ] Artifact metadata
* [ ] Audit events

---

## Phase 5 — Production Reliability

Planned:

* [ ] Authentication
* [ ] Authorization
* [ ] Rate limiting
* [ ] Request IDs
* [ ] Structured logging
* [ ] Metrics
* [ ] Distributed tracing
* [ ] Circuit breakers
* [ ] Service-level timeouts
* [ ] Resource limits
* [ ] Failure recovery

---

## Phase 6 — Agent Intelligence

Planned:

* [ ] LLM-based intent classification
* [ ] Capability-based routing
* [ ] Dynamic planning
* [ ] Multi-agent task decomposition
* [ ] Agent selection based on capabilities
* [ ] Tool selection
* [ ] Result verification
* [ ] Agent fallback
* [ ] Human approval for sensitive operations

---

## Phase 7 — Memory

Planned:

* [ ] Short-term memory
* [ ] Long-term memory
* [ ] Semantic search
* [ ] Vector database
* [ ] Project memory
* [ ] User preferences
* [ ] Task memory

---

## Phase 8 — User Interface

Planned:

* [ ] Web dashboard
* [ ] Task console
* [ ] Agent status
* [ ] Job monitoring
* [ ] Logs
* [ ] Artifacts
* [ ] Workspace browser
* [ ] Configuration management

---

# Long-Running Tasks

The current architecture uses synchronous HTTP execution for the basic execution path.

This is sufficient for:

```text
short requests
health checks
simple commands
basic agent tasks
integration tests
```

It should not be treated as the final architecture for tasks that may take many minutes.

The planned architecture is:

```text
POST /chat
     ↓
Gateway
     ↓
Create Job
     ↓
Redis / Queue
     ↓
Worker
     ↓
Agent
     ↓
Ollama
     ↓
Persist Result
```

The client can then query:

```text
GET /jobs/{job_id}
```

instead of holding an HTTP connection open for the entire task.

---

# Security

AI-OS agents can potentially execute powerful operations.

Especially:

* Open Interpreter
* Browser automation
* Software engineering agents
* Autonomous agents

Therefore the production architecture should introduce:

```text
Authentication
      ↓
Authorization
      ↓
Policy Engine
      ↓
Sandbox
      ↓
Agent
```

Potential controls include:

* Workspace restrictions
* Command allowlists
* Filesystem isolation
* Network restrictions
* Process limits
* Container isolation
* Human approval
* Secrets isolation

The local development configuration should not automatically be exposed to the public internet.

---

# Design Principles

AI-OS follows several architectural principles.

### 1. Local First

Prefer local models and local execution whenever practical.

### 2. Modular Agents

Each agent should be independently replaceable.

### 3. Unified Contract

All services should expose predictable APIs.

### 4. Centralized Configuration

Defaults should be defined once.

### 5. Service Overrides

Individual agents can override defaults when necessary.

### 6. Capability-Based Routing

The Gateway should eventually route based on capabilities rather than fragile keyword rules.

### 7. Fault Isolation

Failure of one agent should not crash the Gateway.

### 8. Observable Execution

Every task should eventually have:

* Request ID
* Job ID
* Agent
* Status
* Logs
* Result
* Artifacts
* Duration

---

# Future Architecture

The long-term architecture is intended to evolve from:

```text
Gateway
   ↓
Keyword Classifier
   ↓
Fixed Agent
```

toward:

```text
                         ┌──────────────┐
                         │    User      │
                         └──────┬───────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ AI-OS Gateway   │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Intent + Goal   │
                       │ Understanding   │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Task Planner    │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Capability      │
                       │ Registry        │
                       └────────┬────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                    ▼           ▼           ▼
                Agent A      Agent B     Agent C
                    │           │           │
                    └───────────┼───────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Verification    │
                       │ + Recovery      │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Result +        │
                       │ Artifacts       │
                       └─────────────────┘
```

---

# Why AI-OS?

Existing AI agents are often optimized for a particular capability.

AI-OS attempts to combine them into a single programmable execution layer.

Instead of asking:

> Which agent should I use?

the user asks:

> What do I want the computer to accomplish?

AI-OS determines how the request should be executed.

---

# Project Goals

The long-term goal is to build a local AI operating layer capable of coordinating:

```text
Software Engineering
        +
Browser Automation
        +
Computer Control
        +
Research
        +
Multi-Agent Workflows
        +
Planning
        +
Memory
        +
Verification
```

through one unified interface.

---

# Status

**Current milestone: Multi-Agent Orchestration Foundation**

```text
Gateway                    ✅
Service Registry           ✅
Intent Routing             ✅
Planner                    ✅
Dispatcher                 ✅
Ollama Integration         ✅
Open Interpreter           ✅
Browser Use                ✅
OpenHands                  ✅
CrewAI                     ✅
AutoGPT                    ✅
Health Monitoring          ✅
E2E Routing Verification   ✅
Async Job System           🚧
Persistence                🚧
Authentication             🚧
Sandboxing                 🚧
Observability              🚧
Web Dashboard              🚧
Long-Term Memory           🚧
```

---

# License

Add the project's chosen license here before publishing.

For example:

```text
MIT License
```

if the project is intended to be released under MIT.

---

# Author

**Muzan Siddig**

GitHub:

https://github.com/muzansiddig

Project:

https://github.com/muzansiddig/AI-OS

---

# Disclaimer

AI-OS is an experimental software project.

Agent capabilities depend on the underlying agent framework, model, tools, operating system, permissions, and local hardware.

Do not give autonomous agents unrestricted access to sensitive systems or data without appropriate isolation and authorization.

---

## Documentation

Ollama documentation:

https://docs.ollama.com/

Ollama API:

https://docs.ollama.com/api/introduction

OpenAI-compatible Ollama API:

https://docs.ollama.com/api/openai-compatibility
