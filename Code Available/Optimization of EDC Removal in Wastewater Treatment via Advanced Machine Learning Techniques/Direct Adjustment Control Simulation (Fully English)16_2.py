import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import warnings
import joblib
import os
import json

warnings.filterwarnings("ignore")

# -----------------------------
# English display names mapping (unchanged)
# -----------------------------
DISPLAY_NAMES = {
    'LVCM2-FC503F': 'Liquid Level (FC503F)',
    'LVCM-TI-C503A-I.PV': 'C503A Internal Temperature (TI) (PV)',
    'LVCM2-FC503AS.PV': 'Steam Flow (FC503AS)',  # keep for axis labels, NOT used in legend
    'LVCM2-TC503T': 'Column Top Temperature (TC503T)',
    'LVCM2-TC503B': 'Column Bottom Temperature (TC503B)',
    'LVCM-PI-C503A-T.PV': 'Column Top Pressure (PI) (PV)',
    'LVCM-PI-C503A-B.PV': 'Column Bottom Pressure (PI) (PV)',
    'LVCM2-LC503': 'Feed Temperature (LC503)',
    'EDC': 'EDC Concentration (ppm)'
}

# -----------------------------
# Load data
# -----------------------------
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
    """Simple rolling-mean smoothing (keeps the original 'time' column)."""
    datetime_col = df['time']
    df_numeric = df.drop(columns=['time'])
    df_smoothed = df_numeric.rolling(window=window, min_periods=1).mean()
    df_smoothed['time'] = datetime_col
    return df_smoothed


data = smooth_data(data)

# -----------------------------
# Define time intervals
# -----------------------------
time_intervals = [
    ["2022-08-26 16:40:00", "2022-11-07 13:00:00"],
    ["2023-12-22 16:50:00", "2024-03-01 15:40:00"]
]


def get_sub_intervals(interval, num_sub_intervals=6):
    """Split an interval into equal-length sub-intervals."""
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
    """Load pre-trained models for the specified time intervals."""
    models = {
        'ARIMA': {},
        'VARIMA': {},
        'RandomForest': {}
    }

    sub_intervals_map = {}
    for idx, interval in enumerate(time_intervals):
        subs = get_sub_intervals(interval)
        for sub_idx, sub_interval in enumerate(subs):
            sub_intervals_map[(sub_interval[0], sub_interval[1])] = (idx, sub_idx)

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
                model.feature_names = np.load(full_rf_model_path.replace('.pkl', '_features.npy'), allow_pickle=True)
                models['RandomForest'][rf_model_path] = model
            rf_count += 1
    print(f"Total RandomForest models loaded: {rf_count}")

    return models


def load_feature_importances(model_folder, interval):
    """Load precomputed feature importances for a given interval (if available)."""
    feature_importance_filename = os.path.join(model_folder,
                                               f'next_rf_model_{interval[0]}_{interval[1]}_without_EDC_feature_importances.npy')
    if os.path.exists(feature_importance_filename):
        feature_importances = np.load(feature_importance_filename, allow_pickle=True)
        feature_importance_pairs = [(str(pair[0]), float(pair[1])) for pair in feature_importances]
        feature_importance_pairs.sort(key=lambda x: x[1], reverse=True)
        return feature_importance_pairs
    else:
        print(f"Feature importance file not found for interval {interval}")
        return []


# Example usage for feature importances
interval = ["2023-12-22 16:50:00", "2024-03-01 15:40:00"]
feature_importance_pairs = load_feature_importances('png/New_merged5_2_3', interval)


# Program 1: Direct adjustment method

