# DB schema

## Article
- artTitle:標題 (App沒有)
- artDate:日期
- artTime:時間 (App沒有)
- artUrl:網址 (App沒有)
- artCat:分類
- sentence:清除過標點符號和數字後的句子
- origin_sentence:原始的句子
- word:斷詞(array)
- sent:主文的情緒
- sentence_sent:每一句的句子和情緒(object array)
- source:資料來源 
```json
{
	"_id" : ObjectId("62fb5e36b383c512406191a6"), 
	"artTitle" : "[情報]渣打現金回饋卡2021", # 
	"artDate" : "2020/12/31",
	"artTime" : "16:25:41",
	"artUrl" : "https://www.ptt.cc/bbs/creditcard/M.1609431943.A.158.html",
	"artCat" : "creditcard",
	"sentence" : "適用日期刷渣打現金回饋御璽卡不論國內或海外新增消費均享現金回饋BUT學費除外學費除外學費除外學費包含但不限於學雜費報名費書籍費校友中心或校園內相關消費補習班才藝健身課程線上課程等以消費商店所屬收單機構登記之行業代號認定為準要繳學費的請另覓別張卡",
	"origin_sentence" : "https://www.sc.com/tw/credit-cards/signaturecard.html\n適用日期:2021/1/1~2021/2/28\n\n刷渣打現金回饋御璽卡，不論國內或海外新增消費均享\n1.88%\n現金回饋！\n\nBUT\n學費除外！學費除外！學費除外！\n＊學費(包含但不限於學雜費、報名費、書籍費、校友中心或校園內相關消費、\n補習班/才藝/健身課程、線上課程等，以消費商店所屬收單機構登記之行業\n代號認定為準)\n\n\n要繳學費的請另覓別張卡......\n",
	"word" : [
		"適用",
		"日期",
		"渣打",
		"現金",
		"回饋",
		"御璽卡",
		..........
	],
	"sent" : "negative",
	"sentence_sent" : [
		{
			"sentence" : "https://www.sc.com/tw/credit-cards/signaturecard.html 適用日期:2021/1/1~2021/2/28\n",
			"sent" : "neutral"
		},
		{
			"sentence" : "刷渣打現金回饋御璽卡，不論國內或海外新增消費均享 1.88% 現金回饋！\n",
			"sent" : "neutral"
		},
		...........
	],
	"source" : "PTT"
}
```

## Dict
- type:字典種類(user_dict、stop_word、pos_dict、neg_dict)
- word:列表(array)

## Review
- artUrl:網址
- cmtStatus: 推或噓
- cmtDate : 日期
- sentence : 清除過標點符號和數字後的句子
- cmtContent : 原始的句子
- word : 斷詞的詞(array)
- sent : 情緒
- source : 資料來源
- type : 留言所屬的看板
```json
{
	"_id" : ObjectId("62e89cf1c90f3397242ebce7"),
	"artUrl" : "https://www.ptt.cc/bbs/creditcard/M.1609433994.A.6B7.html",
	"cmtStatus" : "推",
	"cmtDate" : "2021/1/1 17:53",
	"cmtContent" : ":這好像不錯！！本來想說都只有大戶2%",
	"sentence" : "這好像不錯本來想說都只有大戶",
	"word" : [
		"好像",
		"不錯",
		"大戶"
	],
	"sent" : "positive",
	"source" : "PTT",
	"type" : "creditcard"
}
```

## 常用的 Query

- DB[collection].find({條件},{選擇}) => sql 的 select from where

- DB[collection].updateOne({條件},{更新內容},) => sql 的 update，只更新一筆

- DB[collection_name].bulk_write(更新內容) => 批次更新多筆
```python
	updates = []
    for index,row in enumerate(tokenDate):
        # 每1000筆就寫入資料庫
        if ((index+1) % 1000) == 0:
            print("STARE WRITE")
			# 寫入
            DB[collection_name].bulk_write(updates)
            print("AFTER WRITE")
            updates = []
            print("CLEAN THE UPDATES")
            time.sleep(5)
		# 把update append進去 list內
        updates.append(UpdateOne({'artUrl': row['artUrl']}, {
                       '$set': row}, upsert=True))
    DB[collection_name].bulk_write(updates)
```
- DB[collection].aggregate(article_pipeline) => 一次執行一整串的query


### aggregate 內常用的query

- $match => sql 的 where 等於
- $project => sql 的 select
- $unwind => 把list拆開 
- $lookup => 做join的動作
- $set => 新增欄位
- $dateFromString => 字串to日期 

# 待做的東西 :)
- 爬蟲的東西還沒自動化，要再去爬然後去看資料有沒有在資料庫裡面