import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, grangercausalitytests
from statsmodels.tsa.api import VAR

df = pd.read_csv("df.txt", sep="\t")

variables = [c for c in df.columns if c != df.columns[0]]

fig, axes = plt.subplots(4, 4, figsize=(14, 14))
for ax, v in zip(axes.flatten(), variables):
    ax.plot(df[v])
    ax.set_title(v)

series = {v: np.log(df[v]) for v in variables}

for v, s in series.items():
    while adfuller(s.dropna())[1] > 0.05:
        s = s.diff()
    series[v] = s.dropna()

matriz_est = pd.concat(series.values(), axis=1, keys=series.keys()).dropna()

plt.figure()
for v in variables:
    plt.plot(matriz_est[v], label=v)
plt.legend()

adf_results = pd.Series({v: adfuller(matriz_est[v])[1] for v in variables})

lag_selection = {}
for v in variables:
    modelo = VAR(matriz_est[[v]])
    seleccion = modelo.select_order(maxlags=26)
    lag_selection[v] = seleccion.selected_orders

lag_AIC = pd.DataFrame(lag_selection)

variable_objetivo = variables[0]
otras_variables = [v for v in variables if v != variable_objetivo]
lags = range(1, 20)

registros = []
for otra in otras_variables:
    for lag in lags:
        for direccion, orden_columnas in [("hacia", [variable_objetivo, otra]), ("desde", [otra, variable_objetivo])]:
            resultado = grangercausalitytests(matriz_est[orden_columnas], maxlag=lag, verbose=False)
            p_value = resultado[lag][0]["ssr_ftest"][1]
            registros.append({"objetivo": variable_objetivo, "otra": otra, "lag": lag, "direccion": direccion, "p_value": p_value})

granger_matrix = pd.DataFrame(registros)

orden_optimo = int(pd.Series(np.concatenate([list(v.values()) for v in lag_selection.values()])).mode()[0])

modelo_var = VAR(matriz_est)
resultado_var = modelo_var.fit(orden_optimo)
print(resultado_var.summary())

granger_matrix.to_csv("resultado_causalidad_granger.csv", sep=";", index=False)
lag_AIC.to_csv("resultado_seleccion_lags_aic.csv", sep=";", index=False)
adf_results.to_csv("resultado_test_adf.csv", sep=";")
