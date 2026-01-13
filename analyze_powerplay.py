"""
Great Britain Power Play Strategy Analysis
CSAS 2026 Data Challenge

This script analyzes Mixed Doubles Curling data to investigate the Power Play strategy
of Great Britain (GBR). It calculates scoring efficiency, conversion rates, and 
shot selection trends compared to the field.

Usage:
    python analyze_powerplay.py

Requirements:
    pandas

Input Files (expected in same directory or DATA_DIR):
    Competition.csv, Ends.csv, Games.csv, Stones.csv, Teams.csv
"""

import pandas as pd
import os

# Configuration
DATA_DIR = "./" # Assumes data is in the current directory for submission
if not os.path.exists(os.path.join(DATA_DIR, "Ends.csv")):
    # Fallback to absolute path for development
    DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"

def load_data():
    """Load necessary CSV files into a dictionary of DataFrames."""
    files = {
        "competitions": os.path.join(DATA_DIR, "Competition.csv"),
        "competitors": os.path.join(DATA_DIR, "Competitors.csv"),
        "ends": os.path.join(DATA_DIR, "Ends.csv"),
        "games": os.path.join(DATA_DIR, "Games.csv"),
        "teams": os.path.join(DATA_DIR, "Teams.csv"),
        "stones": os.path.join(DATA_DIR, "Stones.csv")
    }
    
    dfs = {}
    print("Loading data files...")
    for name, path in files.items():
        if os.path.exists(path):
            dfs[name] = pd.read_csv(path)
        else:
            print(f"Warning: {path} not found.")
    return dfs

def add_keys(df, key_type='game'):
    """Create composite keys for merging across files."""
    if key_type == 'game':
        return (
            df['CompetitionID'].astype(str) + "_" + 
            df['SessionID'].astype(str) + "_" + 
            df['GameID'].astype(str)
        )
    elif key_type == 'end':
        return (
            df['CompetitionID'].astype(str) + "_" + 
            df['SessionID'].astype(str) + "_" + 
            df['GameID'].astype(str) + "_" + 
            df['EndID'].astype(str)
        )
    return None

