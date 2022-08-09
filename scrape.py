from pathlib import Path
import unicodedata
import re
import requests
import csv
import pandas as pd
from bs4 import BeautifulSoup


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode(
            'ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def grab_data(url, params):
    r = requests.post(url, data=params)
    soup = BeautifulSoup(r.text, 'html.parser')

    return soup

def save_data(soup, fname):
    df = pd.read_html(str(soup), header=0, flavor='bs4', skiprows=[1])
    df[0] = df[0].dropna(how='all')
    df[0].to_csv('industries/'+fname+'.csv', index=False)         


# url = 'https://statistics.labor.ny.gov/cesemp.asp'
# LI = '23035004'
# old URL phased out

url = 'https://statistics.labor.ny.gov/ins.asp'
LI = '01000036'

Path("industries").mkdir(parents=True, exist_ok=True)

industries = {}

while not industries:
    soup = grab_data(url, {
        'term': '1',
        'geog': LI,
        'submit': 'Go to Step 2'
    })

    options = soup.find_all('option')
    for option in options[1:]:
        industries[option.text] = option['value']

while len(industries) != 0:
    print('industries not blank, meaning we need to scrape')
    for key in list(industries):
        fname = slugify(key)

        soup = grab_data(url, {
            'term': '2',
            'geog': LI,
            'sect': industries[key],
            'submit': 'Go to Step 3'
        })
        
        sub_industries = {}
        options_sub = soup.find_all('option')
        
        for option in options_sub[1:]:
            sub_industries[option.text] = option['value']

        page_data = grab_data(url, {
            'term': '3',
            'geog': LI,
            'sect': industries[key],
            'periods': '999999',
            'ind': industries[key],
            'submit': 'Go to Step 4'
        })

        save_data(page_data, fname)

        if len(sub_industries) != 0:
            for sub in list(sub_industries):
                print(sub)
                fname = slugify(sub)
                page_data = grab_data(url, {
                    'term': '3',
                    'geog': LI,
                    'sect': industries[key],
                    'periods': '999999',
                    'ind': industries[key],
                    'submit': 'Go to Step 4'
                })

                save_data(page_data, fname)                                
        
        del industries[key]