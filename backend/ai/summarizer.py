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
    
    prompt = f"""You are a news analyst specializing in clear, structured summaries. Below are news updates from various sources. 
Please provide a summary in the following strict format:

[Main Topic/Region] Update - [Current Date]

Overview:
Write a focused 2-3 sentence overview covering the most significant developments. If there are multiple unrelated but important developments, mention them all briefly.

Key Developments:

[Primary Event/Topic]:
- Detailed point with specific facts (numbers, names, locations)
- Another specific point with clear impact or significance
- Additional key detail with concrete information

[Secondary Developments]:
- Important but separate development with specific details
- Another significant but unrelated event
- Additional noteworthy development from different area/topic

[Additional Details/Impact]:
- Clear, factual point with specific information
- Another detailed development
- Final key point with concrete details

Guidelines:
- Primary category should cover the main event/crisis
- Secondary Developments category must include other significant events, even if unrelated
- Each bullet point must contain specific facts (numbers, names, locations)
- Include both major developments and significant tangential events
- Maintain clear cause-and-effect relationships
- Avoid vague language or speculation
- Keep a neutral, analytical tone

News Updates to Summarize:
{formatted_text}

Summary:"""

    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1500,
            temperature=0,
            system="""You are an expert news analyst that creates clear, structured summaries.
Focus on specific facts and concrete details.
Avoid vague language like 'multiple', 'various', or 'several'.
Use precise numbers, names, and locations whenever possible.
Include both primary events and significant secondary developments.
Ensure no important information is omitted, even if it seems tangential.
Maintain consistent formatting and professional tone.""",
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