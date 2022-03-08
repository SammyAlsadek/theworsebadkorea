# Assignment 1a

1. Create Web Crawler
   - Input: 1 or more seeds
   - For each URL
   - Check if it can be crawled based on robots.txt
   - Check if the crawled page is in a desired language (see next slide)
   - Download the complete textual page content (including all html tags, but not images or external 
  Javascript/CSS) into a folder called repository
   - Add the page URL, additional statistics to a file called report.csv (see next slide)
   - Crawl all outlinks
   - Output: repository folder and report.csv

2. Run crawler 
   - 3 different domains, in different languages
   - At the end of the crawl, your program should have (for each domain):
   - Downloaded the content from all crawled pages into the repository folder
   - Generated one report.csvfile, which contains the following data for each downloaded page: 
   - URL, number of outlinks

3. Count word occurrences 
   - For each domain, output the top 100 most frequent words, and their 
  associated frequencies, e.g. Domain 1: the (3432), a (1843), of (743), etc.
   - Store in words.csv

# Submission
1. Crawler code - All code required to run the 
  crawler
2. Report (in PDF - 2 page max), containing:
   - The main components of the program
   - Any challenges faced during the development of the 
    crawler
   - An appendix containing details on these 3 crawls (e.g. 
    seeds, domains), as well as a list of the 100 most 
    frequent words for each crawl
   - Discussion about each team member’s contribution
   - Note: Graphs/screenshots can be added to an appendix, 
    and do not count towards page limit

# Submission Format
One .zip file: 
- GroupX.zip
- Report.pdf
- Code (folder)
- Output (folder)
- Report1.csv
- Report2.csv
- Report3.csv
- Words1.csv
- Words.2.csv
- Words3.csv
    
# Deadlines and submission
- Pick group (9 groups of 4) and domains:
- Wednesday, February 9th, end of day
- https://docs.google.com/spreadsheets/d/1rYbRtm
  x0j66Ke_FQTQiPqF3L2RVBaFk2-
  ApC9sGXO1E/edit#gid=0
- Submit report and code:
- Wednesday, February 23rd, end of day
- Canvas

# Resources
  Reading from and Writing to a URLConnection (Java)
  https://docs.oracle.com/javase/tutorial/networking/urls/readingWriting.html
  
  HTML parser (e.g. for link extraction)
  https://jsoup.org
  
  Language detection
  https://languagelayer.com

# Assignment 1b
Text Processing
- Perform word frequency analyses on the processed content for your 3 different crawls from part 1a 
- For each analysis: 
1. Zipf’s law
   - Calculate word frequencies and ranks using all textual content, i.e. not HTML tags (feel free to use any tool/language)
   - Plot word frequencies and word ranks (feel free to use any tool/language)
   - Check if crawled content follows Zipf’s law (i.e. compare with typical Zipf’s distribution)
2. Heap’s Law
   - Plot vocabulary growth by collection growth, e.g. as examples in 
class


Indexing
- Create a simple index as discussed in class
- Minimum: Simple Inverted Index, e.g.

Retrieval
- Implement a simple search system
- Minimum: Boolean Retrieval System (not including complex Boolean operators, e.g. OR, NOT)
- No GUI required, e.g.
   `Please enter your query: tropical fish`
   `Relevant results are: doc12, doc24, doc45`

