library(tidyverse)
library(rworldmap)
library(ggplot2)
library(dplyr)
library(RColorBrewer)
library(rnaturalearth)
library(rnaturalearthdata)
library(sf)
library(extrafont)
library(wordcloud)
library(wordcloud2)
library(igraph)
library(ggraph)
library(bibliometrix)

df <- read.csv("df.csv", stringsAsFactors = FALSE)

mapped_data <- joinCountryData2Map(df, joinCode = "NAME", nameJoinColumn = "pais")
par(mar = c(0, 0, 1, 0))
mapCountryData(
  mapped_data,
  nameColumnToPlot = "freq",
  catMethod = "fixedWidth",
  colourPalette = "heat",
  oceanCol = "lightblue",
  missingCountryCol = "gray"
)
legend("bottomleft", legend = names(attr(mapped_data, "table")$freq), fill = "heat", cex = 0.7)

world_map <- ne_countries(scale = "medium", returnclass = "sf")
df$pais <- tolower(df$pais)
world_map$pais <- tolower(world_map$name)
world_map <- left_join(world_map, df, by = "pais")
world_map$freq[is.na(world_map$freq)] <- 0

ggplot(world_map) +
  geom_sf(aes(fill = freq), color = "black") +
  geom_sf_text(aes(label = freq), size = 3) +
  scale_fill_gradientn(colors = brewer.pal(9, "YlGnBu"), na.value = "grey90", name = "freq") +
  theme_minimal() +
  theme(legend.position = "bottom", panel.grid = element_blank(), axis.ticks = element_blank(), axis.text = element_blank()) +
  coord_sf()

wcl <- read.csv("terminos_frecuencia.csv", stringsAsFactors = FALSE)
wcl$pasted <- paste0(wcl$words, ":(", wcl$freq, ")")

wordcloud(wcl$pasted, wcl$freq, scale = c(8, .5), min.freq = 3, max.words = Inf,
          random.order = FALSE, random.color = TRUE, rot.per = 0,
          colors = "black", ordered.colors = FALSE, use.r.layout = TRUE, fixed.asp = FALSE)

wordcloud2::wordcloud2(data.frame(wcl$pasted, wcl$freq), size = 1, minSize = 0.1,
                       color = "white", minRotation = 0, maxRotation = 0, shuffle = FALSE,
                       backgroundColor = "gray", shape = "square")

trend_df <- read.csv("terminos_por_periodo.csv", stringsAsFactors = FALSE)

trend_long <- trend_df %>%
  pivot_longer(cols = c("q1", "mediana", "q3"), names_to = "cuantil", values_to = "periodo")

ggplot(trend_long, aes(x = periodo, y = reorder(termino, frecuencia), size = frecuencia)) +
  geom_line(aes(group = termino), color = "gray") +
  geom_point(aes(color = frecuencia)) +
  scale_size_continuous(range = c(2, 6)) +
  scale_color_gradient(low = "blue", high = "red") +
  theme_minimal() +
  labs(x = "periodo", y = "termino")

fuentes <- lapply(list.files(pattern = "\\.(txt|bib)$"), function(f) {
  if (grepl("\\.bib$", f)) convert2df(f, dbsource = "scopus", format = "bibtex") else convert2df(f)
})
M <- do.call(mergeDbSources, c(fuentes, remove.duplicated = TRUE))

mapa_tematico1 <- thematicMap(M, field = "DE")
mapa_tematico1$clusters

mapa_tematico <- mapa_tematico1$clusters

mean_centrality <- mean(mapa_tematico$centrality)
mean_density <- mean(mapa_tematico$density)
centrality_limit <- max(abs(mapa_tematico$centrality - mean_centrality))
density_limit <- max(abs(mapa_tematico$density - mean_density))

ggplot(mapa_tematico, aes(x = centrality, y = density, size = freq, label = name, color = color)) +
  geom_point(alpha = 0.6) +
  geom_text(aes(label = name), hjust = 0.5, vjust = 1.5) +
  scale_size_continuous(range = c(2, 15)) +
  scale_color_identity() +
  theme_minimal() +
  theme(legend.position = "none") +
  geom_hline(yintercept = mean_density, linetype = "dashed") +
  geom_vline(xintercept = mean_centrality, linetype = "dashed") +
  coord_cartesian(
    xlim = c(mean_centrality - centrality_limit, mean_centrality + centrality_limit),
    ylim = c(mean_density - density_limit, mean_density + density_limit)
  )

themevlo <- thematicEvolution(M, field = "DE", years = c(2020), n = 250,
                              minFreq = 5, size = 0.3, ngrams = 1, stemming = FALSE,
                              n.labels = 3, repel = TRUE, cluster = "walktrap")

evolucion <- themevlo$Data %>%
  mutate(CL1 = gsub("--.*", "", CL1), CL2 = gsub("--.*", "", CL2))

grafo <- graph_from_data_frame(evolucion)

ggraph(grafo, layout = "bipartite") +
  geom_edge_link(aes(edge_alpha = Inc_Weighted), show.legend = FALSE) +
  geom_node_point(aes(filter = (name %in% unique(evolucion$CL1)), x = 0), size = 6) +
  geom_node_point(aes(filter = !(name %in% unique(evolucion$CL1)), x = 1), size = 6) +
  geom_node_text(aes(filter = (name %in% unique(evolucion$CL1)), x = 0, label = name), hjust = 1, size = 5) +
  geom_node_text(aes(filter = !(name %in% unique(evolucion$CL1)), x = 1, label = name), hjust = 0, size = 5) +
  theme_void() +
  theme(legend.position = "none")

nodos_1 <- unique(data.frame(name = themevlo$Data$CL1, type = 1))
nodos_2 <- unique(data.frame(name = themevlo$Data$CL2, type = 2))
nodos <- rbind(nodos_1, nodos_2)
aristas <- data.frame(from = themevlo$Data$CL1, to = themevlo$Data$CL2, weight = themevlo$Data$Inc_Weighted)
grafo2 <- graph_from_data_frame(aristas, vertices = nodos, directed = FALSE)
V(grafo2)$type <- ifelse(V(grafo2)$name %in% nodos_1$name, TRUE, FALSE)

ggraph(grafo2, layout = "bipartite") +
  geom_edge_link(aes(edge_alpha = weight), show.legend = FALSE) +
  geom_node_point(aes(color = as.factor(type)), size = 6) +
  geom_node_text(aes(label = name), hjust = 1, size = 3, nudge_x = -0.05) +
  theme_void() +
  theme(legend.position = "none")

plotThematicEvolution(themevlo$Nodes, themevlo$Edges, measure = "inclusion", min.flow = 1)
