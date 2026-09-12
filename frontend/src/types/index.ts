export type FeedbackSeverity = 'info' | 'good' | 'warning' | 'error';

export interface FeedbackEvent {
  type: string;
  severity: FeedbackSeverity;
  message: string;
  timestamp: number;
}

export interface RepResult {
  rep_number: number;
  duration_seconds: number;
  form_score: number;
  depth_score: number;
  alignment_score: number;
  consistency_score: number;
  primary_feedback: string;
  completed_at: number;
}

export interface ExerciseMetadata {
  id: string;
  name: string;
  category: string;
  muscle_groups: string[];
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  description: string;
  target_angle_name: string;
  target_angle_range: string;
  default_target_reps: number;
}

export interface LandmarkCoordinate {
  x: number;
  y: number;
  visibility: number;
}

export interface FrameAnalysisResult {
  detected: boolean;
  multiple_people?: boolean;
  rep_count: number;
  phase: string;
  primary_angle: number;
  angles: Record<string, number>;
  form_score: number;
  confidence: number;
  inference_ms: number;
  feedback: FeedbackEvent[];
  rep_completed: boolean;
  is_calibrated: boolean;
  calibration_message?: string | null;
  landmarks?: Record<number, LandmarkCoordinate>;
  server_processing_ms?: number;
  fps?: number;
  error?: string;
}

export interface WorkoutSummary {
  id: string;
  exercise: string;
  started_at: string;
  ended_at?: string;
  duration_seconds: number;
  target_reps: number;
  completed_reps: number;
  average_form_score: number;
  depth_score: number;
  alignment_score: number;
  consistency_score: number;
  status: string;
  notes?: string;
  reps_detail?: RepResult[];
  what_went_well: string[];
  focus_next_time: string[];
}

export interface AnalyticsOverview {
  total_workouts: number;
  total_reps: number;
  avg_form_score: number;
  best_form_score: number;
  total_duration_minutes: number;
  exercise_distribution: Array<{
    exercise: string;
    count: number;
    reps: number;
    avg_score: number;
  }>;
  recent_trend: Array<{
    id: string;
    exercise: string;
    started_at: string;
    completed_reps: number;
    average_form_score: number;
  }>;
}

export interface DemoSample {
  id: string;
  name: string;
  video_url: string;
  description: string;
}
