import { FrameAnalysisResult } from '../types';

export class WorkoutWebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private onAnalysisCallback: (data: FrameAnalysisResult) => void;
  private onErrorCallback?: (err: any) => void;
  private isConnected = false;

  constructor(
    sessionId: string,
    onAnalysis: (data: FrameAnalysisResult) => void,
    onError?: (err: any) => void
  ) {
    const wsBase = (import.meta.env.VITE_API_URL || 'http://localhost:8000')
      .replace(/^http/, 'ws');
    this.url = `${wsBase}/api/ws/workout/${sessionId}`;
    this.onAnalysisCallback = onAnalysis;
    this.onErrorCallback = onError;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          this.isConnected = true;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data: FrameAnalysisResult = JSON.parse(event.data);
            this.onAnalysisCallback(data);
          } catch (e) {
            console.error('Failed to parse WebSocket message', e);
          }
        };

        this.ws.onerror = (err) => {
          if (this.onErrorCallback) this.onErrorCallback(err);
          reject(err);
        };

        this.ws.onclose = () => {
          this.isConnected = false;
        };
      } catch (err) {
        reject(err);
      }
    });
  }

  sendFrame(imageBase64: string, timestamp?: number) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(
      JSON.stringify({
        image_base64: imageBase64,
        timestamp: timestamp || performance.now() / 1000,
      })
    );
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
    }
  }
}
