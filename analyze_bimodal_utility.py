
import pandas as pd
import numpy as np
import os

DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"

def load_data():
    ends = pd.read_csv(os.path.join(DATA_DIR, "Ends.csv"))
    # Handle PowerPlay column correctly
    ends['PowerPlay'] = pd.to_numeric(ends['PowerPlay'], errors='coerce').fillna(0)
    # Ensure Result is numeric
    ends['Result'] = pd.to_numeric(ends['Result'], errors='coerce')
    return ends.dropna(subset=['Result'])

def analyze_bimodal():
    ends = load_data()
    
    # We need to find the "paired" rows for each end to see if it was a steal.
    # Pivot ends to have one row per end with Team A and Team B results
    # For PP analysis, we want Team A to be the PP team.
    
    # 1. Identify PP Ends and the team that called it
    pp_team_ends = ends[ends['PowerPlay'] > 0].copy()
    
    # 2. Get the opponent's result for the same end
    opponents = ends[ends['PowerPlay'] == 0].copy() # This is a heuristic, needs careful merge
    # Better: merge on Competition/Session/Game/End where TeamID != PP TeamID
    
    merged = pd.merge(
        pp_team_ends, 
        ends[['CompetitionID', 'SessionID', 'GameID', 'EndID', 'TeamID', 'Result']], 
        on=['CompetitionID', 'SessionID', 'GameID', 'EndID'],
        suffixes=('', '_Opp')
    )
    # Filter for the other team
    merged = merged[merged['TeamID'] != merged['TeamID_Opp']].copy()
    
    # Calculate signed result: PP Team Result - Opponent Result
    # If Result_Opp > 0 and Result == 0, that's a steal.
    merged['SignedResult'] = merged['Result'] - merged['Result_Opp']
    
    def get_bimodal_stats(df, label):
        steal_rate = (df['SignedResult'] < 0).mean() * 100
        big_end_rate = (df['SignedResult'] >= 3).mean() * 100
        conversion_rate = (df['SignedResult'] > 0).mean() * 100 # Scoring at least 1
        avg_points = df['SignedResult'].mean()
        return {
            'Mode': label,
            'Steal Rate': f"{steal_rate:.1f}%",
            'Efficiency (1+)': f"{conversion_rate:.1f}%",
            'Big End (3+)': f"{big_end_rate:.1f}%",
            'Avg Net Points': f"{avg_points:.2f}",
            'Sample Size (N)': len(df)
        }

    # Bimodal Breakdown: Early vs Late
    early_pp = merged[merged['EndID'] <= 2]
    mid_pp = merged[(merged['EndID'] >= 3) & (merged['EndID'] <= 6)]
    late_pp = merged[merged['EndID'] >= 7]
    
    bimodal_results = [
        get_bimodal_stats(early_pp, "Offensive Intent (End 1-2)"),
        get_bimodal_stats(mid_pp, "Balanced Intent (End 3-6)"),
        get_bimodal_stats(late_pp, "Defensive Intent (End 7-8)")
    ]
    
    print("\n--- Bimodal Power Play Utility ---")
    df_bi = pd.DataFrame(bimodal_results)
    print(df_bi.to_string())

if __name__ == "__main__":
    analyze_bimodal()

if __name__ == "__main__":
    analyze_bimodal()
