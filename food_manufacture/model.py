import pyomo.environ as pyo
import pandas as pd

class FoodManufactureModel:
    def __init__(self, oils_df, prices_df, params):
        self.oils = oils_df
        self.prices = prices_df
        self.params = params
        self.model = None
        self.result_data = {}

    def build(self, use_integer_logic=False):
        """
        Constructs the optimization model.
        :param use_integer_logic: If True, adds Part 2 constraints (binary variables).
        """
        m = pyo.ConcreteModel()

        # --- SETS ---
        m.T = pyo.Set(initialize=self.prices.index) # Time periods (Months)
        m.O = pyo.Set(initialize=self.oils.index)   # Oils (VEG1, OIL1...)

        # --- VARIABLES ---
        # Continuous Variables
        m.Buy   = pyo.Var(m.O, m.T, domain=pyo.NonNegativeReals)
        m.Use   = pyo.Var(m.O, m.T, domain=pyo.NonNegativeReals)
        m.Stock = pyo.Var(m.O, m.T, domain=pyo.NonNegativeReals, 
                          bounds=(0, self.params['storage_capacity_per_oil']))
        m.Produce = pyo.Var(m.T, domain=pyo.NonNegativeReals)

        # Binary Variables (Only initialized if Integer Logic is requested)
        if use_integer_logic:
            m.IsUsed = pyo.Var(m.O, m.T, domain=pyo.Binary)

        # --- CONSTRAINTS ---

        # 1. Inventory Balance: Stock[t] = Stock[t-1] + Buy[t] - Use[t]
        def balance_rule(model, o, t):
            if t == model.T.first():
                prev_stock = self.params['initial_stock']
            else:
                prev_stock = model.Stock[o, t-1]
            return model.Stock[o, t] == prev_stock + model.Buy[o, t] - model.Use[o, t]
        m.Balance = pyo.Constraint(m.O, m.T, rule=balance_rule)

        # 2. Target Final Stock
        def final_stock_rule(model, o):
            return model.Stock[o, model.T.last()] == self.params['target_final_stock']
        m.FinalStock = pyo.Constraint(m.O, rule=final_stock_rule)

        # 3. Refining Capacity (Veg vs Non-Veg limits)
        # Note: We group dynamically using the DataFrame 'type' column
        def capacity_rule(model, t, oil_type, limit):
            relevant_oils = self.oils[self.oils['type'] == oil_type].index
            return sum(model.Use[o, t] for o in relevant_oils) <= limit
        
        m.VegCapacity = pyo.Constraint(m.T, rule=lambda mod, t: 
            capacity_rule(mod, t, 'Veg', self.params['max_veg_refine_per_month']))
        m.NonVegCapacity = pyo.Constraint(m.T, rule=lambda mod, t: 
            capacity_rule(mod, t, 'NonVeg', self.params['max_nonveg_refine_per_month']))

        # 4. Production Continuity: Produce[t] = sum(Use[o,t])
        def production_def(model, t):
            return model.Produce[t] == sum(model.Use[o, t] for o in m.O)
        m.ProductionDef = pyo.Constraint(m.T, rule=production_def)

        # 5. Hardness Constraints (Linearized)
        # 3 * Produce <= sum(Hardness * Use) <= 6 * Produce
        def hardness_min_rule(model, t):
            total_hardness = sum(self.oils.loc[o, 'hardness'] * model.Use[o, t] for o in m.O)
            return total_hardness >= self.params['min_hardness'] * model.Produce[t]
        m.HardnessMin = pyo.Constraint(m.T, rule=hardness_min_rule)

        def hardness_max_rule(model, t):
            total_hardness = sum(self.oils.loc[o, 'hardness'] * model.Use[o, t] for o in m.O)
            return total_hardness <= self.params['max_hardness'] * model.Produce[t]
        m.HardnessMax = pyo.Constraint(m.T, rule=hardness_max_rule)

        # --- PART 2: LOGICAL CONSTRAINTS (MIP) ---
        if use_integer_logic:
            # 6. Linking Constraint (Big-M): Use <= Capacity * IsUsed
            # Capacity is effectively the refining limit (250)
            big_m = 250.0 
            def link_rule(model, o, t):
                return model.Use[o, t] <= big_m * model.IsUsed[o, t]
            m.LinkVars = pyo.Constraint(m.O, m.T, rule=link_rule)

            # 7. Minimum Usage: If used, must use at least 20 tons
            def min_usage_rule(model, o, t):
                return model.Use[o, t] >= self.params['min_usage_if_used'] * model.IsUsed[o, t]
            m.MinThreshold = pyo.Constraint(m.O, m.T, rule=min_usage_rule)

            # 8. Max Ingredients: Max 3 oils per month
            def max_ingredients_rule(model, t):
                return sum(model.IsUsed[o, t] for o in m.O) <= self.params['max_ingredients_per_month']
            m.MaxIngredients = pyo.Constraint(m.T, rule=max_ingredients_rule)

            # 9. Logical Dependency: If VEG1 or VEG2 is used, OIL3 must be used
            # Logic: IsUsed[VEG1] <= IsUsed[OIL3]
            def logic_veg1_rule(model, t):
                return model.IsUsed['VEG1', t] <= model.IsUsed['OIL3', t]
            m.LogicVeg1 = pyo.Constraint(m.T, rule=logic_veg1_rule)

            def logic_veg2_rule(model, t):
                return model.IsUsed['VEG2', t] <= model.IsUsed['OIL3', t]
            m.LogicVeg2 = pyo.Constraint(m.T, rule=logic_veg2_rule)


        # --- OBJECTIVE ---
        # Maximize Profit = Sales Revenue - Purchase Costs - Storage Costs
        def objective_rule(model):
            revenue = sum(model.Produce[t] * self.params['product_sales_price'] for t in m.T)
            
            purchase_cost = sum(model.Buy[o, t] * self.prices.loc[t, o] 
                                for o in m.O for t in m.T)
            
            storage_cost = sum(model.Stock[o, t] * self.params['storage_cost_per_ton'] 
                               for o in m.O for t in m.T)
            
            return revenue - purchase_cost - storage_cost
        
        m.Objective = pyo.Objective(rule=objective_rule, sense=pyo.maximize)
        
        self.model = m

    def solve(self):
        # We use Highs, an excellent open-source solver for MIPs
        solver = pyo.SolverFactory('appsi_highs') 
        result = solver.solve(self.model)
        
        # Extract results into a clean Pandas DataFrame
        results = []
        for t in self.model.T:
            for o in self.model.O:
                results.append({
                    'Month': t,
                    'Oil': o,
                    'Buy': pyo.value(self.model.Buy[o,t]),
                    'Use': pyo.value(self.model.Use[o,t]),
                    'Stock': pyo.value(self.model.Stock[o,t]),
                })
        self.result_data = pd.DataFrame(results)
        return result