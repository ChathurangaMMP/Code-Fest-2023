import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
import json
import configparser
import openai
from language_api import *
from selenium_emails import *

# finds the path and loads the .env file
env_path = Path('.') / 'slackbot/.env'
load_dotenv(dotenv_path=env_path)

# configure flask app
app = Flask(__name__)

slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)

# loads the Bot User OAuth Token from the .env file and passes as the token
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']

config = configparser.ConfigParser()
config.read("conf/application.ini")
headers = {"Content-Type": "application/json"}

openai_gpt_api_key = config["OpenAI"]["gpt_api_key"]

with open(config["Rasa"]["english_intent_response"], "r") as file:
    english_intent_response = json.load(file)

with open(config["OpenAI"]["email_parameters_prompt_file"], "r") as file:
    email_parameters_prompt = file.read()

with open(config["OpenAI"]["email_body_prompt_file"], "r") as file:
    email_body_prompt = file.read()

language_cache = {}
email_drafting_cache = {}
email_parameters_cache = {}

FIRST_STATE_ID = 1
SECOND_STATE_ID = 2
THIRD_STATE_ID = 3
FOURTH_STATE_ID = 4
FIFTH_STATE_ID = 5

english_http_nlu_endpoint = config["Rasa"]["english_http_nlu_endpoint"]


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if BOT_ID != user_id:
        if text == "hi":
            client.chat_postMessage(channel=channel_id, text="hello")
        else:
            client.chat_postMessage(channel=channel_id, text=text)


# take our flask app and run on port 5000
if __name__ == "__main__":
    app.run(debug=True)
