# Flotorch Python

A modular Python framework for AI agents and LLM interactions with support for multiple AI frameworks.

## Features

- **Modular Design**: Install only what you need
- **SDK Core**: Foundation for all AI interactions with LLM, Memory, Session, and Vector Store support
- **Multi-Framework Support**: Seamless integration with popular AI frameworks
  - **ADK**: Google Agent Development Kit integration
  - **CrewAI**: Full CrewAI framework support with agents, tasks, and memory
  - **AutoGen**: Microsoft AutoGen integration with agents and memory
  - **LangChain**: LangChain-compatible LLM, agents, memory, and sessions
  - **LangGraph**: LangGraph agent support with checkpointing and memory stores
  - **Strands**: Strands Agents framework integration
- **Flexible Dependencies**: Choose your installation level
- **Built-in Logging**: Configurable logging system with console and file providers
- **Session Management**: Persistent session state management
- **Memory & Vector Stores**: Long-term memory storage with vector search capabilities

## Installation

### Option 1: Install everything 
```bash
# Install all modules and dependencies
pip install flotorch[all]
```

### Option 2: Install specific modules only
```bash
# Install only SDK (core functionality)
pip install flotorch[sdk]

# Install SDK + ADK (Google Agent Development Kit) (Recommended)
pip install flotorch[adk]

# Install SDK + CrewAI (Recommended)
pip install flotorch[crewai]

# Install SDK + AutoGen
pip install flotorch[autogen]

# Install SDK + LangChain
pip install flotorch[langchain]

# Install SDK + LangGraph (includes LangChain)
pip install flotorch[langgraph]

# Install SDK + Strands
pip install flotorch[strands]

# Install multiple modules
pip install flotorch[adk,crewai,langchain]
```

### Option 3: Development installation
```bash
# Install in development mode with all dependencies
pip install -e .

# Install with development tools
pip install -e .[dev]
```

### Option 4: Beta/Pre-release installation
```bash
# Install latest beta version
pip install --pre flotorch

# Install specific beta version
pip install --pre flotorch==2.6.1b1

# Install beta with specific modules
pip install --pre flotorch[adk]
pip install --pre flotorch[crewai]
pip install --pre flotorch[autogen]
pip install --pre flotorch[langchain]
pip install --pre flotorch[langgraph]
pip install --pre flotorch[strands]

# Install specific beta version with modules
pip install --pre flotorch[adk]==2.6.1b1
pip install --pre flotorch[all]==2.6.1b1
```

**Note**: The `--pre` flag is required to install beta/pre-release versions. Without it, pip will only install stable releases.

## Configuration

### Environment Variables

Flotorch uses environment variables for configuration. You can set these in your `.env` file or as environment variables:

```bash
# Required for most operations
FLOTORCH_API_KEY=your-api-key-here
FLOTORCH_BASE_URL=https://api.flotorch.com

# Optional: Enable debug logging
FLOTORCH_DEBUG=true
```

### SDK Components

The core SDK provides the following components:

- **FlotorchLLM**: LLM client for making API calls to various language models
- **FlotorchSession**: Session management for maintaining conversation state
- **FlotorchMemory**: Long-term memory storage with vector search support
- **FlotorchVectorStore**: Vector store operations for semantic search
- **Logging System**: Configurable logging with console and file providers

## Module Dependencies

### SDK (Core) - Always included
- `httpx>=0.24` - HTTP client
- `pydantic>=1.10` - Data validation

### ADK Module
- **Requires**: SDK dependencies
- **Adds**: 
  - `google-adk>=1.5.0`
  - `python-dotenv>=1.0.0`
  - `opentelemetry-exporter-otlp-proto-grpc>=1.34.0`

### CrewAI Module
- **Requires**: SDK dependencies
- **Adds**:
  - `crewai==0.193.2`
  - `crewai-tools==0.73.1`
  - `crewai-tools[mcp]==0.73.1`
  - `python-dotenv>=1.0.0`

