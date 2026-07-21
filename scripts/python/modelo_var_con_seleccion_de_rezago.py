import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.api import VAR

df = df

variables = [c for c in df.columns if c != df.columns[0]]

fig, axes = plt.subplots(len(variables), 1, figsize=(8, 2 * len(variables)))
for ax, v in zip(axes, variables):
    ax.plot(df[v])
    ax.set_title(v)

for v in variables:
    print(v, adfuller(df[v].dropna())[1])

df_diff = df[variables].diff().dropna()

for v in df_diff.columns:
    print(v, adfuller(df_diff[v])[1])

plt.figure()
for v in df_diff.columns:
    plt.plot(df_diff[v], label=v)
plt.legend()

modelo = VAR(df_diff)
seleccion = modelo.select_order(maxlags=24)
print(seleccion.summary())

resultado = modelo.fit(3, ic="aic")
print(resultado.summary())
