#race.csvアップデートするファイル　未完成
import scrape
import csv

scrape = scrape.Scrape() # Scrapeクラスのインスタンス化
update_race_csv = "update_race.csv"
scrape.scrape_race_data("2025","10","2025","12",update_race_csv,"update_pay.csv", 43, "w") # スクレイピング実行

with open("race.csv", newline="", encoding="utf-8") as src, open(update_race_csv, mode="a", newline="", encoding="utf-8") as dst:
    reader = csv.reader(src) # 元ファイルを読む
    writer = csv.writer(dst) # 書き込み用ファイルを開く
    for row in reader:
        if reader.line_num == 1:
            continue # ヘッダー行をスキップ
        writer.writerow(row)
