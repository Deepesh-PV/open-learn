import json
from typing import List, Optional
from pydantic import BaseModel
from difflib import SequenceMatcher
from youtube_resource import missing_video, Video



# === Pydantic models ===

class SubtitleChapter(BaseModel):
    title: str
    start_time: float
    end_time: float
    content: str
    url: str

class RoadMapDay(BaseModel):
    day: str
    topics: List[str]

class EnrichedTopic(BaseModel):
    topic: str
    matched_chapter: Optional[str]
    url: Optional[str]

class EnrichedRoadMapDay(BaseModel):
    day: str
    topics: List[EnrichedTopic]


# === Load JSON files ===

def load_cleaned_subtitles(subtitle: list) -> List[SubtitleChapter]:
    final_list=[]
    for item in subtitle:
        final_list.append(SubtitleChapter(**item))
    return final_list

def load_roadmap(road:list) -> List[RoadMapDay]:
    road_dict=dict(road)
    final_list=[]
    for values in road_dict.items():
        final_list.append(RoadMapDay(day=values[0],topics=values[1]))
    return final_list

# === Match roadmap topic to subtitle title ===

def match_topic_to_chapter(topic: str, chapters: List[SubtitleChapter]) -> Optional[SubtitleChapter]:
    best_match = None
    highest_score = 0.0

    for chapter in chapters:
        score = SequenceMatcher(None, topic.lower(), chapter.title.lower()).ratio()
        if score > highest_score:
            highest_score = score
            best_match = chapter

    return best_match if highest_score > 0.5 else None   # Threshold can be adjusted


# === Build enriched roadmap ===

def enrich_roadmap(roadmap: List[RoadMapDay], chapters: List[SubtitleChapter]) -> List[EnrichedRoadMapDay]:
    enriched = []

    for day_entry in roadmap:
        enriched_topics = []
        for topic in day_entry.topics:
            match = match_topic_to_chapter(topic, chapters)
            
            if match:
                enriched_topic = EnrichedTopic(
                    topic=topic,
                    matched_chapter=match.title,
                    url=match.url
                )
            else:
                # No good match found, try to find a missing video
                print(f"🔍 No match found for topic: '{topic}', searching YouTube...")
                try:
                    video = missing_video(topic)
                    enriched_topic = EnrichedTopic(
                        topic=topic,
                        matched_chapter=video.title,
                        url=video.url
                    )
                except Exception as e:
                    print(f"❌ Failed to fetch fallback video for '{topic}': {e}")
                    enriched_topic = EnrichedTopic(
                        topic=topic,
                        matched_chapter=None,
                        url=None
                    )
            
            enriched_topics.append(enriched_topic)

        enriched.append(EnrichedRoadMapDay(day=day_entry.day, topics=enriched_topics))

    return enriched



# === Save output ===

def save_enriched_roadmap(data: List[EnrichedRoadMapDay], path: str):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump([entry.dict() for entry in data], f, indent=2)


# === Main ===
