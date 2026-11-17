import os
import re
import asyncio
import subprocess
import importlib.util
import numpy as np
import edge_tts
import imageio_ffmpeg
from PIL import ImageDraw
from moviepy import VideoClip, AudioFileClip, AudioArrayClip, concatenate_audioclips

def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

vis = load_mod("ve", "1_visual_engine.py")
demo = load_mod("dr", "2_demo_renderer.py")
data = load_mod("pd", "3_presentation_data.py")

VOICE = "zh-TW-HsiaoChenNeural"
RATE = "-12%"
FPS = 12
ASS_HEADER = """[Script Info]
Title: VOC_Sentry 20min Cyber Presentation
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft JhengHei,34,&H0000FFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,3,2,0,2,20,20,25,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def interp_mouse(path, prog):
    if len(path) < 2:
        return path.__getitem__(0)
    segs = len(path) - 1
    sc = prog * segs
    idx = min(int(sc), segs - 1)
    lt = sc - idx
    st = lt * lt * (3 - 2 * lt)
    p1, p2 = path.__getitem__(idx), path.__getitem__(idx + 1)
    return int(p1.__getitem__(0) + (p2.__getitem__(0) - p1.__getitem__(0)) * st), int(p1.__getitem__(1) + (p2.__getitem__(1) - p1.__getitem__(1)) * st)
def fmt_ass(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int((sec - int(sec)) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def split_sentences(script):
    parts = re.split(r'([。！？；])', script)
    sents, buf = [], ""
    for p in parts:
        buf += p
        if p in "。！？；":
            if buf.strip():
                sents.append(buf.strip())
            buf = ""
    if buf.strip():
        sents.append(buf.strip())
    return sents

def split_sub_clauses(sentence):
    parts = re.split(r'([。，；！？：、])', sentence)
    lines, buf = [], ""
    for p in parts:
        buf += p
        if p in "。，；！？：、":
            clean = buf.rstrip("。，；！？：、").strip()
            if clean:
                lines.append(clean)
            buf = ""
    if buf.strip():
        lines.append(buf.strip())
    return lines

async def build_chapter_audio_and_subs(cid, script, audio_dir, events, tl):
    sents = split_sentences(script)
    sent_clips, sent_timings = [], []
    local_t = 0.0
    for idx, sent in enumerate(sents):
        sp = f"{audio_dir}/part_{cid:02d}_s{idx:02d}.mp3"
        if not os.path.exists(sp):
            await edge_tts.Communicate(sent, VOICE, rate=RATE).save(sp)
        ac = AudioFileClip(sp)
        sdur = ac.duration
        sent_clips.append(ac)
        sent_timings.append((sent, local_t, local_t + sdur))

        # 單句內部再按逗號切分短字幕，單句僅 3~6 秒，誤差趨近於 0
        clauses = split_sub_clauses(sent)
        tot_c = max(1, sum(len(c) for c in clauses))
        ct = tl + local_t
        for c in clauses:
            cd = sdur * (len(c) / tot_c)
            events.append(f"Dialogue: 0,{fmt_ass(ct)},{fmt_ass(ct+cd)},Default,,0,0,0,,{c}")
            ct += cd
        local_t += sdur

    silence = AudioArrayClip(np.zeros((int(2.0 * 44100), 2)), fps=44100)
    full_ac = concatenate_audioclips(sent_clips + [silence])
    return full_ac, sent_clips, local_t, sent_timings

def calc_sent_ratios(sent_timings, keywords, total_dur):
    res = []
    for kw in keywords:
        found = None
        for sent, s_t, _ in sent_timings:
            if kw in sent:
                found = s_t / total_dur
                break
        res.append(found if found is not None else (res.__getitem__(-1) if res else 0.0))
    return res
async def main():
    out = "output_visual_20min"
    os.makedirs(f"{out}/audio", exist_ok=True)
    os.makedirs(f"{out}/clips", exist_ok=True)
    events, tl, clip_files = [], 0.0, []
    print("🚀 啟動逐句精準合成 0 誤差音畫同步引擎...")

    for ch in data.SLIDE_CHAPTERS:
        cid = ch["id"]
        cp = f"{out}/clips/clip_{cid:02d}.mp4"
        full_ac, s_clips, speech_dur, stimes = await build_chapter_audio_and_subs(cid, ch["script"], f"{out}/audio", events, tl)
        dur = speech_dur + 2.0
        tl += dur
        clip_files.append(cp)
        if os.path.exists(cp):
            full_ac.close()
            for c in s_clips:
                c.close()
            continue
        l_tr = calc_sent_ratios(stimes, ch.get("triggers", []), dur)
        r_tr = calc_sent_ratios(stimes, ch.get("right_triggers", []), dur)
        def mk_slide(t, c=ch, d=dur, lt=l_tr, rt=r_tr):
            return vis.render_slide_frame_array(c["id"], 8, c["title"], c["bullets"], c["chart_type"], min(1.0, max(0.0, t / d)), lt, rt)
        vc = VideoClip(mk_slide, duration=dur).with_audio(full_ac)
        vc.write_videofile(cp, fps=FPS, codec="libx264", audio_codec="aac", preset="ultrafast", threads=4, logger=None)
        vc.close()
        full_ac.close()
        for c in s_clips:
            c.close()

    for sc in data.DEMO_SCENES:
        sid = sc["id"]
        cp = f"{out}/clips/clip_{sid:02d}.mp4"
        full_ac, s_clips, speech_dur, _ = await build_chapter_audio_and_subs(sid, sc["script"], f"{out}/audio", events, tl)
        dur = speech_dur + 2.0
        tl += dur
        clip_files.append(cp)
        if os.path.exists(cp):
            full_ac.close()
            for c in s_clips:
                c.close()
            continue
        ar = speech_dur / dur
        c_times = [ct * ar for ct in sc["click_times"]]
        def mk_demo(t, s=sc, d=dur, cts=c_times, audio_r=ar):
            p = min(1.0, max(0.0, t / d))
            p_speech = min(1.0, p / max(0.1, audio_r))
            img = demo.render_demo_frame(s["scene_type"], p_speech, s["title"])
            mx, my = interp_mouse(s["mouse_path"], p_speech)
            demo.draw_cursor_and_click(ImageDraw.Draw(img), mx, my, any(abs(p - ct) < 0.035 for ct in cts))
            return np.array(img)
        vc = VideoClip(mk_demo, duration=dur).with_audio(full_ac)
        vc.write_videofile(cp, fps=FPS, codec="libx264", audio_codec="aac", preset="ultrafast", threads=4, logger=None)
        vc.close()
        full_ac.close()
        for c in s_clips:
            c.close()

    with open(f"{out}/VOC_Sentry_20min_Visual_Master.ass", "w", encoding="utf-8-sig") as f:
        f.write(ASS_HEADER + "\n".join(events))
    concat_txt = f"{out}/clips/concat_list.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for cf in clip_files:
            f.write(f"file '{os.path.basename(cf)}'\n")
    mp4_path = f"{out}/VOC_Sentry_20min_Visual_Master.mp4"
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", mp4_path], check=True)
    print(f"🎉 全部製作完成！總片長：{tl/60:.2f} 分鐘 -> {mp4_path}")

if __name__ == "__main__":
    asyncio.run(main())
