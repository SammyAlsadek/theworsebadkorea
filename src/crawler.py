import argparse
import csv
import hashlib
from os import makedirs
from os.path import exists
import re
from time import sleep
from urllib import robotparser
from urllib.parse import urlparse

from langdetect import detect
from bs4 import BeautifulSoup
import requests

# -- language detection and verification --


def detect_language(soup: BeautifulSoup) -> str:
    return detect(soup.text)


def verify_language(language: str) -> bool:
    if language == desired_language:
        return True
    return False


def isDesiredLanguage(soup: BeautifulSoup) -> bool:
    return verify_language(detect_language(soup))


parser = argparse.ArgumentParser()
parser.add_argument('seed_url')
parser.add_argument('-p', '--pages', default=0, type=int)
parser.add_argument('-l', '--language', default='en', type=str)

args = parser.parse_args()

seed_url = args.seed_url
page_limit = args.pages
desired_language = args.language

# -- setup files/directories --
report_file = open('report.csv', 'w', newline='')
report_csv = csv.writer(report_file)
report_csv.writerow(['URL', 'Filename', 'Outlinks'])

makedirs('repository', exist_ok=True)

# -- initial setup --
dir_re = re.compile(r'(\/.+\/|\/)')

frontier = set([seed_url])  # going to
explored = set()  # already did

seed_parse = urlparse(seed_url)

seed_scheme = seed_parse.scheme
seed_domain = seed_parse.netloc

pages = 0

# -- robots.txt magic
robots_entries = {"Disallowed":[], "Allowed":[]}
robots_response = requests.get(f'{seed_scheme}://{seed_domain}/robots.txt')
if robots_response.ok:
    for line in robots_response.text.splitlines():
        if line.startswith('Allow'):
            robots_entries['Allowed'].append(re.compile(line.split(':')[1].strip().replace('*', '.*')))
        elif line.startswith('Disallow'):
            robots_entries['Disallowed'].append(re.compile(line.split(':')[1].strip().replace('*', '.*')))

while len(frontier) > 0 and (page_limit == 0 or pages < page_limit):
    curr_url = frontier.pop()
    curr_path = urlparse(curr_url).path
    curr_dir = dir_re.match(curr_path).group(1)

    allowed = True

    for pattern in robots_entries['Disallowed']:
        if pattern.match(curr_path):
            allowed = False

    for pattern in robots_entries['Allowed']:
        if pattern.match(curr_path):
            allowed = True

    if not allowed:
        print(f'Disallowed: {curr_dir}')
        continue

    r = requests.get(curr_url)
    final_url = r.url

    # Some servers redirect 404s back to a valid page instead of exposing a 404
    # so we instead check to see if the final redirected URL is already visited
    # to avoid recrawling a previously visited page
    if final_url in explored:
        print('[{0}, {1}]+ {2}'.format(r.status_code,
              r.headers['content-type'], curr_url))
        continue

    if r.ok and 'content-type' in r.headers and r.headers['content-type'].startswith('text/html'):
        print('[{0}, {1}] {2}'.format(r.status_code,
              r.headers['content-type'], curr_url))

        soup = BeautifulSoup(r.text, 'html.parser')
        desired = isDesiredLanguage(soup)
        all_links = [link.get('href')
                     for link in soup.find_all('a') if link.get('href')]

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

        # Avoid excess file I/O on crawled pages by hashing the final url instead
        # of the requeted URL and checking if it was previously downloaded
        url_hash = hashlib.sha1(final_url.encode()).hexdigest()
        filename = f'{url_hash}.html'

        if desired:
            if not exists(filename):
                with open(f'repository/{filename}', 'w') as f:
                    f.write(r.text)
            report_csv.writerow([curr_url, filename, outlinks])
            pages += 1
        else:
            print('- Skipped for lang verification')
            report_csv.writerow([curr_url, '', outlinks])

        # Add both the path requested and the final path after redirects to
        # explored set
        explored.add(curr_url)
        explored.add(final_url)
    else:
        content_type = r.headers['content-type'] if 'content-type' in r.headers else '?'
        print('[{0}, {1}]* {2}'.format(r.status_code, content_type, curr_url))

report_file.close()
