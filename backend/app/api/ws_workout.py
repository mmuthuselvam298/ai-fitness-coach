"""Real-time low-latency WebSocket endpoint for live camera streaming."""

import base64
import json
import time

import cv2
import numpy as np
from app.core.logging import logger
from app.services.workout_service import workout_service
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/workout/{session_id}")
async def workout_websocket_endpoint(websocket: WebSocket, session_id: str):
    """Real-time bi-directional streaming for camera frames and pose telemetry."""
    await websocket.accept()
    logger.info(f"WebSocket client connected to session: {session_id}")

    session = workout_service.active_sessions.get(session_id)
    if not session:
        await websocket.send_json({"error": "Session not found or expired"})
        await websocket.close()
        return

    last_frame_time = time.perf_counter()
    frame_count = 0

    try:
        while True:
            # Receive either binary data or text json
            message = await websocket.receive()

            client_start_t = time.perf_counter()
            frame_bgr = None
            client_timestamp = None

            if message.get("bytes"):
                np_arr = np.frombuffer(message["bytes"], np.uint8)
                frame_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            elif message.get("text"):
                try:
                    payload = json.loads(message["text"])
                    if payload.get("action") == "ping":
                        await websocket.send_json({"action": "pong"})
                        continue

                    img_b64 = payload.get("image_base64")
                    client_timestamp = payload.get("timestamp")
                    if img_b64:
                        split = img_b64.split(",")
                        raw = base64.b64decode(split[1] if len(split) > 1 else split[0])
                        np_arr = np.frombuffer(raw, np.uint8)
                        frame_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                except Exception as e:
                    await websocket.send_json({"error": f"Invalid frame payload: {e}"})
                    continue

            if frame_bgr is None:
                await websocket.send_json({"error": "Failed to decode frame"})
                continue

            # Process frame through vision engine and state machine
            res = workout_service.process_frame(
                session_id=session_id,
                frame_bgr=frame_bgr,
                timestamp=client_timestamp,
            )

            # Compute real FPS and round-trip processing time
            now_t = time.perf_counter()
            server_processing_ms = round((now_t - client_start_t) * 1000.0, 1)
            frame_count += 1
            elapsed_total = now_t - last_frame_time
            current_fps = round(frame_count / elapsed_total, 1) if elapsed_total >= 1.0 else 30.0
            if elapsed_total >= 1.0:
                frame_count = 0
                last_frame_time = now_t

            res["server_processing_ms"] = server_processing_ms
            res["fps"] = current_fps

            await websocket.send_json(res)

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket stream error: {e}")
        try:
            await websocket.close()
        except Exception:
            pass
