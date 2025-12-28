#!/usr/bin/env python3
"""
Calculate average contaminant concentrations from water sample data.
Handles raw laboratory data with non-detects (values below detection limit).
"""

import pandas as pd
import numpy as np

def load_water_data(filepath):
    """Load CSV file containing water sample results."""
    df = pd.read_csv(filepath)
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()
    return df

def calculate_average_ethylbenzene(df):
    """
    Calculate average ethylbenzene concentration (μg/L) for samples within 1 mile of drilling.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Must contain columns:
        - 'ethylbenzene_ugl': concentration in micrograms per liter
        - 'distance_miles': distance from nearest drilling site
    
    Returns:
    --------
    float : average concentration
    """
    # Filter samples within 1 mile
    near_samples = df[df['distance_miles'] <= 1.0].copy()
    
    # Handle non-detects: values marked as '<LOD' (limit of detection) are treated as 0
    # This is a simplified approach; actual practice may use LOD/2 or other methods.
    near_samples['ethylbenzene_ugl'] = near_samples['ethylbenzene_ugl'].replace('<LOD', 0)
    near_samples['ethylbenzene_ugl'] = pd.to_numeric(near_samples['ethylbenzene_ugl'], errors='coerce')
    
    # Drop any rows where concentration is NaN after conversion
    near_samples = near_samples.dropna(subset=['ethylbenzene_ugl'])
    
    # Calculate average
    avg = near_samples['ethylbenzene_ugl'].mean()
    return avg

def generate_summary_statistics(df, contaminant):
    """
    General function to compute summary stats for a given contaminant.
    Non-detects are treated as zero.
    """
    # Replace non-detects with zero
    df[contaminant] = df[contaminant].replace('<LOD', 0)
    df[contaminant] = pd.to_numeric(df[contaminant], errors='coerce')
    
    stats = {
        'mean': df[contaminant].mean(),
        'median': df[contaminant].median(),
        'std': df[contaminant].std(),
        'count': df[contaminant].count(),
        'max': df[contaminant].max(),
        'min': df[contaminant].min()
    }
    return stats

if __name__ == '__main__':
    # Example usage
    data = load_water_data('../data/processed/water_samples_2023.csv')
    avg_ethylbenzene = calculate_average_ethylbenzene(data)
    print(f'Average ethylbenzene concentration within 1 mile: {avg_ethylbenzene:.2f} μg/L')
    
    # Compare with EPA screening level (700 μg/L)
    epa_level = 700.0
    if avg_ethylbenzene > epa_level:
        print(f'Exceeds EPA screening level ({epa_level} μg/L)')
    else:
        print(f'Below EPA screening level ({epa_level} μg/L)')