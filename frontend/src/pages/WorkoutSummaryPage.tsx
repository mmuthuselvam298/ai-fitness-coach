import React, { useEffect } from 'react';
import confetti from 'canvas-confetti';
import { Award, CheckCircle2, ArrowRight, RotateCcw, Clock, Target, Activity } from 'lucide-react';
import { WorkoutSummary } from '../types';

interface WorkoutSummaryPageProps {
  summary: WorkoutSummary;
  onDone: () => void;
  onWorkoutAgain: () => void;
}

export const WorkoutSummaryPage: React.FC<WorkoutSummaryPageProps> = ({
  summary,
  onDone,
  onWorkoutAgain,
}) => {
  useEffect(() => {
    // Athletic celebration confetti burst
    confetti({
      particleCount: 60,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#10B981', '#F97316', '#0284C7', '#181A1B'],
    });
  }, []);

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 32, maxWidth: 840, margin: '0 auto', paddingBottom: 40 }}>
      {/* Header */}
      <div style={{ textAlign: 'center', paddingTop: 16 }}>
        <div className="badge badge-green" style={{ marginBottom: 12, padding: '6px 16px' }}>
          Workout Complete
        </div>
        <h1 style={{ fontSize: 'clamp(2.4rem, 5vw, 3.4rem)', fontWeight: 800, letterSpacing: '-0.03em' }}>
          Great work.
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', marginTop: 6 }}>
          Here is your biomechanical analysis and form score breakdown.
        </p>
      </div>

      {/* Hero Stat Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: 16,
      }}>
        <div className="card" style={{ textAlign: 'center', padding: '24px 16px' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.82rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: 6 }}>
            Completed Reps
          </div>
          <div className="rep-display" style={{ fontSize: '3.8rem', color: 'var(--accent-green-dark)' }}>
            {summary.completed_reps}
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: 4 }}>
            {summary.exercise.toUpperCase()} (Target: {summary.target_reps})
          </div>
        </div>

        <div className="card" style={{ textAlign: 'center', padding: '24px 16px' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.82rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: 6 }}>
            Form Score
          </div>
          <div className="rep-display" style={{ fontSize: '3.8rem', color: summary.average_form_score >= 80 ? 'var(--text-primary)' : 'var(--accent-coral)' }}>
            {Math.round(summary.average_form_score)}
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: 4 }}>
            out of 100 Quality Points
          </div>
        </div>

        <div className="card" style={{ textAlign: 'center', padding: '24px 16px' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.82rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: 6 }}>
            Session Duration
          </div>
          <div className="rep-display mono" style={{ fontSize: '3.4rem', color: 'var(--text-primary)', marginTop: 8 }}>
            {formatDuration(summary.duration_seconds)}
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: 8 }}>
            Active Workout Time
          </div>
        </div>
      </div>

      {/* Transparent Form Breakdown */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
        <div>
          <div className="badge badge-sky" style={{ marginBottom: 6 }}>Scoring Methodology</div>
          <h3 style={{ fontSize: '1.3rem', fontWeight: 800 }}>Biomechanical Quality Breakdown</h3>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
            Application-defined heuristic score based on depth flexion, alignment posture, and movement cadence:
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
          <div style={{
            backgroundColor: 'var(--bg-primary)',
            borderRadius: 'var(--radius-md)',
            padding: '16px',
            border: '1px solid var(--border-subtle)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
              <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>Depth Flexion</span>
              <span className="mono" style={{ fontWeight: 800, color: 'var(--accent-green-dark)' }}>
                {Math.round(summary.depth_score)} / 100
              </span>
            </div>
            <div style={{ width: '100%', height: 6, backgroundColor: 'var(--bg-subtle)', borderRadius: 3, overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${summary.depth_score}%`, backgroundColor: 'var(--accent-green)' }} />
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 6 }}>
              Weight: 40% of overall score
            </div>
          </div>

          <div style={{
            backgroundColor: 'var(--bg-primary)',
            borderRadius: 'var(--radius-md)',
            padding: '16px',
            border: '1px solid var(--border-subtle)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
              <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>Postural Alignment</span>
              <span className="mono" style={{ fontWeight: 800, color: 'var(--accent-green-dark)' }}>
                {Math.round(summary.alignment_score)} / 100
              </span>
            </div>
            <div style={{ width: '100%', height: 6, backgroundColor: 'var(--bg-subtle)', borderRadius: 3, overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${summary.alignment_score}%`, backgroundColor: 'var(--accent-green)' }} />
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 6 }}>
              Weight: 35% of overall score
            </div>
          </div>

          <div style={{
            backgroundColor: 'var(--bg-primary)',
            borderRadius: 'var(--radius-md)',
            padding: '16px',
            border: '1px solid var(--border-subtle)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
              <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>Cadence & Tempo</span>
              <span className="mono" style={{ fontWeight: 800, color: 'var(--accent-green-dark)' }}>
                {Math.round(summary.consistency_score)} / 100
              </span>
            </div>
            <div style={{ width: '100%', height: 6, backgroundColor: 'var(--bg-subtle)', borderRadius: 3, overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${summary.consistency_score}%`, backgroundColor: 'var(--accent-green)' }} />
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 6 }}>
              Weight: 25% of overall score
            </div>
          </div>
        </div>
      </div>

      {/* Actionable Coaching Insights: What went well vs Focus next time */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: 20,
      }}>
        <div className="card" style={{ borderLeft: '4px solid var(--accent-green)' }}>
          <h4 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--accent-green-dark)', marginBottom: 12 }}>
            ✓ What Went Well
          </h4>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 8, fontSize: '0.92rem' }}>
            {summary.what_went_well.map((item, idx) => (
              <li key={idx} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <CheckCircle2 size={16} color="var(--accent-green)" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="card" style={{ borderLeft: '4px solid var(--accent-coral)' }}>
          <h4 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--accent-coral)', marginBottom: 12 }}>
            → Focus Next Time
          </h4>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 8, fontSize: '0.92rem' }}>
            {summary.focus_next_time.map((item, idx) => (
              <li key={idx} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <ArrowRight size={16} color="var(--accent-coral)" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Rep-by-Rep Log Table */}
      {summary.reps_detail && summary.reps_detail.length > 0 && (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <h4 style={{ fontSize: '1.1rem', fontWeight: 800 }}>Repetition Telemetry Log</h4>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-subtle)', textAlign: 'left', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '8px 12px' }}>Rep #</th>
                  <th style={{ padding: '8px 12px' }}>Duration</th>
                  <th style={{ padding: '8px 12px' }}>Form Score</th>
                  <th style={{ padding: '8px 12px' }}>Depth</th>
                  <th style={{ padding: '8px 12px' }}>Alignment</th>
                  <th style={{ padding: '8px 12px' }}>Feedback</th>
                </tr>
              </thead>
              <tbody>
                {summary.reps_detail.map((r) => (
                  <tr key={r.rep_number} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '10px 12px', fontWeight: 700 }}>#{r.rep_number}</td>
                    <td className="mono" style={{ padding: '10px 12px' }}>{r.duration_seconds}s</td>
                    <td className="mono" style={{ padding: '10px 12px', fontWeight: 700, color: r.form_score >= 80 ? 'var(--accent-green-dark)' : 'var(--accent-coral)' }}>
                      {Math.round(r.form_score)}
                    </td>
                    <td className="mono" style={{ padding: '10px 12px' }}>{Math.round(r.depth_score)}</td>
                    <td className="mono" style={{ padding: '10px 12px' }}>{Math.round(r.alignment_score)}</td>
                    <td style={{ padding: '10px 12px', color: 'var(--text-secondary)' }}>{r.primary_feedback}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: 16, marginTop: 12 }}>
        <button onClick={onDone} className="btn btn-primary btn-lg">
          <span>Done</span>
        </button>
        <button onClick={onWorkoutAgain} className="btn btn-secondary btn-lg">
          <RotateCcw size={16} />
          <span>Workout Again</span>
        </button>
      </div>
    </div>
  );
};
