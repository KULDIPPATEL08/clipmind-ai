"""Next-Level modern styling — premium AI SaaS glassmorphism, GSAP-class animations, cinematic dark mode for ClipMind AI."""

MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* =========================================================================
   PREMIUM DESIGN TOKENS — ClipMind AI Creator Studio
   ========================================================================= */
:root {
    --font-sans: 'Space Grotesk', 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
    --bg-void: #03050c;
    --bg-deep: #060912;
    --bg-glass: rgba(16, 24, 48, 0.72);
    --bg-glass-elevated: rgba(22, 33, 62, 0.88);
    --border-void: rgba(255, 255, 255, 0.05);
    --border-glass: rgba(255, 255, 255, 0.09);
    --border-accent: rgba(99, 102, 241, 0.45);
    --border-cyan: rgba(6, 182, 212, 0.35);
    --border-pink: rgba(236, 72, 153, 0.35);
    --neon-indigo: #6366f1;
    --neon-violet: #8b5cf6;
    --neon-cyan: #06b6d4;
    --neon-emerald: #10b981;
    --neon-pink: #ec4899;
    --neon-amber: #f59e0b;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --text-accent: #a5b4fc;
}

html, body, [class*="css"] {
    font-family: var(--font-sans) !important;
    -webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
}

/* GLOBAL KEY ANIMATIONS */
@keyframes gradientFlow {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

@keyframes logoSheen {
    0% { left: -60%; }
    40%, 100% { left: 150%; }
}

@keyframes auroraRotate {
    from { transform: rotate(0deg) scale(1.02); }
    to { transform: rotate(360deg) scale(1.02); }
}

@keyframes borderGlow {
    0%, 100% { border-color: rgba(99, 102, 241, 0.3); }
    50% { border-color: rgba(6, 182, 212, 0.5); }
}

@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.0); }
    50% { box-shadow: 0 0 0 6px rgba(99, 102, 241, 0.25); }
}

@keyframes scissorBob {
    0%, 100% { transform: rotate(-8deg) scale(1); }
    50% { transform: rotate(8deg) scale(1.12); }
}

@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes shimmerSweep {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}

/* Respect prefers-reduced-motion: disable all animations for accessibility */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.001ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.001ms !important;
    }
}

/* =========================================================================
   AURORA ANIMATED BACKGROUND
   ========================================================================= */
.stApp {
    background-color: var(--bg-void) !important;
    background-image:
        radial-gradient(ellipse 80% 60% at 10% -10%, rgba(99, 102, 241, 0.12) 0%, transparent 55%),
        radial-gradient(ellipse 60% 50% at 90% 110%, rgba(6, 182, 212, 0.10) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 50% 50%, rgba(139, 92, 246, 0.06) 0%, transparent 60%),
        linear-gradient(rgba(255, 255, 255, 0.012) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.012) 1px, transparent 1px) !important;
    background-size: 100% 100%, 100% 100%, 100% 100%, 52px 52px, 52px 52px !important;
    min-height: 100vh !important;
}

/* AI Cockpit Status Strip */
.ai-cockpit-status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 16px;
    background: rgba(10, 15, 28, 0.8);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-glass);
    border-radius: 999px;
    margin-bottom: 20px;
    font-size: 0.72rem;
    font-family: var(--font-mono);
    color: var(--text-secondary);
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.ai-status-item {
    display: flex;
    align-items: center;
    gap: 6px;
}

.ai-pulse-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background-color: var(--neon-emerald);
    box-shadow: 0 0 10px var(--neon-emerald);
    animation: aiPulse 2s infinite ease-in-out;
}

.ai-pulse-dot.cyan {
    background-color: var(--neon-cyan);
    box-shadow: 0 0 10px var(--neon-cyan);
}

.ai-pulse-dot.indigo {
    background-color: var(--neon-indigo);
    box-shadow: 0 0 10px var(--neon-indigo);
}

@keyframes aiPulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.85); }
}

/* Futuristic Brand Header */
.clipmind-brand-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 0 16px 0;
    margin-bottom: 24px;
    border-bottom: 1px solid var(--border-glass);
    position: relative;
}

