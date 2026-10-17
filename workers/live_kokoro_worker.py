#!/usr/bin/env python3
"""Local-only, warm Kokoro worker. Text and WAVs stay in memory."""

from __future__ import annotations

import argparse
import base64
import contextlib
import io
import json
import os
import sys
import wave

from kokoro_worker import portable_espeak_data


def serve(model: str, voices: str) -> None:
    output = sys.stdout
    # Libraries may print diagnostics; stdout is reserved for the private protocol.
    with contextlib.redirect_stdout(sys.stderr):
        import numpy as np
        import onnxruntime as rt
        from kokoro_onnx import Kokoro
        from kokoro_onnx.config import EspeakConfig

        options = rt.SessionOptions()
        options.intra_op_num_threads = max(1, min(4, os.cpu_count() or 2))
        options.inter_op_num_threads = 1
        options.add_session_config_entry("session.intra_op.allow_spinning", "0")
        session = rt.InferenceSession(
            model, sess_options=options, providers=["CPUExecutionProvider"]
        )
        with portable_espeak_data() as data:
            engine = Kokoro.from_session(
                session, voices, espeak_config=EspeakConfig(data_path=data)
            )
            while line := sys.stdin.readline(8193):
                if len(line) > 8192:
                    break
                try:
                    request = json.loads(line)
                    samples, rate = engine.create(
                        request["text"],
                        voice=request["voice"],
                        speed=1.0,
                        lang=request["language"],
                    )
                    pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16)
                    buffer = io.BytesIO()
                    with wave.open(buffer, "wb") as audio:
                        audio.setnchannels(1)
                        audio.setsampwidth(2)
                        audio.setframerate(rate)
                        audio.writeframes(pcm.tobytes())
                    response = {"audio": base64.b64encode(buffer.getvalue()).decode()}
                except Exception:
                    # Do not echo text, paths or provider diagnostics to the UI.
                    response = {"error": "Local speech generation failed"}
                output.write(json.dumps(response) + "\n")
                output.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--voices", required=True)
    args = parser.parse_args()
    serve(args.model, args.voices)
