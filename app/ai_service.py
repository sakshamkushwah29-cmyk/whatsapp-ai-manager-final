import os
from bytez import Bytez
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.key = os.getenv("BYTEZ_KEY")
        self.sdk = Bytez(self.key)
        self.model_name = "Qwen/Qwen3-0.6B"
        self.model = self.sdk.model(self.model_name)

    def generate_response(self, user_message: str, history: list = None, profile: object = None, knowledge: str = ""):
        """
        profile: BusinessProfile object from DB
        knowledge: Combined text from all uploaded files
        """
        system_prompt = f"""
        You are an expert AI assistant for {profile.brand_name}.
        Website: {profile.website_link}
        
        YOUR PRIMARY GOAL:
        {profile.primary_goal}
        
        TONE & PERSONALITY:
        {profile.brand_tone}
        
        GREETING STYLE:
        {profile.greeting_message}
        
        HANDLING OBJECTIONS:
        {profile.common_objections}
        
        BUSINESS KNOWLEDGE BASE (USE THIS TO ANSWER):
        {knowledge}
        
        RULES:
        1. Keep responses concise and naturally conversational for WhatsApp.
        2. If you don't know an answer, don't make it up. Refer to the knowledge base or ask them to wait for a human.
        3. Always guide the user towards the Primary Goal.
        """

        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            messages.extend(history)
            
        messages.append({"role": "user", "content": user_message})

        try:
            results = self.model.run(messages)
            if results.error:
                return f"I'm sorry, I'm having a technical issue. Please try again in a moment."
            return results.output
        except Exception:
            return "I'm currently busy helping other customers. Please wait a moment."

ai_service = AIService()
