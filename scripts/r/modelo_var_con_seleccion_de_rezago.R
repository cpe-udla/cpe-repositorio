library(vars)
library(tseries)
library(forecast)
library(urca)
library(highcharter)

df <- df

variables <- setdiff(names(df), names(df)[1])

layout(matrix(seq_along(variables), ncol = 2))
for (v in variables) plot.ts(df[[v]], main = v, ylab = "", xlab = "")

for (v in variables) print(adf.test(df[[v]]))

df_diff <- as.data.frame(lapply(df[variables], diff))
df_diff <- df_diff[-1, ]

for (v in names(df_diff)) print(adf.test(df_diff[[v]]))

ts1 <- ts(df_diff)

plot.ts(ts1)

VARselect(ts1, lag.max = 24, type = "const")

modelo_var <- VAR(ts1, p = 3, ic = "AIC", lag.max = 5)
summary(modelo_var)
