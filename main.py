from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "API is running successfully!"}

@app.get("/transcript")
def get_transcript(video_id: str):
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        
        # Original English / Spoken track select karna
        selected = None
        for t in transcript_list:
            if not getattr(t, 'is_generated', False) and t.language_code.lower().startswith('en'):
                selected = t
                break
        if not selected:
            for t in transcript_list:
                if t.language_code.lower().startswith('en'):
                    selected = t
                    break
        if not selected:
            selected = next(iter(transcript_list))

        data = selected.fetch()
        
        lines = []
        for item in data:
            text = getattr(item, 'text', item['text'] if isinstance(item, dict) else '')
            start = int(getattr(item, 'start', item['start'] if isinstance(item, dict) else 0))
            mins = start // 60
            secs = start % 60
            lines.append(f"[{mins:02d}:{secs:02d}] {text}")

        return {
            "success": True,
            "language": getattr(selected, 'language', 'Original'),
            "transcript": "\n".join(lines)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
