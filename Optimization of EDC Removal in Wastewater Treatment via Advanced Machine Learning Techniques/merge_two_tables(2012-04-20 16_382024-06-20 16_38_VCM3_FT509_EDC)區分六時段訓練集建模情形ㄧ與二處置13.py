import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from statsmodels.tsa.arima.model import ARIMA
import warnings
import joblib
import os
import json

warnings.filterwarnings("ignore")

# Load data
data = pd.read_csv("data/combined_spike_periods_vcm3_ft509_edc_all_timestamps.csv", parse_dates=['time'])
data['time'] = pd.to_datetime(data['time'])
data.replace('No Data', np.nan, inplace=True)
cols = ['EDC', 'LVCM2-FC503F', 'LVCM-TI-C503A-I.PV', 'LVCM2-FC503AS.PV', 'LVCM2-TC503T', 'LVCM2-TC503B',
        'LVCM-PI-C503A-T.PV', 'LVCM-PI-C503A-B.PV', 'LVCM2-LC503']
data[cols] = data[cols].apply(pd.to_numeric, errors='coerce')
data.fillna(method='ffill', inplace=True)
data.fillna(method='bfill', inplace=True)

lookback = 1
model_folder = "png/ARIMA_VARIMA_RF_model5"
model_folder2 = "png/ARIMA_VARIMA_RF_model6"

def smooth_data(df, window=5):
    datetime_col = df['time']
    df_numeric = df.drop(columns=['time'])
    df_smoothed = df_numeric.rolling(window=window, min_periods=1).mean()
    df_smoothed['time'] = datetime_col
    return df_smoothed

data = smooth_data(data)

# Define time intervals
time_intervals = [
    ["2022-08-26 16:40:00", "2022-11-07 13:00:00"],
    ["2023-12-22 16:50:00", "2024-03-01 15:40:00"]
]

def get_sub_intervals(interval, num_sub_intervals=6):
    start, end = interval
    start_date = pd.to_datetime(start)
    end_date = pd.to_datetime(end)
    total_duration = (end_date - start_date) / num_sub_intervals
    sub_intervals = []
    for i in range(num_sub_intervals):
        sub_start = start_date + i * total_duration
        sub_end = sub_start + total_duration
        sub_intervals.append((sub_start, sub_end))
    return sub_intervals

sub_intervals = []
for interval in time_intervals:
    sub_intervals.extend(get_sub_intervals(interval))

def load_models(data, time_intervals, model_folder="png/ARIMA_VARIMA_RF_model5"):
    models = {
        'ARIMA': {},
        'VARIMA': {},
        'RandomForest': {}
    }

    sub_intervals_map = {}
    for idx, interval in enumerate(time_intervals):
        sub_intervals = get_sub_intervals(interval)
        for sub_idx, sub_interval in enumerate(sub_intervals):
            sub_intervals_map[(sub_interval[0], sub_interval[1])] = (idx, sub_idx)

    # Load ARIMA models
    arima_count = 0
    for col in cols:
        if col != 'time':
            for (start, end) in sub_intervals_map.keys():
                arima_model_path = os.path.join(model_folder, f"ARIMA_model_{col}_{start}_{end}.joblib")
                if os.path.exists(arima_model_path):
                    time_idx, sub_idx = sub_intervals_map[(start, end)]
                    models['ARIMA'][(time_idx, sub_idx, col)] = joblib.load(arima_model_path)
                    arima_count += 1
    print(f"Total ARIMA models loaded: {arima_count}")

    # Load VARIMA models
    varima_count = 0
    for col1 in cols:
        for col2 in cols:
            if col1 != col2 and col1 != 'time' and col2 != 'time':
                for (start, end) in sub_intervals_map.keys():
                    varima_model_path = os.path.join(model_folder, f"VARIMA_model_{col1}_{col2}_{start}_{end}.joblib")
                    if os.path.exists(varima_model_path):
                        time_idx, sub_idx = sub_intervals_map[(start, end)]
                        models['VARIMA'][(time_idx, sub_idx, col1, col2)] = joblib.load(varima_model_path)
                        varima_count += 1
    print(f"Total VARIMA models loaded: {varima_count}")
    
    # Load RandomForest models
    rf_count = 0
    rf_model_paths = [
        "next_rf_model_2022-08-26_2022-11-07_without_EDC.pkl",
        "next_rf_model_2023-12-22_2024-03-01_without_EDC.pkl"
    ]
    
    for rf_model_path in rf_model_paths:
        full_rf_model_path = os.path.join(model_folder, rf_model_path)
        if os.path.exists(full_rf_model_path):
            with open(full_rf_model_path, 'rb') as f:
                model = joblib.load(f)
                model.feature_names = np.load(full_rf_model_path.replace('.pkl', '_features.npy'),allow_pickle=True)
                models['RandomForest'][rf_model_path] = model
                print("Number of features in loaded model:", model.n_features_in_)
                print ("model.n_features_in_ : ", model.n_features_in_)        # 100
            rf_count += 1
    print(f"Total RandomForest models loaded: {rf_count}")
    
    return models