.clipmind-brand-header::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    width: 180px;
    height: 2px;
    background: linear-gradient(90deg, #6366f1, #06b6d4, transparent);
    box-shadow: 0 0 14px #6366f1;
}

.clipmind-brand-left {
    display: flex;
    align-items: center;
    gap: 16px;
}

.clipmind-logo-badge {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #0891b2 100%);
    color: white;
    font-family: var(--font-sans);
    font-weight: 900;
    font-size: 18px;
    padding: 10px 16px;
    border-radius: 14px;
    box-shadow: 0 0 32px rgba(79, 70, 229, 0.55), inset 0 1px 0 rgba(255,255,255,0.22);
    letter-spacing: 0.04em;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(255, 255, 255, 0.18);
    position: relative;
    overflow: hidden;
}

.clipmind-logo-badge::after {
    content: '';
    position: absolute;
    top: 0; left: -60%;
    width: 50%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.22), transparent);
    animation: logoSheen 4s infinite ease-in-out;
    pointer-events: none;
}

.clipmind-header-text h1 {
    font-size: 2.0rem !important;
    font-weight: 800 !important;
    margin: 0 !important;
    line-height: 1.12 !important;
    background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 40%, #94a3b8 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    letter-spacing: -0.035em;
}

.clipmind-header-text p {
    font-size: 0.87rem !important;
    color: #64748b !important;
    margin: 4px 0 0 0 !important;
    letter-spacing: -0.01em;
    font-weight: 500;
}

/* Landing Page Hero Section */
.landing-hero-box {
    background: linear-gradient(135deg, rgba(20, 28, 48, 0.85) 0%, rgba(10, 16, 30, 0.95) 100%);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 20px;
    padding: 36px 40px;
    margin: 16px 0 28px 0;
    box-shadow: 0 24px 60px -15px rgba(0, 0, 0, 0.6), 0 0 35px rgba(99, 102, 241, 0.15);
    position: relative;
    overflow: hidden;
}

.landing-hero-box::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 250px;
    height: 250px;
    background: radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, transparent 70%);
    pointer-events: none;
}

.hero-pill-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.35);
    color: #a5b4fc;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 6px 14px;
    border-radius: 999px;
    margin-bottom: 16px;
    box-shadow: 0 0 16px rgba(99, 102, 241, 0.2);
}

.hero-headline {
    font-size: 2.35rem;
    font-weight: 900;
    line-height: 1.22;
    color: #ffffff;
    margin-bottom: 12px;
    letter-spacing: -0.03em;
}

.hero-subhead {
    font-size: 1.05rem;
    line-height: 1.6;
    color: #94a3b8;
    max-width: 820px;
    margin-bottom: 24px;
}

/* Feature Capabilities Grid */
.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin: 24px 0 12px 0;
}

.feature-card {
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border-glass);
    border-radius: 14px;
    padding: 20px 22px;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.feature-card:hover {
    transform: translateY(-4px);
    border-color: rgba(99, 102, 241, 0.45);
    box-shadow: 0 16px 36px rgba(99, 102, 241, 0.2);
}

.feature-icon-box {
    width: 42px;
    height: 42px;
    border-radius: 10px;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(6, 182, 212, 0.2));
    border: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    margin-bottom: 12px;
}

.feature-title {
    font-size: 1.0rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 6px;
    letter-spacing: -0.01em;
}

.feature-desc {
    font-size: 0.84rem;
    color: #94a3b8;
    line-height: 1.5;
}

/* Pipeline Stepper */
.pipeline-stepper {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(10, 15, 28, 0.6);
    border: 1px solid var(--border-glass);
    border-radius: 12px;
    padding: 14px 20px;
    margin: 24px 0;
    gap: 8px;
    overflow-x: auto;
}

.step-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.82rem;
    font-weight: 600;
    color: #cbd5e1;
    white-space: nowrap;
}

.step-num {
    background: rgba(99, 102, 241, 0.2);
    border: 1px solid rgba(99, 102, 241, 0.4);
    color: #a5b4fc;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    padding: 3px 8px;
    border-radius: 6px;
}

