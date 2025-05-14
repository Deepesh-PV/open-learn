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

def load_cleaned_subtitles(path: str) -> List[SubtitleChapter]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [SubtitleChapter(**item) for item in data]

def load_roadmap(path: str) -> List[RoadMapDay]:
    with open(path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    return [RoadMapDay(day=key, topics=value) for key, value in raw.items()]


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

if __name__ == "__main__":
    cleaned_subs = load_cleaned_subtitles("cleaned_subtitles.json")
    roadmap = load_roadmap("courseplan.json")
    enriched = enrich_roadmap(roadmap, cleaned_subs)
    save_enriched_roadmap(enriched, "enriched_road_map.json")
    print("✅ Enriched roadmap with matched URLs saved to 'enriched_road_map.json'")
