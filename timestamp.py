import subprocess
import os
import glob
import re
from datetime import datetime



def download_subtitles(video_url, lang="en", output_dir="./subtitles"):
    os.makedirs(output_dir, exist_ok=True)

    print("📥 Downloading subtitles...")
    subprocess.run([
        "yt-dlp",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs", lang,
        "--skip-download",
        "--output", os.path.join(output_dir, "%(title)s.%(ext)s"),
        video_url
    ])

    vtt_files = glob.glob(os.path.join(output_dir, "*.vtt"))
    if not vtt_files:
        print("⚠ No .vtt subtitle files found.")
        return

    for vtt_file in vtt_files:
        merge_chunks_to_single_file(vtt_file, output_dir)

def timestamp_to_seconds(timestamp):
    """Convert timestamp string like 00:01:23.456 to seconds"""
    t = datetime.strptime(timestamp, "%H:%M:%S.%f")
    return t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1e6

def format_time(seconds):
    """Format seconds into mm:ss"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def merge_chunks_to_single_file(vtt_file, output_dir):
    print(f"🧹 Cleaning and merging {os.path.basename(vtt_file)}...")
    minute_chunks = {}

    with open(vtt_file, "r", encoding="utf-8") as f:
        for line in f:
            timestamps = re.findall(r"<(\d+:\d+:\d+\.\d+)>", line)
            if not timestamps:
                continue

            start_time = timestamp_to_seconds(timestamps[0])
            minute_index = int(start_time // 60)

            # Clean sentence
            sentence = re.sub(r"<\d+:\d+:\d+\.\d+>", "", line)
            sentence = re.sub(r"</?c>", "", sentence).strip()

            if sentence:
                minute_chunks.setdefault(minute_index, []).append(sentence)

    output_file = os.path.join(output_dir, "merged_subtitles.txt")
    with open(output_file, "w", encoding="utf-8") as fout:
        for minute in sorted(minute_chunks.keys()):
            start = format_time(minute * 60)
            end = format_time((minute + 1) * 60)
            fout.write(f"[{start} - {end}]\n")
            fout.write(" ".join(minute_chunks[minute]) + "\n\n")

    print(f"✅ Merged subtitles saved to: {output_file}")
    




if __name__ == "__main__":
    youtube_url = input("🔗 Enter YouTube video URL: ").strip()
    download_subtitles(youtube_url)
