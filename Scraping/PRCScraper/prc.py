#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 18:04:58 2020

@author: TheNsofini


This program scrape data from the website of the PR of the republic of Cameroon. It can be adapted to scrape his visits of his speeches.

"""
import csv
import requests
from bs4 import BeautifulSoup
import time

#We want to tract the progress so we can tell where it broke!
import logging
logging.basicConfig(filename='pr_speeches.log', level=logging.INFO, format='%(levelname)s:(message)s')


class Content:
    """
    Common base class for all articles/pages
    """
    def __init__(self, url, title, body, date=None):
        self.url = url
        self.title = title
        self.body = body
        self.date = date
        self.next_url = None
        
        logging.info('Succesfully scraped site: {} - {}'.format(self.url, self.title))
        
    def print(self):
        """
        Flexible printing function controls output
        """
        print(f"URL: {self.url}")
        print(f"URL: {self.next_url}")
        print(f"--------------------------------------------------------------")
        print(f"TITLE: {self.title}")
        print(f"BODY:\n{self.body}")
        

class Webpage:
    """
    Contains information about website structure
    """
    def __init__(self, name, url, title_tag, body_tag, next_tag):
        self.name = name
        self.url = url
        self.title_tag = title_tag
        self.body_tag = body_tag
        self.next_tag = next_tag
        
        logging.info('Succesfully initialized site: {} - {}'.format(self.url, self.name))
        
# =============================================================================
# class Webpage:
#     """
#     Contains information about website structure
#     """
#     def __init__(self, name, url, title_tag, body_tag):
#         self.name = name
#         self.url = url
#         self.title_tag = title_tag
#         self.body_tag = body_tag
# 
# 
#     
#     def getPage(self, url):
#         try:
#             req = requests.get(url)
#         except requests.exceptions.RequestException:
#             return None
#         return BeautifulSoup(req.text, 'html.parser')
# 
# 
#     def safeGet(self, page_obj, selector):
#         """
#         Utility function used to get a content string from a
#         Beautiful Soup object and a selector. Returns an empty
#         string if no object is found for the given selector
#         """
#         selected_elems = page_obj.select(selector)
#         if selectedElems is not None and len(selected_elems) > 0:
#             return '\n'.join( [elem.get_text() for elem in selected_elems])
#         
#         return ''
#     
#     def parse(self, site, url):
#         """
#         Extract content from a given page URL
#         """
#         bs = self.getPage(url)
#         if bs is not None:
#             title = self.safeGet(bs, site.title_tag)
#             body = self.safeGet(bs, site.body_tag)
#             if title != '' and body != '':
#                 content = Content(url, title, body)
#                 content.print()
# =============================================================================
                
class Crawler:
    '''
    Crawler to go through a provided page and retrive the url, title, body and next url
    '''
    
    def getPage(self, url):
        """
        Utility function to get the data using request
        
        Inputs
        ------
        url: the page link
        
        Returns
        -------
        Beautifulsoup object
        """
        
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, 'html.parser')


    def safeGet(self, page_obj, selector):
        """
        Utility function used to get a content string from a
        Beautiful Soup object and a selector.
        Checks if selector is url based, and return the url OR
        Returns an empty tring if no object is found for the given selector
        
        Inputs
        ------
        page_obj: the beautifulsoup object 
        selector: selector for the tag
        
        Returns
        -------
        The string or URL
        
        """
        selected_elems = page_obj.select(selector)
        if selected_elems is not None and len(selected_elems) > 0:    
            if 'a' == selector.split()[-1]: #check if selector is url and pick first
                return selected_elems[0]['href']
                
            return '\n'.join( [elem.get_text() for elem in selected_elems])
        
        return ''
    
    def parse(self, site, url):
        """
        Extract content from a given page URL
        """
        bs = self.getPage(url)
        if bs is not None:
            title = self.safeGet(bs, site.title_tag)
            body = self.safeGet(bs, site.body_tag)
            next_url = self.safeGet(bs, site.next_tag)
            #Reformat because only relative urls are extracted. We will need to extract abosulte at some point
            next_url = f"{url.split('/en')[0]}{next_url}"
            if title != '' and body != '':
                content = Content(url, title, body)
                content.next_url = next_url        #Look for URL to the next page
                #content.print()
                
        return content
    





