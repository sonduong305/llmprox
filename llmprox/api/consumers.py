import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from litellm import acompletion


class LLMCompletionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(
            json.dumps(
                {
                    "type": "connection_established",
                    "message": "Connected to LLM completion service",
                }
            )
        )

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            model = data.get("model", "gpt-3.5-turbo")
            messages = data.get("messages", [])
            temperature = data.get("temperature", 0.7)

            if not messages:
                await self.send(
                    json.dumps(
                        {"type": "error", "message": "Messages array is required"}
                    )
                )
                return

            async for chunk in await acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                api_key=settings.OPENAI_API_KEY,
                stream=True,
            ):
                if chunk.choices[0].delta.content is not None:
                    await self.send(
                        json.dumps(
                            {
                                "type": "stream",
                                "content": chunk.choices[0].delta.content,
                            }
                        )
                    )

            await self.send(json.dumps({"type": "complete"}))

        except Exception as e:
            await self.send(json.dumps({"type": "error", "message": str(e)}))
            await self.send(json.dumps({"type": "error", "message": str(e)}))
