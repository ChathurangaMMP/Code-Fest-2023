import json
from google_auth_oauthlib import flow
from google.auth import default, exceptions
import subprocess
import shutil
import os
import uuid
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery

# Install Google Cloud SDK if not already installed


def install_google_cloud_sdk():
    if not shutil.which('gcloud'):
        subprocess.run(['curl', 'https://sdk.cloud.google.com',
                       '--output', 'install_google_cloud_sdk.sh'])
        subprocess.run(['chmod', '+x', 'install_google_cloud_sdk.sh'])
        subprocess.run(['./install_google_cloud_sdk.sh', '--disable-prompts'])
        subprocess.run(['rm', 'install_google_cloud_sdk.sh'])
        print("Google Cloud SDK installed successfully.")
    else:
        print("Google Cloud SDK is already installed.")

# Create project using gcloud CLI


def create_project(project_id, project_name):
    create_cmd = ['gcloud', 'projects', 'create',
                  project_id, '--name', project_name]
    subprocess.run(create_cmd)

# Set up default credentials


def set_up_default_credentials(scopes):
    subprocess.run(['gcloud', 'auth', 'application-default', 'login'])
    subprocess.run(['gcloud', 'auth', 'application-default',
                   'print-access-token'], capture_output=True)
    subprocess.run(['gcloud', 'config', 'list'], capture_output=True)


# 1

scopes = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/gmail.send']
project_id = 'taskbuddyai-731'
project_name = 'TaskBuddyAI-1'

install_google_cloud_sdk()
create_project(project_id, project_name)
set_up_default_credentials(scopes)

# Fetch client ID, client secret, and project ID


def fetch_client_info():
    try:
        credentials, project_id = default()
        client_id = credentials.client_id
        client_secret = credentials.client_secret
        return client_id, client_secret, project_id
    except exceptions.DefaultCredentialsError:
        print("Unable to fetch client information.")
        return None, None, None


# Example usage
client_id, client_secret, project_id = fetch_client_info()

print(client_id, client_secret, project_id)

credentials = {
    'installed': {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uris': [],
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://accounts.google.com/o/oauth2/token'
    }
}

with open('client_secrets/client_secret.json', 'w') as file:
    json.dump(credentials, file)


# List of required APIs
required_apis = ['https://www.googleapis.com/auth/gmail.compose',
                 'https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/calendar']


flow = InstalledAppFlow.from_client_secrets_file(
    'client_secrets/client_secret.json',
    scopes=['https://www.googleapis.com/auth/gmail.send']
)

credentials = flow.run_console()

service = googleapiclient.discovery.build(
    'gmail', 'v1', credentials=credentials)

print('done')


def create_message(sender, to, subject, message_text):
    message = {
        'raw': base64.urlsafe_b64encode(
            f'From: {sender}\nTo: {to}\nSubject: {subject}\n\n{message_text}'
            .encode('utf-8')
        ).decode('utf-8')
    }
    return message


def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(
            userId=user_id, body=message).execute()
        print('Message sent!')
        return message
    except Exception as e:
        print(f'An error occurred: {e}')
        return None
