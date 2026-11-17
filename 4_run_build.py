import os
import re
import asyncio
import subprocess
import importlib.util
import numpy as np
import edge_tts
import imageio_ffmpeg
from PIL import ImageDraw
from moviepy import VideoClip, AudioFileClip

def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

vis = load_mod("ve", "1_visual_engine.py")
demo = load_mod("dr", "2_demo_renderer.py")
data = load_mod("pd", "3_presentation_data.py")

VOICE = "zh-TW-HsiaoChenNeural"
RATE = "-5%"
FPS = 12  # 12 FPS 簡報與鼠標操作流暢且渲染速度倍增

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
        return path
    segs = len(path) - 1
    sc = prog * segs
    idx = min(int(sc), segs - 1)
    lt = sc - idx
    st = lt * lt * (3 - 2 * lt)
    x1, y1 = path[idx]
    x2, y2 = path[idx + 1]
    return int(x1 + (x2 - x1) * st), int(y1 + (y2 - y1) * st)

def fmt_ass(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int((sec - int(sec)) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def add_subs(events, script, start_t, dur):
    parts = re.split(r'([。，；！？：])', script)
    lines, buf = [], ""
    for p in parts:
        buf += p
        if p in "。，；！？：":
            clean = buf.rstrip("。，；！？：").strip()
            if clean:
                lines.append(clean)
            buf = ""
    if buf.strip():
        lines.append(buf.strip())
    tot = sum(len(l) for l in lines)
    t = start_t
    for l in lines:
        d = dur * (len(l) / tot)
        events.append(f"Dialogue: 0,{fmt_ass(t)},{fmt_ass(t+d)},Default,,0,0,0,,{l}")
        t += d

async def main():
    out = "output_visual_20min"
    os.makedirs(f"{out}/audio", exist_ok=True)
    os.makedirs(f"{out}/clips", exist_ok=True)
    events, tl, clip_files = [], 0.0, []

    print("🚀 啟動極速分段＋斷點續傳渲染引擎（隨時按 Ctrl+C 中斷，下次自動接續）...")

    # 第一部分：1-8 幕動態圖表簡報
    for ch in data.SLIDE_CHAPTERS:
        cid = ch["id"]
        ap = f"{out}/audio/part_{cid:02d}.mp3"
        cp = f"{out}/clips/clip_{cid:02d}.mp4"
        if not os.path.exists(ap):
            await edge_tts.Communicate(ch["script"], VOICE, rate=RATE).save(ap)

        ac = AudioFileClip(ap)
        dur = ac.duration + 0.6
        add_subs(events, ch["script"], tl, ac.duration)
        tl += dur
        clip_files.append(cp)

        if os.path.exists(cp):
            print(f"⏭️ [{cid:02d}/16] 已存在分段檔，自動跳過：{cp}")
            ac.close()
            continue

        print(f"⚡ [{cid:02d}/16] 正在渲染分段：{ch['title']}")
        def mk_slide(t, c=ch, d=dur):
            p = min(1.0, max(0.0, t / d))
            return vis.render_slide_frame_array(c["id"], 8, c["title"], c["bullets"], c["chart_type"], p)

        vc = VideoClip(mk_slide, duration=dur).with_audio(ac)
        vc.write_videofile(cp, fps=FPS, codec="libx264", audio_codec="aac", preset="ultrafast", threads=4, logger=None)
        vc.close()
        ac.close()

    # 第二、三部分：9-16 幕 GitHub 與網站操作演示
    for sc in data.DEMO_SCENES:
        sid = sc["id"]
        ap = f"{out}/audio/part_{sid:02d}.mp3"
        cp = f"{out}/clips/clip_{sid:02d}.mp4"
        if not os.path.exists(ap):
            await edge_tts.Communicate(sc["script"], VOICE, rate=RATE).save(ap)

        ac = AudioFileClip(ap)
        dur = ac.duration + 0.6
        add_subs(events, sc["script"], tl, ac.duration)
        tl += dur
        clip_files.append(cp)

        if os.path.exists(cp):
            print(f"⏭️ [{sid:02d}/16] 已存在分段檔，自動跳過：{cp}")
            ac.close()
            continue

        print(f"🖱️ [{sid:02d}/16] 正在渲染分段：{sc['title']}")
        def mk_demo(t, s=sc, d=dur):
            p = min(1.0, max(0.0, t / d))
            img = demo.render_demo_frame(s["scene_type"], p, s["title"])
            mx, my = interp_mouse(s["mouse_path"], p)
            clicking = any(abs(p - ct) < 0.04 for ct in s["click_times"])
            demo.draw_cursor_and_click(ImageDraw.Draw(img), mx, my, clicking)
            return np.array(img)

        vc = VideoClip(mk_demo, duration=dur).with_audio(ac)
        vc.write_videofile(cp, fps=FPS, codec="libx264", audio_codec="aac", preset="ultrafast", threads=4, logger=None)
        vc.close()
        ac.close()

    ass_path = f"{out}/VOC_Sentry_20min_Visual_Master.ass"
    with open(ass_path, "w", encoding="utf-8-sig") as f:
        f.write(ASS_HEADER + "\n".join(events))

    # 使用 FFmpeg 無損極速串接 16 個分段影片（僅需 2 秒）
    concat_txt = f"{out}/clips/concat_list.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for cf in clip_files:
            f.write(f"file '{os.path.basename(cf)}'\n")

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    mp4_path = f"{out}/VOC_Sentry_20min_Visual_Master.mp4"
    print("🎬 正在使用 FFmpeg 秒速合併 16 個分段影片...")
    subprocess.run([ffmpeg_exe, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", mp4_path], check=True)
    print(f"🎉 全部製作完成！總片長：{tl/60:.2f} 分鐘 -> {mp4_path}")

if __name__ == "__main__":
    asyncio.run(main())
