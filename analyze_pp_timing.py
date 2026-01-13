import pandas as pd
import os

# Configuration
DATA_DIR = "./"
if not os.path.exists(os.path.join(DATA_DIR, "Ends.csv")):
    DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"

def load_data():
    files = {
        "competitors": os.path.join(DATA_DIR, "Competitors.csv"),
        "ends": os.path.join(DATA_DIR, "Ends.csv"),
        "games": os.path.join(DATA_DIR, "Games.csv"),
        "teams": os.path.join(DATA_DIR, "Teams.csv")
    }
    dfs = {}
    for name, path in files.items():
        if os.path.exists(path):
            dfs[name] = pd.read_csv(path)
    return dfs

def analyze_timing(dfs):
    competitors = dfs['competitors']
    ends = dfs['ends']
    
    # 1. Identify Groups
    mowat_team_ids = competitors[competitors['Reportingname'].str.contains("MOUAT", case=False, na=False)]['TeamID'].unique()
    italy_team_ids = competitors[competitors['NOC'] == "ITA"]['TeamID'].unique()
    
    # Create GameKey
    ends['GameKey'] = ends['CompetitionID'].astype(str) + "_" + ends['SessionID'].astype(str) + "_" + ends['GameID'].astype(str)
    
    pp_events = []
    
    # Filter for PowerPlay rows (Assuming valuable if not NaN/0)
    # Check what PP values exist
    # print(ends['PowerPlay'].value_counts()) 
    # Usually 1=PP. Some might be 2? Data showed 2 in view_file. Let's treat any non-zero/non-null as PP.
    
    pp_rows = ends[ends['PowerPlay'].notna() & (ends['PowerPlay'] != 0)].copy()
    
    print(f"Found {len(pp_rows)} Power Play events.")
    
    # Pre-calculate scores per game/team/end to avoid slow loops
    # Group by GameKey, TeamID, EndID -> Sum Result
    # Actually, the file has 1 row per team per end.
    
    # We need running score.
    # Improve speed:
    # 1. Group by GameKey
    # 2. Iterate.
    
    game_groups = ends.groupby('GameKey')
    
    for idx, row in pp_rows.iterrows():
        game_key = row['GameKey']
        game_ends = game_groups.get_group(game_key)
        
        pp_team = row['TeamID']
        end_id = row['EndID']
        
        # Calculate running score of PREVIOUS ends
        prev_ends = game_ends[game_ends['EndID'] < end_id]
        
        if prev_ends.empty:
            my_score = 0
            opp_score = 0
        else:
            scores = prev_ends.groupby('TeamID')['Result'].sum()
            my_score = scores.get(pp_team, 0)
            opp_score = scores.drop(pp_team).sum() if pp_team in scores else scores.sum()
            
        diff = my_score - opp_score
        
        # Determine Outcome of THIS end (did they win?)
        # PP Team points in this end
        # "row" is the row with PP flag. Does it contain the score?
        # In the view_file, line 13 (Team 27, PP 1) had Result 1.
        # So yes, the row itself likely contains the score for that team.
        points_scored = row['Result']
        
        # Categorize Context
        # Categorize Context
        if diff >= 3: context = "Leading Big (>2)"
        elif diff == 2: context = "Leading 2"
        elif diff == 1: context = "Leading 1"
        elif diff == 0: context = "Tied"
        elif diff == -1: context = "Trailing 1"
        elif diff == -2: context = "Trailing 2"
        else: context = "Trailing Big (>2)"
        
        # Group
        group = "Field"
        if pp_team in mowat_team_ids: group = "Mowat"
        if pp_team in italy_team_ids: group = "Italy"
        
        # Determine Game Winner to calculate Win Prob
        # We need final game result.
        # Find the last end of this game
        final_end = game_ends.iloc[-1]
        
        # Determine winner ID
        # Ends.csv doesn't explicitly store winner per game easily without parsing scores.
        # But games_df might have it?
        # Let's rely on scoring.
        # Sum all scores.
        total_scores = game_ends.groupby('TeamID')['Result'].sum()
        winner_id = total_scores.idxmax() if not total_scores.empty else None
        won = (winner_id == pp_team)
        
        pp_events.append({
            'Group': group,
            'Context': context,
            'Diff': diff,
            'EndID': end_id,
            'Points': points_scored,
            'Success': points_scored >= 2,
            'WonGame': won
        })
        
    df = pd.DataFrame(pp_events)
    
    # Analysis 1: PP Usage by Context (When do they use it?)
    print("\n--- Context When Power Play is Called (%) ---")
    order = ["Trailing Big (>2)", "Trailing 2", "Trailing 1", "Tied", "Leading 1", "Leading 2", "Leading Big (>2)"]
    
    ctx_usage = df.groupby(['Group', 'Context']).size().unstack(fill_value=0)
    for o in order:
        if o not in ctx_usage.columns: ctx_usage[o] = 0
    ctx_usage = ctx_usage[order]
    
    print(ctx_usage.div(ctx_usage.sum(axis=1), axis=0).round(3) * 100)
    
    # Analysis 2: Success Rate (2+ pts) by Context
    print("\n--- Power Play Conversion Success (2+ pts) ---")
    success = df.pivot_table(index='Group', columns='Context', values='Success', aggfunc='mean')
    for o in order:
        if o not in success.columns: success[o] = 0.0
    success = success[order]
    print(success.round(2))

    # Analysis 3: Win Rate
    print("\n--- Game Win % When Using PP in Context ---")
    win_rate = df.pivot_table(index='Group', columns='Context', values='WonGame', aggfunc='mean')
    for o in order:
        if o not in win_rate.columns: win_rate[o] = 0.0
    win_rate = win_rate[order]
    print(win_rate.round(2))
    
    # Analysis 4: "Trailing 1 vs 2" Specifics
    print("\n--- Deep Dive: Trailing 1 vs 2 ---")
    trail = df[df['Context'].isin(["Trailing 1", "Trailing 2"])]
    print(trail.groupby(['Group', 'Context'])[['Points', 'Success', 'WonGame']].agg(['count', 'mean']).round(2))

    # Analysis 5: Early Power Play (Ends 1-4)
    print("\n--- Deep Dive: Early Power Play (Ends 1-4) ---")
    early = df[df['EndID'] <= 4].copy()
    print("Early PP Stats (Field only due to sample size?):")
    print(early.groupby('Group')[['Points', 'Success', 'WonGame']].agg(['count', 'mean']).round(2))
    
    print("\nComparison: Early vs Late (Field & Mowat combined)")
    df['Half'] = df['EndID'].apply(lambda x: "First Half (1-4)" if x <= 4 else "Second Half (5-8)")
    print(df.groupby('Half')[['Points', 'Success', 'WonGame']].agg(['count', 'mean']).round(2))

    print("\n--- Failure Analysis: Why does Early PP fail? ---")
    # Show value counts of 'Diff' (Score Differential) for Early PPs
    print("Score Differential distribution when PP is called in Ends 1-4:")
    print(early['Diff'].value_counts().sort_index())
    
    print("\n--- Bias Check: Desperation vs Control ---")
    # 1. Are there ANY non-desperate early PPs?
    non_desperate_early = early[early['Diff'] > -3]
    print(f"Number of Non-Desperate Early PPs (Diff > -3): {len(non_desperate_early)}")
    if len(non_desperate_early) > 0:
        print(non_desperate_early.groupby('Group')[['Points', 'Success', 'WonGame']].mean())
        
    # 2. Counterfactual: If you are Trailing Big (-3 or worse) in Ends 1-4,
    # what is the Win Rate for those who SAVE the PP vs those who USE it?
    # This requires looking at ALL ends data, not just PP events.
    # We need to find game states (Game, End) where Diff <= -3 and End <= 4.
    # Then check if they used PP (from df) or not.
    
    # We need a different approach to get the "Saved" group. 
    # Iterate all ends again?
    # Or just count outcomes. 
    # Win Rate of teams who were trailing by 3+ in First Half and did NOT use PP.
    
    # Let's approximate:
    # We found 43 Early PPs used when Trailing Big.
    # How many times were teams Trailing Big in Ends 1-4 and DIDN'T use it, and won?
    # This is complex to extract without full game state iteration.
    # Simplified Logic: 
    # We have `pp_events`. We lack non-PP events.
    # For now, let's just confirm the Lack of Data (Bias).
    print("Hypothesis: We only see desperate teams using early PP.")
    print(f"Total Early PPs: {len(early)}")
    print(f"Desperate Early PPs (Diff <= -3): {len(early[early['Diff'] <= -3])}")

if __name__ == "__main__":
    dfs = load_data()
    analyze_timing(dfs)