def process_intervals(data, time_intervals, model_folder=model_folder):
    all_predicted_data = {}
    models = load_models(data, time_intervals, model_folder)

    for interval in time_intervals:
        sub_intervals = get_sub_intervals(interval)
        test_interval = sub_intervals[-1]  # 最後一個子間隔作為測試間隔

        # 使用ARIMA和VARIMA模型預測測試間隔
        test_predicted_data = {}
        for col in cols:
            if col != 'time':
                test_predicted_data[col] = models['ARIMA'][(time_intervals.index(interval), 5, col)].forecast(steps=len(data[(data['time'] >= test_interval[0]) & (data['time'] <= test_interval[1])]))[0]

        # 確保預測數據與測試間隔對齊
        test_interval_len = len(data[(data['time'] >= test_interval[0]) & (data['time'] <= test_interval[1])])
        test_predicted_data = {k: v[-test_interval_len:].tolist() for k, v in test_predicted_data.items()}  # 轉換為列表
        all_predicted_data[str(test_interval)] = test_predicted_data

    # Save all_predicted_data to txt files
    with open(os.path.join(model_folder2, 'all_predicted_data.txt'), 'w') as f:
        json.dump({str(k): v for k, v in all_predicted_data.items()}, f)

    return all_predicted_data

def adjust_predictions(test_interval_id, test_interval, data, predictions, rf_model, selected_features):
    if not predictions:
        print(f"No predictions available for test interval {test_interval_id}.")
        return predictions

    # 1. Initialize adjusted predictions:
    adjusted_predictions = {key: list(value) for key, value in predictions.items()}

    interval_start, interval_end = test_interval
    interval_data = data[(data['time'] >= interval_start) & (data['time'] <= interval_end)].reset_index(drop=True)

    if 'time' not in adjusted_predictions:
        adjusted_predictions['time'] = list(interval_data['time'])

    for col in adjusted_predictions:
        if col != 'time':
            while len(adjusted_predictions[col]) < len(interval_data):
                adjusted_predictions[col].append(adjusted_predictions[col][-1])

    # 2. Add lag features
    max_lag = 48
    for lag in range(1, max_lag + 1):
        for var in cols:
            interval_data[f'{var}_lag{lag}'] = interval_data[var].shift(lag)

    interval_data.dropna(inplace=True)  # Remove rows with NaN
    
    # 過濾掉 selected_features 中的重複欄位
    #selected_features = [f for f in selected_features if '_lag' in f]

    for i in range(1, len(interval_data)):
        current_edc = adjusted_predictions['EDC'][i - 1]
        current_fc503as = adjusted_predictions['LVCM2-FC503AS.PV'][i - 1]

        if current_edc is None or current_fc503as is None:
            continue

        exog_data = pd.DataFrame()

        for lag in range(0, max_lag):
            for var in cols:
                exog_col = f'{var}_lag{lag}'
                if lag == 0:
                    exog_data[exog_col] = interval_data[var]  # lag 0 is the original variable
                else:
                    exog_data[exog_col] = interval_data[var].shift(lag)  # Add lag features

        exog_data = exog_data.iloc[i][selected_features].values.reshape(1, -1)
        expected_features = rf_model.n_features_in_
        #print("exog_data.shape[1]:", exog_data.shape[1], "; expected_features:", expected_features) # exog_data.shape[1]: 92 ; expected_features: 100

        if exog_data.shape[1] < expected_features:
            missing_features = expected_features - exog_data.shape[1]
            exog_data = np.hstack([exog_data, np.zeros((1, missing_features))])

        if current_edc < 0.1 and current_fc503as > 0.85 * np.mean(interval_data['LVCM2-FC503AS.PV']):
            adjusted_fc503as = current_fc503as * 0.85
            adjusted_predictions['LVCM2-FC503AS.PV'][i] = adjusted_fc503as
            adjusted_edc = rf_model.predict(exog_data)[0]
            adjusted_predictions['EDC'][i] = adjusted_edc
        elif current_edc > 0.1:
            adjusted_fc503as = current_fc503as * 1.15
            adjusted_predictions['LVCM2-FC503AS.PV'][i] = adjusted_fc503as
            adjusted_edc = rf_model.predict(exog_data)[0]
            adjusted_predictions['EDC'][i] = adjusted_edc
            if 'LVCM2-TC503T' in adjusted_predictions:
                adjusted_tc503t = adjusted_predictions['LVCM2-TC503T'][i - 1] * 1.15
                adjusted_predictions['LVCM2-TC503T'][i] = adjusted_tc503t
                adjusted_edc = rf_model.predict(exog_data)[0]
                adjusted_predictions['EDC'][i] = adjusted_edc

    return adjusted_predictions

