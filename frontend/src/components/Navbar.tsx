import React, { useState, useEffect } from 'react';
import { Activity, Play, BarChart2, History, Shield, Zap } from 'lucide-react';
import { api } from '../services/api';

interface NavbarProps {
  currentView: string;
  onNavigate: (view: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentView, onNavigate }) => {
  const [engineReady, setEngineReady] = useState(false);

  useEffect(() => {
    api.getHealth()
      .then((data) => {
        if (data?.vision_engine?.model_ready) {
          setEngineReady(true);
        }
      })
      .catch(() => setEngineReady(false));
  }, []);

  return (
    <header style={{
      borderBottom: '1px solid var(--border-subtle)',
      backgroundColor: 'rgba(250, 249, 245, 0.95)',
      backdropFilter: 'blur(8px)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
    }}>
      <div style={{
        maxWidth: 1200,
        margin: '0 auto',
        padding: '16px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        {/* Brand Logo */}
        <div 
          onClick={() => onNavigate('landing')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            cursor: 'pointer',
            userSelect: 'none',
          }}
        >
          {/* Abstract movement arc + motion icon */}
          <div style={{
            width: 38,
            height: 38,
            borderRadius: 12,
            backgroundColor: 'var(--text-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#FFFFFF',
            position: 'relative',
          }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 4l-4 4 3 3-4 4 3 3" />
              <circle cx="6" cy="12" r="3" fill="#10B981" stroke="none" />
            </svg>
          </div>
          <div>
            <div style={{
              fontSize: '1.15rem',
              fontWeight: 800,
              letterSpacing: '-0.03em',
              lineHeight: 1.1,
              color: 'var(--text-primary)',
            }}>
              FORMFIT
            </div>
            <div style={{
              fontSize: '0.68rem',
              fontWeight: 700,
              letterSpacing: '0.12em',
              color: 'var(--accent-green-dark)',
              textTransform: 'uppercase',
            }}>
              AI Fitness Coach
            </div>
          </div>
        </div>

        {/* Navigation items */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <button
            onClick={() => onNavigate('exercises')}
            className={`btn btn-sm ${currentView === 'exercises' || currentView === 'workout' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ border: 'none' }}
          >
            <Play size={15} />
            <span>Workout</span>
          </button>

          <button
            onClick={() => onNavigate('demo')}
            className={`btn btn-sm ${currentView === 'demo' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ border: 'none' }}
          >
            <Zap size={15} color="var(--accent-coral)" />
            <span>Demo Mode</span>
          </button>

          <button
            onClick={() => onNavigate('history')}
            className={`btn btn-sm ${currentView === 'history' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ border: 'none' }}
          >
            <History size={15} />
            <span>History</span>
          </button>

          <button
            onClick={() => onNavigate('analytics')}
            className={`btn btn-sm ${currentView === 'analytics' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ border: 'none' }}
          >
            <BarChart2 size={15} />
            <span>Progress</span>
          </button>
        </nav>

        {/* System telemetry indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div className="badge badge-green" style={{ fontSize: '0.75rem' }}>
            <span className="pulse-dot" style={{ backgroundColor: engineReady ? 'var(--accent-green)' : '#F59E0B' }}></span>
            <span>{engineReady ? 'Vision Engine Active' : 'Connecting...'}</span>
          </div>
        </div>
      </div>
    </header>
  );
};
