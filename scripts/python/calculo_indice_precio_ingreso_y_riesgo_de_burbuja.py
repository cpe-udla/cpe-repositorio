import pandas as pd
import matplotlib.pyplot as plt

df = df

df["PIR"] = df["var1"] / df["wage"]

promedio_PIR = df["PIR"].mean()
desviacion_PIR = df["PIR"].std()
umbral_riesgo = promedio_PIR + (1.25 * desviacion_PIR)

df["Riesgo"] = df["PIR"].apply(lambda x: "Alto" if x > umbral_riesgo else "Bajo")

plt.plot(df["PIR"], color="red")
plt.show()

df.to_csv("df_riesgo.csv", index=False)
