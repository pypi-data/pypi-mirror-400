"""
Tests for AgentRegistry
"""
import pytest
import yaml
from axis_registry.agent_registry import AgentRegistry


def test_agent_registry_load_yml(tmp_path):
    # Setup mock data
    agent_dir = tmp_path / "agents"
    agent_dir.mkdir()

    agent_data = {
        "id": "test_agent",
        "role": "tester",
        "tier": "L1",
        "activation_policy": "always",
        "model": "gpt-4",
        "provider": "openai",
        "budget": {"token_budget": 1000, "cost_multiplier": 1.0},
        "capabilities": ["test"],
        "strengths": ["test"],
        "weaknesses": ["none"],
        "family": "alpha",
        "description": "test agent",
        "system_prompt": "you are a tester",
    }

    yml_file = agent_dir / "test_agent.yml"
    with open(yml_file, "w") as f:
        yaml.dump(agent_data, f)

    registry = AgentRegistry(search_paths=[agent_dir])

    assert "test_agent" in [a.id for a in registry.list_agents()]
    agent = registry.get_agent("test_agent")
    assert agent.role == "tester"
    assert agent.schema_version == "1.0.0"


def test_agent_registry_load_md_frontmatter(tmp_path):
    agent_dir = tmp_path / "workflows"
    agent_dir.mkdir()

    content = """---
id: workflow_agent
role: architect
tier: L2
activation_policy: semantic
model: claud-3
provider: anthropic
budget: {token_budget: 5000, cost_multiplier: 1.2}
capabilities: [design]
strengths: [system thinking]
weaknesses: [details]
family: beta
description: workflow agent
system_prompt: plan the system
---
# Workflow Content
Does not matter for the registry.
"""

    md_file = agent_dir / "workflow.md"
    with open(md_file, "w") as f:
        f.write(content)

    registry = AgentRegistry(search_paths=[agent_dir])

    agent = registry.get_agent("workflow_agent")
    assert agent.role == "architect"
    assert agent.tier == "L2"


def test_agent_registry_not_found():
    registry = AgentRegistry(search_paths=[])
    with pytest.raises(ValueError, match="Agent not found"):
        registry.get_agent("ghost")


def test_agent_registry_recursive_scan(tmp_path):
    # Setup nested structure
    root_dir = tmp_path / "agents"
    sub_dir = root_dir / "tier1" / "active"
    sub_dir.mkdir(parents=True)

    agent_data = {
        "id": "nested_agent",
        "role": "scout",
        "tier": "L0",
        "activation_policy": "semantic",
        "model": "gpt-3.5",
        "provider": "openai",
        "budget": {"token_budget": 500, "cost_multiplier": 1.0},
        "capabilities": [],
        "strengths": [],
        "weaknesses": [],
        "family": "scout",
        "description": "nested",
        "system_prompt": "scout",
    }

    with open(sub_dir / "agent.yml", "w") as f:
        yaml.dump(agent_data, f)

    registry = AgentRegistry(search_paths=[root_dir])
    assert "nested_agent" in [a.id for a in registry.list_agents()]


def test_agent_registry_invalid_yaml(tmp_path):
    root_dir = tmp_path / "invalid"
    root_dir.mkdir()

    with open(root_dir / "bad.yml", "w") as f:
        f.write("this: is: not: valid: yaml: - [")

    registry = AgentRegistry(search_paths=[root_dir])
    assert len(registry.list_agents()) == 0
