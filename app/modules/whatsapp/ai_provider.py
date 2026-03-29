"""DeepSeek AI Provider — The Brain of AFAQ WhatsApp Bot."""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

SYSTEM_PROMPT = """You are AFAQ Beauty's intelligent WhatsApp assistant. You are professional, warm, and knowledgeable about beauty products.

STORE INFO:
- AFAQ Beauty is the official UAE distributor of ENZO Italy & Lizze Brazil
- Located in Deira, Dubai, UAE
- Products: Hair dryers, straighteners, trimmers, clippers, curling irons, hair care products
- Brands: ENZO Professional, Lizze Professional, Wahl, Babyliss, Philips, Braun

YOUR ROLE:
1. Answer product questions accurately
2. Help customers find the right product for their needs
3. Provide pricing information when asked
4. Guide customers through ordering
5. Handle complaints with empathy
6. Be concise — WhatsApp messages should be brief and clear

LANGUAGE DETECTION:
- If customer writes in Arabic, respond in Arabic
- If customer writes in English, respond in English
- Match the customer's language style

RESPONSE STYLE:
- Be friendly and professional
- Use emojis sparingly for WhatsApp
- Keep responses under 200 words
- Always offer to help further
- If you don't know something, say so honestly

PRODUCT KNOWLEDGE:
- ENZO Professional Dryer: High-power, ionic technology, ceramic coating
- ENZO Straightener: Tourmaline plates, adjustable temp, auto-shutoff
- Lizze Extreme Dryer: Brazilian design, powerful motor
- Wahl Senior Clipper: Professional barber clipper, cord/cordless
- Babyliss Pro: Premium styling tools

PRICING NOTE: Always say "Let me check the latest price for you" and direct them to the pricing menu or connect with a human agent for exact pricing.
"""


async def generate_ai_response(message: str, context=None) -> str:
    if not DEEPSEEK_API_KEY:
        return None

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if context:
        for msg in context[-6:]:
            role = "user" if msg.get("direction") == "inbound" else "assistant"
            messages.append({"role": role, "content": msg.get("message", "")})

    messages.append({"role": "user", "content": message})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "max_tokens": 500,
                    "temperature": 0.7,
                    "stream": False
                }
            )

            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            else:
                print(f"DeepSeek API error: {response.status_code} - {response.text}")
                return None

    except Exception as e:
        print(f"DeepSeek API exception: {e}")
        return None


async def generate_contextual_response(message, conversation_history, customer_name=None):
    if not DEEPSEEK_API_KEY:
        return None

    context_prompt = f"Customer name: {customer_name or 'Unknown'}\n"
    context_prompt += "Recent conversation:\n"

    for msg in conversation_history[-10:]:
        sender = "Customer" if msg.get("direction") == "inbound" else "Bot"
        context_prompt += f"{sender}: {msg.get('message', '')}\n"

    full_message = f"{context_prompt}\nCurrent message: {message}"
    return await generate_ai_response(full_message)