def analyze_powerplay(dfs):
    teams_df = dfs['teams']
    ends_df = dfs['ends']
    games_df = dfs['games']
    stones_df = dfs['stones']

    # 1. Identify GBR TeamIDs
    gbr_teams = teams_df[teams_df['NOC'] == 'GBR']
    gbr_team_ids = gbr_teams['TeamID'].unique()
    print(f"GBR Team IDs found: {gbr_team_ids}")
    
    # 2. Filter for Power Play Ends
    pp_ends = ends_df[ends_df['PowerPlay'].notna()].copy()
    pp_ends['GameKey'] = add_keys(pp_ends, 'game')
    pp_ends['EndKey'] = add_keys(pp_ends, 'end')
    
    print(f"Total Power Play Ends in Dataset: {len(pp_ends)}")

    # 3. Efficiency Metrics
    gbr_pp_ends = pp_ends[pp_ends['TeamID'].isin(gbr_team_ids)].copy()
    field_pp_ends = pp_ends[~pp_ends['TeamID'].isin(gbr_team_ids)].copy()
    
    metrics = {
        "GBR": {
            "Ends": len(gbr_pp_ends),
            "Avg Pts": gbr_pp_ends['Result'].mean(),
            "Conversion (2+)": (gbr_pp_ends['Result'] >= 2).mean(),
            "Big End (3+)": (gbr_pp_ends['Result'] >= 3).mean()
        },
        "Field": {
            "Ends": len(field_pp_ends),
            "Avg Pts": field_pp_ends['Result'].mean(),
            "Conversion (2+)": (field_pp_ends['Result'] >= 2).mean(),
            "Big End (3+)": (field_pp_ends['Result'] >= 3).mean()
        }
    }
    
    print("\n--- Efficiency Metrics ---")
    print(pd.DataFrame(metrics).T)
    
    # 4. Shot Selection Analysis
    stones_df['EndKey'] = add_keys(stones_df, 'end')
    
    # Analyze GBR Power Play Stones
    gbr_pp_keys = gbr_pp_ends['EndKey'].unique()
    gbr_pp_stones = stones_df[stones_df['EndKey'].isin(gbr_pp_keys)].copy()
    
    # Calculate Shot Rank (order of shots within the end)
    gbr_pp_stones['ShotRank'] = gbr_pp_stones.groupby('EndKey')['ShotID'].rank(method='first').astype(int)
    
    # Task ID Mapping
    task_map = {
        0: "Draw", 1: "Front", 2: "Guard", 3: "Raise", 4: "Wick", 5: "Freeze",
        6: "Take-out", 7: "Hit and Roll", 8: "Clearing", 9: "Double Take-out",
        10: "Promotion Take-out", 11: "Through"
    }

    print("\n--- GBR Strategy Analysis ---")
    # Shot 2 is the FIRST stone thrown by the team with the Power Play (Hammer)
    # Shot 1 is thrown by the opponent.
    shot2_gbr = gbr_pp_stones[gbr_pp_stones['ShotRank'] == 2]
    print("GBR First Shot Selection (Shot 2):")
    print(shot2_gbr['Task'].map(task_map).fillna(shot2_gbr['Task']).value_counts())
    
    # Analyze Field Performance by Shot Choice
    field_pp_keys = field_pp_ends['EndKey'].unique()
    field_pp_stones = stones_df[stones_df['EndKey'].isin(field_pp_keys)].copy()
    field_pp_stones['ShotRank'] = field_pp_stones.groupby('EndKey')['ShotID'].rank(method='first').astype(int)
    
    shot2_field = field_pp_stones[field_pp_stones['ShotRank'] == 2]
    
    # Link to outcome
    shot2_field_res = shot2_field.merge(field_pp_ends[['EndKey', 'Result']], on='EndKey')
    shot2_field_res['TaskName'] = shot2_field_res['Task'].map(task_map).fillna(shot2_field_res['Task'])
    
    print("\n--- Field Strategy Effectiveness (Shot 2) ---")
    stats = shot2_field_res.groupby('TaskName')['Result'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    print(stats)

    # 5. Defensive Analysis (Shot 1 Effectiveness)
    # Shot 1 is thrown by the Defending team.
    # We want to know which Shot 1 Task results in the LOWEST Score (Result) for the PP team.
    print("\n--- Defensive Strategy (Shot 1 vs Outcome) ---")
    shot1_field = field_pp_stones[field_pp_stones['ShotRank'] == 1] # Defending stones
    shot1_field_res = shot1_field.merge(field_pp_ends[['EndKey', 'Result']], on='EndKey')
    shot1_field_res['TaskName'] = shot1_field_res['Task'].map(task_map).fillna(shot1_field_res['Task'])
    
    def_stats = shot1_field_res.groupby('TaskName')['Result'].agg(['mean', 'count']).sort_values('mean', ascending=True) # Ascending: Lower score is better defense
    print(def_stats)
    
    # 6. Score Differential Analysis (For GBR)
    # Need to calculate running score before the PP end.
    # Filter ends for GBR games
    gbr_game_keys = gbr_pp_ends['GameKey'].unique()
    all_gbr_game_ends = ends_df[add_keys(ends_df, 'game').isin(gbr_game_keys)].copy()
    all_gbr_game_ends['GameKey'] = add_keys(all_gbr_game_ends, 'game')
    
    print("\n--- GBR Score Context at Power Play ---")
    for game_key in gbr_game_keys:
        game_ends = all_gbr_game_ends[all_gbr_game_ends['GameKey'] == game_key].sort_values('EndID')
        # Find the PP end
        pp_end_row = game_ends[game_ends['PowerPlay'].notna() & game_ends['TeamID'].isin(gbr_team_ids)]
        
        if not pp_end_row.empty:
            pp_end_id = pp_end_row['EndID'].iloc[0]
            # Sum scores of previous ends
            # We need to know who scored. Result is points for 'TeamID'. 
            # If TeamID is GBR, add to GBR score. Else add to Opp score.
            
            prev_ends = game_ends[game_ends['EndID'] < pp_end_id]
            gbr_score = prev_ends[prev_ends['TeamID'].isin(gbr_team_ids)]['Result'].sum()
            opp_score = prev_ends[~prev_ends['TeamID'].isin(gbr_team_ids)]['Result'].sum()
            
            diff = gbr_score - opp_score
            print(f"Game {game_key}, PP at End {pp_end_id}: Score Diff {diff} (GBR {gbr_score}-{opp_score})")


if __name__ == "__main__":
    dfs = load_data()
    if 'stones' in dfs: # simple check if loaded
        analyze_powerplay(dfs)
    else:
        print("Data load failed.")
