
import pandas as pd
import numpy as np
import os

DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"

def load_data():
    ends = pd.read_csv(os.path.join(DATA_DIR, "Ends.csv"))
    stones = pd.read_csv(os.path.join(DATA_DIR, "Stones.csv"))
    teams = pd.read_csv(os.path.join(DATA_DIR, "Teams.csv"))
    return ends, stones, teams

def has_guard_static(row):
    for i in range(1, 13):
        y = row[f'stone_{i}_y']
        if not np.isnan(y) and 2000 < y < 4880: return True
    return False

def analyze():
    print("Starting Analysis...")
    ends, stones, teams = load_data()
    ends['PowerPlay'] = pd.to_numeric(ends['PowerPlay'], errors='coerce').fillna(0)
    
    # Filter for PP ends only
    pp_game_ends = ends[ends['PowerPlay'] > 0][['CompetitionID', 'SessionID', 'GameID', 'EndID']].drop_duplicates()
    pp_stones = pd.merge(stones, pp_game_ends, on=['CompetitionID', 'SessionID', 'GameID', 'EndID'])
    pp_stones = pp_stones.sort_values(['CompetitionID', 'SessionID', 'GameID', 'EndID', 'ShotID'])
    
    # 1. State after 3 shots
    # We take the 3rd shot recorded in each PP end
    state_after_3 = pp_stones.groupby(['CompetitionID', 'SessionID', 'GameID', 'EndID']).nth(2).copy().reset_index()
    
    in_house_list = []
    congestion_list = []
    for _, row in state_after_3.iterrows():
        ih, co = 0, 0
        for i in range(1, 13):
            x, y = row[f'stone_{i}_x'], row[f'stone_{i}_y']
            # Coordinates (0,0) are outside the field of play in this context (Tee is 750,0 or similar)
            if not np.isnan(x) and not np.isnan(y) and not (x == 0 and y == 0):
                # Distance to button (750, 0)
                dist = np.sqrt((x-750)**2 + (y-0)**2)
                if dist <= 300: ih += 1
                if abs(x-750) <= 200: co += 1
        in_house_list.append(ih)
        congestion_list.append(co)
        
    state_after_3['InHouse'] = in_house_list
    state_after_3['Congestion'] = congestion_list
    state_after_3['HasGuardAt3'] = state_after_3.apply(has_guard_static, axis=1)
    
    # Merge with results for the PP caller
    pp_info = ends[ends['PowerPlay'] > 0][['CompetitionID', 'SessionID', 'GameID', 'EndID', 'TeamID', 'Result']]
    calc_df = pd.merge(state_after_3, pp_info, on=['CompetitionID', 'SessionID', 'GameID', 'EndID'], suffixes=('_stone', ''))
    
    # Buckets for Probability Calculator
    calc_df['CongestionBucket'] = pd.cut(calc_df['Congestion'], bins=[-1, 2, 4, 12], labels=['Clean', 'Moderate', 'Heavy'])
    calc_df['HouseBucket'] = pd.cut(calc_df['InHouse'], bins=[-1, 1, 12], labels=['Empty/1', 'Occupied'])
    
    def sum_probs(group):
        return pd.Series({
            'Avg': group['Result'].mean(),
            'P(0)': (group['Result'] == 0).mean() * 100,
            'P(1)': (group['Result'] == 1).mean() * 100,
            'P(2)': (group['Result'] == 2).mean() * 100,
            'P(3+)': (group['Result'] >= 3).mean() * 100,
            'N': len(group)
        })

    summary = calc_df.groupby(['CongestionBucket', 'HouseBucket'], observed=True).apply(sum_probs).unstack()
    print("\n--- Shot 3 Outcomes Calculator ---")
    print(summary.to_string())

    # 2. Draw under guard failure
    pp_stones['HasGuard'] = pp_stones.apply(has_guard_static, axis=1)
    dug = pp_stones[(pp_stones['Task'] == 0) & (pp_stones['HasGuard'] == True)]
    # End-level 0 results for DUG attempts
    dug_ends = pd.merge(dug, pp_info, on=['CompetitionID', 'SessionID', 'GameID', 'EndID'])
    print(f"\n--- Draw Under Guard Failure (End Result=0): {(dug_ends['Result'] == 0).mean()*100:.1f}% ---")
    print(f"--- Draw Under Guard Shot Failure (Points=0): {(dug['Points'] == 0).mean()*100:.1f}% ---")

    # 3. USA CSI
    team_map = teams.set_index('TeamID')['NOC'].to_dict()
    calc_df['NOC'] = calc_df['TeamID'].map(team_map)
    usa = calc_df[calc_df['NOC'] == 'USA'].copy()
    if not usa.empty:
        usa['CSI'] = usa['Congestion'] + usa['HasGuardAt3'].astype(int)
        csi_big_end = usa.groupby('CSI')['Result'].apply(lambda x: (x >= 3).mean() * 100)
        print("\n--- USA CSI vs Big End Prob (%) ---")
        print(csi_big_end.to_string())

if __name__ == "__main__":
    analyze()
