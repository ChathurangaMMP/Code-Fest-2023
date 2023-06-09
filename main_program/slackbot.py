import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
import json
import configparser
import openai
import requests
from language_api import *
from selenium_emails import *
from fuzzywuzzy import fuzz
import logging
from logging import handlers

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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s|%(levelname)s|%(funcName)s|%(message)s')
handler = handlers.TimedRotatingFileHandler(
    "logs/log_file.log", when="H", interval=24)
handler.setFormatter(formatter)
logger.addHandler(handler)

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

with open(config["OpenAI"]["document_drafting_prompt_file"], "r") as file:
    document_parameters_prompt = file.read()

with open(config["OpenAI"]["creative_content_prompt_file"], "r") as file:
    creative_content_prompt = file.read()

language_cache = {}
use_case_cache = {}
email_drafting_cache = {}
email_parameters_cache = {}
document_drafting_cache = {}
document_drafting_parameters_cache = {}
creative_content_cache = {}
creative_content_parameters_cache = {}

FIRST_STATE_ID = 1
SECOND_STATE_ID = 2
THIRD_STATE_ID = 3
FOURTH_STATE_ID = 4
FIFTH_STATE_ID = 5

english_http_nlu_endpoint = config["Rasa"]["english_http_nlu_endpoint"]

email_drafting_intents = ["compelling_introduction_email", "thank_you_email", "complaint_resolve_email",
                          "meeting_request_email", "networking_email", "persuasive_email", "apology_email", "export_gmail"]

document_drafting_intents = ["create_project_proposal", "create_bussiness_report",
                             "create_presentation", "create_user_manual", "create_legal_documents", "create_marketing_collateral", "export_to_gdoc"]

creative_content_intents = ["create_likedin_marketing_caption", "create_blog_content",
                            "create_instagram_marketing_caption", "create_datasheet_content", "export_to_gdoc"]

