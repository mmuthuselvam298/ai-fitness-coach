import React, { useState, useEffect } from 'react';
import { History, Calendar, Clock, Filter, ArrowRight, Activity, Plus } from 'lucide-react';
import { WorkoutSummary } from '../types';
import { api } from '../services/api';

interface HistoryPageProps {
  onStartNewWorkout: () => void;
  onViewWorkoutDetail: (summary: WorkoutSummary) => void;
}

export const HistoryPage: React.FC<HistoryPageProps> = ({
  onStartNewWorkout,
  onViewWorkoutDetail,
}) => {
  const [workouts, setWorkouts] = useState<WorkoutSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterExercise, setFilterExercise] = useState<string>('all');

  useEffect(() => {
    fetchWorkouts();
  }, [filterExercise]);

  const fetchWorkouts = async () => {
    setLoading(true);
    try {
      const data = await api.getWorkouts(30, filterExercise === 'all' ? undefined : filterExercise);
      setWorkouts(data);
    } catch (err) {
      console.error('Failed to load workouts:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (isoStr: string) => {
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
      return isoStr;
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 28, maxWidth: 960, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <div className="badge badge-neutral" style={{ marginBottom: 6 }}>Workout History</div>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>Past Sessions</h1>
        </div>

        <button onClick={onStartNewWorkout} className="btn btn-primary btn-sm">
          <Plus size={16} />
          <span>New Workout</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {['all', 'squat', 'pushup', 'bicep_curl'].map((item) => (
          <button
            key={item}
            onClick={() => setFilterExercise(item)}
            className={`btn btn-sm ${filterExercise === item ? 'btn-primary' : 'btn-secondary'}`}
            style={{ textTransform: 'capitalize' }}
          >
            {item === 'all' ? 'All Exercises' : item.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '48px 0', color: 'var(--text-muted)' }}>
          Loading workout history...
        </div>
      ) : workouts.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '56px 20px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
          <div style={{
            width: 56,
            height: 56,
            borderRadius: '50%',
            backgroundColor: 'var(--bg-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-muted)',
          }}>
            <History size={26} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, marginBottom: 4 }}>No Workouts Recorded Yet</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', maxWidth: 420 }}>
              Complete your first computer vision coaching session to track repetitions, duration, and form score trends.
            </p>
          </div>
          <button onClick={onStartNewWorkout} className="btn btn-accent btn-sm" style={{ marginTop: 8 }}>
            <span>Start Your First Set</span>
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {workouts.map((w) => (
            <div
              key={w.id}
              onClick={() => onViewWorkoutDetail(w)}
              className="card card-hover"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '18px 24px',
                cursor: 'pointer',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
                <div style={{
                  width: 44,
                  height: 44,
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'var(--accent-green-light)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--accent-green-dark)',
                  fontWeight: 800,
                  fontSize: '1rem',
                }}>
                  {w.completed_reps}
                </div>

                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 800, textTransform: 'capitalize' }}>
                      {w.exercise.replace('_', ' ')}
                    </h3>
                    <span className="badge badge-neutral" style={{ fontSize: '0.72rem' }}>
                      Target: {w.target_reps}
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 16, fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: 4 }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <Calendar size={13} />
                      {formatDate(w.started_at)}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <Clock size={13} />
                      {formatDuration(w.duration_seconds)}
                    </span>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
                    Form Score
                  </div>
                  <div className="mono" style={{
                    fontSize: '1.4rem',
                    fontWeight: 800,
                    color: w.average_form_score >= 80 ? 'var(--accent-green-dark)' : 'var(--accent-coral)',
                  }}>
                    {Math.round(w.average_form_score)}
                  </div>
                </div>
                <ArrowRight size={18} color="var(--border-strong)" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
