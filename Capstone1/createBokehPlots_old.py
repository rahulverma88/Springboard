import numpy as np
import pandas as pd

from bokeh.plotting import figure, show, output_file
from bokeh.sampledata.us_counties import data as counties
from bokeh.plotting import ColumnDataSource
from bokeh.models import HoverTool, Slider
from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import LinearAxis, Range1d, LogAxis
from bokeh.models import LogColorMapper
from bokeh.palettes import Viridis6 as palette
from bokeh.palettes import Blues8 as palette1

# Macroeconomic data
sp500 = pd.read_csv('./EconomicIndices/sp500_month.csv')
sp500['Date'] = pd.to_datetime(sp500['Date'])
source_sp500 = ColumnDataSource(sp500)

# Oil Price data
oil_price = pd.read_csv('./OilPrices/oil_price_by_month.csv')
oil_price['Date'] = pd.to_datetime(oil_price['Date'])
source_oil_price = ColumnDataSource(oil_price)

# Set date for geographical maps
cur_year = 1996
cur_month = 2
cur_date = pd.to_datetime({'year':[cur_year],'month':[cur_month],'day':[1]})

# create dictionary for mapping month names
month_dict = dict(zip(range(1,13),['January','February', 'March', 'April', 'May',
    'June','July','August','September','October','November','December']))

# Texas maps
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



target_state = ("tx")
tx_county_xs=[counties[code]["lons"] for code in counties if counties[code]["state"] in target_state]
tx_county_ys=[counties[code]["lats"] for code in counties if counties[code]["state"] in target_state]

tx_county_names = tx_unemp.columns
tx_county_rates = tx_unemp.loc[cur_date].values[0]
tx_county_prods = tx_oil.loc[cur_date].values[0]

(tx_hist, tx_bin_edges) = np.histogram(tx_county_rates, bins=5)

tx_bins = np.linspace(0,max(tx_county_rates)+1,6)
tx_pos = np.digitize(tx_county_rates,tx_bins)

colors = ["#F1EEF6", "#D4B9DA", "#C994C7", "#DF65B0", "#DD1C77", "#980043"]

tx_county_colors = []
tx_bins = np.linspace(0, max(tx_county_rates) + 1, 6)
tx_color_bins = np.digitize(tx_county_rates, tx_bins)

for idx in tx_color_bins:
    tx_county_colors.append(colors[idx])


TOOLS="pan,wheel_zoom,box_zoom,reset,hover,save,tap"

source_tx_maps = ColumnDataSource(data=dict(
    x=tx_county_xs,
    y=tx_county_ys,
    color=tx_county_colors,
    name=tx_county_names,
    rate=tx_county_rates,
    prod=tx_county_prods
))

tx_unemp_color_mapper = LogColorMapper(palette=palette1)

fig_tx_unemp = figure(title='Texas unemployment data for %s, %d' % (month_dict[cur_month], cur_year), toolbar_location="left",tools=TOOLS,
           plot_width=500, plot_height=500)

pyglyph = fig_tx_unemp.patches('x', 'y',source=source_tx_maps,
          fill_color={'field': 'prod', 'transform': tx_unemp_color_mapper},
          fill_alpha=0.7,
          line_color="white", line_width=0.5,
         # set visual properties for selected glyphs
          selection_color="firebrick",

        # set visual properties for non-selected glyphs
       nonselection_fill_alpha=0.2,
        nonselection_fill_color="blue",
        nonselection_line_color="firebrick",
        nonselection_line_alpha=1.0)


hover_tx = fig_tx_unemp.select(HoverTool)
hover_tx.point_policy = "follow_mouse"
hover_tx.tooltips = [
    ("Name", "@name"),
    ("Unemployment rate", "@rate%"),
    ("(Long, Lat)", "($x, $y)"),
]


tx_prod_color_mapper = LogColorMapper(palette=palette)

fig_tx_prods = figure(title='Texas production data for %s, %d' % (month_dict[cur_month], cur_year), toolbar_location="left",tools=TOOLS,
           plot_width=500, plot_height=500)

pyglyph_prod = fig_tx_prods.patches('x', 'y',source=source_tx_maps,
          fill_color={'field': 'prod', 'transform': tx_prod_color_mapper},
          fill_alpha=0.7, line_color="white", line_width=0.5,
         # set visual properties for selected glyphs
          selection_color="firebrick",

        # set visual properties for non-selected glyphs
       nonselection_fill_alpha=0.2,
        nonselection_fill_color="blue",
        nonselection_line_color="firebrick",
        nonselection_line_alpha=1.0)


hover_prod = fig_tx_prods.select(HoverTool)
hover_prod.point_policy = "follow_mouse"
hover_prod.tooltips = [
    ("Name", "@name"),
    ("Production", "@prod bbls"),
    ("(Long, Lat)", "($x, $y)"),
]

cur_tx_county = 'Andrews County, TX'
source_tx_oil = ColumnDataSource(data=dict(
    date=tx_oil.index,
    oil_prod=tx_oil[cur_tx_county]
))

