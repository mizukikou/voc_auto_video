import os
import re
from moviepy import AudioFileClip
from manual_demo_22min_video import SLIDE_CHAPTERS, MANUAL_SCENES

# 字型設為 34px 粗體亮黃色 (&H0000FFFF)，1920px 寬螢幕單行可完整容納 48 個中文字不換行
ASS_HEADER = """[Script Info]
Title: VOC_Sentry Natural Semantic Subtitles
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft JhengHei,34,&H0000FFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,3,2,0,2,20,20,25,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def format_ass_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centisecs = int((seconds - int(seconds)) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"

def split_by_natural_semantics(text):
    """完全依照中文標點符號自然語意斷句，絕不硬性切斷詞彙或英文單字"""
    # 依照句號、逗號、分號、驚嘆號、問號、冒號進行自然語意切分
    parts = re.split(r'([。，；！？：])', text)
    lines = []
    buf = ""
    for p in parts:
        buf += p
        if p in "。，；！？：":
            clean = buf.rstrip("。，；！？：").strip()
            if clean:
                lines.append(clean)
            buf = ""
    if buf.strip():
        lines.append(buf.strip())
    return lines

def generate_ass_directly(items, audio_dir, ass_output_path, old_srt_path):
    if not os.path.exists(audio_dir):
        return

    events = []
    current_timeline = 0.0

    for item in items:
        cid = item["id"]
        audio_path = os.path.join(audio_dir, f"part_{cid:02d}.mp3")
        if not os.path.exists(audio_path):
            audio_path = os.path.join(audio_dir, f"voice_{cid:02d}.mp3")
        if not os.path.exists(audio_path):
            continue

        audio_clip = AudioFileClip(audio_path)
        audio_dur = audio_clip.duration
        clip_dur = audio_dur + 0.8

        lines = split_by_natural_semantics(item["script"])
        total_chars = sum(len(line) for line in lines)

        s_start = current_timeline
        for line in lines:
            s_dur = audio_dur * (len(line) / total_chars)
            start_str = format_ass_time(s_start)
            end_str = format_ass_time(s_start + s_dur)
            events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{line}")
            s_start += s_dur

        current_timeline += clip_dur
        audio_clip.close()

    with open(ass_output_path, "w", encoding="utf-8-sig") as f:
        f.write(ASS_HEADER + "\n".join(events))

    if os.path.exists(old_srt_path):
        os.remove(old_srt_path)

    print(f"✅ 自然語意不斷詞亮黃色 ASS 字幕已生成：{ass_output_path}")

if __name__ == "__main__":
    generate_ass_directly(
        SLIDE_CHAPTERS,
        "output/audio",
        "output/VOC_Sentry_15min_Full.ass",
        "output/VOC_Sentry_15min_Full.srt"
    )
    generate_ass_directly(
        SLIDE_CHAPTERS + MANUAL_SCENES,
        "output_20min/audio",
        "output_20min/VOC_Sentry_20min_Master.ass",
        "output_20min/VOC_Sentry_20min_Master.srt"
    )
