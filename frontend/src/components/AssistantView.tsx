import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  Sparkles,
  RefreshCw,
  Trash2,
} from "lucide-react";
import type { HandFeatureData, ReadingResult } from "../api";
import { sendChat } from "../api";

interface AssistantViewProps {
  features: Record<string, HandFeatureData> | null;
  reading: ReadingResult | null;
  language: "en" | "si" | "ta";
  onChangeLanguage: (lang: "en" | "si" | "ta") => void;
  onNavigateToReading: () => void;
}

interface Message {
  role: "user" | "model";
  text: string;
}

export const AssistantView: React.FC<AssistantViewProps> = ({
  features,
  reading,
  language,
  onChangeLanguage,
  onNavigateToReading,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (queryText?: string) => {
    const q = queryText || input;
    if (!q.trim() || !features || !reading) return;

    const userMsg: Message = { role: "user", text: q };
    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setInput("");
    setIsLoading(true);

    try {
      const res = await sendChat(
        q,
        features,
        reading.report,
        language,
        messages
      );
      setMessages((prev) => [...prev, { role: "model", text: res.reply }]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "model",
          text: `Sorry, could not answer: ${err.message}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const promptsByLang: Record<"en" | "si" | "ta", string[]> = {
    en: [
      "What does my heart line traditionally represent?",
      "What differences are visible between my left and right palms?",
      "What does palmistry say about my career?",
      "Tell me about my fate line.",
      "Explain the computer vision techniques used on my hand.",
    ],
    si: [
      "මගේ හෘද රේඛාවෙන් සම්ප්‍රදායිකව කියවෙන්නේ කුමක්ද?",
      "මගේ වම් සහ දකුණු අත්ල අතර ඇති වෙනස්කම් මොනවාද?",
      "මගේ වෘත්තිය ගැන හස්තරේඛා ශාස්ත්‍රය පවසන්නේ කුමක්ද?",
      "මගේ දෛව රේඛාව ගැන විස්තර කරන්න.",
    ],
    ta: [
      "என் இதயக் கோடு பாரம்பரியமாக எதைக் குறிக்கிறது?",
      "என் இடது மற்றும் வலது உள்ளங்கைகளுக்கு இடையே உள்ள வேறுபாடுகள் என்ன?",
      "என் தொழில் பற்றி கைரேகை சாஸ்திரம் என்ன கூறுகிறது?",
      "என் விதி ரேகை பற்றி விளக்குங்கள்.",
    ],
  };

  if (!features || !reading) {
    return (
      <div className="glass-panel" style={{ textAlign: "center", padding: "60px 20px" }}>
        <Bot size={48} color="#8B5CF6" style={{ marginBottom: "16px" }} />
        <h2 style={{ fontSize: "1.4rem", color: "#F8FAFC", marginBottom: "8px" }}>
          Generate Your Palm Reading First
        </h2>
        <p style={{ color: "#94A3B8", maxWidth: "500px", margin: "0 auto 24px auto" }}>
          The AI Assistant is strictly grounded in your generated palm features and
          RAG knowledge base. Please generate your reading before starting dialogue.
        </p>
        <button className="btn-primary" onClick={onNavigateToReading}>
          Go to My Reading
        </button>
      </div>
    );
  }

  const promptChips = promptsByLang[language] || promptsByLang.en;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 120px)" }}>
      {/* Header Bar */}
      <div
        className="glass-panel"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "16px 22px",
          marginBottom: "16px",
          borderRadius: "14px",
        }}
      >
        <div>
          <h2 style={{ fontSize: "1.25rem", color: "#F8FAFC", marginBottom: "2px" }}>
            Grounded Palmistry Assistant
          </h2>
          <div style={{ fontSize: "0.78rem", color: "#94A3B8" }}>
            Strictly grounded in your anatomical features & 20-passage RAG corpus
          </div>
        </div>

        {/* Language & Actions */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            style={{
              display: "flex",
              background: "rgba(8, 11, 20, 0.8)",
              padding: "4px",
              borderRadius: "8px",
              border: "1px solid var(--border-glass)",
            }}
          >
            <button
              onClick={() => onChangeLanguage("en")}
              style={{
                padding: "4px 10px",
                borderRadius: "6px",
                border: "none",
                background: language === "en" ? "var(--violet)" : "transparent",
                color: language === "en" ? "#FFFFFF" : "#94A3B8",
                fontSize: "0.78rem",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              EN
            </button>
            <button
              onClick={() => onChangeLanguage("si")}
              style={{
                padding: "4px 10px",
                borderRadius: "6px",
                border: "none",
                background: language === "si" ? "var(--violet)" : "transparent",
                color: language === "si" ? "#FFFFFF" : "#94A3B8",
                fontSize: "0.78rem",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              සිංහල
            </button>
            <button
              onClick={() => onChangeLanguage("ta")}
              style={{
                padding: "4px 10px",
                borderRadius: "6px",
                border: "none",
                background: language === "ta" ? "var(--violet)" : "transparent",
                color: language === "ta" ? "#FFFFFF" : "#94A3B8",
                fontSize: "0.78rem",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              தமிழ்
            </button>
          </div>

          <button
            className="btn-secondary"
            onClick={() => setMessages([])}
            style={{ padding: "6px 12px", fontSize: "0.78rem" }}
            title="Clear Chat History"
          >
            <Trash2 size={13} /> Clear
          </button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div
        className="glass-panel"
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          gap: "16px",
          marginBottom: "16px",
        }}
      >
        {messages.length === 0 && (
          <div
            style={{
              textAlign: "center",
              margin: "auto",
              maxWidth: "550px",
              padding: "20px",
            }}
          >
            <div
              style={{
                width: "50px",
                height: "50px",
                borderRadius: "50%",
                background: "rgba(139, 92, 246, 0.15)",
                border: "1px solid rgba(139, 92, 246, 0.35)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#A78BFA",
                margin: "0 auto 16px auto",
              }}
            >
              <Bot size={26} />
            </div>
            <h3 style={{ color: "#F8FAFC", fontSize: "1.1rem", marginBottom: "8px" }}>
              How can I assist your palm analysis today?
            </h3>
            <p
              style={{
                color: "#94A3B8",
                fontSize: "0.86rem",
                lineHeight: 1.5,
                marginBottom: "20px",
              }}
            >
              Ask any question about your heart line, head line, life line, fate
              line, elemental hand shape, or the computer vision techniques used.
            </p>

            {/* Suggested Prompt Chips */}
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "8px",
                justifyContent: "center",
              }}
            >
              {promptChips.map((chip, idx) => (
                <button
                  key={idx}
                  className="btn-secondary"
                  style={{
                    fontSize: "0.8rem",
                    padding: "6px 14px",
                    borderRadius: "20px",
                  }}
                  onClick={() => handleSend(chip)}
                >
                  <Sparkles size={12} color="#22D3EE" />
                  <span>{chip}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Render Chat Messages */}
        {messages.map((m, idx) => {
          const isUser = m.role === "user";
          return (
            <div
              key={idx}
              style={{
                display: "flex",
                gap: "12px",
                alignSelf: isUser ? "flex-end" : "flex-start",
                maxWidth: "80%",
              }}
            >
              {!isUser && (
                <div
                  style={{
                    width: "34px",
                    height: "34px",
                    borderRadius: "50%",
                    background:
                      "linear-gradient(135deg, rgba(139, 92, 246, 0.3) 0%, rgba(34, 211, 238, 0.2) 100%)",
                    border: "1px solid var(--border-cyan)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#22D3EE",
                    flexShrink: 0,
                  }}
                >
                  <Bot size={18} />
                </div>
              )}

              <div
                style={{
                  background: isUser
                    ? "linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%)"
                    : "rgba(18, 25, 44, 0.9)",
                  border: isUser
                    ? "1px solid rgba(167, 139, 250, 0.4)"
                    : "1px solid var(--border-glass)",
                  borderRadius: isUser
                    ? "16px 16px 4px 16px"
                    : "16px 16px 16px 4px",
                  padding: "14px 18px",
                  color: "#F8FAFC",
                  fontSize: "0.92rem",
                  lineHeight: 1.6,
                  boxShadow: "0 4px 15px rgba(0, 0, 0, 0.3)",
                }}
              >
                {m.text.split("\n\n").map((chunk, cIdx) => (
                  <p key={cIdx} style={{ marginBottom: cIdx > 0 ? "8px" : "0" }}>
                    {chunk}
                  </p>
                ))}
              </div>

              {isUser && (
                <div
                  style={{
                    width: "34px",
                    height: "34px",
                    borderRadius: "50%",
                    background: "rgba(255, 255, 255, 0.1)",
                    border: "1px solid var(--border-glass)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#FFFFFF",
                    flexShrink: 0,
                  }}
                >
                  <User size={18} />
                </div>
              )}
            </div>
          );
        })}

        {isLoading && (
          <div
            style={{
              display: "flex",
              gap: "12px",
              alignSelf: "flex-start",
            }}
          >
            <div
              style={{
                width: "34px",
                height: "34px",
                borderRadius: "50%",
                background: "rgba(139, 92, 246, 0.2)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#A78BFA",
              }}
            >
              <Bot size={18} />
            </div>
            <div
              style={{
                background: "rgba(18, 25, 44, 0.9)",
                border: "1px solid var(--border-glass)",
                borderRadius: "14px",
                padding: "12px 18px",
                color: "#94A3B8",
                fontSize: "0.88rem",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <RefreshCw size={14} className="animate-spin" />
              <span>Gemini is synthesizing grounded answer…</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div
        className="glass-panel"
        style={{
          padding: "12px 16px",
          display: "flex",
          gap: "12px",
          alignItems: "center",
        }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
          placeholder={`Ask about your palms (${language.toUpperCase()})…`}
          style={{
            flex: 1,
            background: "transparent",
            border: "none",
            outline: "none",
            color: "#F8FAFC",
            fontSize: "0.95rem",
            fontFamily: "inherit",
          }}
        />

        <button
          className="btn-primary"
          onClick={() => handleSend()}
          disabled={!input.trim() || isLoading}
          style={{ padding: "10px 18px" }}
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
};
