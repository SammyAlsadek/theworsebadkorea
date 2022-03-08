import argparse
import json
import re

parser = argparse.ArgumentParser()
parser.add_argument('index_file')
parser.add_argument('search_txt')

args = parser.parse_args()
index_filename = args.index_file
search_txt = args.search_txt

index_file = open(index_filename, 'r')
index = json.load(index_file)

results = set()
search_terms = re.findall(r'\w+', search_txt.lower())
for term in search_terms:
    if term not in index:
        results = set()
        break

    if len(results) == 0:
        results.update(index[term])
        continue

    for result in set(results):
        if result not in index[term]:
            results.remove(result)
            continue

print(results)
