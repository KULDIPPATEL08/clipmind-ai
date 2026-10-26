"""Next-Level modern styling, glassmorphism, and cyber-aesthetic design tokens for ClipMind AI."""

MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --font-sans: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    --bg-main: #090d16;
    --bg-glass: rgba(18, 24, 38, 0.72);
    --bg-glass-elevated: rgba(26, 35, 54, 0.85);
    --border-glass: rgba(255, 255, 255, 0.08);
    --border-accent: rgba(99, 102, 241, 0.5);
    --neon-indigo: #6366f1;
    --neon-cyan: #06b6d4;
    --neon-emerald: #10b981;
    --neon-pink: #ec4899;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
}

html, body, [class*="css"] {
    font-family: var(--font-sans) !important;
}

/* Futuristic Brand Header */
.clipmind-brand-header {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 24px 0 16px 0;
    margin-bottom: 24px;
    border-bottom: 1px solid var(--border-glass);
    position: relative;
}

.clipmind-brand-header::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    width: 140px;
    height: 2px;
    background: linear-gradient(90deg, #6366f1, #06b6d4, transparent);
    box-shadow: 0 0 12px #6366f1;
}

.clipmind-logo-badge {
    background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
    color: white;
    font-weight: 800;
    font-size: 22px;
    padding: 10px 16px;
    border-radius: 12px;
    box-shadow: 0 0 25px rgba(79, 70, 229, 0.45);
    letter-spacing: 0.05em;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.clipmind-header-text h1 {
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    margin: 0 !important;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #94a3b8 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    letter-spacing: -0.03em;
}

.clipmind-header-text p {
    font-size: 0.98rem !important;
    color: #94a3b8 !important;
    margin: 4px 0 0 0 !important;
    letter-spacing: -0.01em;
}

/* Glassmorphic Metric KPI Cards */
div[data-testid="stMetric"] {
    background: var(--bg-glass) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.35) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: rgba(99, 102, 241, 0.4) !important;
    box-shadow: 0 12px 36px 0 rgba(99, 102, 241, 0.2) !important;
}

div[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

div[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    font-size: 1.6rem !important;
}

/* Next-Level Narrative Glass Card */
.narrative-hero-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 16px;
    padding: 24px 28px;
    margin: 20px 0 28px 0;
    box-shadow: 0 16px 40px -10px rgba(0, 0, 0, 0.5), 0 0 20px rgba(99, 102, 241, 0.12);
}

.narrative-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.narrative-synopsis {
    font-size: 1.0rem;
    line-height: 1.65;
    color: #cbd5e1;
    margin-bottom: 16px;
}

/* Palette Swatches */
.palette-container {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin: 12px 0;
}

.palette-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 8px;
    font-size: 0.78rem;
    font-family: var(--font-mono);
    font-weight: 600;
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.swatch-circle {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    border: 1px solid rgba(255, 255, 255, 0.4);
    display: inline-block;
}

/* Motion Energy Gauge */
.motion-gauge-box {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid var(--border-glass);
    border-radius: 10px;
    padding: 10px 14px;
    margin-top: 10px;
}

.motion-bar-track {
    width: 100%;
    height: 8px;
    background-color: rgba(255, 255, 255, 0.08);
    border-radius: 999px;
    overflow: hidden;
    margin-top: 6px;
}

.motion-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #10b981 0%, #06b6d4 50%, #f59e0b 80%, #ef4444 100%);
    transition: width 0.4s ease;
}

/* Timeline Track */
.timeline-track {
    display: flex;
    width: 100%;
    height: 42px;
    border-radius: 10px;
    overflow: hidden;
    background-color: rgba(15, 23, 42, 0.85);
    border: 1px solid var(--border-glass);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    margin: 16px 0 10px 0;
}

.timeline-segment {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.78rem;
    font-weight: 700;
    color: #ffffff;
    cursor: pointer;
    transition: all 0.2s ease;
    border-right: 1px solid rgba(0, 0, 0, 0.4);
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8);
}

.timeline-segment:hover {
    filter: brightness(1.25) saturate(1.2);
    transform: scaleY(1.06);
    z-index: 2;
}

/* Status Badges */
.badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-rapid {
    background-color: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.35);
}

.badge-standard {
    background-color: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.35);
}

.badge-extended {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.35);
}

/* Scene Card Container */
.scene-detail-card {
    background: var(--bg-glass);
    border: 1px solid var(--border-glass);
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 14px;
    transition: border-color 0.2s ease;
}

.scene-detail-card:hover {
    border-color: rgba(99, 102, 241, 0.4);
}

/* Buttons Styling */
button[kind="primary"], div.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s ease !important;
}

div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35) !important;
}
</style>
"""
