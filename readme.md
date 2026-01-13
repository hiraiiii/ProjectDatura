プロジェクトの概要
このプロジェクトは機械学習で競馬の着順を予想するためのものです。netkeibaをスクレイピングしてデータセットを入手しています。

スクリプトの説明

スクレイピング関係
scrape.py netkeibaをスクレイピングして、データセットを作る関数
scrape_to_csv.py　10年分のデータセットを取得する
update_scrape.py scrape.pyでデータセットをアップデートする


arrange_csv.py データセットの数値化と特徴量を増やす
train.py モデルをトレーニングする
datura.py 最新のレース情報を取得してlgbm_modelで予想する

CSVファイルの説明
pay.csv 払い戻しのデータセット　原文
race.csv レース情報のデータセット　原文
race_new.csv レース情報を数値化し、特徴量を増やしたもの

lgbm_model.text トレーニングした機械学習モデル