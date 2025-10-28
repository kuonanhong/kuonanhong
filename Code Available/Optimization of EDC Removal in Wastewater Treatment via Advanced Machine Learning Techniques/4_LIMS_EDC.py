import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import joblib

# =============================
# Load data
# =============================
combined_df = pd.read_csv('data/combined_spike_periods_vcm3_ft509_edc_all_timestamps.csv', parse_dates=['time'])
combined_df['time'] = pd.to_datetime(combined_df['time'])

combined_df.replace('No Data', np.nan, inplace=True)
variables = ['EDC', 'LVCM2-FC503F', 'LVCM-TI-C503A-I.PV', 'LVCM2-FC503AS.PV', 'LVCM2-TC503T', 'LVCM2-TC503B',
             'LVCM-PI-C503A-T.PV', 'LVCM-PI-C503A-B.PV', 'LVCM2-LC503']
combined_df[variables] = combined_df[variables].apply(pd.to_numeric, errors='coerce')

combined_df.fillna(method='ffill', inplace=True)
combined_df.fillna(method='bfill', inplace=True)

# =============================
# English display name mapping (for plots/legends only)
# Keeps raw column names for data processing so paths and keys still work
# =============================
DISPLAY_NAME = {
    'EDC': 'EDC Concentration',
    'LVCM2-FC503F': 'Liquid Level',
    'LVCM-TI-C503A-I.PV': 'Internal Temperature',  # generic, avoids plant codes
    'LVCM2-FC503AS.PV': 'Steam Flow',               # do NOT display the code in figures
    'LVCM2-TC503T': 'Top Temperature',
    'LVCM2-TC503B': 'Bottom Temperature',
    'LVCM-PI-C503A-T.PV': 'Top Pressure',
    'LVCM-PI-C503A-B.PV': 'Bottom Pressure',
    'LVCM2-LC503': 'Feed Temperature',
}

def pretty_feature_name(name: str) -> str:
    """Convert raw feature name like 'LVCM2-FC503AS.PV_lag10' to
    de-identified English label like 'Steam Flow (lag 10)'.
    If no lag suffix, return mapped base name.
    """
    if '_lag' in name:
        base, lag = name.rsplit('_lag', 1)
        base_disp = DISPLAY_NAME.get(base, base)
        return f"{base_disp} (lag {lag})"
    else:
        return DISPLAY_NAME.get(name, name)

# =============================
# Smooth data (exclude EDC)
# =============================

def smooth_data(df, window=5):
    datetime_col = df['time']
    df_numeric = df.drop(columns=['time', 'EDC'])
    df_smoothed = df_numeric.rolling(window=window, min_periods=1).mean()
    df_smoothed['EDC'] = df['EDC']
    df_smoothed['time'] = datetime_col
    return df_smoothed

combined_df = smooth_data(combined_df)

# =============================
# Create lag features (keep current-time features too), but drop EDC_lag0 later
# =============================
max_lag = 48
for lag in range(0, max_lag):  # include current-time features (lag 0)
    for var in variables:
        combined_df[f'{var}_lag{lag}'] = combined_df[var].shift(lag)

# Drop rows with NaNs introduced by shifting
combined_df = combined_df.dropna()

# Remove current-time EDC value (EDC_lag0) from features
combined_df = combined_df.drop(columns=['EDC_lag0'])

# =============================
# Define time intervals
# =============================
time_intervals = [
    ["2022-08-26 16:40:00", "2022-11-07 13:00:00"],
    ["2023-12-22 16:50:00", "2024-03-01 15:40:00"]
]

# =============================
# Plot feature importances (de-identified labels)
# =============================

def plot_feature_importances(model, features, interval):
    feature_importances = model.feature_importances_
    importance_df = pd.DataFrame({'Feature': features, 'Importance': feature_importances})
    importance_df = importance_df.sort_values(by='Importance', ascending=False)

    # Only take top-5 or those with weight > 0.05 (retain original selection logic)
    importance_df = importance_df[(importance_df['Importance'] > 0.05) | (importance_df.index < 5)]

    # Map to de-identified display names for plotting
    importance_df['FeatureDisplay'] = importance_df['Feature'].map(pretty_feature_name)

    plt.figure(figsize=(14, 7))
    plt.barh(importance_df['FeatureDisplay'], importance_df['Importance'])
    plt.xlabel('Importance', fontsize=18)
    plt.ylabel('Feature', fontsize=18)
    plt.title('Feature Importances', fontsize=20)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(f'file/Feature_Importances_{interval[0]}_{interval[1]}.png')
    plt.show()
    return importance_df

# =============================
# Train next-interval RF using accumulated historical data
# =============================

def train_next_interval_rf_model(historical_rf_params, new_X, new_y, selected_features):
    combined_features = []
    combined_targets = []

    for model, X, y in historical_rf_params:
        combined_features.append(X[selected_features])
        combined_targets.append(y.values)

    combined_features.append(new_X[selected_features])
    combined_targets.append(new_y.values)

    combined_features = np.vstack(combined_features)
    combined_targets = np.hstack(combined_targets)

    # Train the next RF model on accumulated data
    next_rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    next_rf_model.fit(combined_features, combined_targets)

    return next_rf_model

