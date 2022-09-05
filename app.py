from datetime import datetime
from flask import Flask, jsonify, request, render_template
# from flask_cors import CORS
from nltk import ngrams
from config import DB_NAME, DB, DICT_COLLECTION, REVIEW_COLLECTION, ARTICLE_COLLECTION
import pandas as pd
import random
app = Flask(__name__)


@app.route('/')
def index():
    print('Request for index page received')
    return render_template('index.html')


@app.route('/hello', methods=['POST'])
def hello():
    name = request.form.get('name')

    if name:
        print('Request for hello page received with name=%s' % name)
        return render_template('hello.html', name=name)
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))


@app.route('/getCloud', methods=['GET'])
def getCloud():
    type = request.args.get('type')
    name = request.args.get('name')
    dataProduct = request.args.get('dataProduct')
    dataSource = request.args.get('dataSource')
    dateStart = request.args.get('dateStart')
    dateEnd = request.args.get('dateEnd')
    dateStartList = dateStart.split('/')
    dateEndList = dateEnd.split('/')
    dataContent = request.args.get('content')
    if type == "App":
        source = dataSource.split(',')
        source_list = []
        for i in source:
            source_list.append({"source": i})
        article_pipeline = [
            {
                "$match": {
                    "artCat": name,
                    "$or": source_list,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "sentence": True,
                    "word": True,
                    "date": {
                        "$dateFromString": {
                            "dateString": '$artDate'
                        }
                    }
                },
            },
            {
                "$match": {
                    "date": {
                        "$gte": datetime(int(dateStartList[0]), int(dateStartList[1]), int(dateStartList[2])),
                        "$lt":datetime(int(dateEndList[0]), int(dateEndList[1]), int(dateEndList[2]))
                    }
                }
            },
            {
                "$unwind": "$word"
            },
            {
                "$group": {
                    "_id": {'$toUpper': "$word"},
                    "wordCount": {
                        "$sum": 1
                    }
                }
            },
            {
                "$match": {
                    "wordCount": {
                        "$gt": 2
                    }
                }
            }
        ]
    else:
        article_pipeline = [
            {
                "$match": {
                    "artCat": dataProduct,
                    "source": dataSource
                }
            },
            {
                "$project": {
                    "artTitle": True,
                    "word": True,
                    "date": {
                        "$dateFromString": {
                            "dateString": '$artDate'
                        }
                    }
                },
            },
            {
                "$match": {
                    "artTitle": {"$regex": name},
                    "date": {
                        "$gte": datetime(int(dateStartList[0]), int(dateStartList[1]), int(dateStartList[2])),
                        "$lt":datetime(int(dateEndList[0]), int(dateEndList[1]), int(dateEndList[2]))
                    }
                }
            },
            {
                "$unwind": "$word"
            },
            {
                "$group": {
                    "_id": {'$toUpper': "$word"},
                    "wordCount": {
                        "$sum": 1
                    }
                }
            },
            {
                "$match": {
                    "wordCount": {
                        "$gt": 2
                    }
                }
            }

        ]
    review_pipeline = [
        {
            "$match": {
                "artCat": dataProduct,
                "source": dataSource
            }
        },
        {
            "$project": {
                "_id": 0,
                "artTitle": True,
                "artUrl": True,
                # "word":True,
                "date": {
                    "$dateFromString": {
                        "dateString": '$artDate'
                    }
                }
            },
        },
        {

            "$match": {
                "artTitle": {"$regex": name},
                "date": {
                    "$gte": datetime(int(dateStartList[0]), int(dateStartList[1]), int(dateStartList[2])),
                    "$lt":datetime(int(dateEndList[0]), int(dateEndList[1]), int(dateEndList[2]))
                }
            }
        },
        {
            "$lookup": {
                "from": "Review",
                "localField": "artUrl",
                "foreignField": "artUrl",
                "as": "reviews"
            }
        },
        {
            "$project": {
                "reviews._id": 0
            },
        },
        {
            "$unwind": "$reviews"
        },
        {
            "$unwind": "$reviews.word"
        },
        {
            "$group": {
                "_id": {'$toUpper': "$reviews.word"},
                "wordCount": {
                    "$sum": 1
                }
            }
        },
        {
            "$match": {
                "wordCount": {
                    "$gt": 2
                }
            }
        },

    ]

    if(dataContent == 'article-content'):
        result = list(DB[ARTICLE_COLLECTION].aggregate(article_pipeline))
    elif(dataContent == 'review-content'):
        result = list(DB[ARTICLE_COLLECTION].aggregate(review_pipeline))
    else:
        article_result = list(
            DB[ARTICLE_COLLECTION].aggregate(article_pipeline))
        reviews_result = list(
            DB[ARTICLE_COLLECTION].aggregate(review_pipeline))
        all_result = article_result+reviews_result
        wordList = []
        result = []
        for item in all_result:
            if item['_id'] not in wordList:
                wordList.append(item['_id'])
                result.append(item)
            else:
                for i in result:
                    if (i['_id'] == item['_id']):
                        i['wordCount'] += item['wordCount']

    return jsonify(result)


