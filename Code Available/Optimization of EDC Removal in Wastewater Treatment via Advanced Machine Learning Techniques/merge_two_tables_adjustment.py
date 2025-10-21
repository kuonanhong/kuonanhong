import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# Load the data
data = pd.read_csv("data/merged_spike_periods_vcm3_ft509_edc_corrected.csv", parse_dates=['time'])
data['time'] = pd.to_datetime(data['time'])
data.replace('No Data', np.nan, inplace=True)
cols = ['EDC', 'LVCM2-FC503F', 'LVCM-TI-C503A-I.PV', 'LVCM2-FC503AS.PV', 'LVCM2-TC503T', 'LVCM2-TC503B',
        'LVCM-PI-C503A-T.PV', 'LVCM-PI-C503A-B.PV', 'LVCM2-LC503']
data[cols] = data[cols].apply(pd.to_numeric, errors='coerce')
data.fillna(method='ffill', inplace=True)
data.fillna(method='bfill', inplace=True)

lookback = 1  
f = open('png/file/output.txt', 'w')  

def smooth_data(df, window=5):
    datetime_col = df['time']
    df_numeric = df.drop(columns=['time'])
    df_smoothed = df_numeric.rolling(window=window, min_periods=1).mean()
    df_smoothed['time'] = datetime_col
    return df_smoothed

data = smooth_data(data)

# Define ARIMA model fitting
def fit_arima(series, min_r2=0.7, max_retries=10):
    best_order = None
    best_aic = float("inf")
    best_r2 = -np.inf
    retries = 0

    while best_r2 < min_r2 and retries < max_retries:
        for p in range(1, 4):
            for d in range(1, 3):
                for q in range(1, 4):
                    try:
                        model = ARIMA(series, order=(p, d, q))
                        result = model.fit()
                        train_pred = result.predict(start=lookback, end=len(series) - 1)
                        r2_train = r2_score(series[lookback:], train_pred)
                        if r2_train > best_r2:
                            best_r2 = r2_train
                            best_aic = result.aic
                            best_order = (p, d, q)
                    except:
                        continue
        retries += 1

    return best_order, best_aic, best_r2

def calculate_aic(series1, order, exog):
    model = ARIMA(series1, order=order, exog=exog)
    result = model.fit()
    return result.aic

# Define the time intervals
time_intervals = [
    ["2022-08-26 16:40:00", "2022-11-07 13:00:00"],
    ["2023-12-22 16:50:00", "2024-03-01 15:40:00"]
]

def get_sub_intervals_with_overlap(interval, num_sub_intervals=5, overlap=0.1):
    start, end = interval
    start_date = pd.to_datetime(start)
    end_date = pd.to_datetime(end)
    total_duration = end_date - start_date
    interval_size = total_duration / num_sub_intervals

    sub_intervals = []
    for i in range(num_sub_intervals):
        sub_start = start_date + i * interval_size * (1 - overlap)
        sub_end = sub_start + interval_size
        sub_intervals.append((sub_start, sub_end))

    return sub_intervals

# Predict next ARIMA parameters
def predict_next_interval_arima_params(arima_params_within, historical_arima_params):
    next_interval_params = {}
    for column, orders in arima_params_within.items():
        p, d, q = orders
        if column in historical_arima_params and len(historical_arima_params[column]) >= 2:
            prev_orders = historical_arima_params[column][-2]
            last_orders = historical_arima_params[column][-1]
            next_p = max(0, last_orders[0] + (last_orders[0] - prev_orders[0]))
            next_d = max(0, last_orders[1] + (last_orders[1] - prev_orders[1]))
            next_q = max(0, last_orders[2] + (last_orders[2] - prev_orders[2]))
        else:
            next_p = p
            next_d = d
            next_q = q
        next_interval_params[column] = (next_p, next_d, next_q)
    return next_interval_params

