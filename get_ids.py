from create_data import scrape
import numpy as np

race_data = "20260125" # スクレイピングしたい日付をYYYYMMDD形式で指定
scrape = scrape.Scrape() # Scrapeクラスのインスタンス化
ids = scrape.scrape_today_raceid(race_data) # 今日のレースIDをスクレイピング

arrays = [[]]*12 # レースIDを12個ずつの配列に変換

print(ids)
for i in range(len(arrays)):
    for id in ids: # 各レースIDについてループ
        if int(id[-2:]) == i: # レース番号が一致するか確認
            print(id)
            arrays[i].append(id) # レース番号に応じて配列に追加

# テキストファイルに書き込み
with open("race_ids.txt", "w", encoding="utf-8") as f:
    f.write(f"{arrays}")

        
"""""
# テキストファイルに書き込み
with open("race_ids.txt", "w", encoding="utf-8") as f:
    for race_id in ids:
        if race_id[-2:] == "01": # レース番号が01のとき
            f.write(f"{race_id[4:6]}\n") # 場名ごとに改行を入れる
        f.write(f"\"{race_id}\"\n") # レースIDを書き込み
"""""