import requests
import json
import os
import sys
from dotenv import load_dotenv
from colorama import Fore, Style
from datetime import datetime, timedelta, timezone

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

if not DISCORD_TOKEN:
    raise ValueError("Discord token not found. Please set DISCORD_TOKEN in environment variables.")

def find_matching_channel(channels, search_term):
    """Find channel that best matches the search term"""
    search_term = search_term.lower()
    
    for channel in channels:
        channel_name = channel['name'].lower()
        if search_term in channel_name:
            return channel
    return None

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
        print(Fore.YELLOW + "Retrieving messages from channel..." + Style.RESET_ALL)
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        print(Fore.CYAN + f"Looking for messages after: {cutoff_time} UTC" + Style.RESET_ALL)
        
        bot_messages = []
        last_message_id = None
        MAX_MESSAGES = 1000  # Safety limit
        
        while True:
            url = f'https://discord.com/api/v10/channels/{channel_id}/messages?limit=100'
            if last_message_id:
                url += f'&before={last_message_id}'
            
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(Fore.RED + f"Failed to retrieve messages: {response.status_code}" + Style.RESET_ALL)
                print(Fore.RED + f"Response: {response.text}" + Style.RESET_ALL)
                break
            
            batch = json.loads(response.text)
            
            if not batch:
                break
            
            for msg in batch:
                username = msg['author'].get('username')
                discriminator = msg['author'].get('discriminator')
                msg_time = datetime.fromisoformat(msg['timestamp'].rstrip('Z')).replace(tzinfo=timezone.utc)
                
                if username == 'FaytuksBot' and discriminator == bot_id and msg_time >= cutoff_time:
                    bot_messages.append(msg)
                    print(Fore.CYAN + f"Found message from {msg_time} UTC by {username}#{discriminator}" + Style.RESET_ALL)
            
            if len(bot_messages) >= MAX_MESSAGES:
                print(Fore.YELLOW + f"Reached maximum message limit ({MAX_MESSAGES}), stopping..." + Style.RESET_ALL)
                break
            
            if len(batch) < 100:
                break
            
            if datetime.fromisoformat(batch[-1]['timestamp'].rstrip('Z')).replace(tzinfo=timezone.utc) < cutoff_time:
                break
                
            last_message_id = batch[-1]['id']
        
        print(Fore.GREEN + f"Total messages from last {hours}h: {len(bot_messages)}" + Style.RESET_ALL)
        return bot_messages

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error retrieving messages: {e}" + Style.RESET_ALL)
        return []

def save_json(channel_name, messages):
    """Save messages to a JSON file"""
    os.makedirs('data', exist_ok=True)
    
    # Convert timestamps to local time (GMT-3)
    local_tz = timezone(timedelta(hours=-3))
    
    start_time = datetime.fromisoformat(messages[-1]['timestamp'].rstrip('Z')).replace(tzinfo=timezone.utc).astimezone(local_tz)
    end_time = datetime.fromisoformat(messages[0]['timestamp'].rstrip('Z')).replace(tzinfo=timezone.utc).astimezone(local_tz)
    
    filename = f"data/messages_{channel_name}_{start_time.strftime('%Y-%m-%d_%H-%M-%S')}_to_{end_time.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    
    print(Fore.GREEN + f"JSON data saved to {filename}" + Style.RESET_ALL)

def main():
    channels = get_guild_channels(GUILD_ID)
    if not channels:
        print(Fore.RED + "Failed to retrieve channels" + Style.RESET_ALL)
        return

    # Time range selection
    time_options = {
        1: ("Last hour", 1),
        2: ("Last 4 hours", 4),
        3: ("Last 8 hours", 8),
        4: ("Last 24 hours", 24)
    }
    
    print(Fore.YELLOW + "\nSelect time range:" + Style.RESET_ALL)
    for idx, (label, _) in time_options.items():
        print(f"{idx}. {label}")
    
    try:
        time_choice = int(input("Enter your choice (1-4): "))
        if time_choice not in time_options:
            print(Fore.RED + "Invalid time selection" + Style.RESET_ALL)
            return
        hours = time_options[time_choice][1]
    except ValueError:
        print(Fore.RED + "Invalid input" + Style.RESET_ALL)
        return

    # Use command line argument if provided, otherwise show channel selection
    if len(sys.argv) == 2:
        search_term = sys.argv[1]
        channel = find_matching_channel(channels, search_term)
    else:
        # Filter channels with specific emojis
        allowed_emojis = {'🟡', '🔴', '🟠', '⚫'}
        filtered_channels = [
            channel for channel in channels 
            if channel['type'] == 0 and 
            len(channel['name']) > 0 and
            channel['name'][0] in allowed_emojis and
            ('godly-chat' not in channel['name'] and channel.get('position', 0) < 40)
        ]

        if not filtered_channels:
            print(Fore.RED + "No channels available for selection" + Style.RESET_ALL)
            return

        print(Fore.YELLOW + "\nPlease select a channel:" + Style.RESET_ALL)
        for idx, channel in enumerate(filtered_channels, start=1):
            print(f"{idx}. {channel['name']}")

        try:
            choice = int(input("Enter channel number: "))
            if choice < 1 or choice > len(filtered_channels):
                print(Fore.RED + "Invalid selection" + Style.RESET_ALL)
                return
            channel = filtered_channels[choice - 1]
        except ValueError:
            print(Fore.RED + "Invalid input" + Style.RESET_ALL)
            return

    if not channel:
        print(Fore.RED + f"No channel found matching '{search_term}'" + Style.RESET_ALL)
        return
    
    print(Fore.GREEN + f"Found channel: {channel['name']}" + Style.RESET_ALL)
    
    messages = get_bot_messages(channel['id'], hours=hours)
    if not messages:
        print(Fore.RED + "No messages found in channel" + Style.RESET_ALL)
        return
    
    save_json(channel['name'], messages)

if __name__ == "__main__":
    main()
