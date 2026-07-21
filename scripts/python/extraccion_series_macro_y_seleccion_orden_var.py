import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
from statsmodels.tsa.api import VAR

start_date = "2002-01-01"
end_date = "2023-01-01"

serie_1 = pdr.DataReader("SERIE_1", "fred", start_date, end_date)

series_ids = ["SERIE_A", "SERIE_B", "SERIE_C", "SERIE_D", "SERIE_E"]
series = {sid: pdr.DataReader(sid, "fred", start_date, end_date) for sid in series_ids}

plt.figure()
for sid, serie in series.items():
    plt.plot(serie.index, serie.iloc[:, 0], label=sid)
plt.legend()

df = pd.concat(series.values(), axis=1)
df.columns = [f"var_{chr(97 + i)}" for i in range(len(series))]
df = df.reset_index().rename(columns={"DATE": "fecha"})

df.to_csv("df.csv", index=False)

columnas = [c for c in df.columns if c != "fecha"]

fig, axes = plt.subplots(5, 4, figsize=(16, 16))
for ax, col in zip(axes.flatten(), columnas):
    ax.plot(df["fecha"], df[col])
    ax.set_title(col)
fig.tight_layout()

resumen_df = df[columnas].agg(["mean", "median", "min", "max"]).T.reset_index()
resumen_df.columns = ["variable", "media", "mediana", "min", "max"]

var_cols = columnas[:4]
exo_cols = columnas[4:]

var_df = df[var_cols].apply(lambda s: s.fillna(s.mean()))
exo_df = df[exo_cols].apply(lambda s: s.fillna(s.mean()))

modelo = VAR(var_df, exog=exo_df)
seleccion = modelo.select_order(maxlags=15)
print(seleccion.summary())
