from nntplib import ArticleInfo
from pickle import NONE
from pymongo import UpdateOne
import os.path
import sys
sys.path.append(os.path.abspath('../'))
from gettext import find
import pandas as pd
import numpy as np
import os
import re
import jieba
import jieba.analyse
from datetime import datetime
import time
from config import DB, DB, REVIEW_COLLECTION, ARTICLE_COLLECTION, DICT_COLLECTION
import pymongo


# 替換掉網址以及標點符號成空值
def subSentence(x):
    value = re.sub('[^\u4e00-\u9fa5a-zA-Z]+', '',
                   re.sub('http(s)?[-://A-Za-z0-9\\.?=/s_&]+', '', x))
    return value

# 將自建字典加到jieba內
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

# 斷詞寫入資料庫
def sentenceToToken(collection,source):
    requestData = list(DB[collection].find({"source":source}))
    stop_words = list(DB[DICT_COLLECTION].find(
        {"type": "stop_word"}))[0]['list']
    article = pd.DataFrame(requestData)
    article['word'] = article.sentence.apply(lambda x: getToken(x, stop_words))
    updates = []
    start_time = time.time()
    for index, row in article.iterrows():
        # 1000筆就先寫進去
        if ((index+1) % 1000) == 0:
            print(index+1)
            print("STARE WRITE")
            DB[collection].bulk_write(updates)
            print("AFTER WRITE")
            updates = []
            print("CLEAN THE UPDATES")
            time.sleep(5)
        # 把要更新的加進去result內
        updates.append(UpdateOne({'_id': row.get('_id')}, {
                       '$set': {'word': row.get('word')}}, upsert=True))
    # 剩下的
    DB[collection].bulk_write(updates)
    print("AFTER WRITE")
    print("--- %s seconds ---" % (time.time() - start_time))
                                            
def main():
    jiebaAddDict()
    sentenceToToken(ARTICLE_COLLECTION,'app store')


if __name__ == '__main__':
    main()
