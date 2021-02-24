import json
import os
from collections import OrderedDict
from datetime import datetime

import face_recognition
import pytz

from settings import PEOPLE_JSON_PATH, PEOPLE_IMG_DIR, TIMEZONE


class Person:
    last_seen_at = datetime.min.replace(tzinfo=pytz.UTC)
    last_seen_face_location = None

    detected_at = datetime.min.replace(tzinfo=pytz.UTC)
    detected_face_location = None
    detected_img = None

    def __init__(self, name, image_path=None):
        self.name = name

        if image_path:
            image = face_recognition.load_image_file(image_path)
            self.face_encoding = face_recognition.face_encodings(image)[0]
        else:
            self.face_encoding = None

    def msg_door(self):
        return '`{}` is at the door at `{}`.'.format(
            self.name,
            self.detected_at.astimezone(pytz.timezone(TIMEZONE)).strftime('%H:%M:%S, %d/%m/%Y')
        )

    @property
    def detected_at_ts(self):
        return int(datetime.timestamp(self.detected_at) * 1000)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


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
