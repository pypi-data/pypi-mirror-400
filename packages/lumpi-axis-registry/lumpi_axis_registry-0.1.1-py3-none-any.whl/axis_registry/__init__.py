"""
AXIS Registry
"""
__version__ = "0.1.1"
__description__ = "Agent and Skill discovery for AXIS"

from axis_registry.agent_registry import AgentRegistry
from axis_registry.skill_registry import SkillRegistry

__all__ = ["AgentRegistry", "SkillRegistry"]
