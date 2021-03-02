import logging
from datetime import datetime
from time import sleep

import cv2
import face_recognition
import numpy as np
import pytz

from camera import VideoStream
from discord import DiscordReporter
from people import FramePerson
from settings import RTSP_STREAM_URL, DISCORD_WEBHOOK_URL, PEOPLE_FORGET_AFTER_UNSEEN_SEC, PEOPLE_SEEN_COUNT_TO_REPORT


def get_frame():
    # Grab a single frame of video
    frame = video_stream.read()

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = frame[:, :, ::-1]

    return frame, rgb_frame


def find_best_match(frame_face_encoding, people_face_encodings):
    # Try to find match in current people
    match_person = None
    if people_face_encodings:
        # Find all matches with people
        matches = face_recognition.compare_faces(people_face_encodings, frame_face_encoding)

        # Find best match
        face_distances = face_recognition.face_distance(people_face_encodings, frame_face_encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            # Match found
            match_person = people[best_match_index]
            match_person.seen_count += 1
            match_person.last_seen_at = now

    return match_person


# Init logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)

# Load people
#logging.info('Loading people.')
#people_ordered_dict = load_people()
#people_face_encodings = [person.face_encoding for person in people_ordered_dict.values()]

logging.info('Initializing camera.')
# Get a reference to video stream
video_stream = VideoStream(RTSP_STREAM_URL).start()

logging.info('Initializing discord reporter.')
discord_reporter = DiscordReporter(DISCORD_WEBHOOK_URL).start()

logging.info('Looping.')
people = []
while True:
    now = datetime.now(tz=pytz.UTC)
    logging.info('Parsing frame.')

    # Get frame
    frame, rgb_frame = get_frame()

    # Find all face locations and face encodings in the current frame of video
    frame_face_locations = face_recognition.face_locations(rgb_frame)
    frame_face_encodings = face_recognition.face_encodings(rgb_frame, frame_face_locations)

    # Extract face_encodings of all current people
    people_face_encodings = [person.face_encoding for person in people]
    for frame_face_encoding in frame_face_encodings:
        match_person = find_best_match(frame_face_encoding, people_face_encodings)

        # If the match was not found create new person
        if not match_person:
            person = FramePerson(frame_face_encoding, now)
            people.append(person)

    # report people if they have not been reported and have been seen PEOPLE_SEEN_COUNT_TO_REPORT times
    # forget people if they have not been seen for PEOPLE_FORGET_AFTER_UNSEEN_SEC seconds
    next_people = []
    for person in people:
        if not person.reported and person.seen_count >= PEOPLE_SEEN_COUNT_TO_REPORT:
            person.reported = True
            #discord_reporter.report(person)

        if person.unseen_for_seconds < PEOPLE_FORGET_AFTER_UNSEEN_SEC:
            next_people.append(person)
    people = next_people

    for person in people:
        person.print_details()
