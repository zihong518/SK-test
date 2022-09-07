import urllib.request as req
import json
import requests
import bs4
import csv
import time
import random
import re
from datetime import datetime
import pandas as pd
import jieba
import jieba.analyse
from random import randint
from pymongo import UpdateOne
from config import DB_NAME, DB, DICT_COLLECTION, REVIEW_COLLECTION, ARTICLE_COLLECTION


my_headers = {'cookie': 'over18=1;'}
articles = []
reviews = []
# 目前的看板
topic = "Bank_Service"
pageId = 0

# 替換掉網址和符號
def subSentence(x):
    value = re.sub('[^\u4e00-\u9fa5a-zA-Z]+', '',
                   re.sub('http(s)?[-://A-Za-z0-9\\.?=/s_&]+', '', x))
    return value

# 加入自建字典
def jiebaAddDict():
    user_dict = list(DB[DICT_COLLECTION].find(
        {"type": "user_dict"}))[0]['list']
    for word in user_dict:
        jieba.add_word(word)

# 斷詞
def getToken(row, stop_word):
    seg_list = jieba.lcut(row)
    # 篩選不在停用字的字與字元數大於1的字詞
    seg_list = [w.lower()
                for w in seg_list if w not in stop_word and len(w) > 1]
    return seg_list

# 斷詞
def addToken(x,stop_words):
    x['word'] = getToken(x['sentence'], stop_words)
    return x 

# 句子斷詞
def sentenceToToken(collection_name,data):
    stop_words = list(DB[DICT_COLLECTION].find(
        {"type": "stop_word"}))[0]['list']

    tokenDate = map(lambda x: addToken(x, stop_words), data)
    
    updates = []
    start_time = time.time()
    for index,row in enumerate(tokenDate):
        # 每1000筆就寫入資料庫
        if ((index+1) % 1000) == 0:
            print("STARE WRITE")
            DB[collection_name].bulk_write(updates)
            print("AFTER WRITE")
            updates = []
            print("CLEAN THE UPDATES")
            time.sleep(5)
        updates.append(UpdateOne({'artUrl': row['artUrl']}, {
                       '$set': row}, upsert=True))
    DB[collection_name].bulk_write(updates)
    print("AFTER WRITE")
    print("--- %s seconds ---" % (time.time() - start_time))

# get 內文
def getArticleData(url):
    resp = requests.get(url, headers=my_headers)
    soup = bs4 . BeautifulSoup(resp.text, 'lxml')
    # 標題
    article = soup.select("span.article-meta-value")[2].text
    # 內文處理
    main_container = soup.find(id='main-container')
    all_text = main_container.text
    pre_text = all_text.split('--')[0]
    texts = pre_text.split('\n')
    contents = texts[2:]
    a_content = '\n'.join(contents)
    # 時間處理
    time_str = soup.select("span.article-meta-value")[3].text
    a_time = datetime.strptime(time_str, '%a %b %d %H:%M:%S %Y')
    a_time = a_time.strftime("%Y/%m/%d")
    return soup, article, a_content, a_time

# get 留言
def getReviewData(push_tags, contents, review_time_str):
    index = contents.index(content)
    review_time_origin = review_time_str[index].text.replace(" ", "")
    review_time_origin = '2022/'+review_time_origin
    try:
        review_time = datetime.strptime(
            review_time_origin, '%Y/%m/%d%H:%M'+'\n')
        
        review_time = review_time.strftime("%Y/%m/%d")
    except:
        review_time = review_time_origin
    tag = push_tags[index].text
    cmtContent = contents[index].text.split(':')[1]
    cmtDate = review_time

    return tag, cmtContent, cmtDate

def main():
    for page in range(1, 214):
        url = f"https://www.ptt.cc/bbs/{topic}/index.html" if not pageId else f"https://www.ptt.cc/bbs/{topic}/index{pageId}.html"
        time.sleep(random.randint(2, 5))
        resp = requests.get(url, headers=my_headers)
        soup = bs4 . BeautifulSoup(resp.text, 'lxml')
        links = soup.select("div.title>a")
        # 得到目前的頁碼
        if not pageId:
            lastPage = soup.select(
                "div.btn-group-paging >a:nth-child(2)")[0]['href']
            pageId = re.search(r"\d{1,4}", lastPage).group(0)
        else:
            pageId = int(pageId)-1

        for link in links:
            try:
                url = f'https://www.ptt.cc{link["href"]}'
                print(url)
                time.sleep(random.randint(1, 3))
                soup, artTitle, sentence, artDate = getArticleData(url)
                article = {
                    "artTitle": artTitle,
                    "artUrl": url,
                    "artDate": artDate,
                    "artCat": topic,
                    "origin_sentence": sentence,
                    "sentence":subSentence(sentence),
                    "source":"PTT"
                }
                
                articles.append(article)

                # insertData(article)
                push_tags = soup.select('span.push-tag')
                contents = soup.select('span.push-content')
                review_time_str = soup.select('span.push-ipdatetime')
                for content in contents:
                    tag, cmtContent, cmtDate = getReviewData(
                        push_tags, content, review_time_str)

                    review = {
                        "artUrl": url,
                        "cmtStatus": tag,
                        "cmtDate": cmtDate,
                        "cmtContent": cmtContent,
                        "sentence":subSentence(cmtContent),
                        "source" : "PTT",
                        "type" : topic
                    }
                    reviews.append(review)
            except:
                continue
        if (page+1) % 10 == 0:
            jiebaAddDict()
            print('start write')
            sentenceToToken(ARTICLE_COLLECTION,articles)
            articles = []
            sentenceToToken(REVIEW_COLLECTION,reviews)
            reviews = []


if __name__ == '__main__':
    main()


    
        