#def generate_report_with_adjustments(data, predictions, adjusted_predictions, interval):
def generate_report_with_adjustments(data, predictions, interval):    
    start, end = interval
    interval_data = data[(data['time'] >= start) & (data['time'] <= end)].reset_index(drop=True)

    fig, ax1 = plt.subplots(figsize=(14, 7))

    ax1.plot(interval_data['time'], interval_data['EDC'], label='Actual EDC', color='blue')

    pred_len = min(len(interval_data['time']), len(predictions['EDC']))
    ax1.plot(interval_data['time'][:pred_len], predictions['EDC'][:pred_len], label='Predicted EDC', color='red', linestyle='--')
    #ax1.plot(interval_data['time'], adjusted_predictions['EDC'], label='Adjusted EDC', color='purple')

    ax1.set_xlabel('Time')
    ax1.set_ylabel('EDC')

    ax2 = ax1.twinx()
    ax2.plot(interval_data['time'], interval_data['LVCM2-FC503AS.PV'], label="Actual LVCM2-FC503AS.PV", color='cyan', linestyle='dashed')

    pred_len = min(len(interval_data['time']), len(predictions['LVCM2-FC503AS.PV']))
    ax2.plot(interval_data['time'][:pred_len], predictions['LVCM2-FC503AS.PV'][:pred_len], label="Predicted LVCM2-FC503AS.PV", color='green', linestyle='dashed')

    #adj_len = min(len(interval_data['time']), len(adjusted_predictions['LVCM2-FC503AS.PV']))
    #ax2.plot(interval_data['time'][:adj_len], adjusted_predictions['LVCM2-FC503AS.PV'][:adj_len], label="Adjusted LVCM2-FC503AS.PV", color='magenta', linestyle='dashed')

    ax2.set_ylabel("LVCM2-FC503AS.PV")

    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.title(f'EDC and Steam Usage Adjustments for Interval {start} to {end}')
    #plt.savefig(f'png/fileㄧ二_13/Adjustments_{start}_{end}_1.png')
    plt.savefig(f'png/fileㄧ二_13/Prediction_{start}_{end}_1.png')
    plt.show()

# Main program
with open(os.path.join(model_folder2, 'all_predicted_data.txt'), 'r') as f:
    all_predicted_data = json.load(f)

test_interval_id = 0
models = load_models(data, time_intervals, model_folder)

for interval in time_intervals:
    sub_intervals = get_sub_intervals(interval)
    test_interval = sub_intervals[-1]

    predictions = all_predicted_data.get(str(test_interval), {})
    if not predictions:
        print(f"No predictions available for test interval {test_interval_id}. Skipping interval.")
        continue

    if interval == ["2022-08-26 16:40:00", "2022-11-07 13:00:00"]:
        rf_model = models['RandomForest']["next_rf_model_2022-08-26_2022-11-07_without_EDC.pkl"]
        
    else:
        rf_model = models['RandomForest']["next_rf_model_2023-12-22_2024-03-01_without_EDC.pkl"]
        
    selected_features = rf_model.feature_names
    print ("len(selected_features) : ",len(selected_features),"; selected_features : ", selected_features)
    #adjusted_predictions = adjust_predictions(test_interval_id, test_interval, data, predictions, rf_model, selected_features)
    #generate_report_with_adjustments(data, predictions, adjusted_predictions, test_interval)
    generate_report_with_adjustments(data, predictions, test_interval)

    test_interval_id += 1
