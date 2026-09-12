import React, { useState, useEffect, useRef } from 'react';
import {
  Play,
  Pause,
  Square,
  Activity,
  CheckCircle,
  AlertTriangle,
  Info,
  ChevronDown,
  ChevronUp,
  Camera,
  Zap,
  Upload,
  Volume2,
  VolumeX,
} from 'lucide-react';
import {
  ExerciseMetadata,
  FrameAnalysisResult,
  WorkoutSummary,
  FeedbackEvent,
} from '../types';
import { api } from '../services/api';
import { WorkoutWebSocketClient } from '../services/websocket';
import { audioCues } from '../components/AudioCues';

interface WorkoutCameraPageProps {
  exercise: ExerciseMetadata;
  targetReps: number;
  initialMode: 'webcam' | 'demo' | 'upload';
  onFinishWorkout: (summary: WorkoutSummary) => void;
  onCancel: () => void;
}

// MediaPipe skeleton connection pairs for canvas drawing
const SKELETON_PAIRS: [number, number][] = [
  [11, 12], // shoulders
  [11, 13], [13, 15], // left arm
  [12, 14], [14, 16], // right arm
  [11, 23], [12, 24], // torso
  [23, 24], // hips
  [23, 25], [25, 27], // left leg
  [24, 26], [26, 28], // right leg
];

