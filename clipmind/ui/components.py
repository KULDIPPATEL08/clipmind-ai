"""Reusable UI presentation components for Streamlit interface."""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import List, Optional

import streamlit as st

from clipmind.analysis.chatbot import answer_video_query
from clipmind.analysis.description import FullVideoNarrative, SceneDescription
from clipmind.analysis.summary import VideoSummaryReport
from clipmind.export.exporter import create_interval_clips_zip
from clipmind.video.clipper import extract_fixed_interval_clips, extract_single_custom_clip
from clipmind.video.detector import SceneInfo, seconds_to_timecode
from clipmind.video.keyframe import Keyframe
from clipmind.video.metadata import VideoMetadata


def render_html(html_str: str) -> None:
    """Safely render HTML without CommonMark code-block indentation bugs."""
    clean = "".join(line.strip() for line in html_str.splitlines() if line.strip())
    if hasattr(st, "html"):
        st.html(clean)
    else:
        st.markdown(clean, unsafe_allow_html=True)




def render_full_video_narrative_hero(narrative: FullVideoNarrative) -> None:
    """Renders executive-level narrative synopsis, mood, aesthetic palette, and motion rhythm."""
    swatches_html = "".join([
        f'<span class="palette-chip" style="background-color: {hex_c};">'
        f'<span class="swatch-circle" style="background-color: {hex_c};"></span>{hex_c}</span>'
        for hex_c in narrative.dominant_palette_hex
    ])

    render_html(
        f"""<div class="narrative-hero-card">
            <div class="narrative-title">
                <span>✨ {narrative.title_suggestion}</span>
            </div>
            <div style="display: flex; gap: 10px; margin-bottom: 12px; flex-wrap: wrap;">
                <span class="badge-pill badge-standard">🎭 Mood: {narrative.primary_mood}</span>
                <span class="badge-pill badge-extended">⚡ Tempo: {narrative.tempo_rhythm_summary}</span>
                <span class="badge-pill badge-rapid">🎬 Scenes: {narrative.total_scenes_count} Cuts</span>
            </div>
            <div class="narrative-synopsis">{narrative.executive_synopsis}</div>
            <div style="margin-top: 14px;">
                <span style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8;">
                    Dominant Visual Color Scheme:
                </span>
                <div class="palette-container">{swatches_html}</div>
            </div>
        </div>"""
    )


def render_scene_intelligence_cards(narrative: FullVideoNarrative) -> None:
    """Renders scene-by-scene visual descriptions, motion energy gauges, and color swatches."""
    st.markdown("##### 📝 Deep Scene-by-Scene Visual Descriptions")

    for s in narrative.scenes:
        swatches = "".join([
            f'<span class="palette-chip" style="background-color: {c};">'
            f'<span class="swatch-circle" style="background-color: {c};"></span>{c}</span>'
            for c in s.dominant_hex_colors
        ])

        with st.expander(f"🎬 {s.title}  •  {s.mood_tag}", expanded=(s.scene_number <= 3)):
            st.markdown(f"**Visual Narrative**: {s.summary_narrative}")

            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                st.caption("Shot Type & Framing")
                st.markdown(f"`{s.shot_type_estimate}`")
            with c2:
                st.caption("Lighting Aesthetic")
                st.markdown(f"`{s.lighting_key}`")
            with c3:
                st.caption(f"Motion Energy Score: {s.motion_energy_score}/100 ({s.motion_level})")
                render_html(
                    f"""<div class="motion-bar-track">
                        <div class="motion-bar-fill" style="width: {s.motion_energy_score}%;"></div>
                    </div>"""
                )

            render_html(f'<div class="palette-container">{swatches}</div>')


def render_ai_cockpit_status_bar() -> None:
    """Renders cybernetic telemetry status bar."""
    render_html(
        """<div class="ai-cockpit-status-bar">
            <div class="ai-status-item">
                <span class="ai-pulse-dot"></span>
                <span>Neural Vision Core v2.4 Online</span>
            </div>
            <div class="ai-status-item">
                <span class="ai-pulse-dot cyan"></span>
                <span>120 FPS Scanner Armed</span>
            </div>
            <div class="ai-status-item">
                <span class="ai-pulse-dot indigo"></span>
                <span>Zero-Cloud Retention Enclave</span>
            </div>
            <div class="ai-status-item" style="color: #64748b;">
                <span>Container: MP4 • MOV • MKV • WEBM • AVI</span>
            </div>
        </div>"""
    )


def render_brand_header() -> None:
    """Renders the top branding header with cyberpunk badges."""
    render_html(
        """<div class="clipmind-brand-header">
            <div class="clipmind-brand-left">
                <div class="clipmind-logo-badge">CM</div>
                <div class="clipmind-header-text">
                    <h1>ClipMind AI</h1>
                    <p>Scene-Aware Video Summarization and Keyframe Extraction Platform</p>
                </div>
            </div>
            <div style="display: flex; gap: 8px;">
                <span class="badge-pill badge-standard">⚡ GPU-Independent</span>
                <span class="badge-pill badge-extended">🛡️ Zero-Leak Enclave</span>
            </div>
        </div>"""
    )


