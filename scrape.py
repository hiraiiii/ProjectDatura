from bs4 import BeautifulSoup
import requests
import time
import random
import re
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
# 2015年以降の全レースのURL
url = 'https://db.netkeiba.com/?pid=race_list&word=&start_year=2015&start_mon=none&end_year=none&end_mon=none&jyo%5B%5D=01&jyo%5B%5D=02&jyo%5B%5D=03&jyo%5B%5D=04&jyo%5B%5D=05&jyo%5B%5D=06&jyo%5B%5D=07&jyo%5B%5D=08&jyo%5B%5D=09&jyo%5B%5D=10&kyori_min=&kyori_max=&sort=date&list=100&page='
race_url = "https://db.netkeiba.com" #レース詳細ページのベースURL

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

with open("pay.csv", mode="a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    # ヘッダー行
    writer.writerow(['race_id','単勝','単勝払い戻し','複勝','複勝払い戻し','馬連','馬連払い戻し','ワイド','ワイド払い戻し','馬単','馬単払い戻し','三連複','三連複払い戻し','三連単','三連単払い戻し'])
with open("race.csv", mode="a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    # ヘッダー行
    writer.writerow(['race_id', '着順', '枠番', '馬番', '馬名', '性別', '年齢', '斤量', '騎手', 'タイム', '通過順位', '上り', 'オッズ', '人気', '馬体重','体重変化','レース名','日付','開催','クラス','芝ダート','距離','回り','馬場','天気','場id','場名'])

for i in range(1,373): # 1から372までのページをクロール
    print(f"Processing page {i}")
    """
    if i == 2: #テスト用
        continue
    """
    
    for j in range(10): # リトライ処理
        try:
            response = requests.get(url + str(i), headers=headers)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Retrying ({j+1}/3)...")
            time.sleep(300) # 300秒待ってからリトライ
            continue
        else:
            print("Request succeeded")
            break
    soup1 = BeautifulSoup(response.content, 'html.parser')
    time.sleep(sleep_time)
    tds = soup1.find_all('td', class_='txt_l w_race')
    
    for td in tds:
        href = td.find('a').get('href') #レース詳細ページ一部を取得
        href = race_url + href #レース詳細ページのフルURL

        # レース詳細ページにアクセス
        for j in range(10): # リトライ処理
            try:
                response = requests.get(href, headers=headers)
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}. Retrying ({j+1}/3)...")
                time.sleep(300) # 300秒待ってからリトライ
                continue
            else:
                print("Request succeeded")
                break
        
        soup2 = BeautifulSoup(response.content, 'html.parser')
        time.sleep(sleep_time)

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
            for id in ids:
                if id in timesPlaceDate: # レース開催場所を特定
                    placeid = ids[id] # レース開催場所を数字に変換
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
            h1 = racefc.select('h1')
            h1 = h1[0].text.strip()
            row.append(h1) # レース名

            smalltxt = soup2.find('p', class_='smalltxt').text.strip().split(" ")
            calendar = smalltxt[0] # 西暦年/月/日
            calendar = calendar.replace('年', '/') # 日付の/を-に変換
            calendar = calendar.replace('月', '/')
            calendar = calendar.replace('日', '')
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
            print(join_string)

            # 馬場を特定
            for condition in condition_list:
                if condition in join_string:
                    ture_condition = condition
                    print(ture_condition)
                    row.append(ture_condition)
                    break
                else:
                    ture_condition = '不明'

            # 天気を特定
            for weather in weather_list:
                if weather in join_string:
                    ture_weather = weather
                    print(ture_weather)
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
        with open("race.csv", mode="a", newline="", encoding="utf-8") as f:
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
        


        with open("pay.csv", mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # データ本体
            writer.writerows(pay_table)








    