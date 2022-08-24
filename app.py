from datetime import datetime
from flask import Flask, jsonify, request, render_template, request, redirect, url_for, send_from_directory
from flask_cors import CORS
from config import DB_NAME, DB, DICT_COLLECTION, REVIEW_COLLECTION, ARTICLE_COLLECTION

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
CORS(app)


@app.route('/', methods=['GET'])
def test():
    print(DICT_COLLECTION)
    return (DICT_COLLECTION)


@app.route('/getCloud', methods=['GET'])
def getCloud():
    name = request.args.get('name')
    dateStart = request.args.get('dateStart')
    dateEnd = request.args.get('dateEnd')
    dateStartList = dateStart.split('/')
    dateEndList = dateEnd.split('/')
    dataContent = request.args.get('content')

    article_pipeline = [
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
                    "$gt": 5
                }
            }
        }

    ]
    review_pipeline = [
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
                    "$gt": 5
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
    now = datetime.now()
    print(now.time())
    bankList = request.args.get('name').split(',')
    dataContent = request.args.get('content')
    article_pipeline = [
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
            "$project": {
                "_id": 0,
                "artUrl": True,
            },
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
            "$match": {
                'reviews.word': {
                    "$in": bankList
                }
            }
        },
        {
            "$project": {
                "artUrl": 0,
                "reviews.cmtDate": {
                    "$dateFromString": {
                        "dateString": '$reviews.cmtDate'
                    }
                },
                "reviews.word": 1
            },
        },
        {
            "$group": {
                "_id": {
                    "Date": {
                        "$dateToString": {
                            "format": "%Y-%m", "date": "$reviews.cmtDate"
                        }
                    },
                    "Word": "$reviews.word"
                },
                "wordCount": {
                    "$sum": 1
                }
            }
        },
        {
            "$set": {
                "date": "$_id.Date",
                "word": {'$toUpper': "$_id.Word"},

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
        result = list(DB[ARTICLE_COLLECTION].aggregate(review_pipeline))
    else:
        article_result = list(
            DB[ARTICLE_COLLECTION].aggregate(article_pipeline))
        reviews_result = list(
            DB[ARTICLE_COLLECTION].aggregate(review_pipeline))
        all_result = article_result+reviews_result
        df = pd.DataFrame(all_result)
        result = df.groupby(by=["date", "word"]).sum()
        result = result.reset_index().to_dict('records')
        # for item in all_result:
        #     if item['_id'] not in wordList:
        #         wordList.append(item['_id'])
        #         result.append(item)
        #     else:
        #         for i in result:
        #             if (i['_id'] == item['_id']):
        #                 i['wordCount'] += item['wordCount']
    print(datetime.now() - now)
    return jsonify(result)


@app.route('/getDateRange', methods=['GET'])
def getDateRange():
    min_pipeline = [
        {
            "$project": {
                "date": {
                    "$dateFromString": {
                        "dateString": '$artDate',
                        "onError": datetime(2021, 5, 5),
                    }
                }
            },
        },
        {
            "$group": {
                "_id": {},
                "minDate": {
                    "$min": "$date"
                }
            }
        }
    ]
    max_pipeline = [
        {
            "$project": {
                "date": {
                    "$dateFromString": {
                        "dateString": '$artDate',
                        "onError": datetime(2021, 5, 5)
                    }
                }
            },
        },
        {
            "$group": {
                "_id": {},
                "maxDate": {
                    "$max": "$date"
                }
            }
        }
        # {
        #     "$sort": {
        #         "date": -1
        #     }
        # },
        # {
        #     "$limit":1
        # }
    ]

    minDate = list(DB[ARTICLE_COLLECTION].aggregate(min_pipeline))[
        0]["minDate"]
    maxDate = list(DB[ARTICLE_COLLECTION].aggregate(max_pipeline))[
        0]["maxDate"]
    result = {
        "minDate": minDate,
        "maxDate": maxDate,
    }
    return jsonify(result)


@app.route('/getProportion', methods=['GET'])
def getProportion():
    dataContent = request.args.get('content')

    def getArticlePipeline(word):

        pipeline = [
            {
                "$project": {
                    "_id": 0,
                    "word": True,
                    "artTitle": 1,
                    "date": {
                        "$dateFromString": {
                            "dateString": '$artDate'
                        }
                    }
                },
            },
            {
                "$match": {
                    'artTitle': {
                        "$regex": word
                    }
                }
            },
            {
                "$unwind": "$word"
            },
            {
                "$group": {
                    "_id": {"word": "$word", "date": "$date"},
                    "wordCount": {
                        "$sum": 1
                    }
                }
            },
            {
                "$set": {
                    "word": {'$toUpper': "$_id.word"},
                    "keyword": word,
                    "date": "$_id.date"
                }
            },
            {
                "$project": {
                    '_id': 0
                }
            }
        ]
        return pipeline

    def getReviewPipeline(word):
        pipeline = [
            {
                "$project": {
                    "_id": 0,
                    "artTitle": 1,
                    "artUrl": True,
                    "date": {
                        "$dateFromString": {
                            "dateString": '$artDate'
                        }
                    }
                },
            },
            {
                "$match": {
                    'artTitle': {
                        "$regex": word
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
                    "date": 1,
                    "reviews._id": 0,
                    "reviews.word": 1
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
                    "_id": {"word": "$reviews.word", "date": "$date"},
                    "wordCount": {
                        "$sum": 1
                    }
                }
            },
            {
                "$set": {
                    "word": {'$toUpper': "$_id.word"},
                    "keyword": word,
                    "date": "$_id.date"
                }
            },
            {
                "$project": {
                    '_id': 0
                }
            }

        ]
        return pipeline
    keywordA = request.args.get('keywordA')
    keywordB = request.args.get('keywordB')

    if(dataContent == 'article-content'):
        article_resultA = list(DB[ARTICLE_COLLECTION].aggregate(
            getArticlePipeline(keywordA)))
        print(article_resultA)
        article_resultB = list(DB[ARTICLE_COLLECTION].aggregate(
            getArticlePipeline(keywordB)))

        result = article_resultA + article_resultB
    elif(dataContent == 'review-content'):
        review_resultA = list(DB[ARTICLE_COLLECTION].aggregate(
            getReviewPipeline(keywordA)))
        review_resultB = list(DB[ARTICLE_COLLECTION].aggregate(
            getReviewPipeline(keywordB)))
        result = review_resultA + review_resultB
    else:
        article_resultA = list(DB[ARTICLE_COLLECTION].aggregate(
            getArticlePipeline(keywordA)))
        review_resultA = list(DB[ARTICLE_COLLECTION].aggregate(
            getReviewPipeline(keywordA)))
        all_resultA = article_resultA+review_resultA
        df = pd.DataFrame(all_resultA)
        resultA = df.groupby(by=["date", "word", "keyword"]).sum()
        resultA = resultA.reset_index().to_dict('records')

        article_resultB = list(DB[ARTICLE_COLLECTION].aggregate(
            getArticlePipeline(keywordB)))
        review_resultB = list(DB[ARTICLE_COLLECTION].aggregate(
            getReviewPipeline(keywordB)))
        all_resultB = article_resultB+review_resultB
        df = pd.DataFrame(all_resultB)
        resultB = df.groupby(by=["date", "word", "keyword"]).sum()
        resultB = resultB.reset_index().to_dict('records')

        result = resultA+resultB

    return jsonify(result)


@app.route('/getSent')
def getSent():
    name = request.args.get('name')

    dataContent = request.args.get('content')
    pipeline = [
        {
            "$match": {
                'origin_sentence': {
                    "$regex": name
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "artTitle": 1,
                "origin_sentence": 1,
                "date": {
                    "$dateFromString": {
                        "dateString": '$artDate'
                    }
                },
                "sent": 1
            },
        },
        {
            "$group": {
                "_id": {"sent": "$sent", "date": "$date"},
                "count": {
                    "$sum": 1
                }
            }
        },
        {
            "$set": {
                "sent": "$_id.sent",
                "date": "$_id.date",
            }
        },
        {
            "$project": {
                '_id': 0
            }
        }
    ]

    result = list(DB[ARTICLE_COLLECTION].aggregate(pipeline))
    return jsonify(result)


@app.route('/getSentWord')
def getSentWord():
    name = request.args.get('name')

    dataContent = request.args.get('content')

    article_pipeline = [
        {
            "$project": {
                "artTitle": True,
                "origin_sentence": True,
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
                "origin_sentence": {"$regex": name},
            }
        },
        {
            "$unwind": "$word"
        },
        {
            "$group": {
                "_id": {'word': "$word", "date": "$date"},
                "wordCount": {
                    "$sum": 1
                }
            }
        },
        {
            "$match": {
                "wordCount": {
                    "$gt": 3
                }
            }
        }
    ]
    review_pipeline = [
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
                "_id": {'word': "$reviews.word", "date": "$date"},
                "wordCount": {
                    "$sum": 1
                }
            }
        },
        {
            "$match": {
                "wordCount": {
                    "$gt": 3
                }
            }
        }


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
                element = next(item for i in result if i["_id"] == item['_id'])
                element['wordCount'] += item['wordCount']
    return jsonify(result)


@app.route('/getSentDict')
def getSentDict():
    result = list(DB[DICT_COLLECTION].find({"$or": [{"type": "pos_dict"}, {
                  "type": "neg_dict"}]}, {"list": 1, "type": 1, "_id": 0}))
    return jsonify(result)


if __name__ == '__main__':
    app.run
