import argparse


def positive_int(value):
    int_value = int(value)
    if int_value <= 0:
        raise argparse.ArgumentTypeError('{} is an invalid positive int value'.format(value))
    return int_value


argparser = argparse.ArgumentParser()

# PEOPLE_FORGET_AFTER_UNSEEN_SEC
argparser.add_argument('--people-forget-after-unseen-sec', dest='people_forget_after_unseen_sec', default=10, type=positive_int)
# PEOPLE_SEEN_COUNT_TO_REPORT
argparser.add_argument('--people-seen-count-to-report', dest='people_seen_count_to_report', default=1, type=positive_int)
# PEOPLE_DRAW
argparser.add_argument('--people-draw', dest='people_draw', action='store_true')
argparser.add_argument('--no-people-draw', dest='people_draw', action='store_false')
argparser.set_defaults(people_draw=True)
# FRAME_SEND_EVERY_SEC
argparser.add_argument('--frame-send-every-sec', dest='frame_send_every_sec', default=10, type=int)
# STREAM
argparser.add_argument('--stream', dest='stream', type=str)