from pymongo import MongoClient
from bcrypt import  hashpw,checkpw,gensalt
from fastapi import FastAPI,Response,HTTPException,Request
from uuid import  uuid4
from pydantic import BaseModel
from typing import Optional
from main import create_course,CoursePlan
from youtube_resource import Video,get_video_metadata
from roadmap import rephrase_description
import merge
import match
import json

client=MongoClient("mongodb://127.0.0.1:27017")
print("client successfull")
db=client["user_data_test"]
user_data=db["user"]
course_data=db["course_data"]
session_ids=db["session_id"]


class desc(BaseModel):
    desc:str
class selected_url(BaseModel):
    selected_url:Optional[str]=None
    course_id:str

app=FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class user(BaseModel):
    password:str
    email:str
    course_ids:Optional[list]=None

salt=gensalt()



@app.post("/create_user")
def create_user(user:user):
    if user_data.find_one({"email":user.email}):
        raise HTTPException(status_code=401,detail="try different email")
    else:
        user_data.insert_one({"email":user.email,"password":hashpw(password=user.password.encode('utf-8'),salt=salt),"course_id":[]})
        return "success"


@app.post("/login")
def login(user_request:user,response:Response):
    user=user_data.find_one({"email":user_request.email})
    if user==False:
        raise HTTPException(status_code=401,detail="not authorized")
    else:
        if checkpw(password=user_request.password.encode('utf-8'),hashed_password=user['password']):
            session_id=str(uuid4())
            session_ids.insert_one({"email":user_request.email,"session_id":session_id})
            response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=False,   # True = secure from JS (prod), False = readable in dev
            secure=False,     # False = allow over HTTP
            samesite="lax"    # good default
        )
            return {"message":"login accepted"}
        else:

            raise HTTPException(status_code=401,detail="wrong password")
        
@app.post("/createcourse")
def new_course(course:CoursePlan,request:Request):
    
    user=session_ids.find_one({"session_id":request.cookies.get("session_id")})
    if request.cookies.get("session_id")==user['session_id']:
        out=create_course(course=course)
        course_id=str(uuid4())
        course_data.insert_one({"email":user['email'],"course":json.dumps(out.dict()),"course_id":course_id})
        user_new=user_data.find_one({"email":user['email']})
        existing_course=user_new['course_id']
        existing_course.append(course_id)
        user_data.update_one({"email":user['email']},{"$set":{"course_id":existing_course}})
        print("dbms updated")
        return {"course_id":course_id}
    else:
        raise HTTPException(status_code=401,detail="not authorized")
    
@app.post("/save_course")
def save_course(course:selected_url,request:Request):
    user=session_ids.find_one({"session_id":request.cookies.get("session_id")})
    if request.cookies.get("session_id")==user['session_id']:
        selectedurl=course.selected_url
        existing_main_course=course_data.find_one({"course_id":course.course_id})
        print(existing_main_course)
        existing_course=json.loads(existing_main_course['course'])
        
        existing_videos=existing_course["videos"]
        for video in existing_videos:
            print(video['url'])
            print(selectedurl)
            if video['url']==selectedurl:
                course_data.update_one({"course_id":course.course_id},{"$set":{"videos":video}})
                course_data.update_one({"course_id":course.course_id},{"$set":{"road_map":existing_course['road_map']}})
                course_data.update_one({"course_id":course.course_id},{"$set":{"title":existing_course['title']}})
                course_data.update_one({"course_id":course.course_id},{"$set":{"days":existing_course['days']}})
                course_data.update_one({"course_id":course.course_id},{"$set":{"level":existing_course['level']}})
                course_data.update_one({"course_id":course.course_id},{"$set":{"progress":existing_course['progress']}})
                course_data.update_one({"course_id":course.course_id},{"$set":{"progress_indicator":existing_course['progress_indicator']}})
                course_data.update_one({"course_id":course.course_id},{"$unset":{"course":""}}) 
                break       
        raise HTTPException(status_code=200,detail="selected video saved")
    else:
        raise HTTPException(status_code=401,detail="not authorized")

@app.get("/get_course/{courseid}")
def get_course(courseid:str):
    course=course_data.find_one({"course_id":courseid})
    if course==None:
        raise HTTPException(status_code=401,detail="wrong courseid")
    else:
        if "course" in course:
            data=course['course']
            return json.loads(data)
        else:
            print(course)
            course['_id']=str(course['_id'])      
            return course

@app.get("/get_course_id")
def find_course(request:Request):
    email=session_ids.find_one({"session_id":request.cookies.get("session_id")})
    email_address=email["email"]
    user=user_data.find_one({"email":email_address})
    return {"course_ids":user['course_id']} 

@app.post("/summarize_description")
def rephrase(desc:desc):
    out=rephrase_description(desc=desc.desc)
    return {"description":out}

@app.post("/match")
def matchingvideos(course_id:selected_url,):
    # user=session_ids.find_one({"session_id":request.cookies.get("session_id")})
    # if request.cookies.get("session_id")==user['session_id']:
        course_main=course_data.find_one({"course_id":course_id.course_id})
        data=course_main['videos']
        keymoments=data['keyMoments']
        merge.download_subtitles(data['url'])
        chapter=merge.load_info_ranges(keymoments)
        subtitle=merge.parse_vtt_file("./info.vtt")
        out=merge.group_subtitles_to_chapters(video_url=data['url'],chapters=chapter,subtitles=subtitle)
        topics_list=course_main['road_map']
        topics_dict=match.load_roadmap(topics_list)
        print("updated")

if __name__=="__main__":
    course_main=course_data.find_one({"course_id":"3b263542-aaa4-4cfb-927e-3aec11e2ca0f"})
    inp=course_main['videos']
    out=match.load_cleaned_subtitles(inp)
    road_map_dict=match.load_roadmap(course_main['road_map'])
    something=match.enrich_roadmap(roadmap=road_map_dict,chapters=out)
    course_data.update_one({"course_id":"3b263542-aaa4-4cfb-927e-3aec11e2ca0f"},{"$set":{"videos":something}})
    print("dbms updated")    