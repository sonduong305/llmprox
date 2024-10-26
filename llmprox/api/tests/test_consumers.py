# # File: llmprox/api/tests/test_consumers.py

# import json
# from unittest.mock import AsyncMock, patch

# import pytest
# from channels.testing import WebsocketCommunicator

# from config.asgi import app  # Ensure this points to your ASGI application
# from llmprox.api.consumers import LLMCompletionConsumer


# @pytest.mark.asyncio
# async def test_connection_established():
#     communicator = WebsocketCommunicator(app, "/ws/api/v1/completion/")
#     connected, _ = await communicator.connect()
#     assert connected
#     message = await communicator.receive_json_from()
#     assert message["type"] == "connection_established"
#     assert message["message"] == "Connected to LLM completion service"
#     await communicator.disconnect()


# @pytest.mark.asyncio
# async def test_start_stream_success():
#     communicator = WebsocketCommunicator(app, "/ws/api/v1/completion/")
#     connected, _ = await communicator.connect()
#     assert connected
#     await communicator.receive_json_from()  # connection_established

#     # Mock the acompletion function
#     with patch(
#         "llmprox.api.consumers.acompletion", new_callable=AsyncMock
#     ) as mock_acompletion:
#         # Simulate streaming chunks
#         mock_stream = AsyncMock()
#         mock_stream.__aiter__.return_value = [
#             AsyncMock(choices=[AsyncMock(delta=AsyncMock(content="Hello! "))]),
#             AsyncMock(
#                 choices=[
#                     AsyncMock(delta=AsyncMock(content="How can I assist you today?"))
#                 ]
#             ),
#         ]
#         mock_acompletion.return_value = mock_stream

#         # Send start_stream message
#         start_message = {
#             "type": "start_stream",
#             "model": "gpt-3.5-turbo",
#             "messages": [{"role": "user", "content": "Hello!"}],
#             "temperature": 0.7,
#         }
#         await communicator.send_json_to(start_message)

#         # Receive stream_started message
#         stream_started = await communicator.receive_json_from()
#         assert stream_started["type"] == "stream_started"
#         stream_id = stream_started["stream_id"]

#         # Receive streamed messages
#         stream_message1 = await communicator.receive_json_from()
#         assert stream_message1["type"] == "stream"
#         assert stream_message1["stream_id"] == stream_id
#         assert stream_message1["content"] == "Hello! "

#         stream_message2 = await communicator.receive_json_from()
#         assert stream_message2["type"] == "stream"
#         assert stream_message2["stream_id"] == stream_id
#         assert stream_message2["content"] == "How can I assist you today?"

#         # Receive complete message
#         complete_message = await communicator.receive_json_from()
#         assert complete_message["type"] == "complete"
#         assert complete_message["stream_id"] == stream_id

#     await communicator.disconnect()


# @pytest.mark.asyncio
# async def test_stop_stream_success():
#     communicator = WebsocketCommunicator(app, "/ws/api/v1/completion/")
#     connected, _ = await communicator.connect()
#     assert connected
#     await communicator.receive_json_from()  # connection_established

#     # Mock the acompletion function to include a long-running stream
#     with patch(
#         "llmprox.api.consumers.acompletion", new_callable=AsyncMock
#     ) as mock_acompletion:
#         mock_stream = AsyncMock()
#         mock_stream.__aiter__.return_value = [
#             AsyncMock(choices=[AsyncMock(delta=AsyncMock(content="Processing... "))]),
#             # The stream will be cancelled before the second chunk
#         ]
#         mock_acompletion.return_value = mock_stream

#         # Send start_stream message
#         start_message = {
#             "type": "start_stream",
#             "model": "gpt-3.5-turbo",
#             "messages": [
#                 {"role": "user", "content": "Start streaming and stop early."}
#             ],
#             "temperature": 0.7,
#         }
#         await communicator.send_json_to(start_message)

#         # Receive stream_started message
#         stream_started = await communicator.receive_json_from()
#         stream_id = stream_started["stream_id"]

