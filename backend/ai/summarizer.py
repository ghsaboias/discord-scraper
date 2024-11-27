import anthropic
from typing import List
import os
from dotenv import load_dotenv

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
    
    prompt = f"""You are a helpful AI assistant. Below are news updates from various sources. 
Please provide a clear, concise summary of the key information, organized by topic.
Focus on the most important developments and maintain a neutral tone. Don't include opinions, speculation or introductory phrases.

News Updates:
{formatted_text}

Please provide a summary in the following format:
- A brief 2-3 sentence overview of the main developments
- Bullet points of key points by topic

Summary:"""

    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            temperature=0,
            system="You are a helpful AI assistant that specializes in summarizing news and information clearly and concisely. You return the summary in the format specified above, without any introductory phrases or additional commentary.",
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