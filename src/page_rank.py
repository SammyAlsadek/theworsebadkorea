import csv
from bs4 import BeautifulSoup
import argparse
from urllib.parse import urlparse
import re
import numpy as np

dir_re = re.compile(r'(\/.+\/|\/)')

parser = argparse.ArgumentParser()
parser.add_argument('report_file')

args = parser.parse_args()

MAX_PAGERANK_ITERS = 100
EPSILON = 10e-10

pagerank_file = open('pagerank.csv', 'w', newline='')
pagerank_csv = csv.writer(pagerank_file)
pagerank_csv.writerow(['URL', 'PageRank'])

report_file = open(args.report_file, 'r', newline='')
report_csv = csv.DictReader(report_file)
report = list(report_csv)
report_file.close()

links = [item['URL'] for item in report]
out_links = {}
N = 0

report_domain = None
report_scheme = None

print('Scraping outlinks: 0.00%')

for row in report:
    if not row['Filename']:
        continue

    N += 1

    if N % 100 == 0:
        percent = N / len(report) * 100
        print(f'Scraping outlinks: %.2f%%' % percent)
    
    if not report_domain:
        report_parse = urlparse(row['URL'])
        report_domain = report_parse.netloc
        report_scheme = report_parse.scheme

    curr_path = urlparse(row['URL']).path
    curr_dir = dir_re.match(curr_path).group(1)

    page = open(f"repository/{row['Filename']}", 'r')
    soup = BeautifulSoup(page, 'html.parser')
    
    all_links = [link.get('href') for link in soup.find_all('a') if link.get('href')]

    for link in all_links:
        link_parse = urlparse(link)
        scheme = link_parse.scheme
        domain = link_parse.netloc
        path = link_parse.path
        # Skip if not http/https
        if scheme and scheme not in ['http', 'https']:
            continue
        # Skip if domain != report domain
        if domain and domain != report_domain:
            continue
        # Skip if path is blank
        if not path:
            continue
        scheme = scheme if scheme else report_scheme
        domain = domain if domain else report_domain
        if path[0] == '/':
            link_url = f'{scheme}://{domain}{path}'
        else:
            path = f'{curr_dir}{path}'
            link_url = f'{scheme}://{domain}{path}'

        if not next((l for l in report if l['URL'] == link_url), False):
            continue

        if row['URL'] in out_links:
            out_links[row['URL']].append(link_url)
        else:
            out_links[row['URL']] = [link_url]

    page.close()

print(f'Building Google matrix ({len(links)}x{len(links)})')

# build the google matrix
M = np.zeros([len(links), len(links)])

for page in out_links.keys():
    for link in out_links[page]:
        if link not in links: #no dangly bois
            continue
        # `page` contributes one more to `link`'s ranking in the 'google' matrix
        M[links.index(link)][links.index(page)] += 1 

# divide each column by the sum of column
for i in range(len(links)):
    if M[:,i].sum() != 0:
        M[:,i] /= M[:,i].sum()

# generate the pagerank column vector
V = np.empty([len(links), 1])
V.fill(1./len(links))

print('Performing PageRank')

# run pagerank for some number of iterations
iters = 0
while iters < MAX_PAGERANK_ITERS:
    iters += 1
    W = np.matmul(M, V)
    # if the difference in vectors is negligible, terminate 
    if np.linalg.norm(W - V) < EPSILON:
        V = W
        break
    V = W

print(f'V sum: {np.sum(V)}')

for i in range(len(links)):
    pagerank_csv.writerow([links[i], V[i][0]])

pagerank_file.close()
