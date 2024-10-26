import asyncio
import json
import logging
import uuid

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from litellm import acompletion

# Configure logging
logger = logging.getLogger(__name__)


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
        self.stream_tasks = {}  # Dictionary to keep track of active streams
        logger.info(
            f"WebSocket connection established with {self.scope.get('client', '')}."
        )

    async def disconnect(self, close_code):
        # Cancel all active streams upon disconnection
        logger.info(
            f"WebSocket connection closed with code {close_code}. Cancelling all active streams."
        )
        for stream_id, task in self.stream_tasks.items():
            task.cancel()
        self.stream_tasks.clear()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "start_stream":
                await self.handle_start_stream(data)
            elif message_type == "stop_stream":
                await self.handle_stop_stream(data)
            else:
                await self.send_error("Invalid message type")
        except json.JSONDecodeError:
            logger.warning("Received invalid JSON format.")
            await self.send_error("Invalid JSON format")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            await self.send_error(f"Unexpected error: {str(e)}")

    async def handle_start_stream(self, data):
        model = data.get("model", "gpt-3.5-turbo")
        messages = data.get("messages", [])
        temperature = data.get("temperature", 0.7)

        if not messages:
            await self.send_error("Messages array is required")
            return

        if len(self.stream_tasks) >= self.MAX_CONCURRENT_STREAMS:
            await self.send_error("Maximum number of concurrent streams reached")
            return

        # Generate a unique stream ID
        stream_id = str(uuid.uuid4())

        # Start the streaming task
        task = asyncio.create_task(
            self.handle_stream(stream_id, model, messages, temperature)
        )

        # Track the task
        self.stream_tasks[stream_id] = task

        # Inform the client about the new stream ID
        await self.send(
            json.dumps(
                {
                    "type": "stream_started",
                    "stream_id": stream_id,
                    "message": "Streaming has started",
                }
            )
        )
        logger.info(f"Started stream {stream_id}.")

    async def handle_stop_stream(self, data):
        stream_id = data.get("stream_id")

        if not stream_id:
            await self.send_error("Stream ID is required to stop a stream")
            return

        task = self.stream_tasks.get(stream_id)

        if task:
            task.cancel()
            del self.stream_tasks[stream_id]
            await self.send(
                json.dumps(
                    {
                        "type": "stream_stopped",
                        "stream_id": stream_id,
                        "message": "Streaming has been stopped",
                    }
                )
            )
            logger.info(f"Stopped stream {stream_id}.")
        else:
            await self.send_error(f"No active stream found with ID: {stream_id}")

    async def handle_stream(self, stream_id, model, messages, temperature):
        try:
            logger.info(f"Handling stream {stream_id} with model {model}.")
            async for chunk in acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                api_key=settings.OPENAI_API_KEY,
                stream=True,
            ):
                content = chunk.choices[0].delta.content
                if content is not None:
                    await self.send(
                        json.dumps(
                            {
                                "type": "stream",
                                "stream_id": stream_id,
                                "content": content,
                            }
                        )
                    )
            await self.send(json.dumps({"type": "complete", "stream_id": stream_id}))
            logger.info(f"Stream {stream_id} completed successfully.")
        except asyncio.CancelledError:
            await self.send(
                json.dumps(
                    {
                        "type": "stream_cancelled",
                        "stream_id": stream_id,
                        "message": "Stream has been cancelled by the user",
                    }
                )
            )
            logger.info(f"Stream {stream_id} was cancelled by the user.")
        except Exception as e:
            await self.send(
                json.dumps({"type": "error", "stream_id": stream_id, "message": str(e)})
            )
            logger.error(f"Error in stream {stream_id}: {str(e)}", exc_info=True)

    async def send_error(self, message):
        await self.send(json.dumps({"type": "error", "message": message}))
        logger.error(f"Error sent to client: {message}")

    # Define a class-level constant for maximum concurrent streams
    MAX_CONCURRENT_STREAMS = 100  # Adjust this value based on your server capacity
