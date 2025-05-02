from googlesearch import search
from pydantic import BaseModel
from typing import Optional
import yt_dlp
from roadmap import rephrase_input
from dotenv import load_dotenv
load_dotenv("api.env")

class Video(BaseModel):
    url:str
    thumbnail:Optional[str]=None
    description:Optional[str]=None
    keyMoments:Optional[tuple]=None
    title:Optional[str]=None

class Playlist(BaseModel):
    url:str
    title:Optional[str]=None
    videos:Optional[list]=None
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
    print('over')
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
    results=search(query,num_results=10)
    videos=[]
    for url in results:
        video=Video(url=url)
        videos.append(video)
    final_videos=[]
    for video in videos:
        final_videos.append(get_video_metadata(video=video))
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
    return final_playlist

if __name__=="__main__":
    print(rephrase_input("guitar tutorials","begginer"))
    video=youtube_playlist_result(rephrase_input("guitar tutorials","begginer"))
    for v in video:
        print(v)
    