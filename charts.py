import pandas as pd
import plotly.express as px
def get_numeric_columns(df):

    if df is None or df.empty:
        return []

    return df.select_dtypes(
        include="number"
    ).columns.tolist()


def get_text_columns(df):

    if df is None or df.empty:
        return []

    return df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()


def get_date_columns(df):

    if df is None or df.empty:
        return []

    date_columns = []

    for column in df.columns:

        if pd.api.types.is_datetime64_any_dtype(
            df[column]
        ):
            date_columns.append(column)
            continue

        if df[column].dtype == "object":

            converted = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            if converted.notna().mean() >= 0.7:
                date_columns.append(column)

    return date_columns
def bar_chart(df):

    numeric = get_numeric_columns(df)
    text = get_text_columns(df)

    if not numeric or not text:
        return None

    x_column = text[0]
    y_column = numeric[0]

    chart_df = df[
        [x_column, y_column]
    ].dropna()

    if chart_df.empty:
        return None

    chart_df = (
        chart_df
        .groupby(
            x_column,
            as_index=False
        )[y_column]
        .sum()
    )

    chart_df = chart_df.nlargest(
        20,
        y_column
    )

    return px.bar(
        chart_df,
        x=x_column,
        y=y_column,
        title=f"{y_column} by {x_column}"
    )

def line_chart(df):

    numeric = get_numeric_columns(df)
    text = get_text_columns(df)

    if not numeric or not text:
        return None

    # Use the first text column and the Commission column
    x_column = text[0]

    if "Commission" in df.columns:
        y_column = "Commission"
    else:
        y_column = numeric[-1]

    chart_df = df[[x_column, y_column]].copy()

    chart_df[y_column] = pd.to_numeric(
        chart_df[y_column],
        errors="coerce"
    )

    chart_df = chart_df.dropna()

    if chart_df.empty:
        return None

    # Preserve the original PDF row order
    figure = px.line(
        chart_df,
        x=x_column,
        y=y_column,
        markers=True,
        title=f"{y_column} by {x_column}"
    )

    figure.update_layout(
        xaxis_title=x_column,
        yaxis_title=y_column
    )

    return figure
def pie_chart(df):

    numeric = get_numeric_columns(df)
    text = get_text_columns(df)

    if not numeric or not text:
        return None

    category_column = text[0]
    value_column = numeric[0]

    chart_df = df[
        [category_column, value_column]
    ].dropna()

    if chart_df.empty:
        return None

    chart_df = (
        chart_df
        .groupby(
            category_column,
            as_index=False
        )[value_column]
        .sum()
    )

    if len(chart_df) < 2:
        return None

    if len(chart_df) > 10:

        chart_df = chart_df.nlargest(
            10,
            value_column
        )

    return px.pie(
        chart_df,
        names=category_column,
        values=value_column,
        title=f"{value_column} Distribution"
    )
def scatter_chart(df):

    numeric = get_numeric_columns(df)

    if len(numeric) < 2:
        return None

    x_column = numeric[0]
    y_column = numeric[1]

    chart_df = df[
        [x_column, y_column]
    ].copy()

    chart_df[x_column] = pd.to_numeric(
        chart_df[x_column],
        errors="coerce"
    )

    chart_df[y_column] = pd.to_numeric(
        chart_df[y_column],
        errors="coerce"
    )

    chart_df = chart_df.dropna()

    if chart_df.empty:
        return None

    figure = px.scatter(
        chart_df,
        x=x_column,
        y=y_column,
        title=f"{y_column} vs {x_column}"
    )

    # Connect the points with a line
    figure.update_traces(
        mode="lines+markers"
    )

    return figure

def make_charts(df):

    charts = {}

    if df is None or df.empty:
        return charts

    bar = bar_chart(df)
    if bar is not None:
        charts["Bar Chart"] = bar

    line = line_chart(df)
    if line is not None:
        charts["Line Chart"] = line

    pie = pie_chart(df)
    if pie is not None:
        charts["Pie Chart"] = pie

    return charts
def make_chart(df):

    charts = make_charts(df)

    if not charts:
        return None

    return next(
        iter(charts.values())
    )
