import requests
import json
import os
import sys
from dotenv import load_dotenv
from colorama import Fore, Style
from datetime import datetime, timedelta, timezone
import anthropic
import emoji
import time

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not DISCORD_TOKEN:
    raise ValueError("Discord token not found. Please set DISCORD_TOKEN in environment variables.")
if not ANTHROPIC_API_KEY:
    raise ValueError("Anthropic API key not found. Please set ANTHROPIC_API_KEY in environment variables.")

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

def get_bot_messages(channel_id, bot_id="7032"):
    headers = {
        'Authorization': DISCORD_TOKEN
    }
    
    try:
        print(Fore.YELLOW + "Retrieving messages from channel..." + Style.RESET_ALL)
        
        # Get 24 hours ago instead of midnight
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=1)
        print(Fore.CYAN + f"Looking for messages after: {cutoff_time} UTC" + Style.RESET_ALL)
        
        all_messages = []
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
                print(Fore.YELLOW + "No more messages in batch" + Style.RESET_ALL)
                break
            
            # Debug first and last message in batch
            first_msg_time = datetime.fromisoformat(batch[0]['timestamp'].rstrip('Z')).replace(tzinfo=timezone.utc)
            last_msg_time = datetime.fromisoformat(batch[-1]['timestamp'].rstrip('Z')).replace(tzinfo=timezone.utc)
            print(Fore.CYAN + f"Batch time range: {first_msg_time} to {last_msg_time} UTC" + Style.RESET_ALL)
            
            # Filter messages from last 24 hours
            recent_messages = []
            for msg in batch:
                msg_time = datetime.fromisoformat(msg['timestamp'].rstrip('Z')).replace(tzinfo=timezone.utc)
                if msg_time >= cutoff_time:
                    recent_messages.append(msg)
                    # Debug message info
                    print(Fore.CYAN + f"Found message from {msg_time} by {msg['author'].get('username')}#{msg['author'].get('discriminator', 'N/A')}" + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + f"Message from {msg_time} is older than 24 hours, stopping..." + Style.RESET_ALL)
                    break
            
            all_messages.extend(recent_messages)
            
            # Stop if we've hit the message limit
            if len(all_messages) >= MAX_MESSAGES:
                print(Fore.YELLOW + f"Reached maximum message limit ({MAX_MESSAGES}), stopping..." + Style.RESET_ALL)
                break
            
            # If we found any messages older than cutoff, stop fetching
            if len(recent_messages) < len(batch):
                break
            
            # If no more messages in batch, stop
            if len(batch) < 100:
                print(Fore.YELLOW + "Incomplete batch, stopping..." + Style.RESET_ALL)
                break
                
            print(Fore.CYAN + f"Retrieved batch of {len(recent_messages)} messages from last 24h. Total so far: {len(all_messages)}" + Style.RESET_ALL)
            
            last_message_id = batch[-1]['id']
        
        # Filter for bot messages with more detailed debugging
        bot_messages = []
        for msg in all_messages:
            username = msg['author'].get('username')
            discriminator = msg['author'].get('discriminator')
            if username == 'FaytuksBot' and discriminator == bot_id:
                bot_messages.append(msg)
                print(Fore.GREEN + f"Found bot message from {username}#{discriminator}" + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + f"Skipping message from {username}#{discriminator}" + Style.RESET_ALL)
        
        print(Fore.GREEN + f"Total messages from today: {len(all_messages)}" + Style.RESET_ALL)
        print(Fore.GREEN + f"Bot messages from today: {len(bot_messages)}" + Style.RESET_ALL)
        
        if not bot_messages:
            print(Fore.YELLOW + "No bot messages found from today" + Style.RESET_ALL)
        
        return bot_messages

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error retrieving messages: {e}" + Style.RESET_ALL)
        return []

