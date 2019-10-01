import time
import validators
import json
import requests
from selenium import webdriver
from bs4 import BeautifulSoup

GET_STRAINS_URLS = False
GET_DESCRIPTIONS = False
GET_IMAGES = False

if GET_STRAINS_URLS:
    """ Leafly has a new website so crawler is broken ATM but we had already scraped all strains.
        Strains "url" are still current so no need to re-scrape.
        New scraper would involve looking at the 3 following pages with "load more" buttons:
          This is because the no longer have a single page displaying all strains...
          "https://www.leafly.com/strains/lists/category/indica"
          "https://www.leafly.com/strains/lists/category/hybrid"
          "https://www.leafly.com/strains/lists/category/sativa"
        for now we will play with "strainsDB.json" as the strain URLs are still consistent"""

    """Creates the driver and clicks yes on the "are you over 21" pop up"""
    driver = webdriver.Chrome('./env/bin/chromedriver')
    driver.get('https://www.leafly.com/explore/sort-alpha')
    yes_button = driver.find_element_by_xpath('//button[text()="yes"]')
    yes_button.click()

    sel_strains = []
    strainsDB = []
    count = 0

    """Clicks load more button 75 times to ensure all strains are loaded before scraping"""
    while count <= 75:
        load_button = driver.find_element_by_xpath(
            '//button[text()="Load More"]')
        load_button.click()
        time.sleep(.5)
        count += 1

    """Scrapes strains into selenium objects to be further scraped for URL's"""
    sel_strains = driver.find_elements_by_class_name(
        'ga_Explore_Strain_Tile') + driver.find_elements_by_class_name('ng-scope')

    """Extracts urls from selenium objects and creates the json object strainsDB"""
    for sel_strain in sel_strains:
        strain_url = str(sel_strain.get_attribute('href'))
        if validators.url(strain_url):
            split_strain = strain_url.split('/')
            strainsDB.append({
                'name': split_strain[-1],
                'type': split_strain[3],
                'url': strain_url
            })

    """Saves strainsDB.json and closes the driver"""
    with open('./strainsDB.json', 'w') as f:
        json.dump(strainsDB, f, indent=4)
    driver.quit()

if GET_DESCRIPTIONS:
    """Finds descriptions on each of the individual strains"""

    strainsDB = json.load(open('./strainsDB.json', 'r'))
    for strain in strainsDB:
        r = requests.get(strain['url'])
        if r:
            soup = BeautifulSoup(r.text)
            description = soup.find('div', {'itemprop': 'description'})
            strain["description"] = description.get_text()

    """Updates strainsDB.json with new strain descriptions"""
    with open('./strainsDB.json', 'w') as f:
        json.dump(strainsDB, f, indent=4)

if GET_IMAGES:
    """Gathers images for each strain"""
    strainsDB = json.load(open('./strainsDB.json', 'r'))

    for strain in strainsDB:
        r = requests.get(strain['url'])
        if r:
            soup = BeautifulSoup(r.text)
            images = soup.findAll('img', {'class': 'image-card__image'})
            strain['images'] = []
            for picture in images:
                strain['images'].append(picture['src'])

    with open('./strainsDB.json', 'w') as f:
        json.dump(strainsDB, f, indent=4)
