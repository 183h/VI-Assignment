from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
from json import dumps

app = Flask(__name__)


@app.route("/")
def main():
    return render_template('main.html', o="asc", rf=0, rt=10)


@app.route("/search", methods=['GET', 'POST'])
def search():
    q = request.form.get('q', default="", type=str)
    o = request.form.get('o', default="desc", type=str)
    a = request.form.get('a', default=None, type=str)
    r = request.form.get('r', default="", type=str)
    b = request.form.get('b', default=None, type=str)

    es = Elasticsearch()
    aggs_filter = []
    sug = {}
    unique_sug = set()
    year_histogram = {}

    if a is not None:
        aggs_filter.append({
            "term": {
                'genres.keyword': a
            }
        })
    if b is not None:
        aggs_filter.append({
            "term": {
                'stars.keyword': b
            }
        })

    rf, rt = r.split(" - ")

    res = es.search(index="imdb", doc_type="movie",
                    body={
                        "sort": [
                            {
                                "ratingValue": {
                                    "order": o
                                }
                            },
                            "_score"
                        ],
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "multi_match": {
                                            "query": q,
                                            "type": "most_fields",
                                            "fields": ["name", "description", "plot", "actors", "stars", "awards", "creators", "keywords", "director", "genres"]
                                        }}, {
                                        "range": {
                                            "ratingValue": {
                                                "gte": int(rf),
                                                "lte": int(rt)
                                            }
                                        }}
                                ],
                                "filter": aggs_filter
                            }
                        },
                        "highlight": {
                            "pre_tags": ['<span style="background-color: yellow">'],
                            "post_tags": ["</span>"],
                            "fields": {
                                '*': {}
                            }
                        },
                        "aggs": {
                            "by_genre": {
                                "terms": {
                                    "field": "genres.keyword",
                                    "size": 10
                                }
                            },
                            "by_releaseYears": {
                                "date_histogram": {
                                    "field": "releaseDate",
                                    "interval": "year"
                                }
                            },
                            "by_stars": {
                                "terms": {
                                    "field": "stars.keyword",
                                    "size": 10
                                }
                            }
                        }
                    }
                    )

    if res["hits"]["total"] == 0:
        res_sug = es.search(index="imdb", doc_type="movie",
                            body={
                                "suggest": {
                                    "text": q,
                                    "name_sugg": {
                                        "phrase": {
                                            "field": "name.suggest",
                                            "size": 10,
                                            "gram_size": 3,
                                            "direct_generator": [{
                                                "field": "name.suggest",
                                                "suggest_mode": "always"
                                            }],
                                            "highlight": {
                                                "pre_tag": '<span style="background-color: yellow">',
                                                "post_tag": "</span>"
                                            }
                                        }
                                    },
                                    "description_sugg": {
                                        "phrase": {
                                            "field": "description.suggest",
                                            "size": 10,
                                            "gram_size": 3,
                                            "direct_generator": [{
                                                "field": "description.suggest",
                                                "suggest_mode": "always"
                                            }],
                                            "highlight": {
                                                "pre_tag": '<span style="background-color: yellow">',
                                                "post_tag": "</span>"
                                            }
                                        }
                                    },
                                    "plot_sugg": {
                                        "phrase": {
                                            "field": "plot.suggest",
                                            "size": 10,
                                            "gram_size": 3,
                                            "direct_generator": [{
                                                "field": "plot.suggest",
                                                "suggest_mode": "always"
                                            }],
                                            "highlight": {
                                                "pre_tag": '<span style="background-color: yellow">',
                                                "post_tag": "</span>"
                                            }
                                        }
                                    }
                                }
                            }
                            )

        sug = res_sug["suggest"]["name_sugg"][0]["options"] + res_sug["suggest"]["description_sugg"][0]["options"] + res_sug["suggest"]["plot_sugg"][0]["options"]
        for s in sug:
            unique_sug.add(s["highlighted"])

    # prepare year histogram
    for y in res["aggregations"]["by_releaseYears"]["buckets"]:
        if y["doc_count"] != 0:
            year = y["key_as_string"].split("-")
            year_histogram[year[0]] = y["doc_count"]

    return render_template(
        'hits.html',
        data=res["hits"]["hits"],
        q=q,
        o=o,
        aggs=res["aggregations"]["by_genre"]["buckets"],
        sug=unique_sug,
        rf=rf, rt=rt,
        a=a,
        total=res["hits"]["total"],
        yh=year_histogram,
        aggs_stars=res["aggregations"]["by_stars"]["buckets"],
        b=b
    )