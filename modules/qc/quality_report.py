from pathlib import Path
from .quality_assessment import QualityAssessment


def write_quality_report(records: tuple[QualityAssessment, ...], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as handle:
        handle.write('genome_id\tcompleteness\tcontamination\tquality_label\n')
        for record in records:
            handle.write(f'{record.genome_id}\t{record.completeness}\t{record.contamination}\t{record.quality_label}\n')
    return path
