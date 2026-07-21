import glob
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
from wordcloud import WordCloud
import bibliometrics as bm

df = pd.read_csv("df.csv")

world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
df["pais"] = df["pais"].str.lower()
world["pais"] = world["name"].str.lower()
world = world.merge(df, on="pais", how="left")
world["freq"] = world["freq"].fillna(0)

fig, ax = plt.subplots(figsize=(14, 8))
world.plot(column="freq", cmap="YlGnBu", edgecolor="black", legend=True, ax=ax)
ax.set_axis_off()

wcl = pd.read_csv("terminos_frecuencia.csv")
frecuencias = dict(zip(wcl["words"], wcl["freq"]))

wc = WordCloud(width=1200, height=800, background_color="gray", colormap="gray")
wc.generate_from_frequencies(frecuencias)

plt.figure(figsize=(12, 8))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")

trend_df = pd.read_csv("terminos_por_periodo.csv")
trend_long = trend_df.melt(id_vars=["termino", "frecuencia"], value_vars=["q1", "mediana", "q3"],
                           var_name="cuantil", value_name="periodo")

fig, ax = plt.subplots(figsize=(10, 8))
for termino, grupo in trend_long.groupby("termino"):
    ax.plot(grupo["periodo"], [termino] * len(grupo), color="gray")
    ax.scatter(grupo["periodo"], [termino] * len(grupo), s=grupo["frecuencia"])

fuentes = []
for archivo in glob.glob("*.txt") + glob.glob("*.bib"):
    fuentes.append(bm.convert_to_df(archivo))
M = bm.merge_sources(fuentes, remove_duplicated=True)

mapa_tematico = bm.thematic_map(M, field="DE")

centralidad_media = mapa_tematico["centrality"].mean()
densidad_media = mapa_tematico["density"].mean()

fig, ax = plt.subplots(figsize=(10, 8))
ax.scatter(mapa_tematico["centrality"], mapa_tematico["density"], s=mapa_tematico["freq"], c=mapa_tematico["color"], alpha=0.6)
for _, fila in mapa_tematico.iterrows():
    ax.annotate(fila["name"], (fila["centrality"], fila["density"]))
ax.axhline(densidad_media, linestyle="--")
ax.axvline(centralidad_media, linestyle="--")

evolucion = bm.thematic_evolution(M, field="DE", years=[2020], min_freq=5)
evolucion["CL1"] = evolucion["CL1"].str.replace(r"--.*", "", regex=True)
evolucion["CL2"] = evolucion["CL2"].str.replace(r"--.*", "", regex=True)

grafo = nx.from_pandas_edgelist(evolucion, "CL1", "CL2", edge_attr="Inc_Weighted")

fig, ax = plt.subplots(figsize=(10, 8))
pos = nx.bipartite_layout(grafo, set(evolucion["CL1"]))
nx.draw(grafo, pos, with_labels=True, node_size=400, ax=ax)

bm.plot_thematic_evolution(evolucion, measure="inclusion", min_flow=1)

plt.show()
