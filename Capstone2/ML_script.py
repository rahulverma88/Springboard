# import required packages
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt

from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import scale

from sklearn.ensemble import RandomForestRegressor


def clean_data(df, lims):
    cols_to_drop = ['file_no', 'Current_Well_Name', 'Lease_Number', 'Township', 'Well_Type', 'Well_Status_Date',
                    'file_number', 'fluid_gal', 'fluid_gal_per_ft', 'top', 'Footages', 'Lease_Name', 'Field_Name', 'QQ',
                    'Range', 'CTB', 'Section', 'Well_Status', 'Original_Well_Name', 'Original_Operator',
                    'Current_Operator']
    df.drop(labels=cols_to_drop, axis=1, inplace=True)
    df.dropna(inplace=True)
    today_date = datetime.date(2018, 5, 23)
    spud_delta = (today_date - pd.to_datetime(df.Spud_Date)).dt.days
    df['spud_timedelta'] = spud_delta
    treatment_delta = (today_date - pd.to_datetime(df.treatment_date)).dt.days
    df['treatment_timedelta'] = treatment_delta
    df.drop(['Spud_Date', 'treatment_date'], axis=1, inplace=True)

    for i in lims:
        df = df[df[i] > lims[i][0]]
        df = df[df[i] < lims[i][1]]

    return df


def lin_reg_func(df, data_cols):
    # get dummy values for the categorical variables
    df = pd.get_dummies(df)
    y = df.cum_oil_365.values

    # scaling the data columns
    X = scale(df[data_cols].values)
    X = np.concatenate((X, df.drop(data_cols, axis=1).values), axis=1)

    # create training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    reg = linear_model.LinearRegression()
    reg.fit(X_train, y_train)
    y_pred = reg.predict(X_test)
    r2_val = reg.score(X_test, y_test)
    rmse_val = np.sqrt(mean_squared_error(y_test, y_pred))
    cv_scores = cross_val_score(reg, X, y, cv=5)

    return r2_val, rmse_val, np.mean(cv_scores)


def random_forest_func(df, data_cols, num_estimators=500):
    df = pd.get_dummies(df)
    y = df.cum_oil_365.values
    X = scale(df[data_cols].drop(['cum_oil_365'],axis=1).values)
    X = np.concatenate((X, df.drop(data_cols, axis=1).values), axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    rf = RandomForestRegressor(n_estimators=num_estimators, random_state=42)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    r2_val = rf.score(X_test, y_test)
    rmse_val = np.sqrt(mean_squared_error(y_test, y_pred))
    cv_scores = cross_val_score(rf, X, y, cv=5)

    return r2_val, rmse_val, np.mean(cv_scores)

# read csv data file
cum_prods = pd.read_csv('prod-by-operated-day.csv')
completions = pd.read_csv('completion.csv')
well_indices = pd.read_csv('well-index.csv')

# isolate the production variable desired
prods_365 = cum_prods.set_index('api')[['cum_oil_365']]

# eliminate rows in completions data where all column values are the same
completions.drop_duplicates(inplace=True)

# eliminate rows where both api and treatment date are the same
completions.drop_duplicates(subset=['api','treatment_date'],keep=False,inplace=True)

# dropping refracked wells
completions.drop_duplicates(subset=['api'],keep=False,inplace=True)

prods_365.reset_index(inplace=True)

final_data = pd.merge(prods_365, well_indices,how='inner',on='api')
final_data = pd.merge(final_data, completions,how='inner',on='api')

limits = {'bottom':[],
       'fluid_bbl':[], 'fluid_bbl_per_ft':[], 'ft_per_stage':[], 'lateral_length':[],
       'max_treat_press':[], 'max_treat_rate':[], 'propp_lbs':[], 'propp_lbs_per_ft':[],
       'stages':[]}

for i in limits.keys():
    limits[i] = [min(final_data[i]), max(final_data[i])]

final_data = clean_data(final_data,limits)

data_cols = ['cum_oil_365', 'TD', 'Latitude', 'Longitude', 'bottom',
       'fluid_bbl', 'fluid_bbl_per_ft', 'ft_per_stage', 'lateral_length',
       'max_treat_press', 'max_treat_rate', 'propp_lbs', 'propp_lbs_per_ft',
       'stages', 'spud_timedelta', 'treatment_timedelta']

r2_rf, rmse_rf, cv_rf = random_forest_func(final_data, data_cols)