fig1_tx = figure(title = 'Employment vs Oil prices for ' + cur_tx_county, x_axis_type='datetime',plot_width=700, plot_height=400,toolbar_location='left',tools=TOOLS)

source_tx_figures = ColumnDataSource(dict(
    date = tx_unemp.index,
    unemp = tx_unemp[cur_tx_county],
    lab_force = tx_lab_force[cur_tx_county]
))


fig1_tx.circle('Date','WTI',source=source_oil_price,legend="Oil Price, $",selection_color='red',nonselection_fill_color='grey',nonselection_fill_alpha=0.2)
fig1_tx.line('Date','WTI',source=source_oil_price,legend="Oil Price, $")
fig1_tx.xaxis.axis_label='Date'
fig1_tx.yaxis.axis_label='Oil Price, $ (month avg.)'
fig1_tx.y_range = Range1d(start=0,end=150)

# Adding second y axis for unemployment
fig1_tx.extra_y_ranges['unemp'] =  Range1d(start=0, end=50)
fig1_tx.add_layout(LinearAxis(y_range_name="unemp", axis_label='Unemployment Rate (%)'),'right')

# Adding third y axis for labor force
fig1_tx.extra_y_ranges['labforce']= Range1d(start=max(100,min(tx_lab_force[cur_tx_county])-1000),end=max(tx_lab_force[cur_tx_county])+1000)
fig1_tx.add_layout(LogAxis(y_range_name="labforce", axis_label='Labor Force (log)'),'right')

fig1_tx.circle('date','unemp', source=source_tx_figures,y_range_name="unemp",legend="Unemployment rate (%)",color='orange')
fig1_tx.line('date','unemp',source=source_tx_figures,y_range_name="unemp",legend="Unemployment rate (%)",color='orange')

fig1_tx.circle('date','lab_force', source=source_tx_figures,y_range_name="labforce",legend="Labor Force (log)",color='green')
fig1_tx.line('date','lab_force',source=source_tx_figures,y_range_name="labforce",legend="Labor Force (log)",color='green')
fig1_tx.legend.location='top_left'
fig1_tx.legend.label_text_font_size='8pt'

fig2_tx = figure(title='Employment vs Oil production for ' + cur_tx_county, x_axis_type='datetime',plot_width=700, plot_height=400,toolbar_location='left',tools=TOOLS)
fig2_tx.circle('date','oil_prod',source=source_tx_oil,legend='Oil production (bbls)',hover_color='red',selection_color='red',nonselection_fill_color='grey',nonselection_fill_alpha=0.2)
fig2_tx.xaxis.axis_label='Date'
fig2_tx.yaxis.axis_label='Oil Production (bbls)'
fig2_tx.y_range = Range1d(start=max(0,min(tx_oil[cur_tx_county])-1000),end=max(tx_oil[cur_tx_county])+1000)

# Adding second y axis for unemployment
fig2_tx.extra_y_ranges['unemp'] =  Range1d(start=0, end=50)
fig2_tx.add_layout(LinearAxis(y_range_name="unemp", axis_label='Unemployment Rate (%)'),'right')

# Adding third y axis for labor force
fig2_tx.extra_y_ranges['labforce']= Range1d(start=max(100,min(tx_lab_force[cur_tx_county])-1000),end=max(tx_lab_force[cur_tx_county]+1000))
fig2_tx.add_layout(LogAxis(y_range_name="labforce", axis_label='Labor Force (log)'),'right')

fig2_tx.circle('date','unemp', source=source_tx_figures,y_range_name="unemp",legend="Unemployment rate (%)",color='orange')
fig2_tx.line('date','unemp',source=source_tx_figures,y_range_name="unemp",legend="Unemployment rate (%)",color='orange')

fig2_tx.circle('date','lab_force', source=source_tx_figures,y_range_name="labforce",legend="Labor Force (log)",color='green')
fig2_tx.line('date','lab_force',source=source_tx_figures,y_range_name="labforce",legend="Labor Force (log)",color='green')
fig2_tx.legend.location='top_left'
fig2_tx.legend.label_text_font_size='8pt'

fig3_tx = figure(title='Employment vs S&P 500 for ' + cur_tx_county, x_axis_type='datetime',plot_width=700, plot_height=400,toolbar_location='left',tools=TOOLS)
fig3_tx.circle('Date','SP500',source=source_sp500,legend='S&P 500 index',hover_color='red',selection_color='red',nonselection_fill_color='grey',nonselection_fill_alpha=0.2)
fig3_tx.xaxis.axis_label='Date'
fig3_tx.yaxis.axis_label='S&P 500 index'
fig3_tx.y_range = Range1d(start=0,end=max(sp500['SP500']))

# Adding second y axis for unemployment
fig3_tx.extra_y_ranges['unemp'] =  Range1d(start=0, end=50)
fig3_tx.add_layout(LinearAxis(y_range_name="unemp", axis_label='Unemployment Rate (%)'),'right')

# Adding third y axis for labor force
fig3_tx.extra_y_ranges['labforce']= Range1d(start=max(100,min(tx_lab_force[cur_tx_county])-1000),end=max(tx_lab_force[cur_tx_county]+1000))
fig3_tx.add_layout(LogAxis(y_range_name="labforce", axis_label='Labor Force (log)'),'right')

