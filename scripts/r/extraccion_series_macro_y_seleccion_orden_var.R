library(quantmod)
library(tidyquant)
library(tidyverse)
library(gridExtra)
library(ggplot2)
library(dplyr)
library(knitr)
library(vars)

start_date <- "2002-01-01"
end_date <- "2023-01-01"

getSymbols("SERIE_1", src = "FRED", from = start_date, to = end_date)

serie_a <- tq_get("SERIE_A", from = start_date, to = end_date, get = "economic.data")
serie_b <- tq_get("SERIE_B", from = start_date, to = end_date, get = "economic.data")
serie_c <- tq_get("SERIE_C", from = start_date, to = end_date, get = "economic.data")
serie_d <- tq_get("SERIE_D", from = start_date, to = end_date, get = "economic.data")
serie_e <- tq_get("SERIE_E", from = start_date, to = end_date, get = "economic.data")

plot(serie_a$price, type = "l")
lines(serie_b$price)
lines(serie_c$price)
lines(serie_d$price)
lines(serie_e$price)

df <- as.data.frame(cbind(
  fecha = as.Date(serie_a$date),
  var_a = serie_a$price,
  var_b = serie_b$price,
  var_c = serie_c$price,
  var_d = serie_d$price,
  var_e = serie_e$price
))

write.csv(df, "df.csv")

nombres_columnas <- setdiff(names(df), "fecha")

plots <- lapply(nombres_columnas, function(col) {
  ggplot(df, aes(x = fecha, y = .data[[col]])) +
    geom_line() +
    labs(title = col, x = "fecha", y = "variacion")
})

do.call(grid.arrange, c(plots, ncol = 4))

resumen_df <- df %>%
  select(-fecha) %>%
  summarise_all(list(
    media = ~mean(., na.rm = TRUE),
    mediana = ~median(., na.rm = TRUE),
    min = ~min(., na.rm = TRUE),
    max = ~max(., na.rm = TRUE)
  ))

resumen_df$variable <- rownames(resumen_df)
rownames(resumen_df) <- NULL
resumen_df <- resumen_df %>% select(variable, everything())

kable(resumen_df, format = "html")

var_df <- df[, nombres_columnas[1:4]]
exogenas <- df[, nombres_columnas[5:length(nombres_columnas)]]

var_df1 <- var_df %>% mutate(across(everything(), ~ifelse(is.na(.), mean(., na.rm = TRUE), .)))
exo_df <- exogenas %>% mutate(across(everything(), ~ifelse(is.na(.), mean(., na.rm = TRUE), .)))

var_order <- VARselect(var_df1, lag.max = 15, type = "both", exogen = exo_df)

print(var_order$selection)
var_order$criteria
