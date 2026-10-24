# -*- coding: utf-8 -*-
"""
Muse Studio - Film Service v2 (sidecar for Muse2API portable)
Pro short-drama pipeline (manifest-driven, like MoneyPrinterTurbo / ShortGPT
and Chinese AI-drama studios):
  character lock happens in Studio (reference sheets + first-frame stills);
  this service does: validate (+anti-duplicate hash gate) -> voice CASTING
  (gender x age matrix, pitch/formant post-processing, per-line loudness)
  -> optional voice cloning (VieNeu-TTS, if installed + reference provided)
  -> concat in script order -> BGM with auto-ducking under dialogue
  -> signature overlay -> verify output.
Binds 127.0.0.1:18621 only.
"""
import asyncio, hashlib, json, os, re, shutil, subprocess, sys, threading, time, unicodedata
import urllib.parse, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 18621
APP_DIR = r"C:\muse2api-test\app\Muse2API_VI_Portable_1.6.8"
MEDIA_DIR = os.path.join(APP_DIR, "data", "media")
FFMPEG = r"C:\muse2api-test\ffmpeg\bin\ffmpeg.exe"
FFPROBE = r"C:\muse2api-test\ffmpeg\bin\ffprobe.exe"
FONT = "C\\:/Windows/Fonts/arial.ttf"
ROOT = r"C:\muse2api-test\film-service"
OUT_DIR = os.path.join(ROOT, "outputs")
JOBS_DIR = os.path.join(ROOT, "jobs")
VOICE_DIR = os.path.join(ROOT, "voices")
MUSIC_DIR = os.path.join(ROOT, "music")
for d in (OUT_DIR, JOBS_DIR, VOICE_DIR, MUSIC_DIR):
    os.makedirs(d, exist_ok=True)

def desktop_dirs():
    home = os.path.expanduser("~")
    cands = [os.path.join(home, "OneDrive", "Máy tính"),
             os.path.join(home, "OneDrive", "Desktop"),
             os.path.join(home, "Desktop")]
    return [d for d in cands if os.path.isdir(d)]

def copy_to_desktop(out_path, fname):
    """Copy a finished film to the Desktop. Returns the dest path or None."""
    for d in desktop_dirs():
        try:
            dest = os.path.join(d, fname)
            if os.path.abspath(dest) != os.path.abspath(out_path):
                shutil.copyfile(out_path, dest)
            return dest
        except Exception:
            continue
    return None

CLONE_HOME = r"C:\muse2api-test\tts-pro"
CLONE_PY = os.path.join(CLONE_HOME, "venv", "Scripts", "python.exe")
CLONE_SCRIPT = os.path.join(CLONE_HOME, "synth_vieneu.py")

# ---- Voice casting matrix: (gender, age) -> synth + post-processing ----
# semi = extra formant/pitch shift in semitones applied to the rendered line
# (this is what separates a child from an adult beyond the TTS pitch knob).
CASTING = {
    ("female", "child"): dict(base="vi-VN-HoaiMyNeural", rate="+8%",  pitch="+55Hz", semi=3.0,  eq=["treble=g=3"], preset="Ngọc Huyền"),
    ("female", "teen"):  dict(base="vi-VN-HoaiMyNeural", rate="+3%",  pitch="+25Hz", semi=1.5,  eq=["treble=g=2"], preset="Trúc Ly"),
    ("female", "adult"): dict(base="vi-VN-HoaiMyNeural", rate="+0%",  pitch="+0Hz",  semi=0.0,  eq=[], preset="Ngọc Linh"),
    ("female", "elder"): dict(base="vi-VN-HoaiMyNeural", rate="-10%", pitch="-30Hz", semi=-2.5, eq=["bass=g=3", "lowpass=f=7000"], preset="Thục Đoan"),
    ("male", "child"):   dict(base="vi-VN-NamMinhNeural", rate="+10%", pitch="+65Hz", semi=4.0, eq=["treble=g=3"], preset="Hải Đăng"),
    ("male", "teen"):    dict(base="vi-VN-NamMinhNeural", rate="+4%",  pitch="+30Hz", semi=2.0, eq=["treble=g=1"], preset="Xuân Vĩnh"),
    ("male", "adult"):   dict(base="vi-VN-NamMinhNeural", rate="+0%",  pitch="-10Hz", semi=0.0, eq=[], preset="Đức Trí"),
    ("male", "elder"):   dict(base="vi-VN-NamMinhNeural", rate="-12%", pitch="-45Hz", semi=-3.0, eq=["bass=g=4", "lowpass=f=6500"], preset="Thiền Tâm Đức"),
}
# Fine-tune presets for the legacy speaker ids of the house film series
LEGACY_PRESET = {"narrator": "Ngọc Linh", "queen": "Kim Thanh", "king": "Thái Sơn"}
LEGACY = {  # speaker ids used by existing scripts -> casting + fine-tune
    "narrator": (("female", "adult"), dict(rate="-5%")),
    "queen":    (("female", "adult"), dict(pitch="-10Hz", semi=-0.5)),
    "female":   (("female", "adult"), dict()),
    "female_warm": (("female", "adult"), dict(pitch="-10Hz", semi=-0.5)),
    "miu":      (("female", "child"), dict()),
    "girl":     (("female", "child"), dict()),
    "king":     (("male", "adult"), dict(rate="-6%", semi=-1.5)),
    "rex":      (("male", "adult"), dict()),
    "male":     (("male", "adult"), dict()),
    "bong":     (("male", "child"), dict()),
    "boy":      (("male", "child"), dict()),
    "grey":     (("male", "elder"), dict()),
    "old":      (("male", "elder"), dict()),
}

