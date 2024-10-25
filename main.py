import requests
import json
import os
from dotenv import load_dotenv
from colorama import Fore, Back, Style
from datetime import datetime
import anthropic
import emoji

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not DISCORD_TOKEN:
    raise ValueError("Discord token not found. Please set DISCORD_TOKEN in environment variables.")
if not ANTHROPIC_API_KEY:
    raise ValueError("Anthropic API key not found. Please set ANTHROPIC_API_KEY in environment variables.")

def get_guild_channels(guild_id):
    headers = {
        'Authorization': DISCORD_TOKEN
    }
    
    try:
        print(Fore.YELLOW + f"Attempting to retrieve channels for guild {guild_id}..." + Style.RESET_ALL)
        print(Fore.CYAN + f"Using token: {DISCORD_TOKEN[:10]}...{DISCORD_TOKEN[-10:]}" + Style.RESET_ALL)
        
        response = requests.get(
            f'https://discord.com/api/v10/guilds/{guild_id}/channels',
            headers=headers
        )
        
        print(Fore.YELLOW + f"Response status code: {response.status_code}" + Style.RESET_ALL)
        
        if response.status_code != 200:
            print(Fore.RED + f"Failed to retrieve channels: {response.status_code} - {response.reason}" + Style.RESET_ALL)
            print(Fore.RED + f"Response content: {response.text}" + Style.RESET_ALL)
            return
        
        channels = json.loads(response.text)
        
        # Filter channels based on emoji and type
        filtered_channels = [
            channel for channel in channels 
            if channel['type'] == 0 and  # 0 is the type for text channels
            len(emoji.emoji_list(channel['name'])) == 1 and # Only one emoji at the start
            ('godly-chat' not in channel['name'] and channel.get('position', 0) < 40)
        ]
        
        # Sort filtered channels by position
        filtered_channels.sort(key=lambda x: x.get('position', 0))
        
        # Remove specified keys from each channel
        keys_to_remove = ['type', 'icon_emoji', 'nsfw', 'rate_limit_per_user', 'theme_color', 'permission_overwrites', 'guild_id', 'flags']
        for channel in filtered_channels:
            for key in keys_to_remove:
                channel.pop(key, None)
        
        print(Fore.GREEN + f"Filtered channels in guild {guild_id} (sorted by position):" + Style.RESET_ALL)
        for channel in filtered_channels:
            print(Fore.CYAN + f"ID: {channel['id']}, Name: {channel['name']}, Position: {channel.get('position', 'N/A')}" + Style.RESET_ALL)
        
        # Save to file
        with open('channels.txt', 'w', encoding='utf-8') as f:
            json.dump(filtered_channels, f, indent=2)
        print(Fore.GREEN + f"Filtered channels data saved to channels.txt" + Style.RESET_ALL)
            
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"An error occurred while retrieving channels: {e}" + Style.RESET_ALL)

# The retrieve_messages function is kept for reference, but not used in this example
def retrieve_messages(channel_id, keywords=None):
    headers = {
        'authorization': DISCORD_TOKEN
    }
    
    try:
        response = requests.get(
            f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers
        )
        
        if response.status_code != 200:
            print(Fore.RED + f"Failed to retrieve messages: {response.status_code} - {response.reason}" + Style.RESET_ALL)
            return
        
        messages = json.loads(response.text)
        
        with open('messages.txt', 'w', encoding='utf-8') as f:
            for message in messages:
                author = message['author']['username']
                author_id = message['author']['id']
                timestamp = message['timestamp']
                content = message['content']
                embeds = message.get('embeds', [])
                
                f.write(f"Author: {author} (ID: {author_id})\n")
                f.write(f"Date: {timestamp}\n")
                f.write(f"Content: {content}\n")
                
                if embeds:
                    f.write("Embeds:\n")
                    for i, embed in enumerate(embeds, 1):
                        f.write(f"  Embed {i}:\n")
                        if 'title' in embed:
                            f.write(f"    Title: {embed['title']}\n")
                        if 'description' in embed:
                            f.write(f"    Description: {embed['description']}\n")
                        if 'url' in embed:
                            f.write(f"    URL: {embed['url']}\n")
                        if 'timestamp' in embed:
                            f.write(f"    Timestamp: {embed['timestamp']}\n")
                        if 'footer' in embed:
                            f.write(f"    Footer: {embed['footer'].get('text', '')}\n")
                
                f.write("\n---\n\n")
                
                # Console output for each message
                print(Fore.CYAN + f"Author: {author} (ID: {author_id}), Time: {timestamp}, Content: {content}\n" + Style.RESET_ALL)
                
            print(Fore.GREEN + f"Messages saved to output.txt" + Style.RESET_ALL)
            
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"An error occurred while retrieving messages: {e}" + Style.RESET_ALL)

