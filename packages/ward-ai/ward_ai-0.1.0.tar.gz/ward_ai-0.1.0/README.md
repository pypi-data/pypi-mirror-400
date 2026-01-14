# Ward - The Universal Safety Layer for AI Agents

> Your AI's safety net — Universal sandbox protection for any AI agent on any platform.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Windows Support](https://img.shields.io/badge/Windows-Supported-brightgreen.svg)](https://www.microsoft.com/windows)
[![Cross Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg)](https://github.com/nashihamm/ward)

## 🚀 Quick Start

### Installation

```bash
pip install ward-ai
```

### Universal AI Agent Protection

Ward works as a CLI wrapper around any AI agent command:

```bash
# Protect Claude Desktop
ward run "claude code 'Fix the login bug'"

# Protect Ollama
ward run "ollama run codellama 'Refactor this function'"

# Protect any Python AI agent
ward run "python my_agent.py --task 'Add tests'"

# Protect shell commands
ward run "npm run build"
```

### Quick Commands

```bash
# Start a protected session
ward start "Fix payment processing bug"

# Check what's happening
ward status

# Approve changes (promote to main codebase)
ward approve

# Emergency stop
ward kill
```

## The Problem

AI agents are powerful but dangerous:
- **No isolation** — AI writes directly to your files
- **Platform limitations** — Anthropic's sandbox only works on Mac/Linux  
- **No universal protection** — Each AI tool has different safety mechanisms
- **Windows gap** — 60% of developers use Windows but lack AI sandbox protection

## The Solution

Ward is the universal safety layer that works with ANY AI agent on ANY platform:

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐     ┌────────────┐
│   Any AI    │────▶│  Ward Wrapper    │────▶│  Container  │────▶│ Validation │
│   Agent     │     │   (CLI Layer)    │     │ Sandbox     │     │    Gate    │
└─────────────┘     └──────────────────┘     └─────────────┘     └────────────┘
                                                                        │
                    ┌──────────────────┐     ┌─────────────┐            │
                    │   Main Codebase  │◀────│   Promote   │◀───────────┘
                    │   (Protected)    │     │  (if safe)  │     
                    └──────────────────┘     └─────────────┘
```

### 🎯 Key Differentiators

**vs. Native Solutions**: Works on Windows (Docker/venv fallback)  
**vs. Vibe Kanban**: We focus on Security, they focus on Speed  
**vs. Ralph**: Ralph manages workflows, Ward provides safety brakes

## ✨ Features

### 🛡️ **Universal Protection**
- **Any AI Agent**: Claude, Ollama, OpenAI, custom Python agents
- **Any Platform**: Windows (Docker/venv), macOS (native), Linux (native)
- **Any Command**: Wrap shell commands, scripts, or AI tools
- **Container Isolation**: Docker-first with intelligent fallbacks

### � **AWindows-First Design**
- **Docker Desktop Integration**: Seamless Windows container support
- **Fallback Modes**: Python venv + tempfile when Docker unavailable
- **Path Handling**: Robust Windows path resolution and security
- **Performance Optimized**: Fast file sync and minimal overhead

### 🤖 **AI Integration**
- **CLI Wrapper**: `ward run "any command here"`
- **Session Management**: Track and control AI work sessions
- **Real-time Monitoring**: See what AI is doing in real-time
- **Emergency Controls**: `ward kill` for immediate shutdown

### �  **Enterprise Ready**
- **Audit Logging**: Complete trail of all AI actions
- **Validation Pipeline**: Syntax, tests, security, scope checks
- **Modular Architecture**: Plugin system for custom validators
- **Open Core Model**: Free core + enterprise plugins

## 📖 Usage Examples

### Universal Command Wrapping

```bash
# Protect any AI agent
ward run "claude code 'Fix the authentication system'"
ward run "ollama run codellama 'Add comprehensive tests'"
ward run "python my_agent.py --task 'Refactor for performance'"

# Protect development commands
ward run "npm run build"
ward run "python manage.py migrate"
ward run "cargo build --release"

# Stream output in real-time
ward run --stream "pytest tests/ -v"
```

### Session Management

```bash
# Start a protected session for AI work
ward start "Implement user authentication"

# Check what's happening
ward status

# Approve changes (promote to main codebase)
ward approve

# Emergency stop everything
ward kill --all
```

### Platform-Specific Features

```bash
# Force Docker isolation (Windows/macOS/Linux)
ward run --isolation docker "python train_model.py"

# Use venv fallback (when Docker unavailable)
ward run --isolation venv "pip install -r requirements.txt"

# Auto-detect best method (default)
ward run "make test"
```

## 🔧 Configuration

### Basic Configuration

```python
from ward import SandboxConfig, AutonomyLevel, ValidationMode

config = SandboxConfig(
    main_codebase="/path/to/your/project",
    autonomy_level=AutonomyLevel.VALIDATED,  # supervised, validated, autonomous
    validation_mode=ValidationMode.STRICT,   # strict, permissive, audit_only
    max_files_per_session=50,
    max_lines_changed=2000,
    session_timeout_minutes=120
)
```

### Windows-Specific Setup

```bash
# Install Docker Desktop (recommended)
# Download from: https://www.docker.com/products/docker-desktop

# Verify Docker is running
docker --version

# Install Ward
pip install ward-ai

# Test Ward with Docker
ward run "echo 'Hello from Ward on Windows!'"
```

### Enterprise Configuration

```python
# Enterprise features (coming soon)
config = SandboxConfig(
    # ... basic config ...
    audit_logging=True,
    remote_execution=True,
    team_permissions=True,
    compliance_mode="SOC2"
)
```

## 🏗️ Architecture

### Universal Wrapper Design

```
┌─────────────────┐
│   ward run      │  ← CLI Command
│   "any command" │
└─────────┬───────┘
          │
┌─────────▼───────┐
│ Universal       │  ← Command Parser & Router
│ Wrapper         │
└─────────┬───────┘
          │
    ┌─────▼─────┐
    │ Platform  │  ← Windows/macOS/Linux Detection
    │ Detection │
    └─────┬─────┘
          │
┌─────────▼───────┐
│ Isolation       │  ← Docker → venv → native
│ Method          │
└─────────┬───────┘
          │
┌─────────▼───────┐
│ Sandbox         │  ← Container/venv/directory
│ Environment     │
└─────────┬───────┘
          │
┌─────────▼───────┐
│ Command         │  ← Execute with monitoring
│ Execution       │
└─────────┬───────┘
          │
┌─────────▼───────┐
│ Validation      │  ← Syntax, tests, security
│ Pipeline        │
└─────────┬───────┘
          │
┌─────────▼───────┐
│ Approval        │  ← Manual or auto-promote
│ Gate            │
└─────────────────┘
```

### Windows Integration

Ward provides first-class Windows support through:

1. **Docker Desktop Integration**: Seamless Windows container support
2. **Intelligent Fallbacks**: Python venv when Docker unavailable  
3. **Path Handling**: Robust Windows path resolution and security
4. **Performance**: Optimized file sync and minimal overhead

## 🚀 Advanced Usage

### Custom Validators

```python
from ward.validators import BaseValidator, ValidationResult

class MyCustomValidator(BaseValidator):
    async def validate(self, changes: list[FileChange]) -> ValidationResult:
        # Your custom validation logic
        return ValidationResult(
            passed=True,
            message="Custom validation passed",
            details={}
        )

# Register validator
ward.add_validator(MyCustomValidator())
```

### Programmatic Usage

```python
import asyncio
from ward import get_wrapper, SandboxConfig

async def main():
    config = SandboxConfig(main_codebase="./my-project")
    wrapper = await get_wrapper(config)
    
    # Execute command safely
    result = await wrapper.wrap_command("python train.py")
    
    if result.validation_passed:
        await wrapper.approve_session(result.session_id)
    else:
        print("Validation failed:", result.validation_results)

asyncio.run(main())
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Run tests with Ward protection
  run: |
    pip install ward-ai
    ward run "pytest tests/ --cov=src/"
    ward approve  # Auto-approve if tests pass
```

## 🔒 Security Features

### Isolation Levels

- **Container Isolation**: Full OS-level isolation via Docker
- **Process Isolation**: Python venv with restricted filesystem access
- **Network Isolation**: No network access by default in containers
- **Resource Limits**: CPU, memory, and disk usage constraints

### Validation Pipeline

- **Syntax Validation**: AST parsing for code correctness
- **Test Validation**: Automated test execution
- **Security Scanning**: Detect secrets, vulnerabilities
- **Scope Validation**: Ensure changes within allowed paths
- **Custom Rules**: Project-specific validation logic

### Audit Trail

```bash
# View complete audit log
ward report --output audit.json

# Session-specific logs
ward status --session abc123 --verbose
```

## 🔧 Development

### Installation from Source

```bash
git clone https://github.com/nashihamm/ward.git
cd ward
pip install -e .
```

### Running Tests

```bash
pytest tests/ -v --cov=ward
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Requirements

- Python 3.10+
- Docker Desktop (recommended for Windows)
- Git (for worktree sandbox mode)

### Platform Support

| Platform | Docker | Venv Fallback | Status |
|----------|--------|---------------|--------|
| Windows 10/11 | ✅ Docker Desktop | ✅ Python venv | Full Support |
| macOS | ✅ Docker Desktop | ✅ Python venv | Full Support |
| Linux | ✅ Docker Engine | ✅ Python venv | Full Support |

## 🤝 Contributing

Ward is open source and welcomes contributions! We're especially interested in:

- Windows-specific improvements and testing
- Additional AI agent integrations
- Custom validator implementations
- Performance optimizations
- Documentation improvements

## � Liccense

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Docker](https://docker.com) for containerization technology
- [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol) for AI tool integration
- [Claude](https://claude.ai) and [Ollama](https://ollama.ai) for inspiring AI agent safety
- The open source community for amazing Python libraries

## 📞 Support & Community

- 📧 **Email**: nashihamm@outlook.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/nashihamm/ward/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/nashihamm/ward/discussions)
- 📖 **Documentation**: [Ward Docs](https://github.com/nashihamm/ward#readme)

## 🚀 Roadmap

### Phase 1: Universal Core (Current)
- ✅ CLI wrapper for any command
- ✅ Windows Docker Desktop integration
- ✅ Venv fallback isolation
- ✅ Basic validation pipeline

### Phase 2: AI Agent Integration
- 🔄 Enhanced Claude Desktop integration
- 🔄 Native Ollama support
- 🔄 OpenAI API integration
- 🔄 Custom agent templates

### Phase 3: Enterprise Features
- 📋 Team management and permissions
- 📋 Centralized audit logging
- 📋 Remote cloud execution
- 📋 Compliance frameworks (SOC2, GDPR)

### Phase 4: Ecosystem
- 📋 VS Code extension
- 📋 Plugin marketplace
- 📋 Community validators
- 📋 Integration templates

---

**Ward - Because every AI agent needs a safety net. 🛡️**

*Made with ❤️ for safer AI development on every platform*