def render_landing_showcase() -> None:
    """Renders the high-impact AI landing showcase with cinematic shutter stutter animation and Figma doodle accents."""
    render_html(
        """<div class="cinematic-shutter-intro">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; flex-wrap: wrap; gap: 12px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div class="aperture-emblem">🎬</div>
                    <div>
                        <span class="hero-pill-tag">⚡ Automated Video Intelligence Core</span>
                        <div style="margin-top: 4px;">
                            <span class="figma-doodle-pill">✨ Creator Studio Edition</span>
                            <span class="creator-tape-badge">Opus & Runway AI Ready</span>
                            <span class="audio-sound-active-badge">🔊 100% Sound Intact</span>
                        </div>
                    </div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <span class="badge-pill badge-extended">🛡️ Zero-Leak Local Storage</span>
                    <span class="badge-pill badge-standard">⚡ Hyper-Turbo 3x</span>
                </div>
            </div>
            <div class="hero-headline">Transform Any Video into Precise Scenes, Keyframes & Video Cuts</div>
            <div class="hero-subhead">ClipMind AI combines dual-engine camera motion compensation, neural color profiling, and lossless audio stream muxing to convert raw video into actionable video cuts, storyboard contact sheets, and social creator clips.</div>
            <div class="pipeline-stepper">
                <div class="step-item"><span class="step-num">01</span> Select or Upload Video</div>
                <span class="step-arrow">➔</span>
                <div class="step-item"><span class="step-num">02</span> Preview & Configure Dials</div>
                <span class="step-arrow">➔</span>
                <div class="step-item"><span class="step-num">03</span> Click Start Analysis</div>
                <span class="step-arrow">➔</span>
                <div class="step-item"><span class="step-num">04</span> Download Cuts (With Sound)</div>
            </div>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon-box">⚡</div>
                    <div class="feature-title">Hybrid Precision Cuts</div>
                    <div class="feature-desc">Combines adaptive rolling threshold with HSV color diff to detect hard cuts, pans, and lighting transitions.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon-box">🎬</div>
                    <div class="feature-title">Lossless MP4 Slicing (Audio Intact)</div>
                    <div class="feature-desc">Extracts frame-accurate individual scene video clips preserving 100% of the original audio soundtrack.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon-box">🎨</div>
                    <div class="feature-title">Neural Aesthetic Palette</div>
                    <div class="feature-desc">K-means color clustering extracts exact hex palettes, lighting key, and motion energy gauges for each scene.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon-box">🤖</div>
                    <div class="feature-title">AI Video Copilot</div>
                    <div class="feature-desc">Interactive conversational assistant for TikTok/Reels hooks, music BPM suggestions, and technical breakdowns.</div>
                </div>
            </div>
        </div>"""
    )


def render_metadata_cards(meta: VideoMetadata) -> None:
    """Renders video metadata KPI summary cards."""
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="Duration", value=meta.duration_formatted, delta=f"{meta.duration_seconds:.1f}s")
    with col2:
        st.metric(label="Resolution", value=f"{meta.width}x{meta.height}", delta=meta.aspect_ratio)
    with col3:
        st.metric(label="Frame Rate", value=f"{meta.fps} fps")
    with col4:
        st.metric(label="Total Frames", value=f"{meta.total_frames:,}")
    with col5:
        st.metric(label="File Size", value=f"{meta.file_size_mb} MB", delta=meta.fourcc_codec)


def render_timeline_bar(scenes: List[SceneInfo], total_duration: float) -> None:
    """Renders a visual timeline bar representing scenes proportionally."""
    if not scenes or total_duration <= 0:
        return

    st.markdown("##### ⏱️ Scene Timeline Visualizer")
    colors = ["#2563eb", "#059669", "#d97706", "#7c3aed", "#0891b2", "#dc2626", "#4f46e5", "#16a34a"]

    segments_html = []
    for idx, s in enumerate(scenes):
        pct = max(1.0, (s.duration_seconds / total_duration) * 100)
        c = colors[idx % len(colors)]
        title = f"Scene #{s.scene_number}: {s.start_timecode} - {s.end_timecode} ({s.duration_seconds:.1f}s)"
        seg = (
            f'<div class="timeline-segment" style="width: {pct:.2f}%; background-color: {c};" '
            f'title="{title}">#{s.scene_number}</div>'
        )
        segments_html.append(seg)

    render_html(f'<div class="timeline-track">{"".join(segments_html)}</div>')
    st.caption("Hover over timeline segments to view scene start, end, and duration timecodes.")


def render_summary_analytics(summary: VideoSummaryReport) -> None:
    """Renders pacing analytics and narrative structure."""
    st.markdown("##### 📊 Pacing & Scene Distribution")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="Total Scenes", value=summary.total_scenes)
    with c2:
        st.metric(label="Avg Scene Duration", value=f"{summary.avg_scene_duration_seconds:.1f}s")
    with c3:
        st.metric(label="Scene Frequency", value=f"{summary.scenes_per_minute}/min")
    with c4:
        st.metric(label="Keyframes Extracted", value=summary.extracted_keyframes_count)

    render_html(
        f"""<div style="display: flex; gap: 12px; margin-top: 8px; flex-wrap: wrap;">
            <span class="badge-rapid">⚡ Rapid Cuts (&lt;2s): {summary.rapid_scenes_count} ({summary.rapid_scenes_pct}%)</span>
            <span class="badge-standard">🎬 Standard (2-8s): {summary.standard_scenes_count} ({summary.standard_scenes_pct}%)</span>
            <span class="badge-extended">🌿 Extended (&gt;8s): {summary.extended_scenes_count} ({summary.extended_scenes_pct}%)</span>
        </div>"""
    )

    if summary.narrative_breakdown:
        st.markdown("##### 📖 Structural Video Breakdown")
        for item in summary.narrative_breakdown:
            with st.expander(f"{item['phase']} — {item['scenes_range']} ({item['timecode_range']})", expanded=True):
                st.write(item["description"])

    st.info(f"ℹ️ **Methodology**: {summary.methodology_note}")


