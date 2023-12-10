"""
Utility functions to clean raw DataFrame that need more thorough explanation.
"""

import pandas as pd


def filter_invoice_id(series: pd.Series):
    """
    According to data source documentation:
        "InvoiceNo: Invoice number. Nominal. A 6-digit integral number 
        uniquely assigned to each transaction. If this code starts with the 
        letter 'c', it indicates a cancellation."
    Therefore, we filter only records that satisfy this description.

    Argument:
        series [pd.Series]: Series to filter.

    Usage: df.loc[filter_invoice_no(pd.Series)]
    """

    # Strip C suffix of cancelled orders
    stripped_cancellation_suffix = series.str.lstrip("C")
    return (stripped_cancellation_suffix.str.len() == 6) \
        & (stripped_cancellation_suffix.str.isdigit())


def filter_stock_code(series: pd.Series):
    """
    According to data source documentation:
        "StockCode: Product (item) code. Nominal. A 5-digit integral number 
        uniquely assigned to each distinct product."
    Therefore, we filter only records that satisfy this description.

    Argument:
        series [pd.Series]: Series to filter.

    Usage: df.loc[filter_stock_code(df["stock_code"])]
    """

    return (series.str.len() == 5) & (series.str.isdigit())