# Food Manufacture: The Classic Blending Problem
**Origin:** H. Paul Williams, *Model Building in Mathematical Programming*, Problems 12.1 & 12.2.

## The Business Problem
A food manufacturer blends oils to produce a product. The challenge is multi-period arbitrage: buying raw materials when they are cheap, storing them, and blending them to meet hard quality constraints.

### Core Challenges
1.  **Inventory Management:** You can store oil, but it costs money (£5/ton/month).
2.  **Hardness Balancing:** Vegetable oils are hard; Oils are soft. The final blend must be between 3.0 and 6.0 hardness units.
3.  **Logical Constraints (MIP):** (Scenario 2 only)
    - If you use an oil, you must use at least 20 tons (to avoid micro-dosing).
    - You cannot use more than 3 distinct oils in a single month.
    - If you use vegetable oils (VEG1/VEG2), you *must* add OIL3 to balance the chemical properties.

## The Mathematical Formulation (Modernized)

### Sets
- $O$: Set of oils $\{VEG1, VEG2, ...\}$
- $T$: Set of months $\{1..6\}$

### Variables
- $Buy_{o,t}$: Tons of oil $o$ bought in month $t$.
- $Use_{o,t}$: Tons of oil $o$ refined/used in month $t$.
- $Stock_{o,t}$: Inventory at end of month $t$.
- $\delta_{o,t} \in \{0,1\}$: Binary indicator (1 if oil $o$ is used in month $t$).

### Key Constraints

**1. Inventory Balance (The Asset Equation)**
$$ Stock_{o,t} = Stock_{o,t-1} + Buy_{o,t} - Use_{o,t} $$

**2. Hardness Blending (Linearized)**
Original form: $\frac{\sum hardness_o \cdot Use_{o,t}}{\sum Use_{o,t}} \geq 3$
Linearized for solver stability:
$$ \sum_{o \in O} hardness_o \cdot Use_{o,t} \geq 3 \cdot \sum_{o \in O} Use_{o,t} $$

**3. Logical Linking (Big-M)**
$$ Use_{o,t} \leq M \cdot \delta_{o,t} $$
$$ Use_{o,t} \geq 20 \cdot \delta_{o,t} $$

**4. The "Conditional" Constraint**
If Veg is used, Oil 3 must be used:
$$ \delta_{VEG1, t} \leq \delta_{OIL3, t} $$
$$ \delta_{VEG2, t} \leq \delta_{OIL3, t} $$

## How to Run
This repository uses `pyomo` with the `highs` solver.

```bash
pip install -r requirements.txt
python main.py