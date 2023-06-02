import os


def delete_default_credentials():
    credentials_path = os.path.expanduser(
        "~/.config/gcloud/application_default_credentials.json")
    if os.path.exists(credentials_path):
        os.remove(credentials_path)
        print("Default credentials deleted successfully.")
    else:
        print("No default credentials found.")


# Example usage
delete_default_credentials()

# import os
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
