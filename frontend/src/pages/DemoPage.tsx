import React, { useState, useEffect } from 'react';
import { Zap, Play, CheckCircle2, ShieldAlert, Cpu, ArrowRight } from 'lucide-react';
import { DemoSample } from '../types';
import { api } from '../services/api';

interface DemoPageProps {
  onLaunchDemoWorkout: (exerciseId: string) => void;
}

export const DemoPage: React.FC<DemoPageProps> = ({ onLaunchDemoWorkout }) => {
  const [samples, setSamples] = useState<DemoSample[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [simResult, setSimResult] = useState<any | null>(null);
  const [simulatingExercise, setSimulatingExercise] = useState<string | null>(null);

  useEffect(() => {
    api.getDemoSamples()
      .then((res) => setSamples(res))
      .catch((err) => console.error('Failed to load demo samples:', err))
      .finally(() => setLoading(false));
  }, []);

  const handleSimulate = async (exerciseId: string) => {
    setSimulatingExercise(exerciseId);
    setSimResult(null);
    try {
      const data = await api.simulateDemo(exerciseId, 3);
      setSimResult(data);
    } catch (err: any) {
      alert(`Simulation failed: ${err.message}`);
    } finally {
      setSimulatingExercise(null);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 32, maxWidth: 960, margin: '0 auto', paddingBottom: 40 }}>
      {/* Header */}
      <div>
        <div className="badge badge-coral" style={{ marginBottom: 6 }}>
          <Zap size={14} />
          <span>Interactive Demo Experience</span>
        </div>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>Hosted Demo Suite</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', marginTop: 6, maxWidth: 680 }}>
          Evaluate FormFit AI's computer vision pipeline, rep state machines, and form scoring without requiring a physical camera or webcam permissions.
        </p>
      </div>

      {/* Privacy Notice Alert */}
      <div style={{
        backgroundColor: '#FFFBEB',
        border: '1px solid #FDE68A',
        borderRadius: 'var(--radius-md)',
        padding: '14px 18px',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        fontSize: '0.88rem',
        color: '#92400E',
      }}>
        <ShieldAlert size={18} style={{ flexShrink: 0 }} />
        <span>
          <strong>Ethical Synthetic Media:</strong> All demo videos and test routines utilize computer-generated synthetic biomechanical motion models. No real individuals' private exercise recordings are stored or processed.
        </span>
      </div>

      {/* Demo Routines Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: 20,
      }}>
        {loading ? (
          <div style={{ color: 'var(--text-muted)' }}>Loading demo media...</div>
        ) : (
          samples.map((sample) => (
            <div key={sample.id} className="card card-hover" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: 16 }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <span className="badge badge-sky" style={{ textTransform: 'capitalize' }}>{sample.id}</span>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>3 Full Reps</span>
                </div>
                <h3 style={{ fontSize: '1.3rem', fontWeight: 800, marginBottom: 6 }}>
                  {sample.name}
                </h3>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {sample.description}
                </p>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <button
                  onClick={() => onLaunchDemoWorkout(sample.id)}
                  className="btn btn-accent btn-sm"
                  style={{ width: '100%' }}
                >
                  <Play size={14} />
                  <span>Launch Live Video Player</span>
                </button>

                <button
                  onClick={() => handleSimulate(sample.id)}
                  disabled={simulatingExercise === sample.id}
                  className="btn btn-secondary btn-sm"
                  style={{ width: '100%' }}
                >
                  <Cpu size={14} />
                  <span>{simulatingExercise === sample.id ? 'Running Simulation...' : 'Algorithmic Test'}</span>
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Algorithmic Simulation Result Panel */}
      {simResult && (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 20, border: '2px solid var(--accent-green)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
            <div>
              <div className="badge badge-green" style={{ marginBottom: 4 }}>Simulation Completed</div>
              <h3 style={{ fontSize: '1.4rem', fontWeight: 800, textTransform: 'capitalize' }}>
                {simResult.exercise} State Machine Verification
              </h3>
            </div>
            <div className="mono" style={{ fontSize: '1.1rem', fontWeight: 700 }}>
              Frames: {simResult.total_simulated_frames} • Verified Reps: <strong style={{ color: 'var(--accent-green-dark)' }}>{simResult.reps_counted}</strong>
            </div>
          </div>

          {/* Heuristic Score Breakdown */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: 12,
            backgroundColor: 'var(--bg-primary)',
            padding: '16px',
            borderRadius: 'var(--radius-md)',
          }}>
            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Overall Form Score</div>
              <div className="mono" style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--accent-green-dark)' }}>
                {Math.round(simResult.average_form_score)} / 100
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Depth Score (40%)</div>
              <div className="mono" style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                {Math.round(simResult.score_breakdown.depth)}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Alignment (35%)</div>
              <div className="mono" style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                {Math.round(simResult.score_breakdown.alignment)}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Tempo (25%)</div>
              <div className="mono" style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                {Math.round(simResult.score_breakdown.consistency)}
              </div>
            </div>
          </div>

          {/* Sampled Inflection Events Table */}
          <div>
            <h4 style={{ fontSize: '1rem', fontWeight: 800, marginBottom: 8 }}>
              Sampled State Machine Transitions
            </h4>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)', textAlign: 'left', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '6px 10px' }}>Timestamp</th>
                    <th style={{ padding: '6px 10px' }}>State Machine Phase</th>
                    <th style={{ padding: '6px 10px' }}>Joint Flexion</th>
                    <th style={{ padding: '6px 10px' }}>Rep Count</th>
                    <th style={{ padding: '6px 10px' }}>Rep Verified</th>
                  </tr>
                </thead>
                <tbody>
                  {simResult.sampled_events?.map((ev: any, idx: number) => (
                    <tr key={idx} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                      <td className="mono" style={{ padding: '8px 10px' }}>{ev.timestamp}s</td>
                      <td style={{ padding: '8px 10px', fontWeight: 700, color: ev.rep_completed ? 'var(--accent-green-dark)' : 'inherit' }}>
                        {ev.phase}
                      </td>
                      <td className="mono" style={{ padding: '8px 10px' }}>{ev.primary_angle}°</td>
                      <td className="mono" style={{ padding: '8px 10px', fontWeight: 700 }}>{ev.reps}</td>
                      <td style={{ padding: '8px 10px' }}>
                        {ev.rep_completed ? (
                          <span className="badge badge-green" style={{ fontSize: '0.7rem' }}>✓ Rep Counted</span>
                        ) : (
                          <span style={{ color: 'var(--text-muted)' }}>—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
