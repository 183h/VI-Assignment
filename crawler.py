class Crawler(object):
    def __init__(self, start_url):
        visited_urls = set()
        unvisited_urls = {}
        self._start_url = start_url


if __name__ == '__main__':
    c = Crawler('http://www.imdb.com/genre/')