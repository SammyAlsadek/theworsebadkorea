import re

from bs4 import BeautifulSoup
import requests

seed_url = 'https://www.telemundo.com/'

frontier = set([seed_url]) # going to
explored = set() # already did

domain_re = re.compile(r'(https?)?:\/\/(.*?)(/.*)')
domain = domain_re.match(seed_url).group(2)

while len(frontier) > 0:
    url = frontier.pop()

    r = requests.get(url)
    print('{0}, status: {1}'.format(url, r.status_code))
    if r.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
        all_links = [link.get('href') for link in soup.find_all('a')]
        internal_links = []

        for link in all_links:
            match = domain_re.match(link)
            if match is None:
                internal_links.append('http://{0}/{1}'.format(domain, link))
            elif match.group(2) == domain:
                internal_links.append(link)

        explored.add(url)

        for link in internal_links:
            if link not in explored:
                frontier.add(link)
