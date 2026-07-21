import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

df = df

def extract_text_from_url(url):
    try:
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.content, "html.parser")
        return " ".join(p.get_text() for p in soup.find_all("p"))
    except Exception:
        return None

df["text"] = df["url"].apply(extract_text_from_url)

stop_es = stopwords.words("spanish")
vectorizer = CountVectorizer(stop_words=stop_es, lowercase=True, strip_accents="unicode")
dtm = vectorizer.fit_transform(df["text"].dropna())

term_frequency = pd.Series(dtm.sum(axis=0).A1, index=vectorizer.get_feature_names_out())
term_frequency = term_frequency.sort_values(ascending=False)

term_df = term_frequency.reset_index()
term_df.columns = ["term", "freq"]

fig, ax = plt.subplots()
term_df.head(10).plot.barh(x="term", y="freq", ax=ax, legend=False)
ax.invert_yaxis()

wc = WordCloud(width=1000, height=600, background_color="white", colormap="Dark2")
wc.generate_from_frequencies(term_frequency.to_dict())

plt.figure(figsize=(10, 6))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")

bigram_vectorizer = CountVectorizer(ngram_range=(2, 2), stop_words=stop_es)
bigram_dtm = bigram_vectorizer.fit_transform(df["text"].dropna())
bigram_freq = pd.Series(bigram_dtm.sum(axis=0).A1, index=bigram_vectorizer.get_feature_names_out())

umbral = bigram_freq.quantile(0.95)
bigram_edges = [tuple(b.split(" ")) for b in bigram_freq[bigram_freq > umbral].index]

grafo = nx.Graph()
grafo.add_edges_from(bigram_edges)

fig, ax = plt.subplots(figsize=(10, 8))
pos = nx.spring_layout(grafo, seed=123)
nx.draw(grafo, pos, with_labels=True, node_color="gray", node_size=300, ax=ax)

analizador = SentimentIntensityAnalyzer()
df["sentiment"] = df["text"].dropna().apply(lambda t: analizador.polarity_scores(t)["compound"])

resumen = df.groupby(df.index).agg(
    avg_sentiment=("sentiment", "mean"),
    positive_count=("sentiment", lambda s: (s > 0).sum()),
    neutral_count=("sentiment", lambda s: (s == 0).sum()),
    negative_count=("sentiment", lambda s: (s < 0).sum()),
)

fig, ax = plt.subplots()
ax.bar(resumen.index, resumen["avg_sentiment"], color="steelblue")

fig, ax = plt.subplots()
df["sentiment"].plot.kde(ax=ax, color="lightblue")

clasificacion = resumen.melt(id_vars=[], value_vars=["positive_count", "neutral_count", "negative_count"],
                             var_name="sentiment_type", value_name="count", ignore_index=False).reset_index()

fig, ax = plt.subplots()
for tipo, grupo in clasificacion.groupby("sentiment_type"):
    ax.bar(grupo["index"], grupo["count"], label=tipo)
ax.legend()
plt.xticks(rotation=90)

edges_df = df_red
grafo2 = nx.from_pandas_edgelist(edges_df, source="from", target="to", create_using=nx.DiGraph)

plt.figure(figsize=(10, 8))
nx.draw(grafo2, with_labels=True, node_size=300)

plt.show()
