"""Modern luxury dark theme and glassmorphic design system for AI Palm Reader."""

MASTER_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-main: #080B14;
    --bg-secondary: #101525;
    --bg-card: rgba(20, 27, 45, 0.7);
    --bg-card-hover: rgba(26, 35, 58, 0.85);
    --primary-accent: #8B5CF6;
    --secondary-accent: #22D3EE;
    --highlight: #A78BFA;
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
    --success: #10B981;
    --warning: #F59E0B;
    --danger: #EF4444;
    --border-subtle: rgba(139, 92, 246, 0.22);
    --border-cyan: rgba(34, 211, 238, 0.25);
    --border-glass: rgba(255, 255, 255, 0.08);
    --glow-violet: 0 0 25px rgba(139, 92, 246, 0.25);
    --glow-cyan: 0 0 25px rgba(34, 211, 238, 0.2);
}

/* Global Application Background */
.stApp {
    background: radial-gradient(circle at 15% 10%, rgba(139, 92, 246, 0.08) 0%, transparent 45%),
                radial-gradient(circle at 85% 85%, rgba(34, 211, 238, 0.06) 0%, transparent 45%),
                linear-gradient(180deg, #080B14 0%, #0D1220 50%, #080B14 100%) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Typography Overrides */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', -apple-system, sans-serif !important;
    letter-spacing: -0.02em !important;
    color: var(--text-primary) !important;
}

/* Streamlit Header & Toolbar */
header[data-testid="stHeader"] {
    background: rgba(8, 11, 20, 0.75) !important;
    backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid var(--border-glass) !important;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B0F1C 0%, #101525 100%) !important;
    border-right: 1px solid var(--border-glass) !important;
}

section[data-testid="stSidebar"] .stMarkdown {
    color: var(--text-secondary);
}

/* Tabs Navigation Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px !important;
    background: rgba(16, 21, 37, 0.6) !important;
    padding: 8px 12px !important;
    border-radius: 14px !important;
    border: 1px solid var(--border-glass) !important;
    backdrop-filter: blur(8px) !important;
}

.stTabs [data-baseweb="tab"] {
    height: 44px !important;
    border-radius: 10px !important;
    color: var(--text-secondary) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    border: 1px solid transparent !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    padding: 0 18px !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-primary) !important;
    background: rgba(139, 92, 246, 0.12) !important;
    border-color: rgba(139, 92, 246, 0.25) !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(34, 211, 238, 0.18) 100%) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border: 1px solid var(--border-cyan) !important;
    box-shadow: 0 4px 20px rgba(139, 92, 246, 0.2) !important;
}

/* Glassmorphic Cards & Containers */
.glass-panel {
    background: var(--bg-card);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.glass-panel:hover {
    border-color: rgba(139, 92, 246, 0.4);
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.45), var(--glow-violet);
}

.glass-panel-cyan {
    background: rgba(16, 25, 45, 0.7);
    border: 1px solid var(--border-cyan);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35), var(--glow-cyan);
}

/* Hero Section Badge */
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(139, 92, 246, 0.15);
    border: 1px solid rgba(139, 92, 246, 0.4);
    color: var(--highlight);
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 14px;
}

/* Gradient Titles */
.gradient-title {
    background: linear-gradient(135deg, #FFFFFF 20%, #A78BFA 60%, #22D3EE 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.3rem;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 10px;
}

.gradient-subtext {
    color: var(--text-secondary);
    font-size: 1.05rem;
    line-height: 1.5;
    margin-bottom: 20px;
}

/* Progress Stepper / Timeline */
.stepper-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(16, 21, 37, 0.6);
    border: 1px solid var(--border-glass);
    border-radius: 14px;
    padding: 14px 20px;
    margin-bottom: 24px;
    backdrop-filter: blur(8px);
}

.step-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.88rem;
    color: var(--text-muted);
}

.step-item.active {
    color: var(--secondary-accent);
    font-weight: 600;
}

