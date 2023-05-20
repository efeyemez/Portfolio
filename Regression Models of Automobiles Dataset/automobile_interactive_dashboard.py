"""
Install these python packages to run the application.
python -m pip install pandas dash plotly

"""

# Import required packages
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

app = dash.Dash(__name__)

app.config.suppress_callback_exceptions = True

# Read the automobiles data into pandas dataframe
auto_data =  pd.read_csv('https://github.com/efeyemez/Portfolio/raw/main/Datasets/automobile_tidy.csv',
                            encoding = "ISO-8859-1")


#Layout Section of Dash

app.layout = html.Div(children=[html.H1("Car Automobile Components",
                                        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),


     #outer division starts
     html.Div([

                   # First inner division for  adding dropdown helper text for Selected Drive wheels
                    
                    html.Div(
                        html.H2('Drive Wheels Type:', style={'margin-right': '2em'}),),

                    

                    dcc.Dropdown(id='demo-dropdown',
                                options=[{'label': 'Rear Wheel Drive', 'value': 'rwd'},
                                         {'label': 'Front Wheel Drive', 'value': 'fwd'},
                                         {'label': 'Four Wheel Drive', 'value': '4wd'}],
                                value='rwd'),                           
                    
                    #Second Inner division for adding 2 inner divisions for 2 output graphs 

                    html.Div([

                            html.Div([ ], id='plot1'),
                            html.Div([ ], id='plot2')
                    
                            ], style={'display': 'flex'}),


    ])
    #outer division ends

])
#layout ends

# add @app.callback Decorator

@app.callback( [Output(component_id='plot1', component_property='children'),
                Output(component_id='plot2', component_property='children')],
               Input(component_id='demo-dropdown', component_property='value'))

# define the callback function .

def display_selected_drive_charts(value):

   filtered_df = auto_data[auto_data['drive-wheels']==value]
   grouped_df = filtered_df['body-style'].value_counts().reset_index()
   grouped_df.columns = ['body-style', 'count']

   fig1 = px.pie(grouped_df, values='count', names='body-style', title="Pie Chart", labels={'count':"Count", 'body-style':"Body Style"})
   fig2 = px.bar(grouped_df, x='body-style', y='count', title='Bar Chart', labels={'count':"Count", 'body-style':"Body Style"})

   return [dcc.Graph(figure=fig1),
            dcc.Graph(figure=fig2) ]


if __name__ == '__main__':
    app.run_server()