def get_bot_messages(channel_id, bot_id="7032"):
    headers = {
        'Authorization': DISCORD_TOKEN
    }
    
    try:
        response = requests.get(
            f'https://discord.com/api/v10/channels/{channel_id}/messages?limit=100',
            headers=headers
        )
        
        if response.status_code != 200:
            print(Fore.RED + f"Failed to retrieve messages for channel {channel_id}: {response.status_code} - {response.reason}" + Style.RESET_ALL)
            return []
        
        messages = json.loads(response.text)
        
        # Filter messages by FaytuksBot#7032
        bot_messages = [
            msg for msg in messages
            if msg['author'].get('username') == 'FaytuksBot' and msg['author'].get('discriminator') == bot_id
        ]
        
        print(Fore.CYAN + f"Retrieved {len(bot_messages)} messages from channel {channel_id}" + Style.RESET_ALL)
        
        return bot_messages

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"An error occurred while retrieving messages for channel {channel_id}: {e}" + Style.RESET_ALL)
        return []

def save_bot_messages_to_file():
    with open('channels.txt', 'r', encoding='utf-8') as f:
        channels = json.load(f)
    
    all_bot_messages = []
    
    for channel in channels:
        channel_id = channel['id']
        channel_name = channel['name']
        print(Fore.YELLOW + f"Retrieving messages from channel: {channel_name}" + Style.RESET_ALL)
        
        bot_messages = get_bot_messages(channel_id)
        if bot_messages:
            all_bot_messages.extend([{**msg, 'channel_name': channel_name} for msg in bot_messages])
    
    # Sort all messages by timestamp (newest first)
    all_bot_messages.sort(key=lambda x: x['timestamp'], reverse=True)
    
    with open('output.txt', 'w', encoding='utf-8') as f:
        for message in all_bot_messages:
            timestamp = datetime.fromisoformat(message['timestamp'].rstrip('Z')).strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"Channel: {message['channel_name']}\n")
            f.write(f"Date: {timestamp}\n")
            f.write(f"Content: {message['content']}\n")
            
            if message.get('embeds'):
                f.write("Embeds:\n")
                for i, embed in enumerate(message['embeds'], 1):
                    f.write(f"  Embed {i}:\n")
                    if 'title' in embed:
                        f.write(f"    Title: {embed['title']}\n")
                    if 'description' in embed:
                        f.write(f"    Description: {embed['description']}\n")
                    if 'url' in embed:
                        f.write(f"    URL: {embed['url']}\n")
            
            f.write("\n---\n\n")
    
    print(Fore.GREEN + f"Bot messages saved to output.txt" + Style.RESET_ALL)

def get_channel_summary(channel_name, messages):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    content = f"""Analyze the following messages from the '{channel_name}' channel and provide the latest news updates:

    {'-' * 40}

    """
    for msg in messages:
        timestamp = datetime.fromisoformat(msg['timestamp'].rstrip('Z')).strftime('%Y-%m-%d %H:%M:%S')
        content += f"""
        Date: {timestamp}
        Content: {msg['embeds']}
        """
    
    content += f"""
    {'-' * 40}

    Provide a concise report of the latest news updates from these messages. Focus on specific, recent events related to {channel_name}. For each update, include:

    1. Date
    2. Location
    3. Event description
    4. Parties involved
    5. Relevant numbers

    Format each update as a bullet point. Use clear, direct language. Prioritize the most recent and significant events. If there are no specific news updates, state that clearly.
    """

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": content}
            ]
        )
        return response.content[0].text
    except Exception as e:
        print(Fore.RED + f"An error occurred while getting summary for channel {channel_name}: {e}" + Style.RESET_ALL)
        return None

def save_bot_messages_and_summaries():
    with open('channels.txt', 'r', encoding='utf-8') as f:
        channels = json.load(f)
    
    all_summaries = []
    
    for channel in channels:
        channel_id = channel['id']
        channel_name = channel['name']
        print(Fore.YELLOW + f"Retrieving messages from channel: {channel_name}" + Style.RESET_ALL)
        
        bot_messages = get_bot_messages(channel_id)
        if bot_messages:
            summary = get_channel_summary(channel_name, bot_messages)
            if summary:
                all_summaries.append({
                    'channel_name': channel_name,
                    'summary': summary,
                    'message_count': len(bot_messages)
                })
    
    with open('output.txt', 'w', encoding='utf-8') as f:
        for summary in all_summaries:
            f.write(f"Channel: {summary['channel_name']}\n")
            f.write(f"Messages analyzed: {summary['message_count']}\n")
            f.write(f"Latest Updates:\n{summary['summary']}\n")
            f.write(f"{'-' * 80}\n\n")
    
    print(Fore.GREEN + f"Channel summaries saved to output.txt" + Style.RESET_ALL)

if __name__ == "__main__":
    save_bot_messages_and_summaries()
