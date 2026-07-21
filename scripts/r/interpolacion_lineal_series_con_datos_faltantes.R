df <- df

df$variable_incompleta[df$variable_incompleta == 'X'] <- NA
df$variable_incompleta <- as.numeric(df$variable_incompleta)
df$variable_incompleta <- approx(x = df$anio, y = df$variable_incompleta, xout = df$anio)$y

print(df)
