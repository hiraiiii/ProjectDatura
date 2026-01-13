
import pandas as pd
import lightgbm as lgb

# 今日のレース情報をスクレイピングするモジュールをインポート
from create_data import scrape_today
# CSVを整形するモジュールをインポート
import arrange_csv

# 今日のレース情報をスクレイピングしてCSVに保存
today_csv = scrape_today.scrape_today_race()

# today_csvにrace.csvをコピー
df_today = pd.read_csv('race.csv', low_memory=False) # race.csvを読み込み
df_today.to_csv(today_csv, index=False) # race.csvに保存

# today_race.csvにarrange_csv.pyの処理を実行
new_today_csv = arrange_csv.arrange_csv(today_csv)

# lgbm_modelで予測を実行
model = lgb.Booster(model_file='lgbm_model.txt')
data = pd.read_csv(new_today_csv)
x = data.drop(columns=['race_id', '着順', '日付', 'タイム', '通過順位', '上り', '場名']) # 目的変数と不要な列を除外
y_pred = model.predict(x)
y_pred_binary = [1 if pred > 0.88 else 0 for pred in y_pred] # 二値化
data['predicted'] = y_pred_binary
data['prediction_score'] = y_pred
data.to_csv('prediction_' + new_today_csv, index=False)
print(f"Predictions saved to prediction_{new_today_csv}")
