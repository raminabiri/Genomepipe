from modules.qc.quality_assessment import assess_quality


def test_high_quality():
    result = assess_quality('g1', 95, 2)
    assert result.quality_label == 'HIGH_QUALITY'


def test_pending_without_external_metrics():
    result = assess_quality('g1')
    assert result.quality_label == 'PENDING'
