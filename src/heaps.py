import csv
import argparse
import re

import numpy as np

from collections import OrderedDict
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt

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

xplot = []
yplot = []
for i, row in enumerate(sorted(file_to_unique_words.items(), key=lambda item: item[1])):
    xplot.append(row[1])
    yplot.append(i)

plt.title("Heap Plot")
plt.xlabel("Collection Growth")
plt.ylabel("Vocabulary Growth")
plt.plot(xplot, yplot)
plt.xticks(np.arange(min(xplot), max(xplot)+1, len(xplot)/7))
plt.show()