def get_channel_summary(channel_name, messages):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    print(Fore.YELLOW + "Analyzing messages with Claude..." + Style.RESET_ALL)
    
    BATCH_SIZE = 50
    message_batches = [messages[i:i + BATCH_SIZE] for i in range(0, len(messages), BATCH_SIZE)]
    
    system_prompt = """
    You are an experienced news analyst tasked with summarizing a sequence of events from a series of messages. Your goal is to create a clear, concise, and objective summary that highlights the most critical events without repetition or unnecessary details.

    ### Requirements:

    1. **Format:**
    - Begin with a summary title in the format "Event Type – Location (Date Range)" to give a clear overview of the topic and timeframe.
    - Add a brief, one- or two-sentence summary encapsulating the overall situation.
    - List events as bullet points with timestamps in the format `[HH:MM]`.
    - For multiple events on the same day, group related updates together to avoid redundancy.

    2. **Content Selection:**
    - Include only essential events that significantly impact the overall narrative.
    - Exclude minor details, repeated information, and unrelated messages.
    - Ensure events are listed in chronological order from earliest to latest.

    3. **Style and Tone:**
    - Use objective, action-oriented language in each event description, focusing on what changed or happened.
    - Specify unresolved details if outcomes or specifics are unknown, noting that the situation may still be developing.
    - Maintain a neutral, factual, emotionless tone suitable for a broad audience.
    """

    all_content = []
    for batch_num, batch in enumerate(message_batches, 1):
        print(Fore.CYAN + f"Processing batch {batch_num}/{len(message_batches)}..." + Style.RESET_ALL)
        
        batch_content = f"Messages from '{channel_name}':\n{'-' * 40}\n"
        for msg in batch:
            timestamp = datetime.fromisoformat(msg['timestamp'].rstrip('Z')).strftime('%Y-%m-%d %H:%M:%S')
            batch_content += f"Date: {timestamp}\nContent: {msg['embeds']}\n"
        all_content.append(batch_content)
    
    # Single API call with all content
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": f"Analyze and summarize these messages:\n\n{'-' * 40}\n".join(all_content)
            }]
        )
        return response.content[0].text
        
    except Exception as e:
        print(Fore.RED + f"Error processing messages: {e}" + Style.RESET_ALL)
        raise e

def save_output(channel_name, messages, summary):
    os.makedirs('summaries', exist_ok=True)
    
    start_time = datetime.fromisoformat(messages[-1]['timestamp'].rstrip('Z')).strftime('%Y-%m-%d_%H-%M-%S')
    end_time = datetime.fromisoformat(messages[0]['timestamp'].rstrip('Z')).strftime('%Y-%m-%d_%H-%M-%S')
    
    summary_filename = f"summaries/summary_{channel_name}_{start_time}_to_{end_time}.txt"
    with open(summary_filename, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(Fore.GREEN + f"Summary saved to {summary_filename}" + Style.RESET_ALL)

def main():
    channels = get_guild_channels(GUILD_ID)
    if not channels:
        print(Fore.RED + "Failed to retrieve channels" + Style.RESET_ALL)
        return

    # Handle channel selection
    if len(sys.argv) == 2:
        search_term = sys.argv[1]
    else:
        allowed_emojis = {'🟡', '🔴', '🟠', '⚫'}
        filtered_channels = [
            channel for channel in channels 
            if channel['type'] == 0 and  # 0 is the type for text channels
            len(emoji.emoji_list(channel['name'])) == 1 and # Only one emoji at the start
            channel['name'][0] in allowed_emojis and
            ('godly-chat' not in channel['name'] and channel.get('position', 0) < 40)
        ]

        if not filtered_channels:
            print(Fore.RED + "No channels available for selection" + Style.RESET_ALL)
            return

        print(Fore.YELLOW + "Please select a channel from the list below:" + Style.RESET_ALL)
        for idx, channel in enumerate(filtered_channels, start=1):
            print(f"{idx}. {channel['name']}")

        try:
            choice = int(input("Enter the number of the channel you want to select: "))
            if choice < 1 or choice > len(filtered_channels):
                print(Fore.RED + "Invalid selection" + Style.RESET_ALL)
                return
            channel = filtered_channels[choice - 1]
        except ValueError:
            print(Fore.RED + "Invalid input" + Style.RESET_ALL)
            return

        search_term = channel['name']

    channel = find_matching_channel(channels, search_term)
    if not channel:
        print(Fore.RED + f"No channel found matching '{search_term}'" + Style.RESET_ALL)
        print(Fore.YELLOW + "Available channels:" + Style.RESET_ALL)
        for ch in channels:
            print(f"- {ch['name']}")
        return
    
    print(Fore.GREEN + f"Found channel: {channel['name']}" + Style.RESET_ALL)
    
    messages = get_bot_messages(channel['id'])
    if not messages:
        print(Fore.RED + "No messages found in channel" + Style.RESET_ALL)
        return
    
    summary = get_channel_summary(channel['name'], messages)
    if not summary:
        print(Fore.RED + "Failed to generate summary" + Style.RESET_ALL)
        return
    
    save_output(channel['name'], messages, summary)

if __name__ == "__main__":
    main()
