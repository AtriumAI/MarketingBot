from re import error
import pandas as pd
from pandas.api.types import is_any_real_numeric_dtype, is_string_dtype
from plotly_graphs import plotly_single_column_numeric, plotly_column2_non_number, plotly_label_number

# This will catch numbers that are being represented as objects
def series_is_numbers(series):
   if is_any_real_numeric_dtype(series):
       return True
   try:
       pd.to_numeric(series)
       return True
   except Exception as e:
       return False

def plotly_dispatch(results, st):
    # Single column
    if len(results.columns) == 1:
        if series_is_numbers(results.iloc[:, 0]):
            plotly_single_column_numeric(results, st)
        else:
            st.write("Cannot create a bar chart with a single non-numeric column.")
    # Second column is not number type
    elif not series_is_numbers(results.iloc[:, 1]):
        print(results.dtypes)
        print(results)
        plotly_column2_non_number(results, st)
    # First column is string type and second column is number type
    elif is_string_dtype(results.iloc[:, 0]) and series_is_numbers(results.iloc[:, 1]):
        plotly_label_number(results, st)
