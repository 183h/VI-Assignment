from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
from json import dumps

app = Flask(__name__)


@app.route("/")
def main():
    return render_template('main.html', o="asc")


@app.route("/search", methods=['GET', 'POST'])
def search():
    q = request.form.get('q', default="", type=str)
    o = request.form.get('o', default="desc", type=str)
    a = request.form.get('a', default=None, type=str)
    es = Elasticsearch()
    aggs_filter = {}
    sug = {}

    if a is not None:
        aggs_filter = {
            "term": {
                'country': a
            }
        }
        print aggs_filter

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
                                "must": {
                                    "multi_match": {
                                        "query": q,
                                        "type": "most_fields",
                                        "fields": ["name", "description", "plot", "actors", "stars"]
                                    }
                                },
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
                            "by_language": {
                                "terms": {
                                    "field": "country",
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
                                    "simple_phrase": {
                                        "phrase": {
                                            "field": "plot.trigram",
                                            "size": 10,
                                            "gram_size": 3,
                                            "direct_generator": [{
                                                "field": "plot.trigram",
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

        sug = res_sug["suggest"]["simple_phrase"][0]["options"]

    # print dumps(res, indent=4)
    # print q, o, a

    return render_template(
        'hits.html',
        data=res["hits"]["hits"], q=q, o=o,
        aggs=res["aggregations"]["by_language"]["buckets"],
        sug=sug
    )