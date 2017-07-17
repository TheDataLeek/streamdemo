#!/usr/bin/env python3.6

import sys
import os
import argparse
import stream
import json


# First make sure our secret file exists
assert os.path.isfile('./config.json'), 'Please provide a config.json'
# Load in API info
#     * key
#     * secret
with open('./config.json', 'r') as fobj:
    API = json.loads(fobj.read())
# Now make sure it provides the correct information
assert API['key'] is not None, 'Need an API key'
assert API['secret'] is not None, 'Need an API secret'


def main():
    args = get_args()

    client = stream.connect(API['key'], API['secret'])


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--logfile', type=str,
                        default='demo.log',
                        help='Specify which logfile to use')
    return parser.parse_args()


if __name__ == '__main__':
    sys.exit(main())
