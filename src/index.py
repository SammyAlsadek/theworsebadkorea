import csv
import json
from bs4 import BeautifulSoup
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('report_file')

args = parser.parse_args()

report_file = open(args.report_file, 'r', newline='')
report_csv = csv.DictReader(report_file)

index_file = open('index.json', 'w')

index = {}
for row in report_csv:
    if not row['Filename']:
        continue
    page = open(f"repository/{row['Filename']}", 'r')
    page_words = re.findall(r'\w+', BeautifulSoup(page, 'html.parser').text.lower())

    for word in page_words:
        if word not in index:
            index[word] = [row['Filename']]
        if row['Filename'] not in index[word]:
            index[word].append(row['Filename'])

json.dump(index, index_file, indent=2)
index_file.close()