caches_list = [language_cache, email_drafting_cache, email_parameters_cache,
               document_drafting_cache, document_drafting_parameters_cache,
               creative_content_cache, creative_content_parameters_cache]


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    sender_id = event.get('user')
    message_text = event.get('text')
    language = "English"

    if is_fuzzy_matched_to_exit(message_text):
        clear_caches_in_exit(sender_id)
        response_text = "All the actions you started have been \
            successfully closed. \n\nIs there anything else I can assist you with?"
        return {"sender": sender_id, "response": response_text}

    if is_fuzzy_matched_to_export_gmail(message_text):
        pass
        if BOT_ID != sender_id:
            client.chat_postMessage(
                channel=channel_id, text="Email is sent successfully.")
            return

    if is_fuzzy_matched_to_export_gdoc(message_text):
        pass
        if BOT_ID != sender_id:
            client.chat_postMessage(
                channel=channel_id, text="Content is successfully exported to Google Documents.")
            return

    if sender_id not in use_case_cache:
        intent, response_text = get_intent_response(
            sender_id, message_text)

        if intent == "nlu_fallback":
            if BOT_ID != sender_id:
                client.chat_postMessage(channel=channel_id, text=response_text)
                return

        use_case_cache[sender_id] = intent

    if use_case_cache[sender_id] in email_drafting_intents:
        if sender_id not in email_drafting_cache:
            email_parameters_cache[sender_id] = {
                "initial_prompt": message_text}

            email_drafting_cache[sender_id] = FIRST_STATE_ID
            email_parameters_cache[sender_id]["follow_up_prompt"] = response_text
            if BOT_ID != sender_id:
                client.chat_postMessage(channel=channel_id, text=response_text)
                return

        else:
            if email_drafting_cache[sender_id] == FIRST_STATE_ID:
                email_parameters_cache[sender_id]["follow_up_response"] = message_text
                try:
                    email_parameters = get_email_parameter_gpt_response(
                        sender_id, email_parameters_cache[sender_id])
                except Exception as error_:
                    logger.info(
                        f'{sender_id}|OPENAI_EXTRACTION_ERROR|{error_}')
                    response_text = "Oops, We're experiencing some connection \
                        issues right now. \n\nCould you please try again?"
                    if BOT_ID != sender_id:
                        client.chat_postMessage(
                            channel=channel_id, text=response_text)
                        return

                email_parameters_cache[sender_id].update(email_parameters)
                email_drafting_cache[sender_id] = SECOND_STATE_ID

                if check_email_drafting_missing_featues(sender_id):
                    response_text = get_email_drafting_missing_feature_response(
                        sender_id)

                    if BOT_ID != sender_id:
                        client.chat_postMessage(
                            channel=channel_id, text=response_text)
                        return
                else:
                    email_drafting_cache[sender_id] = THIRD_STATE_ID

            if email_drafting_cache[sender_id] == SECOND_STATE_ID:
                missing_feature = get_email_drafting_missing_feature(sender_id)
                email_parameters_cache[sender_id][missing_feature] = message_text

                if check_email_drafting_missing_featues(sender_id):
                    response_text = get_email_drafting_missing_feature_response(
                        sender_id)
                    if BOT_ID != sender_id:
                        client.chat_postMessage(
                            channel=channel_id, text=response_text)
                        return
                else:
                    email_drafting_cache[sender_id] = THIRD_STATE_ID

            if email_drafting_cache[sender_id] == THIRD_STATE_ID:
                try:
                    generated_email_content = get_email_body_gpt_response(
                        sender_id, email_parameters_cache[sender_id])
                except Exception as error_:
                    logger.info(
                        f'{sender_id}|OPENAI_EXTRACTION_ERROR|{error_}')
                    response_text = "Oops, We're experiencing some connection \
                        issues right now. \n\t\nCould you please try again?"
                    if BOT_ID != sender_id:
                        client.chat_postMessage(
                            channel=channel_id, text=response_text)
                        return

                email_parameters_cache[sender_id]["email_body"] = generated_email_content
                email_content = email_parameters_cache[sender_id]

                content_translator(language, email_content)
                email_drafting_cache[sender_id] = FOURTH_STATE_ID

                email_parameters_cache[sender_id] = email_content
                if BOT_ID != sender_id:
                    client.chat_postMessage(
                        channel=channel_id, text=email_content["email_body"])
                    return

    elif use_case_cache[sender_id] in document_drafting_intents:
        if sender_id not in document_drafting_cache:
            document_drafting_parameters_cache[sender_id] = {
                "initial_prompt": message_text}

            document_drafting_cache[sender_id] = FIRST_STATE_ID
            document_drafting_parameters_cache[sender_id]["follow_up_prompt"] = response_text
            if BOT_ID != sender_id:
                client.chat_postMessage(channel=channel_id, text=response_text)
                return

        else:
            if document_drafting_cache[sender_id] == FIRST_STATE_ID:
                document_drafting_parameters_cache[sender_id]["follow_up_response"] = message_text
                gpt_prompt_params = document_drafting_parameters_cache[sender_id]
                del gpt_prompt_params["follow_up_prompt"]
                try:
                    document_content = get_document_content_gpt_response(
                        sender_id, gpt_prompt_params)
                except Exception as error_:
                    logger.info(
                        f'{sender_id}|OPENAI_EXTRACTION_ERROR|{error_}')
                    response_text = "Oops, We're experiencing some connection \
                        issues right now. \n\t\nCould you please try again?"
                    if BOT_ID != sender_id:
                        client.chat_postMessage(
                            channel=channel_id, text=response_text)
                        return

                content_translator(language, document_content)
                document_drafting_parameters_cache[sender_id].update(
                    {"content": document_content})
                document_drafting_cache[sender_id] = SECOND_STATE_ID

                if BOT_ID != sender_id:
                    client.chat_postMessage(
                        channel=channel_id, text=document_content)
                    return

    elif use_case_cache[sender_id] in creative_content_intents:
        if sender_id not in creative_content_cache:
            creative_content_parameters_cache[sender_id] = {
                "initial_prompt": message_text}

            creative_content_cache[sender_id] = FIRST_STATE_ID
            creative_content_parameters_cache[sender_id]["follow_up_prompt"] = response_text

            if BOT_ID != sender_id:
                client.chat_postMessage(channel=channel_id, text=response_text)
                return

        else:
            if creative_content_cache[sender_id] == FIRST_STATE_ID:
                creative_content_parameters_cache[sender_id]["follow_up_response"] = message_text
                try:
                    creative_document_content = get_creative_content_gpt_response(
                        sender_id, creative_content_parameters_cache[sender_id])
                except Exception as error_:
                    logger.info(
                        f'{sender_id}|OPENAI_EXTRACTION_ERROR|{error_}')
                    response_text = "Oops, We're experiencing some connection \
                        issues right now. \n\t\nCould you please try again?"
                    if BOT_ID != sender_id:
                        client.chat_postMessage(
                            channel=channel_id, text=response_text)
                        return

                content_translator(language, creative_document_content)
                creative_content_parameters_cache[sender_id].update(
                    {"content": creative_document_content})
                creative_content_cache[sender_id] = SECOND_STATE_ID

                if BOT_ID != sender_id:
                    client.chat_postMessage(
                        channel=channel_id, text=creative_document_content)
                    return


def get_intent_response(sender_id, message_text):
    data = json.dumps({"text": message_text})
    response = requests.request(
        "POST", english_http_nlu_endpoint, headers=headers,
        data=data)

    intent = "nlu_fallback"
    if response.status_code == 200:
        response_dict = response.json()
        logger.info(
            f'{sender_id}|RASA_INTENT_RECEIVED|{response.text.strip()}')

        intent_confidence = response_dict["intent"]["confidence"]
        if intent_confidence > float(config["Rasa"]["intent_confidence"]):
            intent = response_dict["intent"]["name"]
        else:
            intent = "nlu_fallback"

        response_text = english_intent_response[intent]

    else:
        response_text = "Oops, We're experiencing some connection \
            issues right now. \n\t\nCould you please try again?"

    return (intent, response_text)


