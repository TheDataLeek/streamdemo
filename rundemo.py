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
    args = get_args()

    users: Dict[str, List[str]] = setup.setup_data()
    setup.generate_events(users)

    random_userid = database.usercollection.find_one({'name': random.choice(list(users.keys()))})['_id']
    flat = feedtools.flatfeed(random_userid)
    train, scores = feedtools.trainedfeed(random_userid)

    userclient = setup.client.feed('timeline', str(random_userid))
    # activities = jack.get(limit=10)['results']
    userfeed = [obj for obj in userclient.get(limit=100)['results'] if obj.get('topic') is not None]

    print(scores)

    for i in range(len(userfeed)):
        print(f'{flat[i]["topic"]}\t{train[i]["topic"]}\t{userfeed[i]["topic"]}')


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--logfile', type=str,
                        default='demo.log',
                        help='Specify which logfile to use')
    return parser.parse_args()


if __name__ == '__main__':
    sys.exit(main())
