from urllib2 import urlopen
from bs4 import BeautifulSoup
import os
from json import dumps
from re import compile, sub
from datetime import datetime
from elasticsearch import helpers


class Parser(object):
    def __init__(self, movies, es):
        self.movies = movies
        self.cwd = os.getcwd() + "/movies/"
        self.date = compile('[0-9]{1,2} (January|February|March|April|June|July|August|September|October|November|December) [0-9]{4}')
        self.es = es

    def findItem(self, soup, tag, attr, find_all=False, ret_type="text"):
        if not find_all:
            value = soup.find(tag, attr)
        else:
            value = soup.find_all(tag, attr)

        if value is not None:
            if ret_type == "text":
                return sub('[\s]{2,}', ' ', sub('[\n]', '', value.text.strip()))
            elif ret_type == "string":
                return sub('[\s]{2,}', ' ', sub('[\n]', '', value.string.strip()))
            elif ret_type == "element":
                return value
        else:
            return None

    def parse(self):
        actions = []
        id_ = 0
        for movie in self.movies:
            json_movie = {}
            title_id = movie.split("/")[4]
            file_path = self.cwd + title_id

            print "Id: {} | TitleId: {}".format(id_, title_id)

            if os.path.isfile(file_path):
                file = open(file_path, "r")
            else:
                file = open(file_path, "w+")
                try:
                    response = urlopen(movie)
                except:
                    continue
                file.write(response.read())
                file.seek(0, 0)

            soup = BeautifulSoup(file.read(), 'lxml', from_encoding="utf-8")
            json_movie["id"] = title_id

            json_movie["ratingValue"] = None
            ratingValue = self.findItem(
                soup,
                "span",
                {"itemprop": "ratingValue"}
            )
            if ratingValue is not None:
                json_movie["ratingValue"] = float(ratingValue)

            json_movie["ratingCount"] = None
            ratingCount = self.findItem(
                soup,
                "span",
                {"itemprop": "ratingCount"}
            )
            if ratingCount is not None:
                json_movie["ratingCount"] = int(sub(',', '', ratingCount))

            json_movie["name"] = self.findItem(
                soup,
                "h1",
                {"itemprop": "name"}
            )

            json_movie["titleYear"] = self.findItem(
                soup,
                "span",
                {"id": "titleYear"}
            )

            content_rating = self.findItem(
                soup,
                "meta",
                {"itemprop": "contentRating"},
                ret_type="element"
            )
            if content_rating is not None:
                json_movie["contentRating"] = content_rating["content"]

            json_movie["duration"] = self.findItem(
                soup,
                "time",
                {"itemprop": "duration"}
            )

            json_movie["genres"] = ""
            genres = self.findItem(
                soup,
                "span",
                {"itemprop": "genre"},
                find_all=True,
                ret_type="element"
            )
            if genres is not None:
                json_movie["genres"] = ", ".join([genre.text.strip() for genre in genres])

            json_movie["description"] = self.findItem(
                soup,
                "div",
                {"itemprop": "description"}
            )

            director = self.findItem(
                soup,
                "span",
                {"itemprop": "director"}
            )
            if director is not None:
                json_movie["director"] = director

            plot_summary = self.findItem(
                soup,
                "div",
                {"class": "plot_summary"},
                find_all=True,
                ret_type="element"
            )

            json_movie["creators"] = ""
            if plot_summary:
                creators = plot_summary[0].find_all('span', {"itemprop": "creator"})
                json_movie["creators"] = " ".join(
                    [creator.text.strip() for creator in creators]
                )

            json_movie["stars"] = ""
            stars = self.findItem(
                soup,
                "span",
                {"itemprop": "actors"},
                find_all=True,
                ret_type="element"
            )
            if stars is not None:
                json_movie["stars"] = " ".join([star.text.strip() for star in stars])

            awards = self.findItem(
                soup,
                "span",
                {"itemprop": "awards"}
            )
            if awards is not None:
                json_movie["awards"] = awards

            json_movie["actors"] = ""
            actors = self.findItem(
                soup,
                "td",
                {"itemprop": "actor"},
                find_all=True,
                ret_type="element"
            )
            if actors is not None:
                json_movie["actors"] = ", ".join([actor.text.strip() for actor in actors])

            title_story_line = self.findItem(
                soup,
                "div",
                {"id": "titleStoryLine"},
                ret_type="element"
            )

            if title_story_line is not None:
                plot = self.findItem(
                    title_story_line,
                    "div",
                    {"itemprop": "description"},
                )
                json_movie["plot"] = plot

                json_movie["keywords"] = ""
                keywords = self.findItem(
                    title_story_line,
                    "span",
                    {"itemprop": "keywords"},
                    find_all=True,
                    ret_type="element"
                )
                if keywords is not None:
                    json_movie["keywords"] = ", ".join([keyword.text.strip() for keyword in keywords])

            title_details = self.findItem(
                soup,
                "div",
                {"id": "titleDetails"},
                ret_type="element"
            )

            if title_details is not None:
                title_details_divs = self.findItem(
                    title_details,
                    "div",
                    {"class": "txt-block"},
                    find_all=True,
                    ret_type="element"
                )

            json_movie["country"] = ""
            country_block = [i for i in title_details_divs if i.find('h4', text=compile('Country:.*'))]
            if country_block:
                country = self.findItem(
                    country_block[0],
                    "a",
                    {"itemprop": "url"},
                )
                json_movie["country"] = country

            json_movie["language"] = ""
            language_block = [i for i in title_details_divs if i.find('h4', text=compile('Language:.*'))]
            if language_block:
                language = self.findItem(
                    language_block[0],
                    "a",
                    {"itemprop": "url"},
                )
                json_movie["language"] = language

            json_movie["releaseDate"] = None
            release_date_block = [i for i in title_details_divs if i.find('h4', text=compile('Release Date:.*'))]
            if release_date_block:
                release_date = self.date.search(release_date_block[0].text)
                if release_date:
                    releaseDate = str(datetime.strptime(release_date.group(), "%d %B %Y")).split(" ")
                    json_movie["releaseDate"] = releaseDate[0]

            # print dumps(json_movie, indent=4, ensure_ascii=False, encoding="utf-8")
            # self.es.index(index="imdb", doc_type="movie", id=id_, body=dumps(json_movie, ensure_ascii=False, encoding="utf-8"))

            actions.append(
                {
                    '_index': 'imdb',
                    '_type': 'movie',
                    '_id': id_,
                    '_source': dumps(json_movie, ensure_ascii=False, encoding="utf-8")
                }
            )

            id_ = id_ + 1

        helpers.bulk(self.es, actions, chunk_size=1000, request_timeout=200)