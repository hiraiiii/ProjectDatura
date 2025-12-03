import pandas as pd
from sklearn.preprocessing import LabelEncoder

sex = {
    '牡':0,
    '牝':1,
    'セ':2
    }
raceclass =  {
    'G1':10,
    'G2':9,
    'G3':8,
    '(L)':7,
    'オープン':7,
    '3勝':6,
    '1600':6,
    '2勝':5,
    '1000':5,
    '1勝':4,
    '500':4,
    '新馬':3,
    '未勝利':2,
    '障害':1
    }
details = {
    '芝':0,
    'ダート':1,
    '障害':2
    }
turns = {
    '右':0,
    '左':1,
    '直線':2,
    '芝':3
    }
condition = {
    '良':0,
    '稍':1,
    '重':2,
    '不良':3,
    '稍重':4
    }
weather = {
    '晴':0,  
    '曇':1,
    '小雨':2,
    '雨':3,
    '雪':4
    }

filepath = 'race.csv'
df = pd.read_csv(filepath,low_memory=False)
print(df.info())

# race_id、着順、年齢、オッズ、馬体重、を数値に変換
cols = ['race_id', '着順', '年齢', 'オッズ', '馬体重']
df[cols] = df[cols].apply(lambda s: pd.to_numeric(s, errors='coerce'))

# 性別を数値に変換
df['性別'] = df['性別'].map(sex)

# クラスを数値に変換
for key in raceclass.keys():
    df.loc[df['クラス'].str.contains(key, na=False), 'クラス'] = raceclass[key]
df['クラス'] = df['クラス'].apply(lambda s: pd.to_numeric(s, errors='coerce'))

# 芝ダートを数値に変換
df['芝ダート'] = df['芝ダート'].map(details)
df['芝ダート'] = df['芝ダート'].fillna(3) # NaNを障害に変換

# 回りを数値に変換
df['回り'] = df['回り'].map(turns)

# 馬場を数値に変換
df['馬場'] = df['馬場'].map(condition)

# 天気を数値に変換
df['天気'] = df['天気'].map(weather)

# 日付をdatetime型に変換
df['日付'] = pd.to_datetime(df['日付'], format='%Y/%m/%d', errors='coerce')

# 馬、騎手、レース名、開催、場所はラベルエンコーディング
label_cols = ['馬名', '騎手', 'レース名', '開催', '場名']
for col in label_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))

# 着順を1着は1、4着以下は0に変換
df['着順'] = df['着順'].apply(lambda x: 1 if x < 4 else 0)

# nanを含む行を削除
df = df.dropna()
'''
# 直近5レースのデータを追加
df = df.sort_values(by=['馬名', '日付'])
for i in range(1, 6):
    df[f'直近{i}_馬番'] = df.groupby('馬名')['馬番'].shift(i)
    df[f'直近{i}_騎手'] = df.groupby('馬名')['騎手'].shift(i)
    df[f'直近{i}_斤量'] = df.groupby('馬名')['斤量'].shift(i)
    df[f'直近{i}_オッズ'] = df.groupby('馬名')['オッズ'].shift(i)
    df[f'直近{i}_体重'] = df.groupby('馬名')['馬体重'].shift(i)
    df[f'直近{i}_体重変化'] = df.groupby('馬名')['体重変化'].shift(i)
    df[f'直近{i}_上り'] = df.groupby('馬名')['上り'].shift(i)
    df[f'直近{i}_通過順'] = df.groupby('馬名')['通過順位'].shift(i)
    df[f'直近{i}_着順'] = df.groupby('馬名')['着順'].shift(i)
    df[f'直近{i}_距離'] = df.groupby('馬名')['距離'].shift(i)
    df[f'直近{i}_クラス'] = df.groupby('馬名')['クラス'].shift(i)
    df[f'直近{i}_タイム'] = df.groupby('馬名')['タイム'].shift(i)
    df[f'直近{i}_芝ダート'] = df.groupby('馬名')['芝ダート'].shift(i)
    df[f'直近{i}_天気'] = df.groupby('馬名')['天気'].shift(i)
    df[f'直近{i}_馬場'] = df.groupby('馬名')['馬場'].shift(i)


# 日付差を追加
for i in range(1, 6):
    df[f'直近{i}_日付差'] = (df['日付'] - df.groupby('馬名')['日付'].shift(i)).dt.days # エラー

# 距離差を追加
for i in range(1, 6):
    df[f'直近{i}_距離差'] = df['距離'] - df.groupby('馬名')['距離'].shift(i) # エラー
    
# 直近5レースの平均斤量を追加
for i in range(1, 6):
    df[f'直近{i}_平均着順'] = df.groupby('馬名')[f'直近{i}_斤量'].transform('mean')  # エラー

# 騎手の勝率を追加
jockey_stats = df.groupby('騎手').agg({'着順': ['count', lambda x: (x == 1).sum()]})
jockey_stats.columns = ['total_races', 'wins']
jockey_stats['win_rate'] = jockey_stats['wins'] / jockey_stats['total_races']
df = df.merge(jockey_stats['win_rate'], on='騎手', how='left')
df.rename(columns={'win_rate': '騎手勝率'}, inplace=True)
'''

print(df.info())
print(df.isnull().sum())
df.to_csv('race_new.csv', index=False)