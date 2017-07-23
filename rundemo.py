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

    client = stream.connect(API['key'], API['secret'])

    users: Dict[str, List[str]] = setup.setup_data()
    setup.generate_events(users)

    random_userid = database.usercollection.find_one({'name': random.choice(list(users.keys()))})['_id']
    feedtools.flatfeed(random_userid)
    feedtools.trainedfeed(random_userid)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--logfile', type=str,
                        default='demo.log',
                        help='Specify which logfile to use')
    return parser.parse_args()


if __name__ == '__main__':
    sys.exit(main())
