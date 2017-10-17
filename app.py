from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
import os
from json import dumps

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['STATIC_FOLDER'] = os.path.join(basedir, 'bower_components')

@app.route("/")
def main():
    return render_template('main.html', orderBy="ratingValue")

@app.route("/search", methods=['GET', 'POST'])
def search():
    q = request.form.get("term", "")
    orderBy = request.form.get("orderBy", "neni")
    es = Elasticsearch()

    res = es.search(index="imdb", doc_type="movie",
        body={
            "sort" : [
                { 
                    orderBy : {
                        "order" : "desc"
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
                        "field" : "",
                        "size" : 5
                    }
                }
            }
        }
    )

    # print dumps(res, indent=4)

    return render_template('hits.html', data=res["hits"]["hits"], value=q, orderBy=orderBy)