from fastapi import FastAPI
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


SLACK_BOT_TOKEN = ''
slack_client = WebClient(token=SLACK_BOT_TOKEN)

app = FastAPI()


@app.post("/send_message")
async def send_message(channel_id: str, message: str):
    try:
        response = slack_client.chat_postMessage(
            channel=channel_id, text=message)
        return {"status": "success", "data": response}
    except SlackApiError as e:
        return {"status": "error", "data": e}


@app.post("/receive_message")
async def receive_message(payload: dict):
    # Handle the Slack challenge verification
    if "challenge" in payload:
        return {"challenge": payload["challenge"]}

    event = payload.get("event", {})
    text = event.get("text")
    channel_id = event.get("channel")

    # You can add your custom logic here to process the received message.
    # For example, you can send a reply to the same channel:
    if text:
        reply = f"Received your message: {text}"
        await send_message(channel_id, reply)
    return {"status": "success", "data": payload}
