from urllib2 import urlopen
from urlparse import urljoin
from time import sleep
from bs4 import BeautifulSoup
from re import compile


class Crawler(object):
    def __init__(self, start_url):
        self.visited_urls = set()
        self.unvisited_urls = []
        self.base_url = 'http://www.imdb.com/'
        self.base_url_regexp = compile(self.base_url + '*')

        self.unvisited_urls.append(start_url)

    def crawl(self):
        for url in self.unvisited_urls:
            self.visited_urls.add(url)
            response = urlopen(url)

            soup = BeautifulSoup(response.read(), 'lxml')
            links_soup = soup('a')
            new_urls = set()

            for link in links_soup:
                if 'href' in link.attrs:
                    pass
                    # print urljoin(self.base_url, link['href'])
                    # link_joined = urljoin(link, )
                    # if self.base_url.match()

            sleep(3)


if __name__ == '__main__':
    c = Crawler('http://www.imdb.com/genre/')
    c.crawl()