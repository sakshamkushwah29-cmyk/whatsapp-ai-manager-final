import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class WhatsAppService:
    def __init__(self):
        self.base_url = os.getenv("WHATSAPP_GATEWAY_URL", "http://localhost:8080")
        self.api_key = os.getenv("EVOLUTION_API_KEY", "my-evolution-api-key")
        self.headers = {"apikey": self.api_key, "Content-Type": "application/json"}

    async def create_instance(self, instance_name: str):
        """Ensure an instance exists in Evolution API"""
        url = f"{self.base_url}/instance/create"
        payload = {"instanceName": instance_name, "token": self.api_key}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers)
                return response.json()
            except Exception:
                return {"status": "already_exists"}

    async def get_qr_code(self, instance_name: str):
        """Get the QR code (Base64) for linking"""
        await self.create_instance(instance_name)
        url = f"{self.base_url}/instance/connect/{instance_name}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            return response.json()

    async def request_pairing_code(self, instance_name: str, number: str):
        """Request a 8-digit pairing code to link by phone number"""
        await self.create_instance(instance_name)
        url = f"{self.base_url}/instance/connect/pairing-code/{instance_name}"
        payload = {"number": number}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            return response.json()

    async def send_text(self, instance_name: str, number: str, text: str):
        """Send a message"""
        url = f"{self.base_url}/message/sendText/{instance_name}"
        payload = {"number": number, "text": text}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            return response.json()

whatsapp_service = WhatsAppService()
