import pandas as pd
import plotly.express as px

df = pd.read_csv('/Users/lakitha/Downloads/MINTS_e45f018020e9_PSA109_2023_06_20.csv')

fig = px.line(df, x = 'dateTime', y = 'hrAmplitude', title='HR')
fig.show()



import heartpy as hp

hrdata = hp.get_data('/Users/lakitha/Downloads/MINTS_e45f018020e9_PSA109_2023_06_20.csv', column_name='hrAmplitude')
working_data, measures = hp.process(hrdata, 38.0)
hp.plotter(working_data, measures)
# print(working_data)
print(measures['bpm'])
# print(measures['lf/hf'])