# Predict next VARIMA parameters
def predict_next_interval_varima_params(varima_params, historical_varima_params):
    next_interval_params = {}
    for (col1, col2), orders in varima_params.items():
        p, d, q = orders
        key = (col1, col2)
        if key in historical_varima_params and len(historical_varima_params[key]) >= 2:
            prev_orders = historical_varima_params[key][-2]
            last_orders = historical_varima_params[key][-1]
            next_p = max(0, last_orders[0] + (last_orders[0] - prev_orders[0]))
            next_d = max(0, last_orders[1] + (last_orders[1] - prev_orders[1]))
            next_q = max(0, last_orders[2] + (last_orders[2] - prev_orders[2]))
        else:
            next_p = p
            next_d = d
            next_q = q
        next_interval_params[key] = (next_p, next_d, next_q)
    return next_interval_params

# Predict next RandomForest parameters (we will use the same hyperparameters)
def predict_next_interval_rf_params(historical_rf_params):
    print("predict_next_interval_rf_params 的 historical_rf_params : ", historical_rf_params, file=f)
    if len(historical_rf_params) >= 2:
        last_model, _ = historical_rf_params[-1]
        prev_model, _ = historical_rf_params[-2]
        return last_model
    else:
        return historical_rf_params[-1][0] if historical_rf_params else RandomForestRegressor()

def analyze_intervals(data, intervals, historical_arima_params, historical_varima_params, historical_rf_params):
    models = []
    arima_params_within = {}
    varima_params = {}

    for start, end in intervals:
        interval_data = data[(data['time'] >= start) & (data['time'] <= end)]

        # Find the best VARIMA parameters
        for column1 in interval_data.columns:
            for column2 in interval_data.columns:
                if column1 != column2 and column1 != 'time' and column2 != 'time':
                    best_aic = np.inf
                    best_order = (0, 0, 0)
                    for p in range(5):
                        for d in range(3):
                            for q in range(5):
                                try:
                                    aic = calculate_aic(interval_data[column1], order=(p, d, q), exog=interval_data[column2])
                                    if aic < best_aic:
                                        best_aic = aic
                                        best_order = (p, d, q)
                                except:
                                    continue
                    varima_params[(column1, column2)] = best_order

        # EDC RandomForest
        edc_data = interval_data.dropna(subset=['EDC'])
        X_edc = edc_data.drop(columns=['time', 'EDC'])
        y_edc = edc_data['EDC']

        rf = RandomForestRegressor()
        rf.fit(X_edc, y_edc)
        y_train_pred = rf.predict(X_edc)
        r2_train = r2_score(y_edc, y_train_pred)

        models.append({
            'interval': (start, end),
            'model': rf,
            'r2_train': r2_train,
            'type': 'RandomForest'
        })

        # Other fields ARIMA and Apply VARIMA model
        for column in interval_data.columns:
            if column not in ['time', 'EDC']:
                series = interval_data[column].dropna()
                order, aic, r2 = fit_arima(series)
                arima_params_within[column] = order

                model = ARIMA(series, order=order)
                fitted_model = model.fit()

                train_pred = fitted_model.predict(start=lookback, end=len(series) - 1)

                valid_indices_train = ~np.isnan(train_pred)
                valid_indices_train = valid_indices_train.reindex(series.index, fill_value=False)  # Align indices

                series_valid = series[valid_indices_train]
                train_pred_valid = train_pred[valid_indices_train]

                if len(series_valid) > 0 and len(train_pred_valid) > 0:
                    r2_train = r2_score(series_valid, train_pred_valid)
                else:
                    r2_train = np.nan

                models.append({
                    'interval': (start, end),
                    'column': column,
                    'model': fitted_model,
                    'order': order,
                    'r2_train': r2_train,
                    'type': 'ARIMA'
                })

                for col in interval_data.columns:
                    if col != column and col != 'time':
                        varima_order = varima_params.get((column, col))
                        if varima_order is not None and not any(x is None for x in varima_order):
                            aligned_exog = interval_data[col].reindex(series.index).values.reshape(-1, 1)
                            arima_model = ARIMA(series, order=varima_order, exog=aligned_exog)
                            arima_result = arima_model.fit()
                            train_pred = arima_result.predict(start=lookback, end=len(series) - 1, exog=aligned_exog)

                            valid_indices_train = ~np.isnan(train_pred)
                            valid_indices_train = valid_indices_train.reindex(series.index, fill_value=False)

                            series_valid = series[valid_indices_train]
                            train_pred_valid = train_pred[valid_indices_train]

                            if len(series_valid) > 0 and len(train_pred_valid) > 0:
                                r2_train = r2_score(series_valid, train_pred_valid)
                            else:
                                r2_train = np.nan

                            models.append({
                                'interval': (start, end),
                                'column': column,
                                'model': arima_result,
                                'order': varima_order,
                                'r2_train': r2_train,
                                'type': 'VARIMA'
                            })

        for column, order in arima_params_within.items():
            if column not in historical_arima_params:
                historical_arima_params[column] = []
            historical_arima_params[column].append(order)

        for (col1, col2), order in varima_params.items():
            if (col1, col2) not in historical_varima_params:
                historical_varima_params[(col1, col2)] = []
            historical_varima_params[(col1, col2)].append(order)

        historical_rf_params.append((rf, r2_train))

    return models, arima_params_within, varima_params, historical_arima_params, historical_varima_params, historical_rf_params