def resolve_cast(spec):
    """spec: legacy id string OR {gender, age, rate?, pitch?, semi?} -> cast dict."""
    if isinstance(spec, dict):
        key = (spec.get("gender", "female"), spec.get("age", "adult"))
        cast = dict(CASTING.get(key, CASTING[("female", "adult")]))
        for f in ("rate", "pitch", "semi", "preset"):
            if spec.get(f) is not None:
                cast[f] = spec[f]
        return cast
    sid = str(spec or "narrator")
    key, extra = LEGACY.get(sid, LEGACY["narrator"])
    cast = dict(CASTING[key])
    cast.update(extra)
    if sid in LEGACY_PRESET:
        cast["preset"] = LEGACY_PRESET[sid]
    return cast

def clone_ready():
    return os.path.isfile(CLONE_PY) and os.path.isfile(CLONE_SCRIPT)

JOBS = {}
JOBS_LOCK = threading.Lock()
INBOX_FILE = os.path.join(ROOT, "inbox.json")

def run(cmd, timeout=1800, env_extra=None):
    env = None
    if env_extra:
        env = dict(os.environ); env.update(env_extra)
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return p.returncode, (p.stdout or "") + (p.stderr or "")

def probe_duration(path):
    rc, out = run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                   "-of", "csv=p=0", path], timeout=60)
    try:
        return float(out.strip().splitlines()[0])
    except Exception:
        return 0.0

def probe_streams(path):
    rc, out = run([FFPROBE, "-v", "error", "-show_entries", "stream=codec_type",
                   "-of", "csv=p=0", path], timeout=60)
    return [s.strip() for s in out.splitlines() if s.strip()]

def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def slugify(text):
    text = unicodedata.normalize("NFD", text or "phim")
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.replace("đ", "d").replace("Đ", "D")
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text or "phim"

async def tts_edge(text, cast, out_path):
    import edge_tts
    comm = edge_tts.Communicate(text, cast["base"], rate=cast["rate"], pitch=cast["pitch"])
    await comm.save(out_path)

def post_process(src, cast, work, idx):
    """Pitch/formant shift (age cue) + EQ + per-line loudness -> 48k wav."""
    out_wav = os.path.join(work, f"line-{idx:02d}.wav")
    semi = float(cast.get("semi") or 0)
    filters = []
    if semi:
        factor = 2 ** (semi / 12.0)
        filters.append(f"asetrate=48000*{factor:.5f}")
        filters.append("aresample=48000")
        filters.append(f"atempo={1/factor:.5f}")
    filters += cast.get("eq") or []
    filters.append("loudnorm=I=-16:TP=-2:LRA=11")
    filters.append("aresample=48000")
    rc, out = run([FFMPEG, "-y", "-v", "error", "-i", src,
                   "-af", ",".join(filters), "-ar", "48000", "-ac", "1", out_wav], timeout=300)
    if rc != 0 or not os.path.isfile(out_wav):
        raise RuntimeError(f"Xử lý âm thanh cảnh {idx} lỗi: " + out[-300:])
    return out_wav

