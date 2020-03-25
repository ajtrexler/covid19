import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.express as px

app = dash.Dash(__name__)

covid_tracker_states_daily = "http://covidtracking.com/api/states/daily.csv"
data = pd.read_csv(covid_tracker_states_daily)

data["date"] = pd.to_datetime(data["dateChecked"])
data["doy"] = data["date"].apply(lambda x: x.timetuple().tm_yday)
data["logPos"] = np.log10(data["positive"].replace(0,1))
data.sort_values(by="date",inplace=True)


# build state
#state_fig = 

mostrecent = sorted(data["date"],reverse=True)[0]

tmp = data.loc[data["date"] == mostrecent][["state","positive"]].dropna()
tmp["state"].values

state_map_fig = px.choropleth(locations=tmp["state"].values,
                                locationmode="USA-states",
                                color=np.log10(tmp["positive"].replace(0,1)).values,
                                scope="usa")

app.layout = html.Div([
    html.H1('COVID-19 statistics from covidtracking.com'),
    dcc.Tabs(id="plot-tabs", value='state-positive', children=[ #setup the tabs.
        dcc.Tab(label='State Positive Tests', value='state-positive'),
        dcc.Tab(label='US State Heatmap', value='us-state-map'),
    ]),
    html.Div(id='plot-tabs-contents') # generate from render content function below, as callback.
])

@app.callback(Output('plot-tabs-contents', 'children'),
              [Input('plot-tabs', 'value')])
def render_content(tab):
    if tab == "state-positive":
        return html.Div([
            html.H2("State Positive Tests over Time"),
            dcc.Graph(id="state-positive-fig",figure="")])

    elif tab == "us-state-map":
        return html.Div([
            html.H2("State Heatmap of Positive Tests"),
            dcc.Graph(id="us-state-map-fig",figure=state_map_fig)])



if __name__ == "__main__":
    app.run_server(debug=True)