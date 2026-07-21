import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
from matplotlib.colors import LinearSegmentedColormap

cmap = LinearSegmentedColormap.from_list("valor", ["red", "yellow", "green"])

df = pd.read_csv("df.csv", index_col=0)

df_long = df.reset_index().melt(id_vars="index", var_name="dimension", value_name="valor")
df_long = df_long.rename(columns={"index": "unidad"})

orden = df_long.groupby("unidad")["valor"].mean().sort_values(ascending=False).index
tabla = df_long.pivot(index="unidad", columns="dimension", values="valor").loc[orden]

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(tabla.values, cmap=cmap, vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(len(tabla.columns)))
ax.set_xticklabels(tabla.columns, rotation=45, ha="right")
ax.set_yticks(range(len(tabla.index)))
ax.set_yticklabels(tabla.index)
fig.colorbar(im, ax=ax, label="valor")
fig.tight_layout()

geo_df = gpd.read_file("geo.shp")
df["unidad"] = df.index.str.upper()
geo_df = geo_df.merge(df, left_on="NOM_UNIDAD", right_on="unidad", how="left")

fig, ax = plt.subplots(figsize=(10, 10))
geo_df.plot(column="variable_1", cmap=cmap, vmin=0, vmax=1, edgecolor="white", legend=True, ax=ax)
ax.set_axis_off()

geo_sub = geo_df[geo_df["variable_1"].notna()].copy()
geo_sub["centroide"] = geo_sub.geometry.centroid

fig, ax = plt.subplots(figsize=(10, 10))
geo_sub.plot(column="variable_1", cmap=cmap, vmin=0, vmax=1, edgecolor="white", alpha=0.85, legend=True, ax=ax)
for _, fila in geo_sub.iterrows():
    ax.annotate(fila["NOM_UNIDAD"], xy=(fila["centroide"].x, fila["centroide"].y), fontsize=6, ha="center")
cx.add_basemap(ax, crs=geo_sub.crs, source=cx.providers.CartoDB.Positron)
ax.set_axis_off()

geo_df.to_file("geo_resultado.shp")
