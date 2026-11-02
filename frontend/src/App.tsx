import { useEffect, useState, useRef } from "react";
import {
  Moon,
  Sun,
  Laptop,
  HelpCircle,
  ChevronDown,
  Lock,
  ShieldAlert,
  Check,
} from "lucide-react";
import { Sidebar } from "./components/Sidebar";
import { DashboardView } from "./components/DashboardView";
import { UploadView } from "./components/UploadView";
import { CvLabView } from "./components/CvLabView";
import { FeaturesView } from "./components/FeaturesView";
import { ReadingView } from "./components/ReadingView";
import { AssistantView } from "./components/AssistantView";
import { MethodologyView } from "./components/MethodologyView";
import { HistoryView, type HistorySession } from "./components/HistoryView";
import { SettingsView } from "./components/SettingsView";
import type {
  AnalysisResult,
  PalmSlot,
  ReadingResult,
  SystemStatus,
} from "./api";
import {
  fetchReading,
  fetchSample,
  fetchStatus,
  runAnalysis,
} from "./api";

export function App() {
  const [currentTab, setCurrentTab] = useState<string>("dashboard");
  const [status, setStatus] = useState<SystemStatus | null>(null);

  // Theme Management: "dark" | "light" | "system"
  const [theme, setTheme] = useState<"dark" | "light" | "system">(() => {
    return (localStorage.getItem("palm_app_theme") as any) || "dark";
  });
  const [themeMenuOpen, setThemeMenuOpen] = useState(false);
  const themeMenuRef = useRef<HTMLDivElement>(null);

  // Sharpness Pre-Processing Enhancement (0.0 to 1.2)
  const [sharpenStrength, setSharpenStrength] = useState<number>(0.6);

  const [leftPalm, setLeftPalm] = useState<PalmSlot | null>(null);
  const [rightPalm, setRightPalm] = useState<PalmSlot | null>(null);

  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

  const [reading, setReading] = useState<ReadingResult | null>(null);
  const [readingLanguage, setReadingLanguage] = useState<"en" | "si" | "ta">("en");
  const [isReadingLoading, setIsReadingLoading] = useState<boolean>(false);

  // Apply Theme to DOM
  useEffect(() => {
    const applyEffectiveTheme = () => {
      let effective = theme;
      if (theme === "system") {
        effective = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      }
      document.documentElement.setAttribute("data-theme", effective);
      localStorage.setItem("palm_app_theme", theme);
    };

    applyEffectiveTheme();

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => {
      if (theme === "system") applyEffectiveTheme();
    };
    media.addEventListener("change", handler);
    return () => media.removeEventListener("change", handler);
  }, [theme]);

  // Close theme menu on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (themeMenuRef.current && !themeMenuRef.current.contains(e.target as Node)) {
        setThemeMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Load backend status and initialize with demo data
  useEffect(() => {
    fetchStatus()
      .then((s) => setStatus(s))
      .catch((err) => console.error("Status fetch error:", err));

    handleLoadSample("pair1", false);
  }, []);

  // Sample Loader
  const handleLoadSample = async (pairName: string, shouldNavigate: boolean = true) => {
    try {
      const data = await fetchSample(pairName);
      const lSlot: PalmSlot = {
        name: data.left.name,
        raw_b64: data.left.raw_b64,
        preview_url: data.left.b64,
        ok: data.left.ok,
        metrics: data.left.metrics,
        errors: data.left.errors,
        warnings: data.left.warnings,
      };

      const rSlot: PalmSlot = {
        name: data.right.name,
        raw_b64: data.right.raw_b64,
        preview_url: data.right.b64,
        ok: data.right.ok,
        metrics: data.right.metrics,
        errors: data.right.errors,
        warnings: data.right.warnings,
      };

      setLeftPalm(lSlot);
      setRightPalm(rSlot);

      const res = await runAnalysis(
        { name: lSlot.name, raw_b64: lSlot.raw_b64 },
        { name: rSlot.name, raw_b64: rSlot.raw_b64 },
        sharpenStrength
      );
      setAnalysis(res);

      if (shouldNavigate) {
        setCurrentTab("upload");
      }
    } catch (err: any) {
      console.warn("Could not auto-load sample:", err.message);
    }
  };

  // Run 10-Stage CV Pipeline with Pre-Processing Sharpness Boost
  const handleRunAnalysis = async () => {
    if (!leftPalm?.ok || !rightPalm?.ok) return;

    setIsAnalyzing(true);
    try {
      const res = await runAnalysis(
        { name: leftPalm.name, raw_b64: leftPalm.raw_b64 },
        { name: rightPalm.name, raw_b64: rightPalm.raw_b64 },
        sharpenStrength
      );
      setAnalysis(res);
      setReading(null);
      setCurrentTab("cvlab");
    } catch (err: any) {
      alert(`Analysis failed: ${err.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Generate Grounded Reading
  const handleGenerateReading = async (lang: "en" | "si" | "ta") => {
    if (!analysis) return;

    setIsReadingLoading(true);
    try {
      const res = await fetchReading(analysis.features, lang);
      setReading(res);
      setReadingLanguage(lang);
    } catch (err: any) {
      alert(`Could not generate reading: ${err.message}`);
    } finally {
      setIsReadingLoading(false);
    }
  };

  // Change Language
  const handleChangeLanguage = (lang: "en" | "si" | "ta") => {
    setReadingLanguage(lang);
    if (analysis && reading) {
      handleGenerateReading(lang);
    }
  };

  // Restore Session from History
  const handleRestoreSession = (session: HistorySession) => {
    setLeftPalm(session.leftPalm);
    setRightPalm(session.rightPalm);
    setAnalysis(session.analysis);
    setReading(session.reading);
    setCurrentTab("dashboard");
  };

  // Reset Session
  const handleReset = () => {
    setLeftPalm(null);
    setRightPalm(null);
    setAnalysis(null);
    setReading(null);
    setCurrentTab("dashboard");
  };

  return (
    <div className="app-container">
      {/* Sleek Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        setTab={setCurrentTab}
        status={status}
        leftPalm={leftPalm}
        rightPalm={rightPalm}
        analysis={analysis}
        hasReading={Boolean(reading)}
        onReset={handleReset}
      />

      {/* Main App Wrapper */}
      <div className="main-wrapper">
        {/* Top Header Navigation Bar */}
        <header className="top-header">
          <div>
            <h2 className="top-header-title">AI Palm Reading &amp; Analysis</h2>
            <p className="top-header-subtitle">
              Discover meaningful insights through advanced AI and Computer Vision
            </p>
          </div>

          <div className="top-header-actions">
            {/* Theme Toggle with Dropdown */}
            <div style={{ position: "relative" }} ref={themeMenuRef}>
              <button
                className="theme-pill"
                onClick={() => setThemeMenuOpen(!themeMenuOpen)}
              >
                {theme === "dark" && <Moon size={14} color="#22D3EE" />}
                {theme === "light" && <Sun size={14} color="#F59E0B" />}
                {theme === "system" && <Laptop size={14} color="#A78BFA" />}
                <span style={{ textTransform: "capitalize" }}>{theme}</span>
                <ChevronDown size={13} />
              </button>

              {themeMenuOpen && (
                <div
                  style={{
                    position: "absolute",
                    top: "115%",
                    right: 0,
                    width: "140px",
                    background: "var(--bg-surface)",
                    border: "1px solid var(--border-glass)",
                    borderRadius: "10px",
                    boxShadow: "0 10px 25px rgba(0,0,0,0.4)",
                    padding: "6px",
                    zIndex: 100,
                    display: "flex",
                    flexDirection: "column",
                    gap: "2px",
                  }}
                >
                  {[
                    { id: "dark", label: "Dark", icon: Moon, color: "#22D3EE" },
                    { id: "light", label: "Light", icon: Sun, color: "#F59E0B" },
                    { id: "system", label: "System", icon: Laptop, color: "#A78BFA" },
                  ].map((t) => {
                    const Icon = t.icon;
                    const isSel = theme === t.id;
                    return (
                      <button
                        key={t.id}
                        onClick={() => {
                          setTheme(t.id as any);
                          setThemeMenuOpen(false);
                        }}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          padding: "8px 10px",
                          borderRadius: "6px",
                          background: isSel ? "rgba(139, 92, 246, 0.15)" : "transparent",
                          border: "none",
                          color: isSel ? "#FFFFFF" : "#94A3B8",
                          cursor: "pointer",
                          fontSize: "0.82rem",
                          fontWeight: isSel ? 600 : 400,
                          textAlign: "left",
                        }}
                      >
                        <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <Icon size={14} color={t.color} />
                          {t.label}
                        </span>
                        {isSel && <Check size={13} color="#22D3EE" />}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Quick Help */}
            <button
              style={{
                width: "32px",
                height: "32px",
                borderRadius: "50%",
                background: "rgba(255, 255, 255, 0.05)",
                border: "1px solid var(--border-glass)",
                color: "#94A3B8",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
              }}
              onClick={() => setCurrentTab("methodology")}
            >
              <HelpCircle size={16} />
            </button>

            {/* User Profile */}
            <div className="user-badge" onClick={() => setCurrentTab("settings")}>
              <div className="user-avatar-circle">U</div>
              <span style={{ fontSize: "0.8rem", color: "#CBD5E1" }}>
                Welcome, <strong style={{ color: "#FFFFFF" }}>User</strong>
              </span>
              <ChevronDown size={14} color="#94A3B8" />
            </div>
          </div>
        </header>

        {/* View Router */}
        <main className="main-content">
          {currentTab === "dashboard" && (
            <DashboardView
              onStartAnalysis={() => setCurrentTab("upload")}
              onLoadSample={(p) => handleLoadSample(p, true)}
              leftPalm={leftPalm}
              rightPalm={rightPalm}
              analysis={analysis}
              hasReading={Boolean(reading)}
              onNavigate={setCurrentTab}
              onQuickAsk={() => setCurrentTab("assistant")}
            />
          )}

          {currentTab === "upload" && (
            <UploadView
              leftPalm={leftPalm}
              rightPalm={rightPalm}
              setLeftPalm={setLeftPalm}
              setRightPalm={setRightPalm}
              onRunAnalysis={handleRunAnalysis}
              onLoadSample={(p) => handleLoadSample(p, true)}
              isAnalyzing={isAnalyzing}
              sharpenStrength={sharpenStrength}
              setSharpenStrength={setSharpenStrength}
            />
          )}

          {currentTab === "cvlab" && (
            <CvLabView
              analysis={analysis}
              onNavigateToUpload={() => setCurrentTab("upload")}
            />
          )}

          {currentTab === "features" && (
            <FeaturesView
              analysis={analysis}
              onNavigateToUpload={() => setCurrentTab("upload")}
            />
          )}

          {currentTab === "reading" && (
            <ReadingView
              features={analysis ? analysis.features : null}
              reading={reading}
              language={readingLanguage}
              onChangeLanguage={handleChangeLanguage}
              onGenerateReading={handleGenerateReading}
              isLoading={isReadingLoading}
              onNavigateToUpload={() => setCurrentTab("upload")}
            />
          )}

          {currentTab === "assistant" && (
            <AssistantView
              features={analysis ? analysis.features : null}
              reading={reading}
              language={readingLanguage}
              onChangeLanguage={setReadingLanguage}
              onNavigateToReading={() => setCurrentTab("reading")}
            />
          )}

          {currentTab === "history" && (
            <HistoryView
              currentLeftPalm={leftPalm}
              currentRightPalm={rightPalm}
              currentAnalysis={analysis}
              currentReading={reading}
              onRestoreSession={handleRestoreSession}
              onNavigate={setCurrentTab}
            />
          )}

          {currentTab === "settings" && (
            <SettingsView
              theme={theme}
              setTheme={setTheme}
              sharpenStrength={sharpenStrength}
              setSharpenStrength={setSharpenStrength}
              defaultLanguage={readingLanguage}
              setDefaultLanguage={setReadingLanguage}
              status={status}
              onResetAll={handleReset}
            />
          )}

          {currentTab === "methodology" && <MethodologyView />}
        </main>

        {/* App Footer */}
        <footer className="app-footer">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <ShieldAlert size={14} color="#A78BFA" />
            <span>
              <strong>Important:</strong> Palmistry is for cultural and entertainment purposes only. It is not a substitute for professional advice.
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <Lock size={13} color="#34D399" />
            <span>Your privacy is important to us. Images are processed in-memory and never stored.</span>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
