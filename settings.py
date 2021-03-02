import os

from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

PEOPLE_DIR = os.path.join(BASE_DIR, 'people')
PEOPLE_JSON_PATH = os.path.join(PEOPLE_DIR, 'people.json')
PEOPLE_IMG_DIR = os.path.join(PEOPLE_DIR, 'img')
PEOPLE_ID_LIMIT = 1000
PEOPLE_FORGET_AFTER_UNSEEN_SEC = 60
PEOPLE_SEEN_COUNT_TO_REPORT = 10

TIMEZONE = 'Europe/Zagreb'

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

RTSP_STREAM_URL = os.getenv('RTSP_STREAM_URL')