.step-arrow {
    color: #475569;
    font-size: 0.9rem;
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
    font-weight: 800 !important;
    font-size: 1.65rem !important;
}

/* Next-Level Narrative Glass Card */
.narrative-hero-card {
    background: linear-gradient(135deg, rgba(24, 34, 58, 0.85) 0%, rgba(12, 18, 32, 0.95) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 18px;
    padding: 26px 30px;
    margin: 20px 0 28px 0;
    box-shadow: 0 18px 45px -10px rgba(0, 0, 0, 0.55), 0 0 24px rgba(99, 102, 241, 0.15);
}

.narrative-title {
    font-size: 1.4rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.narrative-synopsis {
    font-size: 1.02rem;
    line-height: 1.7;
    color: #cbd5e1;
    margin-bottom: 18px;
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
    gap: 7px;
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-family: var(--font-mono);
    font-weight: 700;
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.18);
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.35);
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
}

.swatch-circle {
    width: 13px;
    height: 13px;
    border-radius: 50%;
    border: 1.5px solid rgba(255, 255, 255, 0.7);
    display: inline-block;
}

/* Motion Energy Gauge */
.motion-bar-track {
    width: 100%;
    height: 9px;
    background-color: rgba(255, 255, 255, 0.08);
    border-radius: 999px;
    overflow: hidden;
    margin-top: 6px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.motion-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #10b981 0%, #06b6d4 50%, #f59e0b 80%, #ef4444 100%);
    box-shadow: 0 0 10px rgba(6, 182, 212, 0.5);
    transition: width 0.4s ease;
}

/* Timeline Track */
.timeline-track {
    display: flex;
    width: 100%;
    height: 44px;
    border-radius: 12px;
    overflow: hidden;
    background-color: rgba(10, 16, 30, 0.9);
    border: 1px solid var(--border-glass);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.45);
    margin: 18px 0 10px 0;
}

.timeline-segment {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
    color: #ffffff;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    border-right: 1px solid rgba(0, 0, 0, 0.45);
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.9);
}

.timeline-segment:hover {
    filter: brightness(1.3) saturate(1.25);
    transform: scaleY(1.08);
    z-index: 2;
}

/* Status Badges */
.badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
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

/* Streamlit Tabs Styling */
div[data-testid="stTabs"] button[role="tab"] {
    font-family: var(--font-sans) !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
    background: transparent !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 10px 18px !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #ffffff !important;
    border-bottom: 2px solid var(--neon-indigo) !important;
    text-shadow: 0 0 12px rgba(99, 102, 241, 0.6);
}

/* Primary and Download Button Styling */
div.stButton > button, div.stDownloadButton > button {
    font-family: var(--font-sans) !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 0.01em !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.28) !important;
    position: relative !important;
    overflow: hidden !important;
}

div.stButton > button:hover, div.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.38) !important;
    border-color: rgba(99, 102, 241, 0.75) !important;
}

div.stButton > button:active {
    transform: translateY(0px) !important;
}

/* =========================================================================
   🎞️ PHYSICAL FILMSTRIP SCISSORS CUTTING ANIMATION & CLIP CARDS
   ========================================================================= */

