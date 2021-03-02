import json
import os
from collections import OrderedDict
from datetime import datetime

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

    def __init__(self, face_encoding, now=datetime.now(tz=pytz.UTC)):
        self.id = id_gen.generate_id()
        self.first_seen_at = now
        self.last_seen_at = now

        self.face_encoding = face_encoding

    def print_details(self):
        details = 'Person `{}`:\n\tFirst seen at: `{}`\n\tLast seen at: `{}`\n\tUnseen for seconds: `{}`\n\tSeen count: `{}`\n\tReported: `{}`'.format(
            self.id,
            self.first_seen_at.astimezone(pytz.timezone(TIMEZONE)).strftime('%H:%M:%S, %d/%m/%Y'),
            self.last_seen_at.astimezone(pytz.timezone(TIMEZONE)).strftime('%H:%M:%S, %d/%m/%Y'),
            self.unseen_for_seconds,
            self.seen_count,
            self.reported,
        )
        print(details)

    @property
    def unseen_for_seconds(self):
        return (datetime.now(tz=pytz.UTC) - self.last_seen_at).total_seconds()

    def __repr__(self):
        return self.id

    def __str__(self):
        return self.__repr__()

"""
def load_people():
    # Read people data from json file
    with open(PEOPLE_JSON_PATH) as json_file:
        people_data = json.load(json_file)

    people_ordered_dict = OrderedDict()

    for i, person_data in enumerate(people_data):
        people_ordered_dict[i] = Person(
            name=person_data['name'],
            image_path=os.path.join(PEOPLE_IMG_DIR, person_data['image_path'])
        )

    return people_ordered_dict

unknown_person = Person(name='Someone')
"""