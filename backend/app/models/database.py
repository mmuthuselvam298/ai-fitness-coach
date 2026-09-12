"""SQLite persistence models and lightweight repository for FormFit AI."""

import os
import sqlite3
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings
from app.core.logging import logger


def init_db(db_path: str | None = None):
    """Initialize database tables with indexes."""
    path = db_path or settings.DATABASE_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()
        # workout_sessions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS workout_sessions (
                id TEXT PRIMARY KEY,
                exercise TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                duration_seconds REAL DEFAULT 0,
                target_reps INTEGER DEFAULT 0,
                completed_reps INTEGER DEFAULT 0,
                average_form_score REAL DEFAULT 0,
                depth_score REAL DEFAULT 0,
                alignment_score REAL DEFAULT 0,
                consistency_score REAL DEFAULT 0,
                status TEXT DEFAULT 'completed',
                notes TEXT
            )
            """
        )

        # exercise_results table (per-repetition metrics)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS exercise_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                rep_number INTEGER NOT NULL,
                duration_seconds REAL,
                form_score REAL NOT NULL,
                depth_score REAL,
                alignment_score REAL,
                consistency_score REAL,
                primary_feedback TEXT,
                completed_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES workout_sessions(id) ON DELETE CASCADE
            )
            """
        )

        # feedback_events table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                rep_number INTEGER,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES workout_sessions(id) ON DELETE CASCADE
            )
            """
        )

        # Indexes for query performance
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_exercise ON workout_sessions(exercise)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_started_at ON workout_sessions(started_at)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_results_session ON exercise_results(session_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_feedback_session ON feedback_events(session_id)"
        )
        conn.commit()
        logger.info(f"Database initialized at {path}")


class Database:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.DATABASE_PATH
        init_db(self.db_path)

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def save_session(self, session_data: dict[str, Any]) -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO workout_sessions (
                    id, exercise, started_at, ended_at, duration_seconds,
                    target_reps, completed_reps, average_form_score,
                    depth_score, alignment_score, consistency_score, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    ended_at=excluded.ended_at,
                    duration_seconds=excluded.duration_seconds,
                    completed_reps=excluded.completed_reps,
                    average_form_score=excluded.average_form_score,
                    depth_score=excluded.depth_score,
                    alignment_score=excluded.alignment_score,
                    consistency_score=excluded.consistency_score,
                    status=excluded.status,
                    notes=excluded.notes
                """,
                (
                    session_data["id"],
                    session_data["exercise"],
                    session_data["started_at"],
                    session_data.get("ended_at"),
                    session_data.get("duration_seconds", 0),
                    session_data.get("target_reps", 0),
                    session_data.get("completed_reps", 0),
                    session_data.get("average_form_score", 0),
                    session_data.get("depth_score", 0),
                    session_data.get("alignment_score", 0),
                    session_data.get("consistency_score", 0),
                    session_data.get("status", "completed"),
                    session_data.get("notes", ""),
                ),
            )
            conn.commit()
            return session_data["id"]

    def save_rep_result(self, result_data: dict[str, Any]) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO exercise_results (
                    session_id, rep_number, duration_seconds, form_score,
                    depth_score, alignment_score, consistency_score,
                    primary_feedback, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result_data["session_id"],
                    result_data["rep_number"],
                    result_data.get("duration_seconds", 0),
                    result_data["form_score"],
                    result_data.get("depth_score", 0),
                    result_data.get("alignment_score", 0),
                    result_data.get("consistency_score", 0),
                    result_data.get("primary_feedback", ""),
                    result_data.get("completed_at", datetime.now(timezone.utc).isoformat()),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def save_feedback_event(self, event_data: dict[str, Any]) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO feedback_events (
                    session_id, rep_number, type, severity, message, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event_data["session_id"],
                    event_data.get("rep_number"),
                    event_data.get("type", "form_feedback"),
                    event_data["severity"],
                    event_data["message"],
                    event_data.get("timestamp", datetime.now(timezone.utc).isoformat()),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_sessions(self, limit: int = 50, exercise: str | None = None) -> list[dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if exercise:
                cursor.execute(
                    """
                    SELECT * FROM workout_sessions
                    WHERE exercise = ?
                    ORDER BY started_at DESC LIMIT ?
                    """,
                    (exercise, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM workout_sessions
                    ORDER BY started_at DESC LIMIT ?
                    """,
                    (limit,),
                )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM workout_sessions WHERE id = ?", (session_id,))
            session_row = cursor.fetchone()
            if not session_row:
                return None
            session = dict(session_row)

            cursor.execute(
                "SELECT * FROM exercise_results WHERE session_id = ? ORDER BY rep_number ASC",
                (session_id,),
            )
            session["reps"] = [dict(r) for r in cursor.fetchall()]

            cursor.execute(
                "SELECT * FROM feedback_events WHERE session_id = ? ORDER BY id ASC",
                (session_id,),
            )
            session["feedback"] = [dict(f) for f in cursor.fetchall()]

            return session

    def get_analytics(self) -> dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    COUNT(*) as total_workouts,
                    COALESCE(SUM(completed_reps), 0) as total_reps,
                    COALESCE(AVG(average_form_score), 0) as avg_form_score,
                    COALESCE(MAX(average_form_score), 0) as best_form_score,
                    COALESCE(SUM(duration_seconds), 0) as total_duration_seconds
                FROM workout_sessions
                WHERE status = 'completed'
                """
            )
            overview = dict(cursor.fetchone())

            # Distribution by exercise
            cursor.execute(
                """
                SELECT exercise, COUNT(*) as count, COALESCE(SUM(completed_reps), 0) as reps, COALESCE(AVG(average_form_score), 0) as avg_score
                FROM workout_sessions
                GROUP BY exercise
                """
            )
            by_exercise = [dict(row) for row in cursor.fetchall()]

            # Form score and reps trend (last 14 sessions)
            cursor.execute(
                """
                SELECT id, exercise, started_at, completed_reps, average_form_score
                FROM workout_sessions
                ORDER BY started_at ASC
                LIMIT 20
                """
            )
            trend = [dict(row) for row in cursor.fetchall()]

            return {
                "overview": overview,
                "exercise_distribution": by_exercise,
                "history_trend": trend,
            }


db = Database()