@keyframes scissorSlice {
    0% { transform: scale(1) rotate(0deg); }
    20% { transform: scale(1.2) rotate(-18deg); filter: drop-shadow(0 0 10px #ec4899); }
    45% { transform: scale(0.92) rotate(14deg); }
    70% { transform: scale(1.12) rotate(-8deg); }
    100% { transform: scale(1) rotate(0deg); }
}

@keyframes bladeFlash {
    0% { left: -30%; opacity: 0; }
    50% { opacity: 1; }
    100% { left: 130%; opacity: 0; }
}

@keyframes sprocketScroll {
    from { background-position: 0 0; }
    to { background-position: 48px 0; }
}

/* Filmstrip Perforation Header & Footer */
.filmstrip-sprockets {
    height: 14px;
    width: 100%;
    background-color: #0b0f19;
    background-image: 
        radial-gradient(ellipse at center, rgba(255, 255, 255, 0.22) 32%, transparent 36%);
    background-size: 16px 14px;
    background-repeat: repeat-x;
    border-radius: 6px;
    margin: 4px 0;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.6);
}

.cutting-machine-banner {
    background: linear-gradient(135deg, rgba(20, 28, 48, 0.95) 0%, rgba(10, 16, 28, 0.98) 100%);
    border: 1px solid rgba(236, 72, 153, 0.35);
    border-radius: 16px;
    padding: 20px 24px;
    margin: 16px 0 24px 0;
    box-shadow: 0 12px 35px rgba(236, 72, 153, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    position: relative;
    overflow: hidden;
}

.cutting-machine-banner::after {
    content: '';
    position: absolute;
    top: 0;
    left: -30%;
    width: 25%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(236, 72, 153, 0.25), transparent);
    animation: bladeFlash 3.5s infinite ease-in-out;
    pointer-events: none;
}

.cutter-title {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 1.15rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 6px;
}

.scissor-icon-animated {
    font-size: 1.6rem;
    display: inline-block;
    animation: scissorSlice 2.4s infinite ease-in-out;
}

.cutter-subhead {
    font-size: 0.88rem;
    color: #94a3b8;
    line-height: 1.5;
}

/* Individual Film Clip Card */
.film-clip-card {
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 20px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
}

.film-clip-card:hover {
    transform: translateY(-3px);
    border-color: rgba(236, 72, 153, 0.5);
    box-shadow: 0 12px 32px rgba(236, 72, 153, 0.2);
}

.clip-badge-cut {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
    font-family: var(--font-mono);
    background: rgba(236, 72, 153, 0.15);
    border: 1px solid rgba(236, 72, 153, 0.4);
    color: #f472b6;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* =========================================================================
   🎛️ PRO IDE STUDIO INSPECTOR SIDEBAR
   ========================================================================= */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070b14 0%, #05080f 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
}

.studio-inspector-header {
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 16px;
}

.studio-title {
    font-size: 0.88rem;
    font-weight: 800;
    color: #f8fafc;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
}

.studio-telemetry {
    font-size: 0.68rem;
    font-family: var(--font-mono);
    color: var(--neon-cyan);
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* =========================================================================
   📦 STAGED VIDEO READY CARD (TWO-STEP UPLOAD)
   ========================================================================= */

.staged-video-card {
    background: linear-gradient(135deg, rgba(16, 24, 50, 0.96) 0%, rgba(8, 14, 30, 0.99) 100%);
    border: 1.5px solid rgba(6, 182, 212, 0.42);
    border-radius: 22px;
    padding: 26px 32px;
    margin: 16px 0 24px 0;
    box-shadow: 0 20px 55px rgba(6, 182, 212, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.08);
    position: relative;
    overflow: hidden;
}

.staged-video-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #06b6d4, #6366f1, #ec4899, #06b6d4);
    background-size: 200% 100%;
    animation: gradientFlow 4s ease-in-out infinite;
}

.staged-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}

.staged-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 10px;
}

.staged-filename {
    font-family: var(--font-mono);
    color: #38bdf8;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.3);
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.82rem;
}

.staged-details-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    background: rgba(10, 15, 26, 0.6);
    border-radius: 10px;
    padding: 12px 16px;
    margin: 14px 0 18px 0;
}

.staged-detail-item {
    font-size: 0.78rem;
    color: #94a3b8;
}

.staged-detail-item b {
    color: #f1f5f9;
    display: block;
    font-size: 0.88rem;
    margin-top: 2px;
}

/* =========================================================================
   🤖 AI VIDEO COPILOT CHATBOT STYLES
   ========================================================================= */

.copilot-card {
    background: linear-gradient(135deg, rgba(16, 22, 48, 0.93) 0%, rgba(6, 10, 24, 0.98) 100%);
    border: 1.5px solid rgba(99, 102, 241, 0.28);
    border-radius: 24px;
    padding: 26px 30px;
    margin: 14px 0 22px 0;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.58), 0 0 30px rgba(99, 102, 241, 0.08);
    position: relative;
    overflow: hidden;
}

