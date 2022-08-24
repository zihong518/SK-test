import pymongo

CONNECTION_STRING = 'mongodb://text-analysis:8im5h6bvEZSWW83JoHknWRBAICJuLipgbyxYj8aPB8V4LWacWeo7klrH0TkCsieXTsWN7AVYMYHZFp5OgUhIMg==@text-analysis.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@text-analysis@'  # Prompts user for connection string
DB_NAME = "SK-text-analysis"
REVIEW_COLLECTION = "Review"
ARTICLE_COLLECTION = "Article"
DICT_COLLECTION = "Dict"

DB = pymongo.MongoClient(CONNECTION_STRING)[DB_NAME]

sentKey = "29c2de4861c643308f53b806c94a39ed"
