import logging
from datetime import datetime

import cv2
import face_recognition
import numpy as np
import pytz

from camera import VideoStream
from discord import DiscordReporter, DiscordReportData
from people import FramePerson, load_people
from settings import *


def find_best_match(face_encoding, face_encodings):
    # Try to find match in current people
    match_person = None
    if face_encodings:
        # Find all matches with people
        matches = face_recognition.compare_faces(face_encodings, face_encoding)

        # Find best match
        face_distances = face_recognition.face_distance(face_encodings, face_encoding)
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
logging.info('Loading people.')
known_people_face_encodings, known_people_names = load_people()

# Get a reference to video stream
logging.info('Initializing camera.')
video_stream = VideoStream(STREAM_URL).start()

logging.info('Initializing discord reporter.')
discord_reporter = DiscordReporter(DISCORD_WEBHOOK_URL).start()

# Drawing
font = cv2.FONT_HERSHEY_DUPLEX
color = (36, 255, 12)

logging.info('Looping.')
people = []
last_frame_sent_at = datetime.min.replace(tzinfo=pytz.UTC)
while True:
    # Grab a single frame of video
    frame = video_stream.read()

    # Get current time
    now = datetime.now(tz=pytz.UTC)

    # Convert the frame from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = frame[:, :, ::-1]

    # Find all face locations and face encodings in the current frame of video
    frame_face_locations = face_recognition.face_locations(rgb_frame)
    frame_face_encodings = face_recognition.face_encodings(rgb_frame, frame_face_locations)

    # Extract face_encodings of all current people
    people_face_encodings = [person.face_encoding for person in people]
    for i, frame_face_encoding in enumerate(frame_face_encodings):
        person = find_best_match(frame_face_encoding, people_face_encodings)

        # If the match was not found create new person
        if not person:
            person = FramePerson(frame_face_encoding, now)

            # Try to find person in known people
            matches = face_recognition.compare_faces(known_people_face_encodings, frame_face_encoding)
            face_distances = face_recognition.face_distance(known_people_face_encodings, frame_face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                person.name = known_people_names[best_match_index]

            people.append(person)

        # If PEOPLE_DRAW then draw boxes around faces
        if PEOPLE_DRAW:
            top, right, bottom, left = frame_face_locations[i]
            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), color, 1)

            # Draw a label above the face
            cv2.putText(frame, person.label_text(), (left, top - 2), font, 0.6, color, 1)

    # report people if they have not been reported and have been seen PEOPLE_SEEN_COUNT_TO_REPORT times
    # forget people if they have not been seen for PEOPLE_FORGET_AFTER_UNSEEN_SEC seconds
    next_people = []
    for person in people:
        if not person.reported and person.seen_count >= PEOPLE_SEEN_COUNT_TO_REPORT:
            person.reported = True
            report_data = DiscordReportData(cv2.imencode('.png', frame)[1].tobytes(), '{}.png'.format(person.id), person.spotted_message())
            logging.info('Reporting people to discord.')
            discord_reporter.report(report_data)
            last_frame_sent_at = now

        if person.unseen_for_seconds < PEOPLE_FORGET_AFTER_UNSEEN_SEC:
            next_people.append(person)
    people = next_people

    # send a frame if last
    if FRAME_SEND_EVERY_SEC and (now - last_frame_sent_at).total_seconds() >= FRAME_SEND_EVERY_SEC:
        report_data = DiscordReportData(
            cv2.imencode('.png', frame)[1].tobytes(),
            '{}.png'.format(datetime.timestamp(now)),
            'Frame at `{}`.'.format(now.astimezone(pytz.timezone(TIMEZONE)).strftime('%H:%M:%S, %d/%m/%Y'))
        )
        logging.info('Reporting frame to discord.')
        discord_reporter.report(report_data)
        last_frame_sent_at = now
