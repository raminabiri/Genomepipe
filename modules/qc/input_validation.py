from pathlib import Path

from .input_manager import GenomeInput


class GenomeInputValidationError(ValueError):
    pass


def validate_fasta_file(path: Path) -> tuple[str, ...]:
    errors: list[str] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            first = handle.readline()
            if not first:
                return (f"Empty genome file: {path}",)
            if not first.startswith(">"):
                errors.append(f"Missing FASTA header: {path}")
                return tuple(errors)
            sequence_found = False
            for line_number, line in enumerate(handle, start=2):
                line = line.strip()
                if not line:
                    continue
                if line.startswith(">"):
                    continue
                sequence_found = True
                invalid = set(line.upper()) - set("ACGTUNRYKMSWBDHV-")
                if invalid:
                    errors.append(
                        f"Invalid nucleotide characters in {path} at line {line_number}: {sorted(invalid)}"
                    )
                    break
            if not sequence_found:
                errors.append(f"FASTA contains no sequence data: {path}")
    except UnicodeDecodeError:
        errors.append(f"Genome file is not valid UTF-8 text: {path}")
    except OSError as exc:
        errors.append(f"Unable to read genome file {path}: {exc}")
    return tuple(errors)


def validate_genomes(inputs: tuple[GenomeInput, ...]) -> dict[str, tuple[str, ...]]:
    report: dict[str, tuple[str, ...]] = {}
    for genome in inputs:
        errors = validate_fasta_file(genome.path)
        if errors:
            report[genome.genome_id] = errors
    return report
