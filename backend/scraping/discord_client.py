import requests
import json
import os
from datetime import datetime, timedelta, timezone
from colorama import Fore, Style
from dotenv import load_dotenv
import emoji

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

def get_guild_channels(guild_id):
    headers = {
        'Authorization': DISCORD_TOKEN
    }
    
    try:
        print(Fore.YELLOW + "Retrieving channels from server..." + Style.RESET_ALL)
        url = f'https://discord.com/api/v10/guilds/{guild_id}/channels'
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(Fore.RED + f"Failed to retrieve channels: {response.status_code}" + Style.RESET_ALL)
            return None
        
        channels = json.loads(response.text)
        return channels
            
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error retrieving channels: {e}" + Style.RESET_ALL)
        return None

def get_bot_messages(channel_id, bot_id="7032", hours=24):
    headers = {
        'Authorization': DISCORD_TOKEN
    }
    
    try:
        print(f"Starting scrape for channel {channel_id} for last {hours} hours")
        print(f"Using Discord token: {DISCORD_TOKEN[:10]}...")  # Show first 10 chars only
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        print(f"Cutoff time: {cutoff_time} UTC")
        
        bot_messages = []
        last_message_id = None
        MAX_MESSAGES = 1000
        batch_count = 0
        
        while True:
            batch_count += 1
            url = f'https://discord.com/api/v10/channels/{channel_id}/messages?limit=100'
            if last_message_id:
                url += f'&before={last_message_id}'
            
            print(f"\nFetching batch {batch_count}...")
            print(f"URL: {url}")
            
            response = requests.get(url, headers=headers)
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Error response: {response.text}")
                break
            
            batch = json.loads(response.text)
            print(f"Received {len(batch)} messages in batch")
            
            if not batch:
                print("Empty batch received, stopping")
                break
            
            # Debug first and last message timestamps in batch
            first_msg_time = datetime.fromisoformat(batch[0]['timestamp'].rstrip('Z')).replace(tzinfo=timezone.utc)
            last_msg_time = datetime.fromisoformat(batch[-1]['timestamp'].rstrip('Z')).replace(tzinfo=timezone.utc)
            print(f"Batch time range: {first_msg_time} to {last_msg_time} UTC")
            
            batch_bot_messages = 0
            for msg in batch:
                username = msg['author'].get('username')
                discriminator = msg['author'].get('discriminator')
                msg_time = datetime.fromisoformat(msg['timestamp'].rstrip('Z')).replace(tzinfo=timezone.utc)
                
                if username == 'FaytuksBot' and discriminator == bot_id and msg_time >= cutoff_time:
                    bot_messages.append(msg)
                    batch_bot_messages += 1
            
            print(f"Found {batch_bot_messages} bot messages in this batch")
            print(f"Total bot messages so far: {len(bot_messages)}")
            
            if len(bot_messages) >= MAX_MESSAGES:
                print(f"Reached message limit ({MAX_MESSAGES}), stopping")
                break
            
            if len(batch) < 100:
                print("Incomplete batch, stopping")
                break
            
            if last_msg_time < cutoff_time:
                print("Reached cutoff time, stopping")
                break
                
            last_message_id = batch[-1]['id']
            print(f"Setting last_message_id to {last_message_id}")

        print(f"\nScraping complete. Total messages found: {len(bot_messages)}")
        return bot_messages

    except Exception as e:
        print(f"Error in get_bot_messages: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return []

def find_matching_channel(channels, search_term):
    search_term = search_term.lower()
    
    for channel in channels:
        channel_name = channel['name'].lower()
        if search_term in channel_name:
            return channel
    return None