import numpy as np
import pandas as pd
from scipy.spatial.distance import mahalanobis

df = df

columnas_logicas = df.select_dtypes(include="bool").columns
df[columnas_logicas] = df[columnas_logicas].astype(float)
df = df.fillna(0)

datos = df.iloc[:, 1:]
medias = datos.mean()
covarianzas = datos.cov()
inv_cov = np.linalg.inv(covarianzas.values)

df["distancia_mahalanobis"] = datos.apply(lambda fila: mahalanobis(fila, medias, inv_cov), axis=1)

media_dist = df["distancia_mahalanobis"].mean()
sd_dist = df["distancia_mahalanobis"].std()
df["z"] = (df["distancia_mahalanobis"] - media_dist) / sd_dist

df.to_csv("resultado_mahalanobis.csv", sep=";")
