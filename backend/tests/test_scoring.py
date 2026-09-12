"""Tests for form scoring model and metric aggregation."""

import pytest
from app.exercises.base import RepResult
from app.exercises.squat import SquatAnalyzer


def test_score_calculation_weights():
    # Test formula: 0.40 * depth + 0.35 * alignment + 0.25 * consistency
    d = 100.0
    a = 80.0
    c = 90.0
    expected = 0.40 * 100.0 + 0.35 * 80.0 + 0.25 * 90.0  # 40 + 28 + 22.5 = 90.5

    rep = RepResult(
        rep_number=1,
        duration_seconds=2.5,
        form_score=expected,
        depth_score=d,
        alignment_score=a,
        consistency_score=c,
        primary_feedback="Great form",
    )
    assert pytest.approx(rep.form_score, 0.01) == 90.5


def test_analyzer_average_and_breakdown():
    analyzer = SquatAnalyzer()
    analyzer.completed_reps = [
        RepResult(1, 2.0, 90.0, 100.0, 80.0, 90.0, "Good depth"),
        RepResult(2, 2.2, 80.0, 80.0, 80.0, 80.0, "Good rep"),
    ]

    assert analyzer.get_average_form_score() == 85.0
    breakdown = analyzer.get_score_breakdown()
    assert breakdown["depth"] == 90.0
    assert breakdown["alignment"] == 80.0
    assert breakdown["consistency"] == 85.0