### AutoGen Module
- **Requires**: SDK dependencies
- **Adds**:
  - `python-dotenv>=1.0.0`
  - `autogen-core>=0.4.0`
  - `autogen-agentchat>=0.4.0`
  - `autogen-ext[openai]>=0.4.0`
  - `openai>=1.0.0`
  - `mcp>=1.2.0`

### LangChain Module
- **Requires**: SDK dependencies
- **Adds**:
  - `langchain>=0.3.27`
  - `langchain-openai>=0.2.14`
  - `langchain-experimental>=0.3.4`
  - `langchain-community>=0.3.29`
  - `langgraph>=0.6.6`
  - `langchain-mcp-tools>=0.2.13`
  - `langchain-mcp-adapters>=0.1.9`
  - `langchain-mcp>=0.2.1`

### LangGraph Module
- **Requires**: SDK and LangChain dependencies
- **Adds**:
  - `langgraph>=0.6.6`
  - `langgraph-checkpoint>=2.1.1`
  - `langgraph-prebuilt>=0.6.4`
  - `langgraph-sdk>=0.2.3`
  - `langchain-core>=0.2.14`
  - `langchain-community>=0.3.27`
  - `langchain-openai>=0.3.30`
  - `langchain-mcp-adapters>=0.1.9`
  - `mcp>=1.13.1`

### Strands Module
- **Requires**: SDK dependencies
- **Adds**:
  - `strands-agents==1.9.0`

### Development Tools
- `build>=0.10.0` - Package building
- `twine>=4.0.0` - PyPI upload
- `pytest>=7.0.0` - Testing
- `pytest-cov>=4.0.0` - Test coverage
- `black>=23.0.0` - Code formatting
- `flake8>=6.0.0` - Linting
- `mypy>=1.0.0` - Type checking

## Quick Start

### SDK (Core)
```python
from flotorch.sdk.llm import FlotorchLLM
from flotorch.sdk.session import FlotorchSession
from flotorch.sdk.memory import FlotorchMemory

# Initialize LLM
llm = FlotorchLLM(
    model_id="gpt-4",
    api_key="your-api-key",
    base_url="https://api.flotorch.com"
)

# Use LLM
response = llm.invoke([{"role": "user", "content": "Hello!"}])

# Initialize Session
session = FlotorchSession(
    api_key="your-api-key",
    base_url="https://api.flotorch.com"
)

# Create a session
session_data = session.create(
    app_name="my-app",
    user_id="user-123"
)

# Initialize Memory
memory = FlotorchMemory(
    api_key="your-api-key",
    base_url="https://api.flotorch.com",
    provider_name="my-provider"
)
```

### ADK Integration
```python
from flotorch.adk.agent import FlotorchADKAgent

agent = FlotorchADKAgent(
    agent_name="my-agent",
    enable_memory=True,
    base_url="https://api.flotorch.com",
    api_key="your-api-key"
)

adk_agent = agent.get_agent()
```

### CrewAI Integration
```python
from flotorch.crewai.agent import FlotorchCrewAIAgent

agent_manager = FlotorchCrewAIAgent(
    agent_name="my-crewai-agent",
    base_url="https://api.flotorch.com",
    api_key="your-api-key"
)

agent = agent_manager.get_agent()
task = agent_manager.get_task()
```

### AutoGen Integration
```python
from flotorch.autogen.agent import FlotorchAutogenAgent

agent = FlotorchAutogenAgent(
    agent_name="my-autogen-agent",
    base_url="https://api.flotorch.com",
    api_key="your-api-key"
)

autogen_agent = agent.get_agent()
```

### LangChain Integration
```python
from flotorch.langchain.agent import FlotorchLangChainAgent

agent = FlotorchLangChainAgent(
    agent_name="my-langchain-agent",
    enable_memory=True,
    base_url="https://api.flotorch.com",
    api_key="your-api-key"
)

langchain_agent = agent.get_agent()
```

