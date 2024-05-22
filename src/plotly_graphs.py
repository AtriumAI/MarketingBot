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
    df = pd.DataFrame("results")
    df["MONTH-YEAR"] = df["MONTH"].astype(str) + "-" + df["YEAR"].astype(str)

    fig = go.Figure(data=[go.Bar(x=df["MONTH-YEAR"], y=df["VALUE"])])

    # Add sorting buttons
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
        updatemenus=[
            dict(
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
