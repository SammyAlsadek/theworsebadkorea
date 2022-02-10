import csv
import hashlib
from os import mkdirs
import re
from time import sleep

from bs4 import BeautifulSoup
import requests

# TODO: Convert this to a CLI arg
seed_url = 'https://www.telemundo.com/'

# -- setup files/directories --
report_file = open('report.csv', 'w', newline='')
report_csv = csv.writer(report_file)
report_csv.writerow(['URL', 'Filename', 'Outlinks'])

mkdirs('repository', exist_ok=True)

# -- initial setup --
frontier = set([seed_url]) # going to
explored = set() # already did

domain_re = re.compile(r'(https?)?:\/\/(.*?)(/.*)')
domain = domain_re.match(seed_url).group(2)

while len(frontier) > 0:
    url = frontier.pop()
    r = requests.get(url)

    print('[{0}] {1}'.format(r.status_code, url))

    if r.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
        all_links = [link.get('href') for link in soup.find_all('a') if link.get('href') is not None]
        internal_links = []

        for link in all_links:
            match = domain_re.match(link)
            if match is None:
                if link[0] != '/':
                    internal_links.append('http://{0}/{1}'.format(domain, link))
                else:
                    internal_links.append('http://{0}{1}'.format(domain, link))
            elif match.group(2) == domain:
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

report_file.close()
