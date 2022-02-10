import argparse
import csv
import hashlib
from os import makedirs
import re
from time import sleep

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
domain_re = re.compile(r'(https?)?:\/\/(.*?)(/.*)')
javascript_re = re.compile(f'javascript:')

frontier = set([seed_url]) # going to
explored = set() # already did

domain_match = domain_re.match(seed_url)

protocol = domain_match.group(1)
domain = domain_match.group(2)

pages = 0

while len(frontier) > 0 and (page_limit == 0 or pages < page_limit):
    url = frontier.pop()
    r = requests.get(url)

    print('[{0}] {1}'.format(r.status_code, url))

    if r.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
        all_links = [link.get('href') for link in soup.find_all('a') if link.get('href') is not None]
        internal_links = []

        for link in all_links:
            domain_match = domain_re.match(link)

            if domain_match is None:
                if javascript_re.match(link) is not None:
                    # Ignore 'javascript:' URLS
                    continue

                if link[0] != '/':
                    internal_links.append('{0}://{1}/{2}'.format(protocol, domain, link))
                else:
                    internal_links.append('{0}://{1}{2}'.format(protocol, domain, link))
            elif domain_match.group(2) == domain:
                internal_links.append(link)

        explored.add(url)

        outlinks_before = len(frontier)
        for link in internal_links:
            if link not in explored:
                frontier.add(link)
        outlinks = len(frontier) - outlinks_before

        url_hash = hashlib.sha1(url.encode()).hexdigest()
        filename = f'{url_hash}.html'
        with open(f'repository/{filename}', 'w') as f:
            f.write(r.text)

        report_csv.writerow([url, filename, outlinks])

        pages += 1

report_file.close()