.copilot-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4, #6366f1);
    background-size: 200% 100%;
    animation: gradientFlow 4s ease-in-out infinite;
}

.copilot-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 14px;
    margin-bottom: 18px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.copilot-agent-badge {
    display: flex;
    align-items: center;
    gap: 12px;
}

.copilot-avatar {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: linear-gradient(135deg, #6366f1, #06b6d4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    box-shadow: 0 0 16px rgba(99, 102, 241, 0.5);
}

.copilot-info h4 {
    margin: 0;
    font-size: 1.05rem;
    font-weight: 800;
    color: #ffffff;
}

.copilot-info span {
    font-size: 0.76rem;
    font-family: var(--font-mono);
    color: #34d399;
}

.prompt-suggestions-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 18px;
}

.prompt-chip {
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.28);
    color: #cbd5e1;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 999px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.prompt-chip:hover {
    background: rgba(99, 102, 241, 0.25);
    color: #ffffff;
    border-color: rgba(99, 102, 241, 0.6);
    transform: translateY(-1px);
}

.chat-bubble-user {
    background: rgba(99, 102, 241, 0.2);
    border: 1px solid rgba(99, 102, 241, 0.4);
    border-radius: 14px 14px 2px 14px;
    padding: 12px 16px;
    color: #f8fafc;
    font-size: 0.92rem;
    margin: 10px 0 14px auto;
    max-width: 80%;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.chat-bubble-ai {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 14px 14px 14px 2px;
    padding: 16px 20px;
    color: #cbd5e1;
    font-size: 0.92rem;
    line-height: 1.6;
    margin: 10px 0 16px 0;
    max-width: 90%;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
}

/* =========================================================================
   🚫 COMPLETE SIDEBAR ELIMINATION & FULL-PAGE STUDIO CANVAS
   ========================================================================= */

section[data-testid="stSidebar"],
div[data-testid="collapsedControl"],
button[data-testid="baseButton-headerNoPadding"] {
    display: none !important;
}

.main .block-container {
    max-width: 1480px !important;
    padding-top: 1.2rem !important;
    padding-left: 2.4rem !important;
    padding-right: 2.4rem !important;
    padding-bottom: 4rem !important;
}

/* =========================================================================
   📸 CINEMATIC CAMERA APERTURE & SHUTTER STUTTER INTRO
   ========================================================================= */

@keyframes filmStutter {
    0% { opacity: 0; transform: translate(0, 8px) scale(0.99); filter: brightness(1.6) saturate(0); }
    8% { opacity: 0.7; transform: translate(-2px, 0) scale(1.005); filter: brightness(1.3); }
    18% { opacity: 0.5; transform: translate(2px, -1px) scale(0.998); filter: brightness(1.6); }
    28% { opacity: 0.9; transform: translate(0, 0) scale(1.002); filter: brightness(1.1); }
    38% { opacity: 0.75; transform: translate(-1px, 1px); }
    100% { opacity: 1; transform: translate(0, 0) scale(1); filter: brightness(1) saturate(1); }
}

@keyframes aperturePulse {
    0%, 100% {
        box-shadow: 0 0 22px rgba(236,72,153,0.35), 0 0 44px rgba(99,102,241,0.2), inset 0 0 18px rgba(6,182,212,0.2);
        transform: scale(1);
    }
    50% {
        box-shadow: 0 0 40px rgba(6,182,212,0.55), 0 0 65px rgba(236,72,153,0.25), inset 0 0 30px rgba(99,102,241,0.3);
        transform: scale(1.07);
    }
}

.cinematic-shutter-intro {
    background: radial-gradient(ellipse 90% 80% at 50% 20%, rgba(26, 38, 72, 0.94) 0%, rgba(4, 7, 18, 0.98) 100%);
    border: 1.5px solid rgba(99, 102, 241, 0.38);
    border-radius: 28px;
    padding: 40px 48px;
    margin: 8px 0 28px 0;
    position: relative;
    overflow: hidden;
    animation: filmStutter 0.9s cubic-bezier(0.16, 1, 0.3, 1) 1, borderGlow 6s ease-in-out infinite 1s;
    box-shadow: 0 32px 85px rgba(0,0,0,0.75), 0 0 55px rgba(99,102,241,0.18);
}

.cinematic-shutter-intro::before {
    content: '';
    position: absolute;
    top: -60%; left: -60%;
    width: 220%; height: 220%;
    background: conic-gradient(from 0deg, transparent, rgba(99,102,241,0.05), transparent 30%, rgba(6,182,212,0.05), transparent 60%, rgba(236,72,153,0.04), transparent);
    animation: auroraRotate 30s linear infinite;
    pointer-events: none;
}

.cinematic-shutter-intro::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 340px; height: 340px;
    background: radial-gradient(circle, rgba(6,182,212,0.13) 0%, transparent 70%);
    pointer-events: none;
}

