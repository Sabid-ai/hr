# MiniCPM-o 4.5 Expressiveness Test — Technical Report

## Setup

| Field | Value |
|---|---|
| Model | MiniCPM-O-4.5-9B |
| API endpoint | `wss://minicpmo45.modelbest.cn/v1/realtime?mode=chat` |
| Generation mode | Realtime WebSocket, chat mode (turn-based), `tts.enabled=true`, `streaming=true`, `use_tts_template=true` |
| Reference audio file | `Kuon_b-1_part01 - segment 2.mp3` |
| Reference source duration | 7.52 s |
| Reference source format | mono, 44.1 kHz, 16-bit (MP3 → 16 kHz mono WAV via ffmpeg) |
| Reference actually sent | 7.52 s (16 kHz, 32-bit float PCM, base64) |
| Output sample rate | 24 kHz mono float32 PCM (saved as 16-bit int PCM WAV) |
| Authentication | None required (public endpoint) |
| System prompts | Persona prompt (Sci-Fi VTuber personality) + Vocal-style prompt sent as `role: system` in `messages` |
| Test sentence delivery | Wrapped as `role: user` with instruction: _"Say this line out loud, exactly as written, in character. Do not add any other words."_ |
| Max retries per test | 2 |

## Results Summary

| # | Test | Status | Audio Duration | TTFA | Total Time |
|---|---|---|---|---|---|
| 01 | Excited | ✅ | 4.16s | 12.59s | 15.97s |
| 02 | Annoyed | ✅ | 5.76s | 8.57s | 12.36s |
| 03 | Soft / Mischievous | ✅ | 6.64s | 17.30s | 38.83s |
| 04 | Panic | ✅ | 4.48s | 21.66s | 27.27s |
| 05 | Sad / Soft | ✅ | 4.84s | 23.53s | 29.69s |
| 06 | Sarcastic | ✅ | 7.36s | 29.32s | 36.16s |
| 07 | Hype | ✅ | 4.56s | 15.28s | 20.53s |
| 08 | Laughing | ✅ | 6.04s | 29.62s | 34.86s |
| 09 | Whisper | ✅ | 4.76s | 25.82s | 29.90s |
| 10 | Rapid Emotion Change | ✅ | 6.40s | 17.61s | 21.88s |

**Success rate: 10/10 (100%)**

## Aggregate Statistics

| Metric | Min | Max | Avg |
|---|---|---|---|
| Audio Duration | 4.16s | 7.36s | 5.50s |
| Time to First Audio (TTFA) | 8.57s | 29.62s | 20.13s |
| Total Generation Time | 12.36s | 38.83s | 26.74s |

## Generated Audio Files

All files are in `results/minicpm_expressiveness/`:

- `01_excited.wav` — High energy, bright delivery
- `02_annoyed.wav` — Sharp, emphatic tone
- `03_soft_mischievous.wav` — Quiet, cute, conspiratorial
- `04_panic.wav` — Urgent, fast-paced panic
- `05_sad_soft.wav` — Gentle, touched, emotional
- `06_sarcastic.wav` — Dry, exaggerated sarcasm
- `07_hype.wav` — Maximum streamer hype energy
- `08_laughing.wav` — Genuine laughter delivery
- `09_whisper.wav` — Hushed, secretive whisper
- `10_rapid_emotion_change.wav` — Multi-emotion transition

## Files in Repository

- `Kuon_b-1_part01 - segment 2.mp3` — Original reference voice audio
- `.ref_converted_tmp.wav` — Reference audio converted to 16kHz mono WAV
- `scripts/minicpm_expressiveness_test.py` — Test script
- `results/minicpm_expressiveness/` — All generated WAVs + metrics
