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
    print(url)

    r = requests.get(url)
    print('Status: {0}'.format(r.status_code))

    if r.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
        all_links = [link.get('href') for link in soup.find_all('a') if link.get('href') is not None]
        internal_links = []

        for link in all_links:
            match = domain_re.match(link)
            if match is None:
                internal_links.append('http://{0}/{1}'.format(domain, link))
            elif match.group(2) == domain:
                internal_links.append(link)

        tokens = re.findall(r'\w+', soup.get_text())
        tokens = [token.lower() for token in tokens]
        print('Tokens: {0}'.format(len(tokens)))

        explored.add(url)

        outlinks_before = len(frontier)
        for link in internal_links:
            if link not in explored:
                frontier.add(link)
        outlinks_after = len(frontier)
        print('Outlinks: {0}\n'.format(outlinks_after - outlinks_before))
