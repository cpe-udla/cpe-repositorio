library(strucchange)
library(ggplot2)

df <- df

serie1_ts <- ts(df$var1, start = c(1944), frequency = 1)
serie2_ts <- ts(df$var2, start = c(1944), frequency = 1)

plot(serie1_ts)
plot(serie2_ts)

breaks_1 <- breakpoints(serie1_ts ~ 1, h = 15)
breaks_2 <- breakpoints(serie2_ts ~ 1, h = 15)

summary(breaks_1)
summary(breaks_2)

plot(serie1_ts)
lines(fitted(breaks_1), col = "red", lwd = 2)
abline(v = breakdates(breaks_1), col = "blue", lwd = 2, lty = 2)

plot(serie2_ts)
lines(fitted(breaks_2), col = "blue", lwd = 2)
abline(v = breakdates(breaks_2), col = "red", lwd = 2, lty = 2)

modelo_1 <- lm(serie1_ts ~ breakfactor(breaks_1))
modelo_2 <- lm(serie2_ts ~ breakfactor(breaks_2))

summary(modelo_1)
summary(modelo_2)

plot(serie1_ts)
lines(fitted(modelo_1), col = "red", lwd = 2)

plot(serie2_ts)
lines(fitted(modelo_2), col = "blue", lwd = 2)

ggplot(df, aes(x = year, y = var1)) +
  geom_line(color = "black", size = 1) +
  geom_vline(xintercept = breakdates(breaks_1), linetype = "dashed", color = "blue", size = 1) +
  theme_minimal(base_size = 15) +
  scale_y_continuous(labels = scales::comma)
