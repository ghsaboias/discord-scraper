from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Change from relative to absolute import
from scraping.discord_client import (
    get_guild_channels,
    get_bot_messages,
    find_matching_channel
)

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TimeRange(BaseModel):
    hours: int

class Channel(BaseModel):
    id: str
    name: str
    type: int
    position: Optional[int]

class ScrapeRequest(BaseModel):
    channel_id: str
    hours: int

@app.get("/")
async def root():
    return {"message": "Discord Scraper API"}

@app.get("/api/channels", response_model=List[Channel])
async def get_channels():
    """Get all available channels"""
    try:
        channels = get_guild_channels(GUILD_ID)
        if not channels:
            raise HTTPException(status_code=404, detail="No channels found")
        
        # Filter channels
        allowed_emojis = {'🟡', '🔴', '🟠', '⚫'}
        filtered_channels = [
            channel for channel in channels 
            if channel['type'] == 0 and
            len(channel['name']) > 0 and
            channel['name'][0] in allowed_emojis and
            ('godly-chat' not in channel['name'] and channel.get('position', 0) < 40)
        ]
        
        return filtered_channels
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scrape")
async def scrape_channel(request: ScrapeRequest):
    """Scrape messages from a channel"""
    try:
        print(f"\nReceived scrape request for channel {request.channel_id}, {request.hours} hours")
        
        if not request.channel_id:
            raise HTTPException(status_code=400, detail="Channel ID is required")
        
        messages = get_bot_messages(request.channel_id, hours=request.hours)
        
        print(f"Scraping complete, found {len(messages) if messages else 0} messages")
        
        return messages or []
        
    except Exception as e:
        print(f"Error in scrape_channel endpoint: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))