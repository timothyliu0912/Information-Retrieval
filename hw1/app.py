from flask import Flask, request
from flask import render_template
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch(['localhost:9200'])

app = Flask(__name__)

@app.route("/",methods=["GET", "POST"])

def index():
    q = request.args.get("q")
    print(q)
    if q is not None:
        data = {
            "query":{
                "match":{ 
                    "content":q 
                    },
                },
                "size":50
            }
        resp = es.search(index="article", doc_type = "art",body=data)
        return render_template('search.html',q=q,response=resp["hits"]["hits"])
    return render_template('search.html')


if __name__ == '__main__':
    app.debug = True
    app.run(port=8000)

