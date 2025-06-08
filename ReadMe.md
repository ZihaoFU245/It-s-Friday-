# We are making a Agent App which is called <i><b>It's Friday!😆</b></i>

## below is the Application Structure (more or less 😆)
```mermaid
flowchart TD
    A[It's Friday! App Structure] --> B(frontend/ Electron + React)
    B --> B1(components/)
    B1 --> B1a(Header.jsx - Mode switcher)
    B1 --> B1b(ModulePanel/ - Each module UI)
    B1 --> B1c(ChatInterface.jsx - Voice + text chat)
    B --> B2(services/ - HTTP API calls)
    B --> B3(app.tsx)

    A --> C(backend/ Python + FastAPI)
    C --> C1(main.py - HTTP server)
    C --> C2(modules/ Independent modules)
    C2 --> C2a(email.py)
    C2 --> C2b(calendar.py)
    C2 --> C2c(weather.py)
    C2 --> C2d(automation.py - App launch / Web scripts)
    C2 --> C2e(memory.py - Vector store / Retrieval)
    C --> C3(skills/ Modular skill interfaces MCP server)
    C3 --> C3a(skill_registry.py)
    C3 --> C3b(skill_invoker.py)
    C --> C4(config.py)

    A --> D(memory/ ChromaDB + embeddings)
    A --> E(tts_stt/ Whisper + ElevenLabs integration)
    A --> F(automation/ AutoGUI scripts)
    A --> G(README.md)

    %% New: LLM orchestrator is separate
    A --> H(llm_orchestrator/ Agent Engine)
    H --> H1(llm_api_client.py - call OpenAI, DeepSeek, Gemini)
    H --> H2(plan_executor.py - plan steps, invoke MCP skills)
    H --> H3(memory_interface.py - retrieve/store context)
    H --> C3(MCP Skill Server - skills/)
```

## Here is the workflow or the app
```mermaid
sequenceDiagram
    participant UI as User Interface
    participant LLM as LLM Orchestrator
    participant MCP as Skill Server (MCP)
    participant Backend as Backend Modules
    participant API as External APIs

    UI->>LLM: User says "Schedule meeting with John"
    LLM->>MCP: invoke(skill="create_calendar_event", params={...})
    MCP->>Backend: Call calendar.py with params
    Backend->>API: Call Google Calendar API
    API-->>Backend: Success / Data
    Backend-->>MCP: Return result
    MCP-->>LLM: Return result
    LLM->>UI: "Meeting scheduled!"
```

### <b> The project is under active development</b>
