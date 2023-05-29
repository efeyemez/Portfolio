"""
Install these python packages to run the application.
python -m pip install pandas dash plotly

"""


# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import plotly.express as px


# Create a dash application
app = dash.Dash(__name__)

app.config.suppress_callback_exceptions = True

# Read the airline data into pandas dataframe
df =  pd.read_csv('https://github.com/efeyemez/Portfolio/raw/main/Datasets/airline_65k.csv',
                            encoding = "ISO-8859-1",
                            dtype={'Div1Airport': str, 'Div1TailNum': str, 
                                   'Div2Airport': str, 'Div2TailNum': str})


# List of years 
year_list = [i for i in range(2005, 2021, 1)]

"""Compute graph data for creating yearly airline performance report 

Function that takes airline data as input and create 5 dataframes based on the
grouping condition to be used for plotting charts and graphs

Argument:    
    df: Filtered dataframe    
Returns:
   Dataframes to create graph. 
"""

def compute_data_choice_1(df):
    # Cancellation Category Count
    bar_data = df.groupby(['Month','CancellationCode'])['Flights'].sum().reset_index()
    # Average flight time by reporting airline
    line_data = df.groupby(['Month','Reporting_Airline'])['AirTime'].mean().reset_index()
    # Diverted Airport Landings
    div_data = df[df['DivAirportLandings'] != 0.0]
    # Source state count
    map_data = df.groupby(['OriginState'])['Flights'].sum().reset_index()
    # Destination state count
    tree_data = df.groupby(['DestState', 'Reporting_Airline'])['Flights'].sum().reset_index()
    return bar_data, line_data, div_data, map_data, tree_data


"""Compute graph data for creating yearly airline delay report

This function takes in airline data and selected year as an input and performs
computation for creating charts and plots.

Arguments:
    df: Input airline data.    
Returns:
    Computed average dataframes for carrier delay, weather delay, NAS delay, security delay, and late aircraft delay.
"""

def compute_data_choice_2(df):
    # Compute delay averages
    avg_car = df.groupby(['Month','Reporting_Airline'])['CarrierDelay'].mean().reset_index()
    avg_weather = df.groupby(['Month','Reporting_Airline'])['WeatherDelay'].mean().reset_index()
    avg_NAS = df.groupby(['Month','Reporting_Airline'])['NASDelay'].mean().reset_index()
    avg_sec = df.groupby(['Month','Reporting_Airline'])['SecurityDelay'].mean().reset_index()
    avg_late = df.groupby(['Month','Reporting_Airline'])['LateAircraftDelay'].mean().reset_index()
    return avg_car, avg_weather, avg_NAS, avg_sec, avg_late


# Application layout
app.layout = html.Div(children=[ 
                                # Add title to the dashboard
                                html.H1("US Domestic Airline Flights Performance",
                                        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),

                                # Dropdown Creation

                                # Create an outer division 
                                html.Div([
                                    # Add a division
                                    html.Div([
                                        # Create a division for adding dropdown helper text for report type
                                        html.Div(
                                            [
                                            html.H2('Report Type:', style={'margin-right': '2em'}),
                                            ]
                                        ),
                                        # Add a dropdown
                                        dcc.Dropdown(id='input-type', 
                                                    options=[
                                                            {'label': 'Yearly Airline Performance Report', 'value': 'OPT1'},
                                                            {'label': 'Yearly Airline Delay Report', 'value': 'OPT2'}
                                                            ],
                                                    placeholder='<Select a report type>',
                                                    style={'width':'80%', "padding-left": 3, "font-size": 20, 'text-align-last': 'center'})

                                    # Place them next to each other using the division style
                                    ], style={'display':'flex'}),
                                    
                                   # Add next division 
                                   html.Div([
                                       # Create a division for adding dropdown helper text for choosing year
                                        html.Div(
                                            [
                                            html.H2('Choose Year:', style={'margin-right': '2em'})
                                            ]
                                        ),
                                        # Add a dropdown
                                        dcc.Dropdown(id='input-year', 
                                                     # Update dropdown values using list comprehension
                                                     options=[{'label': i, 'value': i} for i in year_list],
                                                     placeholder="<Select a year>",
                                                     style={'width':'80%', 'padding':3, 'font-size': 20, 'text-align-last' : 'center'}),
                                            # Place them next to each other using the division style
                                            ], style={'display': 'flex'}),  
                                          ]),
                                
                                # Add Computed graphs
                                html.Div([ ], id='plot1'),

                                # Add a division with two empty divisions inside
                                html.Div([
                                        html.Div([ ], id='plot2'),
                                        html.Div([ ], id='plot3')
                                ], style={'display': 'flex'}),
                                
                                # Add a division with two empty divisions inside
                                html.Div([
                                        html.Div([ ], id='plot4'),
                                        html.Div([ ], id='plot5')
                                ], style={'display': 'flex'}),
                                ])

