# ClipMind AI 🎬
### Scene-Aware Video Summarization and Keyframe Extraction Platform

[![ClipMind CI](https://github.com/clipmind/clipmind-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/clipmind/clipmind-ai/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)](https://www.docker.com/)

ClipMind AI is an enterprise-grade, scene-aware video intelligence application. It performs deterministic scene boundary detection, extracts timestamped representative keyframes, generates visual contact sheets, analyzes video pacing and narrative structure, and exports intelligence packages in industry-standard formats (ZIP, CSV, JSON, Markdown).

---

## 🌟 Key Features

- **🛡️ Secure Upload & Ingestion**:
  - Container magic byte signature verification (MP4, MKV, MOV, AVI, WEBM).
  - Protection against path traversal and file upload attacks.
  - Streaming chunked file-size enforcement (default 500 MB limit).
  - Ephemeral isolated working sessions with automated cleanup.

- **🔍 Dual-Engine Scene Detection**:
  - Primary: **PySceneDetect** (`ContentDetector`, `AdaptiveDetector`, `ThresholdDetector`).
  - Fallback: Deterministic **OpenCV HSV histogram differencing** for uninterrupted execution on edge-case video streams.
  - Configurable sensitivity threshold and minimum scene length in frames.

- **🖼️ Timestamped Keyframe Extraction & Deduplication**:
  - Representative frame selection strategies: Middle (recommended), Start, End.
  - Perceptual color histogram deduplication to filter visually near-identical frames across scenes.
  - Built-in tiled **Visual Contact Sheet / Storyboard Grid** generator (Pillow).

- **📊 Structural Video Analytics**:
  - Video KPI metrics: duration, resolution, aspect ratio, frame rate, total frames, FourCC codec.
  - Pacing metrics: Rapid cuts (<2s), Standard takes (2-8s), Extended takes (>8s).
  - Phased structural video breakdown (Intro, Core Body, Conclusion).
  - Transparent methodology disclosure (zero generative hallucinations).

- **📦 Multi-Format Export Engine**:
  - Keyframes ZIP archive with timestamped file names.
  - Standardized CSV scene manifest with timecodes.
  - Machine-readable JSON metadata export.
  - Formatted Markdown summary report.
  - High-resolution JPEG contact sheet.

- **🎨 Modern Dark UI / UX**:
  - Responsive layout built with Streamlit and modern CSS design tokens.
  - Interactive proportional scene timeline visualizer.
  - Searchable and filterable keyframe gallery with individual download buttons.
  - One-click **"Load Demo Video"** button for immediate testing without external video files.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### 2. Local Setup
```bash
# Clone the repository
git clone https://github.com/clipmind/clipmind-ai.git
cd clipmind-ai

# Create and activate virtual environment
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt
```

### 3. Launch the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🐳 Docker Deployment

A production-ready `Dockerfile` and `docker-compose.yml` are provided. The container runs as a secure, unprivileged non-root user (`clipmind`) and mounts temporary storage on `tmpfs`.

```bash
# Build and run with Docker Compose
docker compose up --build -d

# Check service health
docker compose ps
```
The application will be accessible at `http://localhost:8501`.

---

## 🧪 Automated Testing

ClipMind AI includes a comprehensive test suite using synthetic video generation via OpenCV fixtures:

```bash
# Run all tests
pytest -v tests/

# Run with test coverage report
pytest -v --cov=clipmind --cov-report=term-missing tests/
```
All 23 tests execute in under 4 seconds without requiring GPU or internet access.

---

## ⚙️ Configuration Reference

All settings can be configured via environment variables:

| Environment Variable | Default | Description |
| :--- | :--- | :--- |
| `CLIPMIND_MAX_UPLOAD_MB` | `500` | Maximum allowable video file upload size in megabytes |
| `CLIPMIND_MAX_DURATION_SEC`| `3600` | Maximum video duration allowed (seconds) |
| `CLIPMIND_MAX_FRAME_DIM` | `4096` | Maximum allowed video frame width or height (pixels) |
| `CLIPMIND_AUTO_CLEANUP` | `true` | Automatically delete ephemeral job folders on completion |
| `CLIPMIND_TEMP_DIR` | `.clipmind_tmp`| Base path for isolated ephemeral job storage |
| `CLIPMIND_LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## 📁 Project Structure

```
clipmind-ai/
├── app.py                      # Main Streamlit web application
├── clipmind/                   # Core Python application package
│   ├── config.py               # 12-factor configuration & env settings
│   ├── exceptions.py           # Custom domain exception hierarchy
│   ├── logger.py               # Structured logging with job_id context
│   ├── security.py             # Security, magic bytes check, JobSession
│   ├── analysis/
│   │   └── summary.py          # Scene pacing analytics & visual narrative
│   ├── export/
│   │   └── exporter.py         # ZIP, CSV, JSON, Markdown, and collage exporters
│   ├── ui/
│   │   ├── components.py       # Streamlit UI cards, gallery, timeline
│   │   └── styles.py           # CSS design tokens & responsive styles
│   └── video/
│       ├── detector.py         # PySceneDetect + OpenCV fallback detector
│       ├── keyframe.py         # Keyframe sampling, deduplication, contact sheet
│       └── metadata.py         # OpenCV video metadata extraction & validation
├── tests/                      # Automated test suite
│   ├── conftest.py             # OpenCV synthetic video fixtures
│   ├── test_cleanup.py         # Workspace isolation & janitor tests
│   ├── test_config.py          # AppConfig and environment override tests
│   ├── test_export.py          # Multi-format export verification tests
│   ├── test_keyframe_extraction.py # Frame sampling & contact sheet tests
│   ├── test_metadata.py        # Metadata & decodability tests
│   ├── test_scene_detection.py # Scene cut detection & timecode tests
│   └── test_security.py        # Magic bytes, sanitization & size limit tests
├── docs/                       # Technical documentation
│   ├── ARCHITECTURE.md         # System design & module breakdown
│   ├── SECURITY.md             # Threat model & security controls
│   ├── TESTING.md              # Testing matrix & execution guide
│   └── ANTIGRAVITY_MASTER_PROMPT.md # Autonomous engineering reference
├── Dockerfile                  # Secure non-root container configuration
├── docker-compose.yml          # Container orchestration with resource caps
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development and testing dependencies
└── TASKS.md                    # Implementation tracking matrix
```

---

## 🔒 Security & Disclosure

Please refer to [docs/SECURITY.md](docs/SECURITY.md) for details on the security posture and threat model.
ClipMind AI uses deterministic algorithmic computer vision for scene and pacing summaries. It does not generate fabricated semantic transcripts or hallucinated descriptions.
