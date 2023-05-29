from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity


#  secret ID - b67916cf-b40c-40b0-92e0-f44fe4cd4d95
# ngrok authtoken - 2Q5ZhI4w9jKLYcK7qZtMngwuq0R_26BDNyEk6o5FGyxVp4mAd
# temp url - https://c5f7-2407-c00-d004-5c51-6abf-c46c-41f3-49a0.ngrok-free.app
# slack app token - xoxb-5300103418852-5294684594885-9K580jYrkK0OXFUZzJuiGozJ

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
