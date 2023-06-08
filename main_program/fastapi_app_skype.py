from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity


class MyBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        text = turn_context.activity.text
        response = f"You said: {text}"
        await turn_context.send_activity(MessageFactory.text(response))


app = FastAPI()
adapter = BotFrameworkAdapter(BotFrameworkAdapterSettings(
    "<Microsoft App ID>", "<Microsoft App Password>"))
bot = MyBot()


@app.post("/api/chat")
async def messages(request: Request):
    body = await request.json()
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization")
    response = await adapter.process_activity(activity, auth_header, bot.on_turn)
    if response:
        return JSONResponse(status_code=response.status, content=response.body)
    return Response(status_code=204)
