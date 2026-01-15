import re
from bs4 import BeautifulSoup
import random
import requests
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def scrape_today_race(race_date):
    user_agent = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    ]
    headers = {
        "User-Agent": random.choice(user_agent),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    kaisai_url =  'https://race.netkeiba.com/top/?kaisai_date=' #今日のレース一覧ページURL
    race_url = 'https://race.netkeiba.com/race/shutuba.html?race_id='
    race_url2 = '&rf=race_list'

    today_csv = race_date + "_race.csv"

    ids = {
        '札幌': '01',
        '函館': '02',
        '福島': '03',
        '新潟': '04',
        '東京': '05',
        '中山': '06',
        '中京': '07',
        '京都': '08',
        '阪神': '09',
        '小倉': '10'
    }
    condition_list = ['不良', '稍重', '稍', '重', '良']
    weather_list = ['小雨', '晴', '曇', '雨', '雪']

    sleep_time = 20 # 本番では20秒くらいにする

    with open(today_csv, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # ヘッダー行
        writer.writerow(['race_id', '着順', '枠番', '馬番', '馬名', '性別', '年齢', '斤量', '騎手', 'タイム', '通過順位', '上り', 'オッズ', '人気', '馬体重','体重変化','レース名','日付','開催','クラス','芝ダート','距離','回り','馬場','天気','場id','場名'])

    # Seleniumの処理
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    for i in range(10): # リトライ処理
        try:
            driver.get(kaisai_url + race_date) # 本番ではkaisai_url + todayにする
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#RaceTopRace')))
            soup1 = BeautifulSoup(driver.page_source, 'lxml')
            page_source = driver.page_source
            race_ids = []

            for a_tag in soup1.select('.RaceList_DataItem > a:first-of-type'):
                race_id = re.search(r'race_id=(.+)&', a_tag.get('href')).group(1)
                print(race_id) # デバッグ用
                race_ids.append(race_id)
            break
        except Exception as e:
            print(f"Selenium request failed: {e}. Retrying ({i+1}/10)...")
            time.sleep(30) # 300秒待ってからリトライ

    # beautifulsoupでレース情報をスクレイピング

    for race_id in race_ids:
        for k in range(10): # リトライ処理
            try:
                driver.get(race_url + race_id + race_url2)
                wait = WebDriverWait(driver, 10)
                print("レースのリンク:" + race_url + race_id + race_url2)  # デバッグ用

            except Exception as e:
                print(f"Request failed: {e}. Retrying ({k+1}/10)...")
                time.sleep(30) # 300秒待ってからリトライ
                continue
            else:
                # print("Request succeeded")
                break
        soup2 = BeautifulSoup(driver.page_source, 'html.parser') # レース情報のスクレイピング
        
        time.sleep(sleep_time)

        result_table = []
        div = soup2.find_all('div',class_="RaceTableArea")

        for g,tr in enumerate(div[0].select('tr', class_="HorseList")):
            row = []
            if g in [0,1]: # ヘッダー行と不要行をスキップ
                continue
            row.append(race_id) # race_idを追加

            order = 0 # 着順は取得できないので0を初期値に設定
            row.append(order)

            for num,td in enumerate(tr.select('td')):
                if num in [2, 7, 9, 10, 11 ,12 ,13, 14]: # 不要な列をスキップ
                    continue
                data = td.get_text(strip=True)
                if num == 4: # 性齢列を分ける
                    sex = data[:1]
                    age = data[1:]
                    row.append(sex)
                    row.append(age)
                    continue
                if num == 6: # 騎手の名前を別のページから取得
                    link = td.find('a').get('href') # 騎手のリンクを取得
                    # print("ジョッキーのリンク" + link) # デバッグ用
                    for j in range(10): # リトライ処理
                        try:
                            response = requests.get(link, headers=headers)
                        except Exception as e:
                            print(f"ジョッキーのページのリクエスト失敗: {e}. Retrying ({j+1}/10)...")
                            time.sleep(300) # 300秒待ってからリトライ
                            continue
                        else:
                            # print("ジョッキーのページのリクエスト成功")
                            break
                    soup_jockey = BeautifulSoup(response.content, 'html.parser')
                    time.sleep(sleep_time)
                    jockey_name = soup_jockey.find('div', class_='Name')
                    jockey_name = jockey_name.find("h1").get_text().strip()
                    jockey_name = re.split(r'\s+', jockey_name)[0] # 名前だけ取得
                    row.append(jockey_name) 
                    times = 0 #タイムは0を初期値に設定
                    row.append(times)
                    ranks = 0 # 通過順位は0を初期値に設定
                    row.append(ranks)
                    up = 0 # 上りは0を初期値に設定
                    row.append(up)
                    try:
                        odds = tr.find("td", class_="Txt_R Popular").get_text().strip() # オッズを取得
                        row.append(odds) # オッズを追加
                    except:
                        row.append('0') # オッズがない場合は0を追加
                    try:
                        popularity = tr.find_all("td", class_=re.compile("^Popular Popular_Ninki"))[0].get_text().strip() # 人気を取得
                        row.append(popularity) # 人気を追加
                    except:
                        row.append('0') # 人気がない場合は0を追加
                    continue
                if num == 8: # 馬体重を分割して増減を取得
                    try:
                        if '(' in data:
                            weight, change = data.split('(') # 馬体重と増減を分割
                            change = change.replace(')', '') # 増減の)を削除
                        elif '-' in data:
                            data = '0'
                            change = '0'
                        else:
                            weight = data
                            change = '0'
                        row.append(weight)
                        row.append(change)
                        continue
                    except:
                        row.append('0')
                        row.append('0')
                        continue
                row.append(data)# 他のデータはそのまま追加
            # レース名、日付、開催、クラス、芝ダート、距離、回り、馬場、天候、場ID、場名を追加
            racename = soup2.find("h1", class_="RaceName").get_text().strip() # レース名
            row.append(racename)

            calendar = soup2.find("meta", attrs={"name":"description"}).get("content").strip() # 日付
            calendar = calendar.split(" ")[0]
            calendar = calendar.replace("年","/").replace("月","/").replace("日","")
            row.append(calendar)

            raceData02 = soup2.find("div", class_="RaceData02").get_text().strip() # 開催、クラス、芝ダート、距離、回り
            raceData02 = re.split(r'\s+', raceData02)
            row.append(raceData02[0]+raceData02[1]+raceData02[2]) # 開催
            # print(RaceData02) # デバッグ用
            row.append(raceData02[3]+raceData02[4]) # クラス

            raceData01 = soup2.find("div", class_="RaceData01").get_text().strip() # 芝ダート、距離、天候、場ID、馬場
            raceData01 = re.split(r'\s+', raceData01)
            # print(raceData01) # デバッグ用

            details = raceData01[2][:1] # 芝ダート
            if details == 'ダ':
                details = 'ダート'
            row.append(details) # 芝ダート

            distance = raceData01[2] # 距離
            distance = re.findall(r'\d+', distance)[0] # 数字だけ抽出
            row.append(distance)

            trun = raceData01[3][1:2] # 回り
            row.append(trun)
            
            #racedata01を全て結合
            race_data_01_all = ''
            for data in raceData01:
                race_data_01_all += data

            # 馬場をcondition_listから判定して追加
            for condition in condition_list:
                if condition in race_data_01_all:
                    row.append(condition) # 馬場
                    break
                else:
                    condition = '不明' # 見つからなかった場合
            # 天候をweather_listから判定して追加
            for weather in weather_list:
                if weather in race_data_01_all:
                    row.append(weather) # 天気
                    break
                else:
                    weather = "不明" # 見つからなかった場合

            # 場IDと場名をidsから判定して追加
            for id in ids:
                if id in raceData02[1]:
                    row.append(ids[id]) # 場ID
                    row.append(id) # 場名

            print(row)
            result_table.append(row)

        with open(today_csv, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # データ本体
            writer.writerows(result_table)
    driver.quit() # Seleniumの終了
    return today_csv # 今日のデータが入ったCSVファイル名を返す