import os
import subprocess
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

input_mp4 = "output_visual_20min/VOC_Sentry_20min_Visual_Master.mp4"
input_ass = "output_visual_20min/VOC_Sentry_20min_Visual_Master.ass"
output_mp4 = "output_visual_20min/VOC_Sentry_20min_Final_HardSub.mp4"

if not os.path.exists(input_mp4) or not os.path.exists(input_ass):
    print("❌ 找不到輸入的 20 分鐘 MP4 或 ASS 檔案，請確認路徑是否正確。")
else:
    # 直接複製原本的 AAC 音軌 (-c:a copy)，僅將亮黃色 ASS 字幕燒入視訊畫面
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", input_mp4,
        "-vf", f"ass='{input_ass}'",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "22",
        "-c:a", "copy",
        output_mp4
    ]

    print("🔥 正在將 20 分鐘亮黃色字幕永久硬燒進 MP4 影片中（約需 1～2 分鐘）...")
    subprocess.run(cmd, check=True)
    print(f"🎉 硬燒完成！以後只需攜帶這單一檔案即可：{output_mp4}")
