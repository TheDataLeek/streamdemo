# stdlib
from typing import List, Dict, Any
import bson

# 3rd party
from pprint import pprint

# local
from . import usercollection, activitycollection
from . import START_OF_WEEK
from .util import datetime_to_secs


def flatfeed(userid: bson.objectid.ObjectId) -> List[Dict[str, Any]]:
    """
    pull out a flat feed, kinda messy
    """
    # TODO: Fix messyness here
    user = usercollection.find_one({'_id': userid})
    feed = []
    posts = [list(activitycollection.find({'actor': friend, 'verb': 'post'}))
             for friend in user['friends']]
    for post in posts:
        for item in post:
            feed.append(item)
    feed.sort(key=lambda obj: obj['time'])
    return feed


def trainedfeed(userid: bson.objectid.ObjectId) -> List[Dict[str, Any]]:
    feed = flatfeed(userid)

    interactions = list(activitycollection.find({'actor': userid, 'verb': 'interact'}))

    interactions = [{
        'time': obj['time'],
        'topic': activitycollection.find_one({'_id': obj['object']})['topic']
    } for obj in interactions]

    # normalizing weights to 1, need max time.
    maxtime = datetime_to_secs(max(feed, key=lambda obj: obj['time'])['time'], reftime=START_OF_WEEK)
    # Adding normalized weights initially based on timestamps
    # neat way to add keys
    weighted_feed = [{**obj, **{'weight': datetime_to_secs(obj['time'], reftime=START_OF_WEEK) / maxtime}}
                     for obj in feed]

    # now we can fiddle with weights based on interactions

    return weighted_feed

