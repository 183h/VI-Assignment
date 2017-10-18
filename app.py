from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
import os
from json import dumps

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('main.html', o="desc")

@app.route("/search", methods=['GET', 'POST'])
def search():
    q = request.form.get('q', default = "", type = str)
    o = request.form.get('o', default = "desc", type = str)
    es = Elasticsearch()

    res = es.search(index="imdb", doc_type="movie",
        body={
            "sort" : [
                { 
                    "ratingValue" : {
                        "order" : o
                    }
                },
                "_score"
            ],
            "query" : {
                "bool" : {
                    "must" : {
                        "multi_match" : {
                            "query" : q,
                            "type" : "most_fields",
                            "fields" : ["name", "description", "plot", "actors", "stars"]
                        }
                    }
                }
            },
            "highlight" : {
                "pre_tags" : ['<span style="background-color: yellow">'],
                "post_tags" : ["</span>"],
                "fields" : {
                    '*' : {}
                }
            },
            "aggs" : {
                "by_language" : {
                    "terms" : {
                        "field" : "country",
                        "size" : 5
                    }
                }
            }
        }
    )

    print dumps(res, indent=4)
    print q, o

    return render_template(
        'hits.html',
         data=res["hits"]["hits"]
         , q=q, o=o,
          aggs=res["aggregations"]["by_language"]["buckets"]
    )