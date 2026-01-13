import pandas as pd
import build_the_machine # We reuse your work from step 1!

CENTER_LINE_X = 750

def analyze_geometry():
    # 1. Get the Master Data
    print("Building the machine...")
    ends, stones = build_the_machine.load_data()
    df = build_the_machine.create_master_dataframe(ends, stones)
    
    print(f"Loaded {len(df)} rows of data.")
    
    # 2. The Hypothesis: "Clutter Kills Scoring"
    # We want to know if stones thrown close to the center line (x=750) 
    # early in the end result in lower scores for the shooter.
    
    # Filter for the "Setup Phase" (Shots 1-4 of the end)
    # We need to rank shots per end first
    df['ShotRank'] = df.groupby('EndKey')['ShotID'].rank(method='first').astype(int)
    setup_stones = df[df['ShotRank'] <= 4].copy()
    
    # 3. Calculate "Clutter" (Distance from Center)
    # 0 = Perfectly on center line
    # High Number = Wide open
    setup_stones['DistanceFromCenter'] = abs(setup_stones['stone_1_x'] - CENTER_LINE_X)
    
    # 4. Compare High Scoring Ends vs Low Scoring Ends
    # High Score: You scored 2+ points
    # Low Score: You scored 0 or 1, or gave up points
    
    # Define "Success" for the team throwing
    # Note: 'Result' is points for the Team specified in Ends.csv.
    # We need to be careful matching Stone Team to End Team.
    # For simplicity, let's look at the End outcome general property first:
    # "Do ends with Wide Centers produce Big Scores?"
    
    big_score_ends = setup_stones[setup_stones['Result'] >= 3]
    low_score_ends = setup_stones[setup_stones['Result'] <= 1]
    
    print("\n--- The Geometry of Winning ---")
    print(f"Avg Distance from Center (Big Score Ends): {big_score_ends['DistanceFromCenter'].mean():.2f}")
    print(f"Avg Distance from Center (Low Score Ends): {low_score_ends['DistanceFromCenter'].mean():.2f}")
    
    if big_score_ends['DistanceFromCenter'].mean() > low_score_ends['DistanceFromCenter'].mean():
        print("\nCONCLUSION: KEEP IT OPEN! Ends with stones further from the center tend to have BIGGER scores.")
    else:
        print("\nCONCLUSION: CLUTTER IT UP! Ends with stones closer to the center tend to have BIGGER scores.")

if __name__ == "__main__":
    analyze_geometry()
