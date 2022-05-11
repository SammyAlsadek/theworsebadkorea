import argparse
import csv
import json
import re
import math

from bs4 import BeautifulSoup

# -- CONSTANTS --
k1 = 1.2
k2 = 1000
b = 0.75

parser = argparse.ArgumentParser()
parser.add_argument('report_file')
parser.add_argument('index_file')
parser.add_argument('pagerank_file')
parser.add_argument('search_txt')

args = parser.parse_args()
report_filename = args.report_file
index_filename = args.index_file
pagerank_filename = args.pagerank_file
search_txt = args.search_txt

report_file = open(report_filename, 'r')

with open(index_filename, 'r') as index_file:
    index = json.load(index_file)

pagerank = {}
with open(pagerank_filename, 'r') as pagerank_file:
    pagerank_csv = csv.DictReader(pagerank_file)
    for row in pagerank_csv:
        pagerank[row['URL']] = float(row['PageRank'])

filename_url_map = {}

# Generate collection stats
print('Generating collection stats...')

collection_len = 0
avg_doc_len = 0
for row in csv.DictReader(report_file):
    if not row['Filename']:
        continue

    collection_len += 1

    filename_url_map[row['Filename']] = row['URL']

    # Load document and calculate number of words
    soup = BeautifulSoup(open(f"repository/{row['Filename']}", 'r'), 'html.parser')
    avg_doc_len += len(re.findall(r'\w+', soup.get_text()))

avg_doc_len /= collection_len
print(f'Collection length: {collection_len}')
print(f'Average document length: {avg_doc_len}')

# Generate results utilizing the BM25 scoring algorithm
print('Generating results...')
results = {}
search_txt = search_txt.lower()
search_terms = re.findall(r'\w+', search_txt)
for term in search_terms:
    if term in index:
        documents = index[term]
        qf_i = search_txt.count(term)
        n_i = len(documents)

        base_score = math.log(1/((n_i + 0.5)/(collection_len - n_i + 0.5))) * (((k2 + 1) * qf_i) / (k2 + qf_i))

        for doc in documents:
            soup = BeautifulSoup(open(f"repository/{doc}", 'r'), 'html.parser')
            raw_text = soup.get_text().lower()
            doc_len = len(re.findall(r'\w+', raw_text))
            f_i = raw_text.count(term)

            k = k1 * ((1 - b) + b * (doc_len / avg_doc_len))
            score = base_score * (((k1 + 1) * f_i) / (k + f_i))

            if doc not in results:
                results[doc] = score
            else:
                results[doc] += score

# Combine with PageRank
print('Generating final results...')
final_results = []
for filename, score in results.items():
    final_results.append((filename_url_map[filename], score * pagerank[filename_url_map[filename]]))

final_results.sort(key=lambda result: result[1], reverse=True)
print(final_results)
