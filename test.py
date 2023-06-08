import json

response = {'id': 'cmpl-7OxKvtMYh5Kut6FEiLOXh7WkiduMk', 'object': 'text_completion', 'created': 1686182317, 'model': 'text-davinci-003', 'choices': [
    {'text': '\n{\n  "recipient_name": "Sahan",\n  "recipient_email": "sahan@gmail.com",\n  "subject": "Introduction Email",\n  "email_body": "Dear Sahan,\n\nI hope this email finds you well. I am writing to introduce myself and to make a strong first impression.\n\nI am writing to you because I am interested in learning more about your background and any specific information that can help personalize the email. Additionally, I would like to highlight any specific points that you think are important.\n\nI look forward to hearing from you soon.\n\nSincerely,\n[Your Name]"\n}', 'index': 0, 'logprobs': None, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 354, 'completion_tokens': 143, 'total_tokens': 497}}

response_text = json.loads(response["choices"][0]["text"])

print(response_text)
