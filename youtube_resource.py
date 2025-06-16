from googlesearch import search
from pydantic import BaseModel
from typing import Optional,List
import yt_dlp
from roadmap import rephrase_input
from dotenv import load_dotenv
import json
import time
from yt_dlp import YoutubeDL
load_dotenv("api.env")
from youtube_search import search_youtube_video


class Video(BaseModel):
    url:str
    thumbnail:Optional[str]=None
    description:Optional[str]=None
    keyMoments:Optional[tuple]=None
    title:Optional[str]=None

class Playlist(BaseModel):
    url:str
    title:Optional[str]=None
    videos:Optional[List[Video]]=None
    description:Optional[str]=None
    count:Optional[int]=None
    thumbnail:Optional[list]=None
    


def get_video_metadata(video:Video)->Video:
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'forcejson': True,
        'simulate': True,
    }
    info=dict()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video.url, download=False)
    video.description=info['description']
    video.title=info['title']
    video.keyMoments=info['chapters']
    return video

def get_playlist_metadata(playlist:Playlist)->Playlist:
    ydl_opts = {
    'quiet': True,
    'skip_download': True,
    'extract_flat': True  # Don't load full video metadata
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist.url, download=False)
    print(info.keys())
    playlist.title=info['title']
    playlist.description=info['description']
    playlist.count=info['playlist_count']
    playlist.thumbnail=info['thumbnails']
    return playlist
    

def youtube_result(q:str)->list:
    query=f"site:youtube.com -inurl:shorts -inurl:playlist {q}"
    results=search(query,num_results=4)
    videos=[]
    for url in results:
        video=Video(url=url)
        videos.append(video)
    final_videos=[]
    for video in videos:
        final_videos.append(get_video_metadata(video=video))
        print("done video")
    return final_videos

def youtube_playlist_result(q:str)->list:
    query=f"site:youtube.com -inurl:shorts inurl:playlist {q}"
    results=search(query,num_results=5)
    print("done")
    playlists=[]

    final_playlist=[]
    for url in results:
        playlists.append(Playlist(url=url))
    for playlist in playlists:
        final_playlist.append(get_playlist_metadata(playlist=playlist))
        print("done playlist")
    return final_playlist

def missing_video(q:str)->Video:
    results=[search_youtube_video(q)]
    for url in results:
        video=Video(url=url)
        print("video")
        break
    video=get_video_metadata(video=video)
    print("video meta-details")
    return video

def get_video_urls_from_playlist(playlist_url):
    ydl_opts = {
        'extract_flat': True,  # Do not download the videos
        'quiet': True,         # Suppress output
        'skip_download': True, # Just extract info
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        entries = info.get('entries', [])
        video_urls = [f"https://www.youtube.com/watch?v={entry['id']}" for entry in entries]
        final_video_list=[]
        print(len(video_urls))
        for url in video_urls:
            video=Video(url=url)
            video=get_video_metadata(video)
            final_video_list.append(video)
        final_video_list=[s.dict() for s in final_video_list]
        return final_video_list



