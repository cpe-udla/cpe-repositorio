library(tidyverse)

df <- df %>%
  mutate(PIR = df$var1 / df$wage)

promedio_PIR <- mean(df$PIR)
desviacion_PIR <- sd(df$PIR)
umbral_riesgo <- promedio_PIR + (1.25 * desviacion_PIR)

df <- df %>%
  mutate(Riesgo = ifelse(PIR > umbral_riesgo, "Alto", "Bajo"))

plot(df$PIR, type = "l", col = "red")

write.csv(df, "df_riesgo.csv", row.names = FALSE)