#         # Receive first streamed message
#         stream_message1 = await communicator.receive_json_from()
#         assert stream_message1["type"] == "stream"
#         assert stream_message1["stream_id"] == stream_id
#         assert stream_message1["content"] == "Processing... "

#         # Send stop_stream message
#         stop_message = {"type": "stop_stream", "stream_id": stream_id}
#         await communicator.send_json_to(stop_message)

#         # Receive stream_stopped message
#         stream_stopped = await communicator.receive_json_from()
#         assert stream_stopped["type"] == "stream_stopped"
#         assert stream_stopped["stream_id"] == stream_id
#         assert stream_stopped["message"] == "Streaming has been stopped"

#     await communicator.disconnect()


# @pytest.mark.asyncio
# async def test_start_stream_without_messages():
#     communicator = WebsocketCommunicator(app, "/ws/api/v1/completion/")
#     connected, _ = await communicator.connect()
#     assert connected
#     await communicator.receive_json_from()  # connection_established

#     # Send start_stream message without messages
#     start_message = {
#         "type": "start_stream",
#         "model": "gpt-3.5-turbo",
#         "temperature": 0.7,
#     }
#     await communicator.send_json_to(start_message)

#     # Receive error message
#     error_message = await communicator.receive_json_from()
#     assert error_message["type"] == "error"
#     assert error_message["message"] == "Messages array is required"

#     await communicator.disconnect()


# @pytest.mark.asyncio
# async def test_stop_nonexistent_stream():
#     communicator = WebsocketCommunicator(app, "/ws/api/v1/completion/")
#     connected, _ = await communicator.connect()
#     assert connected
#     await communicator.receive_json_from()  # connection_established

#     # Send stop_stream message with invalid stream_id
#     stop_message = {"type": "stop_stream", "stream_id": "nonexistent-stream-id"}
#     await communicator.send_json_to(stop_message)

#     # Receive error message
#     error_message = await communicator.receive_json_from()
#     assert error_message["type"] == "error"
#     assert (
#         error_message["message"]
#         == "No active stream found with ID: nonexistent-stream-id"
#     )

#     await communicator.disconnect()


# @pytest.mark.asyncio
# async def test_max_concurrent_streams():
#     communicator = WebsocketCommunicator(app, "/ws/api/v1/completion/")
#     connected, _ = await communicator.connect()
#     assert connected
#     await communicator.receive_json_from()  # connection_established

#     # Mock acompletion to simulate immediate completion
#     with patch(
#         "llmprox.api.consumers.acompletion", new_callable=AsyncMock
#     ) as mock_acompletion:
#         mock_stream = AsyncMock()
#         mock_stream.__aiter__.return_value = [
#             AsyncMock(choices=[AsyncMock(delta=AsyncMock(content="Stream 1"))]),
#         ]
#         mock_acompletion.return_value = mock_stream

#         # Define the maximum concurrent streams
#         max_streams = LLMCompletionConsumer.MAX_CONCURRENT_STREAMS

#         # Start maximum allowed streams
#         stream_ids = []
#         for _ in range(max_streams):
#             start_message = {
#                 "type": "start_stream",
#                 "model": "gpt-3.5-turbo",
#                 "messages": [{"role": "user", "content": "Hello!"}],
#                 "temperature": 0.7,
#             }
#             await communicator.send_json_to(start_message)
#             stream_started = await communicator.receive_json_from()
#             stream_ids.append(stream_started["stream_id"])

#         # Attempt to start one more stream beyond the limit
#         start_message = {
#             "type": "start_stream",
#             "model": "gpt-3.5-turbo",
#             "messages": [{"role": "user", "content": "This should fail."}],
#             "temperature": 0.7,
#         }
#         await communicator.send_json_to(start_message)
#         error_message = await communicator.receive_json_from()
#         assert error_message["type"] == "error"
#         assert (
#             error_message["message"] == "Maximum number of concurrent streams reached"
#         )

#     await communicator.disconnect()
