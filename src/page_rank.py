import csv
from bs4 import BeautifulSoup
import argparse
from urllib.parse import urlparse
import re
import numpy as np
import pickle

dir_re = re.compile(r'(\/.+\/|\/)')

parser = argparse.ArgumentParser()
parser.add_argument('report_file')

args = parser.parse_args()

pagerank_file = open('pagerank.csv', 'w', newline='')
pagerank_csv = csv.writer(pagerank_file)
pagerank_csv.writerow(['URL', 'PageRank'])

report_file = open(args.report_file, 'r', newline='')
report_csv = csv.DictReader(report_file)
report = list(report_csv)
report_file.close()

links = [item['URL'] for item in report]
in_links = {} # dict where key=page, value=number of pages that link to it
out_links = {}
N = 0

report_domain = None
report_scheme = None

for row in report:
    if not row['Filename']:
        continue

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

        # if next((l for l in report if l['URL'] == link_url), None) != None:
        #     continue

        if not any([True for line in report if link == line['URL']]):
            continue

        if row['URL'] in out_links:
            out_links[row['URL']].append(link_url)
        else:
            out_links[row['URL']] = [link_url]
        
        if link_url in in_links:
            in_links[link_url] += 1
        else:
            in_links[link_url] = 1

# test_pickle = open('test.pickle', 'wb')
# pickle.dump({'links': links,'out_links': out_links,'in_links': in_links}, test_pickle)

# test_pickle = open('test.pickle', 'rb')
# tpo = pickle.load(test_pickle)

# links = tpo['links']
# in_links = tpo['in_links']
# out_links = tpo['out_links']

# build the google matrix
M = np.zeros([len(links), len(links)])

for page in out_links.keys():
    for link in out_links[page]:
        if link not in links: #no dangly bois
            continue
        # `page` contributes one more to `link`'s ranking in the 'google' matrix
        M[links.index(link)][links.index(page)] += 1 


# divide each column by the sum of outlinks from a certain page
for i in range(len(links)):
    if M[:,i].sum() != 0:
        M[:,i] /= M[:,i].sum()

# generate the pagerank column vector
V = np.empty([len(links), 1])
V.fill(1./len(links))

# run pagerank for some number of iterations
iters = 0
while iters < 10:
    iters += 1
    V = np.matmul(M, V)

# get the indices for the 100 top pages
# ind = (-V).argsort()[:100]
ind = np.argpartition(V, -100, axis=0)[-100:]
# ind = idx[np.argsort((-V)[idx])]

# print the result
for i in ind:
    print(V[i[0]][0])
    print(links[i[0]])
