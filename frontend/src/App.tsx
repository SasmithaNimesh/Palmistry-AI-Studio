import { useEffect, useState } from "react";
import { Moon, HelpCircle, ChevronRight, ChevronDown, Lock, ShieldAlert } from "lucide-react";
import { Sidebar } from "./components/Sidebar";
import { DashboardView } from "./components/DashboardView";
import { UploadView } from "./components/UploadView";
import { CvLabView } from "./components/CvLabView";
import { FeaturesView } from "./components/FeaturesView";
import { ReadingView } from "./components/ReadingView";
import { AssistantView } from "./components/AssistantView";
import { MethodologyView } from "./components/MethodologyView";
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

  const [leftPalm, setLeftPalm] = useState<PalmSlot | null>(null);
  const [rightPalm, setRightPalm] = useState<PalmSlot | null>(null);

  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

  const [reading, setReading] = useState<ReadingResult | null>(null);
  const [readingLanguage, setReadingLanguage] = useState<"en" | "si" | "ta">("en");
  const [isReadingLoading, setIsReadingLoading] = useState<boolean>(false);

  // Load backend status and initialize with demo data for rich dashboard presentation
  useEffect(() => {
    fetchStatus()
      .then((s) => setStatus(s))
      .catch((err) => console.error("Status fetch error:", err));

    // Auto-load sample pair 1 on first launch to match reference UI dashboard
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

      // Auto run analysis on sample to populate pipeline & detected lines overview
      const res = await runAnalysis(
        { name: lSlot.name, raw_b64: lSlot.raw_b64 },
        { name: rSlot.name, raw_b64: rSlot.raw_b64 }
      );
      setAnalysis(res);

      if (shouldNavigate) {
        setCurrentTab("upload");
      }
    } catch (err: any) {
      console.warn("Could not auto-load sample:", err.message);
    }
  };

  // Run 10-Stage CV Pipeline
  const handleRunAnalysis = async () => {
    if (!leftPalm?.ok || !rightPalm?.ok) return;

    setIsAnalyzing(true);
    try {
      const res = await runAnalysis(
        { name: leftPalm.name, raw_b64: leftPalm.raw_b64 },
        { name: rightPalm.name, raw_b64: rightPalm.raw_b64 }
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
            <button className="theme-pill" onClick={() => alert("Theme: Luxury Dark (Default)")}>
              <Moon size={13} color="#22D3EE" />
              <span>Dark</span>
              <ChevronRight size={13} />
            </button>

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

            <div className="user-badge">
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
