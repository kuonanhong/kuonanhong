import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
import joblib

data = pd.read_csv("data/merged_spike_periods_vcm3_ft509_edc_corrected.csv", parse_dates=['time'])
data['time'] = pd.to_datetime(data['time'])
data.replace('No Data', np.nan, inplace=True)

variables = ['EDC', 'LVCM2-FC503F', 'LVCM-TI-C503A-I.PV', 'LVCM2-FC503AS.PV', 'LVCM2-TC503T', 'LVCM2-TC503B',
             'LVCM-PI-C503A-T.PV', 'LVCM-PI-C503A-B.PV', 'LVCM2-LC503']
data[variables] = data[variables].apply(pd.to_numeric, errors='coerce')
data.fillna(method='ffill', inplace=True)
data.fillna(method='bfill', inplace=True)

def smooth_data(df, window=5):
    datetime_col = df['time']
    df_numeric = df.drop(columns=['time'])
    df_smoothed = df_numeric.rolling(window=window, min_periods=1).mean()
    df_smoothed['time'] = datetime_col
    return df_smoothed

data = smooth_data(data)

time_intervals = [
    ["2022-08-26 16:40:00", "2022-11-07 13:00:00"],
    ["2023-12-22 16:50:00", "2024-03-01 15:40:00"]
]

def train_and_evaluate_rf(data):
    X = data.drop(columns=['EDC', 'time'])
    y = data['EDC']

    # Use the first 90% of the data for the entire process
    data_size = int(len(X) * 0.9)
    X, y = X[:data_size], y[:data_size]
    end_time = data['time'].iloc[data_size - 1].strftime('%Y-%m-%d %H:%M:%S')  # 将end_time格式化为字符串
    print ("end_time: ", end_time)

    # Split data into training and testing sets using random split (80% training, 20% testing)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize RandomForest model
    rf = RandomForestRegressor(n_estimators=100, random_state=42)

    # Train model
    rf.fit(X_train, y_train)

    # Predict
    y_pred_train = rf.predict(X_train)
    y_pred_test = rf.predict(X_test)

    # Calculate R2 scores
    r2_train = r2_score(y_train, y_pred_train)
    r2_test = r2_score(y_test, y_pred_test)

    return r2_train, r2_test, rf, end_time

def save_best_model(best_model, interval, end_time):
    start, _ = interval
    model_filename = f'file/RF_model_{start}_{end_time}.joblib'
    joblib.dump(best_model, model_filename)
    print ("best_model: ", best_model)
    print(f'Model saved: {model_filename}')

def plot_best_model_results(data, interval, best_model, interval_index, best_r2_train, best_r2_test):
    interval_data = data[(data['time'] >= interval[0]) & (data['time'] <= interval[1])].reset_index(drop=True)
    X = interval_data.drop(columns=['EDC', 'time'])
    y = interval_data['EDC']

    # Use the first 90% of the data for the entire process
    data_size = int(len(X) * 0.9)
    X, y = X[:data_size], y[:data_size]

    # Split data into training and testing sets using random split (80% training, 20% testing)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    y_pred_train = best_model.predict(X_train)
    y_pred_test = best_model.predict(X_test)

    plt.figure(figsize=(14, 7))
    plt.plot(interval_data['time'], interval_data['EDC'], label='Actual EDC', alpha=0.5, color='gray')
    plt.plot(interval_data['time'].iloc[X_train.index], y_train, 'o', label='Actual EDC (Training)', alpha=0.5, color='blue')
    plt.plot(interval_data['time'].iloc[X_train.index], y_pred_train, 'x', label='Predicted EDC (Training)', alpha=0.5, color='green')
    plt.plot(interval_data['time'].iloc[X_test.index], y_test, 'o', label='Actual EDC (Testing)', alpha=0.5, color='red')
    plt.plot(interval_data['time'].iloc[X_test.index], y_pred_test, 'x', label='Predicted EDC (Testing)', alpha=0.5, color='orange')

    plt.xlabel('Time')
    plt.ylabel('EDC')
    plt.title(f'Interval {interval_index} - Best Model Results - R2 Train: {best_r2_train:.2f}, R2 Test: {best_r2_test:.2f}')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'file/interval_{interval_index}_best_model_results(smooth).png')
    plt.show()

for idx, interval in enumerate(time_intervals):
    interval_data = data[(data['time'] >= interval[0]) & (data['time'] <= interval[1])]
    best_r2_train, best_r2_test, best_model, end_time = train_and_evaluate_rf(interval_data)
    print(f'Interval {idx + 1}:')
    print(f'Best R2 Train: {best_r2_train:.2f}')
    print(f'Best R2 Test: {best_r2_test:.2f}')
    save_best_model(best_model, interval, end_time)
    plot_best_model_results(data, interval, best_model, idx + 1, best_r2_train, best_r2_test)