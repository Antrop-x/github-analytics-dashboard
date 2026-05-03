#!/usr/bin/env python
from services.analysis_service import interpret_dataset, interpret_power_structure
import pandas as pd

# Criar dados de teste
df = pd.DataFrame({
    'appropriation_rate': [0.1, 0.2, 0.15, 0.25, 0.18, 0.12, 0.22, 0.19, 0.14, 0.16],
    'symbolic_density': [0.5, 0.8, 0.6, 0.7, 0.55, 0.65, 0.75, 0.58, 0.62, 0.68],
    'stars': [1, 2, 3, 4, 5, 10, 20, 50, 100, 200]
})

df_heg = pd.DataFrame({
    'name': ['test'],
    'stars': [100],
    'forks': [10],
    'hegemony_index': [110]
})

# Testar interpretação
result = interpret_dataset(df, df_heg, 0.7)

print(f"appropriation_level: {result.appropriation_level}")
print(f"density_level: {result.density_level}")
print(f"inequality_level: {result.inequality_level}")
print(f"gini_coefficient: {result.gini_coefficient}")
print(f"top10_concentration: {result.top10_concentration}")
print(f"power_structure_insights: {result.power_structure_insights}")
print(f"summary (preview): {result.summary[:200]}...")

print("\nTeste da interpretação concluído!")