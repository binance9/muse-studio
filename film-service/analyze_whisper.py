"""Whisper analysis helper for the Studio chat (run with the tts-pro venv python).

Usage: python analyze_whisper.py <media_path>
Prints ONE JSON line: {language, probability, text, segments:[{start,end,text}]}
Uses faster-whisper 'base' on CPU (already cached on this PC from earlier
transcription tests). No GPU, no network, no cost.
"""
import sys, os, json

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

def main():
    path = sys.argv[1]
    from faster_whisper import WhisperModel
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(path, language="vi", vad_filter=True)
    segs = [{"start": round(s.start, 1), "end": round(s.end, 1),
             "text": s.text.strip()} for s in segments]
    out = {"language": info.language,
           "probability": round(float(info.language_probability), 3),
           "text": " ".join(s["text"] for s in segs),
           "segments": segs}
    sys.stdout.write(json.dumps(out, ensure_ascii=False))

if __name__ == "__main__":
    main()
