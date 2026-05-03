#!/usr/bin/env python
from core.metrics import gini, top_concentration
import pandas as pd

# Criar dados de teste
df = pd.DataFrame({
    'stars': [1, 2, 3, 4, 5, 10, 20, 50, 100, 200]
})

# Testar Gini
gini_val = gini(df['stars'])
print(f"Gini: {gini_val}")

# Testar top_concentration
top10 = top_concentration(df, col="stars", top=0.1)
print(f"Top 10%: {top10}")

print("Teste das métricas concluído!")