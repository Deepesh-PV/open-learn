from pymongo import MongoClient
from bcrypt import  hashpw,checkpw,gensalt
from fastapi import FastAPI,Response,HTTPException,Request
from uuid import  uuid4
from pydantic import BaseModel

client=MongoClient("mongodb://127.0.0.1:27017")
print("client successfull")
db=client["user_data_test"]
user_data=db["user"]
course_data=db["course_data"]
session_ids=db["session_id"]

app=FastAPI()

class user(BaseModel):
    password:str
    email:str


salt=gensalt()

@app.post("/create_user")
def create_user(user:user):
    if user_data.find_one({"email":user.email}):
        return "not success"
    else:
        user_data.insert_one({"email":user.email,"password":hashpw(password=user.password.encode('utf-8'),salt=salt)})
        return "success"


@app.post("/login")
def login(user_request:user,response:Response):
    user=user_data.find_one({"email":user_request.email})
    if user==False:
        return HTTPException(status_code=401,detail="not authorized")
    else:
        if checkpw(password=user_request.password.encode('utf-8'),hashed_password=user['password']):
            session_id=str(uuid4())
            session_ids.insert_one({"email":user_request.email,"session_id":session_id})
            response.set_cookie(key="session_id",value=session_id,httponly=True)
            return HTTPException(status_code=200,detail="login accepted")
        else:

            return HTTPException(status_code=401,detail="not authorized")
        

def session_check(session_id:str):
    if db['session_id'].find_one({"session_id":session_id}):
        return True
    else:
        False



