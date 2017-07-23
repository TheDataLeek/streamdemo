import os
import json
from typing import Dict, List, Any

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

# DATABASE #########################################################################################
from pymongo import MongoClient
client             = MongoClient()
database           = client.streamdb
usercollection     = database.usercollection
activitycollection = database.activitycollection


# LOCALS ###########################################################################################
from .setup import *
