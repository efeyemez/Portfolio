"""
After visual analysis using the dashboard, we will be able to obtain insights to answer the following questions:

Which site has the highest success rate?
Which payload range(s) has the highest/lowest success rate?
Which orbit has the highest success rate?
"""

"""
Install these python packages to run the application.
python -m pip install pandas dash plotly

"""


# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the wrangled launch data into dataframe
df = pd.read_csv("https://github.com/efeyemez/Portfolio/raw/main/Datasets/SpaceX_Falcon_9/falcon9_wrangled.csv")
max_payload = df['PayloadMass'].max()
min_payload = df['PayloadMass'].min()

df['Class'] = df['Class'].replace({1: 'Success', 0: 'Failure'})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SPACEX LAUNCH RECORDS DASHBOARD',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),

                                # A dropdown list to enable Launch Site selection
                                # The default select value is ALL
                                dcc.Dropdown(id='site-dropdown',
                                             options=[{'label': 'All Sites', 'value': 'ALL'},
                                                      {'label': 'CCSFS SLC 40', 'value': 'CCSFS SLC 40'},
                                                      {'label': 'KSC LC 39A', 'value': 'KSC LC 39A'},
                                                      {'label': 'VAFB SLC 4E', 'value': 'VAFB SLC 4E'}],
                                             value='ALL',
                                             placeholder='<Select a launch site>',
                                             searchable=True),
                                html.Br(),

                                # A pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, shows the Success vs. Failed counts for it
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload Range (kg):"),

                                # A slider to select payload range
                                dcc.RangeSlider(id='payload-slider',min=0,max=16000,
                                                step=1000,value=[min_payload,max_payload]),

                                # A scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


# Callback function for `site-dropdown` as input
# `success-pie-chart` as output

@app.callback(Output(component_id="success-pie-chart", component_property="figure"),
              Input(component_id="site-dropdown", component_property="value"))

def get_pie_chart(entered_site):
    df_pie = df

    if entered_site == 'ALL':
        count_df = df_pie["Class"].value_counts().reset_index()
        count_df.columns = ["Class", 'Count']

        fig = px.pie(count_df, values='Count', names='Class', title='Success Rate of All Launches',
                     category_orders={"Class": ["Success", "Failure"]},
                     labels={'Count': "Count", "Class": "Outcome"})
        return fig

    else:
        fil_df = df_pie[df_pie["LaunchSite"] == entered_site]
        fil_df = fil_df.groupby(["LaunchSite", "Class"]).size().reset_index(name='Count')

        fig = px.pie(fil_df, values="Count", names='Class', title='Success Rate of the Site ' + entered_site,
                     category_orders={"Class": ["Success", "Failure"]},
                     labels={'Count': "Count", "Class": "Outcome"})
        return fig

# Callback function for `site-dropdown` and `payload-slider` as inputs
# `success-payload-scatter-chart` as output

@app.callback(Output(component_id="success-payload-scatter-chart", component_property="figure"),
              [Input(component_id="site-dropdown", component_property="value"),
               Input(component_id="payload-slider", component_property="value")])

def get_scatter_chart(entered_site, entered_payload):
    low, high = (entered_payload[0], entered_payload[1])
    pl_range = df[df["PayloadMass"].between(low, high)]

    if entered_site == 'ALL':
        fig = px.scatter(pl_range, x="PayloadMass", y="Orbit",
                         color="Class",
                         title="Success Graph of Payload vs. Orbit",
                         category_orders={"Class": ["Success", "Failure"]},
                         labels={"PayloadMass": "Payload Mass (kg)",
                                 "Class": "Outcome"})
        fig.update_traces(marker_size=10)
        return fig

    else:
        fil_df = pl_range[pl_range["LaunchSite"] == entered_site]

        fig = px.scatter(fil_df, x="PayloadMass", y="Orbit",
                         color="Class",
                         title="Success Graph of Payload vs. Orbit for the Site " + entered_site,
                         category_orders={"Class": ["Success", "Failure"]},
                         labels={"PayloadMass": "Payload Mass (kg)",
                                 "Class": "Outcome"})
        fig.update_traces(marker_size=10)
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()