def is_fuzzy_matched_to_export_gmail(message_text):
    similar_words = ["export to gmail", "open in gmail", "send it", "send the email",
                     "send to gmail", "copy content to gmail", "compose a new email"]
    for word in similar_words:
        similarity = fuzz.ratio(word, message_text.lower())
        if similarity >= 80:
            return True
        else:
            return False


def is_fuzzy_matched_to_export_gdoc(message_text):
    similar_words = ["export to google doc", "open in google", "send it to google documents",
                     "open the editor", "send to gdocs", "copy content to google documents"]
    for word in similar_words:
        similarity = fuzz.ratio(word, message_text.lower())
        if similarity >= 80:
            return True
        else:
            return False


def is_fuzzy_matched_to_exit(message_text):
    similarity = fuzz.ratio('exit', message_text.lower())
    if similarity >= 80:
        return True
    else:
        return False


def clear_caches_in_exit(sender_id):
    for cache in caches_list:
        if sender_id in cache:
            del cache[sender_id]


def clear_email_drafting_caches(sender_id):
    del email_drafting_cache[sender_id]
    del email_parameters_cache[sender_id]


def get_email_drafting_missing_feature(sender_id):
    email_parameters_json = email_parameters_cache[sender_id]
    if email_parameters_json["recipient_email"] == "":
        return "recipient_email"

    elif email_parameters_json["recipient_name"] == "":
        return "recipient_name"


def get_email_drafting_missing_feature_response(sender_id):
    email_parameters_json = email_parameters_cache[sender_id]
    if email_parameters_json["recipient_email"] == "":
        response_text = "Hey, it looks like the recipient's email is missing. \
            Can you provide that information?"

    elif email_parameters_json["recipient_name"] == "":
        response_text = "Hey, it looks like the recipient's name is missing. \
            Can you provide that information?"

    return response_text


def check_email_drafting_missing_featues(sender_id):
    email_parameters_json = email_parameters_cache[sender_id]
    if "" in email_parameters_json.values():
        return True
    return False


def content_translator(language, email_content):
    if language == "Sinhala":
        email_content["subject"] = english_to_sinhala_translator(
            email_content["subject"])
        email_content["email_body"] = english_to_sinhala_translator(
            email_content["email_body"])

    elif language == "Tamil":
        email_content["subject"] = english_to_tamil_translator(
            email_content["subject"])
        email_content["email_body"] = english_to_tamil_translator(
            email_content["email_body"])


def message_translator(message, language):
    if language == "English":
        message_text = message
    elif language == "Sinhala":
        message_text = sinhala_to_english_translator(message)
    elif language == "Tamil":
        message_text = tamil_to_english_translator(message)
    return message_text


def send_gpt_request(sender_id, prompt_text):
    openai.api_key = openai_gpt_api_key
    response = openai.Completion.create(
        model=config["GPT_request"]["model"],
        prompt=prompt_text,
        temperature=float(config["GPT_request"]["temperature"]),
        max_tokens=int(config["GPT_request"]["max_tokens"]),
        top_p=int(config["GPT_request"]["top_p"]),
        frequency_penalty=int(config["GPT_request"]["frequency_penalty"]),
        presence_penalty=int(config["GPT_request"]["presence_penalty"])
    )
    return response


def get_email_parameter_gpt_response(sender_id, message_text):
    prompt_text = email_parameters_prompt + \
        "\nRequest:" + str(message_text) + "\nJSON:"

    response = send_gpt_request(sender_id, prompt_text)
    response_dict = json.loads(json.dumps(response))
    logger.info(
        f'{sender_id}|OPENAI_EMAIL_PARAMETERS_RESPONSE|{response_dict}')
    response_text = json.loads(response_dict["choices"][0]["text"])
    return response_text


def get_document_content_gpt_response(sender_id, message_text):
    prompt_text = document_parameters_prompt + \
        "\nRequest:" + str(message_text) + "\nOutput:"

    response = send_gpt_request(sender_id, prompt_text)
    response_dict = json.loads(json.dumps(response))
    logger.info(
        f'{sender_id}|OPENAI_DOCUMENT_PARAMETERS_RESPONSE|{response_dict}')
    response_text = response_dict["choices"][0]["text"]
    return response_text


def get_creative_content_gpt_response(sender_id, message_text):
    prompt_text = creative_content_prompt + \
        "\nRequest:" + str(message_text) + "\nOutput:"

    response = send_gpt_request(sender_id, prompt_text)
    response_dict = json.loads(json.dumps(response))
    logger.info(
        f'{sender_id}|OPENAI_DOCUMENT_PARAMETERS_RESPONSE|{response_dict}')
    response_text = response_dict["choices"][0]["text"]
    return response_text


def get_email_body_gpt_response(sender_id, parameter_json):
    prompt_text = email_body_prompt + "\nRequest:" + \
        str(parameter_json) + "\nOutput:"

    response = send_gpt_request(sender_id, prompt_text)
    response_dict = json.loads(json.dumps(response))
    logger.info(f'{sender_id}|OPENAI_EMAIL_BODY_RESPONSE|{response_dict}')
    response_text = response_dict["choices"][0]["text"]

    return response_text


# take our flask app and run on port 5000
if __name__ == "__main__":
    app.run(debug=True)
