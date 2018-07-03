import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectFromModel
from sklearn.preprocessing import scale

# Macroeconomic data
sp500 = pd.read_csv('./EconomicIndices/sp500_month.csv')
sp500['Date'] = pd.to_datetime(sp500['Date'])
sp500.set_index('Date',inplace=True)

# Oil Price data
oil_price = pd.read_csv('./OilPrices/oil_price_by_month.csv')
oil_price['Date'] = pd.to_datetime(oil_price['Date'])
oil_price.set_index('Date',inplace=True)


def get_main_feature(oil_prod, unemp, lab_force):
    min_date = max(min(unemp.index), min(oil_prod.index))
    max_date = min(max(unemp.index), max(oil_prod.index))

    cur_sp500 = sp500.loc[min_date:max_date]
    cur_oil_price = oil_price.loc[min_date:max_date]

    oil_prod = oil_prod.loc[min_date:max_date]
    unemp = unemp.loc[min_date:max_date]
    lab_force = lab_force.loc[min_date:max_date]

    imp_feature = dict()
    county_list = oil_prod.columns.values
    #county_list = [oil_prod.columns.values[0]]

    for county in county_list:
        cur_data = pd.DataFrame(data={'oil': oil_prod[county], 'lab_force': lab_force[county],
                                      'sp500': cur_sp500['SP500'], 'oil_price': cur_oil_price['WTI']})
        X = scale(cur_data.values)
        y = unemp[county].values

        # Create a random forest classifier
        clf = RandomForestRegressor(n_estimators=500, random_state=42)

        # Train the classifier
        clf.fit(X, y)

        feat_labels = cur_data.columns.values

        # Print the name and gini importance of each feature
        feat_imp = dict(zip(feat_labels, clf.feature_importances_))
        imp_feature[county] = max(feat_imp, key=feat_imp.get)

    return imp_feature

tx_oil = pd.read_csv('./OilGasProduction/Texas/TexasOilProdCounty.csv')
tx_unemp = pd.read_csv('./Unemployment/tx_unemployment.csv')
tx_lab_force = pd.read_csv('./Unemployment/tx_laborForce.csv')

tx_oil.reset_index(inplace=True)
tx_oil['Date']= pd.to_datetime(tx_oil['Date'])
tx_oil.drop('index',axis=1,inplace=True)
tx_oil = tx_oil.set_index('Date')

tx_unemp['Date']= pd.to_datetime(tx_unemp['Date'])
tx_unemp = tx_unemp.set_index('Date')

tx_lab_force['Date']= pd.to_datetime(tx_lab_force['Date'])
tx_lab_force = tx_lab_force.set_index('Date')

tx_features = get_main_feature(tx_oil, tx_unemp, tx_lab_force)