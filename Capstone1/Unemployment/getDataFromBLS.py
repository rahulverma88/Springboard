import requests
import json
import numpy as np
import pandas as pd



area_codes = pd.read_csv('BLS_AreaCodes.txt',sep='\t',index_col=False)
county_codes = area_codes[area_codes['area_type_code'] == 'F']
county_codes = county_codes.reset_index(drop=True)

county_names = dict(zip(county_codes['area_code'],county_codes['area_text']))
months = dict(zip(['M01','M02','M03','M04','M05','M06','M07','M08','M09','M10','M11','M12'],
                  ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']))
# The county codes for each state can be extracted using the 'selectable sort_sequence' column
# Texas county codes : 6755-7008
# North Dakota county codes: 5563-5615
# Oklahoma county codes: 5881-5957
state_sequences = {'tx':[6755,7008], 'nd':[5563,5615], 'ok':[5881,5957]}

# Pick state(s) to extract data for
target_states = ['tx','nd','ok']
start_year = 1990
end_year = 2017

headers = {'Content-type': 'application/json'}
for state in target_states:
    start_row = int(county_codes.index[county_codes['sort_sequence'] == state_sequences[state][0]].values)
    end_row = int(start_row + state_sequences[state][1] - state_sequences[state][0])
    series_id_list = list(map(lambda x: 'LAU' + x + '03', list(county_codes.iloc[start_row:end_row]['area_code'].values)))

    cur_state_data = {'SeriesId': [], 'Year': [], 'Period': [], 'Value': []}

    # must break up series list into lots of 50 for API
    for i in np.arange(0,len(series_id_list),50):
        series_end = min(i+50,len(series_id_list))
        cur_series_list = series_id_list[i:series_end]
        for year in np.arange(start_year,end_year,20): # 20 years at a time
            cur_start_year = year
            cur_end_year = min(year + 20, end_year)
            data = json.dumps({"seriesid": cur_series_list, "startyear": str(cur_start_year), "endyear": str(cur_end_year),"registrationkey":"62fa9141c8314e7eb68c043321bde37a"})
            p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
            json_data = json.loads(p.text)


            for series in json_data['Results']['series']:
                seriesId = series['seriesID']
                for item in series['data']:
                    cur_state_data['SeriesId'].append(seriesId)
                    cur_state_data['Year'].append(item['year'])
                    cur_state_data['Period'].append(item['period'])
                    cur_state_data['Value'].append(item['value'])


    cur_state_df = pd.DataFrame.from_dict(cur_state_data)
    cur_state_df['CountyName'] = cur_state_df['SeriesId'].apply(lambda x: x[3:-2]).map(county_names)
    cur_state_df['Month'] = cur_state_df['Period'].map(months)
    cur_state_df['Time'] = pd.to_datetime(cur_state_df['Month'] + cur_state_df['Year'].astype(str))
    cur_state_df = cur_state_df[['Time','CountyName','Value']]
    cur_state_df = cur_state_df.pivot(index='Time',columns='CountyName',values='Value')
    cur_state_df.to_csv(state + '_unemployment.csv')
