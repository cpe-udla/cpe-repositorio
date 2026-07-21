import glob
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from wordcloud import WordCloud
import bibliometrics as bm

fuentes = [bm.convert_to_df(f, dbsource="wos", format="plaintext") for f in glob.glob("*.txt")]
M = bm.merge_sources(fuentes, remove_duplicated=True)

results = bm.biblio_analysis(M)
print(results.summary(k=20, width=130))
results.plot(k=10)

top_cited_papers = pd.DataFrame(results.most_cited_papers)

author_keywords = pd.DataFrame(results.de)
author_keywords = author_keywords[author_keywords["Freq"] > 15]

wc = WordCloud(width=1000, height=700, colormap="Dark2").generate_from_frequencies(
    dict(zip(author_keywords["term"], author_keywords["Freq"]))
)
plt.figure(figsize=(10, 7))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")

M1 = bm.meta_tag_extraction(M, field="CR_AU", sep=";")
net_matrix = bm.biblio_network(M1, analysis="co-citation", network="authors", sep=";")
net = bm.network_plot(net_matrix, n=net_matrix.shape[0], size=10, labelsize=0.45, cluster="none", remove_isolates=False)
bm.export_to_vosviewer(net)

nexus = bm.thematic_evolution(M, field="ID", years=[2014, 2016, 2018], n=100, min_freq=5)
bm.plot_thematic_evolution(nexus)

tm = bm.thematic_map(M, field="AB", n=250, minfreq=3, ngrams=3, stemming=True, size=0.5, n_labels=1, repel=True)
res_t = bm.thematic_map(M, field="TI", n=500, minfreq=3, size=0.5, repel=True)

wa = bm.coc_matrix(M, field="AU", type="sparse", sep=";")

net_matrix = bm.biblio_network(M, analysis="co-occurrences", network="keywords", sep=";")
grafo = nx.from_numpy_array(net_matrix)

plt.figure(figsize=(10, 8))
nx.draw(grafo, with_labels=True, node_size=200)
plt.show()
