import React from 'react';
import { Play, Zap, CheckCircle2, ArrowRight, ShieldCheck, Cpu, Compass, Activity } from 'lucide-react';
import { ExerciseMetadata } from '../types';

interface LandingPageProps {
  onStartWorkout: () => void;
  onTryDemo: () => void;
  onNavigateAbout?: () => void;
  exercises: ExerciseMetadata[];
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onStartWorkout,
  onTryDemo,
  onNavigateAbout,
  exercises,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 64, paddingBottom: 40 }}>
      {/* Hero Section */}
      <section style={{
        paddingTop: 48,
        paddingBottom: 32,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        position: 'relative',
      }}>
        {/* Athletic Pill Tag */}
        <div className="badge badge-green" style={{ marginBottom: 24, padding: '6px 16px', fontSize: '0.85rem' }}>
          <Activity size={15} />
          <span>Real-Time Biomechanical Coaching Engine</span>
        </div>

        {/* Hero Headlines */}
        <h1 style={{
          fontSize: 'clamp(2.8rem, 7vw, 4.8rem)',
          fontWeight: 800,
          lineHeight: 1.05,
          letterSpacing: '-0.04em',
          maxWidth: 820,
          color: 'var(--text-primary)',
          marginBottom: 20,
        }}>
          TRAIN SMARTER.<br />
          <span style={{ color: 'var(--accent-green-dark)' }}>MOVE BETTER.</span>
        </h1>

        <p style={{
          fontSize: 'clamp(1.1rem, 2.5vw, 1.35rem)',
          color: 'var(--text-secondary)',
          maxWidth: 640,
          lineHeight: 1.5,
          marginBottom: 36,
          fontWeight: 400,
        }}>
          AI-powered movement analysis that tracks joint angles, detects exercise phases, and delivers actionable coaching feedback in real time.
        </p>

        {/* CTAs */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, justifyContent: 'center' }}>
          <button onClick={onStartWorkout} className="btn btn-primary btn-lg">
            <Play size={18} />
            <span>Start Workout</span>
          </button>
          
          <button onClick={onTryDemo} className="btn btn-secondary btn-lg">
            <Zap size={18} color="var(--accent-coral)" />
            <span>Try Interactive Demo</span>
          </button>
        </div>

        {/* Sub-text highlights */}
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 24,
          justifyContent: 'center',
          marginTop: 36,
          fontSize: '0.88rem',
          color: 'var(--text-muted)',
        }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <CheckCircle2 size={16} color="var(--accent-green)" />
            No special hardware needed
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <CheckCircle2 size={16} color="var(--accent-green)" />
            Private in-browser analysis
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <CheckCircle2 size={16} color="var(--accent-green)" />
            Zero video stored
          </span>
        </div>
      </section>

      {/* Movement Engine Architecture Pillars */}
      <section style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: 24,
      }}>
        <div className="card card-hover" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{
            width: 48,
            height: 48,
            borderRadius: 14,
            backgroundColor: 'var(--accent-green-light)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-green-dark)',
          }}>
            <Cpu size={24} />
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Pose & Joint Geometry</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.6 }}>
            Extracts 33 anatomical landmarks using Google MediaPipe Pose. Vector geometry calculates true 3D joint angles for hips, knees, elbows, and torso tilt with visibility confidence gating.
          </p>
        </div>

        <div className="card card-hover" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{
            width: 48,
            height: 48,
            borderRadius: 14,
            backgroundColor: 'var(--accent-coral-light)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-coral)',
          }}>
            <Compass size={24} />
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>State Machine Rep Counter</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.6 }}>
            Eliminates jitter and accidental movements through deterministic biomechanical state machines (Ready → Descending → Bottom Inflection → Ascending → Complete).
          </p>
        </div>

        <div className="card card-hover" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{
            width: 48,
            height: 48,
            borderRadius: 14,
            backgroundColor: 'var(--accent-sky-light)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-sky)',
          }}>
            <ShieldCheck size={24} />
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Transparent Form Scoring</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.6 }}>
            Provides immediate coaching prompts and a heuristic 0–100 score based on depth accuracy (40%), posture alignment (35%), and movement tempo consistency (25%).
          </p>
        </div>
      </section>

      {/* Supported Exercises Showcase */}
      <section style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div className="badge badge-neutral" style={{ marginBottom: 8 }}>Curated Catalog</div>
            <h2 style={{ fontSize: '2rem', fontWeight: 800 }}>Supported Exercises</h2>
          </div>
          <button onClick={onStartWorkout} className="btn btn-secondary btn-sm" style={{ alignSelf: 'flex-end' }}>
            <span>Explore All</span>
            <ArrowRight size={14} />
          </button>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 20,
        }}>
          {exercises.map((ex) => (
            <div 
              key={ex.id} 
              className="card card-hover"
              onClick={onStartWorkout}
              style={{
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                minHeight: 220,
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <span className="badge badge-green">{ex.difficulty}</span>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                    {ex.category}
                  </span>
                </div>
                <h3 style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: 8 }}>
                  {ex.name}
                </h3>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 16 }}>
                  {ex.description}
                </p>
              </div>

              <div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  paddingTop: 12,
                  borderTop: '1px solid var(--border-subtle)',
                  fontSize: '0.82rem',
                }}>
                  <span style={{ color: 'var(--text-muted)' }}>Target: <strong>{ex.target_angle_name}</strong></span>
                  <span style={{ fontWeight: 600, color: 'var(--accent-green-dark)' }}>{ex.target_angle_range}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Pipeline Visual diagram */}
      <section className="card" style={{
        backgroundColor: '#FFFFFF',
        padding: '36px 28px',
        display: 'flex',
        flexDirection: 'column',
        gap: 24,
      }}>
        <div>
          <div className="badge badge-sky" style={{ marginBottom: 8 }}>Under The Hood</div>
          <h3 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Computer Vision Pipeline</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            FormFit AI operates in an asynchronous loop to maintain high responsiveness and low frame latency:
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
          gap: 12,
          textAlign: 'center',
        }}>
          {[
            { step: '01', title: 'Frame Capture', desc: 'Webcam / Video stream' },
            { step: '02', title: 'Pose Detection', desc: 'MediaPipe 33 keypoints' },
            { step: '03', title: 'Stabilization', desc: 'EMA / One Euro filter' },
            { step: '04', title: 'Geometry Math', desc: 'Vector angles & alignment' },
            { step: '05', title: 'State Engine', desc: 'Rep cycle validation' },
            { step: '06', title: 'Coaching Overlay', desc: 'Real-time cues & score' },
          ].map((item) => (
            <div key={item.step} style={{
              backgroundColor: 'var(--bg-primary)',
              borderRadius: 'var(--radius-md)',
              padding: '16px 12px',
              border: '1px solid var(--border-subtle)',
            }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--accent-green-dark)', marginBottom: 4 }}>
                {item.step}
              </div>
              <div style={{ fontWeight: 700, fontSize: '0.92rem', marginBottom: 4 }}>
                {item.title}
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                {item.desc}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* About Section on Landing Page */}
      <section className="card" style={{
        backgroundColor: '#FFFFFF',
        padding: '36px 28px',
        display: 'flex',
        flexDirection: 'column',
        gap: 20,
        borderLeft: '5px solid var(--accent-green)',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div className="badge badge-green" style={{ marginBottom: 6 }}>About FormFit AI</div>
            <h2 style={{ fontSize: '1.8rem', fontWeight: 800 }}>Engineered for Real Biomechanics</h2>
          </div>
          {onNavigateAbout && (
            <button onClick={onNavigateAbout} className="btn btn-secondary btn-sm">
              <span>Read Full Architecture & Story</span>
              <ArrowRight size={14} />
            </button>
          )}
        </div>

        <p style={{ color: 'var(--text-secondary)', fontSize: '0.96rem', lineHeight: 1.7, maxWidth: 840 }}>
          FormFit AI was created by <strong>Muthuselvam</strong> as Project 8 of an advanced AI software engineering portfolio. Rather than relying on simple webcam angle heuristics or black-box health predictions, FormFit AI delivers deterministic movement phase state machines, One Euro velocity-adaptive landmark filtering, and transparent 0–100 quality scoring.
        </p>

        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 16,
          paddingTop: 8,
          fontSize: '0.85rem',
          color: 'var(--text-muted)',
        }}>
          <span>• <strong>Python 3.12 & FastAPI</strong></span>
          <span>• <strong>MediaPipe Tasks API (Metal/XNNPACK)</strong></span>
          <span>• <strong>React 19 & TypeScript</strong></span>
          <span>• <strong>Zero Persistent Visual Storage</strong></span>
        </div>
      </section>
    </div>
  );
};
