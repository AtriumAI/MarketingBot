import pandas as pd
import plotly.graph_objects as go

def plotly_single_column_numeric(results, st):
    df = pd.DataFrame(results)
    fig = go.Figure(data=[go.Bar(x=df.iloc[:, 0], y=df.iloc[:, 0])])
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=list(
                    [
                        dict(
                            label="Ascending",
                            method="update",
                            args=[
                                {
                                    "x": [df.sort_values(df.columns[0])[df.columns[0]]],
                                    "y": [df.sort_values(df.columns[0])[df.columns[0]]],
                                }
                            ],
                        ),
                        dict(
                            label="Descending",
                            method="update",
                            args=[
                                {
                                    "x": [
                                        df.sort_values(df.columns[0], ascending=False)[
                                            df.columns[0]
                                        ]
                                    ],
                                    "y": [
                                        df.sort_values(df.columns[0], ascending=False)[
                                            df.columns[0]
                                        ]
                                    ],
                                }
                            ],
                        ),
                    ]
                ),
                direction="down",
            ),
        ]
    )
    st.plotly_chart(fig, use_container_width=True)


def plotly_column2_non_number(results, st):
    df = pd.DataFrame(results)
    df["MONTH-YEAR"] = df["MONTH"].astype(str) + "-" + df["YEAR"].astype(str)

    fig = go.Figure(data=[go.Bar(x=df["MONTH-YEAR"], y=df["VALUE"])])

    # Add sorting buttons
    fig.update_layout(
        xaxis_title = "Month-Year",
        title = {
            'text': df.columns[1],
            'x': 0.5,
            'xanchor': 'center'
        },
        updatemenus=[
            dict(
                x=0.99, # Position button at top right of chart, otherwise it interferes with the y-axis labels
                y=1,
                active=1, # Default to descending
                buttons=list(
                    [
                        dict(
                            label="Ascending",
                            method="update",
                            args=[
                                {
                                    "x": [df.sort_values("VALUE")["MONTH-YEAR"]],
                                    "y": [df.sort_values("VALUE")["VALUE"]],
                                }
                            ],
                        ),
                        dict(
                            label="Descending",
                            method="update",
                            args=[
                                {
                                    "x": [
                                        df.sort_values("VALUE", ascending=False)[
                                            "MONTH-YEAR"
                                        ]
                                    ],
                                    "y": [
                                        df.sort_values("VALUE", ascending=False)[
                                            "VALUE"
                                        ]
                                    ],
                                }
                            ],
                        ),
                    ]
                ),
                direction="down",
            ),
        ]
    )
    st.plotly_chart(fig, use_container_width=True)
    if len(df["VARIABLE"].unique()) > 1:
        st.write(
            "We recommend running the same prompt for one variable for optimal plots"
        )


def plotly_label_number(results, st):
    df = pd.DataFrame(results)
    fig = go.Figure(data=[go.Bar(x=df.iloc[:, 0], y=df.iloc[:, 1])])
    fig.update_layout(
        xaxis_title = df.columns[0],
        title = {
            'text': df.columns[1],
            'x': 0.5,
            'xanchor': 'center'
        },
        updatemenus=[
            dict(
                x=0.99, # position button at top right of chart
                y=1,
                active=1, # Default to Descending
                buttons=list(
                    [   
                        dict(
                            label="Ascending",
                            method="update",
                            args=[
                                {
                                    "x": [df.sort_values(df.columns[1])[df.columns[0]]],
                                    "y": [df.sort_values(df.columns[1])[df.columns[1]]],
                                }
                            ],
                        ),
                        dict(
                            label="Descending",
                            method="update",
                            args=[
                                {
                                    "x": [
                                        df.sort_values(df.columns[1], ascending=False)[
                                            df.columns[0]
                                        ]
                                    ],
                                    "y": [
                                        df.sort_values(df.columns[1], ascending=False)[
                                            df.columns[1]
                                        ]
                                    ],
                                }
                            ],
                        ),
                    ]
                ),
                direction="down",
            ),
        ]
    )
    st.plotly_chart(fig, use_container_width=True)

def plotly_trend(results, st):
    '''When the result set contains month or year, we want to plot the data as a trend
    over time.
    ''' 
    df = pd.DataFrame(results)
    # Assume that the column that is not Month or Year is the 
    # value to track in the y axis
    for column_name in df.columns:
        if column_name != "MONTH" and column_name != "YEAR":
            value_column = column_name
            break

    if "MONTH" in df.columns and "YEAR" in df.columns:
        df["MONTH-YEAR"] = df["MONTH"].astype(str) + "-" + df["YEAR"].astype(str)
        df.sort_values(by=["YEAR","MONTH"], inplace=True)
        x_axis = df["MONTH-YEAR"]
        x_axis_title = "MONTH-YEAR"
        
    elif "MONTH" in df.columns:
        df.sort_values(by="MONTH", inplace=True)
        x_axis = df["MONTH"]
        x_axis_title = "MONTH"

    else:
        df.sort_values(by="YEAR", inplace=True)
        x_axis = df["YEAR"]
        x_axis_title = "YEAR"

    fig = go.Figure(data=[go.Line(x=x_axis, y=df[value_column])])
    fig.update_layout(
        xaxis_title = x_axis_title,
        title = {
            'text': 'Trend',
            'x': 0.5,
            'xanchor': 'center'
        }
    )
    st.plotly_chart(fig, use_container_width=True)
    
    '''if len(df["VARIABLE"].unique()) > 1:
        st.write(
            "We recommend running the same prompt for one variable for optimal plots"
        )'''