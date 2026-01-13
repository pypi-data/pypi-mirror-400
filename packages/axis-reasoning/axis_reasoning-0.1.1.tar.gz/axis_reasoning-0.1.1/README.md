# AXIS Reasoning

**Version:** 0.1.1
**Status:** Initial Structure (Code Migration Pending)
**License:** Proprietary - Enterprise Antigravity Labs

⚠️ **PRIVATE REPOSITORY** - Internal use only

## Purpose

The `axis-reasoning` contains the **internal reasoning and orchestration logic** for AXIS. This is a private repository containing proprietary algorithms and multi-agent coordination strategies.

### ✅ Responsibilities
- Agent orchestration and routing
- Model selection and optimization
- Execution engine for multi-agent workflows
- Governance enforcement
- Telemetry collection and analysis

### ❌ Excluded
- Public-facing protocols (handled by `axis-sdk`)
- Agent/skill discovery (handled by `axis-registry`)

## Installation

**Internal team only:**

```bash
# Requires GitHub authentication for private repo
pip install git+https://github.com/emilyveigaai/axis-reasoning.git
```

**For development:**

```bash
git clone https://github.com/emilyveigaai/axis-reasoning.git
cd axis-reasoning
pip install -e ".[dev]"
```

## Dependencies

- `axis-sdk>=0.3.0` - Protocol definitions
- `axis-registry>=0.1.0` - Agent/skill discovery
- `google-genai>=1.56.0` - Gemini API
- `anthropic>=0.39.0` - Claude API
- `sqlalchemy>=2.0.0` - Database ORM

## Migration Status

### ✅ Completed (Fase 2.1)
- pyproject.toml with all dependencies
- GitHub workflows (test.yml, publish.yml)
- Basic package structure

### 🚧 Pending (Fase 2.2)
- Migrate core modules from `antigravity/orchestrator/`:
  - `engine.py` → `axis_reasoning/engine.py`
  - `executor.py` → `axis_reasoning/executor.py`
  - `model_selector.py` → `axis_reasoning/model_selector.py`
- Migrate telemetry modules
- Migrate governance modules
- Update all imports to use `axis-sdk` protocols

## Development

### Install Dev Dependencies
```bash
pip install -e ".[dev]"
```

### Run Tests
```bash
pytest
```

### Run Linter
```bash
ruff check axis_reasoning
```

### Run Type Checker
```bash
mypy axis_reasoning
```

## Security

⚠️ **CRITICAL:** This repository contains proprietary logic. Do NOT:
- Share code publicly
- Commit API keys or credentials
- Expose internal algorithms

## Links

- **GitHub (Private):** https://github.com/emilyveigaai/axis-reasoning
- **Issues:** https://github.com/emilyveigaai/axis-reasoning/issues
- **Main Project:** https://github.com/emilyveigaai/AXIS

---

**Part of AXIS Migration Project**
Separated from monorepo: https://github.com/emilyveigaai/AXIS
