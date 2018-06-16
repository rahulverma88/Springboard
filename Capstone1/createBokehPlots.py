import requests
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from os import listdir

from bokeh.plotting import figure, show, output_file
from bokeh.sampledata.us_counties import data as counties
from bokeh.sampledata.us_states import data as states
from bokeh.plotting import ColumnDataSource
from bokeh.models import HoverTool, Slider
from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import LinearAxis, Range1d


tx_data = pd.read_csv('Texas_combined.csv')
tx_data['Date'] = pd.to_datetime(tx_data['Date'])

tx_oil = tx_data.pivot(index='Date',columns='County_Name',values='Oil_Production')
tx_unemp = pd.read_csv('./UnemploymentData/tx_unemployment.csv')#tx_data.pivot(index='Date',columns='County_Name',values='Unemployment_Rate')
tx_lab_force = pd.read_csv('./UnemploymentData/tx_laborForce.csv')

tx_unemp['Date']= pd.to_datetime(tx_unemp['Date'])
tx_unemp = tx_unemp.set_index('Date')

EXCLUDED = ("ak", "hi", "pr", "gu", "vi", "mp", "as")

target_state = ("tx")#,"nd","co","wy","ok","nm","pa","ca","la")
state_xs = [states[code]["lons"] for code in states]
state_ys = [states[code]["lats"] for code in states]

county_xs=[counties[code]["lons"] for code in counties if counties[code]["state"] in target_state]
county_ys=[counties[code]["lats"] for code in counties if counties[code]["state"] in target_state]

cur_year = 1995
cur_month = 2
cur_date = pd.to_datetime({'year':[cur_year],'month':[cur_month],'day':[1]})

month_dict = dict(zip(range(1,13),['January','February', 'March', 'April', 'May',
    'June','July','August','September','October','November','December']))

county_names = tx_unemp.columns
county_rates = tx_unemp.loc[cur_date].values[0]

source_tx_oil = ColumnDataSource(tx_oil)
county_names_orig = [county['name'] for county in counties.values()]

colors = ["#F1EEF6", "#D4B9DA", "#C994C7", "#DF65B0", "#DD1C77", "#980043"]

county_colors = []
bins = np.linspace(0, max(county_rates) + 1, 6)
color_bins = np.digitize(county_rates, bins)

for idx in color_bins:
    county_colors.append(colors[idx])


TOOLS="pan,wheel_zoom,box_zoom,reset,hover,save,tap"

source_tx_unemp = ColumnDataSource(data=dict(
    x=county_xs,
    y=county_ys,
    color=county_colors,
    name=county_names,
    rate=county_rates,
))


p = figure(title='Texas unemployment data for %s, %d' % (month_dict[cur_month], cur_year), toolbar_location="left",tools=TOOLS,
           plot_width=600, plot_height=600)

pyglyph = p.patches('x', 'y',source=source_tx_unemp,
          fill_color='color', fill_alpha=0.7,
          line_color="white", line_width=0.5)#,
         # set visual properties for selected glyphs
         # selection_color="firebrick",

        # set visual properties for non-selected glyphs
       # nonselection_fill_alpha=0.2,
       # nonselection_fill_color="blue",
       # nonselection_line_color="firebrick",
       # nonselection_line_alpha=1.0)


