import pandas as pd
from core.metrics import get_top_hegemonic_repo, compute_hegemony_index

# Teste com dados de exemplo
df = pd.DataFrame({
    'name': ['repo1', 'repo1', 'repo2', 'repo2', 'repo3'],
    'stars': [100, 110, 50, 60, 200],
    'forks': [10, 12, 8, 9, 15]
})

# Testar get_top_hegemonic_repo
name, value, rank = get_top_hegemonic_repo(df)
print(f'Top hegemonic repo: {name} with value {value:.2f} (rank: {rank})')

# Testar compute_hegemony_index
heg = compute_hegemony_index(df)
print('\nHegemony Index:')
print(heg)
print(f'\nNAs na coluna hegemony_index: {heg["hegemony_index"].isna().sum()}')
