import requests
import json
import os
import sys
from dotenv import load_dotenv
from colorama import Fore, Style
from datetime import datetime, timedelta, timezone
import emoji
import shutil

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
        
        # Get messages from specified hours ago
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
                print(Fore.YELLOW + "No more messages in batch" + Style.RESET_ALL)
                break
            
            # Debug first and last message in batch
            first_msg_time = datetime.fromisoformat(batch[0]['timestamp'].rstrip('Z')).replace(tzinfo=timezone.utc)
            last_msg_time = datetime.fromisoformat(batch[-1]['timestamp'].rstrip('Z')).replace(tzinfo=timezone.utc)
            print(Fore.CYAN + f"Batch time range: {first_msg_time} to {last_msg_time} UTC" + Style.RESET_ALL)
            
            for msg in batch:
                username = msg['author'].get('username')
                discriminator = msg['author'].get('discriminator')
                msg_time = convert_to_local(msg['timestamp'], fmt=None)
                if username == 'FaytuksBot' and discriminator == bot_id and msg_time >= cutoff_time:
                    bot_messages.append(msg)
                    print(Fore.CYAN + f"Found message from {msg_time} by {msg['author'].get('username')}#{msg['author'].get('discriminator', 'N/A')}" + Style.RESET_ALL)
            
            # Stop if we've hit the message limit
            if len(bot_messages) >= MAX_MESSAGES:
                print(Fore.YELLOW + f"Reached maximum message limit ({MAX_MESSAGES}), stopping..." + Style.RESET_ALL)
                break
            
            # If no more messages in batch, stop
            if len(batch) < 100:
                print(Fore.YELLOW + "Incomplete batch, stopping..." + Style.RESET_ALL)
                break
            
            if last_msg_time < cutoff_time:
                print(Fore.YELLOW + "Reached cutoff time, stopping..." + Style.RESET_ALL)
                break
                
            print(Fore.CYAN + f"Retrieved batch of {len(bot_messages)} messages from last {hours}h. Total so far: {len(bot_messages)}" + Style.RESET_ALL)
            
            last_message_id = batch[-1]['id']
        
        print(Fore.GREEN + f"Total messages from last {hours}h: {len(bot_messages)}" + Style.RESET_ALL)
        
        if not bot_messages:
            print(Fore.YELLOW + f"No bot messages found from last {hours}h" + Style.RESET_ALL)
        
        return bot_messages

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error retrieving messages: {e}" + Style.RESET_ALL)
        return []
    
def convert_to_local(utc_timestamp, fmt='%Y-%m-%d %H:%M:%S'):
    """Convert UTC timestamp string to local time (GMT-3)"""
    utc_time = datetime.fromisoformat(utc_timestamp.rstrip('Z')).replace(tzinfo=timezone.utc)
    local_time = utc_time.astimezone(timezone(timedelta(hours=-3)))
    return local_time.strftime(fmt) if fmt else local_time

