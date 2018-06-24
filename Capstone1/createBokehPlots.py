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
from bokeh.palettes import Viridis6 as palette1
from bokeh.palettes import Blues8 as palette
from bokeh.models.widgets import Panel
from bokeh.models.widgets import Tabs

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

def create_plots(state,oil_prod,unemp,lab_force):
    target_state = (state)
    state_dict = {'tx':'Texas','nd':'North Dakota','wy':'Wyoming'}

    county_xs = [counties[code]["lons"] for code in counties if counties[code]["state"] in target_state]
    county_ys = [counties[code]["lats"] for code in counties if counties[code]["state"] in target_state]

    county_names = unemp.columns
    county_rates = unemp.loc[cur_date].values[0]
    county_prods = oil_prod.loc[cur_date].values[0]

    TOOLS = "pan,wheel_zoom,box_zoom,reset,hover,save,tap"

    source_maps = ColumnDataSource(data=dict(
        x=county_xs,
        y=county_ys,
        name=county_names,
        rate=county_rates,
        prod=county_prods
    ))

    unemp_color_mapper = LogColorMapper(palette=palette1)

    fig_unemp = figure(title='%s unemployment data for %s, %d' % (state_dict[state], month_dict[cur_month], cur_year),
                          toolbar_location="left", tools=TOOLS,
                          plot_width=500, plot_height=500)

    pyglyph = fig_unemp.patches('x', 'y', source=source_maps,
                                   fill_color={'field': 'rate', 'transform': unemp_color_mapper},
                                   fill_alpha=0.7,
                                   line_color="white", line_width=0.5,
                                   # set visual properties for selected glyphs
                                   selection_color="firebrick",

                                   # set visual properties for non-selected glyphs
                                   nonselection_fill_alpha=0.2,
                                   nonselection_fill_color="blue",
                                   nonselection_line_color="firebrick",
                                   nonselection_line_alpha=1.0)

    hover_unemp = fig_unemp.select(HoverTool)
    hover_unemp.point_policy = "follow_mouse"
    hover_unemp.tooltips = [
        ("Name", "@name"),
        ("Unemployment rate", "@rate%"),
        ("(Long, Lat)", "($x, $y)"),
    ]

    prod_color_mapper = LogColorMapper(palette=palette)

    fig_prods = figure(title='%s production data for %s, %d' % (state_dict[state], month_dict[cur_month], cur_year),
                          toolbar_location="left", tools=TOOLS,
                          plot_width=500, plot_height=500)

    pyglyph_prod = fig_prods.patches('x', 'y', source=source_maps,
                                        fill_color={'field': 'prod', 'transform': prod_color_mapper},
                                        fill_alpha=0.7, line_color="grey", line_width=0.5,
                                        # set visual properties for selected glyphs
                                        selection_color="firebrick",

                                        # set visual properties for non-selected glyphs
                                        nonselection_fill_alpha=0.2,
                                        nonselection_fill_color="blue",
                                        nonselection_line_color="firebrick",
                                        nonselection_line_alpha=1.0)

    hover_prod = fig_prods.select(HoverTool)
    hover_prod.point_policy = "follow_mouse"
    hover_prod.tooltips = [
        ("Name", "@name"),
        ("Production", "@prod bbls"),
        ("(Long, Lat)", "($x, $y)"),
    ]

    cur_county = county_names[0]
    source_oil = ColumnDataSource(data=dict(
        date=oil_prod.index,
        oil_prod=oil_prod[cur_county]
    ))

    fig1 = figure(title='Employment vs Oil prices for ' + cur_county, x_axis_type='datetime', plot_width=700,
                     plot_height=400, toolbar_location='left', tools=TOOLS)

    source_figures = ColumnDataSource(dict(
        date=unemp.index,
        unemp=unemp[cur_county],
        lab_force=lab_force[cur_county]
    ))

    fig1.circle('Date', 'WTI', source=source_oil_price, legend="Oil Price, $", selection_color='red',
                   nonselection_fill_color='grey', nonselection_fill_alpha=0.2)
    fig1.line('Date', 'WTI', source=source_oil_price, legend="Oil Price, $")
    fig1.xaxis.axis_label = 'Date'
    fig1.yaxis.axis_label = 'Oil Price, $ (month avg.)'
    fig1.y_range = Range1d(start=0, end=150)

    # Adding second y axis for unemployment
    fig1.extra_y_ranges['unemp'] = Range1d(start=0, end=50)
    fig1.add_layout(LinearAxis(y_range_name="unemp", axis_label='Unemployment Rate (%)'), 'right')

    # Adding third y axis for labor force
    fig1.extra_y_ranges['labforce'] = Range1d(start=max(100, min(lab_force[cur_county]) - 1000),
                                                 end=max(lab_force[cur_county]) + 1000)
    fig1.add_layout(LogAxis(y_range_name="labforce", axis_label='Labor Force (log)'), 'right')

    fig1.circle('date', 'unemp', source=source_figures, y_range_name="unemp", legend="Unemployment rate (%)",
                   color='orange')
    fig1.line('date', 'unemp', source=source_figures, y_range_name="unemp", legend="Unemployment rate (%)",
                 color='orange')

    fig1.circle('date', 'lab_force', source=source_figures, y_range_name="labforce", legend="Labor Force (log)",
                   color='green')
    fig1.line('date', 'lab_force', source=source_figures, y_range_name="labforce", legend="Labor Force (log)",
                 color='green')
    fig1.legend.location = 'top_left'
    fig1.legend.label_text_font_size = '8pt'

    fig2 = figure(title='Employment vs Oil production for ' + cur_county, x_axis_type='datetime', plot_width=700,
                     plot_height=400, toolbar_location='left', tools=TOOLS)
    fig2.circle('date', 'oil_prod', source=source_oil, legend='Oil production (bbls)', hover_color='red',
                   selection_color='red', nonselection_fill_color='grey', nonselection_fill_alpha=0.2)
    fig2.xaxis.axis_label = 'Date'
    fig2.yaxis.axis_label = 'Oil Production (bbls)'
    fig2.y_range = Range1d(start=max(0, min(oil_prod[cur_county]) - 1000), end=max(oil_prod[cur_county]) + 1000)

    # Adding second y axis for unemployment
    fig2.extra_y_ranges['unemp'] = Range1d(start=0, end=50)
    fig2.add_layout(LinearAxis(y_range_name="unemp", axis_label='Unemployment Rate (%)'), 'right')

    # Adding third y axis for labor force
    fig2.extra_y_ranges['labforce'] = Range1d(start=max(100, min(lab_force[cur_county]) - 1000),
                                                 end=max(lab_force[cur_county] + 1000))
    fig2.add_layout(LogAxis(y_range_name="labforce", axis_label='Labor Force (log)'), 'right')

    fig2.circle('date', 'unemp', source=source_figures, y_range_name="unemp", legend="Unemployment rate (%)",
                   color='orange')
    fig2.line('date', 'unemp', source=source_figures, y_range_name="unemp", legend="Unemployment rate (%)",
                 color='orange')

    fig2.circle('date', 'lab_force', source=source_figures, y_range_name="labforce", legend="Labor Force (log)",
                   color='green')
    fig2.line('date', 'lab_force', source=source_figures, y_range_name="labforce", legend="Labor Force (log)",
                 color='green')
    fig2.legend.location = 'top_left'
    fig2.legend.label_text_font_size = '8pt'

    fig3 = figure(title='Employment vs S&P 500 for ' + cur_county, x_axis_type='datetime', plot_width=700,
                     plot_height=400, toolbar_location='left', tools=TOOLS)
    fig3.circle('Date', 'SP500', source=source_sp500, legend='S&P 500 index', hover_color='red',
                   selection_color='red', nonselection_fill_color='grey', nonselection_fill_alpha=0.2)
    fig3.xaxis.axis_label = 'Date'
    fig3.yaxis.axis_label = 'S&P 500 index'
    fig3.y_range = Range1d(start=0, end=max(sp500['SP500']))

    # Adding second y axis for unemployment
    fig3.extra_y_ranges['unemp'] = Range1d(start=0, end=50)
    fig3.add_layout(LinearAxis(y_range_name="unemp", axis_label='Unemployment Rate (%)'), 'right')

    # Adding third y axis for labor force
    fig3.extra_y_ranges['labforce'] = Range1d(start=max(100, min(lab_force[cur_county]) - 1000),
                                                 end=max(lab_force[cur_county] + 1000))
    fig3.add_layout(LogAxis(y_range_name="labforce", axis_label='Labor Force (log)'), 'right')

    fig3.circle('date', 'unemp', source=source_figures, y_range_name="unemp", legend="Unemployment rate (%)",
                   color='orange')
    fig3.line('date', 'unemp', source=source_figures, y_range_name="unemp", legend="Unemployment rate (%)",
                 color='orange')

    fig3.circle('date', 'lab_force', source=source_figures, y_range_name="labforce", legend="Labor Force (log)",
                   color='green')
    fig3.line('date', 'lab_force', source=source_figures, y_range_name="labforce", legend="Labor Force (log)",
                 color='green')
    fig3.legend.location = 'top_left'
    fig3.legend.label_text_font_size = '8pt'

    def fig_callback_tap(attr, old, new):
        try:
            # The index of the selected glyph is : new['1d']['indices'][0]
            selections = new['1d']['indices']
            patch_name = source_maps.data['name'][selections[0]]
            source_figures.data = dict(
                date=unemp.index,
                unemp=unemp[patch_name],
                lab_force=lab_force[patch_name]
            )
            source_oil.data = dict(
                date=oil_prod.index,
                oil_prod=oil_prod[patch_name]
            )
        except:
            selections = old['1d']['indices']
            patch_name = source_maps.data['name'][selections[0]]
            source_figures.data = dict(
                date=unemp.index,
                unemp=unemp[patch_name],
                lab_force=lab_force[patch_name]
            )
            source_oil.data = dict(
                date=oil_prod.index,
                oil_prod=oil_prod[patch_name]
            )

        fig1.title.text = 'Employment vs Oil prices for ' + patch_name
        fig2.title.text = 'Employment vs Oil production for ' + patch_name
        fig3.title.text = 'Employment vs S&P 500 for ' + patch_name
        fig2.y_range.start = max(0, min(oil_prod[patch_name]) - 1000)
        fig2.y_range.end = max(oil_prod[patch_name]) + 1000

        fig1.extra_y_ranges['labforce'].start = max(100, min(lab_force[patch_name]) - 1000)
        fig1.extra_y_ranges['labforce'].end = max(lab_force[patch_name] + 1000)
        fig2.extra_y_ranges['labforce'].start = max(100, min(lab_force[patch_name]) - 1000)
        fig2.extra_y_ranges['labforce'].end = max(lab_force[patch_name] + 1000)
        fig3.extra_y_ranges['labforce'].start = max(100, min(lab_force[patch_name]) - 1000)
        fig3.extra_y_ranges['labforce'].end = max(lab_force[patch_name] + 1000)

    pyglyph.data_source.on_change('selected', fig_callback_tap)
    pyglyph_prod.data_source.on_change('selected', fig_callback_tap)

    def update_plot_yr(attr, old, new):
        # Assign the value of the slider: new_year
        new_year = slider_yr.value
        new_month = slider_month.value

        new_date = pd.to_datetime({'year': [new_year], 'month': [new_month], 'day': [1]})
        new_rates = unemp.loc[new_date].values[0]
        new_prods = oil_prod.loc[new_date].values[0]

        # Set new_data
        new_data = dict(
            x=county_xs,
            y=county_ys,
            name=county_names,
            rate=new_rates,
            prod=new_prods
        )

        # Assign new_data to: source.data
        source_maps.data = new_data

        # Add title to figure: plot.title.text
        fig_unemp.title.text = '%s unemployment data for %s, %d' % (state_dict[state],month_dict[new_month], new_year)

        # Add title to figure: plot.title.text
        fig_prods.title.text = '%s production data for %s, %d' % (state_dict[state],month_dict[new_month], new_year)


    # Make a slider object: slider
    slider_yr = Slider(title='Year', start=1990, end=2016, step=1, value=cur_year)

    # Attach the callback to the 'value' property of slider
    slider_yr.on_change('value', update_plot_yr)

    # Make a slider object: slider
    slider_month = Slider(title='Month', start=1, end=12, step=1, value=cur_month)

    # Attach the callback to the 'value' property of slider
    slider_month.on_change('value', update_plot_yr)

    return fig_unemp, fig_prods, fig1, fig2, fig3, slider_yr, slider_month

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

