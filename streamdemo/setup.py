#!/usr/bin/env python3.6

#stdlib
import sys
import random
import time
from datetime import datetime
from datetime import datetime as dt
from datetime import timedelta

# typing
from typing import Dict, List, Any, Optional

# third party
import names  # http://treyhunner.com/2013/02/random-name-generator/
import stream
import pymongo as pm
from pprint import pprint

# third-party, math bits
import networkx as nx
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

# Local
from . import API
from . import SIZE_MULTIPLIER, THEMES
from . import database  # pull in db
from . import usercollection, activitycollection


WEEK_SECONDS: int = 604800  # https://www.wolframalpha.com/input/?i=1+week+to+seconds
START_OF_WEEK: datetime = dt.now()


def random_week_time(weekstart: Optional[datetime]=START_OF_WEEK) -> datetime:
    return (weekstart + timedelta(seconds=(random.random() * WEEK_SECONDS)))


def setup_data() -> Dict[str, List[str]]:
    # First let's generate a bunch of random users,
    # store as edge dictionary to make friendships easier
    users = {names.get_first_name(): list() for _ in range(1 * SIZE_MULTIPLIER)}

    # for each user friend a random number of friends between 2 and 10
    # this is kinda sloppy since random.choices only has replacement,
    # so we just prune duplicates (which is ok since we're randomizing numfriends anyway)
    # this makes a DIGRAPH, since friendships are one-way
    for user in users:
        # we don't want them to try to friend themselves....
        possible_friends = list(set(users.keys()) - {user})
        num_friends      = random.randint(5, SIZE_MULTIPLIER)
        # remove duplicates too
        friends          = list(set(random.choices(possible_friends,
                                                   k=num_friends)))
        users[user]      = friends

    assert len(list(usercollection.find({}))) == 0

    # populate database
    # (1) add all users (so we can pull them out)
    usercollection.insert_many([
        {
            'name': name,
            'friends': None
        }
        for name in users.keys()
    ])

    # (2) add friendships
    # not super pretty overwriting local vars here, but we only care about the dbobjs anyway sooooo
    for username, friends_s in users.items():
        user         = usercollection.find_one({'name': username})
        friends      = [usercollection.find_one({'name': friend})['_id']
                        for friend in friends_s]
        usercollection.update_one({
            '_id': user['_id']
        }, {
            '$set': {
                'friends': friends
            }
        })

    # hey look at that we have a network (draw real quick)
    draw_connections(users)

    # now we need to generate a bunch of posts from each
    generate_posts(users)

    return users


def draw_connections(users):
    social_graph = nx.DiGraph()
    social_graph.add_nodes_from(users.keys())
    edges = []
    for user, friends in users.items():
        for friend in friends:
            edges.append((user, friend))
    social_graph.add_edges_from(edges)

    # this is gonna look real messy cause there are sooo many connections...
    # GOOD
    # only wanna draw once
    # nx.draw(social_graph)
    # plt.savefig('nasty_mess_of_friends.png')


def generate_posts(users: Dict[str, List[str]]):
    # Lets generate somewhere between 50 and 100 posts per user over a week
    for user in users:
        user = usercollection.find_one({'name': user})  # pull out db obj
        random_num_of_posts = random.randint(5 * SIZE_MULTIPLIER, 10 * SIZE_MULTIPLIER)
        # To generate a random time, we add to the start of a week a random multiple of week's seconds
        activitycollection.insert_many([
            {
                'actor': user['_id'],
                'verb': 'post',
                'object': None,
                'time': random_week_time(),
                'message': 'foooobar',
                'topic': random.choice(THEMES)
            }
            for _ in range(random_num_of_posts)
        ])


def generate_events(users):
    # lets make 10000 events? random users interacting with random things.
    # These are the collected metrics that we'll analyze
    # We'll have all events happen ONLY AFTER the first week
    start_of_second_week = START_OF_WEEK + timedelta(seconds=WEEK_SECONDS)
    for _ in range(100):
        usernames = list(users.keys())
        from_user = usercollection.find_one({'name': random.choice(usernames)})
        # print(from_user['friends'])
        to_user = usercollection.find_one({'_id': random.choice(from_user['friends'])})

        to_user_post = random.choice(list(activitycollection.find({'actor': to_user['_id'], 'verb': 'post'})))

        activitycollection.insert_one({
            'actor': from_user['_id'],
            'verb': 'interact',   # type of interaction doesn't matter here, gonna weight everything equally
            'object': to_user_post['_id'],
            'time': random_week_time(weekstart=start_of_second_week),  # again after first week
            'to': to_user['_id']
        })
