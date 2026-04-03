import httpx

class WhatsAppService:
    def get_config(self, profile):
        """Retrieve dynamic config from DB profile"""
        base_url = profile.gateway_url or "http://localhost:8080"
        api_key = profile.gateway_api_key or "my-evolution-api-key"
        headers = {"apikey": api_key, "Content-Type": "application/json"}
        return base_url, headers

    async def create_instance(self, profile, instance_name: str):
        base_url, headers = self.get_config(profile)
        url = f"{base_url}/instance/create"
        payload = {"instanceName": instance_name, "token": profile.gateway_api_key}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                return response.json()
            except Exception:
                return {"status": "exists"}

    async def get_qr_code(self, profile, instance_name: str):
        await self.create_instance(profile, instance_name)
        base_url, headers = self.get_config(profile)
        url = f"{base_url}/instance/connect/{instance_name}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            return response.json()

    async def request_pairing_code(self, profile, instance_name: str, number: str):
        await self.create_instance(profile, instance_name)
        base_url, headers = self.get_config(profile)
        url = f"{base_url}/instance/connect/pairing-code/{instance_name}"
        payload = {"number": number}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            return response.json()

    async def send_text(self, profile, instance_name: str, number: str, text: str):
        base_url, headers = self.get_config(profile)
        url = f"{base_url}/message/sendText/{instance_name}"
        payload = {"number": number, "text": text}
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload, headers=headers)

whatsapp_service = WhatsAppService()
