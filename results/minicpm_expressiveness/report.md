# MiniCPM-o 4.5 Expressiveness Test — Technical Report

## Setup

| Field | Value |
|---|---|
| Model | MiniCPM-O-4.5-9B |
| API endpoint | `wss://minicpmo45.modelbest.cn/v1/realtime?mode=chat` |
| Generation mode | Realtime WebSocket, chat mode (turn-based), `tts.enabled=true`, `streaming=true`, `use_tts_template=true` |
| Reference audio file | `hr/Kuon_b-1_part01.wav` |
| Reference source duration | 54.45 s |
| Reference source format | mono, 48 kHz, 16-bit PCM |
| Reference actually sent | first 8.0 s only (16 kHz, 32-bit float PCM, base64) |
| Reference truncation reason | The public endpoint closes sessions with a `1011 (internal error) keepalive ping timeout` when `tts.ref_audio_data` exceeds ~8 s, suggesting a server-side turn-time budget of roughly 42 s; a 54 s reference pushes the session past this limit. |
| Output sample rate | 24 kHz mono float32 PCM (saved as 16-bit int PCM WAV) |
| Authentication | None required (public endpoint, no `Authorization` header used) |
| System prompts | Persona prompt (Sci-Fi VTuber personality) sent as `role: system` in `messages`; Vocal-style prompt sent as second `role: system` in `messages` |
| Test sentence delivery | Wrapped as `role: user` with instruction: _"Say this line out loud, exactly as written, in character. Do not add any other words."_ |
| Max retries per test | 2 (one test needed 1 retry) |
| Dependencies | `websockets`, `numpy`, `scipy` |

## API Issues Discovered

1. **Reference audio length limit (~8 s)** — The official documentation does not state a maximum length for `tts.ref_audio_data`. Sending ≥10 s of reference audio consistently caused the server to terminate the WebSocket session with code `1011` ("keepalive ping timeout") after ~42 s, even with client keepalive pings enabled (`ping_interval=20, ping_timeout=120`). Reducing the reference to ≤8 s eliminated the issue entirely.

2. **Duplicate text in streaming deltas** — Every `response.done` event contained the full text as a second duplicate copy (e.g. `"…"` repeated twice). This is a server-side bug in the streaming text accumulation; it does not affect the audio.

3. **No `voice.*` init fields in chat mode** — `session.init` payload fields `voice.ref_audio_base64` and `voice.tts_ref_audio_base64` (documented for video/audio full-duplex modes) are **not accepted** in chat mode; they also triggered the same ~42 s keepalive timeout. Only `tts.ref_audio_data` inside `input.append` works.

4. **`use_tts_template: true` required** — Without `use_tts_template`, audio generation sometimes produced only text with no audio deltas.

## Results

| Test | Status | Audio Duration (s) | TTFA (s) | Total Time (s) | Retries | Output File |
|---|---|---|---|---|---|---|
| Excited | success | 4.44 | 29.65 | 32.79 | 0 | `01_excited.wav` |
| Annoyed | success | 7.48 | 37.27 | 42.19 | 0 | `02_annoyed.wav` |
| Soft / Mischievous | success | 5.32 | 37.58 | 41.17 | 0 | `03_soft_mischievous.wav` |
| Panic | success | 5.24 | 40.22 | 43.79 | 0 | `04_panic.wav` |
| Sad / Soft | success | 5.20 | 25.00 | 28.29 | 1 | `05_sad_soft.wav` |
| Sarcastic | success | 7.32 | 30.40 | 35.52 | 0 | `06_sarcastic.wav` |
| Hype | success | 3.96 | 35.94 | 40.31 | 0 | `07_hype.wav` |
| Laughing | success | 6.12 | 32.35 | 36.30 | 0 | `08_laughing.wav` |
| Whisper | success | 5.00 | 39.65 | 43.78 | 1 | `09_whisper.wav` |
| Rapid Emotion Change | success | 5.64 | 30.72 | 34.41 | 0 | `10_rapid_emotion_change.wav` |

### Summary

| Metric | Value |
|---|---|
| Tests succeeded | **10 / 10** |
| Mean audio duration | 5.57 s |
| Min audio duration | 3.96 s (Hype) |
| Max audio duration | 7.48 s (Annoyed) |
| Mean TTFA | 33.88 s |
| Mean total time | 37.86 s |
| Total wall-clock time (all 10) | ~378 s |

## File Listing

All generated files are saved under `results/minicpm_expressiveness/`:

```
results/minicpm_expressiveness/
├── 01_excited.wav            (213 KB)
├── 02_annoyed.wav            (359 KB)
├── 03_soft_mischievous.wav   (255 KB)
├── 04_panic.wav              (251 KB)
├── 05_sad_soft.wav           (249 KB)
├── 06_sarcastic.wav          (351 KB)
├── 07_hype.wav               (190 KB)
├── 08_laughing.wav           (295 KB)
├── 09_whisper.wav            (241 KB)
├── 10_rapid_emotion_change.wav (274 KB)
└── report.md                 (this file)
```

## Script Used

The generation script is at `scripts/minicpm_expressiveness_test.py`. It supports resume: re-running it skips any test whose WAV was already successfully generated.

---

*Report generated automatically. No subjective audio-quality judgments are included.*
