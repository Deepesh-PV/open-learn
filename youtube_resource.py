from googlesearch import search
from pydantic import BaseModel
from typing import Optional
import yt_dlp
import time



class Video(BaseModel):
    url:str
    thumbnail:Optional[str]=None
    description:Optional[str]=None
    keyMoments:Optional[tuple]=None
    title:Optional[str]=None

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




if __name__=="__main__":
    out=youtube_result("machine learning")
    for video in out:
        print(video.title)
    