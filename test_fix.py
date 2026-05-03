#!/usr/bin/env python
from services.analysis_service import interpret_dataset
import pandas as pd

# Criar dados de teste
df = pd.DataFrame({
    'appropriation_rate': [0.1, 0.2, 0.15],
    'symbolic_density': [0.5, 0.8, 0.6]
})

df_heg = pd.DataFrame({
    'name': ['test'],
    'stars': [100],
    'forks': [10],
    'hegemony_index': [110]
})

# Testar função
result = interpret_dataset(df, df_heg, 0.5)

print(f"✓ appropriation_level: {result.appropriation_level}")
print(f"✓ density_level: {result.density_level}")
print(f"✓ inequality_level: {result.inequality_level}")
print(f"✓ gini_coefficient: {result.gini_coefficient}")
print(f"✓ summary (preview): {result.summary[:100]}...")
print("\nTeste bem-sucedido! Erro NameError foi corrigido.")