hover = p.select(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [
    ("Name", "@name"),
    ("Unemployment rate", "@rate%"),
    ("(Long, Lat)", "($x, $y)"),
]


p1 = figure(x_axis_type='datetime',plot_width=450, plot_height=300,toolbar_location='left',tools='box_select')
p1.circle('Date','Andrews County, TX',source=source_tx_oil,selection_color='red',nonselection_fill_color='grey',nonselection_fill_alpha=0.2)

oil_price = pd.read_csv('./OilPrices/oil_price_by_month.csv')
oil_price['Date'] = pd.to_datetime(oil_price['Date'])
source_oil_price = ColumnDataSource(oil_price)
source_tx_unemp_2 = ColumnDataSource(dict(
    x = tx_unemp.index,
    y = tx_unemp['Andrews County, TX']
))

p1 = figure(x_axis_type='datetime',plot_width=600, plot_height=300,toolbar_location='left',tools='box_select')
# Setting the second y axis range name and range
p1.extra_y_ranges = {"unemp": Range1d(start=0, end=50)}

# Adding the second axis to the plot.
p1.add_layout(LinearAxis(y_range_name="unemp"), 'right')

p1.circle('Date','WTI',source=source_oil_price,selection_color='red',nonselection_fill_color='grey',nonselection_fill_alpha=0.2)
p1.line('Date','WTI',source=source_oil_price)
p1.circle('x','y', source=source_tx_unemp_2,y_range_name="unemp",color='orange')
p1.title.text = 'Historical unemployment rates vs oil prices for ' + 'Andrews County, TX'

hover = HoverTool(tooltips=None,mode='vline')
p2 = figure(x_axis_type='datetime',plot_width=450, plot_height=300,toolbar_location='left',tools=[hover,'crosshair','box_select'])
p2.circle('Date','Zavala County, TX',source=source_tx_oil,hover_color='red',selection_color='red',nonselection_fill_color='grey',nonselection_fill_alpha=0.2)


def callback_tap(attr, old, new):
    try:
        # The index of the selected glyph is : new['1d']['indices'][0]
        selections = new['1d']['indices']
        patch_name = source_tx_unemp.data['name'][selections[0]]
        source_tx_unemp_2.data = dict(
            x = tx_unemp.index,
            y = tx_unemp[patch_name]
        )
    except:
        selections = old['1d']['indices']
        patch_name = source_tx_unemp.data['name'][selections[0]]
        source_tx_unemp_2.data = dict(
            x = tx_unemp.index,
            y = tx_unemp[patch_name]
        )

    p1.title.text = 'Historical unemployment rates vs oil prices for ' + patch_name


pyglyph.data_source.on_change('selected',callback_tap)


def update_plot_yr(attr, old, new):
    # Assign the value of the slider: new_year
    new_year = slider_yr.value
    new_month = slider_month.value

    new_date = pd.to_datetime({'year': [new_year], 'month': [new_month], 'day': [1]})
    new_rates = tx_unemp.loc[new_date].values[0]

    new_county_colors = []
    new_bins = np.linspace(0, max(new_rates) + 1, 6)
    new_color_bins = np.digitize(new_rates, new_bins)

    for idx in new_color_bins:
        new_county_colors.append(colors[idx])

    # Set new_data
    new_data = dict(
        x=county_xs,
        y=county_ys,
        color=new_county_colors,
        name=county_names,
        rate=new_rates
    )

    # Assign new_data to: source.data
    source_tx_unemp.data = new_data

    # Add title to figure: plot.title.text
    p.title.text = 'Texas unemployment data for %s, %d' % (month_dict[new_month],new_year)


def update_plot_month(attr, old, new):
    # Assign the value of the slider:
    new_year = slider_yr.value
    new_month = slider_month.value

    new_date = pd.to_datetime({'year': [new_year], 'month': [new_month], 'day': [1]})
    new_rates = tx_unemp.loc[new_date].values[0]

    new_county_colors = []
    new_bins = np.linspace(0, max(new_rates) + 1, 6)
    new_color_bins = np.digitize(new_rates, new_bins)

    for idx in new_color_bins:
        new_county_colors.append(colors[idx])

    # Set new_data
    new_data = dict(
        x=county_xs,
        y=county_ys,
        color=new_county_colors,
        name=county_names,
        rate=new_rates
    )

    # Assign new_data to: source.data
    source_tx_unemp.data = new_data

    # Add title to figure: plot.title.text
    p.title.text = 'Texas unemployment data for %s, %d' % (month_dict[new_month],new_year)


# Make a slider object: slider
slider_yr = Slider(title='Year', start=1990, end=2016, step=1, value=cur_year)

# Attach the callback to the 'value' property of slider
slider_yr.on_change('value', update_plot_yr)

# Make a slider object: slider
slider_month = Slider(title='Month', start=1, end=12, step=1, value=cur_month)

# Attach the callback to the 'value' property of slider
slider_month.on_change('value', update_plot_month)

col1 = column(p)
col2 = column([slider_yr,slider_month,p1])
layout = row(p,col2)
#show(layout)
curdoc().add_root(layout)