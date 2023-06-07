import json

response = {'id': 'cmpl-7OipbEnpphVMS4jjJ7iqpvaYXatqh', 'object': 'text_completion', 'created': 1686126559, 'model': 'text-davinci-003', 'choices': [
    {'text': " {'recipient_name': 'Sahan', 'recipient_email': 'sahan@gmail.com', 'subject': ''}", 'index': 0, 'logprobs': None, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 291, 'completion_tokens': 30, 'total_tokens': 321}}

response_text = json.loads(response["choices"][0]["text"])

print(response_text)
