#!/usr/bin/env python
"""
Test analysis services and data interpretation functionality.
"""

import pytest
import pandas as pd
import numpy as np
from services.analysis_service import (
    interpret_dataset, 
    interpret_domination,
    interpret_power_structure
)


class TestInterpretDomination:
    """Test domination level interpretation."""
    
    def test_interpret_domination_alta(self):
        """Test interpretation of high domination."""
        result = interpret_domination(0.75)
        assert result == "Alta", "High domination index should be interpreted as 'Alta'"
    
    def test_interpret_domination_media(self):
        """Test interpretation of medium domination."""
        result = interpret_domination(0.50)
        assert result == "Moderada", "Medium domination index should be interpreted as 'Moderada'"
    
    def test_interpret_domination_baixa(self):
        """Test interpretation of low domination."""
        result = interpret_domination(0.25)
        assert result == "Baixa", "Low domination index should be interpreted as 'Baixa'"


class TestInterpretDataset:
    """Test complete dataset interpretation."""
    
    def test_interpret_dataset_insufficient_sample(self):
        """Test interpretation with insufficient sample size."""
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
        
        result = interpret_dataset(df, df_heg, 0.5)
        
        # With small sample, levels should be "Indefinido"
        assert result.appropriation_level == "Indefinido", "Small sample should have indefinido level"
        assert result.density_level == "Indefinida", "Small sample should have indefinida level"
        assert result.inequality_level == "Indefinida", "Small sample should have indefinida level"
        print("✓ Correctly handles insufficient sample size")
    
    def test_interpret_dataset_sufficient_sample(self):
        """Test interpretation with sufficient sample size."""
        # Create larger sample
        n = 50
        df = pd.DataFrame({
            'appropriation_rate': np.random.uniform(0.1, 0.3, n),
            'symbolic_density': np.random.uniform(0.5, 1.0, n),
            'stars': np.random.exponential(100, n)
        })
        
        df_heg = df.copy()
        df_heg['name'] = [f'repo_{i}' for i in range(n)]
        df_heg['forks'] = df_heg['stars'] / 10
        df_heg['hegemony_index'] = df_heg['stars'] + df_heg['forks']
        
        result = interpret_dataset(df, df_heg, 0.6)
        
        # With sufficient sample, should have interpretable values
        assert result.gini_coefficient is not None, "Gini should be calculated"
        assert result.summary is not None, "Summary should be generated"
        print(f"✓ Sufficient sample interpretation: Inequality={result.inequality_level}")
    
    def test_interpret_dataset_attributes(self):
        """Test that all expected attributes are present in result."""
        df = pd.DataFrame({
            'appropriation_rate': [0.1, 0.2, 0.15, 0.25, 0.18],
            'symbolic_density': [0.5, 0.8, 0.6, 0.7, 0.55],
            'stars': [1, 2, 3, 4, 5]
        })
        
        df_heg = pd.DataFrame({
            'name': ['test'],
            'stars': [100],
            'forks': [10],
            'hegemony_index': [110]
        })
        
        result = interpret_dataset(df, df_heg, 0.7)
        
        # Check all expected attributes
        assert hasattr(result, 'appropriation_level'), "Should have appropriation_level"
        assert hasattr(result, 'density_level'), "Should have density_level"
        assert hasattr(result, 'inequality_level'), "Should have inequality_level"
        assert hasattr(result, 'gini_coefficient'), "Should have gini_coefficient"
        assert hasattr(result, 'top10_concentration'), "Should have top10_concentration"
        assert hasattr(result, 'hegemonic_repo'), "Should have hegemonic_repo"
        assert hasattr(result, 'hegemony_type'), "Should have hegemony_type"
        assert hasattr(result, 'domination_level'), "Should have domination_level"
        assert hasattr(result, 'power_structure_insights'), "Should have power_structure_insights"
        assert hasattr(result, 'summary'), "Should have summary"
        print("✓ All expected attributes present in result")


class TestPowerStructureInterpretation:
    """Test power structure interpretation."""
    
    def test_power_structure_with_hegemonic_data(self):
        """Test power structure analysis with hegemonic repository."""
        # Create highly asymmetric distribution
        stars_distribution = [10000, 5000, 2000, 500, 100, 50, 10, 5, 2, 1]
        
        df = pd.DataFrame({
            'name': [f'repo_{i}' for i in range(len(stars_distribution))],
            'appropriation_rate': np.random.uniform(0.1, 0.3, len(stars_distribution)),
            'symbolic_density': np.random.uniform(0.5, 1.0, len(stars_distribution)),
            'stars': stars_distribution,
            'forks': [s // 20 for s in stars_distribution]
        })
        
        df_heg = df[['name', 'stars', 'forks']].copy()
        df_heg['hegemony_index'] = df_heg['stars'] + df_heg['forks']
        
        result = interpret_dataset(df, df_heg, 0.772)
        
        # High asymmetry should show domination
        assert result.domination_level in ["Alta", "Média", "Indefinida"], \
            "Should have valid domination level"
        assert result.summary is not None, "Should generate summary"
        print(f"✓ Power structure identified: Domination={result.domination_level}")


class TestServiceErrorHandling:
    """Test error handling in services."""
    
    def test_empty_dataframe_handling(self):
        """Test that service handles empty DataFrames gracefully."""
        df_empty = pd.DataFrame()
        df_heg_empty = pd.DataFrame({'name': [], 'stars': [], 'forks': [], 'hegemony_index': []})
        
        # Should not raise exception
        try:
            result = interpret_dataset(df_empty, df_heg_empty, 0.5)
            print("✓ Empty DataFrame handled gracefully")
        except Exception as e:
            pytest.fail(f"Should handle empty DataFrame: {str(e)}")
    
    def test_nan_values_handling(self):
        """Test that service handles NaN values gracefully."""
        df = pd.DataFrame({
            'appropriation_rate': [0.1, np.nan, 0.15],
            'symbolic_density': [0.5, 0.8, np.nan],
            'stars': [1, 2, 3]
        })
        
        df_heg = pd.DataFrame({
            'name': ['test'],
            'stars': [100],
            'forks': [10],
            'hegemony_index': [110]
        })
        
        # Should not raise exception
        try:
            result = interpret_dataset(df, df_heg, 0.5)
            print("✓ NaN values handled gracefully")
        except Exception as e:
            pytest.fail(f"Should handle NaN values: {str(e)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
