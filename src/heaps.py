import csv
from collections import OrderedDict
from bs4 import BeautifulSoup
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('report_file')

args = parser.parse_args()

report_file = open(args.report_file, 'r', newline='')
report_csv = csv.DictReader(report_file)

heaps_file = open('heaps.csv', 'w', newline='')
heaps_csv = csv.writer(heaps_file)
heaps_csv.writerow(['Filename', 'Number of Unique Words'])

file_to_unique_words = OrderedDict()
unique_list = []
for row in report_csv:
    if not row['Filename']:
        continue
    page = open(f"repository/{row['Filename']}", 'r')
    page_words = re.findall(r'\w+', BeautifulSoup(page, 'html.parser').text.lower())
    for word in page_words:
        if word not in unique_list:
            unique_list.append(word)
            if row['Filename'] not in file_to_unique_words:
                entry = row['Filename']
                file_to_unique_words[entry] = 0
            else:
                file_to_unique_words[row['Filename']] += 1

for row in file_to_unique_words.items():
    heaps_csv.writerow(row)
heaps_file.close()