def render_keyframe_gallery(
    keyframes: List[Keyframe],
    scenes: List[SceneInfo],
    filter_duplicates: bool = True,
) -> None:
    """Renders a responsive gallery of extracted keyframes with timestamps."""
    st.markdown("##### 🖼️ Extracted Keyframes Gallery")

    display_frames = [
        k for k in keyframes if k.image_path.exists() and (not filter_duplicates or not k.is_duplicate)
    ]

    if not display_frames:
        st.warning("No keyframes available to display.")
        return

    # Filter controls
    search_q = st.text_input("Filter scenes by keyword / number", placeholder="e.g. Scene 2 or 00:01")

    filtered = []
    for kf in display_frames:
        searchable_text = f"scene {kf.scene_number} {kf.timecode}".lower()
        if not search_q or search_q.lower() in searchable_text:
            filtered.append(kf)

    st.caption(f"Showing {len(filtered)} of {len(display_frames)} keyframes.")

    # 3-column responsive layout
    cols = st.columns(3)
    for idx, kf in enumerate(filtered):
        col = cols[idx % 3]
        with col:
            st.image(str(kf.image_path), use_container_width=True)
            caption = f"**Scene #{kf.scene_number:02d}** • `{kf.timecode}`"
            st.markdown(caption)
            with open(kf.image_path, "rb") as img_file:
                st.download_button(
                    label="⬇️ Download Frame",
                    data=img_file.read(),
                    file_name=kf.image_filename,
                    mime="image/jpeg",
                    key=f"dl_kf_{kf.scene_number}_{idx}",
                    use_container_width=True,
                )


def render_studio_inspector_header() -> None:
    """Renders sleek studio IDE inspector telemetry header in the sidebar."""
    render_html(
        """<div class="studio-inspector-header">
            <div class="studio-title">
                <span>🛠️ Studio Inspector</span>
            </div>
            <div class="studio-telemetry">
                <span>8 vCPUs • Zero-Copy RAM • Frame-Lock</span>
            </div>
        </div>"""
    )


