from pathlib import Path

import pytest

from modules.core.contracts import ContractError, ModuleContract, ModuleInput, ModuleOutput


def test_declared_input_is_accepted():
    contract = ModuleContract("qc", "1.0", input_names=("genomes",), output_names=("qc",))
    value = ModuleInput("genomes", (Path("input/genomes"),))
    contract.validate_input(value)


def test_undeclared_input_is_rejected():
    contract = ModuleContract("qc", "1.0", input_names=("genomes",))
    with pytest.raises(ContractError):
        contract.validate_input(ModuleInput("metadata"))


def test_declared_output_is_accepted():
    contract = ModuleContract("qc", "1.0", output_names=("qc",))
    contract.validate_output(ModuleOutput("qc", (Path("output/qc.json"),)))


def test_undeclared_output_is_rejected():
    contract = ModuleContract("qc", "1.0", output_names=("qc",))
    with pytest.raises(ContractError):
        contract.validate_output(ModuleOutput("report"))


def test_duplicate_contract_names_are_rejected():
    with pytest.raises(ContractError):
        ModuleContract("qc", "1.0", input_names=("genomes", "genomes"))
