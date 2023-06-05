from fastapi import FastAPI
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

language_cache = {}
use_case_cache = {}
email_drafting_cache = {}
email_parameters_cache = {}

FIRST_STATE_ID = 1
SECOND_STATE_ID = 2
THIRD_STATE_ID = 3


@app.post("/chat")
async def process_chat_request(request: UIRequest):
    sender_id = request.sender
    message = request.message
    language = request.language  # default language is English.
    button = request.button

    # if is_button:
    #     if button == "email_drafting":
    #         use_case_cache[sender_id] = "email_drafting"
    #         return {"sender_id": sender_id, "response": ""}

    if language != "":
        language_cache[sender_id] = language

    if message != "" and email_parameters_cache[sender_id]["recipient_name"] != "":
        message_text = message_translator(message, language)
    logger.info(f'{sender_id}|{language}|{message_text}')

    if sender_id in email_drafting_cache and email_drafting_cache[sender_id] == FIRST_STATE_ID:
        pass

    if use_case_cache[sender_id] == "email_drafting":
        if sender_id not in email_drafting_cache:
            email_parameters = get_email_parameter_gpt_response(
                sender_id, message_text)
            email_parameters["overview"] = message_text
            email_drafting_cache[sender_id] = FIRST_STATE_ID
            email_parameters_cache[sender_id] = email_parameters

            if check_email_drafting_missing_featues(sender_id):
                response_text = get_email_drafting_missing_feature_response(
                    sender_id)
                return {"sender_id": sender_id, "response": response_text}

        email_content = get_email_body_gpt_response(
            sender_id, email_parameters)

        content_translator(language, email_content)

        driver = set_up_chrome_driver()
        send_email(driver, email_content["recipient_email"],
                   email_content["subject"], email_content["email_body"])


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
    prompt_text = "Extract the following list of features from the given text \
        and return the results as a JSON. The subject feature needs to be generated \
            according to the purpose of the email.\n\nlist of features=\
                [recipient_name, recipient_email, subject]. If a feature is missing, \
                    add "" as the value to the JSON.\
                    \n\nRequest:" + message_text + "\nJSON:"

    response = send_gpt_request(sender_id, prompt_text)
    response_dict = json.loads(json.dumps(response))
    response_text = json.loads(response_dict["choices"][0]["text"])

    logger.info(
        f'{sender_id}|OPENAI_EMAIL_PARAMETERS_RESPONSE|{response_dict}')
    return response_text


def get_email_body_gpt_response(sender_id, parameter_json):
    prompt_text = "Generate an email body content according to the following details. \
        Use followings as the keys in JSON response. Keys= \
        [recipient_name, recipient_email, subject, email_body]\
                    \n\nRequest:" + str(parameter_json) + "\nJSON:"

    response = send_gpt_request(sender_id, prompt_text)
    response_dict = json.loads(json.dumps(response))
    print(response_dict)
    response_text = json.loads(response_dict["choices"][0]["text"])

    logger.info(f'{sender_id}|OPENAI_EMAIL_BODY_RESPONSE|{response_dict}')
    return response_text
