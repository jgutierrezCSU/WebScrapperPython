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
import email

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText




# subprocess.call(['touch', 'lab9seven.csv'])
MAX = 300.00 # set maximum price
url_list = []
item_list = []
page_counter = 0
item_counter = 0
max_item_counter = 30

# get user input
print('Search: ')
tmp=input()

#URL encoding convertion (setting to Percent Encoding)
search_cri=tmp.replace(" ", "%20")
homepage='https://www.walmart.com/search/?query='+search_cri

#homepage = 'https://www.walmart.com/search/?query=sony%20%20headphones'
landing = requests.get(homepage)
content = landing.content
firstsoup = BeautifulSoup(content, 'lxml')
num_results = firstsoup.find('div',{'class':'result-summary-container'}).get_text() #gets the div tag w/ num of results
count = str(num_results)

#tot_count = count[-11:-8]

#place all ints into list and get last item as total results
tmp_count=re.findall(r'\d+', num_results)
tot_count=tmp_count[-1]

print(tot_count)

page_count = int(int(tot_count)/10)
if page_count <= 1:
	page_count =2
print(page_count)
for i in range(1,page_count):
	print('found',i)
	url_list.append('https://www.walmart.com/search/?page=' + str(i) + '&ps=10&query='+search_cri)
for url in url_list:
	page_counter = page_counter + 1
	result = requests.get(url)
	c = result.content
	soup = BeautifulSoup(c, 'lxml')

	#get summary for grid views
	summary = soup.find('ul', {'class':'search-result-gridview-items four-items'}) #gets the grid view of results
	if summary is not None:
		page_list = summary.findAll('li')

	#if not grid then List
	#get summary for list view
	if summary is None:
		summary = soup.find('div', {'class':'search-result-listview-items'}) #gets the grid view of results
		#print(summary)
		page_list = summary.findAll('div')

	

	for page in page_list:

		#print(page)
		print(page_list)
		print('X')
		item_counter = item_counter + 1
		mytuple = ()
		# to get the item name
		title = page.find('a', {'class': 'product-title-link'}).get_text()
		if title is not None and re.search('Noise', title, re.IGNORECASE):
			print('title :',title)
		
			mytuple = mytuple + (title,)

	 		# to get the item price
			price_summary = page.find('span', {'class' : 'search-result-productprice gridview enable-2price-2'})
			if price_summary is None:
	 			mytuple = mytuple + ('No Price Available',)
			else:
				if price_summary.find('span', {'class': 'price-main-block'}) is not None:
					price = price_summary.find('span', {'class': 'price-main-block'}).get_text()
					reg_price =re.search("\d+\.\d{1,2}",price)
					if(reg_price): #making sure array is not empty
						a_price=float(reg_price[0])# reg ex stores results in array. get first integer found
						if re.search('Noise', title, re.IGNORECASE) and a_price < MAX and isinstance(a_price, float):
							mytuple = mytuple + (a_price,)
				else:
					mytuple = mytuple + ('No Price Available',)

			#item rating
			
			initial_rating = page.find('span', {'class' : 'visuallyhidden seo-avg-rating'}).get_text()
			
			rating = initial_rating
			rating=re.search("(-?[0-9]+(?:[,.][0-9]+)?)",rating)# get int or double
			print(rating[0])
			rating=rating[0] + " out of 5"
			
			mytuple = mytuple + (rating,)
			
			#get Reviews-------
			
			#old
			#reviews = page.find('span', {'class' : 'stars-reviews font-normal'})
			#updated
			if page.find('span', {'class' : 'seo-review-count visuallyhidden'}) is not None:
				reviews = page.find('span', {'class' : 'seo-review-count visuallyhidden'}).get_text()
				
			#reviews = initial_rating[38:]# get a small chuck of string w/ reviews
			#reviews=re.search("[0-9]+",reviews) # get integers from that chunk
			#reviews=reviews[0] # reg ex stores results in array. get first integer found

			mytuple = mytuple + (reviews,)
							
			item_list.append(mytuple)

			if item_counter >= max_item_counter:
				break
			# print(page_count)
			# if page_count ==2:
			# 	break


def comparePricesSendEmail(prevCSV,newCSV):
	head_lim=10
	prevCSV=prevCSV.head(head_lim)
	newCSV=newCSV.head(head_lim)
	print('Prev Top',head_lim,' : ',prevCSV)
	print('New Top',head_lim,' : ',newCSV)
	if prevCSV.equals(newCSV):
		pass
	else:
		EMAIL_ADDRESS = 'njdevil707@gmail.com'
		#print("enter pword for ", EMAIL_ADDRESS , ":")

		#EMAIL_PASSWORD = input()
		read_pword = open("ep.txt","r")
		EMAIL_PASSWORD=read_pword.readline()

		fname="Top10ByPrice.csv"
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

		#for attachments
		body = "The Prices have changed"
		msg.attach(MIMEText(body, "plain"))
		with open(fname, "rb") as attachment:
		# Add file as application/octet-stream
		# Email client can usually download this automatically as attachment
			part = MIMEBase("application", "octet-stream")
			part.set_payload(attachment.read())

		# Encode file in ASCII characters to send by email
		encoders.encode_base64(part)
		# Add header as key/value pair to attachment part
		part.add_header(
			"Content-Disposition",
			f"attachment; filename= {fname}",
		)
		# Add attachment to message and convert message to string
		msg.attach(part)
		text = msg.as_string()

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
sortedFile.sort_values("Price", axis = 0, ascending = False,inplace = True, na_position ='last')
#-- end of clean up ------

#before saving new csv localy , compare prices betwen prev results and new results
#get prev csv results
#sortedFile.to_csv('Top10ByPrice.csv') # uncomment for first time running program
prevCSVFile = pd.read_csv("Top10ByPrice.csv")
prevCSVFile=prevCSVFile.set_index('Title') # remove deafult index 
newCSVFile =sortedFile
prevCSVFile.to_csv('Prev10ByPrice.csv')

# functions compares top 10 results if false , send email w/ new changes
comparePricesSendEmail(prevCSVFile,newCSVFile)

sortedFile.to_csv('Top10ByPrice.csv')


