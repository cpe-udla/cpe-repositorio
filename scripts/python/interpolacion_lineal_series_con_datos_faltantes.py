import pandas as pd
import numpy as np

df = df

df["variable_incompleta"] = df["variable_incompleta"].replace("X", np.nan).astype(float)
df["variable_incompleta"] = df.set_index("anio")["variable_incompleta"].interpolate(method="index").values

print(df)