def render_precision_clip_trimmer(video_path: Path, metadata: VideoMetadata, output_dir: Path) -> None:
    """Renders interactive precision timecode trimming suite with direct audio playback."""
    video_path = Path(video_path)
    if not video_path.exists():
        st.info(
            "ℹ️ Precision trimmer unavailable — the source video file is not accessible in this session. "
            "You can still download the automatically extracted scene clips below."
        )
        return

    render_html(
        """<div class="precision-trimmer-card">
            <div class="trimmer-title">
                <span>✂️ Precision Clip Trimmer & Audio Slicer</span>
                <span class="audio-sound-active-badge">🔊 High-Fidelity Audio Enabled</span>
            </div>
            <div style="font-size: 0.86rem; color: #94a3b8; margin-bottom: 12px;">
                Drag the timecode slider or enter exact start and end timestamps to render a custom high-quality clip with 100% audio preserved.
            </div>
        </div>"""
    )

    max_sec = max(0.5, float(metadata.duration_seconds))
    min_clip_req = min(70.0, max_sec)

    # Initialize single source-of-truth slider state: timeline starts at 0.0s, minimum 70s
    if "clip_trim_slider" not in st.session_state:
        st.session_state["clip_trim_slider"] = (0.0, min_clip_req)
    else:
        # Validate existing state
        cur_s, cur_e = st.session_state["clip_trim_slider"]
        cur_s = max(0.0, min(float(cur_s), max_sec - 0.1))
        cur_e = max(cur_s + 0.1, min(float(cur_e), max_sec))
        st.session_state["clip_trim_slider"] = (cur_s, cur_e)

    # 1. Quick Presets (One-click jump to exact time ranges)
    st.markdown("###### ⚡ Quick Presets (Min 70s)")
    pr_col1, pr_col2, pr_col3, pr_col4, pr_col5 = st.columns(5)
    with pr_col1:
        if st.button("⏱️ Min Clip (70s)", key="btn_pr_70", use_container_width=True):
            st.session_state["clip_trim_slider"] = (0.0, min_clip_req)
            st.rerun()
    with pr_col2:
        if st.button("⚡ 90s Segment", key="btn_pr_90", use_container_width=True):
            st.session_state["clip_trim_slider"] = (0.0, min(max_sec, max(min_clip_req, 90.0)))
            st.rerun()
    with pr_col3:
        if st.button("🎬 2 Mins (120s)", key="btn_pr_120", use_container_width=True):
            st.session_state["clip_trim_slider"] = (0.0, min(max_sec, max(min_clip_req, 120.0)))
            st.rerun()
    with pr_col4:
        if st.button("🎬 5 Mins (300s)", key="btn_pr_300", use_container_width=True):
            st.session_state["clip_trim_slider"] = (0.0, min(max_sec, max(min_clip_req, 300.0)))
            st.rerun()
    with pr_col5:
        if st.button("🎞️ Full Video", key="btn_pr_all", use_container_width=True):
            st.session_state["clip_trim_slider"] = (0.0, max_sec)
            st.rerun()

    # 2. Main Fine-Tune Slider (Single Source of Truth)
    time_range = st.slider(
        "Fine-Tune Boundary Slider (Timeline starts at 0.0s • Minimum 70s)",
        min_value=0.0,
        max_value=max_sec,
        value=st.session_state["clip_trim_slider"],
        step=0.5,
        format="%.1fs",
        key="clip_trim_slider",
        help="Timeline starts at 0.0s. Drag handles to adjust start and end cut points (min 70s enforced).",
    )

    sel_start, sel_end = time_range
    if sel_start > sel_end:
        sel_start, sel_end = sel_end, sel_start

    # Enforce 70s minimum clip duration
    if (sel_end - sel_start) < min_clip_req and max_sec > min_clip_req:
        if sel_start + min_clip_req <= max_sec:
            sel_end = sel_start + min_clip_req
        else:
            sel_start = max(0.0, sel_end - min_clip_req)
        st.session_state["clip_trim_slider"] = (sel_start, sel_end)

    duration = max(0.1, sel_end - sel_start)

    # 3. Live Synchronized Range Card
    render_html(
        f"""<div style="background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(99, 102, 241, 0.35); border-radius: 14px; padding: 16px 20px; margin: 12px 0 16px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
                <span style="font-size: 0.82rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Selected Cut Range</span>
                <span class="badge-pill badge-extended" style="font-size: 0.72rem;">Min 70s Enforced</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
                <div>
                    <span style="font-size: 0.75rem; color: #64748b; display: block;">START POINT</span>
                    <span style="font-size: 1.15rem; font-weight: 800; color: #38bdf8; font-family: monospace;">{seconds_to_timecode(sel_start)}</span>
                    <span style="font-size: 0.8rem; color: #94a3b8; margin-left: 6px;">({sel_start:.1f}s)</span>
                </div>
                <div style="font-size: 1.2rem; color: #6366f1;">➔</div>
                <div>
                    <span style="font-size: 0.75rem; color: #64748b; display: block;">END POINT</span>
                    <span style="font-size: 1.15rem; font-weight: 800; color: #38bdf8; font-family: monospace;">{seconds_to_timecode(sel_end)}</span>
                    <span style="font-size: 0.8rem; color: #94a3b8; margin-left: 6px;">({sel_end:.1f}s)</span>
                </div>
                <div>
                    <span style="font-size: 0.75rem; color: #64748b; display: block;">CLIP DURATION</span>
                    <span style="font-size: 1.15rem; font-weight: 800; color: #34d399; font-family: monospace;">{duration:.1f}s</span>
                    <span style="font-size: 0.8rem; color: #94a3b8; margin-left: 6px;">({(duration / max_sec) * 100:.1f}% of video)</span>
                </div>
            </div>
        </div>"""
    )

    # 4. Step Adjuster Buttons (Nudge start or end by +/- 5s without desync)
    st.caption("🎯 Quick Fine-Tuning Step Adjusters:")
    st_col1, st_col2 = st.columns(2)
    with st_col1:
        st.markdown("**Start Point Adjuster:**")
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("⏪ -10s Start", key="nudge_s_minus_10", use_container_width=True):
                new_s = max(0.0, sel_start - 10.0)
                st.session_state["clip_trim_slider"] = (new_s, sel_end)
                st.rerun()
        with b2:
            if st.button("⏮️ -1s Start", key="nudge_s_minus_1", use_container_width=True):
                new_s = max(0.0, sel_start - 1.0)
                st.session_state["clip_trim_slider"] = (new_s, sel_end)
                st.rerun()
        with b3:
            if st.button("⏭️ +1s Start", key="nudge_s_plus_1", use_container_width=True):
                new_s = min(sel_end - min_clip_req, sel_start + 1.0)
                st.session_state["clip_trim_slider"] = (new_s, sel_end)
                st.rerun()

    with st_col2:
        st.markdown("**End Point Adjuster:**")
        b4, b5, b6 = st.columns(3)
        with b4:
            if st.button("⏮️ -1s End", key="nudge_e_minus_1", use_container_width=True):
                new_e = max(sel_start + min_clip_req, sel_end - 1.0)
                st.session_state["clip_trim_slider"] = (sel_start, new_e)
                st.rerun()
        with b5:
            if st.button("⏭️ +1s End", key="nudge_e_plus_1", use_container_width=True):
                new_e = min(max_sec, sel_end + 1.0)
                st.session_state["clip_trim_slider"] = (sel_start, new_e)
                st.rerun()
        with b6:
            if st.button("⏩ +10s End", key="nudge_e_plus_10", use_container_width=True):
                new_e = min(max_sec, sel_end + 10.0)
                st.session_state["clip_trim_slider"] = (sel_start, new_e)
                st.rerun()

    # 5. Optional Direct Numeric Form (Isolated in a clean form, cannot desync slider)
    with st.expander("⌨️ Or Enter Exact Custom Seconds Manually", expanded=False):
        with st.form("manual_timestamp_form"):
            f_col1, f_col2, f_col3 = st.columns([1, 1, 1])
            with f_col1:
                man_start = st.number_input("Exact Start (Seconds)", min_value=0.0, max_value=max(0.0, max_sec - min_clip_req), value=float(sel_start), step=0.5, format="%.1f")
            with f_col2:
                man_end = st.number_input("Exact End (Seconds)", min_value=min(max_sec, man_start + min_clip_req), max_value=max_sec, value=float(sel_end), step=0.5, format="%.1f")
            with f_col3:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                apply_man = st.form_submit_button("✅ Apply to Slider", use_container_width=True)
            if apply_man:
                if (man_end - man_start) < min_clip_req and max_sec > min_clip_req:
                    man_end = min(max_sec, man_start + min_clip_req)
                st.session_state["clip_trim_slider"] = (man_start, man_end)
                st.rerun()

    st.markdown("")
    if st.button("⚡ Cut & Render Custom High-Quality Clip (With Audio)", type="primary", use_container_width=True):
        if duration < min_clip_req and max_sec > min_clip_req:
            st.error(f"⚠️ Minimum clip duration must be at least 70.0s (currently {duration:.1f}s). Please adjust your selection.")
            return

        custom_clip_name = f"custom_clip_{int(sel_start)}s_to_{int(sel_end)}s.mp4"
        custom_clip_path = output_dir / custom_clip_name
        with st.spinner(f"✂️ Cutting clip from {seconds_to_timecode(sel_start)} to {seconds_to_timecode(sel_end)} ({duration:.1f}s, Audio Preserved)..."):
            try:
                success = extract_single_custom_clip(
                    video_path=video_path,
                    start_seconds=sel_start,
                    end_seconds=sel_end,
                    output_path=custom_clip_path,
                )
                if success and custom_clip_path.exists() and custom_clip_path.stat().st_size > 0:
                    st.session_state["last_custom_clip"] = str(custom_clip_path)
                    st.session_state["last_custom_clip_meta"] = {
                        "name": custom_clip_name,
                        "duration": duration,
                        "start_tc": seconds_to_timecode(sel_start),
                        "end_tc": seconds_to_timecode(sel_end),
                        "size_mb": round(custom_clip_path.stat().st_size / (1024 * 1024), 2),
                    }
                    st.success(f"✅ Custom clip ready! ({seconds_to_timecode(sel_start)} ➔ {seconds_to_timecode(sel_end)}, {duration:.1f}s, Sound Preserved)")
                else:
                    st.error("⚠️ Clip extraction failed. Please try a slightly different time range.")
            except Exception as clip_err:
                st.error(f"⚠️ Custom clip error: {clip_err}")

    # Show the last successfully rendered custom clip
    last_clip_key = st.session_state.get("last_custom_clip")
    if last_clip_key and Path(last_clip_key).exists():
        c_path = Path(last_clip_key)
        clip_meta = st.session_state.get("last_custom_clip_meta", {})
        clip_size = clip_meta.get("size_mb", round(c_path.stat().st_size / (1024 * 1024), 2))
        clip_dur = clip_meta.get("duration", duration)

        st.markdown("##### 🎬 Custom Clip Monitor (Lossless Sound)")
        render_html(
            f"""<div style="display: flex; gap: 10px; margin-bottom: 8px; flex-wrap: wrap;">
                <span class="badge-pill badge-standard">⚡ Duration: {clip_dur:.1f}s</span>
                <span class="badge-pill badge-extended">💾 Size: {clip_size} MB</span>
                <span class="audio-sound-active-badge">🔊 Sound Preserved</span>
            </div>"""
        )
        try:
            st.video(str(c_path))
        except Exception:
            st.caption("⚠️ Preview unavailable — download the clip to play it.")
        try:
            with open(c_path, "rb") as cf:
                st.download_button(
                    label=f"⬇️ Download Custom Clip ({clip_size} MB MP4 with Sound)",
                    data=cf.read(),
                    file_name=c_path.name,
                    mime="video/mp4",
                    key="dl_custom_trim_clip",
                    use_container_width=True,
                )
        except OSError as cf_err:
            st.caption(f"⚠️ Download unavailable: {cf_err}")


