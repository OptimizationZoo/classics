import pandas as pd

def load_oils_data():
    """
    Defines the static characteristics of the raw materials (Oils).
    Modern Twist: In a real app, this might come from a Feature Store.
    """
    data = [
        {'id': 'VEG1', 'type': 'Veg',    'hardness': 8.8},
        {'id': 'VEG2', 'type': 'Veg',    'hardness': 6.1},
        {'id': 'OIL1', 'type': 'NonVeg', 'hardness': 2.0},
        {'id': 'OIL2', 'type': 'NonVeg', 'hardness': 4.2},
        {'id': 'OIL3', 'type': 'NonVeg', 'hardness': 5.0},
    ]
    return pd.DataFrame(data).set_index('id')

def load_market_prices():
    """
    Forecasted purchase prices for raw oils over the 6-month horizon.
    Prices are in £/ton.
    """
    # H. Paul Williams Original Dataset (Jan-Jun)
    prices = {
        'VEG1': [110, 130, 110, 120, 100, 90],
        'VEG2': [120, 130, 140, 110, 120, 100],
        'OIL1': [130, 110, 130, 120, 150, 140],
        'OIL2': [110, 90, 100, 120, 110, 80],
        'OIL3': [115, 115, 95, 125, 105, 135]
    }
    df = pd.DataFrame(prices)
    df.index = [1, 2, 3, 4, 5, 6] # Months 1-6
    df.index.name = 'month'
    return df

def get_parameters():
    """
    Returns the scalar business constraints.
    """
    return {
        'storage_cost_per_ton': 5.0,
        'product_sales_price': 150.0,
        'max_veg_refine_per_month': 200.0,
        'max_nonveg_refine_per_month': 250.0,
        'storage_capacity_per_oil': 1000.0,
        'initial_stock': 500.0,
        'target_final_stock': 500.0,
        'min_hardness': 3.0,
        'max_hardness': 6.0,
        # Part 2 (Integer) Parameters
        'min_usage_if_used': 20.0,
        'max_ingredients_per_month': 3
    }