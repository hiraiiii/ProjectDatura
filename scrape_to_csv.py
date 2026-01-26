import scrape
import csv

race_csv = "202512_race.csv"
pay_csv = "202512pay.csv"

scrape = scrape.Scrape() # Scrapeクラスのインスタンス化
with open(race_csv, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # ヘッダー行
        writer.writerow(['race_id', '着順', '枠番', '馬番', '馬名', '性別', '年齢', '斤量', '騎手', 'タイム', '通過順位', '上り', 'オッズ', '人気', '馬体重','体重変化','レース名','日付','開催','クラス','芝ダート','距離','回り','馬場','天気','場id','場名'])
with open(pay_csv, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # ヘッダー行
        writer.writerow(['race_id','単勝','単勝払い戻し','複勝','複勝払い戻し','馬連','馬連払い戻し','ワイド','ワイド払い戻し','馬単','馬単払い戻し','三連複','三連複払い戻し','三連単','三連単払い戻し'])

scrape.scrape_race_data("2025","12","2025","12",race_csv,pay_csv, 14, "a") # 2025年12月のデータをスクレイピング