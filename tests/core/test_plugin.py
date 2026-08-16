import pytest

from modules.core.contracts import ModuleContract
from modules.core.models import ModuleResult, ModuleSpec, ProjectContext
from modules.core.plugin import AnalysisPlugin


class DummyPlugin(AnalysisPlugin):
    spec = ModuleSpec("typing", "1.0", organisms=("demo",))
    contract = ModuleContract("typing", "1.0", input_names=("genomes",), output_names=("typing",))

    def run(self, context, inputs):
        self.validate_input(inputs)
        return ModuleResult(module=self.spec.name, status="success")

    def describe(self):
        return self.spec


def test_plugin_exposes_organism_capability():
    plugin = DummyPlugin()
    assert plugin.describe().supports("demo")
    assert not plugin.describe().supports("other")


def test_plugin_is_abstract():
    assert not hasattr(AnalysisPlugin, "run") or getattr(AnalysisPlugin.run, "__isabstractmethod__", False)


def test_plugin_context_can_be_constructed(tmp_path):
    context = ProjectContext("demo", tmp_path, "demo", "existing", tmp_path / "project.yaml", tmp_path / "input", tmp_path / "output")
    result = DummyPlugin().run(context, __import__("modules.core.contracts", fromlist=["ModuleInput"]).ModuleInput("genomes"))
    assert result.status == "success"
