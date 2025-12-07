import aiohttp, asyncio, os

# Load OpenAI API Key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

async def gpt4o(message, lang):
    """
    Use OpenAI API to generate human-like responses for Instagram DMs
    """
    session = aiohttp.ClientSession()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    # System prompt to make responses human-like and casual for Instagram DMs
    system_prompt = f"""You are a friendly human chatting on Instagram DMs. 
Rules:
- Respond in {lang} language
- Keep responses SHORT (1-2 sentences max, like real texting)
- Be casual, friendly, and natural like a real person
- Use lowercase mostly, occasional emojis are okay but don't overdo it
- NEVER mention you're an AI or assistant
- NEVER use formal language or bullet points
- Respond like you're texting a friend
- Match the energy of the message you receive"""

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        "max_tokens": 150,
        "temperature": 0.9
    }
    
    try:
        async with session.post(
            'https://api.openai.com/v1/chat/completions',
            json=payload,
            headers=headers
        ) as res:
            if res.status == 200:
                data = await res.json()
                response = data['choices'][0]['message']['content']
                await session.close()
                return response.strip()
            else:
                error = await res.text()
                print(f"OpenAI API Error: {error}")
                await session.close()
                return "hey, sorry my phone's acting weird rn 😅"
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        await session.close()
        return "hmm something went wrong, text me again?"

