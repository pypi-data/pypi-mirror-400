"""
Skill Registry Implementation
"""
import importlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from axis_sdk.protocols.reasoning import SkillRegistryProtocol
from axis_sdk.protocols.skills import SkillProtocol
from axis_sdk.types.agent import SkillDefinition

logger = logging.getLogger(__name__)


class SkillRegistry(SkillRegistryProtocol):
    """
    Registry for discovering and loading skill implementations securely.
    """

    def __init__(self, definition_paths: List[Path], allowlist: Dict[str, str]):
        """
        Args:
            definition_paths: Paths to look for .yml skill definitions.
            allowlist: Mapping of skill_id to full python module path.
                       Example: {"math": "antigravity.skills.impl.math"}
        """
        self.definition_paths = definition_paths
        self.allowlist = allowlist
        self._definitions: Dict[str, SkillDefinition] = {}
        self._cache: Dict[str, SkillProtocol] = {}
        self.refresh()

    def refresh(self) -> None:
        """Scan paths for skill definitions."""
        new_defs = {}
        for path in self.definition_paths:
            if not path.exists():
                continue

            for file_path in path.rglob("*.yml"):
                skill_def = self._load_definition(file_path)
                if skill_def:
                    new_defs[skill_def.id] = skill_def

        self._definitions = new_defs
        logger.info(
            f"Skill registry refreshed: {len(self._definitions)} definitions loaded."
        )

    def get_skill(self, skill_id: str) -> SkillProtocol:
        """
        Retrieve skill implementation by ID.
        Lazy loads and caches implementation.
        """
        if skill_id in self._cache:
            return self._cache[skill_id]

        if skill_id not in self.allowlist:
            raise PermissionError(
                f"Skill implementation not authorized in allowlist: {skill_id}"
            )

        module_path = self.allowlist[skill_id]
        try:
            module = importlib.import_module(module_path)
            # Strategy 1: Look for 'execute' function (Minimal implementation)
            if hasattr(module, "execute") and callable(module.execute):
                # Wrap it in a class that matches SkillProtocol if it's just a function
                class SkillWrapper(SkillProtocol):
                    def execute(
                        self, params: Dict[str, Any], context: Dict[str, Any]
                    ) -> Dict[str, Any]:
                        return module.execute(params, context)

                impl = SkillWrapper()
                self._cache[skill_id] = impl
                return impl

            # Strategy 2: Look for 'Skill' class
            if hasattr(module, "Skill"):
                skill_class = getattr(module, "Skill")
                impl = skill_class()
                if isinstance(impl, SkillProtocol):
                    self._cache[skill_id] = impl
                    return impl

            raise ImportError(
                f"No valid SkillProtocol implementation found in {module_path}"
            )

        except Exception as e:
            logger.error(f"Failed to load skill {skill_id} from {module_path}: {e}")
            raise

    def list_skills(self) -> List[str]:
        """List all available skill IDs."""
        return list(self._definitions.keys())

    def _load_definition(self, file_path: Path) -> Optional[SkillDefinition]:
        """Load skill definition from YAML."""
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
                if data and isinstance(data, dict) and "id" in data and "name" in data:
                    return SkillDefinition(**data)
        except Exception as e:
            logger.error(f"Error loading skill definition from {file_path}: {e}")
        return None
