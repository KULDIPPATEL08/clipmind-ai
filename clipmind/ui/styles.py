"""Custom styling and CSS tokens for modern, clean ClipMind AI interface."""

MAIN_CSS = """
<style>
/* Main typography and root variables */
:root {
    --bg-primary: #0f131a;
    --bg-secondary: #171d27;
    --bg-card: #1f2735;
    --border-subtle: #2d3848;
    --border-accent: #3b82f6;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --accent-blue: #2563eb;
    --accent-emerald: #10b981;
    --accent-amber: #f59e0b;
    --accent-indigo: #6366f1;
}

/* App Header Styling */
.clipmind-brand-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px 0 10px 0;
    margin-bottom: 24px;
    border-bottom: 1px solid var(--border-subtle);
}

.clipmind-logo-badge {
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    color: white;
    font-weight: 800;
    font-size: 20px;
    padding: 8px 14px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.clipmind-header-text h1 {
    font-size: 1.85rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em;
}

.clipmind-header-text p {
    font-size: 0.95rem !important;
    color: var(--text-secondary) !important;
    margin: 2px 0 0 0 !important;
}

/* KPI Metric Cards */
.kpi-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
    margin: 16px 0 24px 0;
}

.kpi-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    padding: 14px 16px;
    text-align: left;
    transition: transform 0.15s ease, border-color 0.15s ease;
}

.kpi-card:hover {
    border-color: #475569;
}

.kpi-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-secondary);
    margin-bottom: 4px;
}

.kpi-value {
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--text-primary);
}

.kpi-sub {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 2px;
}

/* Timeline Visualizer */
.timeline-track {
    display: flex;
    width: 100%;
    height: 38px;
    border-radius: 8px;
    overflow: hidden;
    background-color: #1a202c;
    border: 1px solid var(--border-subtle);
    margin: 14px 0 8px 0;
}

.timeline-segment {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 600;
    color: #ffffff;
    cursor: pointer;
    transition: opacity 0.15s ease, filter 0.15s ease;
    border-right: 1px solid rgba(0,0,0,0.3);
}

.timeline-segment:hover {
    filter: brightness(1.2);
}

/* Pacing Badges */
.badge-rapid {
    background-color: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-standard {
    background-color: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.3);
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-extended {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* Keyframe Card */
.keyframe-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 16px;
}

.keyframe-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background-color: #171d27;
    border-bottom: 1px solid var(--border-subtle);
    font-size: 0.85rem;
    font-weight: 600;
}

.keyframe-body {
    padding: 10px 12px;
    font-size: 0.8rem;
    color: var(--text-secondary);
}

/* Safe notice card */
.notice-card {
    background-color: #1e293b;
    border-left: 4px solid var(--accent-blue);
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin: 16px 0;
    font-size: 0.88rem;
    color: #cbd5e1;
}
</style>
"""
