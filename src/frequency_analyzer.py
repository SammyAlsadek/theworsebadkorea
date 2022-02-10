import csv
from bs4 import BeautifulSoup
import argparse
import re
from operator import itemgetter

parser = argparse.ArgumentParser()
parser.add_argument('report_file')

args = parser.parse_args()

report_file = open(args.report_file, 'r', newline='')
report_csv = csv.DictReader(report_file)

words_file = open('words.csv', 'w', newline='')
words_csv = csv.writer(words_file)
words_csv.writerow(['Word', 'Frequency'])

freqs = {}
for row in report_csv:
    page = open(f"repository/{row['Filename']}", 'r')
    page_words = re.findall(r'\w+', BeautifulSoup(page, 'html.parser').text.lower())
    for word in page_words:
        if word not in freqs:
            freqs[word] = 0
        freqs[word] += page_words.count(word)

for entry in sorted(freqs.items(), key=lambda item: item[1], reverse=True)[:100]:
    words_csv.writerow(list(entry))

words_file.close()