def format_message_to_html(msg):
    """Convert a Discord message to HTML format"""
    timestamp = convert_to_local(msg['timestamp'])
    
    # Start message div and prepare source/timestamp line
    html = '<div class="message">'
    
    # Extract source from fields if it exists
    source = None
    if msg.get('embeds'):
        for embed in msg['embeds']:
            if embed.get('fields'):
                for field in embed['fields']:
                    if field.get('name', '').lower() == 'source':
                        source = field.get('value', '')
                        break
    
    # If no source found in embeds, use message content  
    if not source and msg.get('content'):
        source = msg['content'].lower()
    
    # Add source and timestamp in the same line
    html += '<div class="header">'
    if source:
        source_text = source
        if 'http' in source.lower():
            url_start = source.find('http')
            url_end = len(source)
            for char in [' ', '\n', ')']:
                pos = source.find(char, url_start)
                if pos != -1:
                    url_end = min(url_end, pos)
            url = source[url_start:url_end]
            source_text = f'<a href="{url}" target="_blank">{url}</a>'
        html += f'<span class="source">Source: {source_text}</span>'
    html += f'<span class="timestamp">{timestamp} (GMT-3)</span></div>'
    
    # Rest of the message formatting remains the same...
    if msg.get('embeds'):
        for embed in msg['embeds']:
            if embed.get('description') or any(
                field.get('name', '').lower() != 'source' and field.get('value')
                for field in embed.get('fields', [])
            ):
                html += '<div class="embed">'
                if embed.get('description'):
                    html += f'<div class="embed-description">{embed["description"]}</div>'
                if embed.get('fields'):
                    html += '<div class="embed-fields">'
                    for field in embed['fields']:
                        if field.get('name', '').lower() != 'source' and field.get('value'):
                            html += f'<div class="field"><div class="field-name">{field.get("name", "")}</div>'
                            html += f'<div class="field-value">{field.get("value", "")}</div></div>'
                    html += '</div>'
                html += '</div>'
    
    if msg.get('attachments'):
        html += '<div class="attachments-grid">'
        for attachment in msg['attachments']:
            content_type = attachment.get('content_type', '')
            if content_type.startswith('image/'):
                html += f'''
                    <div class="attachment-item">
                        <img src="{attachment["url"]}" 
                             alt="{attachment["filename"]}" 
                             class="attachment-img"
                             loading="lazy">
                    </div>'''
            elif content_type.startswith('video/'):
                html += f'''
                    <div class="attachment-item">
                        <video controls class="attachment-video">
                            <source src="{attachment["url"]}" type="{content_type}">
                            Your browser does not support the video tag.
                        </video>
                    </div>'''
        html += '</div>'
    
    html += '</div>'
    return html

def create_html_report(channel_name, messages):
    """Create an HTML report from the messages"""
    # Read template files
    template_dir = os.path.join(os.path.dirname(__file__), 'assets')
    
    with open(os.path.join(template_dir, 'report_template.html'), 'r', encoding='utf-8') as f:
        html_template = f.read()
    
    messages_html = '\n'.join(format_message_to_html(msg) for msg in reversed(messages))
    
    # Get time range in local time
    start_time = convert_to_local(messages[-1]['timestamp'])
    end_time = convert_to_local(messages[0]['timestamp'])
    
    html_content = html_template.format(
        channel=channel_name,
        timestamp=datetime.now(timezone(timedelta(hours=-3))).strftime('%Y-%m-%d %H:%M:%S'),
        message_count=len(messages),
        time_range=f'{start_time} to {end_time} (GMT-3)',
        messages=messages_html
    )
    
    return html_content

def save_output(channel_name, messages, html_content):
    """Save the report"""
    os.makedirs('summaries', exist_ok=True)
    
    # Save the report
    start_time = convert_to_local(messages[-1]['timestamp'], '%Y-%m-%d_%H-%M-%S')
    end_time = convert_to_local(messages[0]['timestamp'], '%Y-%m-%d_%H-%M-%S')
    
    filename = f"summaries/report_{channel_name}_{start_time}_to_{end_time}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(Fore.GREEN + f"Report saved to {filename}" + Style.RESET_ALL)

def files_are_identical(path1, path2):
    """Compare two files to see if they are identical"""
    if not os.path.exists(path1) or not os.path.exists(path2):
        return False
        
    with open(path1, 'rb') as f1, open(path2, 'rb') as f2:
        return f1.read() == f2.read()

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

    # Channel selection (existing code)
    if len(sys.argv) == 2:
        search_term = sys.argv[1]
    else:
        allowed_emojis = {'🟡', '🔴', '🟠', '⚫'}
        filtered_channels = [
            channel for channel in channels 
            if channel['type'] == 0 and  
            len(emoji.emoji_list(channel['name'])) == 1 and 
            channel['name'][0] in allowed_emojis and
            ('godly-chat' not in channel['name'] and channel.get('position', 0) < 40)
        ]

        if not filtered_channels:
            print(Fore.RED + "No channels available for selection" + Style.RESET_ALL)
            return

        print(Fore.YELLOW + "\nPlease select a channel from the list below:" + Style.RESET_ALL)
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
    
    messages = get_bot_messages(channel['id'], hours=hours)
    if not messages:
        print(Fore.RED + "No messages found in channel" + Style.RESET_ALL)
        return
    
    html_content = create_html_report(channel['name'], messages)
    save_output(channel['name'], messages, html_content)

if __name__ == "__main__":
    main()
