import lightgbm as lgb
import pandas as pd
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

x = data.drop(columns=['race_id', '着順', '日付', 'タイム', '通過順位', '上り', '場名']) # 目的変数と不要な列を除外
y = data['着順']

# データの分割
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

# ハイパーパラメータの設定
params = {
    'objective': 'binary',
    'metric': 'auc',
    'is_unbalance': True,  # 自動でクラス重みを調整
}

# モデルの訓練
train_data = lgb.Dataset(x_train, label=y_train)
test_data = lgb.Dataset(x_test, label=y_test)
model = lgb.train(params, train_set=train_data, valid_sets=test_data)

# モデルの保存
model.save_model('lgbm_model.txt')

# テストデータの予測
y_pred = model.predict(x_test)
y_pred_binary = [1 if pred > 0.88 else 0 for pred in y_pred] # 二値化


# 評価指標の計算
accuracy = accuracy_score(y_test, y_pred_binary)
precision = precision_score(y_test, y_pred_binary)
recall = recall_score(y_test, y_pred_binary)
f1 = f1_score(y_test, y_pred_binary)
roc_auc = roc_auc_score(y_test, y_pred)
# 結果の表示
print(f'正解率: {accuracy}')
print(f'適合率: {precision}')
print(f'再現率: {recall}')
print(f'F値: {f1}')
print(f'AUC: {roc_auc}')

# 回収率の計算
test_results = x_test.copy()
test_results['actual'] = y_test
test_results['predicted'] = y_pred_binary
test_results['odds'] = data.loc[test_results.index, 'オッズ']  # 元のデータからオッズを取得

bet_amount = 100
total_bets = len(test_results[test_results['predicted'] == 1])  # 賭けた回数
total_investment = total_bets * bet_amount                     # 投資金額
total_returns = (test_results[(test_results['predicted'] == 1) & (test_results['actual'] == 1)]['odds'] * bet_amount).sum()

# 回収率（%）
return_rate = (total_returns / total_investment * 100) if total_investment > 0 else 0

print(f'投資金額: {total_investment}')
print(f'払い戻し: {total_returns}')
print(f'回収率: {return_rate:.2f}%')


# 特徴量重要度のプロット
lgb.plot_importance(model, max_num_features=20)
plt.show()