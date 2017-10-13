from urllib2 import urlopen
from time import sleep
from bs4 import BeautifulSoup
import os


class Parser(object):
    def __init__(self, movies):
        self.movies = movies
        self.cwd = os.getcwd() + "/movies/"

    def parse(self):
        for movie in self.movies:
            title_id = movie.split("/")[4]
            file_path = self.cwd + title_id

            if os.path.isfile(file_path):
                file = open(file_path, "r")
            else:
                file = open(file_path, "w")
                response = urlopen(movie)

                file.write(response.read())