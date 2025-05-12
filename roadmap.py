from langchain_groq import ChatGroq

from langchain_groq import ChatGroq
import json
from dotenv import load_dotenv

from pydantic import BaseModel
from typing import Optional
load_dotenv("api.env")




class CoursePlan(BaseModel):
    course_id:int
    title:str
    days:int
    level:str
    road_map:Optional[list]=None
    playlist:bool=True
    videos:Optional[list]=None
    progress:Optional[dict]=None
    progress_indicator:Optional[float]=0



llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,

)



def roadmap(content:str,days:int,level:str):
    messages=[
        {
            "role": "system",
            "content": "youre a routemap assistant to students who want to study topics that they prompt in a given time and given level you should give them the day wise topics to study give it in the form of a json and only that as the output only.dont add any youtube video as resource.give it in a json format no other thing is accepted.dont wrote json in heading.dont add time keys"
        },
        {
            "role":"user",
            "content":f"i have to study {content} topic and i am a {level} i have {days} to study."
        }
    ]
    out=llm.invoke(messages).content
    print(out)
    return json.loads(out)

def rephrase_input(topic:str,level:str):
    messages = [
    {
        "role": "system",
        "content": (
            "You are an assistant that rewrites a given title into an optimized search query "
            "for YouTube that would yield highly relevant results. "
            "Your output should be a single search query string and nothing else. "
            "Do not add quotes, explanations, or additional words. "
            "Only return the raw search query that would work well for YouTube search."
        )
    },
    {
        "role": "user",
        "content": f"{topic} and level {level}"
    }
    ]
    out=llm.invoke(messages).content
    print(out)
    return out 



    


if __name__=="__main__":
    print(roadmap("machine learning",days=7,level="begginer"))
