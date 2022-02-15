import argparse
import csv
import hashlib
from os import makedirs
import re
from time import sleep
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests

parser = argparse.ArgumentParser()
parser.add_argument('seed_url')
parser.add_argument('-p', '--pages', default=0, type=int)

args = parser.parse_args()

seed_url = args.seed_url
page_limit = args.pages

# -- setup files/directories --
report_file = open('report.csv', 'w', newline='')
report_csv = csv.writer(report_file)
report_csv.writerow(['URL', 'Filename', 'Outlinks'])

makedirs('repository', exist_ok=True)

# -- initial setup --
dir_re = re.compile(r'(\/.+\/|\/)')

frontier = set([seed_url]) # going to
explored = set() # already did

seed_parse = urlparse(seed_url)

seed_scheme = seed_parse.scheme
seed_domain = seed_parse.netloc

pages = 0

while len(frontier) > 0 and (page_limit == 0 or pages < page_limit):
    curr_url = frontier.pop()
    curr_dir = dir_re.match(urlparse(curr_url).path).group(1)

    r = requests.get(curr_url)

    if r.ok and r.headers['content-type'].startswith('text/html'):
        print('[{0}, {1}] {2}'.format(r.status_code, r.headers['content-type'], curr_url))

        soup = BeautifulSoup(r.text, 'html.parser')
        all_links = [link.get('href') for link in soup.find_all('a') if link.get('href')]

        outlinks_before = len(frontier)

        for link in all_links:
            link_parse = urlparse(link)

            scheme = link_parse.scheme
            domain = link_parse.netloc
            path = link_parse.path

            # Skip if not http/https
            if scheme and scheme not in ['http', 'https']:
                continue

            # Skip if domain != seed domain
            if domain and domain != seed_domain:
                continue

            # Skip if path is blank
            if not path:
                continue

            scheme = scheme if scheme else seed_scheme
            domain = domain if domain else seed_domain

            if path[0] == '/':
                link_url = f'{scheme}://{domain}{path}'
            else:
                path = f'{curr_dir}{path}'
                link_url = f'{scheme}://{domain}{path}'

            if link_url not in explored:
                frontier.add(link_url)

        outlinks = len(frontier) - outlinks_before

        url_hash = hashlib.sha1(curr_url.encode()).hexdigest()
        filename = f'{url_hash}.html'
        with open(f'repository/{filename}', 'w') as f:
            f.write(r.text)

        report_csv.writerow([curr_url, filename, outlinks])

        pages += 1
        explored.add(curr_url)
    else:
        print('*[{0}, {1}] {2}'.format(r.status_code, r.headers['content-type'], curr_url))

report_file.close()
