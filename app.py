"""ClipMind AI — Streamlit Web Application Entrypoint."""

from __future__ import annotations

import importlib
import io
from pathlib import Path
import sys
from typing import Optional

# Ensure hot-reloaded modules in running Streamlit processes stay strictly in sync
for _mod in ["clipmind.video.clipper", "clipmind.ui.components", "clipmind.export.exporter"]:
    if _mod in sys.modules:
        try:
            importlib.reload(sys.modules[_mod])
        except Exception:
            pass

import cv2
import numpy as np
import streamlit as st

from clipmind.analysis.description import generate_full_video_narrative
from clipmind.analysis.summary import generate_video_summary
from clipmind.config import config
from clipmind.exceptions import ClipMindError
from clipmind.export.exporter import (
    create_interval_clips_zip,
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
import textwrap

from clipmind.ui.components import (
    render_ai_cockpit_status_bar,
    render_ai_copilot_chatbot,
    render_brand_header,
    render_fixed_interval_cutter,
    render_full_video_narrative_hero,
    render_interval_clips_gallery,
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


def render_html(html_str: str) -> None:
    """Safely render HTML without CommonMark code-block indentation bugs."""
    clean = "".join(line.strip() for line in html_str.splitlines() if line.strip())
    if hasattr(st, "html"):
        st.html(clean)
    else:
        st.markdown(clean, unsafe_allow_html=True)



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
    if target_path.exists() and target_path.stat().st_size > 5000:
        return target_path

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


def reset_all_state() -> None:
    """Atomically resets all ClipMind session state for a clean new analysis."""
    keys_to_clear = [
        "analysis_results", "staged_type", "staged_file",
        "copilot_history", "active_session", "last_custom_clip",
        "last_custom_clip_meta", "clip_trim_slider",
        "trim_start_val", "trim_end_val",
        "custom_trim_slider", "num_trim_start", "num_trim_end",
        "interval_win_start", "interval_win_end", "interval_chunk_len",
        "generated_interval_clips", "generated_interval_zip",
    ]
    for k in keys_to_clear:
        st.session_state.pop(k, None)
    # Increment uploader key counter to force Streamlit to render a fresh empty widget
    st.session_state["uploader_key_counter"] = (
        st.session_state.get("uploader_key_counter", 0) + 1
    )


def main() -> None:
    """Main application routine."""
    # Top AI Cockpit Telemetry Strip & Brand Header
    render_ai_cockpit_status_bar()
    render_brand_header()

    # Periodic background cleanup of stale jobs (silent, non-blocking)
    try:
        cleanup_stale_jobs(max_age_seconds=3600)
    except Exception as e:
        logger.debug("Background stale job cleanup: %s", e)

    # If results are already present, render the complete Studio Results view
    if "analysis_results" in st.session_state:
        render_results_workspace()
        return

    # ── Initialize session state defaults ────────────────────────────────────
    if "staged_type" not in st.session_state:
        st.session_state["staged_type"] = None
    if "uploader_key_counter" not in st.session_state:
        st.session_state["uploader_key_counter"] = 0

    # Read the staged file from our own session key (not the widget key directly)
    # This is stable across reruns and key changes.
    uploaded_file = st.session_state.get("staged_file")

    # Determine current staged status
    is_demo_staged = st.session_state.get("staged_type") == "demo"
    is_upload_staged = st.session_state.get("staged_type") == "upload"
    is_any_staged = is_demo_staged or is_upload_staged

    # Guard: uploaded file disappeared (page refresh mid-session)
    if is_upload_staged and uploaded_file is None:
        st.warning(
            "⚠️ Your uploaded video was cleared (likely a page refresh or session reset). "
            "Please re-upload your video to continue."
        )
        reset_all_state()
        st.rerun()

    # =========================================================================
    # PHASE A: LANDING & INGESTION (When no video is staged yet)
    # =========================================================================
    if not is_any_staged:
        # Show Landing Showcase
        render_landing_showcase()

        render_html(
            """<div class="deck-headline">
                <div class="deck-title">
                    <span>📥 Step 1: Ingest Video to Studio</span>
                </div>
                <span class="deck-specs-tag">Local Enclave • Zero-Upload Lag</span>
            </div>"""
        )

        col_up, col_demo = st.columns([3, 2])

        with col_up:
            st.markdown("##### 📤 Option A: Upload Your Video File")
            st.caption("Supports MP4, MOV, AVI, MKV, and WEBM containers.")
            # Use a dynamic key so incrementing the counter forces a fresh empty widget
            uploader_key = f"video_uploader_{st.session_state['uploader_key_counter']}"
            new_upload = st.file_uploader(
                "Drag and drop video here",
                type=["mp4", "mov", "avi", "mkv", "webm"],
                help=f"Maximum size: {config.max_upload_size_mb} MB. Maximum duration: {config.max_video_duration_seconds // 60} mins.",
                key=uploader_key,
            )
            if new_upload is not None:
                # Store the file object in our own key, independent of the widget key
                st.session_state["staged_file"] = new_upload
                st.session_state["staged_type"] = "upload"
                st.rerun()

        with col_demo:
            st.markdown("##### ⚡ Option B: 1-Click Instant Demo")
            st.caption("No video file on hand? Evaluate the complete pipeline with our synthetic benchmark.")
            render_html(
                """<div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 16px; margin-bottom: 14px;">
                    <div style="font-size: 0.92rem; font-weight: 700; color: #f8fafc; margin-bottom: 4px;">🎯 4-Scene Benchmark Video</div>
                    <div style="font-size: 0.82rem; color: #94a3b8; line-height: 1.45;">
                        Features hard cuts, color shifts, high-contrast objects, and audio support. Pre-configured for immediate testing.
                    </div>
                </div>"""
            )
            if st.button("✨ Load Instant Demo Video (4 Scenes)", use_container_width=True):
                st.session_state["staged_type"] = "demo"
                st.rerun()

        render_html(
            """<div style="margin-top: 20px; text-align: center; color: #64748b; font-size: 0.84rem;">
                💡 <i>Select or upload a video above. You will be able to watch the on-page preview and configure all speed, cut, and audio dials before starting!</i>
            </div>"""
        )
        return

    # =========================================================================
    # PHASE B: VIDEO STAGED & INTERACTIVE STUDIO CONFIGURATION (BEFORE START)
    # =========================================================================
    render_html(
        """<div class="pipeline-stepper" style="margin-top: 0; margin-bottom: 22px;">
            <div class="step-item"><span class="step-num">01</span> ✅ Video Loaded & Ready</div>
            <span class="step-arrow">➔</span>
            <div class="step-item" style="color: #38bdf8;"><span class="step-num" style="background: rgba(56, 189, 248, 0.2); border-color: #38bdf8; color: #38bdf8;">02</span> 🎛️ Preview & Configure Studio Dials</div>
            <span class="step-arrow">➔</span>
            <div class="step-item"><span class="step-num">03</span> 🚀 Click Start Button Below</div>
        </div>"""
    )

    # Prepare physical video path on disk for immediate extraction & trimming tools
    staging_dir = config.base_temp_dir / "clipmind_staged_media"
    staging_dir.mkdir(parents=True, exist_ok=True)
    if is_demo_staged:
        staged_video_path = staging_dir / "demo_synthetic_preview.mp4"
        create_demo_synthetic_video(staged_video_path)
    else:
        staged_video_path = staging_dir / uploaded_file.name
        if not staged_video_path.exists() or staged_video_path.stat().st_size != len(uploaded_file.getvalue()):
            with open(staged_video_path, "wb") as f:
                f.write(uploaded_file.getvalue())

    # Cache metadata for instant UI responsiveness
    meta_cache_key = f"staged_meta_{staged_video_path.name}_{staged_video_path.stat().st_size}"
    if meta_cache_key in st.session_state:
        staged_metadata = st.session_state[meta_cache_key]
    else:
        staged_metadata = extract_video_metadata(staged_video_path)
        st.session_state[meta_cache_key] = staged_metadata

    # Layout: Left = Video Preview & Media Specs, Right = Studio Controls & Slicing Suite
    col_preview, col_controls = st.columns([1, 1], gap="large")

    with col_preview:
        st.markdown("##### 📺 Video Monitor & Audio Verification")
        try:
            st.video(str(staged_video_path))
        except Exception:
            try:
                st.video(uploaded_file)
            except Exception:
                st.warning("⚠️ Could not preview this video in browser. It will still be processed correctly.")

        render_html(
            f"""<div class="staged-video-card">
                <div class="staged-header">
                    <div class="staged-title">
                        <span>🎬 {staged_metadata.filename}</span>
                    </div>
                    <span class="audio-sound-active-badge">🔊 Sound Preserved</span>
                </div>
                <div class="staged-details-grid">
                    <div class="staged-detail-item">Duration: <b>{staged_metadata.duration_formatted} ({staged_metadata.duration_seconds:.1f}s)</b></div>
                    <div class="staged-detail-item">Resolution: <b>{staged_metadata.width}x{staged_metadata.height} ({staged_metadata.aspect_ratio})</b></div>
                    <div class="staged-detail-item">Frame Rate: <b>{staged_metadata.fps} FPS</b></div>
                    <div class="staged-detail-item">File Size: <b>{staged_metadata.file_size_mb} MB ({staged_metadata.fourcc_codec})</b></div>
                </div>
            </div>"""
        )

        if st.button("✖ Change / Choose Another Video", use_container_width=True):
            reset_all_state()
            st.rerun()

    with col_controls:
        st.markdown("##### 🎛️ Studio Intelligence & Slicing Suite")
        st.caption("Slice custom fixed-duration clips right now, or tune AI detection dials for full analysis.")

        tab_slicer, tab_trimmer, tab_dials = st.tabs([
            "✂️ Fixed 60s/Custom Clip Slicer",
            "🎯 Single Clip Trimmer",
            "⚙️ AI Pipeline Dials",
        ])

        with tab_slicer:
            render_fixed_interval_cutter(
                video_path=staged_video_path,
                metadata=staged_metadata,
                output_dir=staging_dir / "interval_clips",
            )

        with tab_trimmer:
            render_precision_clip_trimmer(
                video_path=staged_video_path,
                metadata=staged_metadata,
                output_dir=staging_dir / "custom_clips",
            )

        with tab_dials:
            # Dial 1: Speed Engine
            st.markdown("###### ⚡ Speed & Acceleration Profile")
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

            # Dial 2: Scene Cut Engine
            st.markdown("###### ⚙️ Scene Cut Detection Engine")
            detector_choice = st.selectbox(
                "Detection Engine Mode",
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

            c_s1, c_s2 = st.columns(2)
            with c_s1:
                if detector_type in ["hybrid", "adaptive"]:
                    adaptive_thresh = st.slider("Adaptive Sensitivity", 1.5, 6.0, 3.0, 0.2)
                else:
                    adaptive_thresh = 3.0
                threshold = st.slider("Content Cut Threshold", 10.0, 50.0, float(config.default_content_threshold), 1.0)
            with c_s2:
                min_scene_frames = st.slider("Min Scene Length (Frames)", 5, 90, config.default_min_scene_length_frames, 5)
                keyframe_strategy = st.selectbox("Representative Frame", ["middle", "start", "end"], index=0)

            # Dial 3: Lossless Audio Slicing & Keyframes
            st.markdown("###### 🎬 Lossless Video Slicing & Keyframe Options")
            c_k1, c_k2 = st.columns(2)
            with c_k1:
                generate_clips = st.checkbox("✂️ Generate Scene Video Clips (100% Audio Intact)", value=True)
                enable_dedup = st.checkbox("🖼️ Keyframe Deduplication", value=True)
            with c_k2:
                max_clips = st.slider("Max Video Clips Limit", 5, 50, 25, 5)
                max_keyframes = st.slider("Max Keyframes Limit", 5, 100, 30, 5)

            pipeline_aspect_choice = st.selectbox(
                "Scene Clips Layout Format",
                [
                    "🖥️ Original Source Aspect Ratio",
                    "📱 9:16 Vertical Portrait (Shorts & Reels • Blurred BG)",
                    "✂️ 9:16 Vertical Portrait (Center Crop Fill)",
                ],
                index=0,
                help="Format auto-generated scene clips for standard widescreen or vertical mobile shorts (9:16).",
            )
            pipeline_aspect_map = {
                "🖥️ Original Source Aspect Ratio": "original",
                "📱 9:16 Vertical Portrait (Shorts & Reels • Blurred BG)": "9:16_blurred",
                "✂️ 9:16 Vertical Portrait (Center Crop Fill)": "9:16_crop",
            }
            pipeline_aspect = pipeline_aspect_map[pipeline_aspect_choice]

    # Step 3: Launch Action Bar
    st.markdown("---")
    render_html(
        """<div style="text-align: center; margin-bottom: 12px;">
            <span style="font-size: 1.15rem; font-weight: 800; color: #f8fafc; letter-spacing: -0.01em;">
                Ready to Process? Click below to launch AI video analysis
            </span>
        </div>"""
    )

    start_analysis = st.button(
        "🚀 START AI VIDEO ANALYSIS & CUTTING",
        type="primary",
        use_container_width=True,
    )

    render_html(
        """<div style="text-align: center; margin-top: 8px; color: #64748b; font-size: 0.8rem; font-family: monospace;">
            🔒 ZERO-LEAK LOCAL WORKSPACE • AUDIO STREAM PRESERVATION • FRAME-ACCURATE CUTTING
        </div>"""
    )

    if not start_analysis:
        return

    # =========================================================================
    # PHASE C: EXECUTION PIPELINE (Triggered ONLY on Start Button click)
    # =========================================================================
    session = JobSession()
    session.start()
    st.session_state["active_session"] = session

    progress_bar = st.progress(0.0)
    status_text = st.empty()

    try:
        # Step 1: Ingestion and Validation
        status_text.text("Validating video file and container headers...")
        progress_bar.progress(0.12)

        if is_demo_staged:
            video_path = session.video_dir / "demo_synthetic.mp4"
            create_demo_synthetic_video(video_path)
        else:
            # Read from our stable staged_file key (not the widget key)
            _upload = st.session_state.get("staged_file") or uploaded_file
            if _upload is None:
                raise ClipMindError(
                    "No uploaded file found in session.",
                    user_friendly_message="No video file was found. Please re-upload your video and try again.",
                )
            # Seek to start in case the file object was already partially read
            try:
                _upload.seek(0)
            except Exception:
                pass
            video_path = save_upload_securely(
                file_obj=_upload,
                original_filename=_upload.name,
                job_session=session,
            )

        # Step 2: Metadata Extraction
        status_text.text("Extracting video metadata, codecs, and audio streams...")
        progress_bar.progress(0.25)
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
            progress_bar.progress(min(0.55, 0.25 + 0.30 * ratio))
            status_text.text(msg)

        scenes = detector.detect_scenes(
            video_path=video_path,
            metadata=metadata,
            progress_callback=on_detect_progress,
        )

        # Step 4: Keyframe Extraction & Deduplication
        status_text.text(f"Extracting representative keyframes for {len(scenes)} scenes...")
        progress_bar.progress(0.60)
        extractor = KeyframeExtractor(
            strategy=keyframe_strategy,
            enable_deduplication=enable_dedup,
            max_keyframes=max_keyframes,
        )

        def on_extract_progress(ratio: float, msg: str) -> None:
            progress_bar.progress(0.60 + 0.15 * ratio)
            status_text.text(msg)

        keyframes = extractor.extract_keyframes(
            video_path=video_path,
            scenes=scenes,
            output_dir=session.keyframes_dir,
            progress_callback=on_extract_progress,
        )

        # Step 5: Deep Video Narrative & Visual Aesthetics Analysis
        status_text.text("Synthesizing executive video narrative, color palettes, and motion dynamics...")
        progress_bar.progress(0.78)
        narrative = generate_full_video_narrative(metadata, scenes, keyframes)

        # Step 6: Lossless Video Clip Extraction
        clips_zip = None
        if generate_clips:
            status_text.text("Extracting frame-accurate video clips (.mp4) with 100% audio preserved...")
            progress_bar.progress(0.85)

            def on_clip_progress(ratio: float, msg: str) -> None:
                progress_bar.progress(0.85 + 0.08 * ratio)
                status_text.text(msg)

            import inspect
            sig = inspect.signature(extract_scene_clips)
            clip_kwargs = {
                "video_path": video_path,
                "scenes": scenes,
                "output_dir": session.clips_dir,
                "max_clips": max_clips,
                "progress_callback": on_clip_progress,
            }
            if "aspect_ratio" in sig.parameters:
                clip_kwargs["aspect_ratio"] = pipeline_aspect

            extract_scene_clips(**clip_kwargs)
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
            "interval_clips": st.session_state.get("generated_interval_clips"),
            "interval_zip": st.session_state.get("generated_interval_zip"),
        }
        st.rerun()

    except ClipMindError as e:
        progress_bar.empty()
        status_text.empty()
        logger.error("Domain error: %s", str(e), exc_info=True)
        st.error(f"⚠️ {e.user_friendly_message}")
        col_retry, col_change = st.columns(2)
        with col_retry:
            if st.button("🔁 Try Again", use_container_width=True):
                st.session_state.pop("analysis_results", None)
                st.rerun()
        with col_change:
            if st.button("📤 Upload Different Video", use_container_width=True):
                reset_all_state()
                st.rerun()
        return
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        logger.critical("Unexpected internal failure: %s", str(e), exc_info=True)
        st.error(
            "⚠️ An unexpected error occurred while processing the video. "
            "Please verify the video plays locally and try again.\n\n"
            f"**Error**: `{type(e).__name__}: {e}`"
        )
        if st.button("🔄 Start Over", use_container_width=True):
            reset_all_state()
            st.rerun()
        return


def render_results_workspace() -> None:
    """Renders the comprehensive post-analysis intelligence workspace."""
    results = st.session_state.get("analysis_results")
    if not results:
        st.error(
            "⚠️ Analysis results could not be loaded — this usually happens after a page refresh. "
            "Please re-upload your video and run the analysis again."
        )
        if st.button("🔄 Start Over", type="primary"):
            reset_all_state()
            st.rerun()
        return
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
    contact_sheet_path = results.get("contact_sheet_path")
    session_obj = st.session_state.get("active_session")

    clip_count = sum(1 for s in scenes if s.clip_path)

    # Top Results Action Bar
    r_col1, r_col2 = st.columns([4, 1])
    with r_col1:
        render_html(
            f"""<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap;">
                <span style="font-size: 1.3rem; font-weight: 800; color: #ffffff;">🎬 Analysis Complete</span>
                <span class="badge-pill badge-standard">⚡ {len(scenes)} Scenes Detected</span>
                <span class="badge-pill badge-extended">🖼️ {len(keyframes)} Keyframes</span>
                <span class="audio-sound-active-badge">✂️ {clip_count} Audio Clips</span>
            </div>"""
        )
    with r_col2:
        if st.button("🔄 Analyze Another Video", type="secondary", use_container_width=True):
            reset_all_state()
            st.rerun()

    # Video Metadata KPI Cards
    render_metadata_cards(meta)

    # Proportional Timeline Bar
    render_timeline_bar(scenes, meta.duration_seconds)

    # Executive Narrative Hero Card
    if narrative:
        render_full_video_narrative_hero(narrative)

    # Master Video Preview Expandable — find the actual video file in job dir safely
    if session_obj:
        _master_video_path = session_obj.video_dir / meta.filename
        if not _master_video_path.exists():
            # Fallback: find any video file in job video dir (randomized internal name)
            _video_candidates = list(session_obj.video_dir.glob("video_*.*"))
            _master_video_path = _video_candidates[0] if _video_candidates else None
        if _master_video_path and Path(_master_video_path).exists():
            with st.expander("📺 Master Video Player (Audio Active)", expanded=False):
                try:
                    st.video(str(_master_video_path))
                except Exception as _ve:
                    st.caption(f"⚠️ Video preview unavailable: {_ve}")

    # Exploration Tabs
    tab_copilot, tab_interval_slicer, tab_clips, tab_storyboard, tab_analytics, tab_manifest, tab_export = st.tabs([
        "🤖 AI Video Copilot",
        "✂️ Fixed 60s/Interval Slicer",
        "🎬 Scene Cut Clips (Sound Intact)",
        "🖼️ Keyframes & Storyboard",
        "📊 Analytics & Narrative",
        "📋 Scene Table Manifest",
        "📦 Export & Download Packages",
    ])

    with tab_copilot:
        render_ai_copilot_chatbot(meta, scenes, summary, narrative)

    with tab_interval_slicer:
        if session_obj:
            _clip_vid = session_obj.video_dir / meta.filename
            if not _clip_vid.exists():
                _cvids = list(session_obj.video_dir.glob("video_*.*"))
                _clip_vid = _cvids[0] if _cvids else None
            if _clip_vid and Path(_clip_vid).exists():
                render_fixed_interval_cutter(
                    video_path=Path(_clip_vid),
                    metadata=meta,
                    output_dir=session_obj.clips_dir / "interval_clips",
                )
            else:
                st.info("ℹ️ Source video file not accessible for interval slicing in this session.")
        elif st.session_state.get("generated_interval_clips"):
            render_interval_clips_gallery(
                interval_clips=st.session_state["generated_interval_clips"],
                zip_path=st.session_state.get("generated_interval_zip"),
            )
        else:
            st.info("ℹ️ No interval clips created yet.")

    with tab_clips:
        if session_obj:
            # Resolve actual video path safely
            _clip_vid = session_obj.video_dir / meta.filename
            if not _clip_vid.exists():
                _cvids = list(session_obj.video_dir.glob("video_*.*"))
                _clip_vid = _cvids[0] if _cvids else None
            if _clip_vid and Path(_clip_vid).exists():
                render_precision_clip_trimmer(Path(_clip_vid), meta, session_obj.clips_dir)
            else:
                st.info("ℹ️ Source video file not accessible for custom clip trimming in this session.")
        render_scene_clips_gallery(scenes)

    with tab_storyboard:
        if contact_sheet_path and Path(contact_sheet_path).exists():
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

    with tab_analytics:
        render_summary_analytics(summary)
        if narrative:
            render_scene_intelligence_cards(narrative)

    with tab_manifest:
        st.markdown("##### 📋 Detected Scene Manifest")
        import pandas as pd
        df = pd.DataFrame([s.to_dict() for s in scenes])
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

    with tab_export:
        st.markdown("##### 📦 Export Intelligence Packages")
        st.write("Download complete analysis packages in standard industry formats.")

        int_zip = results.get("interval_zip") or st.session_state.get("generated_interval_zip")
        if int_zip and Path(int_zip).exists():
            c_int_p = Path(int_zip)
            st.markdown("###### ✂️ Fixed-Duration Interval Clips Package")
            with open(c_int_p, "rb") as izf:
                st.download_button(
                    label=f"📦 Download Interval Clips ZIP ({round(c_int_p.stat().st_size / (1024 * 1024), 2)} MB)",
                    data=izf.read(),
                    file_name=c_int_p.name,
                    mime="application/zip",
                    key="dl_export_interval_zip",
                    use_container_width=True,
                )

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
