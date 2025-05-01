import yt_dlp
from youtube_resource import Video
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
    
    
video=Video(url="https://www.youtube.com/watch?v=i_LwzRVP7bg")
out=get_video_metadata(video=video)
print(out)