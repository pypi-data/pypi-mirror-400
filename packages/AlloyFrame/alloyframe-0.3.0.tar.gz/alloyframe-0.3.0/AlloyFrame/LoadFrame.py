import pandas as pd
from AlloyFrame.AlloyFrame import DataFrame


def read_clipboard(*args, **kwargs):
    df = pd.read_clipboard(*args, **kwargs)
    return DataFrame(df)


def read_csv(*args, **kwargs):
    df = pd.read_csv(*args, **kwargs)
    return DataFrame(df)


def read_excel(*args, **kwargs):
    df = pd.read_excel(*args, **kwargs)
    return DataFrame(df)


def read_feather(*args, **kwargs):
    df = pd.read_feather(*args, **kwargs)
    return DataFrame(df)


def read_fwf(*args, **kwargs):
    df = pd.read_fwf(*args, **kwargs)
    return DataFrame(df)


def read_gbq(*args, **kwargs):
    df = pd.read_gbq(*args, **kwargs)
    return DataFrame(df)


def read_hdf(*args, **kwargs):
    df = pd.read_hdf(*args, **kwargs)
    return DataFrame(df)


def read_html(*args, **kwargs):
    df = pd.read_html(*args, **kwargs)
    return DataFrame(df)


def read_json(*args, **kwargs):
    df = pd.read_json(*args, **kwargs)
    return DataFrame(df)


def read_orc(*args, **kwargs):
    df = pd.read_orc(*args, **kwargs)
    return DataFrame(df)


def read_parquet(*args, **kwargs):
    df = pd.read_parquet(*args, **kwargs)
    return DataFrame(df)


def read_pickle(*args, **kwargs):
    df = pd.read_pickle(*args, **kwargs)
    return DataFrame(df)


def read_sas(*args, **kwargs):
    df = pd.read_sas(*args, **kwargs)
    return DataFrame(df)


def read_spss(*args, **kwargs):
    df = pd.read_spss(*args, **kwargs)
    return DataFrame(df)


def read_sql(*args, **kwargs):
    df = pd.read_sql(*args, **kwargs)
    return DataFrame(df)


def read_sql_query(*args, **kwargs):
    df = pd.read_sql_query(*args, **kwargs)
    return DataFrame(df)


def read_sql_table(*args, **kwargs):
    df = pd.read_sql_table(*args, **kwargs)
    return DataFrame(df)


def read_stata(*args, **kwargs):
    df = pd.read_stata(*args, **kwargs)
    return DataFrame(df)


def read_table(*args, **kwargs):
    df = pd.read_table(*args, **kwargs)
    return DataFrame(df)


def read_xml(*args, **kwargs):
    df = pd.read_xml(*args, **kwargs)
    return DataFrame(df)


def concat(*args, **kwargs):
    df = pd.concat(*args, **kwargs)
    return DataFrame(df)
