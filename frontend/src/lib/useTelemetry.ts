"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type {
  AnalysisResult,
  ClientMessage,
  ConnectionStatus,
  HistoryPoint,
  ServerMessage,
  Telemetry,
} from "./types";
import { clockLabel } from "./telemetry-utils";

const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL ?? "ws://127.0.0.1:8000/ws/telemetry";

/** Rolling window of telemetry snapshots retained for the live chart. */
const HISTORY_LIMIT = 30;

/** Reconnection backoff (ms): capped exponential, reset on a clean connect. */
const RECONNECT_BASE = 1_000;
const RECONNECT_MAX = 15_000;

export interface UseTelemetry {
  status: ConnectionStatus;
  /** Latest full telemetry snapshot, or null before the first message. */
  telemetry: Telemetry | null;
  /** Rolling history (oldest → newest), capped at HISTORY_LIMIT points. */
  history: HistoryPoint[];
  /** Latest analysis result from the agent graph, or null. */
  analysis: AnalysisResult | null;
  /** True between `analysis_started` and its `analysis_result`. */
  analysisRunning: boolean;
  /** True once at least one telemetry frame has arrived. */
  hasData: boolean;
  /** Trigger a manual analysis run. */
  requestAnalysis: () => void;
  /** Approve a paused plan by thread id. */
  approvePlan: (threadId: string) => void;
  /** Locally dismiss the current analysis (e.g. close the modal). */
  dismissAnalysis: () => void;
}

/**
 * Manages the single two-way telemetry WebSocket: connection lifecycle,
 * latest snapshot, rolling chart history, analysis state, and the
 * analyse/approve commands. Reconnects automatically with capped backoff.
 */
export function useTelemetry(): UseTelemetry {
  const [status, setStatus] = useState<ConnectionStatus>("connecting");
  const [telemetry, setTelemetry] = useState<Telemetry | null>(null);
  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [analysisRunning, setAnalysisRunning] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const attemptsRef = useRef(0);
  /** Guards against setState after unmount / stale reconnects. */
  const closedByUs = useRef(false);

  const send = useCallback((message: ClientMessage) => {
    const socket = socketRef.current;
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    }
  }, []);

  const requestAnalysis = useCallback(() => {
    setDismissed(false);
    setAnalysisRunning(true);
    send({ action: "analyse" });
  }, [send]);

  const approvePlan = useCallback(
    (threadId: string) => {
      setAnalysisRunning(true);
      send({ action: "approve", thread_id: threadId });
    },
    [send],
  );

  const dismissAnalysis = useCallback(() => setDismissed(true), []);

  useEffect(() => {
    closedByUs.current = false;

    function scheduleReconnect() {
      if (closedByUs.current) return;
      const delay = Math.min(
        RECONNECT_BASE * 2 ** attemptsRef.current,
        RECONNECT_MAX,
      );
      attemptsRef.current += 1;
      reconnectTimer.current = setTimeout(connect, delay);
    }

    function connect() {
      setStatus((prev) => (prev === "closed" ? "connecting" : prev));

      let socket: WebSocket;
      try {
        socket = new WebSocket(WS_URL);
      } catch {
        setStatus("error");
        scheduleReconnect();
        return;
      }
      socketRef.current = socket;

      socket.onopen = () => {
        attemptsRef.current = 0;
        setStatus("connected");
      };

      socket.onmessage = (event: MessageEvent<string>) => {
        let msg: ServerMessage;
        try {
          msg = JSON.parse(event.data) as ServerMessage;
        } catch {
          return; // ignore malformed frames rather than crash the stream
        }
        handleMessage(msg);
      };

      socket.onerror = () => {
        setStatus("error");
      };

      socket.onclose = () => {
        socketRef.current = null;
        if (closedByUs.current) return;
        setStatus("closed");
        setAnalysisRunning(false);
        scheduleReconnect();
      };
    }

    function handleMessage(msg: ServerMessage) {
      switch (msg.type) {
        case "telemetry": {
          const snapshot = msg.data;
          setTelemetry(snapshot);
          setHistory((prev) => appendHistory(prev, snapshot));
          break;
        }
        case "analysis_started": {
          setDismissed(false);
          setAnalysisRunning(true);
          break;
        }
        case "analysis_result": {
          setAnalysis(msg.data);
          setAnalysisRunning(false);
          setDismissed(false);
          break;
        }
      }
    }

    connect();

    return () => {
      closedByUs.current = true;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      socketRef.current?.close();
      socketRef.current = null;
    };
  }, []);

  return {
    status,
    telemetry,
    history,
    // When locally dismissed, hide the analysis from consumers (modal closes).
    analysis: dismissed ? null : analysis,
    analysisRunning,
    hasData: telemetry !== null,
    requestAnalysis,
    approvePlan,
    dismissAnalysis,
  };
}

/** Append a snapshot to the rolling history, flattening ward occupancies and
 *  trimming to HISTORY_LIMIT. Pure so it's trivial to reason about/test. */
function appendHistory(
  prev: HistoryPoint[],
  snapshot: Telemetry,
): HistoryPoint[] {
  const point: HistoryPoint = {
    t: new Date(snapshot.timestamp).getTime() || Date.now(),
    label: clockLabel(snapshot.timestamp),
    pressure: snapshot.hospital_pressure,
  };
  for (const ward of snapshot.wards) {
    point[ward.ward] = ward.occupancy_rate;
  }
  const next = [...prev, point];
  return next.length > HISTORY_LIMIT
    ? next.slice(next.length - HISTORY_LIMIT)
    : next;
}
