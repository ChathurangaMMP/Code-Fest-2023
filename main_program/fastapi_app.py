from fastapi import FastAPI, Request
import requests
import json
import configparser
import logging
from logging import handlers
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import openai
from language_api import *
from selenium_emails import *


class UIRequest(BaseModel):
    sender: str
    message: str
    language: str
    button: str


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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.post("/chat")
async def process_chat_request(request: Request):
    json_data = await request.json()
    request = UIRequest.parse_obj(json_data)

    sender_id = request.sender
    message = request.message
    language = request.language  # default language is English.
    button = request.button

    if language != "":
        language_cache[sender_id] = language
    else:
        language_cache[sender_id] = "English"

    message_text = message_translator(message, language)
    logger.info(f'{sender_id}|{language}|{message_text}')

    if button == "Email Drafting":
        if sender_id not in email_drafting_cache:
            email_parameters_cache[sender_id] = {
                "initial_prompt": message_text}
            intent, response_text = get_intent_response(
                sender_id, message_text)
            email_drafting_cache[sender_id] = FIRST_STATE_ID
            email_parameters_cache[sender_id]["follow_up_prompt"] = response_text
            print(response_text)
            return {"sender": sender_id, "response": response_text}

        else:
            if email_drafting_cache[sender_id] == FIRST_STATE_ID:
                email_parameters_cache[sender_id]["follow_up_response"] = response_text
                email_parameters = get_email_parameter_gpt_response(
                    sender_id, email_parameters_cache[sender_id])

                email_parameters_cache[sender_id].update(email_parameters)
                email_drafting_cache[sender_id] = SECOND_STATE_ID

                if check_email_drafting_missing_featues(sender_id):
                    response_text = get_email_drafting_missing_feature_response(
                        sender_id)
                    return {"sender_id": sender_id, "response": response_text}
                else:
                    email_drafting_cache[sender_id] = THIRD_STATE_ID

            if email_drafting_cache[sender_id] == SECOND_STATE_ID:
                missing_feature = get_email_drafting_missing_feature(sender_id)
                email_parameters_cache[sender_id][missing_feature] = message_text

                if check_email_drafting_missing_featues(sender_id):
                    response_text = get_email_drafting_missing_feature_response(
                        sender_id)
                    return {"sender_id": sender_id, "response": response_text}
                else:
                    email_drafting_cache[sender_id] = THIRD_STATE_ID

            if email_drafting_cache[sender_id] == THIRD_STATE_ID:
                email_content = get_email_body_gpt_response(
                    sender_id, email_parameters_cache[sender_id])
                content_translator(language, email_content)
                email_drafting_cache[sender_id] = FOURTH_STATE_ID
                return {"sender_id": sender_id, "response": email_content["email_body"]}


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


@app.post("/send_email")
async def process_send_email_request(request: UIRequest):
    sender_id = request.sender
    message = request.message
    language = request.language  # default language is English.
    button = request.button

    email_content = email_parameters_cache[sender_id]

    driver = set_up_chrome_driver()
    send_email(driver, email_content["recipient_email"],
               email_content["subject"], message)

    clear_email_drafting_caches(sender_id)
    return {"sender_id": sender_id, "response": "Email is sent successfully."}


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
    logger.info(f'{sender_id}|OPENAI_PROMPT_SENT')
    response = openai.Completion.create(
        model=config["GPT_request"]["model"],
        prompt=prompt_text,
        temperature=int(config["GPT_request"]["temperature"]),
        max_tokens=int(config["GPT_request"]["max_tokens"]),
        top_p=int(config["GPT_request"]["top_p"]),
        frequency_penalty=int(config["GPT_request"]["frequency_penalty"]),
        presence_penalty=int(config["GPT_request"]["presence_penalty"])
    )
    logger.info(f'{sender_id}|OPENAI_RESPONSE_RECEIVED')
    return response


def get_email_parameter_gpt_response(sender_id, message_text):
    prompt_text = email_parameters_prompt + "\nRequest:" + message_text + "\nJSON:"

    response = send_gpt_request(sender_id, prompt_text)
    response_dict = json.loads(json.dumps(response))
    response_text = json.loads(response_dict["choices"][0]["text"])

    logger.info(
        f'{sender_id}|OPENAI_EMAIL_PARAMETERS_RESPONSE|{response_dict}')
    return response_text


def get_email_body_gpt_response(sender_id, parameter_json):
    prompt_text = email_body_prompt + "\nRequest:" + \
        str(parameter_json) + "\nJSON:"

    response = send_gpt_request(sender_id, prompt_text)
    response_dict = json.loads(json.dumps(response))

    response_text = json.loads(response_dict["choices"][0]["text"])

    logger.info(f'{sender_id}|OPENAI_EMAIL_BODY_RESPONSE|{response_dict}')
    return response_text