# Callback function definition

# Add 5 output components
@app.callback( [Output(component_id='plot1', component_property='children'),
                Output(component_id='plot2', component_property='children'),
                Output(component_id='plot3', component_property='children'),
                Output(component_id='plot4', component_property='children'),
                Output(component_id='plot5', component_property='children')],
               [Input(component_id='input-type', component_property='value'),
                Input(component_id='input-year', component_property='value')],

               # Holding output state until user enters all the form information.
               # In this case, it will be chart type and year
               [State("plot1", 'children'), State("plot2", "children"),
                State("plot3", "children"), State("plot4", "children"),
                State("plot5", "children")]
               )

# Add computation to callback function and return graph
def get_graph(chart, year, children1, children2, c3, c4, c5):
      
        # Select data
        filtered_df =  df[df['Year']==int(year)]

        # This covers chart type 1
        if chart == 'OPT1':
            # Compute required information for creating graph from the data
            bar_data, line_data, div_data, map_data, tree_data = compute_data_choice_1(filtered_df)
            
            # Number of flights under different cancellation categories
            bar_fig = px.bar(bar_data, x='Month', y='Flights', color='CancellationCode', title='Monthly Flight Cancellation')
            
            # Average flight time by reporting airline
            line_fig = px.line(line_data, x='Month', y='AirTime', color='Reporting_Airline', title='Average Monthly Flight Time (minutes) by Airline')
            
            # Percentage of diverted airport landings per reporting airline
            pie_fig = px.pie(div_data, values='Flights', names='Reporting_Airline', title='% of Flights by Reporting Airline')
            
            # Number of flights flying from each state using choropleth
            map_fig = px.choropleth(map_data,  # Input data
                    locations='OriginState', 
                    color='Flights',  
                    hover_data=['OriginState', 'Flights'], 
                    locationmode = 'USA-states', # Set to plot as US States
                    color_continuous_scale='GnBu',
                    range_color=[0, map_data['Flights'].max()]) 
            map_fig.update_layout(
                    title_text = 'Number of Flights from Origin State',
                    geo_scope='usa') # Plot only the USA instead of globe
            
            # Number of flights flying to each state from each reporting airline
            tree_fig = px.treemap(tree_data, path=['DestState', 'Reporting_Airline'], 
                      values='Flights',
                      color='Flights',
                      color_continuous_scale='RdBu',
                      title='Flight Count by Airline to Destination State')

            # Return dcc.Graph component to the empty division
            return [dcc.Graph(figure=tree_fig), 
                    dcc.Graph(figure=pie_fig),
                    dcc.Graph(figure=map_fig),
                    dcc.Graph(figure=bar_fig),
                    dcc.Graph(figure=line_fig)]

        # This covers chart type 2
        else:

            # Compute required information for creating graph from the data
            avg_car, avg_weather, avg_NAS, avg_sec, avg_late = compute_data_choice_2(filtered_df)
            
            # Create graphs
            carrier_fig = px.line(avg_car, x='Month', y='CarrierDelay', color='Reporting_Airline',
                                  title='Average Carrier Delay Time (minutes) by Airline')

            weather_fig = px.line(avg_weather, x='Month', y='WeatherDelay', color='Reporting_Airline',
                                  title='Average Weather Delay Time (minutes) by Airline')

            nas_fig = px.line(avg_NAS, x='Month', y='NASDelay', color='Reporting_Airline',
                              title='Average NAS Delay Time (minutes) by Airline')

            sec_fig = px.line(avg_sec, x='Month', y='SecurityDelay', color='Reporting_Airline',
                              title='Average Security Delay Time (minutes) by Airline')

            late_fig = px.line(avg_late, x='Month', y='LateAircraftDelay', color='Reporting_Airline',
                               title='Average Late Aircraft Delay Time (minutes) by Airline')
            
            return[dcc.Graph(figure=carrier_fig), 
                   dcc.Graph(figure=weather_fig), 
                   dcc.Graph(figure=nas_fig), 
                   dcc.Graph(figure=sec_fig), 
                   dcc.Graph(figure=late_fig)]


# Run the app
if __name__ == '__main__':
    app.run_server()