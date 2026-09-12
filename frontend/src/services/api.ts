import {
  ExerciseMetadata,
  WorkoutSummary,
  AnalyticsOverview,
  DemoSample,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = {
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
  },

  async getExercises(): Promise<ExerciseMetadata[]> {
    const res = await fetch(`${API_BASE}/exercises`);
    if (!res.ok) throw new Error('Failed to fetch exercises');
    return res.json();
  },

  async getExercise(id: string): Promise<ExerciseMetadata> {
    const res = await fetch(`${API_BASE}/exercises/${id}`);
    if (!res.ok) throw new Error('Failed to fetch exercise');
    return res.json();
  },

  async startWorkout(exercise: string, targetReps: number = 12): Promise<{ session_id: string; started_at: string }> {
    const res = await fetch(`${API_BASE}/workouts/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ exercise, target_reps: targetReps }),
    });
    if (!res.ok) throw new Error('Failed to start workout');
    return res.json();
  },

  async finishWorkout(sessionId: string): Promise<WorkoutSummary> {
    const res = await fetch(`${API_BASE}/workouts/${sessionId}/finish`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to finalize workout');
    return res.json();
  },

  async getWorkouts(limit: number = 20, exercise?: string): Promise<WorkoutSummary[]> {
    const url = new URL(`${API_BASE}/workouts`);
    url.searchParams.set('limit', limit.toString());
    if (exercise) url.searchParams.set('exercise', exercise);
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error('Failed to fetch workouts history');
    return res.json();
  },

  async getWorkout(sessionId: string): Promise<WorkoutSummary> {
    const res = await fetch(`${API_BASE}/workouts/${sessionId}`);
    if (!res.ok) throw new Error('Failed to fetch workout session');
    return res.json();
  },

  async getAnalytics(): Promise<AnalyticsOverview> {
    const res = await fetch(`${API_BASE}/analytics`);
    if (!res.ok) throw new Error('Failed to fetch analytics');
    return res.json();
  },

  async getDemoSamples(): Promise<DemoSample[]> {
    const res = await fetch(`${API_BASE}/demo/samples`);
    if (!res.ok) throw new Error('Failed to fetch demo samples');
    return res.json();
  },

  async simulateDemo(exercise: string, reps: number = 3) {
    const res = await fetch(`${API_BASE}/demo/simulate/${exercise}?reps=${reps}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Simulation failed');
    return res.json();
  },

  async analyzeVideo(file: File, exercise: string, frameSkip: number = 2) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('exercise', exercise);
    formData.append('frame_skip', frameSkip.toString());

    const res = await fetch(`${API_BASE}/analyze/video`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Video analysis failed' }));
      throw new Error(err.detail || 'Video analysis failed');
    }
    return res.json();
  },
};
