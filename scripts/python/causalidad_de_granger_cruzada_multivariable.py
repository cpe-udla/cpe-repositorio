import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, grangercausalitytests
from statsmodels.tsa.api import VAR

df = pd.read_csv("df.txt", sep="\t")

variables = [c for c in df.columns if c != df.columns[0]]

series = {v: np.log(df[v]) for v in variables}

for v, s in series.items():
    while adfuller(s.dropna())[1] > 0.05:
        s = s.diff()
    series[v] = s.dropna()

adf_results = {v: adfuller(s)[1] for v, s in series.items()}
adf_results = pd.Series(adf_results)

lag_selection = {}
for v, s in series.items():
    modelo = VAR(pd.DataFrame(s))
    seleccion = modelo.select_order(maxlags=26)
    lag_selection[v] = seleccion.selected_orders

lag_AIC = pd.DataFrame(lag_selection)

variable_objetivo = variables[0]
otras_variables = [v for v in variables if v != variable_objetivo]
lags = range(1, 20)

registros = []
for otra in otras_variables:
    largo = min(len(series[variable_objetivo]), len(series[otra]))
    datos = pd.concat([series[variable_objetivo].iloc[-largo:], series[otra].iloc[-largo:]], axis=1)
    datos.columns = [variable_objetivo, otra]

    for lag in lags:
        for direccion, orden_columnas in [("hacia", [variable_objetivo, otra]), ("desde", [otra, variable_objetivo])]:
            resultado = grangercausalitytests(datos[orden_columnas], maxlag=lag, verbose=False)
            p_value = resultado[lag][0]["ssr_ftest"][1]
            registros.append({"objetivo": variable_objetivo, "otra": otra, "lag": lag, "direccion": direccion, "p_value": p_value})

granger_matrix = pd.DataFrame(registros)

granger_matrix.to_csv("resultado_causalidad_granger.csv", sep=";", index=False)
lag_AIC.to_csv("resultado_seleccion_lags_aic.csv", sep=";", index=False)
adf_results.to_csv("resultado_test_adf.csv", sep=";")
