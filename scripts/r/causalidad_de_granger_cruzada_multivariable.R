library(tidyverse)
library(car)
library(urca)
library(tseries)
library(lmtest)
library(lubridate)
library(forecast)
library(astsa)
library(vars)
library(mFilter)
library(dynlm)
library(nlme)
library(quantmod)
library(xts)
library(dplyr)

df <- as.data.frame(read_tsv(file = "df.txt"))

variables <- setdiff(names(df), names(df)[1])
frecuencia <- 52
inicio <- c(2008, 1)

series <- lapply(variables, function(v) ts(df[[v]], start = inicio, frequency = frecuencia))
names(series) <- variables

lapply(series, plot)

series_log <- lapply(series, log)

diffs_necesarias <- sapply(series_log, ndiffs)

series_est <- lapply(series_log, function(s) if (ndiffs(s) > 0) diff(s) else s)

sapply(series_est, ndiffs)

ts.plot(do.call(cbind, series_est), col = rainbow(length(series_est)))

adf_results <- as.data.frame(t(sapply(series_est, function(s) adf.test(s)$p.value)))
names(adf_results) <- variables

lag_selection <- lapply(series_est, function(s) VARselect(s, lag.max = 26)$selection)
lag_AIC <- as.data.frame(do.call(cbind, lag_selection))
summary(lag_AIC)

variable_objetivo <- variables[1]
otras_variables <- setdiff(variables, variable_objetivo)
lags <- 1:19

granger_matrix <- expand.grid(objetivo = variable_objetivo, otra = otras_variables, lag = lags, direccion = c("hacia", "desde"))

granger_matrix$p_value <- apply(granger_matrix, 1, function(fila) {
  x <- series_est[[fila[["objetivo"]]]]
  y <- series_est[[fila[["otra"]]]]
  formula_obj <- if (fila[["direccion"]] == "hacia") x ~ y else y ~ x
  grangertest(formula_obj, order = as.numeric(fila[["lag"]]))$`Pr(>F)`[2]
})

write_csv2(granger_matrix, file = "resultado_causalidad_granger.csv")
write_csv2(lag_AIC, file = "resultado_seleccion_lags_aic.csv")
write_csv2(adf_results, file = "resultado_test_adf.csv")
