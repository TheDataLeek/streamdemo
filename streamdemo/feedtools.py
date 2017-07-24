# stdlib
from typing import List, Dict, Any, Tuple
import bson

# 3rd party
from pprint import pprint

# local
from . import usercollection, activitycollection
from . import START_OF_WEEK
from .util import datetime_to_secs
from .algo import train_from_interactions


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


def trainedfeed(userid: bson.objectid.ObjectId) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
    """
    Pull out a trained feed
    """
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
    # Using algo.py for algorithm here
    weights = train_from_interactions(interactions)

    weighted_feed = order_by_theme_weights(weights, weighted_feed)

    return weighted_feed, weights


def order_by_theme_weights(weights, feed):
    """
    Order a feed by provided topic weights
    """
    new_feed = []
    for obj in feed:
        obj['weight'] = obj['weight'] * weights[obj['topic']][1]
        new_feed.append(obj)
    feed.sort(key=lambda obj: obj['weight'])
    return feed
