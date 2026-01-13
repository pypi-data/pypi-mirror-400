"""
Tests for SkillRegistry
"""
import pytest
import yaml
from axis_registry.skill_registry import SkillRegistry
from axis_sdk.protocols.skills import SkillProtocol


def test_skill_registry_load_definition(tmp_path):
    def_dir = tmp_path / "skills"
    def_dir.mkdir()

    skill_data = {
        "id": "test_skill",
        "name": "Test Skill",
        "description": "A test skill",
        "version": "1.0.0",
    }

    with open(def_dir / "test_skill.yml", "w") as f:
        yaml.dump(skill_data, f)

    registry = SkillRegistry(definition_paths=[def_dir], allowlist={})

    assert "test_skill" in registry.list_skills()


def test_skill_registry_load_implementation(tmp_path, mocker):
    def_dir = tmp_path / "skills"
    def_dir.mkdir()

    # Mock definition
    skill_data = {
        "id": "math_skill",
        "name": "Math",
        "description": "Add",
        "version": "1.0.0",
    }
    with open(def_dir / "math_skill.yml", "w") as f:
        yaml.dump(skill_data, f)

    # Mock module
    mock_module = mocker.Mock()

    def mock_execute(params, context):
        return {"result": params["a"] + params["b"]}

    mock_module.execute = mock_execute

    mocker.patch("importlib.import_module", return_value=mock_module)

    registry = SkillRegistry(
        definition_paths=[def_dir], allowlist={"math_skill": "fake_math_module"}
    )

    skill = registry.get_skill("math_skill")
    assert isinstance(skill, SkillProtocol)

    result = skill.execute({"a": 1, "b": 2}, {})
    assert result["result"] == 3


def test_skill_registry_not_authorized(tmp_path):
    registry = SkillRegistry(definition_paths=[], allowlist={})
    with pytest.raises(PermissionError, match="not authorized"):
        registry.get_skill("rogue_skill")


def test_skill_registry_caching(tmp_path, mocker):
    def_dir = tmp_path / "skills"
    def_dir.mkdir()

    # Mock definition
    skill_data = {
        "id": "cache_skill",
        "name": "Cache",
        "description": "Cache",
        "version": "1.0.0",
    }
    with open(def_dir / "cache_skill.yml", "w") as f:
        yaml.dump(skill_data, f)

    # Mock module
    mock_module = mocker.Mock()
    mock_module.execute = lambda p, c: {"status": "ok"}
    mock_import = mocker.patch("importlib.import_module", return_value=mock_module)

    registry = SkillRegistry(
        definition_paths=[def_dir], allowlist={"cache_skill": "fake_path"}
    )

    # First call
    skill1 = registry.get_skill("cache_skill")
    # Second call
    skill2 = registry.get_skill("cache_skill")

    assert skill1 is skill2
    assert mock_import.call_count == 1


def test_skill_registry_refresh(tmp_path):
    def_dir = tmp_path / "skills"
    def_dir.mkdir()

    registry = SkillRegistry(definition_paths=[def_dir], allowlist={})
    assert len(registry.list_skills()) == 0

    # Add definition after init
    skill_data = {
        "id": "new_skill",
        "name": "New",
        "description": "New",
        "version": "1.0.0",
    }
    with open(def_dir / "new_skill.yml", "w") as f:
        yaml.dump(skill_data, f)

    registry.refresh()
    assert "new_skill" in registry.list_skills()
