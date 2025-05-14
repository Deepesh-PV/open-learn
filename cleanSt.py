import json
import os
import glob
import re
from yt_dlp import YoutubeDL
from pydantic import BaseModel
from typing import List
from datetime import timedelta

VIDEO_URL = "https://www.youtube.com/watch?v=i_LwzRVP7bg"  # Replace this
INFO_FILE = "video_info.json"
OUTPUT_FILE = "cleaned_subtitles.json"

# === Pydantic models ===
class Chapter(BaseModel):
    start_time: float
    end_time: float
    title: str

class FinalChapter(Chapter):
    content: str
    url: str

# === Step 1: Download subtitles using yt-dlp ===
def download_subtitles(url):
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'skip_download': True,
        'quiet': True,
        'outtmpl': '%(title)s.%(ext)s'
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# === Step 2: Find the downloaded VTT file ===
def find_vtt_file():
    vtt_files = glob.glob("*.en.vtt")
    if not vtt_files:
        raise FileNotFoundError("No .en.vtt file found in the directory.")
    return vtt_files[0]

# === Step 3: Convert timestamp to seconds ===
def vtt_timestamp_to_seconds(ts):
    parts = re.split('[:.]', ts)
    h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
    return h * 3600 + m * 60 + s

# === Step 4: Convert seconds to HH:MM:SS ===
def seconds_to_hhmmss(seconds):
    return str(timedelta(seconds=int(seconds)))

# === Step 5: Parse subtitles from VTT ===
def parse_vtt_file(file_path):
    subtitles = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    entry = {}
    for line in lines:
        line = line.strip()
        if "-->" in line:
            start, end = line.split(" --> ")
            entry = {
                "start": vtt_timestamp_to_seconds(start),
                "end": vtt_timestamp_to_seconds(end),
                "text": ""
            }
        elif line == "":
            if entry:
                subtitles.append(entry)
                entry = {}
        elif entry:
            entry["text"] += line + " "
    return subtitles

# === Step 6: Load video_info.json ===
def load_info_ranges(json_file) -> List[Chapter]:
    with open(json_file, "r", encoding='utf-8') as f:
        data = json.load(f)
    return [Chapter(**item) for item in data]

# === Step 7: Group subtitles by chapter ===
def group_subtitles_to_chapters(subtitles, chapters, video_url):
    output = []

    for chapter in chapters:
        content = ""
        for sub in subtitles:
            if chapter.start_time <= sub["start"] < chapter.end_time:
                content += sub["text"].strip() + " "

        chapter_url = f"{video_url}&t={int(chapter.start_time)}"
        cleaned = FinalChapter(
            title=chapter.title,
            start_time=chapter.start_time,
            end_time=chapter.end_time,
            content=content.strip(),
            url=chapter_url
        )
        output.append(cleaned.dict())
    return output

# === Main pipeline ===
if __name__ == "__main__":
    download_subtitles(VIDEO_URL)
    vtt_file = find_vtt_file()
    subtitles = parse_vtt_file(vtt_file)
    chapters = load_info_ranges(INFO_FILE)
    merged_chapters = group_subtitles_to_chapters(subtitles, chapters, VIDEO_URL)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(merged_chapters, f, indent=2)

    print(f"Cleaned subtitles saved to: {OUTPUT_FILE}")
