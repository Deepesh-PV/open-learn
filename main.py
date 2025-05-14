from roadmap import roadmap
import fastapi
from fastapi import FastAPI
from roadmap import rephrase_input,roadmap,CoursePlan
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from youtube_resource import youtube_playlist_result,youtube_result
load_dotenv("api.env")
app=FastAPI()
import random


class Video(BaseModel):
    video_url:list
    video_timings:list
    description:list
    titles:Optional[list]
    subtopic:Optional[str]


class Resourse(BaseModel):
    playlist:list #its a list of object of class type Video


def create_course(course:CoursePlan):
    plan=roadmap(course.title,course.days,course.level)
    course.road_map=[(day,[subtopic for subtopic in plan[day]])for day in plan.keys()]
    return course



    
if __name__=="__main__":
    course=CoursePlan(title="machine learning",days=7,level="begginer",course_id=random.randint(1000,9999))
    out=create_course(course=course)
    
    if out.playlist==True:
        out.videos=youtube_playlist_result(rephrase_input(course.title,course.level))
    else:
        out.videos=youtube_result(rephrase_input(course.title,course.level))
    
    print(out)
    


