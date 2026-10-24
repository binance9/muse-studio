# -*- coding: utf-8 -*-
"""Batch Vietnamese TTS via VieNeu-TTS v3 Turbo (runs in the tts-pro venv).
Usage: python synth_vieneu.py jobs.json
jobs.json: {"items": [{"text": "...", "voice": "<preset name>", "out": "path.wav"},
                      {"text": "...", "ref": "ref.wav", "out": "path.wav"}]}
Prints one line per item: OK <out> / ERR <out> <message>. Model loads once.
"""
import json, sys, os

def main():
    jobs = json.load(open(sys.argv[1], encoding="utf-8"))
    # Workaround: HF cache stores files as symlinks into blob dirs, and newer
    # onnxruntime rejects external .data files that resolve outside the model
    # folder. Dereference the codec snapshot into a real local folder.
    try:
        import pathlib, shutil
        from vieneu._v3_turbo_engine import onnx_runtime_lite as _E
        _orig_fetch = _E.OnnxV3LiteEngine._fetch
        def _deref_fetch(repo, files, subfolder=None):
            p = pathlib.Path(_orig_fetch(repo, files, subfolder))
            dest = pathlib.Path(r"C:\muse2api-test\tts-pro\codec_local")
            dest.mkdir(parents=True, exist_ok=True)
            for f in p.iterdir():
                if f.is_file():
                    t = dest / f.name
                    if (not t.exists()) or t.stat().st_size != f.stat().st_size:
                        shutil.copyfile(f, t)
            return dest
        _E.OnnxV3LiteEngine._fetch = staticmethod(_deref_fetch)
    except Exception as e:
        print("PATCH_SKIP " + str(e)[:150], flush=True)
    from vieneu import Vieneu
    model_dir = r"C:\muse2api-test\tts-pro\model"
    onnx_dir = os.path.join(model_dir, "onnx_update")
    if os.path.isdir(onnx_dir):
        tts = Vieneu(mode="v3turbo", backbone_repo=model_dir, onnx_dir=onnx_dir)
    else:
        tts = Vieneu(mode="v3turbo")
    print("MODEL_READY", flush=True)
    for it in jobs["items"]:
        try:
            if it.get("ref"):
                wav = tts.infer(it["text"], ref_audio=it["ref"])
            else:
                wav = tts.infer(it["text"], voice=it.get("voice") or None)
            tts.save(wav, it["out"])
            print("OK " + it["out"], flush=True)
        except Exception as e:
            print("ERR " + it["out"] + " " + str(e)[:200], flush=True)
    tts.close()

if __name__ == "__main__":
    main()
