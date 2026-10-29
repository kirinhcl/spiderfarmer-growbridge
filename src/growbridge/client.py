import httpx


class Client:
    def __init__(self, settings):
        self.settings = settings

    async def call(self, method, path, body=None, params=None):
        async with httpx.AsyncClient(
            base_url=self.settings.url,
            headers={"Authorization": f"Bearer {self.settings.token}"},
            timeout=90,
            trust_env=False,
        ) as client:
            response = await client.request(method, path, json=body, params=params)
            if response.is_error:
                raise RuntimeError(response.json().get("detail", "GrowBridge request failed"))
            return response.json()
