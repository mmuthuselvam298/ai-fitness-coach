import React from 'react';
import {
  Info,
  Shield,
  Cpu,
  Compass,
  CheckCircle2,
  Lock,
  ArrowRight,
  Sparkles,
} from 'lucide-react';

interface AboutPageProps {
  onStartWorkout: () => void;
}

export const AboutPage: React.FC<AboutPageProps> = ({ onStartWorkout }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 40, maxWidth: 960, margin: '0 auto', paddingBottom: 40 }}>
      {/* Header */}
      <div>
        <div className="badge badge-green" style={{ marginBottom: 8 }}>
          <Info size={14} />
          <span>Project Philosophy & Vision</span>
        </div>
        <h1 style={{ fontSize: '2.6rem', fontWeight: 800, letterSpacing: '-0.03em' }}>
          About FormFit AI
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.15rem', marginTop: 8, lineHeight: 1.6 }}>
          A portfolio-grade computer vision system engineered to make biomechanical form analysis real-time, deterministic, and privacy-preserving.
        </p>
      </div>

      {/* Origin & Problem Statement */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 36,
            height: 36,
            borderRadius: 10,
            backgroundColor: 'var(--accent-green-light)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-green-dark)',
          }}>
            <Sparkles size={20} />
          </div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>The Core Mission</h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.96rem', lineHeight: 1.7 }}>
          Most digital fitness apps simply count time or guess calorie burn based on generic heart rate formulas. Meanwhile, typical pose detection demonstrations consist of toy scripts with hardcoded <code className="mono">if angle &lt; X: reps += 1</code> checks that trigger accidental reps from camera wobble, half-movements, and noise.
        </p>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.96rem', lineHeight: 1.7 }}>
          <strong>FormFit AI</strong> was designed from the ground up as a systematic computer vision coaching platform. It treats human exercise as a continuous physical state machine, applying mathematical rigor, coordinate smoothing, landmark confidence gating, and transparent heuristic scoring.
        </p>
      </div>

      {/* Engineering Principles */}
      <div>
        <h3 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: 16 }}>
          Engineering Principles
        </h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: 20,
        }}>
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{
              width: 42,
              height: 42,
              borderRadius: 12,
              backgroundColor: 'var(--accent-green-light)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-green-dark)',
            }}>
              <Compass size={22} />
            </div>
            <h4 style={{ fontSize: '1.15rem', fontWeight: 800 }}>Deterministic State Automata</h4>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              Movement is modeled through distinct kinematic phases: <code className="mono">READY</code> → <code className="mono">DESCENDING</code> → <code className="mono">BOTTOM</code> → <code className="mono">ASCENDING</code> → <code className="mono">COMPLETED</code>. Incomplete dips and jitter are mathematically rejected.
            </p>
          </div>

          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{
              width: 42,
              height: 42,
              borderRadius: 12,
              backgroundColor: 'var(--accent-coral-light)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-coral)',
            }}>
              <Cpu size={22} />
            </div>
            <h4 style={{ fontSize: '1.15rem', fontWeight: 800 }}>Sub-40ms Asynchronous Loop</h4>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              Using Google MediaPipe's Tasks API with Metal/XNNPACK acceleration, One Euro adaptive filtering, and bi-directional WebSocket streaming, the system maintains 28–30 real-time FPS.
            </p>
          </div>

          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{
              width: 42,
              height: 42,
              borderRadius: 12,
              backgroundColor: 'var(--accent-sky-light)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-sky)',
            }}>
              <Lock size={22} />
            </div>
            <h4 style={{ fontSize: '1.15rem', fontWeight: 800 }}>Zero Cloud Video Storage</h4>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              Camera frames are analyzed strictly in volatile heap memory and deallocated immediately. No user video feeds or photos are ever saved or uploaded to external servers.
            </p>
          </div>
        </div>
      </div>

      {/* Heuristic Scoring Model */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
        <div>
          <div className="badge badge-neutral" style={{ marginBottom: 6 }}>Mathematical Model</div>
          <h3 style={{ fontSize: '1.3rem', fontWeight: 800 }}>Transparent Form Scoring (0–100)</h3>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: 4 }}>
            FormFit AI explicitly rejects black-box or fake health claims. The form quality score is a transparent weighted formula:
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 16,
        }}>
          <div style={{
            backgroundColor: 'var(--bg-primary)',
            borderRadius: 'var(--radius-md)',
            padding: '16px',
            border: '1px solid var(--border-subtle)',
          }}>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-green-dark)' }}>Depth Quality (40%)</div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: 4 }}>
              Measures joint flexion at bottom inflection against anatomical targets (e.g. knee &le; 90° for squats).
            </p>
          </div>

          <div style={{
            backgroundColor: 'var(--bg-primary)',
            borderRadius: 'var(--radius-md)',
            padding: '16px',
            border: '1px solid var(--border-subtle)',
          }}>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-coral)' }}>Alignment (35%)</div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: 4 }}>
              Measures torso vertical uprightness (&le; 32°) and plank spine linearity (&sim; 170°–180°).
            </p>
          </div>

          <div style={{
            backgroundColor: 'var(--bg-primary)',
            borderRadius: 'var(--radius-md)',
            padding: '16px',
            border: '1px solid var(--border-subtle)',
          }}>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-sky)' }}>Cadence & Tempo (25%)</div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: 4 }}>
              Rewards smooth phase transitions between 1.5s and 4.2s without sudden bounces or rushes.
            </p>
          </div>
        </div>
      </div>

      {/* Creator & Portfolio Section */}
      <div className="card" style={{
        backgroundColor: '#FFFFFF',
        display: 'flex',
        flexDirection: 'column',
        gap: 20,
        borderLeft: '4px solid var(--text-primary)',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div className="badge badge-neutral" style={{ marginBottom: 6 }}>Portfolio Roadmap • Project 8</div>
            <h3 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Designed & Developed by Muthuselvam</h3>
            <p style={{ fontSize: '0.92rem', color: 'var(--text-secondary)', marginTop: 4 }}>
              Full-Stack Developer, AI/ML Engineer & Computer Vision Enthusiast
            </p>
          </div>

          <a
            href="https://github.com/mmuthuselvam298/ai-fitness-coach"
            target="_blank"
            rel="noreferrer"
            className="btn btn-secondary btn-sm"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
            </svg>
            <span>GitHub Profile</span>
          </a>
        </div>

        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 12,
          paddingTop: 12,
          borderTop: '1px solid var(--border-subtle)',
          fontSize: '0.85rem',
          color: 'var(--text-secondary)',
        }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <CheckCircle2 size={16} color="var(--accent-green)" />
            Python 3.12 & FastAPI
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <CheckCircle2 size={16} color="var(--accent-green)" />
            React 19 & TypeScript
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <CheckCircle2 size={16} color="var(--accent-green)" />
            MediaPipe Pose Tasks API
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <CheckCircle2 size={16} color="var(--accent-green)" />
            OpenCV & Vector Math
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <CheckCircle2 size={16} color="var(--accent-green)" />
            SQLite & WebSockets
          </span>
        </div>
      </div>

      {/* Safety & Non-Medical Disclaimer */}
      <div style={{
        backgroundColor: '#FEF3C7',
        border: '1px solid #FCD34D',
        borderRadius: 'var(--radius-md)',
        padding: '18px 22px',
        display: 'flex',
        gap: 14,
        alignItems: 'flex-start',
      }}>
        <Shield size={22} color="#B45309" style={{ marginTop: 2, flexShrink: 0 }} />
        <div style={{ fontSize: '0.88rem', color: '#78350F', lineHeight: 1.6 }}>
          <strong style={{ display: 'block', marginBottom: 4, color: '#92400E' }}>
            Important Health & Biomechanical Disclaimer
          </strong>
          FormFit AI provides computer-vision-based exercise feedback for informational and educational purposes only. It is not medical advice, physical therapy, or a substitute for a qualified fitness trainer or medical professional. It does not diagnose injuries or clinical conditions.
        </div>
      </div>

      {/* Bottom CTA */}
      <div style={{ textAlign: 'center', paddingTop: 8 }}>
        <button onClick={onStartWorkout} className="btn btn-accent btn-lg">
          <span>Start a Workout Session</span>
          <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );
};
