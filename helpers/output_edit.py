

import pandas as pd


def nbsp_clean(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe = dataframe.copy()
    for col in dataframe.select_dtypes(include='object').columns:
        dataframe[col] = dataframe[col].str.replace('\xa0', ' ', regex=False)
    re_df: pd.DataFrame = dataframe
    return re_df
