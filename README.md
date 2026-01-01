# 🏛️ Optimization Zoo: The Classics

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Solver: HiGHS](https://img.shields.io/badge/solver-HiGHS-green.svg)](https://highs.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Canonical Operations Research problems, modernized for the Data Scientist of the 2020s.**

## 📜 The Mission

For decades, the "bible" of mathematical modeling was H. Paul Williams' *Model Building in Mathematical Programming*. It taught a generation how to think structurally about optimization. However, the implementation details—MPS files, punch-card logic, and matrix generators—are now artifacts of history.

**This repository bridges the gap.** We take the timeless mathematical logic of classic OR problems and implement them using the modern Data Science stack: **Python**, **Pandas**, and **Pyomo**.

### The Shift: Legacy vs. Modern

| Feature | The Legacy Way (1980s) | The Optimization Zoo Way (2020s) |
| :--- | :--- | :--- |
| **Data Source** | Static `.dat` or `.txt` files | Pandas DataFrames & SQL Connectors |
| **Variables** | Cryptic indices (`x[1,1]`) | Semantic keys (`Use['Veg1', 'Jan']`) |
| **Logic** | Manual Matrix Generation | Object-Oriented Constraint definitions |
| **Solvers** | Expensive, proprietary binaries | High-performance Open Source (HiGHS) |
| **Infeasibility** | "Infeasible" (Good luck!) | Big-M relaxation & IIS Debugging |

---

## 🦁 The Zoo (Problem Index)

We are systematically porting the 24 classic problems from Williams' text, plus other canonical problems (TSP, Knapsack), into production-grade Python.

| ID | Problem Name | Core Concepts | Formulation | Code |
| :--- | :--- | :--- | :--- | :--- |
| **12.1** | **Food Manufacture** | Multi-period blending, Inventory management | LP | [Link](./food_manufacture) |
| **12.2** | **Food Manufacture (II)** | Logical constraints, Indicator variables, Big-M | MIP | [Link](./food_manufacture) |
| **12.3** | **Factory Planning** | Multi-machine scheduling, Maintenance planning | LP | *Coming Soon* |
| **12.7** | **Mining** | Topology, Precedence constraints, Graph theory | MIP | *Coming Soon* |
| **12.15**| **Power Generation** | Unit commitment, Startup costs, Convex hulls | MIP | *Coming Soon* |
| **12.24**| **Yield Management** | Stochastic programming, Scenarios, Pricing | Stochastic | *Coming Soon* |
| **N/A** | **Traveling Salesman** | Subtour elimination, Callbacks, lazy constraints | MIP | *Coming Soon* |

---

## 🚀 Getting Started

We use `Pyomo` as our modeling language and `HiGHS` as our solver. HiGHS is a modern, open-source solver that rivals commercial performance for many standard problems.

### 1. Installation
Clone the repo and install dependencies. We recommend using a virtual environment.

```bash
git clone https://github.com/OptimizationZoo/classics.git
cd classics
pip install -r requirements.txt
```

### 2. Running a Model
Each problem is self-contained in its own directory. To run the **Food Manufacture** blend planning model:

```bash
cd food_manufacture
python main.py
```

*Sample Output:*
```text
--- MIP Results (Food Manufacture 2) ---
Total Profit: £100,279.00

Refining Plan (Tons Used):
Oil    OIL1  OIL2  OIL3   VEG1   VEG2
Month                                
1       0.0   0.0   0.0  200.0    0.0
2       0.0   0.0  20.0    0.0  190.0
...
```

---

## 🛠️ Anatomy of a Modern Model

Every model in this repository follows a strict **Separation of Concerns** architecture. We do not hardcode numbers into optimization models.

1.  **`data.py`**: The ETL layer. Responsible for loading data (from CSVs, APIs, or Mock Generators) and returning clean Pandas DataFrames.
2.  **`model.py`**: The Logic layer. A Python class that accepts DataFrames, instantiates a Pyomo model, and defines constraints dynamically.
3.  **`main.py`**: The Orchestrator. It loads data, builds the model, solves it, and extracts results.

### Example: The "Pythonic" Constraint
**Old Way (Algebraic modeling languages):**
```text
SUBJECT TO
  R_1(t): SUM(i) Use(i,t) <= Cap(t)
```

**New Way (Pandas + Pyomo):**
```python
def capacity_rule(model, t):
    # Dynamic summation based on DataFrames
    return sum(model.Use[i, t] for i in oils_df.index) <= capacity_df.loc[t, 'Max']

model.CapacityConstr = pyo.Constraint(model.TimePeriods, rule=capacity_rule)
```

---

## 🤖 For AI Researchers

This repository serves as a **Ground Truth Benchmark** for LLMs (Large Language Models) in the domain of Operations Research. 

If you are building agents to solve math word problems, do not train them on the raw MPS files found online. Train them to generate the **Pyomo** code found here. This code represents *semantic understanding* of the problem, whereas MPS files represent only the *matrix structure*.

---

## 🤝 Contributing

We welcome contributions! If you are a student, professor, or practitioner:

1.  Pick an un-implemented problem from the [Williams Index](https://github.com/OptimizationZoo/classics/issues).
2.  Follow the folder structure: `data.py`, `model.py`, `main.py`.
3.  Ensure you use **Type Hinting** and **Pandas**.
4.  Submit a Pull Request.

---

## 📚 References

*   Williams, H. P. (2013). *Model Building in Mathematical Programming* (5th ed.). Wiley.
*   The `HiGHS` Solver: [https://highs.dev/](https://highs.dev/)
*   Pyomo Documentation: [http://www.pyomo.org/](http://www.pyomo.org/)