export const WorkoutCameraPage: React.FC<WorkoutCameraPageProps> = ({
  exercise,
  targetReps,
  initialMode,
  onFinishWorkout,
  onCancel,
}) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isCalibrated, setIsCalibrated] = useState<boolean>(false);
  const [calibrationMsg, setCalibrationMsg] = useState<string>('Step back so your full body is visible in the frame');
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [isEnding, setIsEnding] = useState<boolean>(false);
  const [soundEnabled, setSoundEnabled] = useState<boolean>(true);
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false);

  // Workout Telemetry
  const [repCount, setRepCount] = useState<number>(0);
  const [phase, setPhase] = useState<string>('READY');
  const [primaryAngle, setPrimaryAngle] = useState<number>(180);
  const [angles, setAngles] = useState<Record<string, number>>({});
  const [formScore, setFormScore] = useState<number>(85);
  const [activeFeedback, setActiveFeedback] = useState<FeedbackEvent[]>([]);
  const [poseConfidence, setPoseConfidence] = useState<number>(0);
  const [inferenceMs, setInferenceMs] = useState<number>(0);
  const [realFps, setRealFps] = useState<number>(30);
  const [mode, setMode] = useState<'webcam' | 'demo' | 'upload'>(initialMode);
  const [uploadLoading, setUploadLoading] = useState<boolean>(false);

  // Timer
  const [elapsedSeconds, setElapsedSeconds] = useState<number>(0);

  // DOM Elements
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const hiddenCanvasRef = useRef<HTMLCanvasElement | null>(null);

  const wsClientRef = useRef<WorkoutWebSocketClient | null>(null);
  const animationFrameId = useRef<number | null>(null);
  const lastSendTime = useRef<number>(0);
  const prevRepCount = useRef<number>(0);

  // 1. Initialize Workout Session in Backend
  useEffect(() => {
    let mounted = true;
    api.startWorkout(exercise.id, targetReps)
      .then((res) => {
        if (!mounted) return;
        setSessionId(res.session_id);
      })
      .catch((err) => {
        console.error('Failed to start workout session:', err);
      });

    return () => {
      mounted = false;
    };
  }, [exercise.id, targetReps]);

  // 2. Timer Loop
  useEffect(() => {
    if (isPaused || !sessionId) return;
    const interval = setInterval(() => {
      setElapsedSeconds((s) => s + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [isPaused, sessionId]);

  // Format seconds to MM:SS
  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  // 3. Setup Video Source (Webcam or Demo Video)
  useEffect(() => {
    if (!sessionId) return;

    if (mode === 'webcam') {
      let stream: MediaStream | null = null;
      navigator.mediaDevices?.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
        audio: false,
      })
        .then((s) => {
          stream = s;
          if (videoRef.current) {
            videoRef.current.srcObject = s;
            videoRef.current.play().catch(() => {});
          }
        })
        .catch((err) => {
          console.warn('Webcam permission denied or unavailable, switching to demo mode', err);
          setMode('demo');
        });

      return () => {
        if (stream) {
          stream.getTracks().forEach((t) => t.stop());
        }
      };
    } else if (mode === 'demo') {
      if (videoRef.current) {
        videoRef.current.srcObject = null;
        videoRef.current.src = `http://localhost:8000/api/demo/video/${exercise.id}`;
        videoRef.current.loop = true;
        videoRef.current.muted = true;
        videoRef.current.play().catch(() => {});
      }
    }
  }, [sessionId, mode, exercise.id]);

  // 4. Connect WebSocket for Real-time Telemetry
  useEffect(() => {
    if (!sessionId) return;

    const ws = new WorkoutWebSocketClient(
      sessionId,
      (data: FrameAnalysisResult) => {
        handleIncomingAnalysis(data);
      },
      (err) => {
        console.warn('WebSocket stream fallback to REST frame', err);
      }
    );

    ws.connect().catch(() => {});
    wsClientRef.current = ws;

    return () => {
      ws.disconnect();
    };
  }, [sessionId]);

  // Handle incoming frame analysis result
  const handleIncomingAnalysis = (data: FrameAnalysisResult) => {
    if (data.rep_count !== undefined) {
      if (data.rep_count > prevRepCount.current) {
        prevRepCount.current = data.rep_count;
        if (soundEnabled) audioCues.playRepChime();
      }
      setRepCount(data.rep_count);
    }

    if (data.phase) setPhase(data.phase);
    if (data.primary_angle !== undefined) setPrimaryAngle(data.primary_angle);
    if (data.angles) setAngles(data.angles);
    if (data.form_score !== undefined) setFormScore(data.form_score);
    if (data.confidence !== undefined) setPoseConfidence(data.confidence);
    if (data.inference_ms !== undefined) setInferenceMs(data.inference_ms);
    if (data.fps !== undefined) setRealFps(data.fps);

    if (data.is_calibrated !== undefined) {
      setIsCalibrated(data.is_calibrated);
      if (data.calibration_message) {
        setCalibrationMsg(data.calibration_message);
      }
    }

    if (data.feedback && data.feedback.length > 0) {
      setActiveFeedback(data.feedback);
      const hasWarning = data.feedback.some((f) => f.severity === 'warning');
      if (hasWarning && soundEnabled) {
        audioCues.playWarningPing();
      }
    }

    // Draw skeleton overlay on canvas
    if (data.landmarks && canvasRef.current && videoRef.current) {
      drawSkeleton(data.landmarks);
    }
  };

  // Draw synchronized pose skeleton on HTML5 Canvas
  const drawSkeleton = (landmarks: Record<number, { x: number; y: number; visibility: number }>) => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const w = canvas.width;
    const h = canvas.height;

    // Draw bones / connections
    ctx.lineWidth = 4;
    ctx.strokeStyle = '#10B981'; // Fresh green accent
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    for (const [p1, p2] of SKELETON_PAIRS) {
      const pt1 = landmarks[p1];
      const pt2 = landmarks[p2];
      if (pt1 && pt2 && pt1.visibility >= 0.5 && pt2.visibility >= 0.5) {
        ctx.beginPath();
        ctx.moveTo(pt1.x * w, pt1.y * h);
        ctx.lineTo(pt2.x * w, pt2.y * h);
        ctx.stroke();
      }
    }

    // Draw landmark joints
    for (const [idxStr, pt] of Object.entries(landmarks)) {
      const idx = Number(idxStr);
      if (pt.visibility >= 0.5 && idx >= 11 && idx <= 28) {
        const cx = pt.x * w;
        const cy = pt.y * h;

        // Outer white ring
        ctx.fillStyle = '#FFFFFF';
        ctx.beginPath();
        ctx.arc(cx, cy, 6, 0, 2 * Math.PI);
        ctx.fill();

        // Inner green core
        ctx.fillStyle = '#059669';
        ctx.beginPath();
        ctx.arc(cx, cy, 4, 0, 2 * Math.PI);
        ctx.fill();
      }
    }
  };

  // 5. Frame Grab & Dispatch Loop
  useEffect(() => {
    if (!sessionId || isPaused) return;

    const captureFrame = () => {
      const video = videoRef.current;
      if (video && video.readyState >= 2) {
        const now = performance.now();
        // Throttle to ~20-25 FPS for optimal bandwidth & performance
        if (now - lastSendTime.current >= 40) {
          lastSendTime.current = now;

          if (!hiddenCanvasRef.current) {
            hiddenCanvasRef.current = document.createElement('canvas');
          }
          const hCanvas = hiddenCanvasRef.current;
          hCanvas.width = 480;
          hCanvas.height = 360;
          const hCtx = hCanvas.getContext('2d');
          if (hCtx) {
            hCtx.drawImage(video, 0, 0, 480, 360);
            const dataUrl = hCanvas.toDataURL('image/jpeg', 0.65);
            if (wsClientRef.current) {
              wsClientRef.current.sendFrame(dataUrl, now / 1000);
            }
          }
        }
      }
      animationFrameId.current = requestAnimationFrame(captureFrame);
    };

    animationFrameId.current = requestAnimationFrame(captureFrame);

    return () => {
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, [sessionId, isPaused]);

  // Finish Workout Session
  const handleFinish = async () => {
    if (!sessionId || isEnding) return;
    setIsEnding(true);
    try {
      const summary = await api.finishWorkout(sessionId);
      onFinishWorkout(summary);
    } catch (err) {
      console.error('Failed to complete workout session:', err);
      setIsEnding(false);
    }
  };

  // Upload custom video file handler
  const handleVideoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadLoading(true);
    try {
      const result = await api.analyzeVideo(file, exercise.id);
      // Produce workout summary from video analysis
      const syntheticSummary: WorkoutSummary = {
        id: sessionId || 'upload-session',
        exercise: exercise.id,
        started_at: new Date().toISOString(),
        duration_seconds: result.processing_time_seconds,
        target_reps: targetReps,
        completed_reps: result.completed_reps,
        average_form_score: result.average_form_score,
        depth_score: result.score_breakdown.depth,
        alignment_score: result.score_breakdown.alignment,
        consistency_score: result.score_breakdown.consistency,
        status: 'completed',
        reps_detail: result.reps_detail,
        what_went_well: ['Successfully processed uploaded exercise video', 'Accurate repetition tracking'],
        focus_next_time: ['Continue maintaining smooth cadence across sets'],
      };
      onFinishWorkout(syntheticSummary);
    } catch (err: any) {
      alert(`Upload analysis error: ${err.message}`);
    } finally {
      setUploadLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20, maxWidth: 1080, margin: '0 auto' }}>
      {/* Top Athletic Status Bar */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '12px 20px',
        backgroundColor: '#FFFFFF',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)',
        gap: 12,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 10,
            height: 10,
            borderRadius: '50%',
            backgroundColor: isPaused ? 'var(--status-warning)' : 'var(--accent-green)',
          }} />
          <div>
            <div style={{ fontSize: '1.05rem', fontWeight: 800 }}>{exercise.name}</div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Goal: {targetReps} reps • Mode: {mode.toUpperCase()}
            </div>
          </div>
        </div>

        {/* Timer & Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div className="mono" style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            {formatTime(elapsedSeconds)}
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={() => setSoundEnabled(!soundEnabled)}
              className="btn btn-secondary btn-sm"
              title={soundEnabled ? 'Mute Sound' : 'Enable Sound'}
              style={{ width: 36, height: 36, padding: 0 }}
            >
              {soundEnabled ? <Volume2 size={16} /> : <VolumeX size={16} color="var(--text-muted)" />}
            </button>

            <button
              onClick={() => setIsPaused(!isPaused)}
              className="btn btn-secondary btn-sm"
              style={{ width: 36, height: 36, padding: 0 }}
              title={isPaused ? 'Resume' : 'Pause'}
            >
              {isPaused ? <Play size={16} /> : <Pause size={16} />}
            </button>

            <button
              onClick={handleFinish}
              disabled={isEnding}
              className="btn btn-primary btn-sm"
              style={{ backgroundColor: '#181A1B', color: '#FFFFFF' }}
            >
              <Square size={14} fill="#FFFFFF" />
              <span>{isEnding ? 'Finalizing...' : 'Finish'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Studio Viewport & Pose Overlay */}
      <div style={{
        position: 'relative',
        width: '100%',
        aspectRatio: '16 / 10',
        maxHeight: '620px',
        backgroundColor: '#1E2022',
        borderRadius: 'var(--radius-xl)',
        overflow: 'hidden',
        boxShadow: 'var(--shadow-float)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        {/* Video stream */}
        <video
          ref={videoRef}
          playsInline
          muted
          autoPlay
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            transform: mode === 'webcam' ? 'scaleX(-1)' : 'none', // mirror webcam
          }}
        />

        {/* Real-time skeleton canvas overlay */}
        <canvas
          ref={canvasRef}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            pointerEvents: 'none',
            transform: mode === 'webcam' ? 'scaleX(-1)' : 'none',
          }}
        />

        {/* Live Calibration Banner if not ready */}
        {!isCalibrated && (
          <div style={{
            position: 'absolute',
            top: 20,
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: 'rgba(28, 30, 33, 0.90)',
            color: '#FFFFFF',
            padding: '10px 20px',
            borderRadius: 'var(--radius-full)',
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            fontSize: '0.85rem',
            fontWeight: 600,
            backdropFilter: 'blur(8px)',
            zIndex: 10,
          }}>
            <AlertTriangle size={16} color="var(--accent-coral)" />
            <span>{calibrationMsg}</span>
          </div>
        )}

        {/* Oversized Athletic Rep Counter Overlay (Top Right) */}
        <div style={{
          position: 'absolute',
          top: 20,
          right: 24,
          textAlign: 'right',
          zIndex: 10,
          userSelect: 'none',
          backgroundColor: 'rgba(255, 255, 255, 0.92)',
          padding: '12px 24px',
          borderRadius: 'var(--radius-lg)',
          backdropFilter: 'blur(10px)',
          boxShadow: 'var(--shadow-md)',
        }}>
          <div className="rep-display" style={{ color: 'var(--text-primary)' }}>
            {repCount}
          </div>
          <div className="rep-label">
            REPS • TARGET {targetReps}
          </div>
        </div>

        {/* Movement Phase Pill (Top Left) */}
        <div style={{
          position: 'absolute',
          top: 24,
          left: 24,
          zIndex: 10,
          display: 'flex',
          flexDirection: 'column',
          gap: 6,
        }}>
          <div className="badge badge-green" style={{ fontSize: '0.85rem', padding: '6px 14px' }}>
            <Activity size={14} />
            <span>PHASE: {phase.toUpperCase()}</span>
          </div>

          <div style={{
            backgroundColor: 'rgba(28, 30, 33, 0.85)',
            color: '#FFFFFF',
            padding: '6px 14px',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.78rem',
            fontWeight: 600,
            backdropFilter: 'blur(6px)',
          }}>
            {exercise.target_angle_name}: {Math.round(primaryAngle)}°
          </div>
        </div>

        {/* Dynamic Coaching Prompt Badge (Bottom Center) */}
        <div style={{
          position: 'absolute',
          bottom: 24,
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 10,
          maxWidth: '85%',
          textAlign: 'center',
        }}>
          {activeFeedback.length > 0 ? (
            <div style={{
              backgroundColor: activeFeedback[0].severity === 'warning'
                ? 'rgba(249, 115, 22, 0.95)'
                : activeFeedback[0].severity === 'good'
                ? 'rgba(16, 185, 129, 0.95)'
                : 'rgba(28, 30, 33, 0.90)',
              color: '#FFFFFF',
              padding: '12px 24px',
              borderRadius: 'var(--radius-full)',
              fontSize: '1rem',
              fontWeight: 700,
              boxShadow: '0 8px 24px rgba(0,0,0,0.2)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              transition: 'all 0.2s ease',
            }}>
              {activeFeedback[0].severity === 'good' && <CheckCircle size={18} />}
              {activeFeedback[0].severity === 'warning' && <AlertTriangle size={18} />}
              {activeFeedback[0].severity === 'info' && <Info size={18} />}
              <span>{activeFeedback[0].message}</span>
            </div>
          ) : (
            <div style={{
              backgroundColor: 'rgba(28, 30, 33, 0.80)',
              color: '#D1D5DB',
              padding: '8px 20px',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.85rem',
              fontWeight: 600,
            }}>
              Maintain smooth form and tempo
            </div>
          )}
        </div>
      </div>

      {/* Target Progress Bar */}
      <div style={{
        backgroundColor: '#FFFFFF',
        borderRadius: 'var(--radius-md)',
        padding: '16px 20px',
        border: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        gap: 8,
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 700 }}>
          <span style={{ color: 'var(--text-secondary)' }}>Workout Target Progress</span>
          <span style={{ color: 'var(--accent-green-dark)' }}>{repCount} of {targetReps} reps ({Math.min(100, Math.round((repCount / targetReps) * 100))}%)</span>
        </div>
        <div style={{ width: '100%', height: 8, backgroundColor: 'var(--bg-subtle)', borderRadius: 4, overflow: 'hidden' }}>
          <div style={{
            height: '100%',
            width: `${Math.min(100, (repCount / targetReps) * 100)}%`,
            backgroundColor: 'var(--accent-green)',
            transition: 'width 0.3s ease-out',
          }} />
        </div>
      </div>

      {/* Camera Mode Switcher & Upload Option */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: 'var(--bg-surface)',
        padding: '12px 18px',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)',
        gap: 12,
      }}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-muted)' }}>Source:</span>
          <button
            onClick={() => setMode('webcam')}
            className={`btn btn-sm ${mode === 'webcam' ? 'btn-primary' : 'btn-secondary'}`}
          >
            <Camera size={14} />
            <span>Webcam</span>
          </button>
          <button
            onClick={() => setMode('demo')}
            className={`btn btn-sm ${mode === 'demo' ? 'btn-primary' : 'btn-secondary'}`}
          >
            <Zap size={14} color="var(--accent-coral)" />
            <span>Sample Video</span>
          </button>
          <label className="btn btn-secondary btn-sm" style={{ cursor: 'pointer', margin: 0 }}>
            <Upload size={14} />
            <span>{uploadLoading ? 'Processing...' : 'Upload Video'}</span>
            <input
              type="file"
              accept="video/mp4,video/webm"
              onChange={handleVideoUpload}
              style={{ display: 'none' }}
              disabled={uploadLoading}
            />
          </label>
        </div>

        {/* Collapsible Advanced CV Telemetry Toggle */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="btn btn-secondary btn-sm"
          style={{ border: 'none' }}
        >
          <span>Advanced CV Metrics</span>
          {showAdvanced ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
        </button>
      </div>

      {/* Advanced Analysis Collapsible Telemetry HUD */}
      {showAdvanced && (
        <div className="card" style={{
          backgroundColor: '#FFFFFF',
          padding: '20px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: 16,
        }}>
          <div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Real-time FPS
            </div>
            <div className="mono" style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-green-dark)' }}>
              {realFps} <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>fps</span>
            </div>
          </div>

          <div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Inference Latency
            </div>
            <div className="mono" style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)' }}>
              {inferenceMs} <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>ms</span>
            </div>
          </div>

          <div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Pose Confidence
            </div>
            <div className="mono" style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)' }}>
              {Math.round(poseConfidence * 100)}%
            </div>
          </div>

          <div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Current Form Score
            </div>
            <div className="mono" style={{ fontSize: '1.5rem', fontWeight: 800, color: formScore >= 80 ? 'var(--accent-green-dark)' : 'var(--accent-coral)' }}>
              {Math.round(formScore)} / 100
            </div>
          </div>

          {Object.entries(angles).map(([k, v]) => (
            <div key={k}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                {k.replace(/_/g, ' ')}
              </div>
              <div className="mono" style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--text-secondary)' }}>
                {Math.round(v)}°
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
