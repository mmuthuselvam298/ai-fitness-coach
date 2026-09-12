# FormFit AI — System Architecture

## 1. High-Level Architectural Overview

FormFit AI employs an asynchronous, event-driven computer vision pipeline designed for sub-40ms end-to-end latency across video processing, landmark stabilization, kinematic state transitions, and UI overlay rendering.

```mermaid
flowchart TD
    subgraph CaptureLayer ["Input / Capture Layer"]
        A1[Webcam Stream]
        A2[Demo Test Clips]
        A3[User Video Upload]
    end

    subgraph TransportLayer ["Transport & Session Layer"]
        B1[HTML5 Canvas Throttler ~25fps]
        B2[WebSocket /api/ws/workout/:id]
        B3[REST Fallback /api/analyze/frame]
    end

    subgraph VisionPipeline ["Python Computer Vision Engine"]
        C1[MediaPipe PoseLandmarker Tasks API]
        C2[Confidence & Visibility Gating]
        C3[One Euro / Exponential Moving Average Smoothing]
        C4[Biomechanical Vector Geometry Engine]
    end

    subgraph StateMachineLayer ["Kinematic State Machines"]
        D1[SquatAnalyzer]
        D2[PushupAnalyzer]
        D3[BicepCurlAnalyzer]
    end

    subgraph FeedbackScoringLayer ["Feedback & Heuristic Scoring"]
        E1[Debounced Coaching Engine]
        E2[Depth Flexion Evaluator 40%]
        E3[Postural Alignment Evaluator 35%]
        E4[Movement Cadence Evaluator 25%]
    end

    subgraph PersistenceLayer ["Persistence & Analytics Layer"]
        F1[(SQLite Database)]
        F2[Workout History Store]
        F3[Volume & Progress Analytics]
    end

    subgraph PresentationLayer ["MOTION Theme Frontend"]
        G1[Real-time Skeleton Canvas Overlay]
        G2[Oversized Rep Display]
        G3[Web Audio Chimes]
        G4[Telemetry HUD - FPS & Angles]
    end

    A1 & A2 --> B1
    A3 --> B3
    B1 --> B2
    B2 --> C1
    B3 --> C1
    C1 --> C2
    C2 --> C3
    C3 --> C4
    C4 --> D1 & D2 & D3
    D1 & D2 & D3 --> E1 & E2 & E3 & E4
    E1 & E2 & E3 & E4 --> B2
    E1 & E2 & E3 & E4 --> F1
    F1 --> F2 & F3
    B2 --> G1 & G2 & G3 & G4
```

## 2. Component Breakdown

### A. Computer Vision Engine (`backend/app/vision/`)
- **PoseLandmarker**: Modern Google MediaPipe Tasks API running with Metal / XNNPACK hardware acceleration.
- **Landmark Filtering**: Low-pass Exponential Moving Average (EMA) and 1D One Euro filters minimize high-frequency camera jitter while preserving zero-latency response during rapid explosive lifts.
- **Geometry Module**: Vector dot product and $\arccos$ calculation with numerical clipping prevents NaN errors in degenerate configurations.

### B. Kinematic State Machines (`backend/app/exercises/`)
Exercises derive from `ExerciseAnalyzer` and model physical exercise as deterministic finite state automata:
- **Squat**: `READY` $\to$ `DESCENDING` $\to$ `BOTTOM` $\to$ `ASCENDING` $\to$ `COMPLETED` $\to$ `READY`.
- **Push-up**: `TOP` $\to$ `DESCENDING` $\to$ `BOTTOM` $\to$ `ASCENDING` $\to$ `COMPLETED` $\to$ `TOP`.
- **Bicep Curl**: `EXTENDED` $\to$ `CURLING` $\to$ `CONTRACTED` $\to$ `RETURNING` $\to$ `COMPLETED` $\to$ `EXTENDED`.

Repetition counts increment **only** after crossing the bottom inflection threshold and returning to the completed upright state. Incomplete or aborted dips are automatically discarded without false increments.

### C. Heuristic Form Scoring Engine
Repetitions receive a deterministic form quality score between 0 and 100:
$$\text{Score} = 0.40 \times \text{Depth} + 0.35 \times \text{Alignment} + 0.25 \times \text{Cadence}$$

### D. Persistence (`backend/app/models/database.py`)
Lightweight SQLite relational schema with dedicated indexes on `started_at`, `exercise`, and `session_id`. All session reps and notable coaching feedback events are stored in relational tables for longitudinal analytics.
