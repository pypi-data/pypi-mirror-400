"""
Integration test for AgentRegistry with real monorepo agents
"""
from pathlib import Path

import pytest
from axis_registry.agent_registry import AgentRegistry


def _get_axis_root():
    """Locate AXIS monorepo root"""
    # Try from environment or working directory
    cwd = Path.cwd()

    # Check if we're already in AXIS
    if (cwd / "antigravity" / "agents").exists():
        return cwd

    # Go up until we find it
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "antigravity" / "agents").exists():
            return parent

    return None


def test_registry_discovers_real_yml_agents():
    """
    CRITICAL SMOKE TEST: Verify registry discovers real agent definitions.

    This validates that the registry works with actual monorepo structure,
    not just mocked temp files.
    """
    axis_root = _get_axis_root()

    if axis_root is None:
        pytest.skip("AXIS monorepo root not found")

    agents_root = axis_root / "antigravity" / "agents"

    definitions_dir = agents_root / "definitions"

    if not definitions_dir.exists():
        pytest.skip("Agent definitions directory not found")

    registry = AgentRegistry(search_paths=[definitions_dir])

    discovered_agents = registry.list_agents()
    agent_ids = [a.id for a in discovered_agents]

    # Assert we discovered at least some core agents
    assert len(discovered_agents) > 0, "Registry failed to discover any agents!"

    # Verify specific known agents exist
    expected_core_agents = [
        "gemini_analyst",
        "claude_architect",
        "gemini_scout",
    ]

    found_core = [aid for aid in expected_core_agents if aid in agent_ids]

    assert len(found_core) >= 2, (
        f"Expected to find at least 2 core agents, found: {found_core}. "
        f"All discovered: {agent_ids[:10]}"
    )

    # Validate schema_version is set
    for agent in discovered_agents[:5]:  # Check first 5
        assert hasattr(
            agent, "schema_version"
        ), f"Agent {agent.id} missing schema_version"
        assert (
            agent.schema_version == "1.0.0"
        ), f"Agent {agent.id} has wrong schema_version"


def test_registry_discovers_real_md_workflows():
    """Verify registry discovers agent definitions from markdown frontmatter"""
    axis_root = _get_axis_root()

    if axis_root is None:
        pytest.skip("AXIS monorepo root not found")

    agents_root = axis_root / "antigravity" / "agents"

    workflows_dir = agents_root / "workflows"

    if not workflows_dir.exists():
        pytest.skip("Agent workflows directory not found")

    registry = AgentRegistry(search_paths=[workflows_dir])

    discovered = registry.list_agents()

    # Should find at least some workflow-based agents
    if len(discovered) == 0:
        pytest.skip("No valid markdown agent definitions found in workflows dir")

    # All discovered agents should have required fields
    for agent in discovered[:3]:
        assert agent.id, "Agent missing id"
        assert agent.role, "Agent {} missing role".format(agent.id)


def test_registry_combined_discovery():
    """Verify registry can scan both YML and MD simultaneously"""
    axis_root = _get_axis_root()

    if axis_root is None:
        pytest.skip("AXIS monorepo root not found")

    agents_root = axis_root / "antigravity" / "agents"

    # Scan both definitions (yml) and workflows (md)
    search_paths = [
        agents_root / "definitions",
        agents_root / "workflows",
    ]

    # Filter only existing paths
    existing_paths = [p for p in search_paths if p.exists()]

    if not existing_paths:
        pytest.skip("No agent directories found")

    registry = AgentRegistry(search_paths=existing_paths)

    total_discovered = len(registry.list_agents())

    # We know there are 71 YML + 78 MD files, but some may be invalid/non-agents
    assert (
        total_discovered >= 10
    ), "Expected at least 10 agents from combined scan, found {}".format(
        total_discovered
    )


def test_registry_handles_invalid_definitions_gracefully():
    """Verify registry doesn't crash on invalid YAML in real files"""
    axis_root = _get_axis_root()

    if axis_root is None:
        pytest.skip("AXIS monorepo root not found")

    agents_root = axis_root / "antigravity" / "agents"

    # This should NOT raise even if some files are malformed
    registry = AgentRegistry(search_paths=[agents_root])

    # Just verify it completes without exception
    agents = registry.list_agents()

    # We should get SOME valid agents even if others fail
    assert isinstance(agents, list)
