import os

from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

PEOPLE_DIR = os.path.join(BASE_DIR, 'people')
PEOPLE_JSON_PATH = os.path.join(PEOPLE_DIR, 'people.json')
PEOPLE_IMG_DIR = os.path.join(PEOPLE_DIR, 'img')

TIMEZONE = 'Europe/Zagreb'

DETECTED_AT_THRESHOLD = 5

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

RTSP_STREAM_URL = os.getenv('RTSP_STREAM_URL')
