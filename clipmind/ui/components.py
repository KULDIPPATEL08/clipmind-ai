"""Reusable UI presentation components for Streamlit interface."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import streamlit as st

from clipmind.analysis.summary import VideoSummaryReport
from clipmind.video.detector import SceneInfo
from clipmind.video.keyframe import Keyframe
from clipmind.video.metadata import VideoMetadata


def render_brand_header() -> None:
    """Renders the top branding header."""
    st.markdown(
        """
        <div class="clipmind-brand-header">
            <div class="clipmind-logo-badge">CM</div>
            <div class="clipmind-header-text">
                <h1>ClipMind AI</h1>
                <p>Scene-Aware Video Summarization and Keyframe Extraction Platform</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
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

    st.markdown(
        f'<div class="timeline-track">{"".join(segments_html)}</div>',
        unsafe_allow_html=True,
    )
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

    st.markdown(
        f"""
        <div style="display: flex; gap: 12px; margin-top: 8px;">
            <span class="badge-rapid">⚡ Rapid Cuts (&lt;2s): {summary.rapid_scenes_count} ({summary.rapid_scenes_pct}%)</span>
            <span class="badge-standard">🎬 Standard (2-8s): {summary.standard_scenes_count} ({summary.standard_scenes_pct}%)</span>
            <span class="badge-extended">🌿 Extended (&gt;8s): {summary.extended_scenes_count} ({summary.extended_scenes_pct}%)</span>
        </div>
        """,
        unsafe_allow_html=True,
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
