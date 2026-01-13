import pandas as pd
import numpy as np
import os
try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    from sklearn.ensemble import GradientBoostingRegressor

# Configuration
DATA_DIR = "./"
if not os.path.exists(os.path.join(DATA_DIR, "Ends.csv")):
    DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"

def load_data():
    files = {
        "competitors": os.path.join(DATA_DIR, "Competitors.csv"),
        "ends": os.path.join(DATA_DIR, "Ends.csv"),
        "teams": os.path.join(DATA_DIR, "Teams.csv")
    }
    dfs = {}
    for name, path in files.items():
        if os.path.exists(path):
            dfs[name] = pd.read_csv(path)
    return dfs

def analyze_prediction(dfs):
    ends = dfs['ends']
    
    # 1. Feature Engineering: Team Strength (Avg Points per End)
    # Simple proxy for "Quality": Average points scored per end across entire dataset
    team_strength = ends.groupby('TeamID')['Result'].mean().to_dict()
    global_avg = ends['Result'].mean()
    
    # 2. Build Dataset
    ends['GameKey'] = ends['CompetitionID'].astype(str) + "_" + ends['SessionID'].astype(str) + "_" + ends['GameID'].astype(str)
    
    # Filter Score Rows (assuming row represents score for TeamID)
    # We need running score diff.
    # Group by game
    game_groups = ends.groupby('GameKey')
    
    # Filter for PowerPlay Ends
    pp_rows = ends[ends['PowerPlay'].notna() & (ends['PowerPlay'] != 0)].copy()
    
    data = []
    
    for idx, row in pp_rows.iterrows():
        game_key = row['GameKey']
        game_ends = game_groups.get_group(game_key)
        
        pp_team = row['TeamID']
        end_id = row['EndID']
        
        # Determine Opponent (The other team in this end?)
        # Game ends has multiple rows. Opponent is the other TeamID in this game.
        teams_in_game = game_ends['TeamID'].unique()
        opp_id = next((t for t in teams_in_game if t != pp_team), None)
        
        if opp_id is None: continue
        
        # Feature: Diff
        prev_ends = game_ends[game_ends['EndID'] < end_id]
        if prev_ends.empty:
            my_score = 0
            opp_score = 0
        else:
            scores = prev_ends.groupby('TeamID')['Result'].sum()
            my_score = scores.get(pp_team, 0)
            opp_score = scores.get(opp_id, 0)
        
        diff = my_score - opp_score
        
        # Feature: Strengths
        my_str = team_strength.get(pp_team, global_avg)
        opp_str = team_strength.get(opp_id, global_avg)
        
        # Target: Points Scored in THIS end
        points = row['Result']
        
        data.append({
            'End': end_id,
            'Diff': diff,
            'TeamStr': my_str,
            'OppStr': opp_str,
            'Points': points
        })
        
    df = pd.DataFrame(data)
    print(f"Dataset Size: {len(df)} ends")
    
    # 3. Train Model
    features = ['End', 'Diff', 'TeamStr', 'OppStr']
    target = 'Points'
    
    X = df[features]
    y = df[target]
    
    print("\nTraining Model...")
    if HAS_XGB:
        print("Using XGBoost Regressor")
        model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100)
    else:
        print("XGBoost not found, using Sklearn GradientBoostingRegressor")
        model = GradientBoostingRegressor(n_estimators=100)
        
    model.fit(X, y)
    
    # 4. Optimization: Predict Optimal Scenarios
    print("\n--- Predicted Expected Points (xPoints) Grid ---")
    
    # Scenario: Generic Good Team vs Generic Good Team
    avg_str = df['TeamStr'].mean()
    
    # Create Grid
    # End: 1 to 8
    # Diff: -4 to +4
    grid_data = []
    for end in range(1, 9):
        for diff in range(-4, 5):
            grid_data.append({
                'End': end,
                'Diff': diff,
                'TeamStr': avg_str, # Assume average strength for generic advice
                'OppStr': avg_str
            })
            
    grid_df = pd.DataFrame(grid_data)
    grid_df['xPoints'] = model.predict(grid_df[features])
    
    # Display Heatmap-like table
    pivot = grid_df.pivot(index='Diff', columns='End', values='xPoints')
    # Sort index descending (Leading at top)
    pivot = pivot.sort_index(ascending=False)
    
    print(pivot.round(2))
    
    # Find Max
    best = grid_df.loc[grid_df['xPoints'].idxmax()]
    print("\n--- Optimal Scenario ---")
    print(f"End: {int(best['End'])}")
    print(f"Score Diff: {int(best['Diff'])}")
    print(f"Expected Points: {best['xPoints']:.2f}")

    # Interpretation
    print("\n--- Interpretation ---")
    print("Values > 1.8 indicate highly favorable conditions.")
    print("Values < 1.4 indicate poor conditions.")

if __name__ == "__main__":
    dfs = load_data()
    analyze_prediction(dfs)
