#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 17:39:49 2019

@author: jnsofini
The details of the code is found in found in the blog post.
"""

from bs4 import BeautifulSoup
from time import sleep, time
from random import randint
from requests import get
from warnings import warn
import os.path
import csv


def getFeatures(container, fh):
    '''
    Takes a doctor container for a page and indenfy various features
    Inputs
    ======
    container: beautiful soup object containing everything vars of a doctor
    including name, specialty, ratings, number of votes, sex
    
    optional returns, should they be used. These are list of 
    names, specialty, ratings, counts, gender for a page
    
    '''
    
    #Optional containers to stor each of the features for a single page
    names = []
    specialty = []
    ratings = []
    counts = []
    gender = []
    for doctor in container:
        # If the doctor has ratings, then extract:
        rating = float(doctor.find('span', class_ = 'star-rating')['title'])
        if rating != 0:    
            name = doctor.a.get_text() #extract the name from the a tag
            names.append(name)   
            #specialty is extracted from the a tag
            special = doctor.find('div', class_ = 'search-item-specialty').a.get_text()
            specialty.append(special)
            #rating
            ratings.append(rating)
            #Number of ratings
            num_ratings = doctor.find('div', class_ = "star-rating-count").get_text()
            counts.append(int(num_ratings.split()[0]))
            #Get the sexurl of the doctor from the profile avater
            sexurl = doctor.find('img', class_="search-item-image")
            sex = os.path.dirname(sexurl['src'])[44] 
            gender.append(sex)
            
            #print(name, special, rating, num_ratings, sex )
            fh.writerow([name, special, sex, rating, int(num_ratings.split()[0])])
            
    return names, specialty, ratings, counts, gender #optional return for other use

#--------------------------------------------------------------------------------------
def getPages(fh):
    '''
    Takes file handle and use it to call getfeatures
    Extracts the pages and call the getfeature functions with each page info
    
    '''
        
    requests = 0
    # Extract data from individual doctor container
    for page in range(1, 129):
        if page == 1: 
            response = get('https://www.ratemds.com/best-doctors/sk/regina/')   
        else:
            response = get('https://www.ratemds.com/best-doctors/sk/regina/?page='+str(page))
        sleep(randint(8,15))
    
        # Monitor the requests
        requests += 1
        elapsed_time = time() - start_time
        print('Request:{}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
    
        #Throw a warning for non-200 status codes
        if response.status_code != 200:
            warn('Request: {}; Status code: {}'.format(requests, response.status_code))
    
        #Parse the content of the request with BeautifulSoup
        page_html = BeautifulSoup(response.text, 'html.parser')
    
        #Select all the 11 doctor containers from a single page
        doctor_container = page_html.find_all('div', class_ = 'search-item doctor-profile')
        
        dnames, dspecialty, dratings, dcounts, dgender = getFeatures(doctor_container, fh)


#--------------------------------------------------------------------------------------

# =============================================================================
# def writeData(fh, data):
#     '''
#     Use to write the data to a file
#     Input
#     =====
#     fh: file handle
#     data: data to write
#     '''
#     names, specialty, ratings, counts, gender = data
#     with open(fh, mode='w') as doc_file:
#         doc_writer = csv.writer(doc_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#         doc_writer.writerow(['Name', 'Specialty', 'Ratings', 'Reviews', 'Gender'])
#         for item in zip(names, specialty, ratings, counts, gender):
#             doc_writer.writerow(item)
# =============================================================================

#-----------------------------------------------------------------------------------------

print('======================================================================================')
print('=======  The ratemeds page is scaping is running. It may take some time   ============')
print('======================================================================================')

# =============================================================================
# # Lists to store the scraped data in
# names = []
# specialty = []
# ratings = []
# counts = []
# gender = []
# 
# =============================================================================
# Preparing the monitoring of the loop
start_time = time()

with open('doctors.csv', mode='w') as doc_file:
    doc_writer = csv.writer(doc_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    doc_writer.writerow(['Name', 'Specialty', 'Ratings', 'Reviews', 'Gender'])
    
    getPages(doc_writer)
    
print("Time taken: {}".format(time() - start_time))
    
