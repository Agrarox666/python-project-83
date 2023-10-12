from datetime import datetime
import requests
from bs4 import BeautifulSoup


def make_request(input_url):
    return requests.get(input_url)


def check_page(input_url):
    result = {'status_code': '',
              'h1': '',
              'title': '',
              'description': '',
              'created_at': '',
              }
    response = requests.get(input_url)
    response.raise_for_status()
    result['status_code'] = response.status_code
    result['created_at'] = datetime.now().date()
    html_doc = response.content
    soup = BeautifulSoup(html_doc, 'html.parser')
    if soup.h1:
        result['h1'] = soup.h1.string
    if soup.title:
        result['title'] = soup.title.string
    meta = soup.find('meta', attrs={'name': 'description'})
    if meta is not None:
        result['description'] = meta['content']
    return result
