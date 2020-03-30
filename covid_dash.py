import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import datetime

# ext_style = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)
app.config['suppress_callback_exceptions'] = True   

covid_tracker_states_daily = "http://covidtracking.com/api/states/daily.csv"
def data_loader(covid_tracker_states_daily):
    data =  pd.read_csv(covid_tracker_states_daily)
    data["date"] = pd.to_datetime(data["dateChecked"])
    data["doy"] = data["date"].apply(lambda x: x.timetuple().tm_yday)
    data["logPos"] = np.log10(data["positive"].replace(0,1))
    data.sort_values(by="date",inplace=True)
    return data

data = data_loader(covid_tracker_states_daily)

plot_values = {"Positive tests":"positive",
               "Total tests":"totalTestResults",
               "Percent increase (rolling day-to-day)":"perc_increase",
               "Percent increase (five-day rolling average)":"perc_five_increase",
               "Percent deaths":"perc_death",
               "Percent hospitalized":"perc_hosp"}



mostrecent = sorted(data["date"],reverse=True)[0]

tmp = data.loc[data["date"] == mostrecent][["state","positive"]].dropna()
tmp["state"].values

state_map_fig = px.choropleth(locations=tmp["state"].values,
                                locationmode="USA-states",
                                color=np.log10(tmp["positive"].replace(0,1)).values,
                                scope="usa")

app.layout = html.Div([
    html.H1('COVID-19 statistics from covidtracking.com'),
    dcc.Tabs(id="plot-tabs", 
    value='state-positive', 
    children = [
        dcc.Tab(label='State Stats over Time', value='state-positive'),
        dcc.Tab(label='US State Heatmap', value='us-state-map'),
        
            ]),
    html.Div(id='plot-tabs-contents') # generate from render content function below, as callback.
])

@app.callback(Output('plot-tabs-contents', 'children'),
              [Input('plot-tabs', 'value')])
def render_tab_content(tab):
    if tab == "state-positive":
        return html.Div([
            html.Div([
                html.H2("States over Time"),
                dcc.Dropdown(id="states",
                            options=[{'label':i,'value':i} for i in data["state"].unique()],
                            value = ["MD"],
                            multi=True),
                dcc.RadioItems(
                    id='yaxis-type',
                    options=[{'label': i, 'value': i} for i in ['linear', 'log']],
                    value='linear',
                    labelStyle={'display': 'inline-block'}),
                dcc.Dropdown(
                    id='xaxis-value',
                    options=[{'label':i[0],'value':i[1]} for i in plot_values.items()],
                    value="positive",
                    multi=False
                )
                ],
                style = {'width':'25%'}
                ),
            html.Div([
                html.Div([
                    dcc.Graph(id="state-pos-fig")
                    ],
                    style = {"width":"60%","float":"center","display":"inline-block"}),
                html.Div([
                    html.Figcaption(["this is a test figure caption.  State positive tests as reported by ... "])],
                    style= {"width":"40%","float":"right","display":"inline-block"})
            ])
        ])

    elif tab == "us-state-map":
        return html.Div([
            html.H2("State Heatmap of Positive Tests"),
            dcc.Graph(id="us-state-map-fig",figure=state_map_fig)])

@app.callback(Output('state-pos-fig','figure'),
              [Input('states','value'),
               Input('yaxis-type','value'),
               Input('xaxis-value','value')])
def create_state_positive(states,yscale,xvalue):
    tmp = data.loc[data["state"].isin(states)]
    fig = px.line(tmp,x="date",y=xvalue,color="state",labels=dict(date="",positive="positive cases"))
    fig.update_yaxes(type = yscale,linecolor="black",gridcolor="grey")
    fig.update_xaxes(tickangle = -45, tickmode = "linear",linecolor="black")
    fig.update_traces(mode = "markers+lines")
    fig.update_traces(marker=dict(size=15))
    fig.update_layout(plot_bgcolor = "#fffff8",
                        paper_bgcolor="#fffff8")

    annotations = []
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.2,
                              xanchor='center', yanchor='top',
                              text="Data current as of {}".format(datetime.strftime(mostrecent,"%Y-%m-%d")),
                              font=dict(family='Arial',
                                        size=12,
                                        color='rgb(150,150,150)'),
                              showarrow=False))

    fig.update_layout(annotations=annotations)
    return fig

# TODO: css styling.
# TODO: chart showing top 5 states for trailing 3 day increase.
# TODO: data update, need to wrap "serve layout" with a data loader function.
# TODO: positive cases normalized by population for state agg

if __name__ == "__main__":
    app.run_server(debug=True)