def adjust_predictions_direct(test_interval, data, predictions, rf_model, selected_features, feature_importance_pairs):
    """Directly adjust control-relevant lag features based on EDC thresholds and re-predict."""
    # Keep only lag features (exclude any potential _lag0)
    selected_features = [feat for feat in selected_features if '_lag' in feat and '_lag0' not in feat]

    adjusted_predictions = {key: list(value) for key, value in predictions.items()}
    interval_start, interval_end = test_interval
    interval_data = data[(data['time'] >= interval_start) & (data['time'] <= interval_end)].reset_index(drop=True)

    if 'time' not in adjusted_predictions:
        adjusted_predictions['time'] = list(interval_data['time'])

    for col in adjusted_predictions:
        if col != 'time':
            while len(adjusted_predictions[col]) < len(interval_data):
                adjusted_predictions[col].append(adjusted_predictions[col][-1])

    max_lag = 48
    exog_data = pd.DataFrame()

    # Build lagged exogenous matrix (start from lag 1)
    for lag in range(1, max_lag + 1):
        for var in cols:
            exog_col = f'{var}_lag{lag}'
            exog_data[exog_col] = interval_data[var].shift(lag)

    exog_data = exog_data.fillna(method='ffill').fillna(method='bfill')

    # Ensure all training-time features are present
    all_features = rf_model.feature_names
    missing_features = [feature for feature in all_features if feature not in exog_data.columns]

    for feature in missing_features:
        exog_data[feature] = 0

    # Animation setup (English titles/legends/labels)
    fig, ax1 = plt.subplots(figsize=(14, 7))
    ax2 = ax1.twinx()

    def update_plot(i):
        if i == 0:
            return

        current_edc = adjusted_predictions['EDC'][i - 1]
        if current_edc is None:
            return

        fc503as_cols = [col for col in selected_features if 'LVCM2-FC503AS.PV' in col and '_lag0' not in col]

        if current_edc < 0.08:
            adjusted_fc503as = exog_data.loc[i, fc503as_cols] * 0.95
            adjusted_fc503as = min(adjusted_fc503as.min(), predictions['LVCM2-FC503AS.PV'][i])
            adjusted_fc503as = max(adjusted_fc503as, 0.9 * predictions['LVCM2-FC503AS.PV'][i])
        elif current_edc > 0.1:
            adjusted_fc503as = exog_data.loc[i, fc503as_cols] * 1.05
            adjusted_fc503as = min(adjusted_fc503as.max(), 1.1 * predictions['LVCM2-FC503AS.PV'][i])

        adjusted_predictions['LVCM2-FC503AS.PV'][i] = adjusted_fc503as
        exog_data.loc[i, fc503as_cols] = adjusted_fc503as
        adjusted_edc = rf_model.predict(exog_data.loc[i, all_features].values.reshape(1, -1))[0]
        adjusted_predictions['EDC'][i] = adjusted_edc

        # Update plot (legend without confidential code)
        ax1.clear(); ax2.clear()
        ax1.plot(interval_data['time'][:i], interval_data['EDC'][:i], label='Actual EDC (ppm)', color='blue')
        ax1.plot(interval_data['time'][:i], predictions['EDC'][:i], label='Predicted EDC (ppm)', color='red', linestyle='--')
        ax1.plot(interval_data['time'][:i], adjusted_predictions['EDC'][:i], label='Adjusted EDC (ppm)', color='purple')
        ax1.set_xlabel('Time'); ax1.set_ylabel(DISPLAY_NAMES['EDC']); ax1.legend(loc='upper left')

        # Legend text changed to avoid "FC503AS" mention
        ax2.plot(interval_data['time'][:i], interval_data['LVCM2-FC503AS.PV'][:i], label='Actual Steam Flow', color='cyan', linestyle='dashed')
        ax2.plot(interval_data['time'][:i], predictions['LVCM2-FC503AS.PV'][:i], label='Predicted Steam Flow', color='green', linestyle='dashed')
        ax2.plot(interval_data['time'][:i], adjusted_predictions['LVCM2-FC503AS.PV'][:i], label='Adjusted Steam Flow', color='magenta', linestyle='dashed')
        ax2.set_ylabel(DISPLAY_NAMES['LVCM2-FC503AS.PV'])  # axis label may keep full technical name
        ax2.legend(loc='upper right')

        plt.title(f"EDC (ppm) and Steam Flow Adjustments for Interval {interval_start} to {interval_end}")

    ani = animation.FuncAnimation(fig, update_plot, frames=len(interval_data)-1, repeat=False)
    os.makedirs('png/fileㄧ二_16_2', exist_ok=True)
    ani.save('png/fileㄧ二_16_2/adjustment_animation.mp4', writer='ffmpeg')
    plt.show()

    for i in range(1, len(interval_data)-1):
        update_plot(i)

    return adjusted_predictions


def generate_report_with_adjustments(data, predictions, adjusted_predictions, interval):
    """Generate a static report plot with English titles/legends/labels (legend without FC503AS)."""
    start, end = interval
    interval_data = data[(data['time'] >= start) & (data['time'] <= end)].reset_index(drop=True)

    fig, ax1 = plt.subplots(figsize=(14, 7))

    pred_len = min(len(interval_data['time']), len(predictions['EDC']))
    ax1.plot(interval_data['time'][:pred_len], predictions['EDC'][:pred_len], label='Predicted EDC (ppm)', color='red', linestyle='--')
    ax1.plot(interval_data['time'], adjusted_predictions['EDC'], label='Adjusted EDC (ppm)', color='purple', linestyle='--')

    ax1.set_xlabel('Time')
    ax1.set_ylabel(DISPLAY_NAMES['EDC'])

    ax2 = ax1.twinx()
    pred_len = min(len(interval_data['time']), len(predictions['LVCM2-FC503AS.PV']))
    ax2.plot(interval_data['time'][:pred_len], predictions['LVCM2-FC503AS.PV'][:pred_len], label='Predicted Steam Flow', color='green', linestyle='dashed')

    adj_len = min(len(interval_data['time']), len(adjusted_predictions['LVCM2-FC503AS.PV']))
    ax2.plot(interval_data['time'][:adj_len], adjusted_predictions['LVCM2-FC503AS.PV'][:adj_len], label='Adjusted Steam Flow', color='magenta', linestyle='dashed')

    ax2.set_ylabel(DISPLAY_NAMES['LVCM2-FC503AS.PV'])  # can keep full name on axis

    ax1.legend(loc='upper left'); ax2.legend(loc='upper right')

    plt.title(f"EDC (ppm) and Steam Flow Adjustments for Interval {start} to {end}")
    os.makedirs('png/fileㄧ二_16_2', exist_ok=True)
    plt.savefig(f'png/fileㄧ二_16_2/Adjustments_{start}_{end}_1.png')
    plt.show()


# -----------------------------
# Main program
# -----------------------------
with open(os.path.join(model_folder2, 'all_predicted_data.txt'), 'r') as f:
    all_predicted_data = json.load(f)

test_interval_id = 0
models = load_models(data, time_intervals, model_folder)

# for interval in time_intervals:
for interval in time_intervals[1:]:
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
    adjusted_predictions = adjust_predictions_direct(test_interval, data, predictions, rf_model, selected_features, feature_importance_pairs)
    generate_report_with_adjustments(data, predictions, adjusted_predictions, test_interval)

    test_interval_id += 1
