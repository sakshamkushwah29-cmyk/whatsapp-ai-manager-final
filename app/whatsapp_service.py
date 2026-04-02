import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class WhatsAppService:
    def __init__(self):
        self.base_url = os.getenv("WHATSAPP_GATEWAY_URL", "http://localhost:8080")
        self.api_key = os.getenv("EVOLUTION_API_KEY", "my-evolution-api-key")
        self.headers = {"apikey": self.api_key, "Content-Type": "application/json"}

    async def send_text(self, instance_name: str, number: str, text: str):
        """Send a text message via Evolution API"""
        url = f"{self.base_url}/message/sendText/{instance_name}"
        payload = {
            "number": number,
            "text": text
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            return response.json()

    async def get_qr_code(self, instance_name: str):
        """Get the QR code for linking the WhatsApp number"""
        url = f"{self.base_url}/instance/connect/{instance_name}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            return response.json()

whatsapp_service = WhatsAppService()
