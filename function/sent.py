from asyncio.windows_events import NULL
import os.path
import sys
sys.path.append(os.path.abspath('../'))
from config import DB, DB, REVIEW_COLLECTION, ARTICLE_COLLECTION, DICT_COLLECTION,sentKey
import time
from pymongo import UpdateOne



endpoint = "https://skfhtextanalysis.cognitiveservices.azure.com/"

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# Authenticate the client using your key and endpoint 
def authenticate_client():
    ta_credential = AzureKeyCredential(sentKey)
    text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, 
            credential=ta_credential,
            default_language= 'zh-TW') 
    return text_analytics_client

client = authenticate_client()

# Example function for detecting sentiment in text for article
def sentiment_article(documents,client):
    sentList = []
    responses = client.analyze_sentiment(documents=documents)
    for response in responses: 
        article = response.confidence_scores
        sent_list = [article.positive,article.neutral,article.negative]
        # 最高的就判定為什麼情緒
        sent_index = sent_list.index(max(sent_list))
        if(sent_index==0):
            sent ='positive'
        elif(sent_index ==1):
            sent = 'neutral'
        else:
            sent = 'negative'
        sentList.append(sent)
    
    sentence_list_all =[]
    sentence_list = []
    # 每一個句子的情緒加進去list內
    for response in responses:
        for idx, sentence in enumerate(response.sentences):
            result ={
                "sentence" : sentence.text,
                'sent':sentence.sentiment
            }
            sentence_list.append(result)
        sentence_list_all.append(sentence_list)
        sentence_list=[]

    return sentList ,sentence_list_all

# review的情緒
def sentiment_review(documents,client):
    sentList = []
    responses = client.analyze_sentiment(documents=documents)
    for response in responses: 
        article = response.confidence_scores
        sent_list = [article.positive,article.neutral,article.negative]
        # 最高的就判定為什麼情緒
        sent_index = sent_list.index(max(sent_list))
        if(sent_index==0):
            sent ='positive'
        elif(sent_index ==1):
            sent = 'neutral'
        else:
            sent = 'negative'
        sentList.append(sent)
    
    return sentList

# review的data
def sentAnalysis_review():
    # 去request沒有情緒的data
    allData = list(DB[REVIEW_COLLECTION].find({"sent":None},{"_id": 1, "cmtContent": 1}))
    print(len(allData))
    updates = []
    temp = []
    id = []
    for index,data in enumerate(allData):
        # 怕資料是空所以加一個0
        temp.append("0"+data['cmtContent'])
        id.append(data['_id'])
        # 一次十筆丟進去model內(最多就十筆)
        if((index+1) % 10 == 0):
            print(len(temp))
            sent = sentiment_review(temp,client)
            for i in range(0,10):
                updates.append(UpdateOne({'_id': id[i]}, {
                            '$set': {'sent':sent[i]}}, upsert=True))
            temp = []
            id= []

        # 每1000筆寫入一次
        if ((index+1) % 1000) == 0:
            print(index+1)
            print("STARE WRITE")
            DB[REVIEW_COLLECTION].bulk_write(updates)
            print("AFTER WRITE")
            updates = []
            print("CLEAN THE UPDATES")
            time.sleep(5)
    DB[REVIEW_COLLECTION].bulk_write(updates)
    print("AFTER WRITE")

# article的data
def sentAnalysis_article():
    allData = list(DB[ARTICLE_COLLECTION].find({"sent":None},{"_id": 1, "origin_sentence": 1}))
    updates = []
    temp = []
    id = []
    for index,data in enumerate(allData):
        # 文字最多只能5120個字
        temp.append('0'+data['origin_sentence'][:5119])
        id.append(data['_id'])
        # 一次最多十筆
        if((index+1) % 10 == 0):
            sent,sentence_list = sentiment_article(temp,client)
            for i in range(0,10):
                updates.append(UpdateOne({'_id': id[i]}, {
                            '$set': {'sent':sent[i],"sentence_sent":sentence_list[i]}}, upsert=True))
            temp=[]
            id=[]
        # 每一千筆就寫入
        if ((index+1) % 1000) == 0:
            print(index+1)
            print("STARE WRITE")
            DB[ARTICLE_COLLECTION].bulk_write(updates)
            print("AFTER WRITE")
            updates = []
            print("CLEAN THE UPDATES")
            time.sleep(5)
            
            
    DB[ARTICLE_COLLECTION].bulk_write(updates)
    print("AFTER WRITE")

def main():
    sentAnalysis_review()
    sentAnalysis_article()


if __name__ == '__main__':
    main()