.aperture-emblem {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 58px; height: 58px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #06b6d4 100%);
    border: 2px solid rgba(255, 255, 255, 0.32);
    font-size: 1.55rem;
    animation: aperturePulse 3.5s infinite ease-in-out;
    flex-shrink: 0;
    position: relative;
    z-index: 1;
}

/* =========================================================================
   ✏️ FIGMA DOODLE GRAPHIC ACCENTS & CREATOR BADGES
   ========================================================================= */

.figma-doodle-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(245, 158, 11, 0.15);
    border: 1.5px dashed rgba(245, 158, 11, 0.55);
    color: #fde68a;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 4px 14px;
    border-radius: 8px;
    transform: rotate(-1.2deg);
    margin-right: 8px;
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.15);
}

.creator-tape-badge {
    background: rgba(236, 72, 153, 0.18);
    border: 1px dashed rgba(236, 72, 153, 0.5);
    color: #f472b6;
    font-family: var(--font-mono);
    font-size: 0.76rem;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 6px;
    transform: rotate(1deg);
    display: inline-block;
}

.audio-sound-active-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16, 185, 129, 0.16);
    border: 1px solid rgba(16, 185, 129, 0.45);
    color: #34d399;
    font-size: 0.74rem;
    font-family: var(--font-mono);
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 999px;
    letter-spacing: 0.04em;
}

/* =========================================================================
   🎛️ ON-PAGE STUDIO CONTROL DECK (NO SIDEBAR NEEDED)
   ========================================================================= */

.onpage-studio-deck {
    background: linear-gradient(135deg, rgba(16, 24, 44, 0.9) 0%, rgba(8, 14, 28, 0.96) 100%);
    border: 1px solid rgba(99, 102, 241, 0.28);
    border-radius: 18px;
    padding: 22px 28px;
    margin: 18px 0 24px 0;
    box-shadow: 0 14px 40px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.deck-headline {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 12px;
    margin-bottom: 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.deck-title {
    font-size: 1.12rem;
    font-weight: 800;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 10px;
}

.deck-specs-tag {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: #06b6d4;
    background: rgba(6, 182, 212, 0.12);
    border: 1px solid rgba(6, 182, 212, 0.3);
    padding: 3px 10px;
    border-radius: 999px;
}

/* =========================================================================
   ✂️ PRECISION TIMECODE CLIP TRIMMER
   ========================================================================= */

.precision-trimmer-card {
    background: linear-gradient(135deg, rgba(20, 28, 56, 0.93) 0%, rgba(8, 13, 28, 0.98) 100%);
    border: 1.5px solid rgba(236, 72, 153, 0.32);
    border-radius: 22px;
    padding: 26px 32px;
    margin: 16px 0 24px 0;
    box-shadow: 0 20px 55px rgba(236, 72, 153, 0.1);
    position: relative;
    overflow: hidden;
}

.precision-trimmer-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #ec4899, #8b5cf6, #06b6d4);
    background-size: 200% 100%;
    animation: gradientFlow 3s ease-in-out infinite;
}

.trimmer-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
    letter-spacing: -0.025em;
}

