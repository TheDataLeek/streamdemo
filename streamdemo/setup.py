#!/usr/bin/env python3.6

#stdlib
import random
from datetime import datetime
from datetime import datetime as dt
from datetime import timedelta

# typing
from typing import Dict, List, Any

# third party
import names  # http://treyhunner.com/2013/02/random-name-generator/
import loremipsum
import stream
import pymongo as pm

# third-party, math bits
import networkx as nx
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

# Local
from . import API
from . import SIZE_MULTIPLIER
from . import database, usercollection, activitycollection  # pull in db


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
        possible_friends = list(set(users.keys()) - set([user]))
        num_friends      = random.randint(1, SIZE_MULTIPLIER)
        friends          = list(set(random.choices(possible_friends,
                                                   k=num_friends)))
        users[user]      = friends

    # populate database
    # (1) add all users (so we can pull them out)
    usercollection.insert_many(
        [
            { 'name': name, 'friends': None } for name in users
        ]
    )

    # (2) add friendships
    # not super pretty overwriting here, but we only care about the instances anyway sooooo
    for user, friends in users.items():
        user         = usercollection.find_one({'name': user})
        # friends      = User.select(lambda x: x.name in friends)[:]
        friends = usercollection.find()
        user.friends = friends

    # hey look at that we have a network
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
    week_seconds: int = 604800  # https://www.wolframalpha.com/input/?i=1+week+to+seconds
    for user in users:
        # user = User.select(lambda x: x.name == user).first()
        for _ in range(random.randint(5 * SIZE_MULTIPLIER, 10 * SIZE_MULTIPLIER)):
            pass
            # Post(
            #     name=str(loremipsum.generate_sentences(1)),
            #     text=str(loremipsum.generate_paragraphs(random.randint(1, 10))),
            #     date_posted=(dt.now() + timedelta(seconds=(random.random() * week_seconds))),
            #     user=user
            # )


def generate_events(users):
    # lets make 1000 events? random users interacting with random things.
    # These are the collected metrics that we'll analyze
    for _ in range(1000):
        user = random.choice(users.keys())
