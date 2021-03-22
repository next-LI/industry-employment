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


url = 'https://statistics.labor.ny.gov/cesemp.asp'
LI = '23035004'
overall_level = '1'
check_industry = '2'
industry_level = '3'
failed = []

Path("industries").mkdir(parents=True, exist_ok=True)

industries = {}

while not industries:
    r = requests.post(url, data={
        'PASS': '2',
        'codename': '23035004',
        'submit': 'Submit'
    })

    print(url)
    print(r)
    print(r.text)

    soup = BeautifulSoup(r.text, 'html.parser')
    print('industries blank, trying to fetch them')
    options = soup.find_all('option')
    for option in options[1:]:
        industries[option.text] = option['value']

print(industries)

while len(industries) != 0:
    print('industries not blank, meaning we need to scrape')
    for key in list(industries):
        fname = slugify(key)

        page_data = requests.post(url, data={
            'PASS': industry_level,
            'codename': LI,
            'seriescode': industries[key]
        })
        try:
            df = pd.read_html(page_data.text, header=0,
                              flavor='bs4', skiprows=[1])
            print(df[0])
            df[0].to_csv('industries/'+fname+'.csv', index=False)
            print('removing completed industry')
            del industries[key]
        except:
            pass
