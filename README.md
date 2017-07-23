# Stream Demo
## Will Farmer

# Introduction

This project acts as a way to tinker with the Stream API and add some machine learning capabilities
with hopefully little overhead.

# Initial Steps

The first thing we need to do is to create a social network with impression/interaction history in
order to have some data to train on. We could do this one of two primary ways:
1. Just simulate events and pull from a random list of users, with the assumption that all users
   *can* react to every other user. The advantage of this approach is that it creates a
   mega-network with a ton of user interaction.
2. Simulate a social network from the ground up. This means starting by generating a finite list of
   users, giving each of them a couple friends, and then simulating events based on who they know.
   The advantage of this solution is two-fold, the first (and primary) being that it's a little more
   realistic. The second is that it creates a bunch of tiny social networks that interact with each
   other.
Currently we're using the second approach, but that might change.

# Data Storage

Initially this was written with sqlite and ponyorm, but it was decided that Mongo *might* be a
better solution for a couple reasons.

# Hooking Up Stream

Stream's API is very easy to use. We're pulling all this code from [Stream's
Website](https://getstream.io/docs/python/).

```python
# Select user to tinker with?
chris = client.feed('user', 'chris')
# Add activity to their feed
chris.add_activity({
    'actor': 'chris',
    'verb': 'add',
    'object': 'picture:10',
    'foreign_id': 'picture:10',
    'message': 'This bird is absolutely beautiful. Glad it\'s recovering from a damaged wing.'
})
```
