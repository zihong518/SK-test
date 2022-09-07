import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
from time import sleep
from datetime import datetime
import random
import re
from tqdm.auto import tqdm, trange
import pandas as pd
import pymongo
from config import DB_NAME, DB, DICT_COLLECTION, REVIEW_COLLECTION, ARTICLE_COLLECTION

    
# 替換掉網址以及標點符號成空值
def subSentence(x):
    value = re.sub('[^\u4e00-\u9fa5a-zA-Z]+', '',
                   re.sub('http(s)?[-://A-Za-z0-9\\.?=/s_&]+', '', x))
    return value

# chrome driver
chrome_driver = r"C:\Users\zihon\Anaconda3\Scripts\chromedriver.exe" 

# url list
bank_list = {
	"新光":'https://play.google.com/store/apps/details?id=com.willmobile.mobilebank.skbbank',
	"國泰":"https://play.google.com/store/apps/details?id=com.cathaybk.mymobibank.android",
    "iLeo":"https://play.google.com/store/apps/details?id=com.firstbank.mbanklite",
    "KoKo":"https://play.google.com/store/apps/details?id=com.cathaybk.koko",
	'台新':"https://play.google.com/store/apps/details?id=tw.com.taishinbank.mobile",
	'Richart':'https://play.google.com/store/apps/details?id=tw.com.taishinbank.richart',
    '永豐':'https://play.google.com/store/apps/details?id=com.sionpac.app.SinoPac',
	'DAWHO':'https://play.google.com/store/apps/details?id=com.sinopac.dawho',

}
# scroll the page
def scroll(modal):
    # 如果資料太多就只滑30下
    pagecount = 30
    try:        
        # return the page height
        last_height = driver.execute_script("return arguments[0].scrollHeight", modal)
        
        while pagecount:
            # 滑動頁面減一下
            pagecount -= 1
            pause_time = random.uniform(0.5, 0.8)
            # scroll the page
            driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", modal)
			# time sleep

            time.sleep(pause_time)
            # scroll top of a little to get more page
            driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight-50);", modal)
            time.sleep(pause_time)
            # return new height
            new_height = driver.execute_script("return arguments[0].scrollHeight", modal)
            try:
                # click the "more" button
                all_review_button = driver.find_element_by_xpath('/html/body/div[1]/div[4]/c-wiz/div/div[2]/div/div/main/div/div[1]/div[2]/div[2]/div/span/span').click()
            except:
                # if the scroll done
                if new_height == last_height:
                    print("scroll done")
                    break
                last_height = new_height
                
    except Exception as e:
        print("error: ", e)
    print(pagecount)

def main():
    for bank in bank_list:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        driver = webdriver.Chrome(options = chrome_options)
        # open the page
        driver.get(bank_list[bank])
        # wait the page loading
        wait = WebDriverWait(driver, 5)

        # find the "view all reviews" button
        all_review_button_xpath = '/html/body/c-wiz[2]/div/div/div[1]/div[2]/div/div[1]/c-wiz[4]/section/div/div/div[5]/div/div/button/span'

        button_loading_wait = wait.until(EC.element_to_be_clickable((By.XPATH, all_review_button_xpath)))
        # click the button
        driver.find_element('xpath',all_review_button_xpath).click()

        # wait the review page render
        all_review_page_xpath = '/html/body/div[4]/div[2]/div/div/div/div/div[2]'
        page_loading_wait = wait.until(EC.element_to_be_clickable((By.XPATH, all_review_page_xpath)))

        # page infinite scroll down
        modal = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='fysCi']")))
        scroll(modal)
        html_source = driver.page_source
        soup_source = BeautifulSoup(html_source, 'html.parser')

        # get review
        review_source = soup_source.find_all(class_ = 'RHo1pe')

        dataset = []
        review_num = 0 

        for review in review_source:
            review_num+=1
            # get review and date
            date_full = review.find_all(class_ = 'bp9Aid')[0].text
            date_year = date_full[0:4]  
            # extract the date data
            year_index = date_full.find('年')
            month_index = date_full.find('月')
            day_index = date_full.find('日')
            # get mouth
            date_month = str(int(date_full[year_index+1:month_index]))
            if len(date_month) == 1:
                date_month = '0' + date_month
            # get day
            date_day = str(int(date_full[month_index+1:day_index])) 
            if len(date_day) == 1:
                date_day = '0' + date_day
            
            # date To yyyymmdd 
            date_full = date_year + date_month + date_day
            date_full = datetime.strptime(
                date_full, '%Y%m%d')
            # limit the date
            compare_date = datetime(2021, 1, 1)
            if(date_full<compare_date):
                continue
            date_full = date_full.strftime("%Y/%m/%d")
            user_name = review.find_all(class_ = 'X5PpBb')[0].text # reviewer name
            rating = review.find_all(class_ = "iXRFPc")[0]['aria-label'][4]  # rating
            if  review.find_all(class_ = 'h3YV2d'):
                content = review.find_all(class_ = 'h3YV2d')[0].text # review
            else:
                content =""
            
            data = {
                "id": review_num, 
                "artDate": date_full,
                "artCat": bank,
                "origin_sentence": content,
                "sentence":subSentence(content),
                "source":"play store"
            }
            dataset.append(data)
        print("START WRITE")
        DB[ARTICLE_COLLECTION].insert_many(dataset)
        print("FINISH WRITE")

if __name__ == '__main__':
    main()
