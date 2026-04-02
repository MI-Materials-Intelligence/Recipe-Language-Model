
import pandas as pd
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error
import numpy as np
import joblib

train = pd.read_csv('df_20250612_FF_xgb_train_538.csv')
test = pd.read_csv('df_20250612_FF_xgb_test_538.csv')

X_train = train.iloc[:,2:-2]
y_train = train.iloc[:,-2]
X_test = test.iloc[:,2:-2]
y_test = test.iloc[:,-2]

col = X_train.columns.tolist()
joblib.dump(col, 'xgb_col_FF.pkl')

std = StandardScaler()
X_fit = std.fit(X_train)
joblib.dump(std, "xgb_scaler_FF.pkl")
X_train_std = X_fit.transform(X_train)
X_test_std = X_fit.transform(X_test)

#{'learning_rate': 0.05, 'max_depth': 7, 'n_estimators': 200}
xgb = XGBRegressor(
    learning_rate=0.05,
    max_depth=7,
    n_estimators=200,
    random_state=0,
    eval_metric='rmse',
    subsample=0.8,
    colsample_bytree=0.8,
)

xgb.fit(X_train_std, y_train)
joblib.dump(xgb, "xgb_model_FF.pkl")
y_train_pred = xgb.predict(X_train_std)
y_test_pred = xgb.predict(X_test_std)

k = 5
train_r2 = r2_score(y_train, y_train_pred)
train_mse = mean_squared_error(y_train, y_train_pred)
cv_r2 = np.mean(cross_val_score(xgb, X_train_std, y_train, cv=k, scoring='r2'))
cv_mse = -np.mean(cross_val_score(xgb, X_train_std, y_train, cv=k, scoring='neg_mean_squared_error'))
test_r2 = r2_score(y_test, y_test_pred)
test_mse = mean_squared_error(y_test, y_test_pred)

print(f'train_r2: {train_r2:.4f}')
print(f'train_mse: {train_mse:.4f}')
print(f'cv_r2: {cv_r2:.4f}')
print(f'cv_mse: {cv_mse:.4f}')
print(f'test_r2: {test_r2:.4f}')
print(f'test_mse: {test_mse:.4f}')