def edge_line(text, cast, work, idx):
    raw = os.path.join(work, f"line-{idx:02d}-raw.mp3")
    last_err = None
    for attempt in range(3):
        try:
            asyncio.run(tts_edge(text, cast, raw))
            return raw
        except Exception as e:
            last_err = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Lồng tiếng cảnh {idx} lỗi sau 3 lần thử: {last_err}")

def synth_all(scenes, work, log):
    """Segment-aware dubbing. A scene's dialogue may be a string (legacy) or a
    list of {speaker, line, voice} segments (several speakers per shot). Every
    segment is synthesized (VieNeu batch, edge-tts fallback per segment),
    post-processed with its own cast, and a scene's segments are joined with
    short pauses into one wav. Returns {scene_idx(1-based): wav_path}."""
    plan = []  # (scene_i, seg_j, text, spec, cast)
    for i, sc in enumerate(scenes, 1):
        d = sc.get("dialogue")
        segs = []
        if isinstance(d, str) and d.strip():
            segs = [(d.strip(), sc.get("voice") or "narrator")]
        elif isinstance(d, list):
            for sg in d:
                t = (sg.get("line") or "").strip()
                if t:
                    segs.append((t, sg.get("voice") or sc.get("voice") or "narrator"))
        for j, (text, spec) in enumerate(segs):
            plan.append((i, j, text, spec, resolve_cast(spec)))
    results = {}
    if not plan:
        return results
    raws = {}
    if clone_ready():
        items = []
        for i, j, text, spec, cast in plan:
            raw = os.path.join(work, f"seg-{i:02d}-{j:02d}-raw.wav")
            item = {"text": text, "out": raw}
            ref_key = spec.get("ref") if isinstance(spec, dict) else None
            ref_wav = os.path.join(VOICE_DIR, slugify(ref_key) + ".wav") if ref_key else None
            if ref_wav and os.path.isfile(ref_wav):
                item["ref"] = ref_wav
            else:
                item["voice"] = cast.get("preset")
            items.append(item)
        jobs_file = os.path.join(work, "vieneu_jobs.json")
        with open(jobs_file, "w", encoding="utf-8") as fh:
            json.dump({"items": items}, fh, ensure_ascii=False)
        log(f"🎙 Đang đọc {len(items)} câu bằng VieNeu-TTS (giọng Việt dựng sẵn/clone)…")
        rc, out = run([CLONE_PY, CLONE_SCRIPT, jobs_file], timeout=3600,
                      env_extra={"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
        ok = 0
        for ln in out.splitlines():
            if ln.startswith("OK "):
                p = ln[3:].strip()
                if os.path.isfile(p):
                    raws[p] = True; ok += 1
        log(f"✓ VieNeu đọc xong {ok}/{len(items)} câu")
        if ok == 0:
            tail = [ln for ln in out.splitlines() if ln.strip()][-4:]
            for ln in tail:
                log("  VieNeu: " + ln[:220])
            log("⚠ VieNeu không đọc được câu nào — chuyển sang giọng dự phòng")
    per_scene = {}
    for i, j, text, spec, cast in plan:
        uidx = i * 100 + j
        raw_v = os.path.join(work, f"seg-{i:02d}-{j:02d}-raw.wav")
        srcp = raw_v if raws.get(raw_v) else edge_line(text, cast, work, uidx)
        per_scene.setdefault(i, []).append(post_process(srcp, cast, work, uidx))
    gap = os.path.join(work, "gap.wav")
    run([FFMPEG, "-y", "-v", "error", "-f", "lavfi", "-i",
         "anullsrc=r=48000:cl=mono", "-t", "0.35", gap], timeout=60)
    for i, parts in per_scene.items():
        if len(parts) == 1:
            results[i] = parts[0]
        else:
            lst = os.path.join(work, f"line-{i:02d}-list.txt")
            with open(lst, "w", encoding="utf-8") as fh:
                for n, pp in enumerate(parts):
                    if n:
                        fh.write("file '%s'\n" % gap.replace("\\", "/"))
                    fh.write("file '%s'\n" % pp.replace("\\", "/"))
            out_w = os.path.join(work, f"line-{i:02d}.wav")
            rc, o = run([FFMPEG, "-y", "-v", "error", "-f", "concat", "-safe", "0",
                         "-i", lst, "-c", "copy", out_w], timeout=120)
            results[i] = out_w if (rc == 0 and os.path.isfile(out_w)) else parts[0]
    return results


def job_update(job, **kw):
    with JOBS_LOCK:
        job.update(kw)

def job_log(job, msg):
    with JOBS_LOCK:
        job["log"].append(msg)


def probe_dims(path):
    rc, out = run([FFPROBE, "-v", "error", "-select_streams", "v:0",
                   "-show_entries", "stream=width,height", "-of", "csv=p=0", path], timeout=60)
    try:
        w, h = out.strip().splitlines()[0].split(",")
        return int(w), int(h)
    except Exception:
        return 1280, 720


def gen_music_bed(work, dur, seed, log):
    """Generative warm underscore: chord pads (D-Bm-G-A) + sparse pentatonic
    plucks rendered with ffmpeg aevalsrc. Returns a wav path or None."""
    import random
    rnd = random.Random(seed)
    chords = [(0, [146.83, 220.00, 369.99]), (8, [123.47, 185.00, 293.66]),
              (16, [98.00, 146.83, 246.94]), (24, [110.00, 164.81, 277.18])]
    pad = []
    for s, freqs in chords:
        for f in freqs:
            gate = (f"between(mod(t,32),{s},{s + 8})"
                    f"*min(1,(mod(t,32)-{s})/1.5)*min(1,({s + 8}-mod(t,32))/1.5)")
            pad.append(f"0.30*sin(2*PI*{f}*t)*{gate}")
    notes = [293.66, 329.63, 369.99, 440.00, 493.88, 587.33]
    mel = []
    t = 2.0
    while t < dur - 3:
        f = rnd.choice(notes)
        mel.append(f"(0.42*sin(2*PI*{f}*(t-{t:.2f}))*exp(-2.0*(t-{t:.2f}))*between(t,{t:.2f},{t + 2.5:.2f}))")
        mel.append(f"(0.15*sin(4*PI*{f}*(t-{t:.2f}))*exp(-3.2*(t-{t:.2f}))*between(t,{t:.2f},{t + 2.0:.2f}))")
        t += rnd.uniform(2.6, 4.6)
    pad_expr = "+".join(pad)
    mel_expr = "+".join(mel) if mel else "0"
    out_w = os.path.join(work, "music_bed.wav")
    fc = ("[0:a]volume=0.55[pad];[1:a]volume=0.8[mel];[pad][mel]amix=inputs=2:normalize=0,"
          f"lowpass=f=1500,afade=t=in:st=0:d=2,afade=t=out:st={max(0.0, dur - 3):.2f}:d=3,"
          "aresample=48000[mus]")
    rc, out = run([FFMPEG, "-y", "-v", "error",
                   "-f", "lavfi", "-i", f"aevalsrc=exprs='{pad_expr}|{pad_expr}':s=48000:d={dur:.2f}",
                   "-f", "lavfi", "-i", f"aevalsrc=exprs='{mel_expr}|{mel_expr}':s=48000:d={dur:.2f}",
                   "-filter_complex", fc, "-map", "[mus]", "-ar", "48000", "-ac", "2", out_w],
                  timeout=600)
    if rc != 0 or not os.path.isfile(out_w):
        log("  (nhạc tự sinh lỗi: " + out[-200:] + ")")
        return None
    log("🎵 Đã tự sinh nhạc nền (nền ấm + giai điệu thưa, sẽ tự hạ nhỏ dưới thoại)")
    return out_w


def build_edit(paths, durs, work, title, edit_cfg, log):
    """Cinematic edit: optional title card + xfade/acrossfade chain.
    Returns (merged_path, scene_starts, total_edit). Raises on failure."""
    tdur = float(edit_cfg.get("duration", 0.6))
    trans = edit_cfg.get("transition", "fade")
    if trans not in ("fade", "fadeblack", "dissolve"):
        trans = "fade"
    W, H = probe_dims(paths[0])
    segs = []
    if edit_cfg.get("title", True) and title:
        tp = os.path.join(work, "title.mp4")
        esc = title.replace("'", "").replace(":", "\\:").replace("%", "\\%")
        fc = (f"drawtext=fontfile='{FONT}':text='{esc}':fontsize=46:fontcolor=white:"
              "x=(w-tw)/2:y=(h-th)/2,fade=t=in:st=0:d=0.6,fade=t=out:st=1.6:d=0.6")
        rc, out = run([FFMPEG, "-y", "-v", "error", "-f", "lavfi", "-i",
                       f"color=black:s={W}x{H}:r=30:d=2.2", "-f", "lavfi", "-i",
                       "anullsrc=r=48000:cl=stereo", "-vf", fc, "-t", "2.2",
                       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                       "-shortest", tp], timeout=300)
        if rc == 0 and os.path.isfile(tp):
            segs.append((tp, 2.2))
    for p, d in zip(paths, durs):
        segs.append((p, d))
    n = len(segs)
    starts, acc = [], 0.0
    for j, (p, d) in enumerate(segs):
        starts.append(0.0 if j == 0 else acc - j * tdur)
        acc += d
    total_edit = acc - (n - 1) * tdur
    inputs, parts = [], []
    for j, (p, d) in enumerate(segs):
        inputs += ["-i", p]
        parts.append(f"[{j}:v]scale={W}:{H}:force_original_aspect_ratio=decrease,"
                     f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p[v{j}]")
        parts.append(f"[{j}:a]aresample=48000,aformat=sample_fmts=fltp[a{j}]")
    vcur, acur = "[v0]", "[a0]"
    for j in range(1, n):
        parts.append(f"{vcur}[v{j}]xfade=transition={trans}:duration={tdur}:"
                     f"offset={starts[j]:.3f}[vx{j}]")
        parts.append(f"{acur}[a{j}]acrossfade=d={tdur}[ax{j}]")
        vcur, acur = f"[vx{j}]", f"[ax{j}]"
    merged = os.path.join(work, "edited.mp4")
    rc, out = run([FFMPEG, "-y", "-v", "error"] + inputs +
                  ["-filter_complex", ";".join(parts), "-map", vcur, "-map", acur,
                   "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                   "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", merged],
                  timeout=3600)
    if rc != 0 or not os.path.isfile(merged):
        raise RuntimeError("edit graph lỗi: " + out[-300:])
    return merged, starts[n - len(paths):], total_edit


def assemble_job(job_id, payload):
    job = JOBS[job_id]
    try:
        scenes = payload.get("scenes") or []
        if not scenes:
            raise ValueError("Manifest rỗng: chưa có cảnh nào")
        title = payload.get("title") or "Phim"
        signature = payload.get("signature", "by prompt Thaovy19T")
        bg_volume = float(payload.get("bg_volume", 0.12))
        music = payload.get("music") or {}
        work = os.path.join(JOBS_DIR, job_id)
        os.makedirs(work, exist_ok=True)
        log = lambda m: job_log(job, m)

        # ---- Gate 1: validate + durations + anti-duplicate ----
        job_update(job, stage="Kiểm tra clip đầu vào", pct=5)
        paths, durs, seen = [], [], {}
        for i, sc in enumerate(scenes, 1):
            f = sc.get("file") or ""
            path = f if os.path.isabs(f) else os.path.join(MEDIA_DIR, os.path.basename(f))
            if not os.path.isfile(path):
                raise ValueError(f"Cảnh {i}: không thấy file {f}")
            d = probe_duration(path)
            if d <= 0:
                raise ValueError(f"Cảnh {i}: không đọc được thời lượng của {f}")
            h = sha256_of(path)[:16]
            if h in seen:
                raise ValueError(f"TRÙNG LẶP: cảnh {i} giống hệt cảnh {seen[h]} (cùng hash) — đã chặn, không ghép")
            seen[h] = i
            paths.append(path); durs.append(d)
        total = sum(durs)
        log(f"✓ {len(paths)} clip hợp lệ, tổng {total:.1f}s, không trùng lặp")

        # ---- Stage 2: casting TTS per line (VieNeu presets/clone, edge fallback) ----
        job_update(job, stage="Lồng tiếng theo casting (giới tính + tuổi)", pct=20)
        by_idx = synth_all(scenes, work, log)
        wavs = []
        for i, sc in enumerate(scenes, 1):
            w = by_idx.get(i)
            if w:
                ld = probe_duration(w)
                if ld > durs[i-1] + 2:
                    log(f"⚠ Cảnh {i}: thoại {ld:.1f}s dài hơn cảnh {durs[i-1]:.1f}s — sẽ tràn nhẹ sang cảnh sau")
            wavs.append(w)
        n_lines = sum(1 for m in wavs if m)
        log(f"✓ Đã lồng tiếng {n_lines} câu thoại (casting theo giới tính + độ tuổi)")

        # ---- Stage 3: edit (cuts + cinematic transitions + title card) ----
        job_update(job, stage="Dựng phim: cắt + chuyển cảnh điện ảnh", pct=45)
        edit_cfg = payload.get("edit") or {}
        starts = []
        _acc = 0.0
        for d in durs:
            starts.append(_acc); _acc += d
        try:
            merged, starts, total = build_edit(paths, durs, work, title, edit_cfg, log)
            log(f"✓ Dựng điện ảnh xong: {len(paths)} cảnh, chuyển cảnh "
                f"{edit_cfg.get('transition', 'fade')} {float(edit_cfg.get('duration', 0.6)):.1f}s, "
                f"thẻ tiêu đề, tổng {total:.1f}s")
        except Exception as e:
            log("⚠ Dựng nâng cao lỗi (" + str(e)[:160] + ") — nối thẳng dự phòng")
            listfile = os.path.join(work, "concat.txt")
            with open(listfile, "w", encoding="utf-8") as fh:
                for p in paths:
                    fh.write("file '%s'\n" % p.replace("\\", "/"))
            merged = os.path.join(work, "merged.mp4")
            rc, out = run([FFMPEG, "-y", "-v", "error", "-f", "concat", "-safe", "0",
                           "-i", listfile, "-c", "copy", merged])
            if rc != 0 or not os.path.isfile(merged):
                raise RuntimeError("ffmpeg concat lỗi: " + out[-400:])

        # ---- Stage 4: mix (ducking BGM) + signature + encode ----
        job_update(job, stage="Trộn tiếng + nhạc nền + chữ ký", pct=65)
        inputs = ["-i", merged]
        for w in wavs:
            if w: inputs += ["-i", w]
        music_path = None
        if music.get("file"):
            cand = os.path.join(MUSIC_DIR, os.path.basename(music["file"]))
            if os.path.isfile(cand):
                music_path = cand
                inputs += ["-stream_loop", "-1", "-i", cand]
            else:
                log("⚠ Không thấy file nhạc nền — bỏ qua nhạc")
        if not music_path and music.get("auto"):
            try:
                bed = gen_music_bed(work, total, abs(hash(title)) % 100000, log)
                if bed:
                    music_path = bed
                    inputs += ["-i", bed]
            except Exception as e:
                log("⚠ Tự sinh nhạc nền lỗi: " + str(e)[:120])
        has_music = bool(music_path)
        parts = [f"[0:a]volume={bg_volume}[bg]"]
        k = 0
        for i, w in enumerate(wavs):
            if not w: continue
            k += 1
            delay = int(starts[i] * 1000) + 300
            parts.append(f"[{k}:a]adelay={delay}|{delay}[d{k}]")
        if k:
            parts.append("".join(f"[d{j}]" for j in range(1, k + 1)) +
                         f"amix=inputs={k}:normalize=0[dlgpre]")
            if has_music:
                parts.append("[dlgpre]asplit=2[dlg][dlgsc]")
            else:
                parts.append("[dlgpre]anull[dlg]")
        else:
            parts.append(f"anullsrc=r=48000:cl=mono,atrim=0:{total:.2f},asetpts=PTS-STARTPTS[dlg]")
            if has_music:
                parts.append(f"anullsrc=r=48000:cl=mono,atrim=0:{total:.2f},asetpts=PTS-STARTPTS[dlgsc]")
        mix_ins = ["[bg]", "[dlg]"]
        if music_path:
            mi = k + 1
            mvol = max(0.0, min(1.0, float(music.get("volume", 0.4))))
            fade_out_st = max(0.0, total - 2.0)
            parts.append(f"[{mi}:a]atrim=0:{total:.2f},asetpts=PTS-STARTPTS,"
                         f"volume={mvol:.2f},afade=t=in:st=0:d=2,"
                         f"afade=t=out:st={fade_out_st:.2f}:d=2[mus0]")
            parts.append("[mus0][dlgsc]sidechaincompress=threshold=0.03:ratio=10:"
                         "attack=150:release=900:makeup=1[musd]")
            mix_ins.append("[musd]")
            log("✓ Nhạc nền có tự động hạ nhỏ khi có thoại (ducking)")
        parts.append("".join(mix_ins) +
                     f"amix=inputs={len(mix_ins)}:normalize=0,"
                     "loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
        fout = max(0.0, total - 1.4)
        if signature:
            esc = signature.replace("'", "").replace(":", "\\:")
            parts.append(f"[0:v]drawtext=fontfile='{FONT}':text='{esc}':fontsize=22:"
                         "fontcolor=white@0.85:borderw=1:bordercolor=black@0.5:"
                         f"x=w-tw-18:y=h-th-14,fade=t=in:st=0:d=0.7,fade=t=out:st={fout:.2f}:d=1.4[vout]")
        else:
            parts.append(f"[0:v]fade=t=in:st=0:d=0.7,fade=t=out:st={fout:.2f}:d=1.4[vout]")
        fname = f"film_{slugify(title)}.mp4"
        out_path = os.path.join(OUT_DIR, fname)
        rc, out = run([FFMPEG, "-y", "-v", "error"] + inputs +
                      ["-filter_complex", ";".join(parts), "-map", "[vout]", "-map", "[aout]",
                       "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                       "-movflags", "+faststart", out_path], timeout=3600)
        if rc != 0 or not os.path.isfile(out_path):
            raise RuntimeError("ffmpeg xuất phim lỗi: " + out[-400:])

        # ---- Gate 5: verify ----
        job_update(job, stage="Kiểm tra phim đầu ra", pct=92)
        fd = probe_duration(out_path)
        streams = probe_streams(out_path)
        if "video" not in streams or "audio" not in streams:
            raise RuntimeError(f"Phim thiếu luồng: {streams}")
        if abs(fd - total) > 2.0:
            raise RuntimeError(f"Lệch thời lượng: phim {fd:.1f}s vs tổng clip {total:.1f}s")
        log(f"✓ Phim hoàn chỉnh: {fd:.1f}s, đủ hình + tiếng, âm lượng chuẩn phát sóng")
        desktop = copy_to_desktop(out_path, fname)
        if desktop:
            log(f"⬇ Đã xuất ra Máy tính: {desktop}")
        else:
            log("⚠ Không tìm thấy thư mục Máy tính để xuất bản sao — phim vẫn ở outputs/")
        job_update(job, status="done", stage="Hoàn thành", pct=100,
                   result={"file": fname, "seconds": round(fd, 1),
                           "size": os.path.getsize(out_path),
                           "desktop": desktop,
                           "url": f"http://127.0.0.1:{PORT}/file/{fname}"})
    except Exception as e:
        job_log(job, "✗ " + str(e))
        job_update(job, status="failed", stage="Lỗi", error=str(e))

def translate_gtx(texts):
    out = []
    for t in texts:
        try:
            q = urllib.parse.urlencode({"client": "gtx", "sl": "auto", "tl": "en",
                                        "dt": "t", "q": t})
            req = urllib.request.Request("https://translate.googleapis.com/translate_a/single?" + q,
                                         headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read().decode("utf-8"))
            out.append("".join(seg[0] for seg in data[0] if seg and seg[0]))
        except Exception:
            out.append(t)
    return out

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Filename")
        self.end_headers()

    def do_GET(self):
        if self.path == "/inbox":
            data = {"items": []}
            if os.path.isfile(INBOX_FILE):
                try:
                    with open(INBOX_FILE, encoding="utf-8") as fh:
                        data = json.load(fh)
                except Exception:
                    pass
            self._send(200, data); return
        if self.path == "/outputs":
            items = []
            try:
                names = [n for n in os.listdir(OUT_DIR) if n.lower().endswith(".mp4")]
                names.sort(key=lambda n: os.path.getmtime(os.path.join(OUT_DIR, n)), reverse=True)
                desks = desktop_dirs()
                # A Desktop copy may carry a friendly name (e.g. Ep1 was saved
                # as Nha-Minh-Con-Noi-Chuyen-Tap-1.mp4) — same byte size counts.
                desk_sizes = set()
                for d in desks:
                    try:
                        for f in os.listdir(d):
                            if f.lower().endswith(".mp4"):
                                desk_sizes.add(os.path.getsize(os.path.join(d, f)))
                    except Exception:
                        pass
                for n in names:
                    p = os.path.join(OUT_DIR, n)
                    sz = os.path.getsize(p)
                    items.append({"file": n, "size": sz,
                                  "seconds": round(probe_duration(p), 1),
                                  "mtime": os.path.getmtime(p),
                                  "on_desktop": any(os.path.isfile(os.path.join(d, n)) for d in desks) or sz in desk_sizes,
                                  "url": f"http://127.0.0.1:{PORT}/file/{n}"})
            except Exception as e:
                items = []
            self._send(200, {"items": items}); return
        if self.path == "/health":
            self._send(200, {"ok": True, "ffmpeg": os.path.isfile(FFMPEG),
                             "media_dir": MEDIA_DIR, "clone_ready": clone_ready(),
                             "casting": [f"{g}-{a}" for (g, a) in CASTING],
                             "voices": list(VOICES_KEYS)})
        elif self.path.startswith("/job/"):
            jid = self.path.split("/job/")[1].split("?")[0]
            with JOBS_LOCK:
                job = JOBS.get(jid)
            if job: self._send(200, job)
            else: self._send(404, {"error": "job not found"})
        elif self.path.startswith("/file/"):
            name = os.path.basename(urllib.parse.unquote(self.path.split("/file/")[1]))
            path = os.path.join(OUT_DIR, name)
            if not os.path.isfile(path):
                self._send(404, {"error": "file not found"}); return
            size = os.path.getsize(path)
            rng = self.headers.get("Range")
            start, end, code = 0, size - 1, 200
            if rng and rng.startswith("bytes="):
                try:
                    s, e = rng[6:].split("-", 1)
                    start = int(s) if s else 0
                    end = int(e) if e else size - 1
                    code = 206
                except Exception:
                    pass
            self.send_response(code)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(end - start + 1))
            if code == 206:
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.end_headers()
            with open(path, "rb") as fh:
                fh.seek(start)
                remaining = end - start + 1
                while remaining > 0:
                    chunk = fh.read(min(1 << 20, remaining))
                    if not chunk: break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b""
        if self.path.startswith("/music") or self.path.startswith("/voice-ref"):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            name = os.path.basename((qs.get("name") or ["upload.bin"])[0])
            if self.path.startswith("/music"):
                dest = os.path.join(MUSIC_DIR, name)
                with open(dest, "wb") as fh: fh.write(raw)
                self._send(200, {"file": name, "size": len(raw)})
            else:
                dest = os.path.join(VOICE_DIR, slugify(name) + "-raw")
                with open(dest, "wb") as fh: fh.write(raw)
                wav = os.path.join(VOICE_DIR, slugify(name) + ".wav")
                rc, out = run([FFMPEG, "-y", "-v", "error", "-i", dest,
                               "-ar", "16000", "-ac", "1", wav], timeout=120)
                if rc != 0:
                    self._send(400, {"error": "Không đọc được file giọng mẫu: " + out[-200:]})
                else:
                    self._send(200, {"file": os.path.basename(wav), "clone_ready": clone_ready()})
            return
        try:
            text = None
            for enc in ("utf-8-sig", "utf-16", "latin-1"):
                try:
                    text = raw.decode(enc); break
                except Exception:
                    continue
            payload = json.loads(text or "{}")
        except Exception as e:
            self._send(400, {"error": f"bad json: {e}"}); return
        if self.path == "/inbox":
            items = payload.get("items") or []
            with open(INBOX_FILE, "w", encoding="utf-8") as fh:
                json.dump({"items": items}, fh, ensure_ascii=False)
            self._send(200, {"ok": True, "count": len(items)})
        elif self.path == "/translate":
            texts = payload.get("texts") or []
            self._send(200, {"translations": translate_gtx([str(t) for t in texts])})
        elif self.path == "/assemble":
            jid = "job_" + hashlib.md5(f"{time.time()}".encode()).hexdigest()[:12]
            with JOBS_LOCK:
                JOBS[jid] = {"id": jid, "status": "running", "stage": "Khởi tạo",
                             "pct": 1, "log": [], "result": None, "error": None}
            threading.Thread(target=assemble_job, args=(jid, payload), daemon=True).start()
            self._send(202, {"job_id": jid})
        else:
            self._send(404, {"error": "not found"})

VOICES_KEYS = list(LEGACY.keys())

if __name__ == "__main__":
    print(f"Film service v2 on http://127.0.0.1:{PORT} (clone_ready={clone_ready()})", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