def render_interval_clips_gallery(
    interval_clips: List[dict],
    zip_path: Optional[Path] = None,
    title: str = "Fixed-Duration Sliced Clips",
) -> None:
    """Renders a gallery of fixed-duration interval video clips with download buttons and audio verification."""
    if not interval_clips:
        st.info("ℹ️ No interval clips available.")
        return

    valid_clips = [c for c in interval_clips if Path(c.get("clip_path", "")).exists()]
    if not valid_clips:
        st.warning("⚠️ No valid clip files found on disk.")
        return

    render_html(
        f"""<div class="cutting-machine-banner">
            <div class="cutter-title">
                <span class="scissor-icon-animated">🎬</span>
                <span>{title} • {len(valid_clips)} Clips Ready</span>
                <span class="audio-sound-active-badge">🔊 100% Sound Intact</span>
            </div>
            <div class="cutter-subhead">
                Uniformly partitioned video segments with lossless audio and frame-accurate cutting. Ready for YouTube Shorts, Instagram Reels, and TikTok.
            </div>
        </div>"""
    )

    # Download All ZIP button
    if zip_path and Path(zip_path).exists():
        zip_size_mb = round(Path(zip_path).stat().st_size / (1024 * 1024), 2)
        try:
            with open(zip_path, "rb") as zf:
                st.download_button(
                    label=f"📦 Download All {len(valid_clips)} Clips in One ZIP ({zip_size_mb} MB Archive)",
                    data=zf.read(),
                    file_name=Path(zip_path).name,
                    mime="application/zip",
                    key=f"dl_interval_zip_{len(valid_clips)}",
                    use_container_width=True,
                )
        except Exception as ze:
            st.caption(f"⚠️ ZIP download unavailable: {ze}")

    # 2-column responsive layout
    cols = st.columns(2)
    for idx, c in enumerate(valid_clips):
        col = cols[idx % 2]
        with col:
            c_path = Path(c["clip_path"])
            c_num = c.get("clip_index", idx + 1)
            c_dur = c.get("duration_sec", 0.0)
            c_start_tc = c.get("start_timecode", "00:00:00.000")
            c_end_tc = c.get("end_timecode", "00:00:00.000")
            c_size = c.get("size_mb", round(c_path.stat().st_size / (1024 * 1024), 2))

            render_html(
                f"""<div class="film-clip-card">
                    <div class="filmstrip-sprockets"></div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin: 8px 0; flex-wrap: wrap; gap: 6px;">
                        <span class="clip-badge-cut">✂️ CLIP #{c_num:02d} ({c_dur:.1f}s)</span>
                        <span class="audio-sound-active-badge" style="font-size: 0.68rem; padding: 2px 8px;">🔊 SOUND PRESERVED</span>
                        <span style="font-family: monospace; font-size: 0.8rem; color: #cbd5e1;">
                            {c_start_tc} ➔ {c_end_tc}
                        </span>
                    </div>
                </div>"""
            )
            try:
                st.video(str(c_path))
            except Exception as ve:
                st.warning(f"⚠️ Cannot preview Clip #{c_num}: {ve}")

            render_html('<div class="filmstrip-sprockets"></div>')
            try:
                with open(c_path, "rb") as cf:
                    st.download_button(
                        label=f"⬇️ Download Clip #{c_num:02d} ({c_dur:.1f}s • {c_size} MB MP4)",
                        data=cf.read(),
                        file_name=c.get("clip_filename") or c_path.name,
                        mime="video/mp4",
                        key=f"dl_interval_clip_{c_num}_{idx}",
                        use_container_width=True,
                    )
            except Exception as oe:
                st.caption(f"⚠️ Download unavailable: {oe}")


