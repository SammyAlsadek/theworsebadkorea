import csv
from bs4 import BeautifulSoup
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('report_file')

args = parser.parse_args()

report_file = open(args.report_file, 'r', newline='')
report_csv = csv.DictReader(report_file)

zipf_file = open('zipf.csv', 'w', newline='')
zipf_csv = csv.writer(zipf_file)
zipf_csv.writerow(['Word', 'Frequency'])

freqs = {}
for row in report_csv:
    if not row['Filename']:
        continue
    page = open(f"repository/{row['Filename']}", 'r')
    page_words = re.findall(r'\w+', BeautifulSoup(page, 'html.parser').text.lower())
    seen = []
    for word in page_words:
        if word not in freqs:
            freqs[word] = 0
        if word not in seen:
            freqs[word] += page_words.count(word)
            seen.append(word)

for entry in sorted(freqs.items(), key=lambda item: item[1], reverse=True):
    zipf_csv.writerow(list(entry))

zipf_file.close()