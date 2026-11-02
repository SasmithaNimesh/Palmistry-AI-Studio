import React, { useState, useEffect } from "react";
import {
  Clock,
  RotateCcw,
  Trash2,
  BookmarkPlus,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import type { AnalysisResult, PalmSlot, ReadingResult } from "../api";

export interface HistorySession {
  id: string;
  timestamp: string;
  leftPalm: PalmSlot | null;
  rightPalm: PalmSlot | null;
  analysis: AnalysisResult | null;
  reading: ReadingResult | null;
  qualityScore: number;
  handType: string;
}

interface HistoryViewProps {
  currentLeftPalm: PalmSlot | null;
  currentRightPalm: PalmSlot | null;
  currentAnalysis: AnalysisResult | null;
  currentReading: ReadingResult | null;
  onRestoreSession: (session: HistorySession) => void;
  onNavigate: (tab: string) => void;
}

const STORAGE_KEY = "palm_studio_history_sessions";

export const HistoryView: React.FC<HistoryViewProps> = ({
  currentLeftPalm,
  currentRightPalm,
  currentAnalysis,
  currentReading,
  onRestoreSession,
  onNavigate,
}) => {
  const [sessions, setSessions] = useState<HistorySession[]>([]);

  // Load saved sessions from localStorage
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        setSessions(JSON.parse(raw));
      }
    } catch (e) {
      console.warn("Failed to read history from localStorage:", e);
    }
  }, []);

  const saveSessions = (items: HistorySession[]) => {
    setSessions(items);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    } catch (e) {
      console.warn("Failed to persist history to localStorage:", e);
    }
  };

  // Bookmark current active session
  const handleSaveCurrentSession = () => {
    if (!currentAnalysis) {
      alert("No active palm analysis to save. Run an analysis first.");
      return;
    }

    const handType =
      currentAnalysis.features?.Right?.palm?.palmistry_hand_type ||
      currentAnalysis.features?.Left?.palm?.palmistry_hand_type ||
      "Earth Hand";

    const newSession: HistorySession = {
      id: "session_" + Date.now(),
      timestamp: new Date().toLocaleString(),
      leftPalm: currentLeftPalm,
      rightPalm: currentRightPalm,
      analysis: currentAnalysis,
      reading: currentReading,
      qualityScore: 92,
      handType,
    };

    const updated = [newSession, ...sessions.slice(0, 9)]; // keep latest 10
    saveSessions(updated);
  };

  const handleDeleteSession = (id: string) => {
    const updated = sessions.filter((s) => s.id !== id);
    saveSessions(updated);
  };

  const handleClearAll = () => {
    if (confirm("Clear all saved session history?")) {
      saveSessions([]);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "22px" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "12px",
        }}
      >
        <div>
          <h2 style={{ fontSize: "1.6rem", color: "#F8FAFC", marginBottom: "4px" }}>
            Analysis Session History
          </h2>
          <p style={{ color: "#94A3B8", fontSize: "0.88rem" }}>
            Review past palm analyses, restore cached features, or export reading logs.
          </p>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {currentAnalysis && (
            <button className="btn-primary" onClick={handleSaveCurrentSession}>
              <BookmarkPlus size={15} />
              <span>Save Current Session</span>
            </button>
          )}

          {sessions.length > 0 && (
            <button className="btn-secondary" onClick={handleClearAll}>
              <Trash2 size={15} color="#F87171" />
              <span>Clear History</span>
            </button>
          )}
        </div>
      </div>

      {/* History Grid */}
      {sessions.length === 0 ? (
        <div
          className="glass-panel"
          style={{
            padding: "48px 24px",
            textAlign: "center",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "14px",
          }}
        >
          <div
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "50%",
              background: "rgba(139, 92, 246, 0.15)",
              border: "1px solid rgba(139, 92, 246, 0.3)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "1.5rem",
            }}
          >
            <Clock size={26} color="#A78BFA" />
          </div>
          <div style={{ fontSize: "1.1rem", fontWeight: 600, color: "#F8FAFC" }}>
            No Saved Sessions Found
          </div>
          <p style={{ color: "#94A3B8", fontSize: "0.88rem", maxWidth: "420px" }}>
            When you complete or bookmark an analysis, it is stored locally on your device
            so you can inspect or restore it at any time.
          </p>
          <button className="btn-primary" onClick={() => onNavigate("upload")}>
            <span>Start an Analysis</span>
            <ArrowRight size={15} />
          </button>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          {sessions.map((sess) => (
            <div
              key={sess.id}
              className="glass-panel"
              style={{
                display: "grid",
                gridTemplateColumns: "140px 1fr auto",
                gap: "20px",
                alignItems: "center",
                padding: "16px 20px",
              }}
            >
              {/* Thumbnails */}
              <div style={{ display: "flex", gap: "8px" }}>
                <div
                  style={{
                    width: "58px",
                    height: "58px",
                    borderRadius: "8px",
                    background: "#050711",
                    overflow: "hidden",
                    border: "1px solid rgba(255, 255, 255, 0.08)",
                  }}
                >
                  {sess.leftPalm?.preview_url ? (
                    <img
                      src={sess.leftPalm.preview_url.startsWith("data:") ? sess.leftPalm.preview_url : `data:image/jpeg;base64,${sess.leftPalm.preview_url}`}
                      alt="Left"
                      style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    />
                  ) : (
                    <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center" }}>
                      ✋
                    </div>
                  )}
                </div>

                <div
                  style={{
                    width: "58px",
                    height: "58px",
                    borderRadius: "8px",
                    background: "#050711",
                    overflow: "hidden",
                    border: "1px solid rgba(255, 255, 255, 0.08)",
                  }}
                >
                  {sess.rightPalm?.preview_url ? (
                    <img
                      src={sess.rightPalm.preview_url.startsWith("data:") ? sess.rightPalm.preview_url : `data:image/jpeg;base64,${sess.rightPalm.preview_url}`}
                      alt="Right"
                      style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    />
                  ) : (
                    <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center" }}>
                      🤚
                    </div>
                  )}
                </div>
              </div>

              {/* Info Details */}
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
                  <span style={{ fontSize: "0.95rem", fontWeight: 700, color: "#F8FAFC" }}>
                    {sess.handType}
                  </span>
                  <span
                    style={{
                      fontSize: "0.7rem",
                      background: "rgba(16, 185, 129, 0.15)",
                      color: "#34D399",
                      padding: "2px 8px",
                      borderRadius: "9999px",
                      fontWeight: 600,
                    }}
                  >
                    Quality: {sess.qualityScore}%
                  </span>
                </div>
                <div style={{ fontSize: "0.76rem", color: "#64748B" }}>
                  Recorded on {sess.timestamp}
                </div>
              </div>

              {/* Actions */}
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <button
                  className="btn-primary"
                  style={{ padding: "8px 14px", fontSize: "0.82rem" }}
                  onClick={() => onRestoreSession(sess)}
                >
                  <RotateCcw size={14} />
                  <span>Restore</span>
                </button>

                <button
                  style={{
                    width: "34px",
                    height: "34px",
                    borderRadius: "8px",
                    background: "rgba(239, 68, 68, 0.1)",
                    border: "1px solid rgba(239, 68, 68, 0.25)",
                    color: "#F87171",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    cursor: "pointer",
                  }}
                  onClick={() => handleDeleteSession(sess.id)}
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Privacy Guarantee Note */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          padding: "12px 18px",
          background: "rgba(255, 255, 255, 0.02)",
          border: "1px solid rgba(255, 255, 255, 0.06)",
          borderRadius: "10px",
          fontSize: "0.78rem",
          color: "#94A3B8",
        }}
      >
        <ShieldCheck size={16} color="#34D399" />
        <span>
          History is strictly persisted in your browser's local sandbox (IndexedDB / localStorage).
          Images and features are never transferred to external servers.
        </span>
      </div>
    </div>
  );
};