fig_tx_unemp, fig_tx_prods, fig1_tx, fig2_tx, fig3_tx, tx_slider_yr, tx_slider_month = create_plots('tx',tx_oil,tx_unemp,tx_lab_force)

tx_col1 = column([tx_slider_yr,tx_slider_month,fig_tx_unemp, fig_tx_prods])
tx_col2 = column([fig1_tx,fig2_tx,fig3_tx])
#tx_row1 = row(tx_col1,tx_col2)
#tx_row2 = row(fig1_tx,fig2_tx,fig3_tx)
tx_layout = row(tx_col1,tx_col2)

# North Dakota maps
nd_oil = pd.read_csv('./OilGasProduction/NorthDakota/NDOilProdCounty.csv')
nd_unemp = pd.read_csv('./Unemployment/nd_unemployment.csv')
nd_lab_force = pd.read_csv('./Unemployment/nd_laborForce.csv')

nd_oil.reset_index(inplace=True)
nd_oil['Date']= pd.to_datetime(nd_oil['Date'])
nd_oil.drop('index',axis=1,inplace=True)
nd_oil = nd_oil.set_index('Date')

nd_unemp['Date']= pd.to_datetime(nd_unemp['Date'])
nd_unemp = nd_unemp.set_index('Date')

nd_lab_force['Date']= pd.to_datetime(nd_lab_force['Date'])
nd_lab_force = nd_lab_force.set_index('Date')