def process_intervals(data, time_intervals):
    historical_arima_params = {}
    historical_varima_params = {}
    historical_rf_params = []
    all_models = []
    all_arima_params_within = []
    all_varima_params = []
    all_predicted_data = []

    for interval in time_intervals:
        sub_intervals = get_sub_intervals_with_overlap(interval)

        # Train on the overlapping sub-intervals
        train_intervals = sub_intervals[:-1]
        test_interval = sub_intervals[-1]

        # Analyze training intervals
        #models, arima_params_within, varima_params = analyze_intervals(data, train_intervals, historical_arima_params,
        #                                                               historical_varima_params, historical_rf_params)
        # Analyze training intervals
        models, arima_params_within, varima_params, historical_arima_params, historical_varima_params, historical_rf_params = analyze_intervals(
            data, train_intervals, historical_arima_params, historical_varima_params, historical_rf_params)


        # Predict next interval's parameters based on training intervals
        next_arima_params = predict_next_interval_arima_params(arima_params_within, historical_arima_params)
        next_varima_params = predict_next_interval_varima_params(varima_params, historical_varima_params)
        next_rf_model = predict_next_interval_rf_params(historical_rf_params)

        predicted_data = predict_with_next_params(data, sub_intervals, next_arima_params, next_varima_params, next_rf_model)
        all_predicted_data.append(predicted_data)

        all_models.extend(models)
        all_arima_params_within.append(arima_params_within)
        all_varima_params.append(varima_params)

        # Now evaluate the model on the test interval
        evaluate_model(data, test_interval, models, predicted_data)

    return all_models, all_arima_params_within, all_varima_params, all_predicted_data

