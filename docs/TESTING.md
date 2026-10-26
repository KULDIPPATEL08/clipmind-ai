# ClipMind AI — Testing Strategy & Verification Guide

## 1. Overview

ClipMind AI utilizes an automated testing pipeline powered by `pytest` and `pytest-cov`. The test suite uses synthetic, on-the-fly video generation via OpenCV fixtures, guaranteeing that all tests execute deterministically without external test video downloads or GPU hardware.

---

## 2. Test Suite Architecture

| Test Suite File | Domain Covered | Tests Implemented |
| :--- | :--- | :--- |
| `tests/test_config.py` | Configuration & Env overrides | `test_default_config_initialization`, `test_config_env_overrides` |
| `tests/test_security.py` | Input sanitization & upload checks | `test_sanitize_filename_prevents_traversal`, `test_validate_file_extension`, `test_validate_video_magic_bytes`, `test_save_upload_securely`, `test_save_upload_rejects_empty_file`, `test_save_upload_rejects_oversized_file` |
| `tests/test_metadata.py` | Video metadata & decodability | `test_format_duration`, `test_calculate_aspect_ratio`, `test_extract_metadata_success`, `test_extract_metadata_corrupted_file`, `test_extract_metadata_missing_file` |
| `tests/test_scene_detection.py` | PySceneDetect & OpenCV fallback | `test_seconds_to_timecode`, `test_detect_scenes_multiscene`, `test_detect_scenes_single_scene`, `test_detect_scenes_opencv_fallback` |
| `tests/test_keyframe_extraction.py`| Frame sampling, dedup & collage | `test_keyframe_extraction_and_contact_sheet`, `test_keyframe_extraction_empty_scenes` |
| `tests/test_export.py` | ZIP, CSV, JSON, Markdown exports | `test_complete_export_workflow` |
| `tests/test_cleanup.py` | Isolation & Janitor cleanup | `test_job_session_cleanup`, `test_job_session_context_manager`, `test_cleanup_stale_jobs` |

---

## 3. Running Automated Tests

### 3.1 Standard Test Execution
```bash
# Run all tests with verbose output
pytest -v tests/
```

### 3.2 Coverage Report
```bash
# Run tests with terminal coverage report
pytest -v --cov=clipmind --cov-report=term-missing tests/
```

### 3.3 HTML Coverage Generation
```bash
pytest --cov=clipmind --cov-report=html tests/
# Open htmlcov/index.html in browser
```

---

## 4. Verification Evidence

Latest test run executed on Windows / Python 3.11.9:
```
tests/test_cleanup.py::test_job_session_cleanup PASSED                   [  4%]
tests/test_cleanup.py::test_job_session_context_manager PASSED           [  8%]
tests/test_cleanup.py::test_cleanup_stale_jobs PASSED                    [ 13%]
tests/test_config.py::test_default_config_initialization PASSED          [ 17%]
tests/test_config.py::test_config_env_overrides PASSED                   [ 21%]
tests/test_export.py::test_complete_export_workflow PASSED               [ 26%]
tests/test_keyframe_extraction.py::test_keyframe_extraction_and_contact_sheet PASSED [ 30%]
tests/test_keyframe_extraction.py::test_keyframe_extraction_empty_scenes PASSED [ 34%]
tests/test_metadata.py::test_format_duration PASSED                      [ 39%]
tests/test_metadata.py::test_calculate_aspect_ratio PASSED               [ 43%]
tests/test_metadata.py::test_extract_metadata_success PASSED             [ 47%]
tests/test_metadata.py::test_extract_metadata_corrupted_file PASSED      [ 52%]
tests/test_metadata.py::test_extract_metadata_missing_file PASSED        [ 56%]
tests/test_scene_detection.py::test_seconds_to_timecode PASSED           [ 60%]
tests/test_scene_detection.py::test_detect_scenes_multiscene PASSED      [ 65%]
tests/test_scene_detection.py::test_detect_scenes_single_scene PASSED    [ 69%]
tests/test_scene_detection.py::test_detect_scenes_opencv_fallback PASSED [ 73%]
tests/test_security.py::test_sanitize_filename_prevents_traversal PASSED [ 78%]
tests/test_security.py::test_validate_file_extension PASSED              [ 82%]
tests/test_security.py::test_validate_video_magic_bytes PASSED           [ 86%]
tests/test_security.py::test_save_upload_securely PASSED                 [ 91%]
tests/test_security.py::test_save_upload_rejects_empty_file PASSED       [ 95%]
tests/test_security.py::test_save_upload_rejects_oversized_file PASSED   [100%]

============================= 23 passed in 3.80s ==============================
```