fig_nd_unemp, fig_nd_prods, fig1_nd, fig2_nd, fig3_nd, nd_slider_yr, nd_slider_month = create_plots('nd',nd_oil,nd_unemp,nd_lab_force)

nd_col1 = column([nd_slider_yr,nd_slider_month,fig_nd_unemp, fig_nd_prods])
nd_col2 = column([fig1_nd,fig2_nd,fig3_nd])
#tx_row1 = row(tx_col1,tx_col2)
#tx_row2 = row(fig1_tx,fig2_tx,fig3_tx)
nd_layout = row(nd_col1,nd_col2)

# Wyoming maps
wy_oil = pd.read_csv('./OilGasProduction/Wyoming/WYOilProdCounty.csv')
wy_unemp = pd.read_csv('./Unemployment/wy_unemployment.csv')
wy_lab_force = pd.read_csv('./Unemployment/wy_laborForce.csv')

wy_oil.reset_index(inplace=True)
wy_oil['Date']= pd.to_datetime(wy_oil['Date'])
wy_oil.drop('index',axis=1,inplace=True)
wy_oil = wy_oil.set_index('Date')

wy_unemp['Date']= pd.to_datetime(wy_unemp['Date'])
wy_unemp = wy_unemp.set_index('Date')

wy_lab_force['Date']= pd.to_datetime(wy_lab_force['Date'])
wy_lab_force = wy_lab_force.set_index('Date')

fig_wy_unemp, fig_wy_prods, fig1_wy, fig2_wy, fig3_wy, wy_slider_yr, wy_slider_month = create_plots('wy',wy_oil,wy_unemp,wy_lab_force)

wy_col1 = column([wy_slider_yr,wy_slider_month,fig_wy_unemp, fig_wy_prods])
wy_col2 = column([fig1_wy,fig2_wy,fig3_wy])
#tx_row1 = row(tx_col1,tx_col2)
#tx_row2 = row(fig1_tx,fig2_tx,fig3_tx)
wy_layout = row(wy_col1,wy_col2)

tab1 = Panel(child=tx_layout,title='Texas')
tab2 = Panel(child=nd_layout,title='North Dakota')
tab3 = Panel(child=wy_layout,title='Wyoming')

layout = Tabs(tabs=[tab1, tab2, tab3])
#show(layout)
curdoc().add_root(layout)