import os

from dotenv import load_dotenv

from argparser import argparser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

args = argparser.parse_args()

PEOPLE_DIR = os.path.join(BASE_DIR, 'people')
PEOPLE_JSON_PATH = os.path.join(PEOPLE_DIR, 'people.json')
PEOPLE_IMG_DIR = os.path.join(PEOPLE_DIR, 'img')
PEOPLE_ID_LIMIT = 100
PEOPLE_FORGET_AFTER_UNSEEN_SEC = args.people_forget_after_unseen_sec
PEOPLE_SEEN_COUNT_TO_REPORT = args.people_seen_count_to_report
PEOPLE_DRAW = args.people_draw

FRAME_SEND_EVERY_SEC = args.frame_send_every_sec

TIMEZONE = 'Europe/Zagreb'

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

STREAM_URL = args.stream if args.stream else os.getenv('STREAM')
