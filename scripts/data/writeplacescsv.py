#!/usr/bin/env python3

"""
Usage:

1. Generate a places snapshot by visiting
https://shareaboutsapi.poepublic.com/api/v2/<owner>/datasets/<dataset>/places/snapshots?new[&include_private]

2. Run this script:
"""

import collections
import csv
import json
import sys


# Load in the data
data = json.load(sys.stdin)

# Transform the data
rows = []
fields = collections.OrderedDict([
    ('ID', lambda f: f['properties']['id']),
    ('Submitted', lambda f: f['properties']['created_datetime']), # TODO: Convert to ET
    ('Category', lambda f: f['properties']['location_type']),
    ('Title', lambda f: f['properties']['title']),
    ('Description', lambda f: f['properties']['description']),
    ('City-wide', lambda f: f['properties']['city_wide']),
    ('Comment count', lambda f: f['properties']['submission_sets'].get('comments', {}).get('length', 0)),
    ('Support count', lambda f: f['properties']['submission_sets'].get('support', {}).get('length', 0)),

    ('Longitude', lambda f: f['geometry']['coordinates'][0]),
    ('Latitude', lambda f: f['geometry']['coordinates'][1]),
    ('Near...', lambda f: f['properties'].get('location', {}).get('street', '')),

    ('Submitter', lambda f: f['properties'].get('submitter_name') or f['properties']['submitter']['name']),
    ('Email', 'private-email'),
    ('Previous participant', 'private-previous_participant'),
    ('Heard about PB from...', lambda f: ', '.join(f['properties']['heard_about_pb']) if isinstance(f['properties']['heard_about_pb'], list) else f['properties']['heard_about_pb']),
    ('Race', lambda f: ', '.join(f['properties']['private-race']) if isinstance(f['properties']['private-race'], list) else f['properties']['private-race']),
    ('Education', 'private-education'),
    ('Gender', 'private-gender'),
    ('Other-gender detail', 'private-gender-other-detail'),
    ('ZIP', 'private-zip'),
    ('Phone #', 'private-phone'),

])
for feature in data['features']:
    row = {key: getter(feature) if callable(getter) else feature['properties'].get(getter, '') for key, getter in fields.items()}
    rows.append(row)

writer = csv.DictWriter(sys.stdout, fieldnames=fields.keys())
writer.writeheader()
writer.writerows(rows)
