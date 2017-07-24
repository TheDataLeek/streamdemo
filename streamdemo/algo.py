# stdlib
from typing import Optional

# third party
from datetime import datetime
from datetime import timedelta

import numpy as np

# local
from . import THEMES
from .util import datetime_to_secs

"""
NOTES

we have some f(post_topic, topics_interacted, interaction_times) -> weight_adj

the more time since interaction the less it adjusts the weight

the more similarity between topics (for this might just say "same") the more effect

i mean in general we need to create an n-dimensional space and locate where the user falls in that n dimensional space
with some generic time-decay function.

FOR INSTANCE

with 2 topics (lets say 'cars' and 'dogs' we'd have something like this (unweighted

         Cars
           |
           |
           |
Dogs ------x---------
           |
           |
           |

BUT if some user interacts a ton with just dogs we'd get

         Cars
           |
           |
           |
Dogs -x-------------
           |
           |
           |

Which would decay over time

Weights of all zeros indicates a flat feed, 1's indicate bias in that direction, not gonna do negative bias.

We want the time decay to be some big logistic with horizontal asymptotes at 0 and 1 on domain [0,\infty] and range [0,1].
This time decay should fiddle with each

We need a frequency estimate of how often they interact with /that/ thing over time

A better way to think of this is to imagine a ton of bars, whose total must add up to 1, that decay down to zero.

SOOOO this means that the solution here is less "machine learning" and more instead just a customizeable adaption algorithm...
Mincing words slightly but it's not super important.
"""


def time_decay(score: float, jump_dist: Optional[float]=1.0, rate_parameter: Optional[float]=1.0) -> float:
    """
    This function is in charge of performing any time decay that needs to happen...

    We're gonna use the same equation for every decaying score

    rate parameter changes the shape of this thing.

    BASICALLY JUST RK1 HILARIOUSLY
    """
    if score <= 0.01:
        return 0.01

    def decay_func(x):
        return 2 / (1 + np.exp(5 * rate_parameter * x))

    def decay_func_p(x):   # just the derivative of the decay func
        return (-2 * (5 * rate_parameter) * np.exp(5 * rate_parameter * x)) / ((np.exp(5 * rate_parameter * x) + 1) ** 2)

    return score + (decay_func_p(score) * jump_dist)


def score_bump(score: float) -> float:
    """
    Bump the score
    """
    return score + ((1 - score) / 2)


def train_from_interactions(interactions):
    """
    Given a set of interactions, train a set of topic weights
    """
    scores = {t: (0, 0) for i, t in enumerate(THEMES)}
    stime, gap = normalize_times(interactions)
    for obj in sorted(interactions, key=lambda obj: obj['time']):
        obj_time = (datetime_to_secs(obj['time']) - stime) / gap
        jump = obj_time - scores[obj['topic']][0]
        decayed_score = time_decay(scores[obj['topic']][1], jump)
        bumped_score = score_bump(decayed_score)
        scores[obj['topic']] = (obj_time, bumped_score)
    return scores


def normalize_times(interactions):
    """
    find the start and gap of normalized times. Allows us to normalize more times.
    """
    stime = datetime_to_secs(min(interactions, key=lambda obj: obj['time'])['time'])
    etime = datetime_to_secs(max(interactions, key=lambda obj: obj['time'])['time'])
    gap = etime - stime
    return stime, gap

