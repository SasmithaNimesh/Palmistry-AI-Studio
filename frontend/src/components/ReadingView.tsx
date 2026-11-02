import React, { useState } from "react";
import {
  Sparkles,
  Download,
  Copy,
  Check,
  Globe,
  BookOpen,
  ChevronDown,
  ChevronUp,
  Brain,
  Briefcase,
  Heart,
  Compass,
  Layers,
  AlertTriangle,
  RefreshCw,
} from "lucide-react";
import type { HandFeatureData, ReadingResult } from "../api";

interface ReadingViewProps {
  features: Record<string, HandFeatureData> | null;
  reading: ReadingResult | null;
  language: "en" | "si" | "ta";
  onChangeLanguage: (lang: "en" | "si" | "ta") => void;
  onGenerateReading: (lang: "en" | "si" | "ta") => void;
  isLoading: boolean;
  onNavigateToUpload: () => void;
}

export const ReadingView: React.FC<ReadingViewProps> = ({
  features,
  reading,
  language,
  onChangeLanguage,
  onGenerateReading,
  isLoading,
  onNavigateToUpload,
}) => {
  const [copied, setCopied] = useState(false);
  const [showRAG, setShowRAG] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    palm_characteristics: true,
    major_lines: true,
    personality: true,
    career: true,
    relationships: true,
    future_narrative: true,
    left_vs_right: true,
    uncertainty: true,
  });

  const toggleSection = (key: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const handleCopy = () => {
    if (!reading) return;
    const reportText = Object.entries(reading.report)
      .map(([k, v]) => `## ${k.replace(/_/g, " ").toUpperCase()}\n${v}`)
      .join("\n\n");
    navigator.clipboard.writeText(reportText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!reading) return;
    const reportText = [
      `# AI Palm Reading Report (${reading.language.toUpperCase()})`,
      "",
      `> ${reading.disclaimer}`,
      "",
      ...Object.entries(reading.report).map(
        ([k, v]) => `### ${reading.titles[k] || k.replace(/_/g, " ")}\n${v}\n`
      ),
    ].join("\n");

    const blob = new Blob([reportText], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `palm_reading_${reading.language}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!features) {
    return (
      <div className="glass-panel" style={{ textAlign: "center", padding: "60px 20px" }}>
        <Sparkles size={48} color="#8B5CF6" style={{ marginBottom: "16px" }} />
        <h2 style={{ fontSize: "1.4rem", color: "#F8FAFC", marginBottom: "8px" }}>
          Ready for Feature Synthesis
        </h2>
        <p style={{ color: "#94A3B8", maxWidth: "500px", margin: "0 auto 24px auto" }}>
          Upload and verify your palm photos first to generate an AI reading
          grounded in classical palmistry literature.
        </p>
        <button className="btn-primary" onClick={onNavigateToUpload}>
          Go to Palm Upload
        </button>
      </div>
    );
  }

  // Section configuration with icons
  const sectionMeta: Record<string, { icon: any; color: string; defaultTitle: string }> = {
    palm_characteristics: {
      icon: Compass,
      color: "#22D3EE",
      defaultTitle: "Palm Characteristics & Morphology",
    },
    major_lines: {
      icon: Layers,
      color: "#8B5CF6",
      defaultTitle: "Major Palm Lines (Observed vs Traditional)",
    },
    personality: {
      icon: Brain,
      color: "#A78BFA",
      defaultTitle: "Personality Themes & Character",
    },
    career: {
      icon: Briefcase,
      color: "#34D399",
      defaultTitle: "Career & Ambition Patterns",
    },
    finance: {
      icon: Compass,
      color: "#FCD34D",
      defaultTitle: "Financial Themes & Stewardship",
    },
    relationships: {
      icon: Heart,
      color: "#F43F5E",
      defaultTitle: "Relationships & Emotional Dynamics",
    },
    future_narrative: {
      icon: Sparkles,
      color: "#67E8F9",
      defaultTitle: "Future Narrative (Symbolic Storytelling)",
    },
    left_vs_right: {
      icon: Layers,
      color: "#C4B5FD",
      defaultTitle: "Left vs. Right Palm Comparative Analysis",
    },
    uncertainty: {
      icon: AlertTriangle,
      color: "#F87171",
      defaultTitle: "Uncertainty & Methodological Limits",
    },
  };

  const getFontClass = () => {
    if (language === "si") return "font-sinhala";
    if (language === "ta") return "font-tamil";
    return "";
  };

  return (
    <div className={getFontClass()}>
      {/* Top Header & Language Bar */}
      <div
        className="glass-panel"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "16px",
          marginBottom: "24px",
          padding: "20px 24px",
          borderColor: "rgba(139, 92, 246, 0.4)",
        }}
      >
        <div>
          <div className="badge badge-purple" style={{ marginBottom: "6px" }}>
            <Sparkles size={12} /> Executive Synthesis
          </div>
          <h2 style={{ fontSize: "1.5rem", color: "#F8FAFC" }}>
            Personalized AI Palm Reading
          </h2>
        </div>

        {/* Multilingual Selector */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              fontSize: "0.82rem",
              color: "#94A3B8",
            }}
          >
            <Globe size={16} color="#22D3EE" />
            <span>Reading Language:</span>
          </div>

          <div
            style={{
              display: "flex",
              background: "rgba(8, 11, 20, 0.8)",
              padding: "4px",
              borderRadius: "10px",
              border: "1px solid var(--border-glass)",
            }}
          >
            <button
              onClick={() => onChangeLanguage("en")}
              style={{
                padding: "6px 14px",
                borderRadius: "8px",
                border: "none",
                background: language === "en" ? "var(--violet)" : "transparent",
                color: language === "en" ? "#FFFFFF" : "#94A3B8",
                fontWeight: 600,
                fontSize: "0.85rem",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
            >
              English
            </button>
            <button
              onClick={() => onChangeLanguage("si")}
              style={{
                padding: "6px 14px",
                borderRadius: "8px",
                border: "none",
                background: language === "si" ? "var(--violet)" : "transparent",
                color: language === "si" ? "#FFFFFF" : "#94A3B8",
                fontWeight: 600,
                fontSize: "0.85rem",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
            >
              සිංහල (Sinhala)
            </button>
            <button
              onClick={() => onChangeLanguage("ta")}
              style={{
                padding: "6px 14px",
                borderRadius: "8px",
                border: "none",
                background: language === "ta" ? "var(--violet)" : "transparent",
                color: language === "ta" ? "#FFFFFF" : "#94A3B8",
                fontWeight: 600,
                fontSize: "0.85rem",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
            >
              தமிழ் (Tamil)
            </button>
          </div>
        </div>
      </div>

      {/* If reading is not yet generated */}
      {!reading && (
        <div
          className="glass-panel"
          style={{
            textAlign: "center",
            padding: "50px 20px",
            borderColor: "rgba(34, 211, 238, 0.35)",
            background:
              "radial-gradient(circle at 50% 50%, rgba(34, 211, 238, 0.08) 0%, transparent 70%), rgba(18, 25, 44, 0.8)",
          }}
        >
          <div style={{ fontSize: "3rem", marginBottom: "14px" }}>✨</div>
          <h3 style={{ fontSize: "1.35rem", color: "#F8FAFC", marginBottom: "8px" }}>
            Ready to Synthesize Your Reading
          </h3>
          <p
            style={{
              color: "#94A3B8",
              maxWidth: "600px",
              margin: "0 auto 24px auto",
              fontSize: "0.92rem",
              lineHeight: 1.55,
            }}
          >
            The system will retrieve relevant traditional passages from our 20-passage
            corpus, ground the context in your verified palm features, and generate
            a structured multi-section report in your chosen language.
          </p>

          <button
            className="btn-primary"
            onClick={() => onGenerateReading(language)}
            disabled={isLoading}
            style={{ minWidth: "240px", justifyContent: "center" }}
          >
            {isLoading ? (
              <>
                <RefreshCw size={18} className="animate-spin" />
                <span>Generating Reading…</span>
              </>
            ) : (
              <>
                <Sparkles size={18} />
                <span>Generate Reading ({language.toUpperCase()})</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Generated Report View */}
      {reading && (
        <div>
          {/* Action Bar: Download & Copy */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "18px",
              flexWrap: "wrap",
              gap: "12px",
            }}
          >
            <div style={{ display: "flex", gap: "10px" }}>
              <button
                className="btn-secondary"
                onClick={handleCopy}
                style={{ fontSize: "0.85rem", padding: "8px 14px" }}
              >
                {copied ? <Check size={15} color="#34D399" /> : <Copy size={15} />}
                <span>{copied ? "Copied to Clipboard" : "Copy Report"}</span>
              </button>

              <button
                className="btn-secondary"
                onClick={handleDownload}
                style={{ fontSize: "0.85rem", padding: "8px 14px" }}
              >
                <Download size={15} color="#22D3EE" />
                <span>Export Markdown</span>
              </button>
            </div>

            <button
              className="btn-secondary"
              onClick={() => onGenerateReading(language)}
              disabled={isLoading}
              style={{ fontSize: "0.85rem", padding: "8px 14px" }}
            >
              <RefreshCw
                size={14}
                className={isLoading ? "animate-spin" : ""}
                color="#A78BFA"
              />
              <span>Regenerate in {language.toUpperCase()}</span>
            </button>
          </div>

          {/* Report Sections Accordion */}
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {Object.entries(reading.report).map(([key, text]) => {
              if (key === "disclaimer") return null;
              const meta = sectionMeta[key] || {
                icon: BookOpen,
                color: "#8B5CF6",
                defaultTitle: key.replace(/_/g, " "),
              };
              const Icon = meta.icon;
              const title = reading.titles[key] || meta.defaultTitle;
              const isExpanded = expandedSections[key] !== false;

              return (
                <div
                  key={key}
                  className="glass-panel"
                  style={{
                    padding: "0",
                    overflow: "hidden",
                    borderLeft: `4px solid ${meta.color}`,
                  }}
                >
                  <div
                    onClick={() => toggleSection(key)}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "18px 24px",
                      cursor: "pointer",
                      background: isExpanded
                        ? "rgba(255, 255, 255, 0.02)"
                        : "transparent",
                      borderBottom: isExpanded
                        ? "1px solid var(--border-glass)"
                        : "none",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                      <div
                        style={{
                          width: "32px",
                          height: "32px",
                          borderRadius: "8px",
                          background: `${meta.color}20`,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          color: meta.color,
                        }}
                      >
                        <Icon size={18} />
                      </div>
                      <h3 style={{ fontSize: "1.1rem", color: "#F8FAFC" }}>{title}</h3>
                    </div>

                    <div style={{ color: "#94A3B8" }}>
                      {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                    </div>
                  </div>

                  {isExpanded && (
                    <div
                      style={{
                        padding: "20px 24px",
                        fontSize: "0.95rem",
                        color: "#E2E8F0",
                        lineHeight: 1.7,
                      }}
                    >
                      {text.split("\n\n").map((para, i) => (
                        <p key={i} style={{ marginBottom: "12px" }}>
                          {para}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* RAG Knowledge Transparency Drawer */}
          <div className="glass-panel" style={{ marginTop: "24px", padding: "20px" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                cursor: "pointer",
              }}
              onClick={() => setShowRAG(!showRAG)}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <BookOpen size={18} color="#22D3EE" />
                <span
                  style={{
                    fontSize: "0.92rem",
                    fontWeight: 600,
                    color: "#F8FAFC",
                  }}
                >
                  RAG Transparency: Retrieved Historical Passages ({reading.passages.length})
                </span>
              </div>
              <div style={{ color: "#94A3B8" }}>
                {showRAG ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              </div>
            </div>

            {showRAG && (
              <div
                style={{
                  marginTop: "16px",
                  paddingTop: "14px",
                  borderTop: "1px solid var(--border-glass)",
                }}
              >
                <p
                  style={{
                    fontSize: "0.82rem",
                    color: "#94A3B8",
                    marginBottom: "12px",
                  }}
                >
                  These exact passages were retrieved from the 20-passage palmistry
                  corpus via TF-IDF matching and injected into Gemini's prompt to ensure
                  every statement is grounded in classical tradition:
                </p>

                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "8px",
                  }}
                >
                  {reading.passages.map((p, i) => (
                    <div
                      key={i}
                      style={{
                        background: "rgba(0, 0, 0, 0.35)",
                        padding: "10px 14px",
                        borderRadius: "8px",
                        border: "1px solid var(--border-glass)",
                        fontSize: "0.82rem",
                        color: "#CBD5E1",
                        lineHeight: 1.5,
                      }}
                    >
                      <strong style={{ color: "#22D3EE" }}>[{p.id}] </strong>
                      {p.text}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Ethics Disclaimer */}
          <div
            style={{
              marginTop: "20px",
              padding: "14px 18px",
              background: "rgba(139, 92, 246, 0.08)",
              border: "1px solid rgba(139, 92, 246, 0.25)",
              borderRadius: "10px",
              fontSize: "0.82rem",
              color: "#CBD5E1",
            }}
          >
            <strong>Disclaimer: </strong> {reading.disclaimer}
          </div>
        </div>
      )}
    </div>
  );
};