def render_fixed_interval_cutter(video_path: Path, metadata: VideoMetadata, output_dir: Path) -> None:
    """Renders interactive custom duration and timing cutter (e.g. 0 to 350s split into 60s clips)."""
    video_path = Path(video_path)
    if not video_path.exists():
        st.warning("⚠️ Source video file not accessible.")
        return

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    max_sec = max(1.0, float(metadata.duration_seconds))

    render_html(
        """<div class="precision-trimmer-card">
            <div class="trimmer-title">
                <span>✂️ Fixed-Duration Clip Slicer (Shorts / Reels / Chunks)</span>
                <span class="audio-sound-active-badge">🔊 100% Sound Preserved</span>
            </div>
            <div style="font-size: 0.86rem; color: #94a3b8; margin-bottom: 12px;">
                Configure your exact start time, end time, and clip duration (e.g., set duration <b>0 to 350 sec</b> and make <b>60 sec clips</b>). 
                Each clip is extracted with frame accuracy and 100% lossless original audio.
            </div>
        </div>"""
    )

    # Initialize session state for interval cutter
    if "interval_win_start" not in st.session_state:
        st.session_state["interval_win_start"] = 0.0
    if "interval_win_end" not in st.session_state:
        st.session_state["interval_win_end"] = min(350.0, max_sec)
    if "interval_chunk_len" not in st.session_state:
        st.session_state["interval_chunk_len"] = 60.0

    # Ensure valid bounds
    st.session_state["interval_win_start"] = max(0.0, min(float(st.session_state["interval_win_start"]), max_sec - 0.5))
    st.session_state["interval_win_end"] = max(float(st.session_state["interval_win_start"]) + 0.5, min(float(st.session_state["interval_win_end"]), max_sec))
    st.session_state["interval_chunk_len"] = max(5.0, min(float(st.session_state["interval_chunk_len"]), max_sec))

    # 1. Quick Presets
    st.markdown("###### ⚡ Quick Setup Presets")
    p1, p2, p3, p4, p5 = st.columns(5)
    with p1:
        if st.button("🔥 0-350s (60s Clips)", key="btn_int_preset_350", use_container_width=True):
            st.session_state["interval_win_start"] = 0.0
            st.session_state["interval_win_end"] = min(350.0, max_sec)
            st.session_state["interval_chunk_len"] = 60.0
            st.rerun()
    with p2:
        if st.button("📱 0-180s (60s Clips)", key="btn_int_preset_180", use_container_width=True):
            st.session_state["interval_win_start"] = 0.0
            st.session_state["interval_win_end"] = min(180.0, max_sec)
            st.session_state["interval_chunk_len"] = 60.0
            st.rerun()
    with p3:
        if st.button("⚡ 0-300s (60s Clips)", key="btn_int_preset_300", use_container_width=True):
            st.session_state["interval_win_start"] = 0.0
            st.session_state["interval_win_end"] = min(300.0, max_sec)
            st.session_state["interval_chunk_len"] = 60.0
            st.rerun()
    with p4:
        if st.button("🌐 Full Video (60s Clips)", key="btn_int_preset_all_60", use_container_width=True):
            st.session_state["interval_win_start"] = 0.0
            st.session_state["interval_win_end"] = max_sec
            st.session_state["interval_chunk_len"] = 60.0
            st.rerun()
    with p5:
        if st.button("⏱️ Full Video (70s Clips)", key="btn_int_preset_all_70", use_container_width=True):
            st.session_state["interval_win_start"] = 0.0
            st.session_state["interval_win_end"] = max_sec
            st.session_state["interval_chunk_len"] = 70.0
            st.rerun()

    # 2. Timing and Duration Inputs
    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1:
        win_start = st.number_input(
            "Start Time (Seconds)",
            min_value=0.0,
            max_value=max(0.0, max_sec - 1.0),
            value=float(st.session_state["interval_win_start"]),
            step=5.0,
            format="%.1f",
            key="input_int_win_start",
            help="Beginning timestamp of the window to slice (e.g. 0.0s).",
        )
    with col_w2:
        win_end = st.number_input(
            "End Time (Seconds)",
            min_value=min(max_sec, win_start + 1.0),
            max_value=max_sec,
            value=float(st.session_state["interval_win_end"]),
            step=5.0,
            format="%.1f",
            key="input_int_win_end",
            help="Ending timestamp of the window to slice (e.g. 350.0s).",
        )
    with col_w3:
        chunk_len = st.number_input(
            "Clip Duration (Seconds)",
            min_value=5.0,
            max_value=max(5.0, win_end - win_start),
            value=float(st.session_state["interval_chunk_len"]),
            step=5.0,
            format="%.1f",
            key="input_int_chunk_len",
            help="Duration of each slice (e.g. 60.0s for Shorts/TikTok).",
        )

    # Keep session state synced
    st.session_state["interval_win_start"] = win_start
    st.session_state["interval_win_end"] = win_end
    st.session_state["interval_chunk_len"] = chunk_len

    # 3. Calculate Planned Intervals
    total_window_dur = max(0.1, win_end - win_start)
    intervals = []
    curr = win_start
    c_idx = 1
    while curr < win_end:
        nxt = min(win_end, curr + chunk_len)
        if (nxt - curr) >= 0.5:
            intervals.append((c_idx, curr, nxt, nxt - curr))
            c_idx += 1
        curr = nxt

    num_clips = len(intervals)

    # 4. Interactive Live Breakdown Card
    pills_html = "".join([
        f'<span class="badge-pill badge-standard" style="margin: 3px; font-size: 0.76rem;">'
        f'#{i:02d} {seconds_to_timecode(s)}➔{seconds_to_timecode(e)} ({d:.1f}s)</span>'
        for i, s, e, d in intervals[:12]
    ])
    if num_clips > 12:
        pills_html += f'<span class="badge-pill badge-extended" style="margin: 3px; font-size: 0.76rem;">...and {num_clips - 12} more clips</span>'

    render_html(
        f"""<div style="background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(14, 165, 233, 0.35); border-radius: 14px; padding: 16px 20px; margin: 12px 0 16px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
                <span style="font-size: 0.82rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Planned Slicing Breakdown</span>
                <span class="badge-pill badge-extended" style="font-size: 0.74rem;">{num_clips} Total Clips</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 10px;">
                <div>
                    <span style="font-size: 0.75rem; color: #64748b; display: block;">TIME WINDOW</span>
                    <span style="font-size: 1.15rem; font-weight: 800; color: #38bdf8; font-family: monospace;">{seconds_to_timecode(win_start)} ➔ {seconds_to_timecode(win_end)}</span>
                    <span style="font-size: 0.8rem; color: #94a3b8; margin-left: 6px;">({win_start:.1f}s to {win_end:.1f}s)</span>
                </div>
                <div>
                    <span style="font-size: 0.75rem; color: #64748b; display: block;">CHUNK DURATION</span>
                    <span style="font-size: 1.15rem; font-weight: 800; color: #34d399; font-family: monospace;">{chunk_len:.1f}s</span>
                    <span style="font-size: 0.8rem; color: #94a3b8; margin-left: 6px;">(Per clip target)</span>
                </div>
                <div>
                    <span style="font-size: 0.75rem; color: #64748b; display: block;">TOTAL SPAN</span>
                    <span style="font-size: 1.15rem; font-weight: 800; color: #f59e0b; font-family: monospace;">{total_window_dur:.1f}s</span>
                    <span style="font-size: 0.8rem; color: #94a3b8; margin-left: 6px;">({(total_window_dur / max_sec) * 100:.1f}% of video)</span>
                </div>
            </div>
            <div style="margin-top: 10px;">
                <span style="font-size: 0.75rem; color: #64748b; display: block; margin-bottom: 4px;">CALCULATED SLICE INTERVALS:</span>
                <div style="display: flex; flex-wrap: wrap; gap: 4px;">{pills_html}</div>
            </div>
        </div>"""
    )

    # 5. Execute Slicing Button
    st.markdown("")
    btn_label = f"⚡ Slice Video into {num_clips} Clips of {chunk_len:.0f}s Now (With 100% Audio)"
    if st.button(btn_label, type="primary", use_container_width=True, key="btn_slice_fixed_intervals"):
        if num_clips == 0:
            st.error("⚠️ Invalid time range. Please specify a window longer than 1 second.")
            return

        prog_bar = st.progress(0.0)
        status_box = st.empty()

        def on_slice_progress(ratio: float, msg: str) -> None:
            prog_bar.progress(ratio)
            status_box.text(msg)

        try:
            results = extract_fixed_interval_clips(
                video_path=video_path,
                start_seconds=win_start,
                end_seconds=win_end,
                clip_duration_seconds=chunk_len,
                output_dir=output_dir,
                progress_callback=on_slice_progress,
            )

            if results:
                # Package into zip
                zip_name = f"interval_clips_{int(win_start)}s_to_{int(win_end)}s_{int(chunk_len)}s_chunks.zip"
                zip_path = output_dir.parent / zip_name
                try:
                    create_interval_clips_zip(results, zip_path)
                except Exception as ze:
                    zip_path = None

                st.session_state["generated_interval_clips"] = results
                st.session_state["generated_interval_zip"] = zip_path
                prog_bar.empty()
                status_box.empty()
                st.success(f"🎉 Successfully sliced {len(results)} clips! (Audio preserved, frame-accurate).")
                st.rerun()
            else:
                prog_bar.empty()
                status_box.empty()
                st.error("⚠️ No clips could be generated. Please verify the time range.")
        except Exception as ex:
            prog_bar.empty()
            status_box.empty()
            st.error(f"⚠️ Slicing error: {ex}")

    # 6. Display Generated Clips Gallery
    gen_clips = st.session_state.get("generated_interval_clips")
    gen_zip = st.session_state.get("generated_interval_zip")
    if gen_clips:
        st.markdown("---")
        render_interval_clips_gallery(
            interval_clips=gen_clips,
            zip_path=gen_zip,
            title=f"🎬 Sliced Clips ({len(gen_clips)} Clips • {win_start:.0f}s to {win_end:.0f}s)",
        )


