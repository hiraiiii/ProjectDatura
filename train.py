import lightgbm as lgb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score

# 日本語フォント設定
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic',
 'Meirio', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']


# データの読み込み
data = pd.read_csv('race_new.csv')

x = data.drop(columns=['race_id', '着順', '日付']) # 目的変数と不要な列を除外
y = data['着順']

# データの分割
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

# ハイパーパラメータの設定
params = {
    'objective': 'binary',
    'metric': 'binary_error',

}

# モデルの訓練
train_data = lgb.Dataset(x_train, label=y_train)
test_data = lgb.Dataset(x_test, label=y_test)
model = lgb.train(params, train_set=train_data, valid_sets=test_data)

# モデルの保存
model.save_model('lgbm_model.txt')

# テストデータの予測
y_pred = model.predict(x_test)
y_pred_binary = [1 if pred > 0.8 else 0 for pred in y_pred] # しきい値0.8で二値化


# 評価指標の計算
accuracy = accuracy_score(y_test, y_pred_binary)
precision = precision_score(y_test, y_pred_binary,average="micro")
recall = recall_score(y_test, y_pred_binary,average="micro")
f1 = f1_score(y_test, y_pred_binary,average="micro")
roc_auc = roc_auc_score(y_test, y_pred_binary)


print(f'正解率: {accuracy}')
print(f'適合率: {precision}')
print(f'再現率: {recall}')
print(f'F値: {f1}')
print(f'AUC: {roc_auc}')

# 特徴量重要度のプロット
lgb.plot_importance(model, max_num_features=20)
plt.show()