# coding: utf-8

# # Mission to Mars

# ## Step 1 - Scraping

# Dependencies
import pandas as pd
import requests

import time
from splinter import Browser
from bs4 import BeautifulSoup
from selenium import webdriver

import tweepy
import TweepyCredentials # twitter keys and tokens
import pymongo

# Setting up splinter
def init_browser():
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

# Define a function 
def scrape():
    browser = init_browser()
    # create mars dict that we can insert into mongo
    mars = {}

    #############################################
    
    # ### NASA Mars News 

    # URL of NASA Mars News to be scraped for latest news and paragraph title
    url_NASA_Mars_News = 'https://mars.nasa.gov/news/'
    browser.visit(url_NASA_Mars_News)
    time.sleep(1)

    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')


    # Latest News Title from NASA Mars News Site
    print("Test 1")
    news_title = news_soup.find_all('div', class_='content_title')
    print(news_title[0].text)
    print("Test 2")

    # Latest News Paragraph Text from NASA Mars News Site
    news_p = news_soup.find_all('div', class_='article_teaser_body')
    print(news_p[0].text)
    print("Test 3")

    # # Adding latest news and paragraph title to the dictionary
    mars['news_title'] = news_title[0].text
    mars['news_p'] = news_p[0].text
    print("Test 4")



    ############################################

    # ### JPL Mars Space Images - Featured Image

    # URL of JPL Mars Space Image to be scraped for featured image
    url_JPL_images = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url_JPL_images)
    print("Test 5")

    # Browse through the pages
    time.sleep(1)

    # Click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()
    time.sleep(2)
    print("Test 6")


    # Click the more info button
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()
    time.sleep(2)
    print("Test 7")


    # Using BeautifulSoup create an object and parse with 'html.parser'
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')
    print("Test 8")


    # find the relative image url
    img_url_rel = img_soup.find('figure', class_='lede').find('img')['src']
    img_url_rel

    # Use the base url to create an absolute url
    baseUrl = 'https://www.jpl.nasa.gov'
    featured_image_url = baseUrl + img_url_rel
    featured_image_url
    print("Test 9")

    # Adding featured image url to the dictionary
    mars['featured_image_url'] = featured_image_url
    print("Test 10")

    #############################################

    # ### Mars Weather

    # Twitter API Keys
    consumer_key = TweepyCredentials.consumer_key
    consumer_secret = TweepyCredentials.consumer_secret
    access_token = TweepyCredentials.access_token
    access_token_secret = TweepyCredentials.access_token_secret


    # Setup Tweepy API Authentication
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())


    # Target User
    target_user = "@MarsWxReport"


    # Retrive latest tweet
    tweet = api.user_timeline(target_user)
    mars_weather = tweet[0]['text']
    mars_weather

    # Adding mars weather from the latest rweet  to the dictionary
    mars['mars_weather'] = mars_weather

    #############################################

    # ### Mars Facts

    # URL of Mars facts to scrape the table containing facts about the planet
    url_Mars_Facts = 'https://space-facts.com/mars/'
    
    df = pd.read_html(url_Mars_Facts)[0]
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)

    table = df.to_html()
    table = table.replace('\n', '')

    mars['facts'] = table
    
    print("Test 11")

    ############################################

    # ### Mars Hemisphere
    
    # Scapping of  USGS Astrogeology site to obtain high resolution images for each of Mars hemispheres.
    hemispheresurl = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    hemisphereBaseUrl = 'https://astrogeology.usgs.gov'
    browser.visit(hemispheresurl)
    soup = BeautifulSoup(browser.html,'html5lib')
    hemispheres = soup.find('div', class_='collapsible results').find_all('a')
    
    # Create an empty list to hold dictionaries of hemisphere title with the image url string
    hemisphere_image_urls = []
    hemispheredict = {}

    # Loop through those links, click the link, find the sample anchor, return the href
    for hemisphere in hemispheres:
        hemisphereLink = hemisphere.get('href')

        browser.visit(hemisphereBaseUrl + hemisphereLink)
        soup = BeautifulSoup(browser.html, 'html.parser')

        # Get Hemisphere title
        title = soup.find('title').text
        hemisphereTitle = title.split('|')
        hemisphereTitle = hemisphereTitle[0].replace(' Enhanced ','')
        imgUrl = soup.find('img',class_='wide-image').get('src')
        imgUrl = hemisphereBaseUrl + imgUrl
        hemispheredict = {"title": hemisphereTitle, "img_url":imgUrl}

        # Append hemisphere object to list
        hemisphere_image_urls.append(hemispheredict)

    # Set hemispheres
    mars["hemispheres"] = hemisphere_image_urls

    browser.quit()

    print("hi!!")
    return mars