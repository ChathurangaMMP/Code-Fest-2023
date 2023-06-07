import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter

# finds the path and loads the .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# configure flask app
app = Flask(__name__)

# add the slackevenadapter which allows to handle different events being sent to us
# from the slackapi and to send the event to the route
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)

# loads the Bot User OAuth Token from the .env file and passes as the token
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']


# function to handle the events,
# when a message is sent we're going to call this function and going to take the payload
# that was sent , the payload consists of the message details
@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if BOT_ID != user_id:
        client.chat_postMessage(channel=channel_id, text=text)


# take our flask app and run on port 5000
if __name__ == "__main__":
    app.run(debug=True)
