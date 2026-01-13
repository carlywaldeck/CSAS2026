
import pandas as pd
import numpy as np
import os

# Configuration
DATA_DIR = "./"
if not os.path.exists(os.path.join(DATA_DIR, "Ends.csv")):
    DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"

def load_data():
    files = {
        "ends": os.path.join(DATA_DIR, "Ends.csv"),
    }
    dfs = {}
    for name, path in files.items():
        if os.path.exists(path):
            dfs[name] = pd.read_csv(path)
            
    return dfs

def analyze_first_strike(dfs):
    ends = dfs['ends']
    
    # We need to determine game winners first
    # Create GameKey
    ends['GameKey'] = ends['CompetitionID'].astype(str) + "_" + ends['SessionID'].astype(str) + "_" + ends['GameID'].astype(str)
    
    # Calculate Total Score per Team per Game
    game_scores = ends.groupby(['GameKey', 'TeamID'])['Result'].sum().reset_index()
    
    # Determine Winner
    # For each game, find team with max score
    # Note: Ties? Curling games usually end with a winner or draw.
    # We'll assume max score wins.
    
    winners = {}
    for game_key, grp in game_scores.groupby('GameKey'):
        winner_id = grp.loc[grp['Result'].idxmax(), 'TeamID']
        winners[game_key] = winner_id
        
    print(f"Games Analyzed: {len(winners)}")
    
    # Now analyze End 1 Scores
    end1 = ends[ends['EndID'] == 1].copy()
    
    results = []
    
    for idx, row in end1.iterrows():
        game_key = row['GameKey']
        team_id = row['TeamID']
        score = row['Result']
        
        # We need the opponent's score in End 1 to know the LEAD.
        # Find row for same game, same end, different team
        # Or faster: Group by End/Game
        pass 
        
    # Optimization: Pivot End 1
    # Check if 'starts_with_hammer' is known? 
    # Usually Hammer in End 1 is randomly assigned or alternating. 
    # We just care about "Leading by X after End 1".
    
    # Pivot end 1 data to have Team A vs Team B
    # Actually, simpler: for each row in End 1, calculate the differential relative to opponent.
    
    # Group by GameKey
    end1_games = end1.groupby('GameKey')
    
    states = []
    
    for game_key, group in end1_games:
        if len(group) != 2: continue # partial data?
        
        row_a = group.iloc[0]
        row_b = group.iloc[1]
        
        score_a = row_a['Result']
        score_b = row_b['Result']
        
        winner_id = winners.get(game_key)
        
        # Team A perspective
        diff_a = score_a - score_b
        won_a = (row_a['TeamID'] == winner_id)
        states.append({'Diff': diff_a, 'Won': won_a})
        
        # Team B perspective
        diff_b = score_b - score_a
        won_b = (row_b['TeamID'] == winner_id)
        states.append({'Diff': diff_b, 'Won': won_b})
        
    df = pd.DataFrame(states)
    
    print("\n--- The \"First Strike\" Value (End 1 Score Differential vs Win Rate) ---")
    
    # Group by Diff
    # Interested in: 0 (Tied), +1, +2, +3, +4
    # And negative counterparts (which should be symmetric)
    
    stats = df.groupby('Diff')['Won'].agg(['mean', 'count'])
    stats['Win %'] = (stats['mean'] * 100).round(1)
    
    # Filter for relevant leads
    print(stats.loc[stats.index.isin([0, 1, 2, 3, 4])])
    
    print("\n--- Interpretation ---")
    win_0 = stats.loc[0, 'mean']
    win_2 = stats.loc[2, 'mean'] if 2 in stats.index else 0
    win_3 = stats.loc[3, 'mean'] if 3 in stats.index else 0
    
    print(f"Win Probability if Tied (Blank End 1): {win_0*100:.1f}%")
    print(f"Win Probability if Leading by 2: {win_2*100:.1f}%")
    print(f"Win Probability if Leading by 3: {win_3*100:.1f}%")
    
    if win_2 > 0:
        increase = win_2 - win_0
        print(f"The 'First Strike' (scoring 2) increases Win Probability by +{increase*100:.1f}%")
        
    if win_3 > 0:
        increase3 = win_3 - win_0
        print(f"The 'Nuclear Strike' (scoring 3) increases Win Probability by +{increase3*100:.1f}%")


if __name__ == "__main__":
    dfs = load_data()
    analyze_first_strike(dfs)
