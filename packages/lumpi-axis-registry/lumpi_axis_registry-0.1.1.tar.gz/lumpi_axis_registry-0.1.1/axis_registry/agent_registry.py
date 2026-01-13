"""
Agent Registry Implementation
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from axis_sdk.protocols.reasoning import AgentRegistryProtocol
from axis_sdk.types.agent import AgentDefinition

logger = logging.getLogger(__name__)


class AgentRegistry(AgentRegistryProtocol):
    """
    Registry for discovering and loading agent definitions from the filesystem.
    """

    def __init__(self, search_paths: List[Path]):
        self.search_paths = search_paths
        self._agents: Dict[str, AgentDefinition] = {}
        self.refresh()

    def refresh(self) -> None:
        """
        Scan search paths for agent definitions.
        Supports .yml files and .md files with YAML frontmatter.
        """
        new_agents = {}
        for path in self.search_paths:
            if not path.exists():
                logger.warning(f"Search path does not exist: {path}")
                continue

            # Scan recursively for .yml and .md files
            for file_path in path.rglob("*"):
                if file_path.suffix in [".yml", ".yaml"]:
                    agent = self._load_yml(file_path)
                    if agent:
                        new_agents[agent.id] = agent
                elif file_path.suffix == ".md":
                    agent = self._load_md_frontmatter(file_path)
                    if agent:
                        new_agents[agent.id] = agent

        self._agents = new_agents
        logger.info(f"Registry refreshed: {len(self._agents)} agents loaded.")

    def get_agent(self, agent_id: str) -> AgentDefinition:
        """Retrieve agent definition by ID."""
        if agent_id not in self._agents:
            raise ValueError(f"Agent not found: {agent_id}")
        return self._agents[agent_id]

    def list_agents(self) -> List[AgentDefinition]:
        """List all available agent definitions."""
        return list(self._agents.values())

    def _load_yml(self, file_path: Path) -> Optional[AgentDefinition]:
        """Load agent from a YAML file."""
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
                if not data or not isinstance(data, dict):
                    return None
                # Basic check if it's an agent definition (looking for 'id' and 'role')
                if "id" in data and "role" in data:
                    return AgentDefinition(**data)
        except Exception as e:
            logger.error(f"Error loading agent from {file_path}: {e}")
        return None

    def _load_md_frontmatter(self, file_path: Path) -> Optional[AgentDefinition]:
        """Load agent from Markdown frontmatter."""
        try:
            with open(file_path, "r") as f:
                content = f.read()
                if not content.startswith("---"):
                    return None

                parts = content.split("---")
                if len(parts) < 3:
                    return None

                frontmatter = parts[1]
                data = yaml.safe_load(frontmatter)
                if not data or not isinstance(data, dict):
                    return None

                # Basic check
                if "id" in data and "role" in data:
                    return AgentDefinition(**data)
        except Exception as e:
            logger.error(f"Error loading agent from {file_path}: {e}")
        return None
