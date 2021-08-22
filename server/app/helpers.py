import requests
import json
from datetime import datetime
from app.models import CallCard, ResponseCard
from app import db


def get_json(url):
    r = requests.get(url)
    print(r.json())
    return r.json()


def read_file(path):
    f = open(path, "r")
    contents = f.read()
    f.close()
    return json.loads(contents)


def join_cards():
    calls = read_file('calls.json')
    f = open('joined_cards.txt', "w")
    for c in calls:
        f.write("%s\n" % '_____'.join(c['text']))
    f.write("\n\n")
    responses = read_file('responses.json')
    for r in responses:
        f.write("%s\n" % '_____'.join(r['text']))
    f.close()

def load_from_file():
    calls = []
    if CallCard.query.count() == 0:
        calls = read_file('calls.json')
        for c in calls:
            date = datetime.strptime(c['created_at'], '%Y-%m-%dT%H:%M:%S%z')
            card = CallCard(text=c['text'], created_at=date, nsfw=True)
            db.session.add(card)
    responses = []
    if ResponseCard.query.count() == 0:
        responses = read_file('responses.json')
        for r in responses:
            date = datetime.strptime(r['created_at'], '%Y-%m-%dT%H:%M:%S%z')
            card = ResponseCard(text=r['text'], created_at=date, nsfw=True)
            db.session.add(card)
    db.session.commit()
    return {
        'calls': calls,
        'responses': responses
    }
