from langchain_groq import ChatGroq

from langchain_groq import ChatGroq
import json
from dotenv import load_dotenv

from pydantic import BaseModel
from typing import Optional
load_dotenv("api.env")




class CoursePlan(BaseModel):
    course_id:Optional[str]=None
    title:str
    days:int
    level:str
    road_map:Optional[list]=None
    playlist:bool=True
    videos:Optional[list]=None
    progress:Optional[dict]=None
    progress_indicator:Optional[float]=0
    selected_url:Optional[str]=None
    



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

def rephrase_description(desc:str):
    messages = [
    {
        "role": "system",
        "content": (
            """ youre a system where u summarize the youtube descriptions without any emoji and into topics covered and what the video is about"""
        )
    },
    {
        "role": "user",
        "content": f" {desc}"
    }
    ]
    out=llm.invoke(messages).content
    print(out)
    return out 
    
    


    


if __name__=="__main__":
    print(roadmap("machine learning",days=7,level="begginer"))
    print(rephrase_description("Don’t miss the FlexiSpot Presidents’ Day flash sale! 🌟 Use my exclusive code 'Q1YTB30' for extra $30 off on E7,E7 Pro and E7L. Let's make a perfect workspace! US: https://bit.ly/4bI9Yix CA: https://bit.ly/3I6v3Wv Learn about the foundations of machine learning (ML) in this video, and how machine learning is different from artificial intelligence (AI) and data science. We will discuss the 3 types of machine learning: supervised learning, unsupervised learning, and reinforcement learning. Then, we'll learn about the different types of supervised learning tasks/outputs: classification, and regression, and how they are different. Timestamps: 00:00 Introduction 01:33 What is Machine Learning? 04:37 AI vs ML vs Data Science 06:55 Supervised Learning 07:46 Unsupervised Learning 09:31 Reinforcement Learning 11:13 Classification 13:35 Regression This Introduction to Machine Learning series is a gentle introduction to machine learning for beginners! Please consider subscribing if you liked this video: https://www.youtube.com/c/ycubed?sub_confirmation=1 Thanks for watching everyone! ~~~~~~~~~~~~~~~~~~~~~~~~ Follow me on Instagram: https://www.instagram.com/kylieyying Follow me on Twitter: https://www.twitter.com/kylieyying Check out my website: https://www.kylieying.com"))