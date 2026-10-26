# ClipMind AI — Security Architecture & Threat Model

## 1. Threat Model & Security Posture

Digital video files are untrusted binary inputs that can carry decompression bombs, malformed container headers, path traversal payloads, or attempt shell execution. ClipMind AI enforces a strict defense-in-depth security model:

```
[Untrusted Input]
       |
       v
1. Extension Whitelist (.mp4, .mov, .avi, .mkv, .webm)
       |
       v
2. Container Header Inspection (Magic bytes: ftyp, EBML, RIFF)
       |
       v
3. Strict Size Ceiling (Chunked stream check, default 500 MB)
       |
       v
4. Randomized Internal Filename (UUIDv4 — zero reliance on upload name)
       |
       v
5. Isolated Job Directory (.clipmind_tmp/<job_id>/)
       |
       v
6. Decodability Verification (Probe frame 0 with OpenCV in try/finally)
       |
       v
7. Duration and Resolution Constraints (Max 1 hr, Max 4096px)
       |
       v
8. Automatic Workspace Cleanup (Context manager & Stale-job Janitor)
```

---

## 2. Implemented Security Controls

### 2.1 File Name Sanitization & Path Traversal Prevention
- `sanitize_filename()` strips all path separators (`/`, `\`), relative directory traversal indicators (`..`), null bytes (`\0`), and non-alphanumeric characters.
- Uploaded files are written with internal synthetic filenames: `video_<uuid4_hex[:12]><ext>`. User-provided names are never used for filesystem operations.
- Destination paths are asserted against the canonical absolute path of the session directory.

### 2.2 Magic Byte / Container Signature Verification
- Extension checks are insufficient on their own. `validate_video_magic_bytes()` inspects the first 1024 bytes of the binary stream for container signatures:
  - MP4 / QuickTime: `ftyp`, `moov`, `mdat` at offset 4.
  - Matroska / WebM: EBML ID `\x1a\x45\xdf\xa3`.
  - AVI: `RIFF....AVI ` signature.
- Executables, scripts, HTML files, and text files renamed with `.mp4` extensions are rejected before decoding.

### 2.3 Streaming Uploads & Resource Exhaustion Protection
- Streams are read in 1 MB chunks and abort immediately if the total size exceeds `CLIPMIND_MAX_UPLOAD_MB`. Partially written files are deleted upon violation.
- Frame dimensions are checked against `CLIPMIND_MAX_FRAME_DIM` (default 4096px) to prevent memory allocation denial-of-service (decompression bombs).
- Duration is verified against `CLIPMIND_MAX_DURATION_SEC` (default 3600s).

### 2.4 Ephemeral Isolation & Guaranteed Cleanup
- Every upload creates an isolated workspace: `.clipmind_tmp/<job_id>/`.
- The `JobSession` context manager removes the entire job workspace upon completion or error.
- A background janitor scans and removes orphaned directories older than 2 hours (`CLIPMIND_AUTO_CLEANUP`).
- In Docker, `.clipmind_tmp` is mounted on a `tmpfs` volume with `noexec,nosuid`.

### 2.5 Information Disclosure & Error Sanitization
- `ClipMindError` defines safe, user-friendly error messages.
- Python stack traces, internal filesystem paths, and environment variables are logged to stdout with structured context filters, but are never exposed in the Streamlit UI.

---

## 3. Production Deployment Security Recommendations

For public or multi-tenant deployments:
1. **Authentication & Rate Limiting**: Deploy behind an API Gateway or reverse proxy (e.g. NGINX, Cloudflare) with OAuth2/OIDC and IP rate limiting (e.g., max 5 uploads per IP per minute).
2. **Container Sandbox**: Run Docker with `security_opt: [no-new-privileges:true]` and a read-only root filesystem.
3. **Network Isolation**: Restrict egress network connectivity from the processing containers as video analysis does not require outbound internet access.
