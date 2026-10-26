# ClipMind AI — Architecture & Technical Design

## 1. Executive Summary

ClipMind AI is an enterprise-grade, scene-aware video summarization and keyframe extraction platform designed to process digital video streams efficiently on CPU architecture. The application is built on modular Python micro-components, utilizing OpenCV and PySceneDetect for deterministic computer vision, Pillow for visual collage synthesis, and Streamlit for a reactive user interface.

---

## 2. System Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                  USER / BROWSER                                   |
+-----------------------------------------+-----------------------------------------+
                                          |
                                HTTP / WebSocket (8501)
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                         STREAMLIT APPLICATION (app.py)                            |
|  - Brand Header & KPI Cards                                                       |
|  - Drag & Drop Upload / Demo Video Trigger                                        |
|  - Visual Timeline Bar & Filterable Keyframe Gallery                              |
|  - Multi-tab Dashboard (Storyboard, Analytics, Data Table, Exports)               |
+-------------------+---------------------+---------------------+-------------------+
                    |                     |                     |
                    v                     v                     v
+-----------------------+ +-----------------------+ +-----------------------+
|  SECURITY LAYER       | |  VIDEO PIPELINE       | |  EXPORT & ANALYTICS   |
|  (clipmind.security)  | |  (clipmind.video)     | |  (clipmind.export,    |
|  - JobSession Context | |  - metadata.py        | |   clipmind.analysis)  |
|  - Container Signatures| |    (Resolution, FPS,  | |  - summary.py         |
|  - Extension Whitelist| |     Duration, Codec)  | |    (Pacing analytics, |
|  - Path Sanitization  | |  - detector.py        | |     Phase breakdown)  |
|  - Size & Time Limits | |    (PySceneDetect +   | |  - exporter.py        |
|  - Ephemeral Cleanup  | |     OpenCV Fallback)  | |    (ZIP, CSV, JSON,   |
+-----------------------+ |  - keyframe.py        | |     Markdown, Collage)|
                          |    (Selection, Dedup, | +-----------------------+
                          |     PIL Contact Sheet)|
                          +-----------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                      EPHEMERAL ISOLATED STORAGE WORKSPACE                         |
|  .clipmind_tmp/<job_id>/                                                          |
|    |-- video/       (Sanitized randomized video file)                             |
|    |-- keyframes/   (Extracted JPEG keyframe images with timestamps)              |
|    |-- exports/     (ZIP archive, CSV manifest, JSON report, MD report)           |
+-----------------------------------------------------------------------------------+
```

---

## 3. Module Breakdown & Separation of Concerns

1. **`clipmind.config` (`AppConfig`)**:
   - Centralized 12-factor configuration.
   - Reads environment variables with secure, production-tested fallback defaults.
   - Zero hardcoding in downstream modules.

2. **`clipmind.security` (`JobSession`, validators)**:
   - Enforces defense-in-depth on untrusted uploads.
   - Isolates processing in non-executable job directories.
   - Performs container signature checks (magic bytes: MP4, MKV/WEBM, AVI).
   - Sanitizes filenames against path traversal.
   - Guarantees immediate cleanup on completion, error, or context exit.

3. **`clipmind.video`**:
   - `metadata.py`: Extracts dimensions, frame count, FPS, aspect ratio, and codec. Probes initial frames to detect corrupted video streams.
   - `detector.py`: Implements PySceneDetect (`ContentDetector`, `AdaptiveDetector`, `ThresholdDetector`) with a deterministic OpenCV HSV histogram difference fallback.
   - `keyframe.py`: Extracts stable middle/start/peak frames per scene, executes color histogram deduplication, and renders tiled high-resolution contact sheets with PIL.

4. **`clipmind.analysis` (`summary.py`)**:
   - Categorizes pacing (Rapid cuts <2s, Standard 2-8s, Extended takes >8s).
   - Generates three-phase narrative structure (Intro, Body, Outro).
   - Transparently discloses deterministic CV methodology without generative hallucinations.

5. **`clipmind.export` (`exporter.py`)**:
   - Assembles clean ZIP archives of keyframes.
   - Exports standardized CSV scene manifests.
   - Generates schema-valid JSON metadata.
   - Formats Markdown intelligence reports with Markdown tables.

6. **`clipmind.ui` (`components.py`, `styles.py`)**:
   - Modern dark design system using custom CSS tokens.
   - Visual timeline bar with proportional scene segments.
   - Filterable keyframe gallery with direct frame downloads.
