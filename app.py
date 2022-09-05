from datetime import datetime
from flask import Flask, jsonify, request, render_template, request, redirect, url_for, send_from_directory
from flask_cors import CORS
from config import DB_NAME, DB, DICT_COLLECTION, REVIEW_COLLECTION, ARTICLE_COLLECTION

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
CORS(app)
@app.route('/', methods=['GET'])
def test():
    return (DICT_COLLECTION)


@app.route('/getCloud', methods=['GET'])
def getCloud():
    type = request.args.get('type')
    name = request.args.get('name')
    dataProduct =  request.args.get('dataProduct')
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
            source_list.append({"source":i})
        article_pipeline=[ 
        {
            "$match": {
                "artCat": name,
                "$or":source_list,
            }
        },
        {
            "$project": {
                "_id":0,
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
                "_id": {'$toUpper':"$word"},
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
                    "source":dataSource
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
                    "_id": {'$toUpper':"$word"},
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
                "source":dataSource
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
                "_id": {'$toUpper':"$reviews.word"},
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
    dataProduct =  request.args.get('dataProduct')
    dataSource = request.args.get('dataSource')
    dataContent = request.args.get('content')
    if type == "App":
        source = dataSource.split(',')
        source_list = []
        bank_list = []
        for i in source:
            source_list.append({"source":i})
        for bank in bankList:
            bank_list.append({"artCat":bank})
        article_pipeline = [
        {
            "$match": {
                "$or": bank_list,
            }
        },
        { 
            "$match": {
                "$or":source_list,
            }
        },
            
        {
            "$project": {
                "_id":0,
                "artCat":1,
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
                "$project":{
                    "_id":0
                }
            }
    ]
    else:
        
        article_pipeline = [
                    {
                "$match": {
                    "artCat": dataProduct,
                    "source":dataSource
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
                    "word": {'$toUpper':"$_id.Word"}
                }
            },
            {
                "$project":{
                    "_id":0
                }
            }

        ]
    review_pipeline = [
                {
            "$match": {
                "type": dataProduct,
                "source":dataSource
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
            "$project":{
                "_id":0
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


@app.route('/getDateRange', methods=['GET'])
def getDateRange():
    type = request.args.get('type')
    if type =="App":
        min_pipeline = [
            {
              "$match":{
                  "$or":[{"source":"app store"},{"source":"play store"}]
              }  
            },
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
              "$match":{
                   "$or":[{"source":"app store"},{"source":"play store"}]
              }  
            },
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
        ]
    else:
        min_pipeline = [
            {
              "$match":{
                  "source":"PTT"
              }  
            },
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
              "$match":{
                  "source":"PTT"
              }  
            },
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
        ]
    minDate = list(DB[ARTICLE_COLLECTION].aggregate(min_pipeline))[0]["minDate"]
    maxDate = list(DB[ARTICLE_COLLECTION].aggregate(max_pipeline))[
        0]["maxDate"]
    result = {
        "minDate": minDate,
        "maxDate": maxDate,
    }
    return jsonify(result)


@app.route('/getProportion', methods=['GET'])
def getProportion():
    type = request.args.get('type')
    dataContent = request.args.get('content')
    dataProduct =  request.args.get('dataProduct')
    dataSource = request.args.get('dataSource')

    def getArticlePipeline(word):
        if type=="App":
            source = dataSource.split(',')
            source_list = []
            for i in source:
                source_list.append({"source":i})
                
            pipeline = [
                {
                    "$match": {
                        "artCat": word,
                        "$or":source_list,
                }
                },
                {
                    "$project": {
                        "_id": 0,
                        "word": True,
                        "date": {
                            "$dateFromString": {
                                "dateString": '$artDate'
                            }
                        }
                    },
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
                        "word": {'$toUpper':"$_id.word"},
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
        else:
            pipeline = [
                {
                    "$match": {
                        "artCat": dataProduct,
                        "source":dataSource
                }
                },
                {
                    "$project": {
                        "_id": 0,
                        "word": True,
                        "artTitle":1,
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
                        "word": {'$toUpper':"$_id.word"},
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
            "$match": {
                "artCat": dataProduct,
                "source":dataSource
            }
        },
            {
                "$project": {
                    "_id": 0,
                    "artTitle":1,
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
                    "date":1,
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
                    "word": {'$toUpper':"$_id.word"},
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
        article_resultA = list(DB[ARTICLE_COLLECTION].aggregate(getArticlePipeline(keywordA)))
        article_resultB = list(DB[ARTICLE_COLLECTION].aggregate(getArticlePipeline(keywordB)))
        
        result = article_resultA + article_resultB
    elif(dataContent == 'review-content'):
        review_resultA = list(DB[ARTICLE_COLLECTION].aggregate(
        getReviewPipeline(keywordA)))
        review_resultB = list(DB[ARTICLE_COLLECTION].aggregate(
        getReviewPipeline(keywordB)))
        result = review_resultA + review_resultB
    else:
        article_resultA = list(DB[ARTICLE_COLLECTION].aggregate(getArticlePipeline(keywordA)))
        review_resultA = list(DB[ARTICLE_COLLECTION].aggregate(getReviewPipeline(keywordA)))
        all_resultA = article_resultA+review_resultA
        df = pd.DataFrame(all_resultA)
        resultA = df.groupby(by=["date", "word","keyword"]).sum()
        resultA = resultA.reset_index().to_dict('records')
        
        article_resultB = list(DB[ARTICLE_COLLECTION].aggregate(getArticlePipeline(keywordB)))
        review_resultB = list(DB[ARTICLE_COLLECTION].aggregate(getReviewPipeline(keywordB)))
        all_resultB = article_resultB+review_resultB
        df = pd.DataFrame(all_resultB)
        resultB = df.groupby(by=["date", "word","keyword"]).sum()
        resultB = resultB.reset_index().to_dict('records')
        
        result = resultA+resultB

    return jsonify(result)

@app.route('/getSent')
def getSent():
    type = request.args.get('type')
    name = request.args.get('name')
    dataProduct =  request.args.get('dataProduct')
    dataSource = request.args.get('dataSource')
    dataContent = request.args.get('content')
    if type=="App":
        source = dataSource.split(',')
        source_list = []
        for i in source:
            source_list.append({"source":i})
        article_pipeline = [
            {
                "$match": {
                    "artCat": name,
                    "$or":source_list,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "origin_sentence":1,
                    "date": {
                        "$dateFromString": {
                            "dateString": '$artDate',
                            "onError": datetime(2021, 5, 5),
                        }
                    },
                    "sent":1
                },
            },
             {
                "$group": {
                    "_id": {
                        "sent": "$sent", 
                        "date":
                            {
                                "$dateToString": {
                                    "format": "%Y-%m-%d", "date": "$date"
                                }
                            }
                            },
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
    else:
        article_pipeline = [
                {
                    "$match": {
                        'origin_sentence': {
                            "$regex": name
                        },
                        "artCat": dataProduct,
                        "source":dataSource
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "artTitle":1,
                        "origin_sentence":1,
                        "date": {
                            "$dateFromString": {
                                "dateString": '$artDate',
                                "onError": datetime(2021, 5, 5),
                            }
                        },
                        "sent":1
                    },
                },
                {
                    "$group": {
                        "_id": {
                            "sent": "$sent", 
                            "date":
                                {
                                    "$dateToString": {
                                        "format": "%Y-%m-%d", "date": "$date"
                                    }
                                }
                                },
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
    review_pipeline =[
         {
                "$match": {
                    'word': {
                        "$in": [name]
                    },
                    "type": dataProduct,
                    "source":dataSource
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "cmtContent":1,
                    "date": {
                        "$dateFromString": {
                            "dateString": '$cmtDate',
                            "onError": datetime(2021, 5, 5),
                        }
                    },
                    "sent":1
                },
            },
             {
                "$group": {
                    "_id": {"sent": "$sent", "date": {
                        "$dateToString": {
                            "format": "%Y-%m-%d", "date": "$date"
                        }
                    }},
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
        result = df.groupby(by=["date", "sent"]).sum()
        result = result.reset_index().to_dict('records')
    return jsonify(result)

@app.route('/getSentWord')
def getSentWord():
    type = request.args.get('type')
    name = request.args.get('name')
    regexName= name.lower()+ '|'+ name.upper()
    dataProduct =  request.args.get('dataProduct')
    dataSource = request.args.get('dataSource')
    dataContent = request.args.get('content')
    if type=="App":
        source = dataSource.split(',')
        source_list = []
        for i in source:
            source_list.append({"source":i})
        article_pipeline = [
            {
                "$match": {
                    "artCat": name,
                    "$or":source_list,
                }
            },
            {
                "$project": {
                    "origin_sentence":True,
                    "word": True,
                    "date": {
                        "$dateFromString": {
                            "dateString": '$artDate'
                        }
                    }
                },
            },

            {
                "$unwind": "$word"
            },
            {
                "$group": {
                    "_id": {'word':"$word","date":"$date"},
                    "wordCount": {
                        "$sum": 1
                    }
                }
            },
            {
                "$match": {
                    "wordCount": {
                        "$gt": 1
                    }
                }
            }
        ]
    else:
        article_pipeline = [
            {
                "$match": {
                    "artCat": dataProduct,
                    "source":dataSource
                }
            },
            {
                "$project": {
                    "artTitle": True,
                    "origin_sentence":True,
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
                    "origin_sentence": {"$regex": regexName},
                }
            },
            {
                "$unwind": "$word"
            },
            {
                "$group": {
                    "_id": {'word':"$word","date":"$date"},
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
            "$match": {
                "artCat": dataProduct,
                "source":dataSource
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
                "artTitle": {"$regex": regexName},
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
                "_id": {'word':"$reviews.word","date":"$date"},
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
        result =  []
        
        for item in all_result:
            if item['_id'] not in wordList:
                wordList.append(item['_id'])
                result.append(item)
            else:
                element = next(item for i in result if i["_id"] == item['_id'])
                element['wordCount'] +=item['wordCount']
    return jsonify(result)

@app.route('/getSentDict')
def getSentDict():
    result = list(DB[DICT_COLLECTION].find({"$or":[{"type":"pos_dict"},{"type":"neg_dict"}]},{"list":1,"type":1,"_id":0}))
    return jsonify(result)



@app.route('/getNgram')
def getNgram():
    type = request.args.get('type')
    topic = request.args.get('topic')
    keyword = request.args.get('keyword').lower()
    dataProduct =  request.args.get('dataProduct')
    dataSource = request.args.get('dataSource')
    dateStart = request.args.get('dateStart')
    dateStartList = dateStart.split('/')
    dateEnd = request.args.get('dateEnd')
    dateEndList = dateEnd.split('/')
    dataContent = request.args.get('content')
    N = int(request.args.get('n'))
    if type=="App":
        source = dataSource.split(',')
        source_list = []
        for i in source:
            source_list.append({"source":i})
            
        article_pipeline=[
                {
                    "$match": {
                        "artCat": topic,
                        "$or":source_list,
                    }
                },
                {
                    "$project":{
                        "_id":0,
                        "origin_sentence":1,
                        "word":1,
                        "date": {
                            "$dateFromString": {
                                "dateString": '$artDate'
                            }
                        }
                    },
                },
                {
                    "$match": {
                        'word': {
                            "$in": [keyword]
                        },
                        "date": {
                            "$gte": datetime(int(dateStartList[0]), int(dateStartList[1]), int(dateStartList[2])),
                            "$lt":datetime(int(dateEndList[0]), int(dateEndList[1]), int(dateEndList[2]))
                        }
                    },
                },
                {
                    "$project":{
                        "_id":0,
                        "word":1
                    }
                }
            ]
    else:
        article_pipeline=[
            {
                "$match": {
                    "artTitle": {'$regex':topic},
                    "artCat":dataProduct,
                    "source":dataSource
                }
            },
            {
                "$project":{
                    "_id":0,
                    "origin_sentence":1,
                    "word":1,
                    "date": {
                        "$dateFromString": {
                            "dateString": '$artDate'
                        }
                    }
                },
            },
            {
                "$match": {
                    'word': {
                        "$in": [keyword]
                    },
                    "date": {
                        "$gte": datetime(int(dateStartList[0]), int(dateStartList[1]), int(dateStartList[2])),
                        "$lt":datetime(int(dateEndList[0]), int(dateEndList[1]), int(dateEndList[2]))
                    }
                },
            },
            {
                "$project":{
                    "_id":0,
                    "word":1
                }
            }
        ]
    review_pipeline = [
        {
            "$match": {
                "artCat": dataProduct,
                "source":dataSource,
                "artTitle": {'$regex':topic},
            }
        },
        {
            "$project": {
                "_id":0,
                "origin_sentence":1,
                "word":1,
                "artUrl":1,
                "date": {
                    "$dateFromString": {
                        "dateString": '$artDate'
                    }
                }
            },
        },
        {
           "$match": {
                'word': {
                    "$in": [keyword]
                },
                "date": {
                    "$gte": datetime(int(dateStartList[0]), int(dateStartList[1]), int(dateStartList[2])),
                    "$lt":datetime(int(dateEndList[0]), int(dateEndList[1]), int(dateEndList[2]))
                }
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
            "$set":{
                "word":"$reviews.word"
            }
        },
        {
            "$project":{
                "word":1
            }
        }
    ]
    def article():
        result = list(DB[ARTICLE_COLLECTION].aggregate(article_pipeline))
        if not result:
           return [] 
        result = pd.DataFrame(result)   
        bigram= result['word'].apply(lambda x:list(ngrams(x,N)))
        bigram_df = bigram.apply(lambda x:[" ".join(w) for w in x]).explode().to_frame()
        bigram_df['word']  = bigram_df['word'].apply(lambda word:str(word).upper())
        group = bigram_df[bigram_df['word'].str.contains(keyword.upper())].groupby(['word'])
        group = group.size().reset_index(name='counts').sort_values(by='counts',ascending=False)
        result = group[group['counts']>1].to_dict('records')
        return result
    def review():
        result = list(DB[ARTICLE_COLLECTION].aggregate(review_pipeline))
        if not result:
           return [] 
        result = pd.DataFrame(result)
        bigram= result['word'].apply(lambda x:list(ngrams(x,N)))
        bigram_df = bigram.apply(lambda x:[" ".join(w) for w in x]).explode().to_frame()
        bigram_df['word']  = bigram_df['word'].apply(lambda word:str(word).upper())
        group = bigram_df[bigram_df['word'].str.contains(keyword.upper() , na=False)].groupby(['word'])
        group = group.size().reset_index(name='counts').sort_values(by='counts',ascending=False)
        result = group[group['counts']>1].to_dict('records')
        return result
    
    
    if(dataContent == 'article-content'):
        result =article()

    elif(dataContent == 'review-content'):
        result = review()
    else:
        all_result = article()+review()
        wordList = []
        result =  []
        
        for item in all_result:
            if item['word'] not in wordList:
                wordList.append(item['word'])
                result.append(item)
            else:
                element = next(item for i in result if i["word"] == item['word'])
                element['counts'] +=item['counts']
            
    return jsonify(result)

@app.route('/getSentence')
def getSentence():
    type = request.args.get('type')
    topic = request.args.get('topic')
    keyword = request.args.get('keyword').lower()
    regexKeyword = keyword.lower()+ '|'+ keyword.upper()
    dataProduct =  request.args.get('dataProduct')
    dataSource = request.args.get('dataSource')
    dateStart = request.args.get('dateStart')
    dateStartList = dateStart.split('/')
    dateEnd = request.args.get('dateEnd')
    dateEndList = dateEnd.split('/')
    dataContent = request.args.get('content')
    if type=="App":
        source = dataSource.split(',')
        source_list = []
        for i in source:
            source_list.append({"source":i})
        article_pipeline=[
                {
                        "$match": {
                            "artCat": topic,
                            "$or":source_list,
                        }
                    },
                    {
                        "$project":{
                            "_id":0,
                            "origin_sentence":1,
                            "word":1,
                            "sent":1,
                            "date": {
                                "$dateFromString": {
                                    "dateString": '$artDate'
                                }
                            }
                        },
                    },
                    {
                        "$match": {
                            'word': {
                                "$in": [keyword]
                            },
                            "date": {
                                "$gte": datetime(int(dateStartList[0]), int(dateStartList[1]), int(dateStartList[2])),
                                "$lt":datetime(int(dateEndList[0]), int(dateEndList[1]), int(dateEndList[2]))
                            }
                        },
                    },
                    
                {
                    "$project":{
                        "date":1,
                        "sentence":"$origin_sentence",
                        "sent":1
                    }
                }
            ]
    else:
        article_pipeline=[
            {
                "$match": {
                    "artTitle": {'$regex':topic},
                    "artCat":dataProduct,
                    "source":dataSource
                }
            },
            {
                "$project":{
                    "_id":0,
                    "artUrl":1,
                    "word":1,
                    "sentence_sent":1,
                    "date": {
                        "$dateFromString": {
                            "dateString": '$artDate'
                        }
                    }
                },
            },
            {
                "$match": {
                    'word': {
                        "$in": [keyword]
                    },
                    "date": {
                        "$gte": datetime(int(dateStartList[0]), int(dateStartList[1]), int(dateStartList[2])),
                        "$lt":datetime(int(dateEndList[0]), int(dateEndList[1]), int(dateEndList[2]))
                    }
                },
            },
            {
                "$unwind":"$sentence_sent"
            },
            {
                "$match":{
                    "sentence_sent.sentence":{'$regex':regexKeyword}
                }
            },
            {
                "$project":{
                    "word":0
                }
            },
            {
                "$set":{
                    "sent":"$sentence_sent.sent",
                    "sentence":"$sentence_sent.sentence"
                }
            },
            {
                "$project":{
                    "sentence_sent":0
                }
            }
        ]
    review_pipeline = [
        {
            "$match": {
                "artTitle": {'$regex':topic},
                "artCat":dataProduct,
                "source":dataSource
            }
        },
        {
            "$project": {
                "_id":0,
                "artUrl":1,
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
            "$match":{
                "reviews.cmtContent":{
                    "$regex":keyword
                        }
                      }
        },
        {
            "$set":{
                "sentence":"$reviews.cmtContent",
                "sent":"$reviews.sent"
            }
        },
        {
            "$project":{
                "artUrl":1,
                "date":1,
                "sentence":1,
                "sent":1
            }
        }

    ]
    
    if(dataContent == 'article-content'):
        result = list(DB[ARTICLE_COLLECTION].aggregate(article_pipeline))
    elif(dataContent == 'review-content'):
        result = list(DB[ARTICLE_COLLECTION].aggregate(review_pipeline))
    else:
        result = list(DB[ARTICLE_COLLECTION].aggregate(article_pipeline)) + list(DB[ARTICLE_COLLECTION].aggregate(review_pipeline))

    if(len(result)>5):
        result = random.sample(result, 5)
        
    return jsonify(result)
if __name__ == '__main__':
    app.run(debug=True)
