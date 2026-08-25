#!/usr/bin/env python3
"""Probe round 2: find the correct way to pass reference audio."""
import asyncio, base64, json, time, wave
import numpy as np
from scipy.signal import resample_poly
import websockets

WS_URL = "wss://minicpmo45.modelbest.cn/v1/realtime?mode=chat"


def load_ref(seconds=None, dtype="f32", sr_out=16000):
    with wave.open("hr/Kuon_b-1_part01.wav", "rb") as w:
        sr = w.getframerate()
        raw = w.readframes(w.getnframes())
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    y = resample_poly(x, sr_out, sr) if sr != sr_out else x.astype(np.float32)
    if seconds:
        y = y[: int(sr_out * seconds)]
    if dtype == "f32":
        return base64.b64encode(y.astype(np.float32).tobytes()).decode()
    return base64.b64encode((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()).decode()


async def probe(name, init_payload=None, tts_cfg=None, max_tok=256):
    print(f"--- {name}", flush=True)
    t0 = time.perf_counter()
    try:
        async with websockets.connect(WS_URL, max_size=100 * 1024 * 1024,
                                      open_timeout=30, ping_interval=20,
                                      ping_timeout=120) as ws:
            while True:
                evt = json.loads(await asyncio.wait_for(ws.recv(), timeout=60))
                if evt.get("type") == "session.queue_done":
                    break
            await ws.send(json.dumps({"type": "session.init",
                                      "payload": init_payload or {}}))
            while True:
                evt = json.loads(await asyncio.wait_for(ws.recv(), timeout=60))
                if evt.get("type") == "session.created":
                    break
                if evt.get("type") == "error":
                    print(f"  init error: {evt}", flush=True)
                    return False
            await ws.send(json.dumps({
                "type": "input.append",
                "input": {
                    "messages": [{"role": "user",
                                  "content": "Say exactly: Hello there, this is a test."}],
                    "streaming": True,
                    "generation": {"max_new_tokens": max_tok},
                    "use_tts_template": True,
                    "enable_thinking": False,
                    "tts": tts_cfg or {"enabled": True},
                },
            }))
            n_audio = 0
            while True:
                evt = json.loads(await asyncio.wait_for(ws.recv(), timeout=300))
                et = evt.get("type")
                if et == "response.output.delta":
                    if evt.get("kind") == "audio":
                        n_audio += 1
                        if n_audio == 1:
                            print(f"  first audio at {time.perf_counter()-t0:.1f}s",
                                  flush=True)
                elif et == "response.done":
                    print(f"  done at {time.perf_counter()-t0:.1f}s "
                          f"audio_deltas={n_audio} done.audio={bool(evt.get('audio'))}",
                          flush=True)
                    break
                elif et == "error":
                    print(f"  error event: {str(evt)[:200]}", flush=True)
                    return False
            await ws.send(json.dumps({"type": "session.close", "reason": "turn_done"}))
        ok = n_audio > 0
        print(f"  RESULT {'AUDIO_OK' if ok else 'NO_AUDIO'}", flush=True)
        return ok
    except Exception as e:
        print(f"  FAILED after {time.perf_counter()-t0:.1f}s: {e}", flush=True)
        return False


async def main():
    r = {}
    # find max usable inline reference length (float32)
    for secs in (4, 6, 8):
        key = f"inline_{secs}s_f32"
        r[key] = await probe(
            f"inline tts.ref_audio_data {secs}s float32",
            tts_cfg={"enabled": True, "ref_audio_data": load_ref(secs)})
        if not r[key]:
            break
    print(json.dumps(r, indent=2), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
