import httpx

class WhatsAppService:
    def get_config(self, profile):
        """Retrieve dynamic config from DB profile"""
        base_url = (profile.gateway_url or "http://localhost:8080").rstrip("/")
        api_key = profile.gateway_api_key or "my-evolution-api-key"
        headers = {"apikey": api_key, "Content-Type": "application/json"}
        return base_url, headers

    async def create_instance(self, profile, instance_name: str):
        base_url, headers = self.get_config(profile)
        url = f"{base_url}/instance/create"
        payload = {"instanceName": instance_name, "token": profile.gateway_api_key}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                return response.json()
            except Exception as e:
                return {"status": "error", "message": str(e)}

    async def get_qr_code(self, profile, instance_name: str):
        base_url, headers = self.get_config(profile)
        # 1. Try to create/check instance
        await self.create_instance(profile, instance_name)
        
        # 2. Get QR
        url = f"{base_url}/instance/connect/{instance_name}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, headers=headers)
                return response.json()
            except Exception as e:
                return {"error": f"Connection failed: {str(e)}"}

    async def request_pairing_code(self, profile, instance_name: str, number: str):
        base_url, headers = self.get_config(profile)
        await self.create_instance(profile, instance_name)
        
        url = f"{base_url}/instance/connect/pairing-code/{instance_name}"
        # Sanitize number: remove + and spaces
        clean_number = "".join(filter(str.isdigit, number))
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(f"{url}?number={clean_number}", headers=headers)
                return response.json()
            except Exception as e:
                return {"error": f"Pairing failed: {str(e)}"}

    async def send_text(self, profile, instance_name: str, number: str, text: str):
        base_url, headers = self.get_config(profile)
        url = f"{base_url}/message/sendText/{instance_name}"
        payload = {"number": number, "text": text}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                await client.post(url, json=payload, headers=headers)
            except Exception as e:
                print(f"Send Message Error: {e}")

whatsapp_service = WhatsAppService()
