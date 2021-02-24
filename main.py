import logging
from datetime import datetime

import cv2
import face_recognition
import numpy as np
import pytz

from camera import VideoStream
from discord import DiscordReporter
from people import load_people, unknown_person
from settings import DETECTED_AT_THRESHOLD, RTSP_STREAM_URL, DISCORD_WEBHOOK_URL


def get_frame():
    # Grab a single frame of video
    frame = video_stream.read()

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = frame[:, :, ::-1]

    return frame, rgb_frame


def find_people_in_frame(rgb_small_frame, now):
    # Find all face locations and face encodings in the current frame of video
    frame_face_locations = face_recognition.face_locations(rgb_small_frame)
    frame_face_encodings = face_recognition.face_encodings(rgb_small_frame, frame_face_locations)

    frame_people = []
    for i, frame_face_encoding in enumerate(frame_face_encodings):
        # Find all matches with people
        matches = face_recognition.compare_faces(people_face_encodings, frame_face_encoding)

        # Find best match
        face_distances = face_recognition.face_distance(people_face_encodings, frame_face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            person = people_ordered_dict[best_match_index]
        else:
            person = unknown_person

        person.last_seen_at = now
        person.last_seen_face_location = frame_face_locations[i]
        frame_people.append(person)

    return frame_people


# Init logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)

# Load people
logging.info('Loading people.')
people_ordered_dict = load_people()
people_face_encodings = [person.face_encoding for person in people_ordered_dict.values()]

logging.info('Initializing camera.')
# Get a reference to video stream
video_stream = VideoStream(RTSP_STREAM_URL).start()

logging.info('Initializing discord reporter.')
discord_reporter = DiscordReporter(DISCORD_WEBHOOK_URL).start()

logging.info('Looping.')
while True:
    now = datetime.now(tz=pytz.UTC)
    logging.info('Parsing frame.')

    # Get frame
    frame, rgb_frame = get_frame()
    # Find people in frame
    frame_people = find_people_in_frame(rgb_frame, now)

    # Process found people
    for frame_person in frame_people:
        # Check if they should be detected (DETECTED_AT_THRESHOLD passed)
        if (frame_person.last_seen_at - frame_person.detected_at).total_seconds() < DETECTED_AT_THRESHOLD:
            continue

        # Update detected_at
        frame_person.detected_at = now
        frame_person.detected_face_location = frame_person.last_seen_face_location
        frame_person.detected_img = cv2.imencode('.png', frame)[1].tobytes()

        # Report to discord
        logging.info('Reporting to discord: {}.'.format(frame_person.name))
        discord_reporter.report(frame_person)