# =============================
# Main experiment routine
# =============================

def run_experiment(include_edc_lags=True):
    for interval in time_intervals:
        start, end = pd.to_datetime(interval[0]), pd.to_datetime(interval[1])
        total_duration = end - start

        sub_intervals = [
            (start, start + total_duration * 0.5),
            (start + total_duration * 0.1, start + total_duration * 0.6),
            (start + total_duration * 0.2, start + total_duration * 0.7),
            (start + total_duration * 0.3, start + total_duration * 0.8),
            (start + total_duration * 0.4, start + total_duration * 0.9)
        ]
        historical_rf_params = []

        for sub_start, sub_end in sub_intervals:
            sub_data = combined_df[(combined_df['time'] >= sub_start) & (combined_df['time'] <= sub_end)]
            X_sub = sub_data.drop(columns=['time', 'EDC'])
            y_sub = sub_data['EDC']

            if not include_edc_lags:
                edc_lag_cols = [col for col in X_sub.columns if 'EDC' in col]
                X_sub = X_sub.drop(columns=edc_lag_cols)

            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            rf_model.fit(X_sub, y_sub)
            y_pred = rf_model.predict(X_sub)

            r2 = r2_score(y_sub, y_pred)
            historical_rf_params.append((rf_model, X_sub, y_sub))

            # Save model
            model_filename = f'file/rf_model_{sub_start}_{sub_end}.pkl'
            joblib.dump(rf_model, model_filename)

            # Save feature names
            feature_names_filename = model_filename.replace('.pkl', '_features.npy')
            np.save(feature_names_filename, X_sub.columns.values)

            # Report R2 score
            print(f"Model {sub_start} to {sub_end} R2 score: {r2}")

        # Ensure we pick the most important features (top 100)
        feature_importances = historical_rf_params[-1][0].feature_importances_
        features = list(historical_rf_params[-1][1].columns)
        feature_importance_pairs = list(zip(features, feature_importances))
        feature_importance_pairs.sort(key=lambda x: x[1], reverse=True)
        selected_features = [feature for feature, importance in feature_importance_pairs[:100]]

        # Train next model using historical data and then evaluate on the remainder (test set)
        test_start = start + total_duration * 0.5
        test_data = combined_df[(combined_df['time'] > test_start) & (combined_df['time'] <= end)]
        X_test = test_data.drop(columns=['time', 'EDC'])
        y_test = test_data['EDC']

        if not include_edc_lags:
            edc_lag_cols = [col for col in X_test.columns if 'EDC' in col]
            X_test = X_test.drop(columns=edc_lag_cols)

        next_rf_model = train_next_interval_rf_model(historical_rf_params, X_test, y_test, selected_features)

        # Predict using the selected feature set
        X_test_selected = X_test[selected_features]
        y_test_pred = next_rf_model.predict(X_test_selected)
        test_r2 = r2_score(y_test, y_test_pred)

        # Report test R2
        print(f"Test-set R2 score: {test_r2}")

        # =============================
        # Plot Actual vs Predicted EDC (avoid overlapping date ticks)
        # =============================
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.plot(test_data['time'], y_test.values, label='Actual EDC (Test)')
        ax.plot(test_data['time'], y_test_pred, label=f'Predicted EDC (Test R2: {test_r2:.2f})', linestyle='--')

        # Make the x-axis readable and non-overlapping
        locator = mdates.AutoDateLocator(minticks=5, maxticks=8)
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        # Add a little padding on both ends so the last labels don't collide
        tmin = test_data['time'].min()
        tmax = test_data['time'].max()
        pad = (tmax - tmin) * 0.02 if (tmax > tmin) else pd.Timedelta(hours=1)
        ax.set_xlim(tmin - pad, tmax + pad)

        # Rotate/align labels and tighten layout
        fig.autofmt_xdate()
        ax.margins(x=0.01)
        ax.legend()
        ax.set_title('Actual vs Predicted EDC')
        ax.set_xlabel('Time')
        ax.set_ylabel('EDC Concentration (ppm)')
        fig.tight_layout()

        fig.savefig(
            f"file/Actual_vs_Predicted_EDC_{interval[0]}_{interval[1]}_{'with_EDC' if include_edc_lags else 'without_EDC'}.png"
        )
        plt.show()

        # Plot feature importance chart with de-identified labels
        importance_df = plot_feature_importances(next_rf_model, X_test_selected.columns, interval)

        # Save next model and its selected feature names
        model_filename = f"file/next_rf_model_{interval[0]}_{interval[1]}_{'with_EDC' if include_edc_lags else 'without_EDC'}.pkl"
        joblib.dump(next_rf_model, model_filename)

        feature_names_filename = model_filename.replace('.pkl', '_features.npy')
        np.save(feature_names_filename, X_test_selected.columns.values)

        # Display (print) the importance table (features remain raw in file; printed names are raw)
        print(importance_df)

# =============================
# 1.3.1 With EDC lags (lag = 1~48)
# =============================
print("Running experiment with EDC lags...")
run_experiment(include_edc_lags=True)

# =============================
# 1.3.2 Without EDC lags (lag = 1~48)
# =============================
print("Running experiment without EDC lags...")
run_experiment(include_edc_lags=False)