def render_scene_clips_gallery(scenes: List[SceneInfo]) -> None:
    """Renders playable video clips for each detected scene with physical film cutting animations."""
    valid_scenes = [s for s in scenes if s.clip_path and Path(s.clip_path).exists()]
    if not valid_scenes:
        st.info("ℹ️ No video clips generated. Enable 'Generate Scene Video Clips' in the control deck to create video cuts.")
        return

    render_html(
        f"""<div class="cutting-machine-banner">
            <div class="cutter-title">
                <span class="scissor-icon-animated">✂️</span>
                <span>Physical Scene Cutting Room • {len(valid_scenes)} Frame-Accurate Slices</span>
                <span class="audio-sound-active-badge">🔊 Audio Intact</span>
            </div>
            <div class="cutter-subhead">
                Every video cut below was extracted losslessly at detected camera cut boundaries with complete audio soundtrack preservation.
                Equipped with filmstrip sprocket spools, exact start-end timecode stamps, and direct MP4 export.
            </div>
        </div>"""
    )

    cols = st.columns(2)
    for idx, s in enumerate(valid_scenes):
        col = cols[idx % 2]
        with col:
            render_html(
                f"""<div class="film-clip-card">
                    <div class="filmstrip-sprockets"></div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin: 8px 0; flex-wrap: wrap; gap: 6px;">
                        <span class="clip-badge-cut">✂️ SCENE CUT #{s.scene_number:02d}</span>
                        <span class="audio-sound-active-badge" style="font-size: 0.68rem; padding: 2px 8px;">🔊 SOUND PRESERVED</span>
                        <span style="font-family: monospace; font-size: 0.8rem; color: #cbd5e1;">
                            {s.start_timecode} ➔ {s.end_timecode} ({s.duration_seconds:.2f}s)
                        </span>
                    </div>
                </div>"""
            )
            clip_p = Path(s.clip_path)
            try:
                st.video(str(clip_p))
            except Exception as ve:
                st.warning(f"⚠️ Cannot preview Scene #{s.scene_number}: {ve}")
            render_html('<div class="filmstrip-sprockets"></div>')
            # Safe file read with existence check
            if clip_p.exists() and clip_p.stat().st_size > 0:
                try:
                    with open(clip_p, "rb") as vf:
                        clip_data = vf.read()
                    st.download_button(
                        label=f"⬇️ Download Scene #{s.scene_number:02d} Clip (MP4 with Sound)",
                        data=clip_data,
                        file_name=s.clip_filename or f"scene_{s.scene_number:03d}.mp4",
                        mime="video/mp4",
                        key=f"dl_clip_{s.scene_number}_{idx}",
                        use_container_width=True,
                    )
                except OSError as oe:
                    st.caption(f"⚠️ Clip file read error for Scene #{s.scene_number}: {oe}")
            else:
                st.caption(f"⚠️ Clip file missing or empty for Scene #{s.scene_number}")


