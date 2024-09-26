#!/usr/bin/env python3

"""
Required python-dateutil

Sample run:

    dotenv python writeplacescsv.py --earliest '2024-09-04' --latest '2024-09-11' > ideas-between-2024-09-04-and-2024-09-11.csv
"""

import click
import collections
import csv
from dateutil.parser import parse
import os
import pytz
from request_utils import download_all_pages
import requests


@click.command()
@click.option('--earliest', type=click.DateTime(), required=False, help='The earliest creation datetime, inclusive')
@click.option('--latest', type=click.DateTime(), required=False, help='The latest creation datetime, inclusive')
@click.option('--outfile', type=click.File('w'), default='-', show_default=True)
@click.option('--timezone', type=str, default='US/Eastern', show_default=True)
def main(earliest, latest, outfile, timezone):
    USERNAME = os.environ['USERNAME']
    PASSWORD = os.environ['PASSWORD']

    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)
    session.headers = {'content-type': 'application/json', 'x-shareabouts-silent': 'true'}

    # Update the DATASET_URL with the root URL of the dataset. There are a few ways
    # you can find the root URL.
    DATASET_URL = 'https://shareaboutsapi.poepublic.com/api/v2/cambridge/datasets/pb-fy2026'

    IDEAS_URL = DATASET_URL + '/places?include_private=True&include_invisible=True'
    TZ = pytz.timezone(timezone)

    # Load in the data
    idea_pages = download_all_pages(IDEAS_URL, session=session)

    # Transform the data
    rows = []
    def is_truthy(x): return bool(x)
    fields = collections.OrderedDict([
        ('ID', lambda f: f['properties']['id']),
        ('Submitted', lambda f: parse(f['properties']['created_datetime']).astimezone(TZ).isoformat()[:19].replace('T', ' ')),
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
        ('User Token', 'user_token'),
        ('Email', 'private-email'),
        ('Phone #', 'private-phone'),
        ('Already submitted personal info', 'private-completed_personal_info_survey'),
        ('Previous participant', 'private-previous_participant'),
        ('Civically involved', 'private-other_civic_participant'),
        # ('Municipal election voter', 'private-municipal_election_voter'),
        ('Heard about PB from...', lambda f: ', '.join(f['properties'].get('heard_about_pb')) if isinstance(f['properties'].get('heard_about_pb'), list) else f['properties'].get('heard_about_pb')),
        ('Other-source detail', 'heard_about_pb-other-detail'),
        # ('ZIP', 'private-zip'),
        ('Neighborhood', 'private-neighborhood'),
        ('Age', 'private-age'),
        ('Cis/Transgender', 'private-gender-alignment'),
        ('Gender', (
            lambda f: ' '.join(filter(is_truthy, gender))
            if isinstance(gender := f['properties'].get('private-gender'), list)
            else gender
        )),
        ('Other-gender detail', 'private-gender-other-detail'),
        ('Language', 'private-language'),
        ('Other-language detail', 'private-language-other-detail'),
        ('Race', lambda f: ', '.join(f['properties'].get('private-race')) if isinstance(f['properties'].get('private-race'), list) else f['properties'].get('private-race')),
        # ('Education', 'private-education'),
        # ('Household income', 'private-income'),

    ])

    earliest = TZ.localize(earliest) if earliest else None
    latest = TZ.localize(latest) if latest else None

    for page in idea_pages:
        for feature in page['features']:
            created_dt = parse(feature['properties']['created_datetime']).astimezone(TZ)

            if earliest and created_dt < earliest:
                continue
            if latest and created_dt > latest:
                continue

            row = {
                key: (
                    getter(feature)
                    if callable(getter)
                    else feature['properties'].get(getter, '')
                ) for key, getter in fields.items()
            }
            rows.append(row)

    writer = csv.DictWriter(outfile, fieldnames=fields.keys())
    writer.writeheader()
    writer.writerows(rows)


if __name__ == '__main__':
    main()
