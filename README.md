[![Build Status](https://travis-ci.org/jgutierrezCSU/WebScrapperPython.svg?branch=master)](https://travis-ci.org/jgutierrezCSU/WebScrapperPython)

Web Scrapper using python :
As of now it is dedicated to scrape Walmart website.

Example:
I search walmart for Sony headphones. The pattern being “noise” wich will filter the results and grabbing any items which are noise canceling head phones.
I used multiple regular expressions to extract data. Line 54 I use reg ex to find the price. Additionally in line 64 to get the rating which could be an int or a double. Once the results were filters and extracted, I placed them in a list. From that list , I then used pandas to sort and clean the data and place it to a local csv.
Additionally It compares previous "scrapes" with new "scrape", if the prices have changed it will send an email.

RESULTS:

![alt text](https://github.com/jgutierrezCSU/WebScrapperPython/blob/master/photos/snip1.png?raw=true)





CSV FILE SAVED LOCALLY :
In the code, after line 124 , it starts to create and filter that data and place it into a csv file. Most of the clean up was making sure the data type in each column was the same. More specifically in the “Price” column since i needed that so I can use that column as a filter and sort it. As you can see , the results are only those having a key word of “noise” and the “Price” column is sorted

RESULTS:
![alt text](https://github.com/jgutierrezCSU/WebScrapperPython/blob/master/photos/snip2.png?raw=true)


UPDATE:
Walmart site is ever changing, this code works fine as long as some code is adjusted (usualy changing the way you get tags and HTML code).
Overall it a great structure to get started with Web Scrapping

UPDATE: Walmart has Forbidden webscrapper, next step is to focus on different site.
