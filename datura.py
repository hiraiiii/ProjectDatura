import pandas as pd
import numpy as np
import lightgbm as lgb
from bs4 import BeautifulSoup
import random
import requests
import time
import csv

user_agent = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
]
headers = {
    "User-Agent": random.choice(user_agent),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}
url =  'https://race.netkeiba.com/top/race_list.html?kaisai_date=' #今日のレース一覧ページURL
base_url = "https://db.netkeiba.com" #netkeibaのベースURL
today = time.strftime('%Y%m%d') # 今日の日付を取得
print(f"Today's date: {today}")

sleep_time = 20 # 本番では20秒くらいにする

with open("today_race.csv", mode="a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    # ヘッダー行
    writer.writerow(['race_id', '着順', '枠番', '馬番', '馬名', '性別', '年齢', '斤量', '騎手', 'タイム', '通過順位', '上り', 'オッズ', '人気', '馬体重','体重変化','レース名','日付','開催','クラス','芝ダート','距離','回り','馬場','天気','場id','場名'])

for i in range(10): # リトライ処理
    try:
        response = requests.get(url + today, headers=headers)
        break
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}. Retrying ({i+1}/10)...")
        time.sleep(300) # 300秒待ってからリトライ

# レース一覧ページを取得
soup1 = BeautifulSoup(response.content, 'html.parser')
time.sleep(sleep_time)

race_links = soup1.find_all('dd', class_='RaceList_Data')

for race in race_links:
    race_url = base_url + race.find('a')['href']

    for j in range(10): # リトライ処理
        try:
            race_response = requests.get(race_url, headers=headers)
            break
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Retrying ({j+1}/10)...")
            time.sleep(300) # 300

    # レース詳細ページを取得
    soup2 = BeautifulSoup(race_response.content, 'html.parser')
    time.sleep(sleep_time)

    race_table = []

    

    