### LangGraph Integration
```python
from flotorch.langgraph.agent import FlotorchLangGraphAgent

agent = FlotorchLangGraphAgent(
    agent_name="my-langgraph-agent",
    base_url="https://api.flotorch.com",
    api_key="your-api-key"
)

langgraph_agent = agent.get_agent()
```

### Strands Integration
```python
from flotorch.strands.llm import FlotorchStrandsModel

model = FlotorchStrandsModel(
    model_id="gpt-4",
    api_key="your-api-key",
    base_url="https://api.flotorch.com"
)
```

## Module Overview

### SDK (Core)
The foundation of Flotorch, providing:
- **FlotorchLLM**: Unified LLM interface supporting multiple providers
- **FlotorchSession**: Persistent session state management
- **FlotorchMemory**: Long-term memory storage with metadata support
- **FlotorchVectorStore**: Vector store for semantic search and RAG applications
- **Logging System**: Structured logging with multiple providers

### ADK Module
Google Agent Development Kit integration:
- **FlotorchADKAgent**: ADK-compatible agent with dynamic configuration
- **FlotorchADKLLM**: LLM wrapper for ADK framework
- **FlotorchADKSession**: Session service implementation
- **FlotorchADKVectorMemoryService**: Memory service with vector search

### CrewAI Module
CrewAI framework integration:
- **FlotorchCrewAIAgent**: Agent and task management from configuration
- **FlotorchCrewAILLM**: LLM integration for CrewAI agents
- **FlotorchCrewAISession**: Short-term storage using Flotorch Sessions
- **FlotorchMemoryStorage**: Long-term memory storage for CrewAI

### AutoGen Module
Microsoft AutoGen integration:
- **FlotorchAutogenAgent**: AutoGen agent with configuration management
- **FlotorchAutogenLLM**: Chat completion client for AutoGen
- **FlotorchAutogenSession**: Model context for conversation state
- **FlotorchAutogenMemory**: Memory integration with AutoGen framework

### LangChain Module
LangChain framework integration:
- **FlotorchLangChainAgent**: LangChain agent with MCP tool support
- **FlotorchLangChainLLM**: BaseChatModel implementation
- **FlotorchLangChainSession**: BaseMemory implementation for sessions
- **FlotorchLangChainMemory**: BaseMemory implementation for long-term storage

### LangGraph Module
LangGraph framework integration:
- **FlotorchLangGraphAgent**: LangGraph agent with checkpointing support
- **FlotorchLanggraphSession**: BaseCheckpointSaver implementation
- **FlotorchStore**: BaseStore implementation for memory operations

### Strands Module
Strands Agents framework integration:
- **FlotorchStrandsModel**: Model class with stream and structured output support

## Project Structure

```
flotorch/
├── __init__.py
├── sdk/                    # Core SDK functionality
│   ├── __init__.py
│   ├── llm.py              # FlotorchLLM - LLM client
│   ├── session.py          # FlotorchSession - Session management
│   ├── memory.py           # FlotorchMemory, FlotorchVectorStore
│   ├── logger/             # Logging system
│   │   ├── logger.py
│   │   ├── logger_provider.py
│   │   ├── console_logger_provider.py
│   │   ├── file_logger_provider.py
│   │   └── global_logger.py
│   └── utils/              # Shared utilities
│       ├── http_utils.py
│       ├── llm_utils.py
│       ├── memory_utils.py
│       ├── session_utils.py
│       └── validation_utils.py
├── adk/                    # Google Agent Development Kit
│   ├── __init__.py
│   ├── agent.py            # FlotorchADKAgent
│   ├── llm.py              # FlotorchADKLLM
│   ├── memory.py           # FlotorchADKVectorMemoryService
│   ├── sessions.py         # FlotorchADKSession
│   └── utils/
├── crewai/                 # CrewAI framework integration
│   ├── __init__.py
│   ├── agent.py            # FlotorchCrewAIAgent
│   ├── llm.py              # FlotorchCrewAILLM
│   ├── memory.py           # FlotorchMemoryStorage
│   └── sessions.py         # FlotorchCrewAISession
├── autogen/                # Microsoft AutoGen integration
│   ├── __init__.py
│   ├── agent.py            # FlotorchAutogenAgent
│   ├── llm.py              # FlotorchAutogenLLM
│   ├── memory.py           # FlotorchAutogenMemory
│   └── sessions.py         # FlotorchAutogenSession
├── langchain/              # LangChain framework integration
│   ├── __init__.py
│   ├── agent.py            # FlotorchLangChainAgent
│   ├── llm.py              # FlotorchLangChainLLM
│   ├── memory.py           # FlotorchLangChainMemory
│   └── session.py          # FlotorchLangChainSession
├── langgraph/              # LangGraph framework integration
│   ├── __init__.py
│   ├── agent.py            # FlotorchLangGraphAgent
│   ├── memory.py           # FlotorchStore
│   └── sessions.py         # FlotorchLanggraphSession
└── strands/                # Strands Agents integration
    ├── __init__.py
    ├── agent.py
    ├── llm.py              # FlotorchStrandsModel
    ├── memory.py
    └── session.py
```

