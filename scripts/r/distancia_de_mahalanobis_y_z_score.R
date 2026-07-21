library(dplyr)
library(stats)

df <- df

columnas_logicas <- names(df)[sapply(df, is.logical)]
df[columnas_logicas] <- lapply(df[columnas_logicas], as.numeric)
df[is.na(df)] <- 0

medias <- colMeans(df[, -1])
covarianzas <- cov(df[, -1])

distancias_mahalanobis <- apply(df[, -1], 1, function(x) mahalanobis(x, medias, covarianzas))

df$distancia_mahalanobis <- distancias_mahalanobis

media_dist <- mean(df$distancia_mahalanobis)
sd_dist <- sd(df$distancia_mahalanobis)
df$z <- (df$distancia_mahalanobis - media_dist) / sd_dist

write.csv2(df, "resultado_mahalanobis.csv")
