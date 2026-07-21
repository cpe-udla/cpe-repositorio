import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
import ruptures as rpt

df = df

variables = ["var1", "var2"]
resultados = {}

for v in variables:
    serie = df[v].to_numpy()

    plt.figure()
    plt.plot(df["year"], serie)
    plt.title(v)

    algo = rpt.Binseg(model="l2", min_size=15).fit(serie)
    quiebres = algo.predict(n_bkps=3)

    plt.figure()
    plt.plot(df["year"], serie)
    for q in quiebres[:-1]:
        plt.axvline(df["year"].iloc[q], color="blue", linestyle="--")

    tramos = np.zeros(len(serie), dtype=int)
    limites = [0] + quiebres
    for i in range(len(limites) - 1):
        tramos[limites[i]:limites[i + 1]] = i

    medias_tramo = pd.Series(serie).groupby(tramos).transform("mean")

    plt.figure()
    plt.plot(df["year"], serie)
    plt.plot(df["year"], medias_tramo, color="red")

    resultados[v] = {"quiebres": [df["year"].iloc[q] for q in quiebres[:-1]], "ajuste": medias_tramo}

plt.show()
