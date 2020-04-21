# Data Craping
The internet is a source of vast data; stored as web pages as well as other forms. In some projects, the data needed is not readily available in clean and formated form like cvs or excel or tables stored in databases, and APIs might not even exist or might be expensive to maintain. However, in some cases, we can extract data from html pages. In this project we obtain data from [ratems site](www.ratemds.com). 
 
We have established our goal to scape [ratems site](www.ratemds.com). The scaper here will focus on doctors in Saskatchewan. However, it can be readily adapted to any region in the world by adjusting the url. Our focus will be pages in https://www.ratemds.com/best-doctors/sk. ,A combination of these pages sends a relatively small number of requests. A request is what happens whenever a web page is accessed. A `request` of the content of a page from the server. The more requests we make, the longer our script will need to run, and the higher the strain on the server.

One way to get all the data we need is to compile a list of specialties and use it to access the web page.
If we go to the [ratemds](www.ratemds.com/best-doctors/sk/regina) site, we can see that the specialties are listed. Upon exploring it, we not that each page for any specialty displays up to 10 doctors and their ratings.
The data is restricted to medical personnel with at least a review.

### Identifying the URL structure
Our challenge now is to make sure we understand the logic of the URL as the pages we want to scrape change. This will help us to extract the parameters we want. At the moment, we are going to extract the __name, specialty, ratings, votes, gender__. The votes refer to the number of people who gave reviews, and the others are self-explanatory. Each page will have information that looks like the following:
![ ](https://github.com/jnsofini/Web-Scaping/blob/master/figs/ratemds_page.png)

Lets further limit ourselves to doctors in the Regina region. The url in this case is <em>https://www.ratemds.com/best-doctors/sk/regina/ </em>. We used url request
<pre><code>
from requests import get
response = get('https://www.ratemds.com/best-doctors/sk/regina/')
</code></pre>
    
### Understanding the HTML structure of a single page
The first line of response.text indicates that the server sent us an HTML document. The document describes with the overall structure of that web page, along with its specific unique content.
Upon inspection, we can notice that the pages we want to scrape have the same overall structure leading to the same HTML structure. So, one task in the script is for it to understand the HTML structure of only one page. The browser Developer Tools can is used.

Each page has 11 health practitioners, and we can navigate the pages by clicking on each of the page numbers displayed underneath. To parse our HTML document and extract the 11 health practitioners div containers, Python BeautifulSoup module is used.
  -  Import BeautifulSoup class creator from the package bs4.
  -  Parse response.text by creating a BeautifulSoup object.
  
<pre><code>from bs4 import BeautifulSoup
html_soup = BeautifulSoup(response.text, 'html.parser')</code></pre>

Before extracting the 11 div containers, we need to figure out what distinguishes them from other div elements on that page. Often, the distinctive mark resides in the class attribute. Upon inspection of the HTML lines of the containers of interest, it can be noted that the class attribute has two values: `search-item doctor-profile`. This combination is unique to these div containers. By checking the len, we notice that there are 11 items in the containers. Now let’s use the `find_all()` method to extract all the div containers that have a class attribute of `search-item doctor-profile.`

<pre><code>
doctor_container = html_soup.find_all('div', class_ = 'search-item doctor-profile')
print(len(doctor_container))</code></pre>

Expected output: 11

Let's select only the first container, and extract each item of interest, including the __name, specialty, ratings, score, sex__

__a. Name__:
Lets concentrate on the first item. Using the Devtools we note that the name is contained within an anchor tag `<a>` inside the`doctor_container[0]` object. To extract it us the command 
</pre><code>doctor_container[0].a.get_text()</code></pre>

__b. Specialty__:
This data is stored within the `<div>` tag below the `<a>` that contains the name. Dot notation will only access the first div element, so a search by the distinctive mark of the second `<div>` using the `find()` method. Note, `find()` is equivalent to `find_all(limit = 1)`, with limit argument restricting the output to the first match. The distinguishing mark consists of the values __search-item-specialty__ assigned to the class attribute. 
To extract thisus the command
<code>doctor_container[0].find('div', class_ = 'search-item-specialty').a.get_text()</code>

__c. Rating__:
Just like above, it is found in a tag, this time specifically `<span>`. The `find()` method with the distinguishing mark consists of the values __star-rating__ assigned to the class attribute. The ratings is present inside a dict that is access via ,title'. Extract it using
<code>doctor_container[0].find('span', class_ = 'star-rating')['title']</code>

__c. Votes__:
The votes are present in a  `<div>` tage identified by values __star-rating-count__ . Using the `find()` method, the text can be extract it using
<code>doctor_container[0].first_doctor.find('div', class_ = "star-rating-count").get_text()</code>

__c. Gender__:
The gender can be extracted in multiple ways including navigating to the individual doctor's profile and extracting it. Here we extract it from the profile picture. This is achieved via the `find()` method to an  `<src>` tag identified by values __search-item-image__ . The following will return the first letter of the sex
<pre><code>sexurl =  doctor_container[0].first_doctor.find('img', class_="search-item-image")['src']      
gender =  os.path.dirname(sexurl['src'])[44]</code></pre>


### The script for a single page

Before piecing together what we’ve done so far, we have to make sure that we’ll extract the data only from the containers that have a rating.  Now let’s put together the code above, and compress it as much as possible, but only insofar as it’s still easily readable. In the next code block we:

   - Declare some list variables to store the extracted data
   - Loop through each container in doctor_containers (the variable which contains all the 11 doctors containers).
   - Extract the data points of interest only if the container has a rating.
   
<pre><code>
#List to store items
names = []
specialty = []
ratings = []
ratings_count = []
gender = []

#Extract data from individual doctor container
for container in doctor_container:
    # If the doctor has ratings, then extract:
    rating = float(container.find('span', class_ = 'star-rating')['title'])
    if rating != 0:        
        names.append(container.a.get_text())   #add the name
        #specialty
        special = container.find('div', class_ = 'search-item-specialty').a.get_text()
        specialty.append(special)
        #rating
        ratings.append(rating)
        #Number of ratings
        num_ratings = container.find('div', class_ = "star-rating-count").get_text()
        ratings_count.append(int(num_ratings.split()[0]))
        #gender
        sexurl =  container.find('img', class_="search-item-image")['src']       
        gender.append(os.path.dirname(sexurl)[44])
</code></pre>

Create a data frame and inspect the content as follows
import pandas as pd
<code><pre>page_1df = pd.DataFrame({'Name': names,
                        'Specialty': specialty,
                        'Ratings': ratings,
                        'Rates': ratings_count
                        'Gender': gender
                        })</code></pre>
`page_1df.head()` should show

![](https://github.com/jnsofini/Web-Scaping/blob/master/figs/df_page1.png)

### The script for multiple pages

Scraping multiple pages is a bit more challenging. We’ll build upon our one-page script by doing three more things:
   - Making all the 'requests' we want from within the loop.
   - Controlling the loop’s rate to avoid bombarding the server with requests.
   - Monitoring the loop while it runs.
We’ll scrape the first 11 doctors of each page throughout the 128 pages that have ratings. 
Careful observation shows that we can go through the pages by varying the last parameter `www.ratemds.com/best-doctors/sk/regina/?page=`__i__. __i__ can vary from '1' to '128'.

It is essential to control the crawl-rate. A benefit for us and the website we are scraping as it avoids overwhelming the server with tens of requests per second. In that regards, one won't get into the bad books and get their IP addresses banned. It also avoids disrupting the activity of the website we scrape by allowing the server to respond to other users’ requests too. 

The loop’s rate is controlled using the sleep() function from Python’s time module. sleep() will pause the execution of the loop for a specified amount of seconds.

It is also essential to mimic human behaviour, by varying the amount of waiting time between requests by using the randint() function from Python’s random module. randint() randomly generates integers within a specified interval.
For the script, make use of this feature, and monitor the following parameters:
  -  The frequency (speed) of requests, so we make sure our program is not overloading the server.
  -  The number of requests, so we can halt the loop in case the number of expected` requests` is exceeded.
  -  The status code of our requests, so we make sure the server is sending back the proper responses.
Use the following code segment:
from time import sleep, time
from random import randint

<pre><code>
from IPython.core.display import clear_output #for IPython notebook
from time import sleep, time
from random import randint
start_time = time()
requests = 0
for requests in range(1, 6):
# A request would go here
    sleep(randint(1,3))
    elapsed_time = time() - start_time
    print('Request: {}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
    clear_output(wait = True) </code></pre>
    
### Piecing everything together 
We pierced them together to get the script located in the code box. as well as the notebook added for quick checks.

Now let’s piece together everything we’ve done so far! In the following code cell, we start by:
  -  Redeclaring the lists variables so they become empty again.
  -  Preparing the monitoring of the loop.

Then, we’ll:
 -   Loop through the pages list to vary the page number of the URL.
 -   For each element in page, loop through the pages list to vary the page parameter of the URL.
 -   Make the GET requests within the pages loop 
 -   Pause the loop for a time interval between 8 and 15 seconds.
 -   Monitor each `request` as discussed before.
 -   Throw a warning for non-200 status codes.
 -   Break the loop if the number of requests is greater than expected.
 -   Convert the response‘s HTML content to a BeautifulSoup object.
 -   Extract all doctor's containers from this BeautifulSoup object.
 -   Loop through all these containers.
 -   Extract the data if a container has a Metascore.
