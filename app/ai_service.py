import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv("BYTEZ_KEY")
        self.base_url = "https://api.bytez.com/models/v2/Qwen/Qwen3-4B"

    async def generate_response(self, user_message: str, history: list = None, profile: object = None, knowledge: str = ""):
        system_prompt = f"""
        You are the AI assistant for {profile.brand_name}.
        Website: {profile.website_link}
        Goal: {profile.primary_goal}
        Tone: {profile.brand_tone}
        Greeting: {profile.greeting_message}
        Objections: {profile.common_objections}
        Knowledge: {knowledge}
        
        Keep it WhatsApp-friendly, short, and effective.
        """

        messages = [{"role": "system", "content": system_prompt}]
        if history: messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        payload = {
            "messages": messages,
            "stream": False,
            "params": {
                "temperature": 0.7,
                "max_length": 500
            }
        }

        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.base_url, json=payload, headers=headers, timeout=30.0)
                result = response.json()
                if "output" in result and "content" in result["output"]:
                    return result["output"]["content"]
                return "I'm processing your request, please hold on."
            except Exception as e:
                print(f"AI Error: {e}")
                return "Our team is currently busy. Please wait a moment."

ai_service = AIService()