def predict_with_next_params(data, intervals, next_arima_params, next_varima_params, next_rf_model):
    last_interval_data = data[(data['time'] >= intervals[-1][0]) & (data['time'] <= intervals[-1][1])]
    predicted_data = {}

    for column, order in next_arima_params.items():
        series = last_interval_data[column].dropna()
        model = ARIMA(series, order=order)
        fitted_model = model.fit()
        train_pred = fitted_model.predict(start=lookback, end=len(series) - 1)
        predicted_data[column] = train_pred

        r2_pred = r2_score(series[lookback:], train_pred)

        plt.figure(figsize=(14, 7))
        plt.plot(last_interval_data['time'], series, label=f'Actual {column}')
        plt.plot(last_interval_data['time'][lookback:], train_pred,
                 label=f'Predicted {column} (ARIMA{order}) R²={r2_pred:.2f}', color='blue')
        plt.legend()
        plt.title(f'{column} Predictions for Last Interval')
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.savefig(f'png/file/{column}_Predictions_for_Last_Interval_Predicted_{intervals[-1][0]}_{intervals[-1][1]}.png')
        # plt.show()

    edc_data = last_interval_data.dropna(subset=['EDC'])
    X_edc = edc_data.drop(columns=['time', 'EDC'])
    y_edc = edc_data['EDC']
    y_train_pred = next_rf_model.predict(X_edc)

    r2_train = r2_score(y_edc, y_train_pred)

    plt.figure(figsize=(14, 7))
    plt.plot(edc_data['time'], y_edc, label=f'Actual EDC')
    plt.plot(edc_data['time'], y_train_pred, label=f'Predicted EDC (RandomForest) R²={r2_train:.2f}', color='red')
    plt.legend()
    plt.title(f'EDC Predictions for Last Interval')
    plt.xlabel('Time')
    plt.ylabel('EDC')
    plt.savefig(f'png/file/EDC_Predictions_for_Last_Interval_Predicted_{intervals[-1][0]}_{intervals[-1][1]}.png')

    return predicted_data

def evaluate_model(data, test_interval, trained_models, predicted_data):
    test_interval_data = data[(data['time'] >= test_interval[0]) & (data['time'] <= test_interval[1])]

    for model in trained_models:
        if model['type'] == 'ARIMA':
            column = model['column']
            series = test_interval_data[column].dropna()
            train_pred = predicted_data[column]

            r2_test = r2_score(series[lookback:], train_pred)

            plt.figure(figsize=(14, 7))
            plt.plot(test_interval_data['time'], series, label=f'Actual {column}')
            plt.plot(test_interval_data['time'][lookback:], train_pred,
                     label=f'Predicted {column} (ARIMA{model["order"]}) R²={r2_test:.2f}', color='blue')
            plt.legend()
            plt.title(f'{column} Model Evaluation for Test Interval')
            plt.xlabel('Time')
            plt.ylabel('Value')
            plt.savefig(
                f'png/file/{column}_Model_Evaluation_for_Test_Interval_{test_interval[0]}_{test_interval[1]}.png')

        elif model['type'] == 'RandomForest':
            edc_data = test_interval_data.dropna(subset=['EDC'])
            X_edc = edc_data.drop(columns=['time', 'EDC'])
            y_edc = edc_data['EDC']
            y_train_pred = model['model'].predict(X_edc)

            r2_test = r2_score(y_edc, y_train_pred)

            plt.figure(figsize=(14, 7))
            plt.plot(edc_data['time'], y_edc, label=f'Actual EDC')
            plt.plot(edc_data['time'], y_train_pred, label=f'Predicted EDC (RandomForest) R²={r2_test:.2f}',
                     color='red')
            plt.legend()
            plt.title(f'EDC Model Evaluation for Test Interval')
            plt.xlabel('Time')
            plt.ylabel('EDC')
            plt.savefig(f'png/file/EDC_Model_Evaluation_for_Test_Interval_{test_interval[0]}_{test_interval[1]}.png')
            # plt.show()

def save_results_to_csv(models, arima_params_within, varima_params):
    models_df = pd.DataFrame(models)
    models_df.to_csv('png/file/models.csv', index=False)

    arima_params_list = [item for sublist in arima_params_within for item in sublist.items()]
    arima_params_df = pd.DataFrame(arima_params_list, columns=['Column', 'Order'])
    arima_params_df.to_csv('png/file/arima_params.csv', index=False)

    varima_params_list = [((k[0], k[1]), v) for sublist in varima_params for k, v in sublist.items()]
    varima_params_df = pd.DataFrame(varima_params_list, columns=['Column Pair', 'Order'])
    varima_params_df[['Column1', 'Column2']] = pd.DataFrame(varima_params_df['Column Pair'].tolist(), index=varima_params_df.index)
    varima_params_df.drop(columns=['Column Pair'], inplace=True)
    varima_params_df.to_csv('png/file/varima_params.csv', index=False)

