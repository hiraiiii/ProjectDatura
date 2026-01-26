import lightgbm as lgb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score

# 日本語フォント設定
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic',
 'Meirio', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

def fbeta(p, r, beta=1):
    if p == 0 and r == 0:
        return 0
    return (1 + beta**2) * p * r / (beta**2 * p + r)


# データの読み込み
df = pd.read_csv('newrace.csv')

cat_cols = ['芝ダート', 'クラス', '天気', '場id'] # 馬名は慎重に（過学習の恐れあり）
# 特徴量候補
features = df.drop(['race_id', '着順', '日付', 'タイム', '通過順位', '上り', 'オッズ', '場名'], axis=1).columns.tolist()

# データの分割
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=0)
groups = df['race_id']
train_idx, test_idx = next(gss.split(df, groups=groups))
x_train = df.loc[train_idx, features]
y_train = df.loc[train_idx, '着順'] # 着順は0かに変換済み
x_test = df.loc[test_idx, features]
y_test = df.loc[test_idx, '着順']

# ハイパーパラメータの設定
params = {
    'objective': 'binary',
    'metric': 'auc',
    'is_unbalance': True, # 自動でクラス重みを調整
    'learning_rate': 0.05, # 学習率
    'num_leaves': 31, # 葉の数
    'seed': 0 # 乱数シード
}

# モデルの訓練
train_data = lgb.Dataset(x_train, label=y_train, categorical_feature=[c for c in cat_cols if c in features])
test_data = lgb.Dataset(x_test, label=y_test, categorical_feature=[c for c in cat_cols if c in features])
model = lgb.train(params, train_set=train_data, valid_sets=[test_data], num_boost_round=1000, callbacks=[lgb.early_stopping(stopping_rounds=50), lgb.log_evaluation(period=50)])

# モデルの保存
model.save_model('lgbm_model2.txt')

# テストデータの予測
y_pred = model.predict(x_test)


# 最適な閾値の探索
thresholds = np.linspace(0.01, 0.99, 99)
best_thr = 0
best_score = -1

for thr in thresholds:
    pred = (y_pred > thr).astype(int)
    p = precision_score(y_test, pred, zero_division=0)
    r = recall_score(y_test, pred, zero_division=0)
    score = fbeta(p, r, beta=0.5)  # Precision重視なら0.5、Recall重視なら2

    if score > best_score:
        best_score = score
        best_thr = thr

print("最適閾値:", best_thr)
print("スコア:", best_score)


y_pred_binary = (y_pred > best_thr).astype(int)



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
test_results['odds'] = df.loc[test_results.index, 'オッズ']  # 元のデータからオッズを取得

bet_amount = 100
total_bets = len(test_results[test_results['predicted'] == 1])  # 賭けた回数
total_investment = total_bets * bet_amount # 投資金額
total_returns = (test_results[(test_results['predicted'] == 1) & (test_results['actual'] == 1)]['odds'] * bet_amount).sum() # 払い戻し金額

# 回収率（%）
return_rate = (total_returns / total_investment * 100) if total_investment > 0 else 0

print(f'データ数: {len(test_results)}')
print(f'賭けた回数: {total_bets}')
print(f'投資金額: {total_investment}')
print(f'払い戻し: {total_returns}')
print(f'回収率: {return_rate:.2f}%')

# 特徴量重要度のプロット
lgb.plot_importance(model, max_num_features=20)
plt.show()