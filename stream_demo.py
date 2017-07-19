#!/usr/bin/env python3.6

#stdlib
import sys
import os
import argparse
import json
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
from pony import orm

# third-party, math bits
import networkx as nx
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt


# GLOBALS ##########################################################################################
# tweak this to generate more or less data (keep as int)
SIZE_MULTIPLIER: int = 10


# First make sure our secret file exists
assert os.path.isfile('./config.json'), 'Please provide a config.json'
# Load in API info
#     * key
#     * secret
with open('./config.json', 'r') as fobj:
    API: Dict[str, str] = json.loads(fobj.read())
# Now make sure it provides the correct information
assert API['key'] is not None, 'Need an API key'
assert API['secret'] is not None, 'Need an API secret'


# Going to need a global db instance for this
db = orm.Database()

# CODE #############################################################################################
def main():
    args = get_args()

    db.bind('sqlite', ':memory:')
    db.generate_mapping(create_tables=True)

    client = stream.connect(API['key'], API['secret'])

    users: Dict[str, List[str]] = setup_data()
    generate_events(users)


@orm.db_session
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
    for user in users:
        User(name=user)

    # (2) add friendships
    # not super pretty overwriting here, but we only care about the instances anyway sooooo
    for user, friends in users.items():
        user         = orm.select(x for x in User if x.name == user).first()  # should only be one
        assert user is not None   # this should never happen
        friends      = User.select(lambda x: x.name in friends)[:]
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


@orm.db_session
def generate_posts(users: Dict[str, List[str]]):
    # Lets generate somewhere between 50 and 100 posts per user over a week
    week_seconds: int = 604800  # https://www.wolframalpha.com/input/?i=1+week+to+seconds
    for user in users:
        user = User.select(lambda x: x.name == user).first()
        for _ in range(random.randint(5 * SIZE_MULTIPLIER, 10 * SIZE_MULTIPLIER)):
            Post(
                name=str(loremipsum.generate_sentences(1)),
                text=str(loremipsum.generate_paragraphs(random.randint(1, 10))),
                date_posted=(dt.now() + timedelta(seconds=(random.random() * week_seconds))),
                user=user
            )


@orm.db_session
def generate_events(users):
    # lets make 1000 events? random users interacting with random things.
    # These are the collected metrics that we'll analyze
    pass


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--logfile', type=str,
                        default='demo.log',
                        help='Specify which logfile to use')
    return parser.parse_args()


# DATABASE SCHEMA ##################################################################################
class User(db.Entity):
    name             = orm.Required(str)
    friends          = orm.Set(lambda: User)
    friends_of       = orm.Set(lambda: User)
    posts            = orm.Set(lambda: Post, reverse='user')
    posts_like       = orm.Set(lambda: Post, reverse='user_likes')
    post_impressions = orm.Set(lambda: Post, reverse='user_impressions')


class Post(db.Entity):
    name             = orm.Required(str)
    text             = orm.Required(str)
    date_posted      = orm.Required(datetime)
    user             = orm.Required(lambda: User)
    user_likes       = orm.Set(lambda: User)
    user_impressions = orm.Set(lambda: User)


class Event(db.Entity):
    """ Basically modelling off of stream API """
    actor = orm.Required(lambda: User)
    verb  = orm.Required(str)
    obj   = orm.Required(lambda: Post)


if __name__ == '__main__':
    sys.exit(main())