## Development

### Easy Building with Makefile

The easiest way to build and manage your package is using the provided Makefile:

#### Direct Version Specification (Recommended)
```bash
# Build with specific version
make build VERSION=2.6.1
make build-beta VERSION=2.6.1b1
make build-prod VERSION=2.6.1

# Test with specific version
make test VERSION=2.6.1

# Publish with specific version
make publish-test VERSION=2.6.1b1
make publish-prod VERSION=2.6.1

# Full workflow with specific version
make all VERSION=2.6.1b1
```

#### Interactive Commands (prompts for version)
```bash
# Interactive builds (if no VERSION specified)
make build          # Prompts: "Enter version (e.g., 2.6.1):"
make build-beta     # Prompts: "Enter beta version (e.g., 2.6.1b1):"
make build-prod     # Prompts: "Enter production version (e.g., 2.6.1):"

# Interactive testing and publishing
make test           # Prompts: "Enter version to test (e.g., 2.6.1):"
make publish-test   # Prompts: "Enter version to publish (e.g., 2.6.1b1):"
make publish-prod   # Prompts: "Enter version to publish (e.g., 2.6.1):"
```

#### Quick Commands (pre-defined versions)
```bash
# Quick development builds
make quick-build        # Builds version 2.6.1
make quick-test         # Tests version 2.6.1
make quick-beta         # Builds version 2.6.1b1

# Quick publishing
make quick-publish-test # Publishes 2.6.1b1 to TestPyPI
make quick-publish      # Publishes 2.6.1 to PyPI
```

#### Development Setup
```bash
# Set up development environment
make install        # Install in development mode
make install-dev    # Install with development dependencies
make dev-setup      # Complete development setup and test

# Other useful commands
make help           # Show all available commands
make clean          # Clean build artifacts
```

### Testing
```bash
# Test specific module installations
python -c "from flotorch.sdk.llm import FlotorchLLM; print('SDK works!')"
python -c "from flotorch.adk.agent import FlotorchADKAgent; print('ADK works!')"
python -c "from flotorch.crewai.agent import FlotorchCrewAIAgent; print('CrewAI works!')"
python -c "from flotorch.autogen.agent import FlotorchAutogenAgent; print('AutoGen works!')"
python -c "from flotorch.langchain.agent import FlotorchLangChainAgent; print('LangChain works!')"
python -c "from flotorch.langgraph.agent import FlotorchLangGraphAgent; print('LangGraph works!')"
python -c "from flotorch.strands.llm import FlotorchStrandsModel; print('Strands works!')"
```

### Publishing
```bash
# Update version in pyproject.toml, then:
python -m build
twine upload dist/*  # For PyPI
twine upload --repository testpypi dist/*  # For TestPyPI
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/flotorch/flotorch-python/issues)
- **Documentation**: [docs.flotorch.com](https://docs.flotorch.com)
- **Discussions**: [GitHub Discussions](https://github.com/flotorch/flotorch-python/discussions)
