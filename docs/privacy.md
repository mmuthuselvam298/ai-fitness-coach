# FormFit AI — Privacy & Security Architecture

FormFit AI adheres to a strict **Zero Persistent Visual Retention** policy.

---

## 1. Ephemeral In-Memory Frame Processing
- All webcam and camera frames are streamed directly to volatile heap memory (RAM).
- Frames are decoded, evaluated for 33 landmark coordinates, and immediately deallocated.
- No images, video segments, or uncompressed frames are ever written to disk or uploaded to external cloud APIs.

## 2. Temporary File Handling Policy
- When users opt to upload an existing video recording (`POST /api/analyze/video`), the video file is stored in an isolated, randomized temporary directory (`tempfile.mkdtemp`).
- Immediately upon completing the frame extraction loop, a `finally:` block executes `shutil.rmtree(temp_dir)`, permanently removing the uploaded media from disk.

## 3. Telemetry & Stored Data
Only non-visual numerical metadata is persisted in the local SQLite database:
- Workout session ID (UUID)
- Exercise category name
- Repetition count and timestamp
- Aggregated heuristic form score (0–100)
- Structured coaching prompt text (e.g. *"Great squat depth"*)

Users maintain complete autonomy to inspect or wipe their local database file (`data/formfit.db`) at any time.
