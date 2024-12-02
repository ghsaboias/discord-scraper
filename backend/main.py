from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import json
import asyncio
from ai.summarizer import generate_summary
from datetime import datetime, timedelta, timezone
import requests

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
            (
                len(channel['name']) > 0 and
                channel['name'][0] in allowed_emojis and
                ('godly-chat' not in channel['name'] and channel.get('position', 0) < 30)
                or channel['parent_id'] == '1112044935982633060'
            ) 
        ]
        
        return filtered_channels
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def event_generator(channel_id: str, hours: int):
    """Generate SSE events for message updates"""
    try:
        last_message_id = None
        batch_count = 0
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        while True:
            batch_count += 1
            print(f"\nFetching batch {batch_count}...")
            
            # Get batch of messages
            batch = get_batch_messages(channel_id, last_message_id)
            if not batch:
                break
                
            # Process batch and get bot messages
            bot_messages = []
            for msg in batch:
                msg_time = datetime.fromisoformat(msg['timestamp'].rstrip('Z')).replace(tzinfo=timezone.utc)
                if (msg['author'].get('username') == 'FaytuksBot' and 
                    msg['author'].get('discriminator') == '7032' and 
                    msg_time >= cutoff_time):
                    bot_messages.append(msg)
            
            # Send this batch's bot messages immediately
            if bot_messages:
                yield f"data: {json.dumps(bot_messages)}\n\n"
                await asyncio.sleep(0.1)  # Small delay between batches
            
            # Check if we should stop
            last_msg_time = datetime.fromisoformat(batch[-1]['timestamp'].rstrip('Z')).replace(tzinfo=timezone.utc)
            if last_msg_time < cutoff_time:
                break
                
            last_message_id = batch[-1]['id']
            
        # Send completion event
        yield "event: complete\ndata: null\n\n"
        
    except Exception as e:
        print(f"Error in event generator: {str(e)}")
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

def get_batch_messages(channel_id: str, last_message_id: Optional[str] = None):
    """Helper function to get a batch of messages"""
    headers = {'Authorization': DISCORD_TOKEN}
    url = f'https://discord.com/api/v10/channels/{channel_id}/messages?limit=100'
    if last_message_id:
        url += f'&before={last_message_id}'
        
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
        
    return json.loads(response.text)

@app.get("/api/scrape/{channel_id}")
async def scrape_channel(channel_id: str, hours: int = 24):
    """Scrape messages from a channel with SSE"""
    try:
        # Validate hours parameter
        if hours not in [6, 12, 24, 48, 72]:
            hours = 24  # Default to 24 if invalid value
            
        return StreamingResponse(
            event_generator(channel_id, hours),
            media_type="text/event-stream",
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            }
        )
    except Exception as e:
        print(f"Error in scrape endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/summarize")
async def summarize_messages(request: dict):
    """Generate an AI summary of the messages"""
    try:
        messages = request.get("messages", [])
        hours = request.get("hours", 24)  # Default to 24 hours if not specified
        
        # Filter messages based on timeframe
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        filtered_messages = [
            msg for msg in messages 
            if datetime.fromisoformat(msg['timestamp'].rstrip('Z')).replace(tzinfo=timezone.utc) >= cutoff_time
        ]
        
        if not filtered_messages:
            raise HTTPException(status_code=400, detail="No messages found in the specified timeframe")
        
        summary = await generate_summary(filtered_messages)
        return {"summary": summary}
    except Exception as e:
        print(f"Error in summarize endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))