/* Scrollbar premium styling */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); border-radius: 3px; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.35); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.62); }

/* Video player */
div[data-testid="stVideo"] video {
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    box-shadow: 0 12px 38px rgba(0,0,0,0.58) !important;
}

/* Image hover zoom */
div[data-testid="stImage"] img {
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.48) !important;
    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
div[data-testid="stImage"] img:hover { transform: scale(1.025) !important; }

/* Progress bar animated gradient */
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #6366f1, #06b6d4, #ec4899) !important;
    background-size: 200% 100% !important;
    animation: gradientFlow 2s ease-in-out infinite !important;
    border-radius: 999px !important;
}

/* Expander premium */
div[data-testid="stExpander"] {
    background: rgba(8, 13, 28, 0.78) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 16px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 8px 28px rgba(0,0,0,0.35) !important;
    backdrop-filter: blur(16px) !important;
    transition: all 0.25s ease !important;
}
div[data-testid="stExpander"]:hover {
    border-color: rgba(99,102,241,0.38) !important;
    box-shadow: 0 12px 38px rgba(99,102,241,0.14) !important;
}

/* Dataframe */
div[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    box-shadow: 0 8px 28px rgba(0,0,0,0.4) !important;
}

/* Dividers */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.3), rgba(6,182,212,0.3), transparent) !important;
    margin: 24px 0 !important;
}

/* Responsive */
@media (max-width: 768px) {
    .cinematic-shutter-intro { padding: 24px 22px; border-radius: 20px; }
    .hero-headline { font-size: 1.85rem; }
    .main .block-container { padding-left: 1.2rem !important; padding-right: 1.2rem !important; }
}

/* =========================================================================
   🛡️ ERROR & WARNING STATES — FRIENDLY, BRANDED
   ========================================================================= */

div[data-testid="stAlert"] {
    border-radius: 14px !important;
    border-width: 1px !important;
    backdrop-filter: blur(10px) !important;
}

div[data-testid="stAlert"][data-baseweb="notification"] {
    font-family: var(--font-sans) !important;
    font-size: 0.93rem !important;
}

/* Success alert — emerald glow */
div[data-testid="stAlert"].st-success {
    background: rgba(16, 185, 129, 0.12) !important;
    border-color: rgba(16, 185, 129, 0.4) !important;
    color: #a7f3d0 !important;
}

/* Error alert — rose glow */
div[data-testid="stAlert"].st-error {
    background: rgba(239, 68, 68, 0.12) !important;
    border-color: rgba(239, 68, 68, 0.4) !important;
    color: #fca5a5 !important;
}

/* Warning alert — amber glow */
div[data-testid="stAlert"].st-warning {
    background: rgba(245, 158, 11, 0.12) !important;
    border-color: rgba(245, 158, 11, 0.4) !important;
    color: #fde68a !important;
}

/* Info alert — cyan glow */
div[data-testid="stAlert"].st-info {
    background: rgba(6, 182, 212, 0.10) !important;
    border-color: rgba(6, 182, 212, 0.35) !important;
    color: #a5f3fc !important;
}

/* =========================================================================
   ✨ RESULTS WORKSPACE — FADE-IN ENTRANCE ANIMATION
   ========================================================================= */

.results-workspace-fadeIn {
    animation: fadeSlideIn 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
}

/* Spinner overlay styling */
div[data-testid="stSpinner"] {
    color: var(--neon-cyan) !important;
}

/* File uploader drop zone */
div[data-testid="stFileUploader"] {
    border-radius: 16px !important;
}

div[data-testid="stFileUploader"] > section {
    border: 2px dashed rgba(99, 102, 241, 0.4) !important;
    border-radius: 16px !important;
    background: rgba(10, 15, 30, 0.6) !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stFileUploader"] > section:hover {
    border-color: rgba(99, 102, 241, 0.75) !important;
    background: rgba(99, 102, 241, 0.06) !important;
    box-shadow: 0 0 24px rgba(99, 102, 241, 0.15) !important;
}
</style>
"""
