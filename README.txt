# Great Britain Power Play Strategy Analysis
## CSAS 2026 Data Challenge Submission

This repository contains the analysis code for the Mixed Doubles Curling Data Challenge, focusing on the Power Play strategies of Great Britain.

### Files
- **analyze_powerplay.py**: The main Python script that processes the provided CSV files and outputs statistical metrics regarding scoring efficiency and shot selection.
- **Competition.csv, Ends.csv, Games.csv, Stones.csv, Teams.csv**: Data files (provided by the challenge).

### How to Run
1. Ensure you have Python installed with `pandas`.
   ```bash
   pip install pandas
   ```
2. Place the script `analyze_powerplay.py` in the same directory as the data CSV files.
3. Run the script:
   ```bash
   python analyze_powerplay.py
   ```

### Output Interpretation
The script prints the following sections to the console:
1. **Efficiency Metrics**: Comparisons of Average Points, Conversion Rate (2+ pts), and Big End Rate (3+ pts) for GBR vs the Field.
2. **GBR Strategy Analysis**: Breakdown of the first shot thrown (Shot 2 of the end) by GBR during Power Plays.
3. **Field Strategy Effectiveness**: Statistical performance of different shot types (Draw vs Guard vs Raise) for the field, validating the efficiency of GBR's choices.

### Key Finding
GBR achieves higher consistency (50% conversion rate) by completely avoiding the "Guard" shot (avg value 1.18 pts) on their opening throw, instead favoring Draws (1.67 pts) and Raises (1.85 pts).
