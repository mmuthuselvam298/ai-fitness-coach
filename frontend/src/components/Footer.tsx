import React from 'react';
import { Shield, Lock, ExternalLink } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer style={{
      borderTop: '1px solid var(--border-subtle)',
      backgroundColor: '#FAF9F5',
      marginTop: 'auto',
      padding: '40px 20px 24px',
    }}>
      <div style={{
        maxWidth: 1200,
        margin: '0 auto',
        display: 'flex',
        flexDirection: 'column',
        gap: 24,
      }}>
        {/* Safety and Privacy callouts */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 16,
          backgroundColor: '#FFFFFF',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '16px 20px',
        }}>
          <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
            <Shield size={18} color="var(--accent-green-dark)" style={{ marginTop: 2, flexShrink: 0 }} />
            <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: 2 }}>
                Safety & Health Notice
              </strong>
              FormFit AI provides computer-vision-based exercise feedback for informational purposes only. It is not medical advice or a substitute for a qualified fitness or healthcare professional.
            </div>
          </div>

          <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
            <Lock size={18} color="var(--accent-sky)" style={{ marginTop: 2, flexShrink: 0 }} />
            <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: 2 }}>
                Privacy Commitment
              </strong>
              Camera frames are analyzed strictly in volatile memory. No video or webcam streams are ever recorded, saved, or uploaded permanently to cloud storage.
            </div>
          </div>
        </div>

        {/* Branding & links */}
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 16,
          fontSize: '0.85rem',
          color: 'var(--text-muted)',
          paddingTop: 8,
        }}>
          <div>
            © {new Date().getFullYear()} <strong>FormFit AI</strong> • Built by <strong>Muthuselvam</strong> (MIT License)
          </div>
          <div style={{ display: 'flex', gap: 20 }}>
            <a 
              href="https://github.com/mmuthuselvam298/ai-fitness-coach" 
              target="_blank" 
              rel="noreferrer"
              style={{ color: 'var(--text-secondary)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 4 }}
            >
              <span>GitHub Repository</span>
              <ExternalLink size={13} />
            </a>
            <span style={{ color: 'var(--border-strong)' }}>•</span>
            <span>FastAPI + MediaPipe + React</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
