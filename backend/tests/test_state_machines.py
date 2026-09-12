"""Deterministic biomechanical state machine and repetition counter unit tests."""

from app.exercises.bicep_curl import BicepCurlAnalyzer
from app.exercises.pushup import PushupAnalyzer
from app.exercises.squat import SquatAnalyzer
from app.services.demo_service import DemoService
from app.vision.geometry import Point3D, PoseLandmark


def test_squat_full_cycle_rep_counted():
    analyzer = SquatAnalyzer()
    frames = DemoService.generate_squat_landmarks_sequence(num_reps=1, fps=30)

    rep_events = []
    for idx, lms in enumerate(frames):
        ts = idx / 30.0
        frame_res = analyzer.process_frame(lms, timestamp=ts)
        if frame_res.rep_completed:
            rep_events.append(frame_res)

    assert analyzer.rep_count == 1
    assert len(rep_events) == 1
    assert rep_events[0].completed_rep_details is not None
    assert rep_events[0].completed_rep_details.form_score > 70.0


def test_squat_shallow_rep_rejected():
    """Verify shallow knee bend (not reaching depth target) is not counted as a full rep."""
    analyzer = SquatAnalyzer()

    # Standing: Knee angle ~175
    standing_lms = {
        PoseLandmark.RIGHT_SHOULDER: Point3D(0.5, 0.2, visibility=0.9),
        PoseLandmark.RIGHT_HIP: Point3D(0.5, 0.5, visibility=0.9),
        PoseLandmark.RIGHT_KNEE: Point3D(0.5, 0.7, visibility=0.9),
        PoseLandmark.RIGHT_ANKLE: Point3D(0.5, 0.9, visibility=0.9),
    }

    # Shallow dip: Knee bends slightly to only ~135 degrees (well above 110)
    shallow_lms = {
        PoseLandmark.RIGHT_SHOULDER: Point3D(0.5, 0.23, visibility=0.9),
        PoseLandmark.RIGHT_HIP: Point3D(0.48, 0.53, visibility=0.9),
        PoseLandmark.RIGHT_KNEE: Point3D(0.54, 0.70, visibility=0.9),
        PoseLandmark.RIGHT_ANKLE: Point3D(0.5, 0.9, visibility=0.9),
    }

    # 1. Standing
    analyzer.process_frame(standing_lms, timestamp=0.0)
    assert analyzer.current_phase == "READY"

    # 2. Shallow dip
    analyzer.process_frame(shallow_lms, timestamp=0.5)
    # Starts descending
    assert analyzer.current_phase == "DESCENDING"

    # 3. Returns standing immediately without reaching depth
    analyzer.process_frame(standing_lms, timestamp=1.0)

    # Should NOT count repetition
    assert analyzer.rep_count == 0


def test_pushup_full_cycle_rep_counted():
    analyzer = PushupAnalyzer()
    frames = DemoService.generate_pushup_landmarks_sequence(num_reps=1, fps=30)

    rep_events = []
    for idx, lms in enumerate(frames):
        ts = idx / 30.0
        frame_res = analyzer.process_frame(lms, timestamp=ts)
        if frame_res.rep_completed:
            rep_events.append(frame_res)

    assert analyzer.rep_count == 1
    assert len(rep_events) == 1
    assert rep_events[0].completed_rep_details.depth_score >= 80.0


def test_bicep_curl_full_cycle_rep_counted():
    analyzer = BicepCurlAnalyzer()
    frames = DemoService.generate_bicep_curl_landmarks_sequence(num_reps=1, fps=30)

    rep_events = []
    for idx, lms in enumerate(frames):
        ts = idx / 30.0
        frame_res = analyzer.process_frame(lms, timestamp=ts)
        if frame_res.rep_completed:
            rep_events.append(frame_res)

    assert analyzer.rep_count == 1
    assert len(rep_events) == 1
    assert rep_events[0].completed_rep_details.form_score >= 80.0


def test_bicep_curl_arm_swing_warning():
    """Verify swinging elbow produces warning feedback."""
    analyzer = BicepCurlAnalyzer()

    # Point with elbow swinging forward excessively (upper arm angle > 35)
    swinging_lms = {
        PoseLandmark.RIGHT_SHOULDER: Point3D(0.50, 0.30, visibility=0.95),
        PoseLandmark.RIGHT_ELBOW: Point3D(0.65, 0.45, visibility=0.95),  # Flared way forward
        PoseLandmark.RIGHT_WRIST: Point3D(0.62, 0.32, visibility=0.95),
        PoseLandmark.RIGHT_HIP: Point3D(0.50, 0.60, visibility=0.95),
    }

    # Start curling
    analyzer.process_frame(
        {
            PoseLandmark.RIGHT_SHOULDER: Point3D(0.5, 0.3, visibility=0.95),
            PoseLandmark.RIGHT_ELBOW: Point3D(0.5, 0.5, visibility=0.95),
            PoseLandmark.RIGHT_WRIST: Point3D(0.5, 0.65, visibility=0.95),
            PoseLandmark.RIGHT_HIP: Point3D(0.5, 0.6, visibility=0.95),
        },
        timestamp=0.0,
    )

    res = analyzer.process_frame(swinging_lms, timestamp=0.5)
    messages = [fb.message for fb in res.feedback]
    assert any("elbow" in m.lower() for m in messages)
