"""Exercise analyzer registry and metadata provider."""

from typing import Any

from app.exercises.base import ExerciseAnalyzer
from app.exercises.bicep_curl import BicepCurlAnalyzer
from app.exercises.pushup import PushupAnalyzer
from app.exercises.squat import SquatAnalyzer

EXERCISE_CATALOG: dict[str, dict[str, Any]] = {
    "squat": {
        "id": "squat",
        "name": "Squats",
        "category": "Lower Body",
        "muscle_groups": ["Quadriceps", "Glutes", "Hamstrings", "Core"],
        "difficulty": "Beginner",
        "description": "Foundational lower-body compound movement focusing on knee flexion depth and upright posture.",
        "target_angle_name": "Knee Angle",
        "target_angle_range": "80° - 95° at bottom",
        "default_target_reps": 15,
        "analyzer_class": SquatAnalyzer,
    },
    "pushup": {
        "id": "pushup",
        "name": "Push-ups",
        "category": "Upper Body & Core",
        "muscle_groups": ["Pectorals", "Triceps", "Anterior Deltoid", "Core Plank"],
        "difficulty": "Intermediate",
        "description": "Upper-body pressing movement emphasizing chest depth and rigid core plank alignment.",
        "target_angle_name": "Elbow Angle",
        "target_angle_range": "80° - 90° at bottom",
        "default_target_reps": 12,
        "analyzer_class": PushupAnalyzer,
    },
    "bicep_curl": {
        "id": "bicep_curl",
        "name": "Bicep Curls",
        "category": "Arms",
        "muscle_groups": ["Biceps Brachii", "Brachialis", "Forearms"],
        "difficulty": "Beginner",
        "description": "Arm isolation exercise requiring controlled elbow flexion and minimal upper-arm swinging.",
        "target_angle_name": "Elbow Flexion",
        "target_angle_range": "45° - 55° at peak",
        "default_target_reps": 12,
        "analyzer_class": BicepCurlAnalyzer,
    },
}


class ExerciseRegistry:
    @staticmethod
    def get_all_exercises() -> list[dict[str, Any]]:
        """Return public list of exercises without class references."""
        result = []
        for ex in EXERCISE_CATALOG.values():
            entry = {k: v for k, v in ex.items() if k != "analyzer_class"}
            result.append(entry)
        return result

    @staticmethod
    def get_exercise_metadata(exercise_id: str) -> dict[str, Any]:
        info = EXERCISE_CATALOG.get(exercise_id.lower())
        if not info:
            raise ValueError(f"Unsupported exercise: '{exercise_id}'")
        return {k: v for k, v in info.items() if k != "analyzer_class"}

    @staticmethod
    def create_analyzer(exercise_id: str) -> ExerciseAnalyzer:
        info = EXERCISE_CATALOG.get(exercise_id.lower())
        if not info:
            raise ValueError(
                f"Unsupported exercise: '{exercise_id}'. Supported: {list(EXERCISE_CATALOG.keys())}"
            )
        cls: type[ExerciseAnalyzer] = info["analyzer_class"]
        return cls()
