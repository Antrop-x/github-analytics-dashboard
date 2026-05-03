#!/usr/bin/env python
"""
Test core metrics calculations and implementations.
"""

import pytest
import pandas as pd
import numpy as np
from core.metrics import (
    gini, 
    top_concentration, 
    domination_index, 
    get_top_hegemonic_repo,
    compute_hegemony_index
)


class TestGiniMetric:
    """Test Gini coefficient calculations."""
    
    def test_gini_basic(self):
        """Test basic Gini calculation."""
        df = pd.DataFrame({
            'stars': [1, 2, 3, 4, 5, 10, 20, 50, 100, 200]
        })
        gini_val = gini(df['stars'])
        assert 0 < gini_val < 1, "Gini should be between 0 and 1"
        assert abs(gini_val - 0.7) < 0.01, "Gini value should be approximately 0.7"
    
    def test_gini_high_inequality(self):
        """Test Gini with high inequality (heavy-tailed distribution)."""
        stars_distribution = [10000, 5000, 2000, 500, 100, 50, 10, 5, 2, 1]
        gini_val = gini(pd.Series(stars_distribution))
        assert gini_val > 0.7, "Gini for high inequality should be > 0.7"
        print(f"✓ Gini for asymmetric distribution: {gini_val:.3f}")
    
    def test_gini_equal_distribution(self):
        """Test Gini with equal distribution."""
        equal_dist = [100] * 10
        gini_val = gini(pd.Series(equal_dist))
        assert gini_val < 0.01, "Gini for equal distribution should be ~0"


class TestTopConcentration:
    """Test top concentration calculations."""
    
    def test_top_concentration_basic(self):
        """Test basic top concentration."""
        df = pd.DataFrame({
            'stars': [1, 2, 3, 4, 5, 10, 20, 50, 100, 200]
        })
        top10 = top_concentration(df, col="stars", top=0.1)
        assert 0 < top10 < 1, "Top concentration should be between 0 and 1"
        assert top10 > 0.5, "Top 10% should have majority of stars"
        print(f"✓ Top 10% concentration: {top10:.2%}")
    
    def test_top_concentration_high_inequality(self):
        """Test top concentration with high inequality."""
        stars_distribution = [10000, 5000, 2000, 500, 100, 50, 10, 5, 2, 1]
        df = pd.DataFrame({'stars': stars_distribution})
        top10 = top_concentration(df, col="stars", top=0.1)
        assert top10 > 0.5, "Top 10% should have majority in high inequality"
        print(f"✓ Top 10% concentration (high inequality): {top10:.2%}")


class TestDominationIndex:
    """Test domination index calculations."""
    
    def test_domination_index_calculation(self):
        """Test domination index with example values."""
        gini_val = 0.772
        top10 = 0.566
        corr_log = 1.0
        
        dom_idx = domination_index(gini_val, top10, corr_log)
        assert 0 <= dom_idx <= 1, "Domination index should be between 0 and 1"
        assert dom_idx > 0.65, "High inequality should result in high domination index"
        print(f"✓ Domination Index: {dom_idx:.3f}")
    
    def test_domination_index_low(self):
        """Test domination index with low values."""
        gini_val = 0.3
        top10 = 0.2
        corr_log = 0.2
        
        dom_idx = domination_index(gini_val, top10, corr_log)
        assert dom_idx < 0.5, "Low inequality should result in low domination index"


class TestHegemonyMetrics:
    """Test hegemony-related metrics."""
    
    def test_get_top_hegemonic_repo(self):
        """Test identification of top hegemonic repository."""
        df = pd.DataFrame({
            'name': ['repo1', 'repo1', 'repo2', 'repo2', 'repo3'],
            'stars': [100, 110, 50, 60, 200],
            'forks': [10, 12, 8, 9, 15]
        })
        
        name, value, rank = get_top_hegemonic_repo(df)
        assert name == 'repo3', "Top hegemonic repo should be repo3"
        assert value > 0, "Hegemony value should be positive"
        print(f"✓ Top hegemonic repo: {name} with value {value:.2f} (rank: {rank})")
    
    def test_compute_hegemony_index(self):
        """Test hegemony index computation."""
        df = pd.DataFrame({
            'name': ['repo1', 'repo2', 'repo3'],
            'stars': [100, 50, 200],
            'forks': [10, 8, 15]
        })
        
        heg = compute_hegemony_index(df)
        assert 'hegemony_index' in heg.columns, "hegemony_index column should exist"
        assert heg['hegemony_index'].isna().sum() == 0, "No NaN values in hegemony_index"
        assert heg.loc[heg['name'] == 'repo3', 'hegemony_index'].values[0] > \
               heg.loc[heg['name'] == 'repo1', 'hegemony_index'].values[0], \
               "repo3 should have higher hegemony than repo1"


class TestMetricCoherence:
    """Test coherence between different metrics."""
    
    def test_metrics_coherence_high_inequality(self):
        """Test that metrics are coherent for high inequality scenarios."""
        stars_distribution = [10000, 5000, 2000, 500, 100, 50, 10, 5, 2, 1]
        df = pd.DataFrame({
            'name': [f'repo_{i}' for i in range(len(stars_distribution))],
            'stars': stars_distribution,
            'forks': [s // 20 for s in stars_distribution],
            'hegemony_index': [s + s // 20 for s in stars_distribution]
        })
        
        gini_val = gini(df['stars'])
        top10 = top_concentration(df, col="stars", top=0.1)
        
        # All metrics should indicate high concentration
        assert gini_val > 0.7, "Gini should be high"
        assert top10 > 0.5, "Top 10% should be high"
        
        log_hegemony = np.log1p(df["hegemony_index"].values)
        log_stars = np.log1p(df["stars"].values)
        corr_log = float(np.corrcoef(log_hegemony, log_stars)[0, 1])
        
        dom_idx = domination_index(gini_val, top10, corr_log)
        assert dom_idx > 0.65, "All metrics point to high domination"
        print(f"✓ Metrics are coherent: Gini={gini_val:.3f}, Top10={top10:.2%}, DomIdx={dom_idx:.3f}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
