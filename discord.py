import requests

import settings


def report_to_discord(person):
    requests.post(url=settings.DISCORD_WEBHOOK_URL,
                  files={
                      'content': (None, person.msg_door()),
                      'file': ('{}.png'.format(person.name.replace(' ', '_').lower()), person.detected_img)
                  })

