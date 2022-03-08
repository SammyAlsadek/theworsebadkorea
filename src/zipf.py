# cry inside
# ahhhhhhhhh

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

zipf_file = open('words.csv', 'w', newline='')
zipf_csv = csv.writer(zipf_file)
zipf_csv.writerow(['Filename', 'Number of Unique Words'])

file_to_unique_words = {}
unique_list = []
for row in report_csv:
    if not row['Filename']:
        continue
    page = open(f"repository/{row['Filename']}", 'r')
    page_words = re.findall(r'\w+', BeautifulSoup(page, 'html.parser').text.lower())
    for word in page_words:
        if word not in unique_list:
            unique_list.append(word)
            if str(row['Filename']) not in file_to_unique_words:
                entry = str(row['Filename'])
                file_to_unique_words[entry] = 0
            else:
                file_to_unique_words[str(row['Filename'])] += 1


zipf_file.close()
