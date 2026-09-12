"""Demo mode endpoints for offline and hosted evaluation."""

import os

from app.exercises.registry import ExerciseRegistry
from app.services.demo_service import DemoService
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/demo", tags=["Demo"])

BASE_DEMO_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "demo",
)


@router.get("/samples")
def list_demo_samples():
    """List pre-packaged synthetic demo exercises."""
    return [
        {
            "id": "squat",
            "name": "Squat Routine (3 Reps)",
            "video_url": "/api/demo/video/squat",
            "description": "Standard parallel squat movement pattern with consistent tempo.",
        },
        {
            "id": "pushup",
            "name": "Push-up Routine (3 Reps)",
            "video_url": "/api/demo/video/pushup",
            "description": "Clean horizontal plank and 90-degree elbow flexion cycles.",
        },
        {
            "id": "bicep_curl",
            "name": "Bicep Curl Routine (3 Reps)",
            "video_url": "/api/demo/video/bicep_curl",
            "description": "Arm isolation with stable elbow position and full contraction.",
        },
    ]


@router.get("/video/{exercise}")
def stream_demo_video(exercise: str):
    """Stream bundled synthetic test video."""
    video_map = {
        "squat": "squat_demo.mp4",
        "pushup": "pushup_demo.mp4",
        "bicep_curl": "bicep_curl_demo.mp4",
    }
    filename = video_map.get(exercise.lower())
    if not filename:
        raise HTTPException(status_code=404, detail="Demo video not found")

    file_path = os.path.join(BASE_DEMO_DIR, filename)
    if not os.path.exists(file_path):
        # Auto render if missing
        DemoService.render_demo_video(exercise.lower(), file_path)

    return FileResponse(file_path, media_type="video/mp4", filename=filename)


@router.post("/simulate/{exercise}")
def simulate_exercise_run(exercise: str, reps: int = 3):
    """Simulate a complete kinematic run and return frame-by-frame analysis with rep completions."""
    try:
        analyzer = ExerciseRegistry.create_analyzer(exercise)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if exercise == "pushup":
        frames = DemoService.generate_pushup_landmarks_sequence(num_reps=reps)
    elif exercise == "bicep_curl":
        frames = DemoService.generate_bicep_curl_landmarks_sequence(num_reps=reps)
    else:
        frames = DemoService.generate_squat_landmarks_sequence(num_reps=reps)

    results = []
    fps = 30.0

    for idx, lms in enumerate(frames):
        ts = idx / fps
        analysis = analyzer.process_frame(lms, timestamp=ts)
        if analysis.rep_completed or idx % 10 == 0:
            results.append(
                {
                    "frame_index": idx,
                    "timestamp": round(ts, 2),
                    "phase": analysis.phase,
                    "primary_angle": round(analysis.primary_angle, 1),
                    "reps": analysis.rep_count,
                    "rep_completed": analysis.rep_completed,
                    "feedback": [f.to_dict() for f in analysis.feedback],
                }
            )

    return {
        "exercise": exercise,
        "total_simulated_frames": len(frames),
        "reps_counted": analyzer.rep_count,
        "average_form_score": analyzer.get_average_form_score(),
        "score_breakdown": analyzer.get_score_breakdown(),
        "rep_results": [r.to_dict() for r in analyzer.completed_reps],
        "sampled_events": results,
    }
