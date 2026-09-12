"""Exercise registry and specification endpoints."""

from app.exercises.registry import ExerciseRegistry
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/exercises", tags=["Exercises"])


@router.get("")
def list_exercises():
    """Retrieve catalog of supported exercises with biomechanical specs."""
    return ExerciseRegistry.get_all_exercises()


@router.get("/{exercise_id}")
def get_exercise(exercise_id: str):
    """Retrieve details for a specific exercise."""
    try:
        return ExerciseRegistry.get_exercise_metadata(exercise_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
