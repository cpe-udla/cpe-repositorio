import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import bibliometrics as bm

M = bm.merge_sources([bm.load("scopus.csv"), bm.load("wos.csv")], remove_duplicated=True)

s = bm.biblio_analysis(M, sep=";")
print(s.summary())

res = bm.thematic_map(M, field="ID", n=10, minfreq=10, size=0.5, repel=True)
res["graph"].plot()

R = bm.author_prod_over_time(M)

M.to_csv("df_bibliometrico.csv", sep=";")

bm.coupling_map(M, analysis="documents", field="CR", n=100,
                impact_measure="local", minfreq=10, size=0.5, repel=True)

df = pd.read_csv("df.csv")
wc = WordCloud(width=1000, height=700).generate_from_frequencies(dict(zip(df["term"], df["freq"])))

plt.figure(figsize=(10, 7))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.show()
