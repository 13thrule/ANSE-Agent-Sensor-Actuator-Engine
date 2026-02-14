/**
 * anseClient.ts - Minimal WebSocket client for ANSE Dashboard
 * 
 * Usage:
 *   import { connect, call } from './anseClient';
 *   
 *   await connect();
 *   const frame = await call('get_camera_frame');
 *   const motors = await call('get_motor_status');
 */

const WS_URL = process.env.VITE_ANSE_WS || "ws://127.0.0.1:8765";

let ws: WebSocket | null = null;
let nextId = 1;
const pending = new Map<number, { resolve: (v: any) => void; reject: (e: Error) => void }>();

export interface CallOptions {
  timeout?: number;
}

/**
 * Connect to ANSE WebSocket server
 */
export function connect(): Promise<void> {
  return new Promise((resolve, reject) => {
    try {
      ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        console.log("[ANSE] Connected to", WS_URL);
        resolve();
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          
          // Handle RPC response
          if (msg.id && pending.has(msg.id)) {
            const { resolve } = pending.get(msg.id)!;
            pending.delete(msg.id);
            resolve(msg.result || msg.error);
          }
          
          // Handle push notifications (world model updates, etc.)
          if (msg.method === "notify") {
            console.log("[ANSE NOTIFY]", msg.params);
            // Dispatch custom events here if needed
          }
        } catch (e) {
          console.error("[ANSE] Failed to parse message:", e);
        }
      };

      ws.onerror = (event) => {
        console.error("[ANSE] WebSocket error:", event);
        reject(new Error("WebSocket connection failed"));
      };

      ws.onclose = () => {
        console.log("[ANSE] Disconnected");
      };
    } catch (e) {
      reject(e);
    }
  });
}

/**
 * Call a dashboard_bridge tool via JSON-RPC
 * 
 * @param method - Tool name (e.g., 'get_camera_frame' or full 'dashboard_bridge.get_camera_frame')
 * @param params - Tool parameters (optional)
 * @param options - Call options (timeout, etc.)
 * @returns Promise that resolves to the tool result
 */
export function call(
  method: string,
  params: Record<string, any> = {},
  options: CallOptions = {}
): Promise<any> {
  return new Promise((resolve, reject) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      return reject(new Error("WebSocket not connected"));
    }

    const id = nextId++;
    const fullMethod = method.includes(".") ? method : `dashboard_bridge.${method}`;
    
    const timer = options.timeout 
      ? setTimeout(() => {
          pending.delete(id);
          reject(new Error(`RPC timeout: ${method}`));
        }, options.timeout)
      : null;

    pending.set(id, {
      resolve: (result) => {
        if (timer) clearTimeout(timer);
        resolve(result);
      },
      reject: (error) => {
        if (timer) clearTimeout(timer);
        reject(error);
      }
    });

    ws!.send(JSON.stringify({
      jsonrpc: "2.0",
      method: fullMethod,
      params,
      id
    }));
  });
}

/**
 * Disconnect from ANSE
 */
export function disconnect(): void {
  if (ws) {
    ws.close();
    ws = null;
  }
}

/**
 * Check if connected
 */
export function isConnected(): boolean {
  return ws !== null && ws.readyState === WebSocket.OPEN;
}

/**
 * Subscribe to push notifications
 */
export function onNotify(callback: (method: string, params: any) => void): () => void {
  const originalOnMessage = ws?.onmessage;
  
  if (ws) {
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.method === "notify") {
        callback(msg.method, msg.params);
      }
      originalOnMessage?.call(ws, event);
    };
  }

  return () => {
    if (ws && originalOnMessage) {
      ws.onmessage = originalOnMessage;
    }
  };
}
