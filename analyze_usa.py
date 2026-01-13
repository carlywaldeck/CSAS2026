
import pandas as pd
import numpy as np
import os

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

def analyze_usa(dfs):
    teams = dfs['teams']
    ends = dfs['ends']
    
    # 1. Identify USA Teams
    usa_teams = teams[teams['NOC'] == 'USA']
    usa_ids = usa_teams['TeamID'].unique()
    print(f"USA Team IDs: {usa_ids}")
    
    # Identify Comparison (Mowat)
    # We know Mowat is GBR/SCO (TeamID 27, 14, 109 from previous looks)
    # Simplest is to filter by 'MOUAT' in competitors if needed, or just hardcode if known.
    # We'll rely on NOC 'GBR' and 'SCO' for broad elite comparison, or just compare to "Field".
    
    # 2. Filter Power Play Ends
    pp_ends = ends[ends['PowerPlay'].notna() & (ends['PowerPlay'] != 0)].copy()
    
    # 3. USA Performance
    usa_pp = pp_ends[pp_ends['TeamID'].isin(usa_ids)]
    field_pp = pp_ends[~pp_ends['TeamID'].isin(usa_ids)]
    
    print("\n--- Efficiency Comparison ---")
    metrics = []
    
    for label, df in [("USA", usa_pp), ("Field", field_pp)]:
        metrics.append({
            "Group": label,
            "Ends": len(df),
            "Avg Pts": df['Result'].mean(),
            "Success % (2+)": (df['Result'] >= 2).mean() * 100,
            "Big End % (3+)": (df['Result'] >= 3).mean() * 100,
            "Fail % (<=1)": (df['Result'] <= 1).mean() * 100
        })
        
    print(pd.DataFrame(metrics).round(2).to_string(index=False))
    
    # 4. Usage Analysis (When do they use it?)
    # We need Context (Score Diff and End)
    # Re-calculate context logic (simplified from previous script)
    
    usa_pp = usa_pp.copy()
    
    # Get Game Context (requires grouping by game to get running score)
    ends['GameKey'] = ends['CompetitionID'].astype(str) + "_" + ends['SessionID'].astype(str) + "_" + ends['GameID'].astype(str)
    
    # Update usa_pp to include the new column
    usa_pp = ends[ends['PowerPlay'].notna() & (ends['PowerPlay'] != 0) & ends['TeamID'].isin(usa_ids)].copy()
    
    game_groups = ends.groupby('GameKey')
    
    contexts = []
    end_usage = []
    
    for idx, row in usa_pp.iterrows():
        game_key = row['GameKey']
        game_ends = game_groups.get_group(game_key)
        end_id = row['EndID']
        
        prev_ends = game_ends[game_ends['EndID'] < end_id]
        if prev_ends.empty:
            diff = 0
        else:
            my_score = prev_ends[prev_ends['TeamID'] == row['TeamID']]['Result'].sum()
            opp_score = prev_ends[prev_ends['TeamID'] != row['TeamID']]['Result'].sum()
            diff = my_score - opp_score
            
        contexts.append(diff)
        end_usage.append(end_id)
        
    usa_pp['Diff'] = contexts
    usa_pp['EndID'] = end_usage
    
    print("\n--- USA Usage Patterns ---")
    print("End Number Distribution:")
    print(usa_pp['EndID'].value_counts(normalize=True).sort_index().round(2))
    
    print("\nScore Context Distribution (Diff):")
    print(usa_pp['Diff'].value_counts().sort_index())
    
    print("\n--- USA Performance by Context ---")
    # Where do they struggle?
    # Bin Diff using cut
    usa_pp['Context'] = pd.cut(usa_pp['Diff'], bins=[-10, -3, -1, 0, 10], labels=['Trailing Big', 'Trailing Small', 'Tied', 'Leading'])
    
    print(usa_pp.groupby('Context')['Result'].agg(['mean', 'count']).round(2))

if __name__ == "__main__":
    dfs = load_data()
    analyze_usa(dfs)
