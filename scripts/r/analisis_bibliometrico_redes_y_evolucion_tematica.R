library(bibliometrix)
library(wordcloud2)

fuentes <- lapply(list.files(pattern = "\\.txt$"), convert2df, dbsource = "wos", format = "plaintext")
M <- do.call(mergeDbSources, c(fuentes, remove.duplicated = TRUE))

results <- biblioAnalysis(M)
summary(results, k = 20, pause = FALSE, width = 130)
plot(results, k = 10, pause = FALSE)

topCited_papers <- as.data.frame(results$MostCitedPapers)

author_keywords <- as.data.frame(results$DE)
author_keywords <- subset(author_keywords, author_keywords$Freq > 15)

wordcloud2(author_keywords, color = c("Black", "Gray", "Red", "Green"), size = 1,
           fontWeight = "normal", rotateRatio = 0)

M1 <- metaTagExtraction(M, Field = "CR_AU", sep = ";")
NetMatrix <- biblioNetwork(M1, analysis = "co-citation", network = "authors", sep = ";")
net <- networkPlot(NetMatrix, n = dim(NetMatrix)[1], type = "auto",
                   size = 10, size.cex = TRUE, edgesize = 1,
                   labelsize = 0.45, cluster = "none", remove.isolates = FALSE)
net2VOSviewer(net, vos.path = NULL)

nexus <- thematicEvolution(M, field = "ID", years = c("2014", "2016", "2018"), n = 100, minFreq = 5)
plotThematicEvolution(nexus$Nodes, nexus$Edges)

tm <- thematicMap(M, field = "AB", n = 250, minfreq = 3, ngrams = 3, stemming = TRUE,
                  size = 0.5, n.labels = 1, repel = TRUE, remove.terms = NULL, synonyms = NULL)
resT <- thematicMap(M, field = "TI", n = 500, minfreq = 3, size = 0.5, repel = TRUE)

WA <- cocMatrix(M, Field = "AU", type = "sparse", sep = ";")
plot(WA)

NetMatrix <- biblioNetwork(M, analysis = "co-occurrences", network = "keywords", sep = ";")
net <- networkPlot(NetMatrix, n = 30, type = "auto", labelsize = 1)
