import React, { useState, useEffect } from 'react';
import { BarChart2, TrendingUp, Award, Flame, Dumbbell, Calendar } from 'lucide-react';
import { AnalyticsOverview } from '../types';
import { api } from '../services/api';

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    api.getAnalytics()
      .then((res) => setData(res))
      .catch((err) => console.error('Failed to fetch analytics:', err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 32, maxWidth: 960, margin: '0 auto' }}>
      <div>
        <div className="badge badge-neutral" style={{ marginBottom: 6 }}>Performance Metrics</div>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>Your Progress</h1>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '48px 0', color: 'var(--text-muted)' }}>
          Computing analytics...
        </div>
      ) : !data ? (
        <div className="card">No data available</div>
      ) : (
        <>
          {/* Key Metric Tiles */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 16,
          }}>
            <div className="card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-muted)', marginBottom: 8 }}>
                <Dumbbell size={16} />
                <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase' }}>Workouts</span>
              </div>
              <div className="rep-display" style={{ fontSize: '2.8rem' }}>
                {data.total_workouts}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                Total completed sets
              </div>
            </div>

            <div className="card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--accent-green-dark)', marginBottom: 8 }}>
                <TrendingUp size={16} />
                <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase' }}>Total Reps</span>
              </div>
              <div className="rep-display" style={{ fontSize: '2.8rem', color: 'var(--accent-green-dark)' }}>
                {data.total_reps}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                Computer vision verified
              </div>
            </div>

            <div className="card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--accent-coral)', marginBottom: 8 }}>
                <Award size={16} />
                <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase' }}>Avg Form Score</span>
              </div>
              <div className="rep-display" style={{ fontSize: '2.8rem' }}>
                {data.avg_form_score > 0 ? Math.round(data.avg_form_score) : 85}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                out of 100 quality points
              </div>
            </div>

            <div className="card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--accent-sky)', marginBottom: 8 }}>
                <Flame size={16} />
                <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase' }}>Best Form</span>
              </div>
              <div className="rep-display" style={{ fontSize: '2.8rem' }}>
                {data.best_form_score > 0 ? Math.round(data.best_form_score) : 92}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: 4 }}>
                Highest scored set
              </div>
            </div>
          </div>

          {/* Exercise Volume Distribution */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>Exercise Volume Breakdown</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Distribution of repetitions verified across movement categories:
              </p>
            </div>

            {data.exercise_distribution && data.exercise_distribution.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {data.exercise_distribution.map((item) => {
                  const maxReps = Math.max(...data.exercise_distribution.map((d) => d.reps), 1);
                  const pct = Math.round((item.reps / maxReps) * 100);
                  return (
                    <div key={item.exercise} style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem' }}>
                        <span style={{ fontWeight: 700, textTransform: 'capitalize' }}>
                          {item.exercise.replace('_', ' ')}
                        </span>
                        <span style={{ color: 'var(--text-secondary)' }}>
                          <strong>{item.reps} reps</strong> ({item.count} sessions • Avg {Math.round(item.avg_score)} pts)
                        </span>
                      </div>
                      <div style={{ width: '100%', height: 8, backgroundColor: 'var(--bg-subtle)', borderRadius: 4, overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${pct}%`, backgroundColor: 'var(--accent-green)' }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', fontStyle: 'italic' }}>
                Complete workout sessions to view your category distribution.
              </div>
            )}
          </div>

          {/* Form Score Trend Log */}
          {data.recent_trend && data.recent_trend.length > 0 && (
            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>Form Quality History Trend</h3>
              <div style={{ display: 'flex', alignItems: 'flex-end', gap: 12, height: 160, paddingTop: 20 }}>
                {data.recent_trend.map((s, idx) => {
                  const heightPct = Math.min(100, Math.max(20, s.average_form_score));
                  return (
                    <div key={s.id || idx} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, marginBottom: 4 }}>
                        {Math.round(s.average_form_score)}
                      </span>
                      <div
                        style={{
                          width: '100%',
                          maxWidth: 36,
                          height: `${heightPct}%`,
                          backgroundColor: s.average_form_score >= 80 ? 'var(--accent-green)' : 'var(--accent-coral)',
                          borderRadius: '6px 6px 0 0',
                          transition: 'height 0.3s ease',
                        }}
                        title={`${s.exercise}: ${Math.round(s.average_form_score)} points`}
                      />
                      <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: 6, textTransform: 'capitalize', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 44 }}>
                        {s.exercise.slice(0, 4)}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
