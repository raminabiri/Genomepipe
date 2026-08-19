import pytest

from modules.core.models import ModuleResult, ModuleSpec
from modules.core.registry import ModuleRegistry


def test_module_spec_supports_global_and_organism_specific_modules():
    assert ModuleSpec("qc", "1.0").supports("any organism")
    assert ModuleSpec("mlst", "1.0", ("Mycobacterium tuberculosis",)).supports(
        "Mycobacterium tuberculosis"
    )
    assert not ModuleSpec("mlst", "1.0", ("Mycobacterium tuberculosis",)).supports(
        "Escherichia coli"
    )


def test_registry_resolves_supported_module():
    registry = ModuleRegistry()
    registry.register(ModuleSpec("example", "1.0"), lambda: {"ok": True})
    assert registry.get("example", "Escherichia coli") == {"ok": True}


def test_registry_rejects_unsupported_organism():
    registry = ModuleRegistry()
    registry.register(ModuleSpec("mlst", "1.0", ("Organism A",)), object)
    with pytest.raises(ValueError):
        registry.get("mlst", "Organism B")


def test_module_result_validates_status():
    result = ModuleResult("qc", "success")
    assert result.status == "success"
    with pytest.raises(ValueError):
        ModuleResult("qc", "running")