#=====================start=====================================================

#Parameters of the page we want tp scrape
baseUrl = "https://prc.cm"        
relurl = "/en/news/speeches-of-the-president/"       
first_page = "4125-head-of-state-s-message-to-the-youth-on-the-54th-edition-of-the-national-youth-day"


# The selectors for what we are looking for
title_tag = 'h2 a'
body_tag = 'article p'
next_tag = 'li.next a'
first_url = baseUrl + relurl + first_page

#first_url = 'https://prc.cm/en/news/speeches-of-the-president/459-speech-by-h-e-paul-biya-president-of-the-republic-on-the-occasion-of-the-inauguration-ceremony-of-the-natural-gas-processing-unit-of-ndogpassi-douala-15-november-2013'
#first_url = 'https://prc.cm/en/news/speeches-of-the-president/528-speech-by-the-president-of-the-republic-during-the-round-table-on-the-fight-against-trafficking-in-and-poaching-of-endangered-species'
#first_page = 'https://prc.cm/en/news/speeches-of-the-president/4105-ceremonie-de-triomphe-de-la-37eme-promotion-de-l-ecole-militaire-interarmees-baptisee-general-de-division-kodji-jacob'

prc_site = Webpage('PRC Speeches', url=first_url, title_tag=title_tag, body_tag=body_tag, next_tag=next_tag)

print("============== scraping in progress, it might take some time ========================")
#Initialize a crawler


#data.print()
# Store the data in CSV file:
with open('pr_speeches.csv', 'w') as speeches:
    speech = csv.writer(speeches, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    print("================= started writing ===============================================")
    speech.writerow(['Url', 'Speech_title', 'body', 'next_speech' ])
    #speech.writerow([data.url, data.title, data.body, data.next_url ])
    
    #crawler = Crawler()
    #data = crawler.parse(prc_site, prc_site.url)
    
    #Continue to write other programs
    # Do some visual output
    k = 1 
    site = Webpage('PRC Speeches', url=first_url,
                       title_tag=title_tag, body_tag=body_tag, next_tag = next_tag)
    
   # start_getting_more = data.next_url
    while site.url != baseUrl:
        #continue to scrap and write
        time.sleep(2)
        print(f" Speech : {k}")
        
        crawler = Crawler()       
        data = crawler.parse(site, site.url)
        speech.writerow([data.url, data.title, data.body, data.next_url ]) 
        
        site = Webpage('PRC Speeches', url=data.next_url,
                       title_tag=title_tag, body_tag=body_tag, next_tag = next_tag)
         
        
        print("\n New crawler {}\n".format(data.next_url))
        k += 1
        
    print("================= scraping done  ===============================================")
    
    print("================= finihsed writing ===============================================")



# =============================================================================
# 
#  data = requests.get(urll)
# data = BeautifulSoup(data.text, 'html.parser')
#  data.article.h2.text.strip()
# data.article.find('li', attrs={'class':'next'}).a['href']
# 
# data.find('li', attrs={'class':'next'}).a['href']
# data.find('h2').text.strip()
# 
# data.find('h2').a['href']
# data.select('li', attrs={'class':'next'})
# 
# data.article.find_all('p')
# : data.select(article ul)
#  data.select('ul.next')
# data.select('li.next')
# data.select('h2')
#  data.select('h2').text
#  data.select('h2 a')
# data.find('h2').text.strip()
#  data.select('h2 a')
# data.find('h2').a.text
# 
# data.find('h2')
# 
# data.article.h2
#  data.article.find_all(p)
# data.article.find_all('p')
#  data.article.find_all(p)
# data.article.find_all('p')
# 
# '\n'.join( [ e.text for e in data.article.find_all('p')])
# '\n'.join( [ e.text for e in data.('article p')])
# 
# '\n'.join( [ e.text for e in data.select('article p')])
# 
#                 
# =============================================================================
