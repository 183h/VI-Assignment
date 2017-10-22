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

    es = Elasticsearch()
    aggs_filter = {}
    sug = {}
    unique_sug = set()

    if a is not None:
        aggs_filter = {
            "term": {
                'country': a
            }
        }

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

    # print dumps(res, indent=4)
    print q, o, a, r

    return render_template(
        'hits.html',
        data=res["hits"]["hits"],
        q=q,
        o=o,
        aggs=res["aggregations"]["by_language"]["buckets"],
        sug=unique_sug,
        rf=rf, rt=rt,
        a=a,
        total=res["hits"]["total"]
    )