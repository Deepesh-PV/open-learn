
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\keert_nxa8mzh\Downloads\LanCh\langc-1c789-af35218ca00a.json"
import json

load_dotenv()

with open("cleaned_subtitles.json") as js:
    data = json.load(js)
    
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite")

j=0
for i in data:
    
    topic = i['title']
    content = i['content']
    print("Generating Question for: ", topic)
    
    qns = model.invoke(f"Generate 5 Questions for a student to check basic understanding of the topic: {topic}, don't go advanced, include few MCQ out of 5 questions, use the following content: {content}")
    with open("QNS.txt", mode="a", encoding="utf-8") as fp:
        fp.write(f"Topic: {topic}\n")
        fp.write(qns.content)
    print(qns.content)
    
    


