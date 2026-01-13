# AXIS Registry

**Version:** 0.1.0
**Status:** Production Ready
**License:** MIT

## Purpose

The `axis-registry` is a **discovery service** for AXIS agents and skills. It provides dynamic agent loading and skill resolution.

### ✅ Features
- Agent discovery from YAML manifests
- Skill registry with semantic search
- Dynamic agent loading
- Dependency resolution
- Protocol validation (uses `axis-sdk`)

### ❌ Excluded
- Agent execution (handled by `axis-reasoning`)
- Orchestration logic (handled by `axis-reasoning`)
- Telemetry collection (handled by `axis-reasoning`)

## Installation

```bash
pip install axis-registry
```

**Dependencies:**
- `axis-sdk>=0.3.0` - Protocol definitions
- `pyyaml>=6.0.0` - YAML parsing

## Quick Start

```python
from axis_registry import AgentRegistry, SkillRegistry

# Initialize registries
agent_registry = AgentRegistry(config_path="config/agents.yml")
skill_registry = SkillRegistry(config_path="config/skills.yml")

# Discover agents
available_agents = agent_registry.list_agents()
print(f"Found {len(available_agents)} agents")

# Get specific agent
agent = agent_registry.get_agent("devops-specialist")
print(f"Agent: {agent.name} - {agent.description}")

# Find skills
skills = skill_registry.search("git operations")
print(f"Found {len(skills)} matching skills")
```

## API Reference

### AgentRegistry

```python
from axis_registry import AgentRegistry

registry = AgentRegistry(config_path="config/agents.yml")

# List all agents
agents = registry.list_agents()

# Get agent by ID
agent = registry.get_agent("agent-id")

# Search agents by capability
matches = registry.search(query="python development")

# Validate agent against protocol
is_valid = registry.validate_agent(agent_instance)
```

### SkillRegistry

```python
from axis_registry import SkillRegistry

registry = SkillRegistry(config_path="config/skills.yml")

# List all skills
skills = registry.list_skills()

# Get skill by ID
skill = registry.get_skill("skill-id")

# Search skills semantically
matches = registry.search(query="database migration")
```

## Configuration

### Agent Manifest (agents.yml)

```yaml
agents:
  - id: devops-specialist
    name: "DevOps Specialist"
    description: "Handles CI/CD and deployment"
    capabilities:
      - git-operations
      - docker-deployment
      - kubernetes-management
    protocols:
      - AgentProtocol
      - TelemetryProtocol
```

### Skill Manifest (skills.yml)

```yaml
skills:
  - id: git-push
    name: "Git Push"
    description: "Push changes to remote repository"
    category: version-control
    required_agent: devops-specialist
```

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
ruff check axis_registry
```

### Run Type Checker
```bash
mypy axis_registry
```

## License

MIT License - See [LICENSE](LICENSE) file.

## Links

- **GitHub:** https://github.com/emilyveigaai/axis-registry
- **PyPI:** https://pypi.org/project/axis-registry/
- **Issues:** https://github.com/emilyveigaai/axis-registry/issues
- **Documentation:** https://github.com/emilyveigaai/axis-registry#readme

---

**Part of AXIS Migration Project**
Separated from monorepo: https://github.com/emilyveigaai/AXIS
