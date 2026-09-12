import React, { useState } from 'react';
import { Play, ArrowLeft, Target, Award, Zap, Video, Camera } from 'lucide-react';
import { ExerciseMetadata } from '../types';

interface ExerciseSelectPageProps {
  exercises: ExerciseMetadata[];
  onSelectExercise: (exerciseId: string, targetReps: number, mode: 'webcam' | 'demo' | 'upload') => void;
  onBack: () => void;
}

export const ExerciseSelectPage: React.FC<ExerciseSelectPageProps> = ({
  exercises,
  onSelectExercise,
  onBack,
}) => {
  const [selectedId, setSelectedId] = useState<string>(exercises[0]?.id || 'squat');
  const [targetReps, setTargetReps] = useState<number>(12);
  const [workoutMode, setWorkoutMode] = useState<'webcam' | 'demo' | 'upload'>('webcam');

  const selectedExercise = exercises.find((e) => e.id === selectedId) || exercises[0];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 32, maxWidth: 960, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <button onClick={onBack} className="btn btn-secondary btn-sm" style={{ width: 40, height: 40, padding: 0 }}>
          <ArrowLeft size={18} />
        </button>
        <div>
          <div className="badge badge-neutral" style={{ marginBottom: 4 }}>Workout Setup</div>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>Choose Your Exercise</h1>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24 }}>
        {/* Left Column: Exercise Cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <label style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-secondary)' }}>
            1. Select Movement
          </label>

          {exercises.map((ex) => {
            const isSelected = ex.id === selectedId;
            return (
              <div
                key={ex.id}
                onClick={() => setSelectedId(ex.id)}
                className="card"
                style={{
                  cursor: 'pointer',
                  borderColor: isSelected ? 'var(--text-primary)' : 'var(--border-subtle)',
                  backgroundColor: isSelected ? '#FFFFFF' : 'var(--bg-primary)',
                  boxShadow: isSelected ? 'var(--shadow-md)' : 'none',
                  borderWidth: isSelected ? 2 : 1,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '20px 24px',
                  transition: 'all 0.15s ease',
                }}
              >
                <div>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 4 }}>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>{ex.name}</h3>
                    <span className="badge badge-green" style={{ fontSize: '0.72rem' }}>{ex.difficulty}</span>
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    {ex.category} • Focus: {ex.target_angle_name}
                  </div>
                </div>

                <div style={{
                  width: 24,
                  height: 24,
                  borderRadius: '50%',
                  border: `2px solid ${isSelected ? 'var(--accent-green)' : 'var(--border-strong)'}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  {isSelected && (
                    <div style={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: 'var(--accent-green)' }} />
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Configuration & Specs */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {selectedExercise && (
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <div>
                <span className="badge badge-sky" style={{ marginBottom: 8 }}>Movement Details</span>
                <h3 style={{ fontSize: '1.4rem', fontWeight: 800 }}>{selectedExercise.name}</h3>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: 6, lineHeight: 1.5 }}>
                  {selectedExercise.description}
                </p>
              </div>

              {/* Targeted Muscles */}
              <div>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
                  Target Muscle Groups
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {selectedExercise.muscle_groups.map((m) => (
                    <span key={m} className="badge badge-neutral" style={{ fontSize: '0.78rem' }}>
                      {m}
                    </span>
                  ))}
                </div>
              </div>

              {/* Target Repetitions */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                  <label style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Target size={15} />
                    <span>Target Repetitions</span>
                  </label>
                  <span style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                    {targetReps} reps
                  </span>
                </div>

                <div style={{ display: 'flex', gap: 8 }}>
                  {[8, 10, 12, 15, 20].map((num) => (
                    <button
                      key={num}
                      type="button"
                      onClick={() => setTargetReps(num)}
                      className={`btn btn-sm ${targetReps === num ? 'btn-primary' : 'btn-secondary'}`}
                      style={{ flex: 1, padding: '8px 0' }}
                    >
                      {num}
                    </button>
                  ))}
                </div>
              </div>

              {/* Mode Selection */}
              <div>
                <label style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', display: 'block', marginBottom: 10 }}>
                  Camera Mode
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
                  <button
                    type="button"
                    onClick={() => setWorkoutMode('webcam')}
                    className={`btn btn-sm ${workoutMode === 'webcam' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ display: 'flex', flexDirection: 'column', gap: 4, padding: '12px 6px' }}
                  >
                    <Camera size={18} />
                    <span style={{ fontSize: '0.78rem' }}>Live Webcam</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setWorkoutMode('demo')}
                    className={`btn btn-sm ${workoutMode === 'demo' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ display: 'flex', flexDirection: 'column', gap: 4, padding: '12px 6px' }}
                  >
                    <Zap size={18} color={workoutMode === 'demo' ? '#FFFFFF' : 'var(--accent-coral)'} />
                    <span style={{ fontSize: '0.78rem' }}>Demo Video</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setWorkoutMode('upload')}
                    className={`btn btn-sm ${workoutMode === 'upload' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ display: 'flex', flexDirection: 'column', gap: 4, padding: '12px 6px' }}
                  >
                    <Video size={18} />
                    <span style={{ fontSize: '0.78rem' }}>Upload Video</span>
                  </button>
                </div>
              </div>

              {/* Start Workout Button */}
              <button
                onClick={() => onSelectExercise(selectedId, targetReps, workoutMode)}
                className="btn btn-accent btn-lg"
                style={{ width: '100%', marginTop: 8 }}
              >
                <Play size={18} />
                <span>Start {selectedExercise.name} Workout</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
