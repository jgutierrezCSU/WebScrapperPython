#!/usr/bin/python3.5
from bs4 import BeautifulSoup
import requests
import subprocess
import csv
import re
import os
import smtplib
import imghdr
from email.message import EmailMessage
import pandas as pd


subprocess.call(['touch', 'lab9seven.csv'])
MAX = 300.00
url_list = []
item_list = []
page_counter = 0
item_counter = 0
max_item_counter = 30

homepage = 'https://www.walmart.com/search/?query=sony%20%20headphones'
landing = requests.get(homepage)
content = landing.content
firstsoup = BeautifulSoup(content, 'lxml')
num_results = firstsoup.find('div',{'class':'result-summary-container'}).text #gets the div tag w/ num of results
count = str(num_results)
tot_count = count[-11:-8]
page_count = int(int(tot_count)/10)-3
for i in range(1,page_count):
	print('found',i)
	url_list.append('https://www.walmart.com/search/?page=' + str(i) + '&ps=10&query=sony%20%20headphones')
for url in url_list:
	page_counter = page_counter + 1
	result = requests.get(url)
	c = result.content
	soup = BeautifulSoup(c, 'lxml')
	summary = soup.find('ul', {'class':'search-result-gridview-items four-items'}) #gets the grid view of results
	page_list = summary.findAll('li')

	for page in page_list:
		item_counter = item_counter + 1
		mytuple = ()
		# to get the item name
		title = page.find('a', {'class': 'product-title-link'}).text
		print('title :',title)
		if re.search('Noise', title, re.IGNORECASE):
			mytuple = mytuple + (title,)

 		# to get the item price
		price_summary = page.find('span', {'class' : 'search-result-productprice gridview enable-2price-2'})
		if price_summary is None:
 			mytuple = mytuple + ('No Price Available',)
		else:
			if price_summary.find('span', {'class': 'price-main-block'}) is not None:
				price = price_summary.find('span', {'class': 'price-main-block'}).text
				reg_price =re.search("\d+\.\d{1,2}",price)
				if(reg_price): #making sure array is not empty
					a_price=float(reg_price[0])# reg ex stores results in array. get first integer found
					if re.search('Noise', title, re.IGNORECASE) and a_price < MAX and isinstance(a_price, float):
						mytuple = mytuple + (a_price,)
			else:
				mytuple = mytuple + ('No Price Available',)

		#item rating
		
		# <span class="visuallyhidden seo-avg-rating">3.8</span>
		initial_rating = page.find('span', {'class' : 'visuallyhidden seo-avg-rating'}).text
		
		rating = initial_rating
		rating=re.search("(-?[0-9]+(?:[,.][0-9]+)?)",rating)# get int or double
		print(rating[0])
		rating=rating[0] + " out of 5"
		
		if re.search('Noise', title, re.IGNORECASE):
			mytuple = mytuple + (rating,)
		
		#get Reviews-------
		
		#old
		#reviews = page.find('span', {'class' : 'stars-reviews font-normal'})
		#updated
		if page.find('span', {'class' : 'seo-review-count visuallyhidden'}) is not None:
			reviews = page.find('span', {'class' : 'seo-review-count visuallyhidden'}).text 
			print('REV',reviews)
		#reviews = initial_rating[38:]# get a small chuck of string w/ reviews
		#reviews=re.search("[0-9]+",reviews) # get integers from that chunk
		#reviews=reviews[0] # reg ex stores results in array. get first integer found
		if re.search('Noise', title, re.IGNORECASE):
			mytuple = mytuple + (reviews,)
		
		if re.search('Noise', title, re.IGNORECASE):
			
			item_list.append(mytuple)

		if item_counter >= max_item_counter:
			break

def comparePricesSendEmail(prevCSV,newCSV):
	
	prevCSV=prevCSV.head(5)
	newCSV=newCSV.head(5)
	print('Prev Top 5 : ',prevCSV)
	print('New Top 5 : ',newCSV)
	if prevCSV.equals(newCSV):
		pass
	else:
		EMAIL_ADDRESS = 'njdevil707@gmail.com'
		#print("enter pword for ", EMAIL_ADDRESS , ":")
		EMAIL_PASSWORD = ''
		contacts = ['jesusg714@gmail.com']
		msg = EmailMessage()
		msg['Subject'] = 'Prices have changed'
		msg['From'] = EMAIL_ADDRESS
		msg['To'] = 'jesusg714@gmail.com'
		msg.set_content('File attached...')
		#send HTML
		msg.set_content('This is a plain text email')

		msg.add_alternative("""\
		<!DOCTYPE html>
		<html>
		    <body>
		        <h1 style="color:SlateGray;"> """+str(newCSV)+"""</h1>
		    </body>
		</html>
		""", subtype='html')


		with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
		    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
		    smtp.send_message(msg)
		    #print('not equals')
		


#create csv with Pandas
pd.set_option('mode.chained_assignment', None)
a_file=pd.DataFrame(item_list)
a_file.columns=['Title', 'Price', 'Rating', 'Reviews']
a_file=a_file.set_index('Title') # remove default index

#sort w/ pandas
# -----clean up ----
#will remove string that are in Price column
sortedFile = a_file[pd.to_numeric(a_file['Price'], errors='coerce').notnull()]
sortedFile['Price'] = sortedFile['Price'].astype(float)
#convert Price column to float otherwise lexsorted result
sortedFile.Price = sortedFile.Price.astype(float)
sortedFile.sort_values("Price", axis = 0, ascending = True,inplace = True, na_position ='last')
#-- end of clean up ------

#before saving new csv localy , compare prices betwen prev results and new results
#get prev csv results
#sortedFile.to_csv('lab9seven.csv') # uncomment for first time running program
prevCSVFile = pd.read_csv("lab9seven.csv")
prevCSVFile=prevCSVFile.set_index('Title') # remove deafult index 
newCSVFile =sortedFile

# functions compares top 5 results if false , send email w/ new changes
comparePricesSendEmail(prevCSVFile,newCSVFile)

sortedFile.to_csv('lab9seven.csv')


