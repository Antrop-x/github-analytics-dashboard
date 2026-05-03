#!/usr/bin/env python
import sys
try:
    import pandas as pd
    print("✓ pandas ok")
    
    from core.metrics import gini, domination_index
    print("✓ métricas importadas")
    
    import numpy as np
    stars = np.array([10000, 5000, 2000, 500, 100])
    g = gini(pd.Series(stars))
    print(f"✓ Gini calculado: {g}")
    
    d = domination_index(g, 0.6, 0.5)
    print(f"✓ Domination Index calculado: {d}")
    
except Exception as e:
    print(f"✗ Erro: {e}")
    import traceback
    traceback.print_exc()