def plot_results(models, intervals):
    for start, end in intervals:
        interval_data = data[(data['time'] >= start) & (data['time'] <= end)]
        for model in models:
            if model['interval'] == (start, end):
                if model['type'] == 'ARIMA':
                    column = model['column']
                    series = interval_data[column]
                    plt.figure(figsize=(14, 7))
                    plt.plot(interval_data['time'], series, label=f'Actual {column}')
                    train_pred = model['model'].predict(start=lookback, end=len(series) - 1)
                    plt.plot(interval_data['time'][lookback:], train_pred,
                             label=f'Train Predict {column} (ARIMA{model["order"]}) R²={model["r2_train"]:.2f}', color='green')
                    plt.legend()
                    plt.title(f'{column} Predictions for Interval {start} to {end}')
                    plt.xlabel('Time')
                    plt.ylabel('Value')
                    plt.savefig(f'png/file/{column}_Predictions_for_Interval_{start}_to_{end}_file.png')
                    # plt.show()
                elif model['type'] == 'RandomForest':
                    plt.figure(figsize=(14, 7))
                    edc_data = interval_data.dropna(subset=['EDC'])
                    plt.plot(edc_data['time'], edc_data['EDC'], label=f'Actual EDC')
                    train_pred = model['model'].predict(edc_data.drop(columns=['time', 'EDC']))
                    plt.plot(edc_data['time'], train_pred,
                             label=f'Train Predict EDC (RandomForest) R²={model["r2_train"]:.2f}', color='red')
                    plt.legend()
                    plt.title(f'EDC Predictions for Interval {start} to {end}')
                    plt.xlabel('Time')
                    plt.ylabel('EDC')
                    plt.savefig(f'png/file/EDC_Predictions_for_Interval_{start}_to_{end}_file.png')

def plot_combined_results(models, test_intervals, all_predicted_data):
    for idx, (start, end) in enumerate(test_intervals):
        interval_data = data[(data['time'] >= start) & (data['time'] <= end)]
        predicted_data = all_predicted_data[idx]
        plt.figure(figsize=(14, 7))
        plt.plot(interval_data['time'], interval_data['EDC'], label='Actual EDC', color='black')

        for model in models:
            if model['interval'] == (start, end):
                if model['type'] == 'ARIMA':
                    column = model['column']
                    series = interval_data[column]
                    train_pred = model['model'].predict(start=lookback, end=len(series) - 1)
                    r2_train = model['r2_train']
                    plt.plot(interval_data['time'][lookback:], train_pred,
                             label=f'Train Predict {column} (ARIMA{model["order"]}) R²={r2_train:.2f}', color='green')

                elif model['type'] == 'RandomForest':
                    edc_data = interval_data.dropna(subset=['EDC'])
                    X_edc = edc_data.drop(columns=['time', 'EDC'])
                    train_pred = model['model'].predict(X_edc)
                    r2_train = model['r2_train']
                    plt.plot(edc_data['time'], train_pred,
                             label=f'Train Predict EDC (RandomForest) R²={r2_train:.2f}', color='red')

        # Plotting predicted data with the next interval's parameters
        for column, train_pred in predicted_data.items():
            series = interval_data[column].dropna()
            r2_pred = r2_score(series[lookback:], train_pred)
            plt.plot(interval_data['time'][lookback:], train_pred,
                     label=f'Predicted {column} (Next Interval) R²={r2_pred:.2f}', color='blue')

        plt.legend()
        plt.title(f'Combined Results for Interval {start} to {end}')
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.savefig(f'png/file/Combined_Results_for_Interval_{start}_to_{end}.png')

all_models, all_arima_params_within, all_varima_params, all_predicted_data = process_intervals(data, time_intervals)
test_intervals = [sub_intervals[-1] for sub_intervals in
                  [get_sub_intervals_with_overlap(interval) for interval in time_intervals]]
plot_combined_results(all_models, test_intervals, all_predicted_data)

save_results_to_csv(all_models, all_arima_params_within, all_varima_params)
