import urllib.request as req
from datetime import datetime
import requests
import bs4
import re
import json
import pymongo
from config import DB_NAME, DB, DICT_COLLECTION, REVIEW_COLLECTION, ARTICLE_COLLECTION


bank_list = {
	"新光":'495872725',
	"國泰":"373500505",
    "iLeo":"1446229166",
    "KoKo":"905157314",
	'台新':"388917170",
	'Richart':'1079733142',
    '永豐':'393497156',
	'DAWHO':'1494273814',
}
# 替換掉網址以及標點符號成空值
def subSentence(x):
    value = re.sub('[^\u4e00-\u9fa5a-zA-Z]+', '',
                   re.sub('http(s)?[-://A-Za-z0-9\\.?=/s_&]+', '', x))
    return value
def main():
    for bank in bank_list:
        results=[]
        for page in range(1,11):
            url = f"https://itunes.apple.com/rss/customerreviews/page={page}/id={bank_list[bank]}/sortby=mostrecent/json?l=en&&cc=tw"
            request = req.Request(url) 
            with req.urlopen(request) as response:
                data=response.read()

            data=json.loads(data)
            # 得到reviews
            reviews = data['feed']['entry']
            
            for review in reviews:
                date = review['updated']['label']
                date = datetime.strptime(date,"%Y-%m-%dT%H:%M:%S-07:00")
                # 日期大於2021的才會寫進去
                compare_date = datetime(2021, 1, 1)
                if(date<compare_date):
                    continue
                content = review['content']['label']
                date = datetime.strftime(date,"%Y/%m/%d")
                
                result={
                    "artDate": date,
                    "artCat": bank,
                    "origin_sentence": content,
                    "sentence":subSentence(content),
                    "source":"app store"
                }

                results.append(result)
        
        print("START WRITE")
        DB[ARTICLE_COLLECTION].insert_many(results)
        print("FINISH WRITE")   
        

if __name__ == '__main__':
    main()
    
