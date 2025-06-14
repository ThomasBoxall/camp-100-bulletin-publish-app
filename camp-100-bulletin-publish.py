# Publish Camp 100 Bulletin

from google.oauth2 import service_account
from googleapiclient.discovery import build

import requests
import base64
import yaml
import logging
import sys

# DECLARE CONSTANTS

# INITIALISE CONSTANTS TO BE POPULATED BY CONFIG FILE
GS_SPREADSHEET_ID = ""
GS_SPREADSHEET_SHEET_NAME = ""

GA_SERVICE_ACCOUNT_CREDS_PATH = ""
GA_SCOPES = []

WP_USERNAME = ""
WP_APPLICATION_PASSWORD = ""
WP_SITE_URL = ""

# INITIALISE LOGGING
logger = logging.getLogger(__name__)
logging.basicConfig(filename='camp-100-bulletin-publish.log', level=logging.INFO)

def initialise():
    # initialise the program

    logger.info("begin initialising")

    global GS_SPREADSHEET_ID, GS_SPREADSHEET_SHEET_NAME, GA_SERVICE_ACCOUNT_CREDS_PATH, GA_SCOPES, WP_USERNAME, WP_APPLICATION_PASSWORD, WP_SITE_URL

    try:
        with open('config.yml', 'r') as configYml:
            logger.info("opened config file")
            configData = yaml.safe_load(configYml)
    except FileNotFoundError as fnfError:
            logger.error('file not found')
            sys.exit()
    
    # we have found the file so crack on and read it
    GS_SPREADSHEET_ID = configData['google-sheets']['spreadsheet-id']
    GS_SPREADSHEET_SHEET_NAME = configData['google-sheets']['spreadsheet-sheet-name']

    GA_SERVICE_ACCOUNT_CREDS_PATH = configData['google-auth']['service-account-creds-path']
    GA_SCOPES = configData['google-auth']['auth-scopes']

    WP_USERNAME = configData['wordpress']['username']
    WP_APPLICATION_PASSWORD = configData['wordpress']['application-password']
    WP_SITE_URL = configData['wordpress']['site-url']

    logger.info("complete initialisation")


def main():
    logger.info("starting main execution")

    logger.info("starting google credentials validation")

    ga_creds = None
    ga_creds = service_account.Credentials.from_service_account_file(
                                filename=GA_SERVICE_ACCOUNT_CREDS_PATH, 
                                scopes=GA_SCOPES)
    
    logger.info("creds validated")

    logger.info("beginning sheet fetch")

    try:
        gs_service = build('sheets', 'v4', credentials=ga_creds)

        result = gs_service.spreadsheets().values().get(
            spreadsheetId=GS_SPREADSHEET_ID, range=GS_SPREADSHEET_SHEET_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found in the spreadsheet.')
            logger.info("no data in spreadsheet")
            return ('No data found.')
        else:
            print('Data from Google Sheet:')
            for row in values:
                print(row)
            logger.info(f'Successfully read {len(values)} rows from Google Sheet.')

            wpPostContent = buildWPPostContent(values)

            postToWP('test1', wpPostContent)
    
    except Exception as e:
        print(f"Error consuming Google Sheet: {e}")
        return (f"Error: {e}")
    
def buildWPPostContent(responseContent):
    wpPost = "<p>Published at (time)</p>"
    
    # delete the header from the spreadsheet
    del responseContent[0]

    for oneRecord in responseContent:
        if oneRecord[0] == '1':
            # to be included
            oneRecordText = f"<h3>{oneRecord[1]}</h3><p>{oneRecord[2]}</p><p>From: {oneRecord[3]}</p>"
            wpPost += oneRecordText
    
    print(wpPost)
    return wpPost

def postToWP(title, content):
    wp_credentials = f"{WP_USERNAME}:{WP_APPLICATION_PASSWORD}"
    wp_token = base64.b64encode(wp_credentials.encode()).decode('utf-8')

    wp_headers = {
        'Authorization': f'Basic {wp_token}',
        'Content-Type': 'application/json'
    }

    api_url = f"{WP_SITE_URL}/wp-json/wp/v2/posts"
    data = {
    'title' : title,
    'status': 'publish',
    'slug' : f'example-post-{title}',
    'content': content
    }
    response = requests.post(api_url,headers=wp_headers, json=data)
    print(response)

if __name__ == "__main__":
  initialise()
  main()