
import pandas as pd
import lightgbm as lgb
import time
import csv
import os

# 今日のレース情報をスクレイピングするモジュールをインポート
from create_data import scrape_today
# CSVを整形するモジュールをインポート
import arrange_csv

start = time.time()

# 今日のレース情報をスクレイピングしてCSVに保存
#today_csv = scrape_today.scrape_today_race("20260111") # 引数にスクレイピングしたい日付をYYYYMMDD形式で指定
today_csv = "202512_race.csv" # テスト用に固定のCSVを使う
"""""
# today_csvにrace.csvをコピー
with open("race.csv", newline="", encoding="utf-8") as src, open(today_csv, mode="a", newline="", encoding="utf-8") as dst:
    reader = csv.reader(src)
    writer = csv.writer(dst)
    for row in reader:
        if reader.line_num == 1:
            continue # ヘッダー行をスキップ
        writer.writerow(row)
"""""
# today_race.csvにarrange_csv.pyの処理を実行
new_today_csv = arrange_csv.arrange_csv(today_csv)
#new_today_csv = "new" + today_csv # テスト用に固定のCSV

# race.csvからレースIDのデータを抽出してnew_today_csvから削除
race_csv_data = pd.read_csv("newrace.csv")
race_ids = race_csv_data['race_id'].unique().tolist() # race.csvのrace_idをリスト化
data = pd.read_csv(new_today_csv)
data = data[~data['race_id'].isin(race_ids)] # race_idがrace.csvに存在する行を削除
data.to_csv(new_today_csv, index=False)

# lgbm_modelで予測を実行
model = lgb.Booster(model_file='lgbm_model2.txt')
data = pd.read_csv(new_today_csv)

x = data.drop(
    columns=['race_id', '着順', '日付', 'タイム', '通過順位', '上り', 'オッズ', '場名'],
    axis=1
)

y_pred = model.predict(x)
y_pred_binary = [1 if pred > 0.7100000000000001 else 0 for pred in y_pred] # 二値化
data['predicted'] = y_pred_binary
data['prediction_score'] = y_pred
data.to_csv('prediction_' + today_csv, index=False)
print(f"Predictions saved to prediction_{today_csv}")
"""""
# 回収率の計算
total_bets = 0
total_returns = 0
for index, row in data.iterrows():
    if row['predicted'] == 1:
        total_bets += 100 # 100円ず
        if row['着順'] == 1:
            total_returns += row['オッズ'] * 100 # 的中した場合の払い戻し金額を加算
if total_bets > 0:
    return_rate = (total_returns / total_bets) * 100
else:
    return_rate = 0
print(f"ベット金額: {total_bets}円")
print(f"リターン: {total_returns}円")
print(f"回収率: {return_rate}%")
"""""

# 予測結果の表示
for index, row in data.iterrows():
    if row['predicted'] == 1:
        print(f"場id: {str(row['race_id'])[4:6]}, レース: {str(row['race_id'])[10:12]}, 馬番: {row['馬番']}, Prediction Score: {row['prediction_score']}")

# スクレイピングと予測にかかった時間を表示
end = time.time()
elapsed = end - start # 経過時間を計算
elapsed = elapsed / 60 / 60 # 時間に変換
print(f"かかった時間は {elapsed} だよ") # スクレイピングにかかった時間を表示

# 処理が終わったことを音声で知らせる(macOSのみ)
os.system('say "おわったにゃん！"') # ←かわいい