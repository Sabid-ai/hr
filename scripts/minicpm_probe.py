#!/usr/bin/env python3
"""Probe MiniCPM-o realtime chat mode to find a working TTS config."""
import asyncio, base64, json, os, time, wave
import numpy as np
from scipy.signal import resample_poly
import websockets

WS_URL = "wss://minicpmo45.modelbest.cn/v1/realtime?mode=chat"


def load_ref(seconds=None):
    with wave.open("hr/Kuon_b-1_part01.wav", "rb") as w:
        sr = w.getframerate()
        raw = w.readframes(w.getnframes())
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    y = resample_poly(x, 1, 3)
    if seconds:
        y = y[: int(16000 * seconds)]
    return base64.b64encode(y.astype(np.float32).tobytes()).decode()


async def probe(name, ref_seconds=None, streaming=True, tts=True, max_tok=256):
    print(f"--- probe: {name} (ref={ref_seconds}s streaming={streaming} tts={tts})",
          flush=True)
    t0 = time.perf_counter()
    try:
        async with websockets.connect(
            WS_URL, max_size=100 * 1024 * 1024, open_timeout=30,
            ping_interval=20, ping_timeout=120,
        ) as ws:
            while True:
                evt = json.loads(await asyncio.wait_for(ws.recv(), timeout=60))
                if evt.get("type") == "session.queue_done":
                    break
            await ws.send(json.dumps({"type": "session.init", "payload": {}}))
            while True:
                evt = json.loads(await asyncio.wait_for(ws.recv(), timeout=60))
                if evt.get("type") == "session.created":
                    break
            payload = {
                "type": "input.append",
                "input": {
                    "messages": [
                        {"role": "user", "content": "Say exactly: Hello there, this is a test."}
                    ],
                    "streaming": streaming,
                    "generation": {"max_new_tokens": max_tok},
                    "use_tts_template": True,
                    "enable_thinking": False,
                    "tts": {"enabled": tts},
                },
            }
            if ref_seconds:
                payload["input"]["tts"]["ref_audio_data"] = load_ref(ref_seconds)
            await ws.send(json.dumps(payload))
            n_audio = 0
            n_text = 0
            while True:
                evt = json.loads(await asyncio.wait_for(ws.recv(), timeout=300))
                et = evt.get("type")
                if et == "response.output.delta":
                    k = evt.get("kind")
                    if k == "audio":
                        n_audio += 1
                        if n_audio == 1:
                            print(f"  first audio delta at "
                                  f"{time.perf_counter()-t0:.1f}s", flush=True)
                    elif k == "text":
                        n_text += 1
                elif et == "response.done":
                    has_a = bool(evt.get("audio"))
                    print(f"  done at {time.perf_counter()-t0:.1f}s "
                          f"deltas(audio={n_audio},text={n_text}) "
                          f"done.audio={has_a} text={str(evt.get('text'))[:60]}",
                          flush=True)
                    break
                elif et == "error":
                    print(f"  server error event: {evt}", flush=True)
                    return False
            await ws.send(json.dumps({"type": "session.close", "reason": "turn_done"}))
        print(f"  RESULT {'AUDIO_OK' if n_audio else ('NO_AUDIO' if tts else 'TEXT_ONLY')}", flush=True)
        return True
    except Exception as e:
        print(f"  FAILED after {time.perf_counter()-t0:.1f}s: {e}", flush=True)
        return False


async def main():
    results = {}
    results["A_no_tts"] = await probe("no tts", tts=False)
    if not results["A_no_tts"]:
        print("Chat itself failing — stop here.")
        return
    ok = await probe("tts stream no ref")
    results["B_tts_stream_noref"] = ok
    if not ok:
        results["C_tts_nonstream_noref"] = await probe("tts non-stream no ref",
                                                       streaming=False)
        ok = results.get("C_tts_nonstream_noref", False)
    if not ok:
        print("TTS failing even without reference — stop here.")
        return
    results["D_tts_stream_ref10s"] = await probe("tts stream ref 10s", ref_seconds=10)
    if not results["D_tts_stream_ref10s"]:
        results["E_tts_nonstream_ref10s"] = await probe("tts non-stream ref 10s",
                                                        ref_seconds=10, streaming=False)
    print(json.dumps(results, indent=2), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
