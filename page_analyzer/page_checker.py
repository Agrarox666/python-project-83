from datetime import datetime
import requests
from bs4 import BeautifulSoup
from requests import HTTPError


def check_page(input_url):
    result = {'status_code': '',
              'h1': '',
              'title': '',
              'description': '',
              'created_at': '',
              }
    try:
        response = requests.get(input_url)
        result['status_code'] = response.status_code
        result['created_at'] = datetime.now().date()
        html_doc = response.content
        soup = BeautifulSoup(html_doc, 'html.parser')
        if soup.h1:
            result['h1'] = soup.h1.string
        if soup.title:
            result['title'] = soup.title.string
        meta = soup.find('meta', attrs={'name': 'description'})
        result['description'] = meta['content']
        return result
    except HTTPError as error:
        result['status_code'] = error.response.status_code
        return result
