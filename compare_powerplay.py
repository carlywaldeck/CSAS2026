import pandas as pd
import os

# Configuration
DATA_DIR = "./"  # Assumes data is in the current directory
if not os.path.exists(os.path.join(DATA_DIR, "Ends.csv")):
    DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"

def load_data():
    """Load necessary CSV files."""
    files = {
        "competitors": os.path.join(DATA_DIR, "Competitors.csv"),
        "ends": os.path.join(DATA_DIR, "Ends.csv"),
        "stones": os.path.join(DATA_DIR, "Stones.csv"),
        "teams": os.path.join(DATA_DIR, "Teams.csv")
    }
    
    dfs = {}
    print("Loading data files...")
    for name, path in files.items():
        if os.path.exists(path):
            dfs[name] = pd.read_csv(path)
        else:
            print(f"Warning: {path} not found.")
            return None
    return dfs

def get_end_keys(df):
    return (
        df['CompetitionID'].astype(str) + "_" + 
        df['SessionID'].astype(str) + "_" + 
        df['GameID'].astype(str) + "_" + 
        df['EndID'].astype(str)
    )

def analyze_comparison(dfs):
    competitors = dfs['competitors']
    ends = dfs['ends']
    stones = dfs['stones']
    
    # 1. Identify Team Groups
    # Group A: Bruce Mowat (GBR/SCO)
    mowat_entries = competitors[competitors['Reportingname'].str.contains("MOUAT", case=False, na=False)]
    mowat_team_ids = mowat_entries['TeamID'].unique()
    
    # Group B: Italy
    # Italy could be TeamID 24 (Constantini/Mosaner) primarily
    italy_entries = competitors[competitors['NOC'] == "ITA"]
    italy_team_ids = italy_entries['TeamID'].unique()
    
    print(f"Mowat Teams: {mowat_team_ids}")
    print(f"Italy Teams: {italy_team_ids}")
    
    # 2. Filter Power Play Ends
    # Only keep ends where PowerPlay is True (or 1)
    pp_ends = ends[ends['PowerPlay'].notna() & (ends['PowerPlay'] != False) & (ends['PowerPlay'] != 0)].copy()
    
    # Exclude null TeamIDs
    pp_ends = pp_ends.dropna(subset=['TeamID'])
    
    # Assign Groups
    def get_group(tid):
        if tid in mowat_team_ids: return "Mowat"
        if tid in italy_team_ids: return "Italy"
        return "Field"
        
    pp_ends['Group'] = pp_ends['TeamID'].apply(get_group)
    
    # 3. Efficiency Metrics
    # Result is the score for the team in 'TeamID' (the hammer team, usually)
    # Check if 'Result' is points scored by TeamID. In Ends.csv, Result usually implies score for the team listed?
    # Actually, in Ends.csv, columns are usually TeamID (hammer?) and Result. 
    # Let's verify assumption: 'Result' is points scored by 'TeamID'.
    
    print("\n--- Power Play Efficiency ---")
    stats = pp_ends.groupby('Group')['Result'].agg(['count', 'mean', 'std']).rename(columns={'count': 'Ends', 'mean': 'Avg Pts'})
    
    # Conversion Rates
    # Scoring 2+
    pp_ends['Score_2plus'] = pp_ends['Result'] >= 2
    # Scoring 3+ (Big End)
    pp_ends['Score_3plus'] = pp_ends['Result'] >= 3
    # Scoring 4+
    pp_ends['Score_4plus'] = pp_ends['Result'] >= 4
    
    conv_2 = pp_ends.groupby('Group')['Score_2plus'].mean()
    conv_3 = pp_ends.groupby('Group')['Score_3plus'].mean()
    conv_4 = pp_ends.groupby('Group')['Score_4plus'].mean()
    
    summary = pd.concat([stats, conv_2, conv_3, conv_4], axis=1)
    summary.columns = ['Ends', 'Avg Pts', 'Std Dev', '2+ %', '3+ %', '4+ %']
    print(summary.round(3))
    
    # 4. Strategy Analysis - Getting to 3+ Points
    print("\n--- Strategy Analysis for Big Scores (3+) ---")
    
    # Helper to map tasks
    task_map = {
        0: "Draw", 1: "Front", 2: "Guard", 3: "Raise", 4: "Wick", 5: "Freeze",
        6: "Take-out", 7: "Hit and Roll", 8: "Clearing", 9: "Double Take-out",
        10: "Prom Take-out", 11: "Through"
    }
    
    # Link Stones to Ends
    stones['EndKey'] = get_end_keys(stones)
    pp_ends['EndKey'] = get_end_keys(pp_ends)
    
    # Filter Stones for PP ends
    pp_stones = stones[stones['EndKey'].isin(pp_ends['EndKey'])].copy()
    
    # Merge Group info to stones
    pp_stones = pp_stones.merge(pp_ends[['EndKey', 'Group', 'Result']], on='EndKey', how='left')
    
    # Determine Shot Rank (order within end)
    pp_stones['ShotRank'] = pp_stones.groupby('EndKey')['ShotID'].rank(method='first').astype(int)
    
    # Analyze Shot 2 (First shot by PP team) for Mowat vs Italy
    # Filter for Rank 2
    shot2 = pp_stones[pp_stones['ShotRank'] == 2].copy()
    shot2['TaskName'] = shot2['Task'].map(task_map).fillna("Unknown")
    
    # Compare Shot 2 Selection
    print("\nShot 2 Selection Distribution (Proportion):")
    selection = shot2.groupby(['Group', 'TaskName']).size().unstack(fill_value=0)
    selection_pct = selection.div(selection.sum(axis=1), axis=0)
    print(selection_pct.round(3))
    
    # Compare success rate (3+ result) by Shot 2 type for Mowat
    print("\nMowat: Avg Score by Shot 2 Type:")
    mowat_s2 = shot2[shot2['Group'] == 'Mowat']
    print(mowat_s2.groupby('TaskName')['Result'].agg(['count', 'mean']).sort_values('mean', ascending=False))
    
    print("\nItaly: Avg Score by Shot 2 Type:")
    italy_s2 = shot2[shot2['Group'] == 'Italy']
    print(italy_s2.groupby('TaskName')['Result'].agg(['count', 'mean']).sort_values('mean', ascending=False))
    
    # 5. Defensive Analysis - Pre-Emptve Stops?
    # Look at Shot 1 (Opponent's first stone)
    # Filter Rank 1
    shot1 = pp_stones[pp_stones['ShotRank'] == 1].copy()
    shot1['TaskName'] = shot1['Task'].map(task_map).fillna("Unknown")
    
    # Does the opponent play differently against Mowat?
    print("\nOpponent Shot 1 Selection vs Group:")
    opp_selection = shot1.groupby(['Group', 'TaskName']).size().unstack(fill_value=0)
    opp_selection_pct = opp_selection.div(opp_selection.sum(axis=1), axis=0)
    print(opp_selection_pct.round(3))
    
    # 6. Conditions for 3+ Points
    # Filter for all Big Ends across the field
    big_ends = pp_stones[(pp_stones['Result'] >= 3) & (pp_stones['ShotRank'] <= 5)].copy()
    # Simple check on Shot 2 choice for ANY team scoring 3+
    print("\nMost Common Shot 2 choice when scoring 3+ (Universal):")
    big_s2 = big_ends[big_ends['ShotRank'] == 2]
    big_s2['TaskName'] = big_s2['Task'].map(task_map)
    print(big_s2['TaskName'].value_counts(normalize=True).head())

if __name__ == "__main__":
    dfs = load_data()
    if dfs:
        analyze_comparison(dfs)
