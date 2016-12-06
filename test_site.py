from bs4 import BeautifulSoup
import requests
import sys
import logging
from urlparse import urljoin

# page_urls = []
# test_urls = ['http://lovestarrace.club/123.html']
# bad_urls = []
start_url = 'http://lovestarrace.club/'


def check_url_status(url):
    resp = requests.head(url)
    if resp.status_code == requests.codes.okay:
        pass
    else:
        return url


def get_bs(page_url):
    r = requests.get(page_url)
    soup = BeautifulSoup(r.text, 'html5lib')
    return soup


def get_page_urls(soup):
    n = soup.find('a', attrs={'class': 'next'})
    if n:
        return n['href']


def get_test_urls(soup):
    t = []
    n = soup.findAll('img')
    for i in n:
        if i['src'].startswith('..'):
            img = i['src'][2:]
            img = urljoin(start_url, img)
            t.append(img)
        else:
            t.append(i)
    return t


if __name__ == '__main__':
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)-26s %(funcName)-20s %(levelname)-8s %(message)s')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    logger.setLevel(logging.DEBUG)


# page_urls.append(start_url)
# s = get_bs(start_url)
# u = get_page_urls(s)
# get_test_urls(s)
# # while u:
# #     u = start_url + u
# #     page_urls.append(u)
# #     s = get_bs(u)
# #     u = get_page_urls(s)
# #     get_test_urls(s)
# for i in test_urls:
#     check_url_status(i)