def render_ai_copilot_chatbot(
    metadata: VideoMetadata,
    scenes: List[SceneInfo],
    summary: VideoSummaryReport,
    narrative: Optional[FullVideoNarrative],
) -> None:
    """Renders interactive AI Video Copilot chatbot interface."""
    render_html(
        f"""<div class="copilot-card">
            <div class="copilot-banner">
                <div class="copilot-agent-badge">
                    <div class="copilot-avatar">🤖</div>
                    <div class="copilot-info">
                        <h4>ClipMind AI Video Copilot</h4>
                        <span>● Neural Context Ingested ({metadata.duration_formatted} • {len(scenes)} Cuts)</span>
                    </div>
                </div>
                <div style="display: flex; gap: 6px;">
                    <span class="badge-pill badge-standard">⚡ Live Model Active</span>
                </div>
            </div>
            <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 12px;">
                Ask any question about scenes, pacing, viral hooks, color aesthetics, motion scores, or audio design:
            </div>
        </div>"""
    )

    # Initialize chat history in session state
    if "copilot_history" not in st.session_state:
        st.session_state["copilot_history"] = [
            {
                "role": "assistant",
                "content": (
                    f"👋 Hi! I have analyzed **{metadata.filename}** ({metadata.duration_formatted}, {len(scenes)} scenes). "
                    "I can help you craft TikTok/Reels hooks, evaluate motion energy, break down color aesthetics, or suggest music BPM. What would you like to explore?"
                ),
            }
        ]

    # Quick Prompt Chips (Click to ask instantly)
    st.markdown("**⚡ Quick Prompts**:")
    p_col1, p_col2, p_col3 = st.columns(3)
    p_col4, p_col5, p_col6 = st.columns(3)

    chosen_prompt = None
    with p_col1:
        if st.button("📱 Suggest TikTok/Reels Hook", key="chip_tiktok", use_container_width=True):
            chosen_prompt = "How can I turn this into a viral TikTok or Reel hook?"
    with p_col2:
        if st.button("⚡ Highest Motion Energy Cut", key="chip_motion", use_container_width=True):
            chosen_prompt = "Which scene cut has the highest motion energy and action?"
    with p_col3:
        if st.button("🎨 Analyze Color & Lighting", key="chip_color", use_container_width=True):
            chosen_prompt = "Analyze the visual color palette and lighting aesthetic."
    with p_col4:
        if st.button("🎵 Recommend Music BPM", key="chip_music", use_container_width=True):
            chosen_prompt = "What background music tempo and BPM matches this video's pacing?"
    with p_col5:
        if st.button("📋 Full Cut Breakdown", key="chip_breakdown", use_container_width=True):
            chosen_prompt = "Give me a timestamp breakdown of all scene cuts."
    with p_col6:
        if st.button("⚙️ Technical Video Specs", key="chip_specs", use_container_width=True):
            chosen_prompt = "What are the technical specs and video metrics?"

    # Chat Input
    user_input = st.chat_input("Ask ClipMind AI anything about this video...")
    active_prompt = chosen_prompt or user_input

    if active_prompt:
        st.session_state["copilot_history"].append({"role": "user", "content": active_prompt})
        answer = answer_video_query(active_prompt, metadata, scenes, summary, narrative)
        st.session_state["copilot_history"].append({"role": "assistant", "content": answer})

    # Render Conversation History
    for msg in st.session_state["copilot_history"]:
        if msg["role"] == "user":
            render_html(f'<div class="chat-bubble-user">👤 <b>You</b>: {msg["content"]}</div>')
        else:
            render_html(f'<div class="chat-bubble-ai">🤖 <b>ClipMind Copilot</b>:<br><br>{msg["content"]}</div>')
