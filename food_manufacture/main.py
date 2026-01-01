import pandas as pd
from data import load_oils_data, load_market_prices, get_parameters
from model import FoodManufactureModel

def print_summary(model_wrapper, title):
    print(f"\n--- {title} ---")
    profit = pyo.value(model_wrapper.model.Objective)
    print(f"Total Profit: £{profit:,.2f}")
    
    # Pivot for readability
    df = model_wrapper.result_data
    usage = df.pivot(index='Month', columns='Oil', values='Use')
    print("\nRefining Plan (Tons Used):")
    print(usage.round(1))

    buying = df.pivot(index='Month', columns='Oil', values='Buy')
    print("\nBuying Plan (Tons Bought):")
    print(buying.round(1))

if __name__ == "__main__":
    # 1. Load Data
    oils = load_oils_data()
    prices = load_market_prices()
    params = get_parameters()

    import pyomo.environ as pyo

    # 2. Run Scenario 1: The Linear Program (Relaxed)
    # Corresponds to Williams' Problem 12.1
    print("Solving Problem 12.1 (Continuous LP)...")
    lp_model = FoodManufactureModel(oils, prices, params)
    lp_model.build(use_integer_logic=False)
    lp_model.solve()
    print_summary(lp_model, "LP Results (Food Manufacture 1)")

    # 3. Run Scenario 2: The Mixed Integer Program
    # Corresponds to Williams' Problem 12.2 (Logical Constraints)
    print("\n" + "="*40 + "\n")
    print("Solving Problem 12.2 (MIP with Logical Constraints)...")
    mip_model = FoodManufactureModel(oils, prices, params)
    mip_model.build(use_integer_logic=True)
    mip_model.solve()
    print_summary(mip_model, "MIP Results (Food Manufacture 2)")