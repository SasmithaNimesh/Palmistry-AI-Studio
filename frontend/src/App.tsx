import { useEffect, useState } from "react";
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

  // Load backend status on mount
  useEffect(() => {
    fetchStatus()
      .then((s) => setStatus(s))
      .catch((err) => console.error("Status fetch error:", err));
  }, []);

  // Fast Sample Loader
  const handleLoadSample = async (pairName: string) => {
    try {
      const data = await fetchSample(pairName);
      setLeftPalm({
        name: data.left.name,
        raw_b64: data.left.raw_b64,
        preview_url: data.left.b64,
        ok: data.left.ok,
        metrics: data.left.metrics,
        errors: data.left.errors,
        warnings: data.left.warnings,
      });

      setRightPalm({
        name: data.right.name,
        raw_b64: data.right.raw_b64,
        preview_url: data.right.b64,
        ok: data.right.ok,
        metrics: data.right.metrics,
        errors: data.right.errors,
        warnings: data.right.warnings,
      });

      setCurrentTab("upload");
    } catch (err: any) {
      alert(`Could not load sample: ${err.message}`);
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
      setReading(null); // Clear previous reading when new analysis runs
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

  // Change Language (instant re-query or translation without re-analyzing)
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
        hasAnalysis={Boolean(analysis)}
        onReset={handleReset}
      />

      {/* Main View Port */}
      <main className="main-content">
        {currentTab === "dashboard" && (
          <DashboardView
            onStartAnalysis={() => setCurrentTab("upload")}
            onLoadSample={handleLoadSample}
            leftPalm={leftPalm}
            rightPalm={rightPalm}
            analysis={analysis}
            hasReading={Boolean(reading)}
            onNavigate={setCurrentTab}
          />
        )}

        {currentTab === "upload" && (
          <UploadView
            leftPalm={leftPalm}
            rightPalm={rightPalm}
            setLeftPalm={setLeftPalm}
            setRightPalm={setRightPalm}
            onRunAnalysis={handleRunAnalysis}
            onLoadSample={handleLoadSample}
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
    </div>
  );
}

export default App;
