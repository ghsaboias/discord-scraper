import anthropic
from typing import List
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def format_messages_for_summary(messages: List[dict]) -> str:
    """Format Discord messages into a clean text format for Claude"""
    formatted_messages = []
    
    for msg in messages:
        # Extract timestamp
        timestamp = msg.get('timestamp', '')
        
        # Extract content and embeds
        content = msg.get('content', '')
        embeds = msg.get('embeds', [])
        
        # Format embed information
        embed_text = []
        for embed in embeds:
            if embed.get('title'):
                embed_text.append(f"Title: {embed['title']}")
            if embed.get('description'):
                embed_text.append(f"Description: {embed['description']}")
            for field in embed.get('fields', []):
                if field['name'].lower() != 'source':
                    embed_text.append(f"{field['name']}: {field['value']}")
        
        # Combine all information
        message_text = f"[{timestamp}]\n"
        if content:
            message_text += f"{content}\n"
        if embed_text:
            message_text += "\n".join(embed_text) + "\n"
        
        formatted_messages.append(message_text)
    
    return "\n---\n".join(formatted_messages)

async def generate_summary(messages: List[dict]) -> str:
    """Generate a summary of the messages using Claude"""
    formatted_text = format_messages_for_summary(messages)
    
    timestamps = [datetime.fromisoformat(msg['timestamp'].rstrip('Z')).replace(tzinfo=timezone.utc) 
                 for msg in messages]
    oldest = min(timestamps)
    newest = max(timestamps)
    hours_diff = round((newest - oldest).total_seconds() / 3600, 1)
    
    prompt = f"""You are a professional news editor specializing in concise, journalistic summaries. Below are news updates from the last {hours_diff} hours.

Create a news summary following this structure:

Headline
LOCATION - Write a clear, impactful lead paragraph that captures the most important development. Include key facts like numbers, names, and dates.

Follow with an appropriate number of paragraphs that:
- Provide essential context and immediate implications
- Include relevant reactions from key figures or organizations
- Add important secondary developments, even if unrelated
- Use specific facts, numbers, and quotes where relevant

Guidelines:
- Write in clear, journalistic style (AP style)
- Lead with the most newsworthy information
- Keep paragraphs short and focused
- Use active voice
- Include specific details while remaining concise
- Maintain neutral tone
- Cover both primary news and significant secondary developments
- Include all relevant information

News Updates to Summarize:
{formatted_text}

Summary:"""

    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=2500,
            temperature=0,
            system="""You are an expert news editor that creates concise, journalistic summaries.
            Write in clear AP style with strong leads.
            Focus on specific facts and concrete details.
            Lead with the most newsworthy information.
            Include both primary developments and significant secondary events.
            Keep writing tight and focused while maintaining context.
            Use active voice and journalistic tone.""",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        raise 