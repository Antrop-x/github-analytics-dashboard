#!/usr/bin/env python
import pandas as pd
import numpy as np
from core.metrics import gini, top_concentration, domination_index, curva_lorenz
from services.analysis_service import interpret_dataset, interpret_domination

# Dados assimétricos como GitHub (heavy-tailed)
stars_distribution = [10000, 5000, 2000, 500, 100, 50, 10, 5, 2, 1]

# Criar DataFrame de teste
df = pd.DataFrame({
    'name': [f'repo_{i}' for i in range(len(stars_distribution))],
    'appropriation_rate': np.random.uniform(0.1, 0.3, len(stars_distribution)),
    'symbolic_density': np.random.uniform(0.5, 1.0, len(stars_distribution)),
    'stars': stars_distribution,
    'forks': [s // 20 for s in stars_distribution]
})

df_heg = pd.DataFrame({
    'name': [f'repo_{i}' for i in range(len(stars_distribution))],
    'stars': stars_distribution,
    'forks': [s // 20 for s in stars_distribution],
    'hegemony_index': [s + s // 20 for s in stars_distribution]
})

# ==========================================
# TESTES DE MÉTRICAS
# ==========================================

print("=" * 60)
print("TESTE 1: DISTRIBUIÇÃO ASSIMÉTRICA")
print("=" * 60)

# Gini
gini_val = gini(df['stars'])
print(f"Gini: {gini_val:.3f}")

# Top 10%
top10 = top_concentration(df, col="stars", top=0.1)
print(f"Top 10%: {top10:.2%}")

# Correlação log-transformada
log_hegemony = np.log1p(df_heg["hegemony_index"].values)
log_stars = np.log1p(df_heg["stars"].values)
corr_log = float(np.corrcoef(log_hegemony, log_stars)[0, 1])
print(f"Correlação (log): {corr_log:.3f}")

# Domination Index
dom_idx = domination_index(gini_val, top10, corr_log)
dom_level = interpret_domination(dom_idx)
print(f"Índice de Dominação: {dom_idx:.3f} ({dom_level})")

print("\n" + "=" * 60)
print("TESTE 2: INTERPRETAÇÃO COMPLETA")
print("=" * 60)

# Análise completa
result = interpret_dataset(df, df_heg, gini_val)

print(f"Desigualdade: {result.inequality_level}")
print(f"Dominação: {result.domination_level}")
print(f"Top repositório: {result.hegemonic_repo}")
print(f"Hegemonia: {result.hegemony_type}")

print("\n" + "=" * 60)
print("TESTE 3: COERÊNCIA DAS MÉTRICAS")
print("=" * 60)

# Verificar coerência
print(f"Gini > 0.7? {gini_val > 0.7}")
print(f"Top10 > 0.5? {top10 > 0.5}")
print(f"Correlação > 0.5? {corr_log > 0.5 if not np.isnan(corr_log) else 'NaN'}")
print(f"Índice de Dominação > 0.65? {dom_idx > 0.65}")
print(f"Expectativa: Alta dominação ✓" if dom_level == "Alta" else f"Expectativa: Alta dominação, obtive {dom_level} ✗")

print("\nTeste concluído!")
