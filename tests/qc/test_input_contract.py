from pathlib import Path

from modules.qc.input_contract import LOCAL_GENOME_INPUT_CONTRACT, build_local_genome_input


def test_local_input_contract_is_network_free(tmp_path: Path):
    contract = LOCAL_GENOME_INPUT_CONTRACT
    module_input = build_local_genome_input(tmp_path / "genomes")
    assert contract.name == "local_genome_input"
    assert module_input.metadata["network"] is False
    assert module_input.metadata["source"] == "local"
