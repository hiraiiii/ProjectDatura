# スクレイピング用のモジュール
"""
scrape_race_data 指定した期間のレースデータをスクレイピングしてCSVファイルに保存する関数
scrape_today_raceid 今日のレースIDをスクレイピング
scrape_today_race 今日のレース情報をスクレイピングしてCSVファイルに保存する関数
"""
from bs4 import BeautifulSoup
import requests
import time
import random
import re
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class Scrape:
    user_agent = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    ]
    headers = {
        "User-Agent": random.choice(user_agent),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
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

    sleep_time_safety = 18 # 本番では20秒くらいにする
    sleep_time_danger = 5 # テスト用に3秒にする

    # 指定した期間のレースデータをスクレイピングしてCSVファイルに保存する関数
    def scrape_race_data(self,start_year,start_mon, end_year, end_mon, race_csv_name, pay_csv_name, endpoint, mode):

        # 2015年以降の全レースのURL
        url = 'https://db.netkeiba.com/?pid=race_list&word=&start_year=' + start_year + '&start_mon=' + start_mon + '&' + 'end_year='+ end_year + '&end_mon=' + end_mon +'&jyo%5B%5D=01&jyo%5B%5D=02&jyo%5B%5D=03&jyo%5B%5D=04&jyo%5B%5D=05&jyo%5B%5D=06&jyo%5B%5D=07&jyo%5B%5D=08&jyo%5B%5D=09&jyo%5B%5D=10&kyori_min=&kyori_max=&sort=date&list=100&page='
        race_url = "https://db.netkeiba.com" #レース詳細ページのベースURL

        for i in range(1,endpoint): # 1から372までのページをクロール
            print(f"Processing page {i}")
            """
            if i == 2: #テスト用
                continue
            """
            
            for j in range(10): # リトライ処理
                try:
                    response = requests.get(url + str(i), headers=Scrape.headers)
                except requests.exceptions.RequestException as e:
                    print(f"Request failed: {e}. Retrying ({j+1}/3)...")
                    time.sleep(300) # 300秒待ってからリトライ
                    continue
                else:
                    print("Request succeeded")
                    break
            soup1 = BeautifulSoup(response.content, 'html.parser')
            time.sleep(Scrape.sleep_time_safety)
            tds = soup1.find_all('td', class_='txt_l w_race')
            
            for td in tds:
                href = td.find('a').get('href') #レース詳細ページ一部を取得
                href = race_url + href #レース詳細ページのフルURL

                # レース詳細ページにアクセス
                for j in range(10): # リトライ処理
                    try:
                        response = requests.get(href, headers=Scrape.headers)
                    except requests.exceptions.RequestException as e:
                        print(f"Request failed: {e}. Retrying ({j+1}/3)...")
                        time.sleep(300) # 300秒待ってからリトライ
                        continue
                    else:
                        print("Request succeeded")
                        break
                
                soup2 = BeautifulSoup(response.content, 'html.parser')
                time.sleep(Scrape.sleep_time_safety)

                result_table = []

                for k,tr_tag in enumerate(soup2.select('.race_table_01 tr')):
                    if k == 0: # ヘッダー行をスキップ enumerateで行番号を取得しているので0番目をスキップ
                        continue
                    row = []

                    #日付とidを使って一意的なレースIDを作成
                    smalltxt = soup2.find('p', class_='smalltxt').text.strip().split(" ") # 日付、レース回数、場所、n日目を取得
                    calendar = smalltxt[0] # 西暦年/月/日
                    calendar = calendar[:4] # 日付から西暦を取り出す 
                    timesPlaceDate = smalltxt[1] # レース回数、場所、n日目
                    times = timesPlaceDate[:2]
                    if '回' in times:
                        times = times.replace('回', '')
                    if len(times) == 1:
                        times = '0' + times # 1桁の場合は0を付与して2桁にする
                    placeid = '00' # レース開催場所を数字に変換するための初期値
                    for id in Scrape.ids:
                        if id in timesPlaceDate: # レース開催場所を特定
                            placeid = Scrape.ids[id] # レース開催場所を数字に変換
                    date = timesPlaceDate[4:]
                    if '日目' in date:
                        date = date.replace('日目', '')
                    if len(date) == 1:
                        date = '0' + date # 1桁の場合は0を付与して2桁にする
                    racefc = soup2.find('dl', class_='racedata fc') #　何レース目かを取得
                    racefc = racefc.select('dt')
                    racefc = racefc[0].text.strip()
                    if 'R' in racefc:
                        racefc = racefc.replace('R', '')
                    if ' ' in racefc:
                        racefc = racefc.replace(' ', '')
                    if '　' in racefc:
                        racefc = racefc.replace('　', '')
                    if len(racefc) == 1:
                        racefc = '0' + racefc # 1桁の場合は0を付与して2桁にする
                    onesid = calendar + placeid + times + str(date) + str(racefc) # レースID
                    row.append(onesid) # レースIDを最初の列に追加

                    for i, data_tag in enumerate(tr_tag.select('th, td')):
                        # プレミアム限定列は除外
                        if i in [8 ,9, 15, 16, 17, 18, 19, 20]:
                            continue
                        data = data_tag.text.strip()
                        if i == 4: # 性齢列を分ける
                            sex = data[:1]
                            age = data[1:]
                            row.append(sex)
                            row.append(age)
                            continue
                        if i == 7: # タイムを秒に変換
                            if '：' in data:
                                min, sec = data.split('：')
                                data = str(int(min) * 60 + float(sec))
                            if ':' in data:
                                min, sec = data.split(':')
                                data = str(int(min) * 60 + float(sec))
                        if i == 10: # 通過順位を分割して平均する
                            ranks = data.split('-')
                            rank = sum(int(r) for r in ranks if r.isdigit()) / len(ranks)
                            row.append(rank)
                            continue
                        if i == 14: # 馬体重を分割して増減を取得
                            if '(' in data and ')' in data:
                                weight, change = data.split('(')
                                change = change.replace(')', '')
                            else:
                                weight = data
                                change = '0'
                            row.append(weight)
                            row.append(change)
                            continue
                        row.append(data) # その他の列はそのまま追加
                    # レース名、日付、開催、クラス、芝ダート、距離、回り、馬場、天候、場ID、場名を追加
                    racefc = soup2.find('dl', class_='racedata fc')
                    racename = racefc.select('h1')
                    racename = racename[0].text.strip()
                    row.append(racename) # レース名

                    smalltxt = soup2.find('p', class_='smalltxt').text.strip().split(" ")
                    calendar = smalltxt[0] # 西暦年/月/日
                    calendar = calendar.replace("年","/").replace("月","/").replace("日","")
                    row.append(calendar) # 日付

                    held = smalltxt[1] # レース回数、場所、n日目
                    row.append(held) # 開催
                    
                    raceclass = smalltxt[2] # レースクラス
                    raceclass = re.split(r'\s+', raceclass) # 空白で分割
                    raceclass = raceclass[0]
                    row.append(raceclass) # クラス

                    p = racefc.find('p').text.strip()
                    p = p.replace('/', '')
                    p = p.replace(':', '')
                    p = re.split(r'\s+', p) # 空白で分割
                    if len(p) >= 8:
                        p[0] = p[0] + p[1]
                        p.pop(1) 

                    details = p[0][:1] # 芝ダート
                    if details == 'ダ':
                        details = 'ダート'
                    row.append(details) # 芝ダート

                    distance = p[0] # 距離
                    distance = re.findall(r'\d+',distance) # 数字のみ抽出
                    row.append(distance[0]) # 距離
                    
                    direction = p[0][1:2] # 回り
                    row.append(direction) # 回り

                    # pを全て結合
                    join_string = ''
                    for plist in p:
                        join_string = join_string + plist 
                    # print(join_string)

                    # 馬場を特定
                    for condition in Scrape.condition_list:
                        if condition in join_string:
                            ture_condition = condition
                            # print(ture_condition)
                            row.append(ture_condition)
                            break
                        else:
                            ture_condition = '不明'

                    # 天気を特定
                    for weather in Scrape.weather_list:
                        if weather in join_string:
                            ture_weather = weather
                            # print(ture_weather)
                            row.append(ture_weather)
                            break
                        else:
                            ture_weather = '不明'

                    row.append(placeid) # 場ID

                    placename = smalltxt[1][2:4] # 場名
                    row.append(placename) # 場名
                    result_table.append(row)
                    

                # print(result_table)
                # CSVファイルに書き込み
                with open(race_csv_name, mode=mode, newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    # データ本体
                    writer.writerows(result_table)
                


                # 払い戻しテーブルを取得
                pay_table = []
                pays = soup2.select(".pay_table_01")
                row2 = [] # レースIDを最初の列に追加
                row2.append(onesid)
                for pay in pays:
                    for tr_tag in pay.select('tr'):
                        for j, data_tag in enumerate(tr_tag.select('th, td')):
                            if j in [0,3]: # 項目名はスキップ
                                continue
                            data = data_tag.get_text(" ").strip()

                            row2.append(data)
                
                pay_table.append(row2)
                # print(pay_table)
                


                with open(pay_csv_name, mode=mode, newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    # データ本体
                    writer.writerows(pay_table)
    
    # 今日のレースIDをスクレイピングする関数
    def scrape_today_raceid(self,race_date):
        kaisai_url =  'https://race.netkeiba.com/top/?kaisai_date=' #今日のレース一覧ページURL

        # Seleniumの処理
        driver = webdriver.Chrome()
        wait = WebDriverWait(driver, Scrape.sleep_time_safety)
        for i in range(10): # リトライ処理
            try:
                driver.get(kaisai_url + race_date) # 本番ではkaisai_url + todayにする
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#RaceTopRace')))
                soup1 = BeautifulSoup(driver.page_source, 'lxml')
                race_ids = []

                for a_tag in soup1.select('.RaceList_DataItem > a:first-of-type'):
                    race_id = re.search(r'race_id=(.+)&', a_tag.get('href')).group(1)
                    print(race_id) # デバッグ用
                    race_ids.append(race_id)
                break
            except Exception as e:
                print(f"Selenium request failed: {e}. Retrying ({i+1}/10)...")
                time.sleep(30) # 300秒待ってからリトライ
        # Seleniumの終了
        driver.quit()
        return race_ids
    
    # 今日のレース情報をスクレイピングしてCSVファイルに保存する関数
    def scrape_today_race(self,race_ids):

        race_url = 'https://race.netkeiba.com/race/shutuba.html?race_id='
        race_url2 = '&rf=race_list'
        today = time.strftime("%Y%m%d") # 今日の日付をYYYYMMDD形式で取得
        today_csv = today + "_race.csv"
        # 今日のCSVファイルのヘッダー行を書き込み
        with open(today_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # ヘッダー行
            writer.writerow(['race_id', '着順', '枠番', '馬番', '馬名', '性別', '年齢', '斤量', '騎手', 'タイム', '通過順位', '上り', 'オッズ', '人気', '馬体重','体重変化','レース名','日付','開催','クラス','芝ダート','距離','回り','馬場','天気','場id','場名'])

        # Seleniumの処理
        driver = webdriver.Chrome()
        wait = WebDriverWait(driver, Scrape.sleep_time_safety)
        # beautifulsoupでレース情報をスクレイピング

        for race_id in race_ids:
            for k in range(10): # リトライ処理
                try:
                    driver.get(race_url + race_id + race_url2)
                    wait = WebDriverWait(driver, Scrape.sleep_time_safety)
                    print("レースのリンク:" + race_url + race_id + race_url2)  # デバッグ用

                except Exception as e:
                    print(f"Request failed: {e}. Retrying ({k+1}/10)...")
                    time.sleep(30) # 300秒待ってからリトライ
                    continue
                else:
                    # print("Request succeeded")
                    break
            soup2 = BeautifulSoup(driver.page_source, 'html.parser') # レース情報のスクレイピング
            
            time.sleep(Scrape.sleep_time_danger)

            result_table = []
            div = soup2.find('div',class_="RaceTableArea")

            for g,tr in enumerate(div.select('tr', class_="HorseList")):
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
                                response = requests.get(link, headers=Scrape.headers)
                            except Exception as e:
                                print(f"ジョッキーのページのリクエスト失敗: {e}. Retrying ({j+1}/10)...")
                                time.sleep(300) # 300秒待ってからリトライ
                                continue
                            else:
                                # print("ジョッキーのページのリクエスト成功")
                                break
                        soup_jockey = BeautifulSoup(response.content, 'html.parser')
                        time.sleep(Scrape.sleep_time_danger)
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
                for condition in Scrape.condition_list:
                    if condition in race_data_01_all:
                        row.append(condition) # 馬場
                        break
                    else:
                        condition = '不明' # 見つからなかった場合
                # 天候をweather_listから判定して追加
                for weather in Scrape.weather_list:
                    if weather in race_data_01_all:
                        row.append(weather) # 天気
                        break
                    else:
                        weather = "不明" # 見つからなかった場合

                # 場IDと場名をidsから判定して追加
                for id in Scrape.ids:
                    if id in raceData02[1]:
                        row.append(Scrape.ids[id]) # 場ID
                        row.append(id) # 場名

                print(row)
                result_table.append(row)

            with open(today_csv, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # データ本体
                writer.writerows(result_table)
        driver.quit() # Seleniumの終了
        return today_csv # 今日のデータが入ったCSVファイル名を返す