fig3_tx.circle('date','unemp', source=source_tx_figures,y_range_name="unemp",legend="Unemployment rate (%)",color='orange')
fig3_tx.line('date','unemp',source=source_tx_figures,y_range_name="unemp",legend="Unemployment rate (%)",color='orange')

fig3_tx.circle('date','lab_force', source=source_tx_figures,y_range_name="labforce",legend="Labor Force (log)",color='green')
fig3_tx.line('date','lab_force',source=source_tx_figures,y_range_name="labforce",legend="Labor Force (log)",color='green')
fig3_tx.legend.location='top_left'
fig3_tx.legend.label_text_font_size='8pt'


def tx_fig_callback_tap(attr, old, new):
    try:
        # The index of the selected glyph is : new['1d']['indices'][0]
        selections = new['1d']['indices']
        patch_name = source_tx_maps.data['name'][selections[0]]
        source_tx_figures.data = dict(
            date = tx_unemp.index,
            unemp = tx_unemp[patch_name],
            lab_force = tx_lab_force[patch_name]
        )
        source_tx_oil.data = dict(
            date=tx_oil.index,
            oil_prod=tx_oil[patch_name]
        )
    except:
        selections = old['1d']['indices']
        patch_name = source_tx_maps.data['name'][selections[0]]
        source_tx_figures.data = dict(
            date = tx_unemp.index,
            unemp = tx_unemp[patch_name],
            lab_force = tx_lab_force[patch_name]
        )
        source_tx_oil.data = dict(
            date=tx_oil.index,
            oil_prod=tx_oil[patch_name]
        )

    fig1_tx.title.text = 'Employment vs Oil prices for ' + patch_name
    fig2_tx.title.text = 'Employment vs Oil production for ' + patch_name
    fig3_tx.title.text = 'Employment vs S&P 500 for ' + patch_name
    fig2_tx.y_range.start=max(0, min(tx_oil[patch_name])- 1000)
    fig2_tx.y_range.end = max(tx_oil[patch_name]) + 1000

    fig1_tx.extra_y_ranges['labforce'].start = max(100, min(tx_lab_force[patch_name]) - 1000)
    fig1_tx.extra_y_ranges['labforce'].end = max(tx_lab_force[patch_name] + 1000)
    fig2_tx.extra_y_ranges['labforce'].start=max(100, min(tx_lab_force[patch_name]) - 1000)
    fig2_tx.extra_y_ranges['labforce'].end=max(tx_lab_force[patch_name] + 1000)
    fig3_tx.extra_y_ranges['labforce'].start = max(100, min(tx_lab_force[patch_name]) - 1000)
    fig3_tx.extra_y_ranges['labforce'].end = max(tx_lab_force[patch_name] + 1000)


pyglyph.data_source.on_change('selected',tx_fig_callback_tap)
pyglyph_prod.data_source.on_change('selected',tx_fig_callback_tap)

# Make a slider object: slider
tx_slider_yr = Slider(title='Year', start=1990, end=2016, step=1, value=cur_year)

# Make a slider object: slider
tx_slider_month = Slider(title='Month', start=1, end=12, step=1, value=cur_month)

def tx_update_plot_yr(attr, old, new):
    # Assign the value of the slider: new_year
    new_year = tx_slider_yr.value
    new_month = tx_slider_month.value

    new_date = pd.to_datetime({'year': [new_year], 'month': [new_month], 'day': [1]})
    new_rates = tx_unemp.loc[new_date].values[0]
    new_prods = tx_oil.loc[new_date].values[0]

    new_county_colors = []
    new_bins = np.linspace(0, max(new_rates) + 1, 6)
    new_color_bins = np.digitize(new_rates, new_bins)

    for idx in new_color_bins:
        new_county_colors.append(colors[idx])

    # Set new_data
    new_data = dict(
        x=tx_county_xs,
        y=tx_county_ys,
        color=new_county_colors,
        name=tx_county_names,
        rate=new_rates,
        prod=new_prods
    )

    # Assign new_data to: source.data
    source_tx_maps.data = new_data

    # Add title to figure: plot.title.text
    fig_tx_unemp.title.text = 'Texas unemployment data for %s, %d' % (month_dict[new_month],new_year)

    # Add title to figure: plot.title.text
    fig_tx_prods.title.text = 'Texas production data for %s, %d' % (month_dict[new_month], new_year)


# Attach the callback to the 'value' property of slider
tx_slider_yr.on_change('value', tx_update_plot_yr)

# Attach the callback to the 'value' property of slider
tx_slider_month.on_change('value', tx_update_plot_yr)

tx_col1 = column([tx_slider_yr,tx_slider_month,fig_tx_unemp, fig_tx_prods])
tx_col2 = column([fig1_tx,fig2_tx,fig3_tx])
#tx_row1 = row(tx_col1,tx_col2)
#tx_row2 = row(fig1_tx,fig2_tx,fig3_tx)
tx_layout = row(tx_col1,tx_col2)

#show(layout)
curdoc().add_root(tx_layout)