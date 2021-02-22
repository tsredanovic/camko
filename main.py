from datetime import datetime, timezone

import cv2
import face_recognition
import numpy as np
import pytz

from discord import report_to_discord
from people import load_people, unknown_person
from settings import DETECTED_AT_THRESHOLD


def get_frame():
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    return frame, rgb_small_frame


def find_people_in_frame(rgb_small_frame, now):
    # Find all the faces and face encodings in the current frame of video
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


def draw_on_frame(frame, frame_person):
    top, right, bottom, left = frame_person.last_seen_face_location
    top *= 4
    right *= 4
    bottom *= 4
    left *= 4
    # Draw a box around the face
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
    # Draw a label with a name below the face
    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
    cv2.putText(frame, frame_person.name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)


def save_frame(frame, frame_person):
    cv2.imwrite(
        'frame_{}_{}.png'.format(
            frame_person.detected_at_ts,
            frame_person.name.replace(' ', '_').lower()
        ),
        frame
    )


# Load people
people_ordered_dict = load_people()
people_face_encodings = [person.face_encoding for person in people_ordered_dict.values()]

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)
# Set font
font = cv2.FONT_HERSHEY_DUPLEX

while True:
    now = datetime.now(tz=pytz.UTC)

    # Get frame
    frame, rgb_small_frame = get_frame()
    # Find people in frame
    frame_people = find_people_in_frame(rgb_small_frame, now)

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
        report_to_discord(frame_person)