@app.route('/getCount', methods=['GET'])
def getCount():
    type = request.args.get('type')
    bankList = request.args.get('name').split(',')
    bankList_lower = [word.lower() for word in bankList]
    bankList = bankList+bankList_lower
    dataProduct = request.args.get('dataProduct')
    dataSource = request.args.get('dataSource')
    dataContent = request.args.get('content')
    if type == "App":
        source = dataSource.split(',')
        source_list = []
        bank_list = []
        for i in source:
            source_list.append({"source": i})
        for bank in bankList:
            bank_list.append({"artCat": bank})
        article_pipeline = [
            {
                "$match": {
                    "$or": bank_list,
                }
            },
            {
                "$match": {
                    "$or": source_list,
                }
            },

            {
                "$project": {
                    "_id": 0,
                    "artCat": 1,
                    "date": {
                        "$dateFromString": {
                            "dateString": '$artDate',
                            "onError": 'null'
                        }
                    }
                },
            },
            {
                "$group": {
                    "_id": {
                        "Date": {
                            "$dateToString": {
                                "format": "%Y-%m", "date": "$date"
                            }
                        },
                        "Word": "$artCat"
                    },
                    "wordCount": {
                        "$sum": 1
                    }
                }
            },
            {
                "$set": {
                    "date": "$_id.Date",
                    "word": "$_id.Word"
                }
            },
            {
                "$project": {
                    "_id": 0
                }
            }
        ]
    else:

        article_pipeline = [
            {
                "$match": {
                    "artCat": dataProduct,
                    "source": dataSource
                }
            },
            {
                "$project": {
                    "word": True,
                    "date": {
                        "$dateFromString": {
                            "dateString": '$artDate',
                            "onError": 'null'
                        }
                    }
                },
            },
            {
                "$unwind": "$word"
            },
            {
                "$match": {
                    'word': {
                        "$in": bankList
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "Date": {
                            "$dateToString": {
                                "format": "%Y-%m", "date": "$date"
                            }
                        },
                        "Word": "$word"
                    },
                    "wordCount": {
                        "$sum": 1
                    }
                }
            },
            {
                "$set": {
                    "date": "$_id.Date",
                    "word": {'$toUpper': "$_id.Word"}
                }
            },
            {
                "$project": {
                    "_id": 0
                }
            }

        ]
    review_pipeline = [
        {
            "$match": {
                "type": dataProduct,
                "source": dataSource
            }
        },
        {
            "$project": {
                "artUrl": 0,
                "cmtDate": {
                    "$dateFromString": {
                        "dateString": '$cmtDate'
                    }
                },
                "word": 1
            },
        },
        {
            "$unwind": "$word"
        },
        {
            "$match": {
                'word': {
                    "$in": bankList
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "Date": {
                        "$dateToString": {
                            "format": "%Y-%m", "date": "$cmtDate"
                        }
                    },
                    "Word": "$word"
                },
                "wordCount": {
                    "$sum": 1
                }
            }
        },
        {
            "$set": {
                "date": "$_id.Date",
                "word": "$_id.Word",

            }
        },
        {
            "$project": {
                "_id": 0
            }
        }


    ]

    if(dataContent == 'article-content'):
        result = list(DB[ARTICLE_COLLECTION].aggregate(article_pipeline))
    elif(dataContent == 'review-content'):
        result = list(DB[REVIEW_COLLECTION].aggregate(review_pipeline))
    else:
        article_result = list(
            DB[ARTICLE_COLLECTION].aggregate(article_pipeline))
        reviews_result = list(
            DB[REVIEW_COLLECTION].aggregate(review_pipeline))
        all_result = article_result+reviews_result
        df = pd.DataFrame(all_result)
        result = df.groupby(by=["date", "word"]).sum()
        result = result.reset_index().to_dict('records')
    return jsonify(result)


if __name__ == '__main__':
    app.run()