.step-item.completed {
    color: var(--success);
    font-weight: 600;
}

.step-num {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid var(--border-glass);
    font-size: 0.78rem;
}

.step-item.active .step-num {
    background: rgba(34, 211, 238, 0.2);
    border-color: var(--secondary-accent);
    color: var(--secondary-accent);
    box-shadow: 0 0 12px rgba(34, 211, 238, 0.35);
}

.step-item.completed .step-num {
    background: rgba(16, 185, 129, 0.2);
    border-color: var(--success);
    color: var(--success);
}

/* Quality Metric Chip */
.metric-chip {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border-glass);
    border-radius: 10px;
    padding: 10px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    font-size: 0.88rem;
}

.metric-chip-label {
    color: var(--text-secondary);
}

.metric-chip-value {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    color: var(--text-primary);
}

/* Feature Status Pill */
.status-pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.status-detected {
    background: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.35);
}

.status-uncertain {
    background: rgba(245, 158, 11, 0.15);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.35);
}

.status-not_detected {
    background: rgba(100, 116, 139, 0.15);
    color: #94A3B8;
    border: 1px solid rgba(100, 116, 139, 0.35);
}

/* Feature Card */
.feature-card {
    background: rgba(20, 27, 45, 0.55);
    border: 1px solid var(--border-glass);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    border-left: 4px solid var(--primary-accent);
    transition: all 0.2s ease;
}

.feature-card:hover {
    background: rgba(26, 35, 58, 0.7);
    border-color: var(--border-subtle);
    transform: translateY(-2px);
}

/* Report Section Card */
.report-section {
    background: rgba(20, 27, 45, 0.6);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}

.report-section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--highlight);
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding-bottom: 8px;
}

/* Buttons Styling */
.stButton > button {
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    transition: all 0.25s ease !important;
    border: 1px solid var(--border-glass) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%) !important;
    border: 1px solid rgba(167, 139, 250, 0.4) !important;
    box-shadow: 0 4px 18px rgba(139, 92, 246, 0.35) !important;
    color: #FFFFFF !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #9D74FF 0%, #7C3AED 100%) !important;
    box-shadow: 0 6px 24px rgba(139, 92, 246, 0.5) !important;
    transform: translateY(-1px) !important;
}

/* File Uploaders */
div[data-testid="stFileUploader"] {
    background: rgba(16, 21, 37, 0.5) !important;
    border: 1px dashed rgba(139, 92, 246, 0.35) !important;
    border-radius: 14px !important;
    padding: 16px !important;
    transition: all 0.25s ease !important;
}

div[data-testid="stFileUploader"]:hover {
    border-color: var(--secondary-accent) !important;
    background: rgba(20, 27, 45, 0.65) !important;
}

/* Streamlit Info/Warning/Success Alerts */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid transparent !important;
    backdrop-filter: blur(10px) !important;
}

/* Chat Input & Messages */
div[data-testid="stChatInput"] {
    border-radius: 14px !important;
    border: 1px solid var(--border-subtle) !important;
    background: rgba(16, 21, 37, 0.8) !important;
    backdrop-filter: blur(12px) !important;
}

div[data-testid="stChatMessage"] {
    background: rgba(20, 27, 45, 0.5) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 14px !important;
    padding: 14px 18px !important;
    margin-bottom: 12px !important;
}

/* Interactive Prompt Chips */
.prompt-chip {
    display: inline-block;
    background: rgba(139, 92, 246, 0.12);
    border: 1px solid rgba(139, 92, 246, 0.3);
    color: var(--highlight);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.82rem;
    margin: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.prompt-chip:hover {
    background: rgba(139, 92, 246, 0.25);
    border-color: var(--secondary-accent);
    color: #FFFFFF;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #080B14;
}
::-webkit-scrollbar-thumb {
    background: #1E293B;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #334155;
}
</style>
"""
