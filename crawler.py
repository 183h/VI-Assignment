class Crawler(object):
    def __init__(self, start_url):
        self.visited_urls = set()
        self.unvisited_urls = []

        self.unvisited_urls.append(start_url)

    def crawl(self):
        pass


if __name__ == '__main__':
    c = Crawler('http://www.imdb.com/genre/')
    c.crawl()