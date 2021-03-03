import json
import os
from datetime import datetime

import face_recognition
import pytz

from settings import PEOPLE_JSON_PATH, PEOPLE_IMG_DIR, TIMEZONE, PEOPLE_ID_LIMIT


class IdGenerator:
    current_id = 0

    def generate_id(self):
        if self.current_id == PEOPLE_ID_LIMIT - 1:
            self.current_id = 0
        self.current_id += 1
        return self.current_id


id_gen = IdGenerator()


class FramePerson:
    seen_count = 1
    reported = False
    name = None

    def __init__(self, face_encoding, now=datetime.now(tz=pytz.UTC)):
        self.id = id_gen.generate_id()
        self.first_seen_at = now
        self.last_seen_at = now

        self.face_encoding = face_encoding

    def print_details(self):
        details = 'Person `{}`:\n\tFirst seen at: `{}`\n\tLast seen at: `{}`\n\tUnseen for seconds: `{}`\n\tSeen count: `{}`\n\tReported: `{}`\n\tName: `{}`'.format(
            self.id,
            self.first_seen_at.astimezone(pytz.timezone(TIMEZONE)).strftime('%H:%M:%S, %d/%m/%Y'),
            self.last_seen_at.astimezone(pytz.timezone(TIMEZONE)).strftime('%H:%M:%S, %d/%m/%Y'),
            self.unseen_for_seconds,
            self.seen_count,
            self.reported,
            self.name,
        )
        print(details)

    def print_slim_details(self):
        details = 'Person `{}`:\n\tUnseen for seconds: `{}`\n\tSeen count: `{}`\n\tReported: `{}`\n\tName: `{}`'.format(
            self.id,
            self.unseen_for_seconds,
            self.seen_count,
            self.reported,
            self.name,
        )
        print(details)

    def door_message(self):
        return '`{}` is at the door.'.format(
            self.name if self.name else 'Person #{}'.format(self.id)
        )

    def label_text(self):
        return self.name if self.name else 'Person {}'.format(self.id)

    @property
    def unseen_for_seconds(self):
        return (datetime.now(tz=pytz.UTC) - self.last_seen_at).total_seconds()

    def __repr__(self):
        return self.id

    def __str__(self):
        return self.__repr__()


def load_people():
    # Read people data from json file
    with open(PEOPLE_JSON_PATH) as json_file:
        people_json = json.load(json_file)

    known_people_face_encodings = []
    known_people_names = []

    for person_json in people_json:
        image = face_recognition.load_image_file(os.path.join(PEOPLE_IMG_DIR, person_json['image_path']))
        face_encoding = face_recognition.face_encodings(image)[0]
        known_people_face_encodings.append(face_encoding)
        known_people_names.append(person_json['name'])

    return known_people_face_encodings, known_people_names
