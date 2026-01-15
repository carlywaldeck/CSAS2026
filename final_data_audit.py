
import pandas as pd
import numpy as np
import os

DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"

def analyze():
    print("--- DATA AUDIT (PHASE 2: DECISION SUPPORT) ---")
    ends = pd.read_csv(os.path.join(DATA_DIR, "Ends.csv"))
    stones = pd.read_csv(os.path.join(DATA_DIR, "Stones.csv"))
    teams = pd.read_csv(os.path.join(DATA_DIR, "Teams.csv"))
    team_map = teams.set_index('TeamID')['NOC'].to_dict()
    
    ends['PowerPlay'] = pd.to_numeric(ends['PowerPlay'], errors='coerce').fillna(0)
    pp_callers = ends[ends['PowerPlay'] > 0][['CompetitionID', 'SessionID', 'GameID', 'EndID', 'TeamID', 'Result']].rename(columns={'TeamID': 'PPTeamID'})
    
    # Defenders
    defenders = pd.merge(ends, pp_callers[['CompetitionID', 'SessionID', 'GameID', 'EndID', 'PPTeamID']], on=['CompetitionID', 'SessionID', 'GameID', 'EndID'])
    defenders = defenders[defenders['TeamID'] != defenders['PPTeamID']].copy()
    print(f"Defending Ends: {len(defenders)}")

    # Stones in PP ends
    pp_stones_meta = pd.merge(stones, pp_callers, on=['CompetitionID', 'SessionID', 'GameID', 'EndID'])
    pp_shots_sorted = pp_stones_meta.sort_values(['CompetitionID', 'SessionID', 'GameID', 'EndID', 'ShotID'])
    
    # After Shot 3 State
    state_3 = pp_shots_sorted.groupby(['CompetitionID', 'SessionID', 'GameID', 'EndID']).nth(2).copy()
    
    results = []
    for _, row in state_3.iterrows():
        cc, ho, bg, hg = 0, False, False, False
        for i in range(1, 13):
            x, y = row[f'stone_{i}_x'], row[f'stone_{i}_y']
            if not np.isnan(x) and not np.isnan(y) and not (x == 0 and y == 0):
                if np.sqrt((x-750)**2 + (y-0)**2) <= 300: ho = True
                if abs(x-750) <= 200: cc += 1
                if abs(x-750) <= 150 and 1100 < y < 2900:
                    bg = True
                    if y > 2200: hg = True
        csi = cc + int(bg) + int(ho) + int(hg)
        results.append((cc, ho, bg, hg, csi))
        
    geom = pd.DataFrame(results, columns=['CC', 'HO', 'BG', 'HG', 'CSI'], index=state_3.index)
    state_3 = pd.concat([state_3, geom], axis=1).reset_index()
    
    # Response Shot (Shot 4)
    shot_4 = pp_shots_sorted.groupby(['CompetitionID', 'SessionID', 'GameID', 'EndID']).nth(3).copy().reset_index()
    
    ev_df = pd.merge(state_3[['CompetitionID', 'SessionID', 'GameID', 'EndID', 'CC', 'HO', 'CSI', 'PPTeamID', 'Result']], 
                     shot_4[['CompetitionID', 'SessionID', 'GameID', 'EndID', 'Task']], 
                     on=['CompetitionID', 'SessionID', 'GameID', 'EndID'])
    
    ev_df['Bucket'] = pd.cut(ev_df['CC'], bins=[-1, 1, 3, 12], labels=['Clean', 'Moderate', 'Heavy'])
    
    print("\n--- EV BY OPTION TABLE ---")
    ev_pivot = ev_df.pivot_table(index='Bucket', columns='Task', values='Result', aggfunc='mean', observed=True)
    # 0: Draw, 4: Wick, 3: Raise, 6: Takeout, 5: Freeze (often mapped to 0 or similar)
    print(ev_pivot[[0, 4, 3]].rename(columns={0:'Draw', 4:'Wick', 3:'Raise'}))

    # USA vs ITA
    ev_df['NOC'] = ev_df['PPTeamID'].map(team_map)
    gi = ev_df[ev_df['NOC'].isin(['USA', 'ITA', 'GBR'])].groupby('NOC')['Result'].agg(['mean', 'std', 'count'])
    print("\n--- PERFORMANCE COMPARISON ---")
    print(gi)
    
if __name__ == "__main__":
    analyze()
