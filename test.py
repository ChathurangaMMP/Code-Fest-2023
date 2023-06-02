import json

response = {'id': 'cmpl-7MslvVETRYiWcyATzkAEdnzUEJAVP', 'object': 'text_completion', 'created': 1685688115, 'model': 'text-davinci-003', 'choices': [
    {'text': '\n{\n"recipient\'s name": "Sahan",\n"recipient\'s email": "sahan@gmail.com",\n"subject": "Request for Access to Project Chatbot in GitLab",\n"sender\'s name": "Unknown",\n"email body": "Dear Sahan,\n\nI am writing to request the access for the project chatbot in GitLab (project link - https://sourcecontrol.hsenidmobile.com/datascience/chatbot/multi-lingual-bot/-/blob/f6a5b173a315779efe3035e9e789974560053fca/case_handler/conf/application.ini) from you.\n\nI would be grateful if you could provide me with the access to the project chatbot.\n\nThank you for your time and consideration.\n\nSincerely,\n[Sender\'s Name]\n}', 'index': 0, 'logprobs': None, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 197, 'completion_tokens': 195, 'total_tokens': 392}}

response_dict = json.loads(json.dumps(response))
response_text = json.loads(response_dict["choices"][0]["text"][3:])
