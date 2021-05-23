#!/usr/bin/env python3

"""
Required python-dateutil
"""

import collections
import csv
from dateutil.parser import parse
import os
import pytz
from request_utils import download_all_pages
import requests
import sys


USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']

session = requests.Session()
session.auth = (USERNAME, PASSWORD)
session.headers = {'content-type': 'application/json', 'x-shareabouts-silent': 'true'}

IDEAS_URL = 'https://shareaboutsapi.poepublic.com/api/v2/cambridge/datasets/pb-fy2022/places?include_private=True'
>>>>>>> 393832b0ae2a6b82d2236ac770656d720e1da474
ET = pytz.timezone('US/Eastern')

# Load in the data
idea_pages = download_all_pages(IDEAS_URL, session=session)

# Transform the data
rows = []
fields = collections.OrderedDict([
    ('ID', lambda f: f['properties']['id']),
    ('Submitted', lambda f: parse(f['properties']['created_datetime']).astimezone(ET).isoformat()[:19].replace('T', ' ')),
    ('Category', lambda f: f['properties']['location_type']),
    ('Title', lambda f: f['properties']['title']),
    ('Description', lambda f: f['properties']['description']),
    ('City-wide', lambda f: f['properties']['city_wide']),
    ('Comment count', lambda f: f['properties']['submission_sets'].get('comments', {}).get('length', 0)),
    ('Support count', lambda f: f['properties']['submission_sets'].get('support', {}).get('length', 0)),

    ('Longitude', lambda f: f['geometry']['coordinates'][0]),
    ('Latitude', lambda f: f['geometry']['coordinates'][1]),
    ('Near...', lambda f: f['properties'].get('location', '')),
    ('Hidden', lambda f: not f['properties']['visible']),

    ('Submitter', lambda f: f['properties'].get('submitter_name') or f['properties']['submitter']['name']),
    ('Email', 'private-email'),
    ('Previous participant', 'private-previous_participant'),
    ('Civically involved', 'private-other_civic_participant'),
    ('Municipal election voter', 'private-municipal_election_voter'),
    ('Heard about PB from...', lambda f: ', '.join(f['properties']['heard_about_pb']) if isinstance(f['properties']['heard_about_pb'], list) else f['properties']['heard_about_pb']),
    ('Other-source detail', 'heard_about_pb-other-detail'),
    ('Age', 'private-age'),
    ('Gender', 'private-gender'),
    ('Other-gender detail', 'private-gender-other-detail'),
    ('Race', lambda f: ', '.join(f['properties']['private-race']) if isinstance(f['properties']['private-race'], list) else f['properties']['private-race']),
    ('Education', 'private-education'),
    ('Household income', 'private-income'),
    ('ZIP', 'private-zip'),
    ('Phone #', 'private-phone'),

])
for page in idea_pages:
    for feature in page['features']:
        row = {key: getter(feature) if callable(getter) else feature['properties'].get(getter, '') for key, getter in fields.items()}
        rows.append(row)

writer = csv.DictWriter(sys.stdout, fieldnames=fields.keys())
writer.writeheader()
writer.writerows(rows)
