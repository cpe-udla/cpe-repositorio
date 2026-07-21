library(ggplot2)
library(reshape2)
library(RColorBrewer)
library(sf)
library(dplyr)
library(ggspatial)
library(ggrepel)
library(rosm)

df <- read.csv("df.csv", stringsAsFactors = FALSE)
rownames(df) <- df[[1]]
df[[1]] <- NULL

df_long <- melt(as.matrix(df))
colnames(df_long) <- c("unidad", "dimension", "valor")

ggplot(df_long, aes(x = dimension, y = reorder(unidad, -valor))) +
  geom_tile(aes(fill = valor), color = "white") +
  scale_fill_gradientn(colors = c("red", "yellow", "green"), limits = c(0, 1), name = "valor") +
  theme_minimal(base_size = 12) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), panel.grid = element_blank())

geo_df <- st_read("geo.shp")
df$unidad <- toupper(rownames(df))
geo_df <- geo_df %>% left_join(df, by = c("NOM_UNIDAD" = "unidad"))

ggplot(geo_df) +
  geom_sf(aes(fill = variable_1), color = "white") +
  scale_fill_gradientn(colors = c("red", "yellow", "green"), limits = c(0, 1), name = "valor") +
  theme_minimal() +
  coord_sf()

geo_sub <- geo_df %>% filter(!is.na(variable_1))
centroides <- st_centroid(geo_sub)

ggplot() +
  annotation_map_tile(type = "cartolight", zoomin = -1) +
  geom_sf(data = geo_sub, aes(fill = variable_1), color = "white", size = 0.2, alpha = 0.85) +
  scale_fill_gradientn(colors = c("red", "yellow", "green"), limits = c(0, 1), name = "valor") +
  geom_text_repel(data = centroides, aes(label = NOM_UNIDAD, geometry = geometry),
                  stat = "sf_coordinates", size = 2.5, box.padding = 0.2, segment.color = "gray50") +
  coord_sf(lims_method = "geometry_bbox") +
  theme_minimal()

st_write(geo_df, "geo_resultado.shp", delete_layer = TRUE)
