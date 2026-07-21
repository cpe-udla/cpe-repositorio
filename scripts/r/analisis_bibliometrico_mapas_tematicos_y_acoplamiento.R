library(bibliometrix)
library(wordcloud2)

biblioshiny()

M <- mergeDbSources(scopus, wos, remove.duplicated = TRUE)

s <- biblioAnalysis(M, sep = ";")
summary(s)

res <- thematicMap(M, field = "ID", n = 10, minfreq = 10, size = 0.5, repel = TRUE)
plot(res$net$graph_pajek)

R <- authorProdOverTime(M)

write.csv2(M, "df_bibliometrico.csv")

couplingMap(M, analysis = "documents", field = "CR", n = 100,
            impact.measure = "local", minfreq = 10, size = 0.5, repel = TRUE)

wordcloud2(df, size = 0.45)
