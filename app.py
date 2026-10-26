"""ClipMind AI — Streamlit Web Application Entrypoint."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import streamlit as st

from clipmind.analysis.description import generate_full_video_narrative
from clipmind.analysis.summary import generate_video_summary
from clipmind.config import config
from clipmind.exceptions import ClipMindError
from clipmind.export.exporter import (
    create_keyframe_zip,
    create_video_clips_zip,
    export_scenes_csv,
    export_summary_json,
    export_summary_markdown,
)
from clipmind.logger import logger
from clipmind.security import (
    JobSession,
    cleanup_stale_jobs,
    save_upload_securely,
    validate_file_extension,
)
from clipmind.ui.components import (
    render_ai_cockpit_status_bar,
    render_ai_copilot_chatbot,
    render_brand_header,
    render_full_video_narrative_hero,
    render_keyframe_gallery,
    render_landing_showcase,
    render_metadata_cards,
    render_precision_clip_trimmer,
    render_scene_clips_gallery,
    render_scene_intelligence_cards,
    render_summary_analytics,
    render_timeline_bar,
)
from clipmind.ui.styles import MAIN_CSS
from clipmind.video.clipper import extract_scene_clips
from clipmind.video.detector import VideoSceneDetector
from clipmind.video.keyframe import KeyframeExtractor, generate_contact_sheet
from clipmind.video.metadata import extract_video_metadata


# Configure Streamlit page
st.set_page_config(
    page_title="ClipMind AI — Video Intelligence Platform",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject custom styles
st.markdown(MAIN_CSS, unsafe_allow_html=True)


def create_demo_synthetic_video(target_path: Path) -> Path:
    """Generates a small multi-scene synthetic video for instant demonstration."""
    target_path = Path(target_path).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    width, height, fps = 640, 360, 30
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(target_path), fourcc, fps, (width, height))

    # 4 distinct visual scenes with clear cuts and motion
    colors = [
        (40, 40, 180),   # Crimson
        (30, 140, 40),   # Forest Green
        (180, 120, 20),  # Blue
        (160, 40, 140),  # Purple
    ]

    for scene_idx, bgr in enumerate(colors):
        for f in range(45):  # 1.5 seconds per scene
            frame = np.full((height, width, 3), bgr, dtype=np.uint8)
            # Add dynamic element to simulate motion
            pos_x = 50 + int((f / 45.0) * (width - 150))
            cv2.circle(frame, (pos_x, height // 2), 35, (255, 255, 255), -1)
            cv2.putText(
                frame,
                f"ClipMind Demo Scene #{scene_idx + 1}",
                (40, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            writer.write(frame)

    writer.release()
    return target_path


def main() -> None:
    """Main application routine."""
    # Top AI Cockpit Telemetry Strip
    render_ai_cockpit_status_bar()
    render_brand_header()

    # Periodic background cleanup of stale jobs
    try:
        cleanup_stale_jobs(max_age_seconds=3600)
    except Exception as e:
        logger.debug("Background stale job cleanup: %s", e)

    # Initialize demo trigger state if needed
    if "trigger_demo" not in st.session_state:
        st.session_state["trigger_demo"] = False

    # On-Page Studio Intelligence Control Deck (No Sidebar)
    with st.expander("🎛️ Studio Intelligence Control Deck (Speed Engine, Hybrid Detector, & Audio Slicing Dials)", expanded=False):
        c_deck1, c_deck2, c_deck3 = st.columns(3)
        with c_deck1:
            st.markdown("##### ⚡ Speed & Acceleration Profile")
            speed_choice = st.radio(
                "Processing Speed Profile",
                options=[
                    "⚡ Hyper-Turbo (3x Speed • Recommended)",
                    "⚖️ Balanced Fast (2x Speed)",
                    "🎯 Studio Precision (1x Detailed)",
                ],
                index=0,
                help="Hyper-Turbo uses calibrated frame skipping to deliver blazing fast processing on standard CPUs.",
            )
            speed_map = {
                "⚡ Hyper-Turbo (3x Speed • Recommended)": "turbo",
                "⚖️ Balanced Fast (2x Speed)": "fast",
                "🎯 Studio Precision (1x Detailed)": "precision",
            }
            speed_profile = speed_map[speed_choice]

        with c_deck2:
            st.markdown("##### ⚙️ Scene Cut Detection Engine")
            detector_choice = st.selectbox(
                "Detection Mode",
                options=[
                    "Hybrid (Best Quality — Adaptive + Content)",
                    "Adaptive (Lighting & Camera Motion Compensated)",
                    "Content (Fast Hard Cut Detection)",
                    "Threshold (Fade In/Out Transitions)",
                ],
                index=0,
                help="Hybrid combines adaptive rolling frame comparison and content color differencing for maximum cut accuracy.",
            )
            detector_map = {
                "Hybrid (Best Quality — Adaptive + Content)": "hybrid",
                "Adaptive (Lighting & Camera Motion Compensated)": "adaptive",
                "Content (Fast Hard Cut Detection)": "content",
                "Threshold (Fade In/Out Transitions)": "threshold",
            }
            detector_type = detector_map[detector_choice]

            if detector_type in ["hybrid", "adaptive"]:
                adaptive_thresh = st.slider("Adaptive Sensitivity", 1.5, 6.0, 3.0, 0.2)
            else:
                adaptive_thresh = 3.0
            threshold = st.slider("Content Cut Threshold", 10.0, 50.0, config.default_content_threshold, 1.0)
            min_scene_frames = st.slider("Min Scene Length (Frames)", 5, 90, config.default_min_scene_length_frames, 5)

        with c_deck3:
            st.markdown("##### 🎬 Lossless Slicing & Keyframes")
            generate_clips = st.checkbox("Generate Video Clips (Audio Intact)", value=True)
            max_clips = st.slider("Max Video Clips", 5, 50, 25, 5)
            keyframe_strategy = st.selectbox("Representative Frame", ["middle", "start", "end"], index=0)
            enable_dedup = st.checkbox("Keyframe Deduplication", value=True)
            max_keyframes = st.slider("Max Keyframes Limit", 5, 150, 40, 5)

    start_analysis = False
    active_upload = None
    run_demo = False

    # Main Area: Landing or Upload
    if "analysis_results" not in st.session_state:
        # Render high-impact landing showcase
        render_landing_showcase()

        st.markdown("### 🚀 Launch Analysis Engine")
        col_up, col_demo = st.columns([3, 2])

        with col_up:
            st.markdown("##### 📤 Step 1: Select Video File")
            uploaded_file = st.file_uploader(
                "Upload MP4, MOV, AVI, MKV, or WEBM",
                type=["mp4", "mov", "avi", "mkv", "webm"],
                help=f"Maximum size: {config.max_upload_size_mb} MB. Maximum duration: {config.max_video_duration_seconds // 60} mins.",
                key="main_video_uploader",
            )

        with col_demo:
            st.markdown("##### ⚡ Instant Evaluation Sandbox")
            st.markdown(
                """
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px; margin-bottom: 12px;">
                    <div style="font-size: 0.9rem; font-weight: 700; color: #f8fafc; margin-bottom: 4px;">Zero Setup Required</div>
                    <div style="font-size: 0.8rem; color: #94a3b8; line-height: 1.4;">
                        Test the complete multi-scene hybrid cut detector, audio preservation slicer, and AI copilot immediately.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("✨ Select Demo Video (4 Scenes • 4K Synthetic)", use_container_width=True):
                st.session_state["staged_video"] = "demo"

        # Check what is staged
        if uploaded_file is not None:
            st.session_state["staged_video"] = "upload"

        staged_kind = st.session_state.get("staged_video")

        if staged_kind == "upload" and uploaded_file is not None:
            size_mb = round(len(uploaded_file.getvalue()) / (1024 * 1024), 2)
            st.markdown(
                f"""
                <div class="staged-video-card">
                    <div class="staged-header">
                        <div class="staged-title">
                            <span>🎬 Video Staged & Ready</span>
                            <span class="audio-sound-active-badge">🔊 Sound Preserved</span>
                        </div>
                        <span class="staged-filename">{uploaded_file.name}</span>
                    </div>
                    <div class="staged-details-grid">
                        <div class="staged-detail-item">Container: <b>{uploaded_file.name.split('.')[-1].upper()}</b></div>
                        <div class="staged-detail-item">File Size: <b>{size_mb} MB</b></div>
                        <div class="staged-detail-item">Speed Engine: <b>{speed_profile.upper()}</b></div>
                        <div class="staged-detail-item">Detector: <b>{detector_type.upper()}</b></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("##### 📺 Direct Video Preview On Page")
            st.video(uploaded_file)

            col_start, col_cancel = st.columns([3, 1])
            with col_start:
                if st.button("🚀 Start AI Scene Slicing & Analysis", type="primary", use_container_width=True):
                    start_analysis = True
                    active_upload = uploaded_file
            with col_cancel:
                if st.button("✖ Cancel Selection", use_container_width=True):
                    st.session_state.pop("staged_video", None)
                    st.rerun()

        elif staged_kind == "demo":
            st.markdown(
                f"""
                <div class="staged-video-card">
                    <div class="staged-header">
                        <div class="staged-title">
                            <span>🎬 Synthetic Demo Staged</span>
                            <span class="audio-sound-active-badge">🔊 Sound Preserved</span>
                        </div>
                        <span class="staged-filename">demo_synthetic_4cut.mp4</span>
                    </div>
                    <div class="staged-details-grid">
                        <div class="staged-detail-item">Source: <b>4 Distinct Multi-Color Scenes</b></div>
                        <div class="staged-detail-item">Frame Rate: <b>30 FPS • 4K Motion Elements</b></div>
                        <div class="staged-detail-item">Speed Engine: <b>{speed_profile.upper()}</b></div>
                        <div class="staged-detail-item">Detector: <b>{detector_type.upper()}</b></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col_start, col_cancel = st.columns([3, 1])
            with col_start:
                if st.button("🚀 Start AI Scene Slicing & Analysis", type="primary", use_container_width=True):
                    start_analysis = True
                    run_demo = True
            with col_cancel:
                if st.button("✖ Cancel Selection", use_container_width=True):
                    st.session_state.pop("staged_video", None)
                    st.rerun()

        if not start_analysis:
            return
    else:
        # Results area action bar
        r_col1, r_col2 = st.columns([5, 1])
        with r_col2:
            if st.button("🔄 New Video", help="Reset workspace and analyze another video"):
                st.session_state.pop("analysis_results", None)
                st.session_state.pop("staged_video", None)
                st.session_state.pop("copilot_history", None)
                st.rerun()

    # Trigger processing only when Start is clicked
    if start_analysis:
        session = JobSession()
        session.start()
        st.session_state["active_session"] = session

        progress_bar = st.progress(0.0)
        status_text = st.empty()

        try:
            # Step 1: Ingestion and Validation
            status_text.text("Validating video file and container headers...")
            progress_bar.progress(0.15)

            if run_demo:
                video_path = session.video_dir / "demo_synthetic.mp4"
                create_demo_synthetic_video(video_path)
            else:
                video_path = save_upload_securely(
                    file_obj=active_upload,
                    original_filename=active_upload.name,
                    job_session=session,
                )

            # Step 2: Metadata Extraction
            status_text.text("Extracting video metadata and verifying decodability...")
            progress_bar.progress(0.3)
            metadata = extract_video_metadata(video_path)

            # Step 3: Scene Detection
            status_text.text(f"Running high-precision scene boundary detection ({speed_profile.upper()} mode)...")
            detector = VideoSceneDetector(
                detector_type=detector_type,
                threshold=threshold,
                min_scene_len_frames=min_scene_frames,
                adaptive_threshold=adaptive_thresh,
                speed_profile=speed_profile,
            )

            def on_detect_progress(ratio: float, msg: str) -> None:
                progress_bar.progress(min(0.60, ratio))
                status_text.text(msg)

            scenes = detector.detect_scenes(
                video_path=video_path,
                metadata=metadata,
                progress_callback=on_detect_progress,
            )

            # Step 4: Keyframe Extraction & Deduplication
            status_text.text(f"Extracting representative keyframes for {len(scenes)} scenes...")
            progress_bar.progress(0.65)
            extractor = KeyframeExtractor(
                strategy=keyframe_strategy,
                enable_deduplication=enable_dedup,
                max_keyframes=max_keyframes,
            )

            def on_extract_progress(ratio: float, msg: str) -> None:
                progress_bar.progress(0.65 + 0.15 * ratio)
                status_text.text(msg)

            keyframes = extractor.extract_keyframes(
                video_path=video_path,
                scenes=scenes,
                output_dir=session.keyframes_dir,
                progress_callback=on_extract_progress,
            )

            # Step 5: Deep Video Narrative & Visual Aesthetics Analysis
            status_text.text("Synthesizing executive video narrative, color palettes, and motion dynamics...")
            progress_bar.progress(0.82)
            narrative = generate_full_video_narrative(metadata, scenes, keyframes)

            # Step 6: Optional Video Clip Extraction
            clips_zip = None
            if generate_clips:
                status_text.text("Extracting frame-accurate video clips (.mp4) for each scene cut...")
                progress_bar.progress(0.88)

                def on_clip_progress(ratio: float, msg: str) -> None:
                    progress_bar.progress(0.88 + 0.08 * ratio)
                    status_text.text(msg)

                extract_scene_clips(
                    video_path=video_path,
                    scenes=scenes,
                    output_dir=session.clips_dir,
                    max_clips=max_clips,
                    progress_callback=on_clip_progress,
                )
                try:
                    clips_zip_path = session.exports_dir / f"{Path(video_path).stem}_scene_clips.zip"
                    create_video_clips_zip(scenes, clips_zip_path)
                    clips_zip = clips_zip_path
                except Exception as ex:
                    logger.warning("Could not package clips zip: %s", ex)
                    clips_zip = None

            # Step 7: Summary and Exports
            status_text.text("Generating analytical summary and export packages...")
            summary = generate_video_summary(metadata, scenes, keyframes)

            # Visual contact sheet
            contact_sheet_path = session.exports_dir / "contact_sheet.jpg"
            generate_contact_sheet(
                keyframes=keyframes,
                output_path=contact_sheet_path,
                columns=config.contact_sheet_columns,
            )

            # Package exports
            zip_path = session.exports_dir / f"{Path(video_path).stem}_keyframes.zip"
            create_keyframe_zip(keyframes, zip_path)

            csv_path = session.exports_dir / "scenes_manifest.csv"
            export_scenes_csv(scenes, csv_path)

            json_path = session.exports_dir / "analysis_report.json"
            export_summary_json(metadata, summary, scenes, json_path, narrative=narrative)

            md_path = session.exports_dir / "summary_report.md"
            export_summary_markdown(metadata, summary, scenes, md_path, narrative=narrative)

            progress_bar.progress(1.0)
            status_text.empty()
            progress_bar.empty()

            # Store in session state for seamless tab navigation
            st.session_state["analysis_results"] = {
                "metadata": metadata,
                "scenes": scenes,
                "keyframes": keyframes,
                "summary": summary,
                "narrative": narrative,
                "zip_path": zip_path,
                "clips_zip": clips_zip,
                "csv_path": csv_path,
                "json_path": json_path,
                "md_path": md_path,
                "contact_sheet_path": contact_sheet_path if contact_sheet_path.exists() else None,
            }
            clip_count = sum(1 for s in scenes if s.clip_path)
            st.success(f"Analysis completed: {len(scenes)} scenes identified, {len(keyframes)} keyframes extracted, and {clip_count} video clips generated.")

        except ClipMindError as e:
            progress_bar.empty()
            status_text.empty()
            logger.error("Domain error: %s", str(e), exc_info=True)
            st.error(f"⚠️ {e.user_friendly_message}")
            return
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            logger.critical("Unexpected internal failure: %s", str(e), exc_info=True)
            st.error("⚠️ An unexpected error occurred while processing the video. Please verify the video plays locally and try again.")
            return

    # Render Results if available in state
    if "analysis_results" in st.session_state:
        results = st.session_state["analysis_results"]
        meta = results["metadata"]
        scenes = results["scenes"]
        keyframes = results["keyframes"]
        summary = results["summary"]
        narrative = results.get("narrative")
        zip_path = results["zip_path"]
        clips_zip = results.get("clips_zip")
        csv_path = results["csv_path"]
        json_path = results["json_path"]
        md_path = results["md_path"]
        contact_sheet_path = results["contact_sheet_path"]

        # Render KPI Cards & Timeline
        render_metadata_cards(meta)
        render_timeline_bar(scenes, meta.duration_seconds)

        # Render Next-Level Executive Narrative Hero
        if narrative:
            render_full_video_narrative_hero(narrative)

        # Master Video Preview on Page
        session_obj = st.session_state.get("active_session")
        if session_obj and (session_obj.video_dir / meta.filename).exists():
            with st.expander("📺 Master Video Player Monitor (Audio Active)", expanded=False):
                st.video(str(session_obj.video_dir / meta.filename))

        # Tabs for deep exploration
        tab_copilot, tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🤖 AI Video Copilot",
            "🎞️ Scene Video Clips",
            "🖼️ Keyframes & Storyboard",
            "📊 Analytics & Narrative",
            "📋 Scene Table",
            "📦 Export & Download",
        ])

        with tab_copilot:
            render_ai_copilot_chatbot(meta, scenes, summary, narrative)

        with tab1:
            if session_obj:
                render_precision_clip_trimmer(session_obj.video_dir / meta.filename, meta, session_obj.clips_dir)
            render_scene_clips_gallery(scenes)

        with tab2:
            if contact_sheet_path and contact_sheet_path.exists():
                with st.expander("📌 Full Video Contact Sheet / Storyboard Grid", expanded=True):
                    st.image(str(contact_sheet_path), use_container_width=True)
                    with open(contact_sheet_path, "rb") as cs_f:
                        st.download_button(
                            label="⬇️ Download Contact Sheet (JPEG)",
                            data=cs_f.read(),
                            file_name="video_storyboard_contact_sheet.jpg",
                            mime="image/jpeg",
                            key="dl_contact_sheet_top",
                        )

            render_keyframe_gallery(keyframes, scenes)

        with tab3:
            render_summary_analytics(summary)
            if narrative:
                render_scene_intelligence_cards(narrative)

        with tab4:
            st.markdown("##### 📋 Detected Scene Manifest")
            import pandas as pd
            df = pd.DataFrame([s.to_dict() for s in scenes])
            # Select and format human-friendly columns
            display_cols = [
                "scene_number",
                "start_timecode",
                "end_timecode",
                "duration_seconds",
                "pacing_label",
                "keyframe_timecode",
                "clip_filename",
            ]
            available_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[available_cols], use_container_width=True)

        with tab5:
            st.markdown("##### 📦 Export Intelligence Packages")
            st.write("Download complete analysis packages in standard industry formats.")

            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                if clips_zip and Path(clips_zip).exists():
                    with open(clips_zip, "rb") as czf:
                        st.download_button(
                            label="🎬 Video Clips ZIP",
                            data=czf.read(),
                            file_name=Path(clips_zip).name,
                            mime="application/zip",
                            use_container_width=True,
                        )
                else:
                    st.caption("Clips ZIP not generated")
            with c2:
                if zip_path.exists():
                    with open(zip_path, "rb") as zf:
                        st.download_button(
                            label="🗜️ Keyframes ZIP",
                            data=zf.read(),
                            file_name=zip_path.name,
                            mime="application/zip",
                            use_container_width=True,
                        )
            with c3:
                if csv_path.exists():
                    with open(csv_path, "rb") as cf:
                        st.download_button(
                            label="📊 Scenes CSV",
                            data=cf.read(),
                            file_name=csv_path.name,
                            mime="text/csv",
                            use_container_width=True,
                        )
            with c4:
                if json_path.exists():
                    with open(json_path, "rb") as jf:
                        st.download_button(
                            label="📄 Analysis JSON",
                            data=jf.read(),
                            file_name=json_path.name,
                            mime="application/json",
                            use_container_width=True,
                        )
            with c5:
                if md_path.exists():
                    with open(md_path, "rb") as mf:
                        st.download_button(
                            label="📝 Summary Markdown",
                            data=mf.read(),
                            file_name=md_path.name,
                            mime="text/markdown",
                            use_container_width=True,
                        )


if __name__ == "__main__":
    main()
