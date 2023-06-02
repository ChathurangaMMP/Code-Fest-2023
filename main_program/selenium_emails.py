# google-chrome --remote-debugging-port=9222

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up Chrome driver

options = Options()
options.add_argument('--start-maximized')  # Maximize the browser window
# Replace with the actual remote debugging URL
options.add_experimental_option('debuggerAddress', 'localhost:9222')


# Replace with the actual path to the Chrome profile directory
# options.add_argument('--user-data-dir=/home/prasad/git-projects/codefest/chrome-profile')
driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=options)


def send_email(sender, recipients, subject, message):
    # Get the list of tab URLs
    tab_urls = driver.window_handles

    # Check if Gmail is open
    is_gmail_open = False

    for handle in tab_urls:
        driver.switch_to.window(handle)
        url = driver.current_url
        print(url)
        if 'mail.google.com' in url:
            is_gmail_open = True
            break

    if is_gmail_open:
        print("Gmail window is open")
    else:
        print("Gmail window is not open")

    # Perform actions on the Gmail tab, e.g., click the compose button
    compose_button = driver.find_element(By.XPATH, '//div[text()="Compose"]')
    compose_button.click()

    # Automate the compose mail process, e.g., fill in recipients, subject, and message body

    recipient_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[19]/div/div/div/div[1]/div[3]/div[1]/div[1]/div/div/div/div[3]/div/div/div[4]/table/tbody/tr/td[2]/form/div[1]/table/tbody/tr[1]/td[2]/div/div/div[1]/div/div[3]/div/div/div/div/div/input')))

    recipient_input.send_keys(recipients)

    subject_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'subjectbox')))
    subject_input.send_keys(subject)

    message_body = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@role="textbox"]')))
    message_body.send_keys(message)


# # Sign in to Gmail
# email = "prasad.c@hsenidmobile.com"
# password = ""


# def login_google():
#     try:
#         driver.get("https://accounts.google.com/signin/v2/identifier?continue=https://mail.google.com/mail/&service=mail&sacu=1&rip=1&flowName=GlifWebSignIn&flowEntry=ServiceLogin")
#         driver.implicitly_wait(15)

#         loginBox = driver.find_element(By.ID, 'identifierId')
#         loginBox.send_keys(email)

#         nextButton = driver.find_element(By.ID, 'identifierNext')
#         nextButton.click()

#         time.sleep(2)

#         passWordBox = driver.find_element(
#             By.XPATH, '//*[@id="password"]/div[1]/div / div[1]/input')
#         passWordBox.send_keys(password)

#         nextButton = driver.find_element(By.ID, 'passwordNext')
#         nextButton.click()

#         print("Login Successful...!!")
#     except:
#         print("Login Failed")
