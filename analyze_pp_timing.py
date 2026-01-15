
import pandas as pd
import numpy as np
import os

DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"

def load_data():
    ends = pd.read_csv(os.path.join(DATA_DIR, "Ends.csv"))
    games = pd.read_csv(os.path.join(DATA_DIR, "Games.csv"))
    return ends, games

def analyze_pp_timing():
    ends, games = load_data()
    
    # Identify PP Ends
    pp_ends = ends[ends['PowerPlay'] > 0].copy()
    
    # Categorize Timing
    def categorize_end(end_id):
        if end_id <= 2: return "Early (1-2)"
        if end_id <= 4: return "Mid (3-4)"
        if end_id <= 6: return "Late (5-6)"
        return "Final (7-8)"

    pp_ends['Timing'] = pp_ends['EndID'].apply(categorize_end)
    
    # Scoring Efficiency
    timing_stats = pp_ends.groupby('Timing')['Result'].agg(['mean', 'count']).rename(columns={'mean': 'AvgPoints'})
    
    # Win Probability
    # Merge with game results
    winners = games[['CompetitionID', 'SessionID', 'GameID', 'WinnerID']]
    pp_outcomes = pd.merge(pp_ends, winners, on=['CompetitionID', 'SessionID', 'GameID'])
    
    pp_outcomes['IsWinner'] = pp_outcomes['TeamID'] == pp_outcomes['WinnerID']
    win_probs = pp_outcomes.groupby('Timing')['IsWinner'].mean() * 100
    
    timing_stats['WinProb'] = win_probs
    
    print("\n--- Power Play Timing Efficiency ---")
    print(timing_stats)
    
    print("\n--- Summary ---")
    best_timing = timing_stats['AvgPoints'].idxmax()
    print(f"Optimal Timing for Points: {best_timing}")

if __name__ == "__main__":
    analyze_pp_timing()
