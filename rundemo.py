#!/usr/bin/env python3.6

# stdlib
import sys
import random
import argparse
from typing import Dict, List, Any

# 3rd party
import stream

# local
import streamdemo
from streamdemo import setup
from streamdemo import API
from streamdemo import feedtools
from streamdemo import database


def main():
    # Setup initial data
    users: Dict[str, List[str]] = setup.setup_data()

    # generate interaction events
    setup.generate_events(users)

    # pull a random document object id for a random user
    random_userid = database.usercollection.find_one({'name': random.choice(list(users.keys()))})['_id']

    # first lets pull a flat feed
    flat = feedtools.flatfeed(random_userid)

    # now lets pull the weighted feed with the scores
    train, scores = feedtools.trainedfeed(random_userid)

    # for last comparison lets pull the aggregated Stream feed
    userclient = setup.client.feed('timeline', str(random_userid))
    # activities = jack.get(limit=10)['results']
    userfeed = [obj for obj in userclient.get(limit=100)['results'] if obj.get('topic') is not None]

    print(scores)

    for i in range(15):
        print(f'{flat[i]["topic"]}\t{train[i]["topic"]}\t{userfeed[i]["topic"]}')


if __name__ == '__main__':
    sys.exit(main())