"""
selected_features :  ['LVCM2-FC503F' 'LVCM-TI-C503A-I.PV' 'LVCM2-FC503AS.PV' 'LVCM2-TC503T'
 'LVCM2-TC503B' 'LVCM-PI-C503A-T.PV' 'LVCM-PI-C503A-B.PV' 'LVCM2-LC503'
 'LVCM2-FC503F_lag0' 'LVCM-TI-C503A-I.PV_lag0' 'LVCM2-FC503AS.PV_lag0'
 'LVCM2-TC503T_lag0' 'LVCM2-TC503B_lag0' 'LVCM-PI-C503A-T.PV_lag0'
 'LVCM-PI-C503A-B.PV_lag0' 'LVCM2-LC503_lag0' 'LVCM2-FC503F_lag1'
 'LVCM-TI-C503A-I.PV_lag1' 'LVCM2-FC503AS.PV_lag1' 'LVCM2-TC503T_lag1'
 'LVCM2-TC503B_lag1' 'LVCM-PI-C503A-T.PV_lag1' 'LVCM-PI-C503A-B.PV_lag1'
 'LVCM2-LC503_lag1' 'LVCM2-FC503F_lag2' 'LVCM-TI-C503A-I.PV_lag2'
 'LVCM2-FC503AS.PV_lag2' 'LVCM2-TC503T_lag2' 'LVCM2-TC503B_lag2'
 'LVCM-PI-C503A-T.PV_lag2' 'LVCM-PI-C503A-B.PV_lag2' 'LVCM2-LC503_lag2'
 'LVCM2-FC503F_lag3' 'LVCM-TI-C503A-I.PV_lag3' 'LVCM2-FC503AS.PV_lag3'
 'LVCM2-TC503T_lag3' 'LVCM2-TC503B_lag3' 'LVCM-PI-C503A-T.PV_lag3'
 'LVCM-PI-C503A-B.PV_lag3' 'LVCM2-LC503_lag3' 'LVCM2-FC503F_lag4'
 'LVCM-TI-C503A-I.PV_lag4' 'LVCM2-FC503AS.PV_lag4' 'LVCM2-TC503T_lag4'
 'LVCM2-TC503B_lag4' 'LVCM-PI-C503A-T.PV_lag4' 'LVCM-PI-C503A-B.PV_lag4'
 'LVCM2-LC503_lag4' 'LVCM2-FC503F_lag5' 'LVCM-TI-C503A-I.PV_lag5'
 'LVCM2-FC503AS.PV_lag5' 'LVCM2-TC503T_lag5' 'LVCM2-TC503B_lag5'
 'LVCM-PI-C503A-T.PV_lag5' 'LVCM-PI-C503A-B.PV_lag5' 'LVCM2-LC503_lag5'
 'LVCM2-FC503F_lag6' 'LVCM-TI-C503A-I.PV_lag6' 'LVCM2-FC503AS.PV_lag6'
 'LVCM2-TC503T_lag6' 'LVCM2-TC503B_lag6' 'LVCM-PI-C503A-T.PV_lag6'
 'LVCM-PI-C503A-B.PV_lag6' 'LVCM2-LC503_lag6' 'LVCM2-FC503F_lag7'
 'LVCM-TI-C503A-I.PV_lag7' 'LVCM2-FC503AS.PV_lag7' 'LVCM2-TC503T_lag7'
 'LVCM2-TC503B_lag7' 'LVCM-PI-C503A-T.PV_lag7' 'LVCM-PI-C503A-B.PV_lag7'
 'LVCM2-LC503_lag7' 'LVCM2-FC503F_lag8' 'LVCM-TI-C503A-I.PV_lag8'
 'LVCM2-FC503AS.PV_lag8' 'LVCM2-TC503T_lag8' 'LVCM2-TC503B_lag8'
 'LVCM-PI-C503A-T.PV_lag8' 'LVCM-PI-C503A-B.PV_lag8' 'LVCM2-LC503_lag8'
 'LVCM2-FC503F_lag9' 'LVCM-TI-C503A-I.PV_lag9' 'LVCM2-FC503AS.PV_lag9'
 'LVCM2-TC503T_lag9' 'LVCM2-TC503B_lag9' 'LVCM-PI-C503A-T.PV_lag9'
 'LVCM-PI-C503A-B.PV_lag9' 'LVCM2-LC503_lag9' 'LVCM2-FC503F_lag10'
 'LVCM-TI-C503A-I.PV_lag10' 'LVCM2-FC503AS.PV_lag10' 'LVCM2-TC503T_lag10'
 'LVCM2-TC503B_lag10' 'LVCM-PI-C503A-T.PV_lag10'
 'LVCM-PI-C503A-B.PV_lag10' 'LVCM2-LC503_lag10' 'LVCM2-FC503F_lag11'
 'LVCM-TI-C503A-I.PV_lag11' 'LVCM2-FC503AS.PV_lag11' 'LVCM2-TC503T_lag11']
"""