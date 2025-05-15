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
title="info"
# === Pydantic models ===
class Chapter(BaseModel):
    start_time: float
    end_time: float
    title: str

class FinalChapter(Chapter):
    content: str
    url: str

# === Step 1: Download subtitles using yt-dlp ===
import os
from yt_dlp import YoutubeDL

def download_subtitles(url):
    # Use yt_dlp to get video info first
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'skip_download': True,
        'quiet': True,
        'outtmpl': 'temp.%(ext)s',
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        title = info_dict.get('title', 'video')
        subtitle_ext = 'vtt'  # Most auto subtitles are .vtt
        subtitle_file = f"temp.en.{subtitle_ext}"
        
        if os.path.exists(subtitle_file):
            os.rename(subtitle_file, f"info.{subtitle_ext}")
            print("Subtitles saved as info." + subtitle_ext)
        else:
            print("Subtitle file not found.")


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
def load_info_ranges(json_file:list) -> List[Chapter]:
    data=json_file
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
    course={'_id':'6825485654a0234612d18f4e', 'email': 'sasi@gmail.com', 'course_id': 'fe80d47e-76b1-43fc-937a-37dc8ecc7602', 'videos': {'url': 'https://www.youtube.com/watch?v=i_LwzRVP7bg', 'thumbnail': None, 'description': "Learn Machine Learning in a way that is accessible to absolute beginners. You will learn the basics of Machine Learning and how to use TensorFlow to implement many different concepts.\n\n✏️ Kylie Ying developed this course. Check out her channel: https://www.youtube.com/c/YCubed\n\n⭐️ Code and Resources ⭐️\n🔗 Supervised learning (classification/MAGIC): https://colab.research.google.com/drive/16w3TDn_tAku17mum98EWTmjaLHAJcsk0?usp=sharing\n🔗 Supervised learning (regression/bikes): https://colab.research.google.com/drive/1m3oQ9b0oYOT-DXEy0JCdgWPLGllHMb4V?usp=sharing\n🔗 Unsupervised learning (seeds): https://colab.research.google.com/drive/1zw_6ZnFPCCh6mWDAd_VBMZB4VkC3ys2q?usp=sharing\n🔗 Dataets (add a note that for the bikes dataset, they may have to open the downloaded csv file and remove special characters)\n🔗 MAGIC dataset: https://archive.ics.uci.edu/ml/datasets/MAGIC+Gamma+Telescope\n🔗 Bikes dataset: https://archive.ics.uci.edu/ml/datasets/Seoul+Bike+Sharing+Demand\n🔗 Seeds/wheat dataset: https://archive.ics.uci.edu/ml/datasets/seeds\n\n🏗 Google provided a grant to make this course possible. \n\n❤️ Support for this channel comes from our friends at Scrimba – the coding platform that's reinvented interactive learning: https://scrimba.com/freecodecamp\n\n⭐️ Contents ⭐️\n⌨️ (0:00:00) Intro\n⌨️ (0:00:58) Data/Colab Intro\n⌨️ (0:08:45) Intro to Machine Learning\n⌨️ (0:12:26) Features\n⌨️ (0:17:23) Classification/Regression\n⌨️ (0:19:57) Training Model\n⌨️ (0:30:57) Preparing Data\n⌨️ (0:44:43) K-Nearest Neighbors\n⌨️ (0:52:42) KNN Implementation\n⌨️ (1:08:43) Naive Bayes\n⌨️ (1:17:30) Naive Bayes Implementation\n⌨️ (1:19:22) Logistic Regression\n⌨️ (1:27:56) Log Regression Implementation\n⌨️ (1:29:13) Support Vector Machine\n⌨️ (1:37:54) SVM Implementation\n⌨️ (1:39:44) Neural Networks\n⌨️ (1:47:57) Tensorflow\n⌨️ (1:49:50) Classification NN using Tensorflow\n⌨️ (2:10:12) Linear Regression\n⌨️ (2:34:54) Lin Regression Implementation\n⌨️ (2:57:44) Lin Regression using a Neuron\n⌨️ (3:00:15) Regression NN using Tensorflow\n⌨️ (3:13:13) K-Means Clustering\n⌨️ (3:23:46) Principal Component Analysis\n⌨️ (3:33:54) K-Means and PCA Implementations\n\n🎉 Thanks to our Champion and Sponsor supporters:\n👾 Raymond Odero\n👾 Agustín Kussrow\n👾 aldo ferretti\n👾 Otis Morgan\n👾 DeezMaster\n\n--\n\nLearn to code for free and get a developer job: https://www.freecodecamp.org\n\nRead hundreds of articles on programming: https://freecodecamp.org/news", 'keyMoments': [{'start_time': 0.0, 'title': 'Intro', 'end_time': 58.0}, {'start_time': 58.0, 'title': 'Data/Colab Intro', 'end_time': 525.0}, {'start_time': 525.0, 'title': 'Intro to Machine Learning', 'end_time': 746.0}, {'start_time': 746.0, 'title': 'Features', 'end_time': 1043.0}, {'start_time': 1043.0, 'title': 'Classification/Regression', 'end_time': 1197.0}, {'start_time': 1197.0, 'title': 'Training Model', 'end_time': 1857.0}, {'start_time': 1857.0, 'title': 'Preparing Data', 'end_time': 2683.0}, {'start_time': 2683.0, 'title': 'K-Nearest Neighbors', 'end_time': 3162.0}, {'start_time': 3162.0, 'title': 'KNN Implementation', 'end_time': 4123.0}, {'start_time': 4123.0, 'title': 'Naive Bayes', 'end_time': 4650.0}, {'start_time': 4650.0, 'title': 'Naive Bayes Implementation', 'end_time': 4762.0}, {'start_time': 4762.0, 'title': 'Logistic Regression', 'end_time': 5276.0}, {'start_time': 5276.0, 'title': 'Log Regression Implementation', 'end_time': 5353.0}, {'start_time': 5353.0, 'title': 'Support Vector Machine', 'end_time': 5874.0}, {'start_time': 5874.0, 'title': 'SVM Implementation', 'end_time': 5984.0}, {'start_time': 5984.0, 'title': 'Neural Networks', 'end_time': 6477.0}, {'start_time': 6477.0, 'title': 'Tensorflow', 'end_time': 6590.0}, {'start_time': 6590.0, 'title': 'Classification NN using Tensorflow', 'end_time': 7812.0}, {'start_time': 7812.0, 'title': 'Linear Regression', 'end_time': 9294.0}, {'start_time': 9294.0, 'title': 'Lin Regression Implementation', 'end_time': 10664.0}, {'start_time': 10664.0, 'title': 'Lin Regression using a Neuron', 'end_time': 10815.0}, {'start_time': 10815.0, 'title': 'Regression NN using Tensorflow', 'end_time': 11593.0}, {'start_time': 11593.0, 'title': 'K-Means Clustering', 'end_time': 12226.0}, {'start_time': 12226.0, 'title': 'Principal Component Analysis', 'end_time': 12834.0}, {'start_time': 12834.0, 'title': 'K-Means and PCA Implementations', 'end_time': 14033}], 'title': 'Machine Learning for Everybody – Full Course'}, 'road_map': [['Day 1', ['Introduction to Machine Learning', 'Types of Machine Learning', 'Supervised vs Unsupervised Learning']], ['Day 2', ['Regression Techniques', 'Linear Regression', 'Multiple Linear Regression']], ['Day 3', ['Classification Techniques', 'Logistic Regression', 'Decision Trees']], ['Day 4', ['Model Evaluation Metrics', 'Confusion Matrix', 'Accuracy Score']], ['Day 5', ['Model Selection', 'Cross Validation', 'Hyperparameter Tuning']], ['Day 6', ['Neural Networks', 'Feedforward Networks', 'Activation Functions']], ['Day 7', ['Deep Learning', 'Convolutional Neural Networks', 'Recurrent Neural Networks']]], 'title': 'machine learning', 'days': 7, 'level': 'Beginner', 'progress': {'Day 1': False, 'Day 2': False, 'Day 3': False, 'Day 4': False, 'Day 5': False, 'Day 6': False, 'Day 7': False}, 'progress_indicator': 0}
    data=course['videos']
    keymoments=data['keyMoments']
    download_subtitles(data['url'])
    print(load_info_ranges(keymoments))
    subtitle=parse_vtt_file("./info.vtt")
    print(group_subtitles_to_chapters(video_url=data['url'],chapters=load_info_ranges(keymoments),subtitles=subtitle))