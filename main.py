#%%

import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import numpy as np
import plotly.graph_objs as go

#%%
data = pd.read_csv('assets/covid19_maroc.csv')
data.head()

#%%

## Check for messing values
msv= data.isnull().sum()
available_values= data.notnull().sum()
msv_perc= round((data.isnull().sum()*100)/len(data),1)
msv_perc= msv_perc.astype(str) + ' %'
msv_df= pd.DataFrame({'feature': msv.index, 'available values': available_values.values,'Missing values': msv.values, 'MVs Percentage': msv_perc.values})
msv_df

#%%

## remove empty variables (100% missing values)
data=data.drop(['group','infected_by', 'contact_number'], axis=1)

#%%

#Convert Dates to pandas datetime
data["confirmed_date"] =pd.to_datetime(data.confirmed_date)
data["released_date"] =pd.to_datetime(data.released_date)
data["deceased_date"] =pd.to_datetime(data.deceased_date)

#%%

# fill null value of infection_reason with an Unknown
data.infection_reason.fillna("Unknown", inplace = True)

#%%
## group and sort cases, deaths and releases
day_cases = data.confirmed_date.value_counts()
day_deaths = data.deceased_date.value_counts()
day_releases = data.released_date.value_counts()
##day counts for daily cases
day_count = (day_cases.index)[-1]-(day_cases.index)[0]
## days range
days = pd.date_range((day_cases.index)[0], (day_cases.index)[-1], freq="D")
for i in days:
    if i not in day_cases.index:
        day_cases = day_cases.append(pd.Series([0], index=[i]))
    if i not in day_deaths.index:
        day_deaths = day_deaths.append(pd.Series([0], index=[i]))
    if i not in day_releases.index:
        day_releases = day_releases.append(pd.Series([0], index=[i]))


#sorting
day_cases = day_cases.sort_index()
day_deaths = day_deaths.sort_index()
day_releases = day_releases.sort_index()
#%%
##daily traces
go_day_cases = go.Bar(x = day_cases.index,
                      y = day_cases.values,
                      name = "daily cases", marker_color='rgb(243, 156, 18)')
go_day_deaths = go.Bar(x = day_deaths.index,
                       y = day_deaths.values,
                       name = "daily death", marker_color='rgb(231, 76, 60)')
go_day_releases = go.Bar(x = day_releases.index,
                         y = day_releases.values,
                         name = "daily releases", marker_color='rgb(46, 204, 113)')

#%%
#accumulate values for i in cases_daily.index:
accumulate_cases= day_cases.cumsum()
accumulate_deaths= day_deaths.cumsum()
accumulate_releases= day_releases.cumsum()

##Accumulate daily traces
go_accumulate_cases = go.Bar(x = accumulate_cases.index,
                             y = accumulate_cases.values,
                             name = "Accumulate daily death",
                             marker_color='rgb(243, 156, 18)')
go_accumulate_deaths = go.Bar(x = accumulate_deaths.index,
                              y = accumulate_deaths.values,
                               name = "Accumulate daily death",
                              marker_color='rgb(231, 76, 60)')
go_accumulate_releases = go.Bar(x = accumulate_releases.index,
                                y = accumulate_releases.values,
                               name = "Accumulate daily death",
                                marker_color='rgb(46, 204, 113)')


# Bar chart
df_sub = pd.DataFrame(data[data.state == "isolated"].province.value_counts())
df_sub.columns = ["isolated"]
lon = [-7.965636,-8.365910,-6.235980,-4.658982,-5.433289,-2.556609,-5.330057,-6.267116,-8.634435,-13.178729,-9.875821]
lat = [33.134399,31.736601,34.140537,33.726610,35.197405,33.991792,31.258876,32.492824,29.992446,27.131740,28.581917]
deceased = data[data.state == "Deceased"].province.value_counts()
exit = data[data.state == "Exit"].province.value_counts()
df_sub["lon"] = lon
df_sub["lat"] = lat
df_sub["deceased"] = deceased
df_sub["exit"] = exit
df_sub.fillna(0, inplace=True)


#traces for a bar chart
go_isolated = go.Bar(
    x = df_sub.index,
    y = df_sub.isolated,
    name = "isolated"
)
go_deceased = go.Bar(
    x = df_sub.index,
    y = df_sub.deceased,
    name = "deceased"
)
go_exit = go.Bar(
    x = df_sub.index,
    y = df_sub.exit,
    name = "exit"
)



#%%
## agregate values
data.replace(to_replace = ["local"], value = "Local", inplace = True)
data.replace(to_replace = ["imported"], value = "Imported", inplace = True)
#Pei chart for infection Reason
infection_reasons = data.infection_reason.value_counts()
go_infection_reasons = go.Pie(labels = infection_reasons.index, values = infection_reasons.values)

#%%
#Dash Application
app = dash.Dash(__name__)
app.css.config.serve_locally = False
## add bootstrap
app.css.append_css({
    'external_url':"https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
})

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Img(src="/assets/UM6p.png")
                ], className="col-4"),
                html.Div([
                    html.Span("Covid19 au Maroc"),
                    html.Img(src="/assets/virus.png")
                ], className="col-8 covid_text"),
            ], className="row"),
        ], className="container"),
    ], className="header"),

    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(
                        figure ={"data":[go_day_cases],
                                 "layout":{"title":"Cases per Day"}
                                 },
                    ),
                    ], className="col-6"),
                html.Div([
                    dcc.Graph(
                        figure ={"data":[go_accumulate_cases],
                                 "layout":{"title":"Cumulative cases"}
                                 },
                    ),
                ], className="col-6")
            ], className="row"),
            html.Div([
                html.Div([
                    dcc.Graph(
                        figure ={"data":[go_day_deaths],
                                 "layout":{"title":"Deaths per Day"}
                                 },
                    ),
                ], className="col-6"),
                html.Div([
                    dcc.Graph(
                        figure ={"data":[go_accumulate_deaths],
                                 "layout":{"title":"Cumulative Deaths"}
                                 },
                    ),
                ], className="col-6")
            ], className="row"),
            html.Div([
                html.Div([
                    dcc.Graph(
                        figure ={"data":[go_day_releases],
                                 "layout":{"title":"Releases per Day"}
                                 },
                    ),
                ], className="col-6"),
                html.Div([
                    dcc.Graph(
                        figure ={"data":[go_accumulate_releases],
                                 "layout":{"title":"Cumulative Releases"}
                                 },
                    ),
                ], className="col-6")
            ], className="row"),
            html.Div([
                html.Div([
                    dcc.Graph(
                        figure ={"data":[go_infection_reasons],
                                 "layout":{"title":"Infection Reason"}
                                 },
                    ),
                ], className="col-4"),
                html.Div([
                    dcc.Graph(
                        id="bar_chart",
                        figure={
                            "data": [go_isolated, go_deceased, go_exit],

                            "layout": {"title": "Bar Chart"}
                        }
                    ),
                ],className="col-8")
            ], className="row")
        ], className="container")
    ], className="dashb"),

    html.Div([
        "Realisé par: Omar El Alaoui"
    ], className="footer")
])


if __name__=="__main__" :
    app.run_server(debug = True)

