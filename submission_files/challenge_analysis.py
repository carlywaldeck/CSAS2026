"""
CSAS 2026 Curling Data Challenge - Strategic Analysis
Power Play Deployment Analysis for Mixed Doubles Curling

This script analyzes Power Play strategy in international Mixed Doubles Curling competition.
It calculates key metrics to answer: When should teams deploy the Power Play?

Author: Cal Poly Student (CS 202)
Date: 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ============================================================================
# CONSTANTS - These values come from the challenge description
# ============================================================================

# The button (center of the house) is at these coordinates
BUTTON_X = 750
BUTTON_Y = 800

# A stone is "in the house" if it's within 600 units of the button
HOUSE_RADIUS = 600

# The center corridor is defined as |X - 750| < 200
CENTER_CORRIDOR_WIDTH = 200
CENTER_LINE_X = 750

# Special values in the data:
# - 4095 means the stone was knocked off the sheet
# - 0 means the stone hasn't been thrown yet
SENTINEL_VALUE = 4095  # Stone removed from play
NOT_THROWN = 0  # Stone not yet thrown

# Where our data files are located
DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"


# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_data():
    """
    Load the CSV files we need for analysis.
    
    Returns:
        stones: DataFrame with stone-level data (each row is one shot)
        ends: DataFrame with end-level data (each row is one end)
    """
    stones = pd.read_csv(os.path.join(DATA_DIR, "Stones.csv"))
    ends = pd.read_csv(os.path.join(DATA_DIR, "Ends.csv"))
    return stones, ends


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_distance_to_button(x, y):
    """
    Calculate how far a stone is from the button (center of the house).
    
    Uses the distance formula: sqrt((x1-x2)^2 + (y1-y2)^2)
    
    Args:
        x: X coordinate of the stone
        y: Y coordinate of the stone
    
    Returns:
        Distance from the button
    """
    # Calculate the difference in x and y coordinates
    x_diff = x - BUTTON_X
    y_diff = y - BUTTON_Y
    
    # Use Pythagorean theorem to get distance
    distance = np.sqrt(x_diff**2 + y_diff**2)
    return distance


# ============================================================================
# MAIN ANALYSIS FUNCTIONS
# ============================================================================

def calculate_traffic(stones_df):
    """
    Calculate "Traffic" - how many stones are in the house at each shot.
    
    This is like "traffic on the bases" in baseball - more stones in the house
    means it's harder to make shots because there are obstacles in the way.
    
    Args:
        stones_df: DataFrame with stone position data
    
    Returns:
        DataFrame with a new 'Traffic' column added
    """
    print("\n" + "="*70)
    print("1. TRAFFIC CALCULATION")
    print("="*70)
    
    # Make a copy so we don't modify the original data
    stones = stones_df.copy()
    
    # This list will store the traffic count for each shot
    traffic_values = []
    
    # Loop through each shot (each row in the dataframe)
    for idx, row in stones.iterrows():
        stones_in_house = 0
        
        # Check each of the 12 possible stone positions
        for stone_num in range(1, 13):
            # Get the x and y coordinates for this stone
            x_col = f'stone_{stone_num}_x'
            y_col = f'stone_{stone_num}_y'
            
            x_val = row[x_col]
            y_val = row[y_col]
            
            # Skip stones that haven't been thrown or were knocked off
            if pd.isna(x_val) or pd.isna(y_val):
                continue
            if x_val == NOT_THROWN or y_val == NOT_THROWN:
                continue
            if x_val == SENTINEL_VALUE or y_val == SENTINEL_VALUE:
                continue
            
            # Calculate distance to button
            distance = calculate_distance_to_button(x_val, y_val)
            
            # If the stone is within the house radius, count it
            if distance <= HOUSE_RADIUS:
                stones_in_house += 1
        
        # Store the traffic count for this shot
        traffic_values.append(stones_in_house)
    
    # Add the traffic column to our dataframe
    stones['Traffic'] = traffic_values
    
    # Print summary statistics
    print(f"\nTotal shots analyzed: {len(stones):,}")
    print(f"Average Traffic (stones in house per shot): {stones['Traffic'].mean():.2f}")
    print(f"Maximum Traffic (most congested state): {stones['Traffic'].max()}")
    print(f"Standard deviation: {stones['Traffic'].std():.2f}")
    
    print("\nTraffic Statistics by End:")
    traffic_by_end = stones.groupby('EndID')['Traffic'].agg(['mean', 'max']).round(2)
    print(traffic_by_end)
    
    return stones


def calculate_power_play_readiness_score(stones_df, ends_df):
    """
    Calculate Power Play Readiness Score (PPRS) for early ends.
    
    This measures how clogged the center corridor is in the first two ends.
    If the center is too crowded, it might not be a good time for a Power Play.
    
    Args:
        stones_df: DataFrame with stone position data
        ends_df: DataFrame with end-level data
    
    Returns:
        DataFrame with PPRS column added for ends 1-2
    """
    print("\n" + "="*70)
    print("2. POWER PLAY READINESS SCORE (PPRS) CALCULATION")
    print("="*70)
    
    # Make a copy and filter to just the first two ends
    stones = stones_df.copy()
    early_ends = stones[stones['EndID'].isin([1, 2])].copy()
    
    # This list will store the PPRS for each shot
    pprs_values = []
    
    # Loop through each shot in the early ends
    for idx, row in early_ends.iterrows():
        center_stones = 0
        
        # Check each of the 12 possible stone positions
        for stone_num in range(1, 13):
            x_col = f'stone_{stone_num}_x'
            y_col = f'stone_{stone_num}_y'
            
            x_val = row[x_col]
            y_val = row[y_col]
            
            # Skip stones that haven't been thrown or were knocked off
            if pd.isna(x_val) or pd.isna(y_val):
                continue
            if x_val == NOT_THROWN or y_val == NOT_THROWN:
                continue
            if x_val == SENTINEL_VALUE or y_val == SENTINEL_VALUE:
                continue
            
            # Check if stone is in the center corridor: |X - 750| < 200
            x_distance_from_center = abs(x_val - CENTER_LINE_X)
            if x_distance_from_center < CENTER_CORRIDOR_WIDTH:
                center_stones += 1
        
        pprs_values.append(center_stones)
    
    # Add the PPRS column
    early_ends['PPRS'] = pprs_values
    
    # Print summary statistics
    print(f"\nTotal shots in Ends 1-2: {len(early_ends):,}")
    print(f"Average PPRS (center corridor stones): {early_ends['PPRS'].mean():.2f}")
    print(f"Maximum PPRS: {early_ends['PPRS'].max()}")
    
    print("\nPPRS by End:")
    pprs_by_end = early_ends.groupby('EndID')['PPRS'].agg(['mean', 'max']).round(2)
    print(pprs_by_end)
    
    return early_ends


def analyze_power_play_deployment(ends_df):
    """
    Analyze when teams deploy Power Plays and how effective they are.
    
    This function looks at:
    - How many Power Plays happen in each end
    - Average points scored in each end
    - "Big End" rate (ends where teams score 3+ points)
    
    Args:
        ends_df: DataFrame with end-level data
    
    Returns:
        DataFrame with Power Play ends and analysis
    """
    print("\n" + "="*70)
    print("3. POWER PLAY DEPLOYMENT ANALYSIS")
    print("="*70)
    
    # Filter to only Power Play ends (PowerPlay column is not NaN and > 0)
    pp_ends = ends_df[ends_df['PowerPlay'].notna() & (ends_df['PowerPlay'] > 0)].copy()
    
    # Overall statistics
    print(f"\nTotal Power Play Ends: {len(pp_ends)}")
    print(f"Overall Average Points: {pp_ends['Result'].mean():.2f}")
    
    # Calculate Big End rate (percentage of Power Plays scoring 3+ points)
    big_end_count = (pp_ends['Result'] >= 3).sum()
    big_end_rate = (big_end_count / len(pp_ends)) * 100
    print(f"Overall Big End Rate (3+ pts): {big_end_rate:.1f}%")
    
    # Analyze by end number
    print("\n" + "-" * 70)
    print("DEPLOYMENT DISTRIBUTION BY END:")
    print("-" * 70)
    
    # Group by end and calculate statistics
    end_stats = pp_ends.groupby('EndID').agg({
        'Result': ['count', 'mean'],
    }).round(2)
    end_stats.columns = ['Count', 'AvgPoints']
    end_stats['Percentage'] = (end_stats['Count'] / len(pp_ends) * 100).round(1)
    print(end_stats)
    
    # Categorize ends into Early, Middle, and Late
    def categorize_end(end_num):
        """Helper function to categorize ends"""
        if end_num <= 2:
            return 'Early (1-2)'
        elif end_num >= 7:
            return 'Late (7-8)'
        else:
            return 'Middle (3-6)'
    
    pp_ends['EndCategory'] = pp_ends['EndID'].apply(categorize_end)
    
    # Calculate statistics by category
    category_stats = pp_ends.groupby('EndCategory').agg({
        'Result': ['mean', 'count'],
    }).round(2)
    
    # Calculate Big End rate by category
    big_end_by_category = pp_ends.groupby('EndCategory').apply(
        lambda x: (x['Result'] >= 3).sum() / len(x) * 100
    ).round(2)
    
    print("\n" + "-" * 70)
    print("PERFORMANCE BY CATEGORY:")
    print("-" * 70)
    print("\nAverage Points Scored:")
    print(category_stats[('Result', 'mean')])
    print("\nNumber of Power Plays:")
    print(category_stats[('Result', 'count')])
    print("\nBig End Rate (% with Result >= 3):")
    print(big_end_by_category)
    
    # Special analysis for early Power Plays (the key finding)
    early_pp = pp_ends[pp_ends['EndCategory'] == 'Early (1-2)']
    print("\n" + "-" * 70)
    print("EARLY POWER PLAY ANALYSIS (Ends 1-2):")
    print("-" * 70)
    print(f"Count: {len(early_pp)}")
    if len(early_pp) > 0:
        print(f"Average Points: {early_pp['Result'].mean():.2f}")
        print(f"Percentage of Total PPs: {len(early_pp) / len(pp_ends) * 100:.2f}%")
    else:
        print("No early power plays found in dataset.")
    
    return pp_ends


def analyze_shot_accuracy(stones_df):
    """
    Compare execution quality between different shot types.
    
    Task 0 = Draw (standard shot to the house)
    Task 4 = Wick/Tick (trick shot using other stones)
    
    The Points column is an execution score from 0-4, where 4.0 is perfect.
    
    Args:
        stones_df: DataFrame with stone-level data
    
    Returns:
        Tuple of (draws DataFrame, wicks DataFrame)
    """
    print("\n" + "="*70)
    print("4. SHOT ACCURACY ANALYSIS - Draw vs Wick")
    print("="*70)
    
    # Filter to just Draws (Task 0) and Wicks (Task 4)
    draws = stones_df[stones_df['Task'] == 0].copy()
    wicks = stones_df[stones_df['Task'] == 4].copy()
    
    # Calculate average execution scores
    draw_avg = draws['Points'].mean()
    wick_avg = wicks['Points'].mean()
    
    # Print results
    print(f"\nDraws (Task 0):")
    print(f"  Total shots: {len(draws):,}")
    print(f"  Average execution score: {draw_avg:.2f}/4.0")
    print(f"  Standard deviation: {draws['Points'].std():.2f}")
    
    print(f"\nWicks/Ticks (Task 4):")
    print(f"  Total shots: {len(wicks):,}")
    print(f"  Average execution score: {wick_avg:.2f}/4.0")
    print(f"  Standard deviation: {wicks['Points'].std():.2f}")
    
    # Calculate the difference
    if len(draws) > 0 and len(wicks) > 0:
        diff = draw_avg - wick_avg
        pct_diff = (diff / wick_avg) * 100 if wick_avg > 0 else 0
        print(f"\nDifference (Draw - Wick): {diff:+.2f} points")
        print(f"Percentage difference: {pct_diff:+.1f}%")
        print(f"  This is the 'Execution Gap' - Draws are {pct_diff:.1f}% more reliable")
    
    return draws, wicks


def analyze_traffic_impact(stones_with_traffic, ends_df):
    """
    Analyze how Traffic (house congestion) affects Power Play scoring.
    
    This is the key finding: when there are too many stones in the house,
    Power Plays become less effective. We call this the "Traffic Tax."
    
    Args:
        stones_with_traffic: DataFrame with Traffic already calculated
        ends_df: DataFrame with end-level data
    
    Returns:
        DataFrame with Traffic categories added
    """
    print("\n" + "="*70)
    print("5. TRAFFIC IMPACT ON POWER PLAY SCORING")
    print("="*70)
    
    # Merge stones data with ends data to get Power Play results
    stones_merged = pd.merge(
        stones_with_traffic,
        ends_df[['CompetitionID', 'SessionID', 'GameID', 'EndID', 'Result', 'PowerPlay']],
        on=['CompetitionID', 'SessionID', 'GameID', 'EndID'],
        how='inner'
    )
    
    # Filter to only Power Play ends
    pp_stones = stones_merged[
        stones_merged['PowerPlay'].notna() & 
        (stones_merged['PowerPlay'] > 0)
    ].copy()
    
    # Categorize Traffic levels
    # Low: 0-2 stones, Medium: 3-4 stones, High: 5+ stones
    pp_stones['Traffic_Category'] = pd.cut(
        pp_stones['Traffic'],
        bins=[-1, 2, 4, 20],
        labels=['Low Traffic (0-2)', 'Medium Traffic (3-4)', 'High Traffic (5+)']
    )
    
    # Calculate average points scored by Traffic category
    scoring_by_traffic = pp_stones.groupby('Traffic_Category').agg({
        'Result': ['mean', 'count'],
    }).round(2)
    
    # Calculate Big End rate by Traffic category
    big_end_by_traffic = pp_stones.groupby('Traffic_Category').apply(
        lambda x: (x['Result'] >= 3).sum() / len(x) * 100
    ).round(2)
    
    # Print results
    print(f"\nTotal Power Play shots analyzed: {len(pp_stones):,}")
    print("\nAverage Points Scored by Traffic Level:")
    print(scoring_by_traffic[('Result', 'mean')])
    print("\nSample Size by Traffic Level:")
    print(scoring_by_traffic[('Result', 'count')])
    print("\nBig End Rate (% with Result >= 3) by Traffic:")
    print(big_end_by_traffic)
    
    # Calculate the Traffic Tax (efficiency penalty from high Traffic)
    low_traffic = pp_stones[pp_stones['Traffic_Category'] == 'Low Traffic (0-2)']
    high_traffic = pp_stones[pp_stones['Traffic_Category'] == 'High Traffic (5+)']
    
    if len(low_traffic) > 0 and len(high_traffic) > 0:
        avg_low = low_traffic['Result'].mean()
        avg_high = high_traffic['Result'].mean()
        
        # Calculate percentage change
        traffic_tax = ((avg_high - avg_low) / avg_low) * 100 if avg_low > 0 else 0
        
        print(f"\n" + "-" * 70)
        print(f"TRAFFIC TAX ANALYSIS:")
        print(f"Low Traffic (0-2 stones): {avg_low:.2f} points")
        print(f"High Traffic (5+ stones): {avg_high:.2f} points")
        print(f"Traffic Tax: {traffic_tax:+.1f}%")
        
        if traffic_tax < 0:
            print(f"\nKEY FINDING: High traffic REDUCES scoring efficiency by {abs(traffic_tax):.1f}%")
            print(f"This quantifies the geometric penalty of house congestion.")
    
    return pp_stones


def analyze_team_comparison(ends_df, stones_df):
    """
    Compare Power Play performance between different teams (GBR vs Italy).
    
    This helps us understand why some teams are better at Power Plays than others.
    
    Args:
        ends_df: DataFrame with end-level data
        stones_df: DataFrame with stone-level data
    
    Returns:
        Dictionary with comparison statistics
    """
    print("\n" + "="*70)
    print("6. TEAM COMPARISON: GBR vs Italy")
    print("="*70)
    
    # Try to load teams data
    try:
        teams = pd.read_csv(os.path.join(DATA_DIR, "Teams.csv"))
    except:
        print("Teams.csv not found - cannot identify GBR/Italy teams")
        return None
    
    # Find GBR and Italy team IDs
    gbr_teams = teams[teams['NOC'] == 'GBR']
    ita_teams = teams[teams['NOC'] == 'ITA']
    
    if gbr_teams.empty or ita_teams.empty:
        print("GBR or Italy teams not found in dataset")
        return None
    
    gbr_team_ids = gbr_teams['TeamID'].unique().tolist()
    ita_team_ids = ita_teams['TeamID'].unique().tolist()
    
    print(f"\nGBR Teams Found: {len(gbr_team_ids)}")
    print(f"Italy Teams Found: {len(ita_team_ids)}")
    
    # Filter to Power Play ends
    pp_ends = ends_df[ends_df['PowerPlay'].notna() & (ends_df['PowerPlay'] > 0)].copy()
    
    gbr_pp = pp_ends[pp_ends['TeamID'].isin(gbr_team_ids)]
    ita_pp = pp_ends[pp_ends['TeamID'].isin(ita_team_ids)]
    
    print("\n" + "-" * 70)
    print("POWER PLAY PERFORMANCE COMPARISON:")
    print("-" * 70)
    
    # GBR statistics
    if len(gbr_pp) > 0:
        gbr_avg = gbr_pp['Result'].mean()
        gbr_big_end = (gbr_pp['Result'] >= 3).sum() / len(gbr_pp) * 100
        gbr_std = gbr_pp['Result'].std()
        print(f"\nGBR Power Play Performance:")
        print(f"  Sample Size: {len(gbr_pp)}")
        print(f"  Average Points: {gbr_avg:.2f}")
        print(f"  Big End Rate (3+): {gbr_big_end:.1f}%")
        print(f"  Standard Deviation: {gbr_std:.2f}")
    else:
        gbr_avg = 0
        gbr_big_end = 0
        gbr_std = 0
        print("\nGBR: No Power Play data found")
    
    # Italy statistics
    if len(ita_pp) > 0:
        ita_avg = ita_pp['Result'].mean()
        ita_big_end = (ita_pp['Result'] >= 3).sum() / len(ita_pp) * 100
        ita_std = ita_pp['Result'].std()
        print(f"\nItaly Power Play Performance:")
        print(f"  Sample Size: {len(ita_pp)}")
        print(f"  Average Points: {ita_avg:.2f}")
        print(f"  Big End Rate (3+): {ita_big_end:.1f}%")
        print(f"  Standard Deviation: {ita_std:.2f}")
    else:
        ita_avg = 0
        ita_big_end = 0
        ita_std = 0
        print("\nItaly: No Power Play data found")
    
    return {
        'gbr_avg': gbr_avg,
        'ita_avg': ita_avg,
        'gbr_big_end': gbr_big_end,
        'ita_big_end': ita_big_end,
        'gbr_std': gbr_std,
        'ita_std': ita_std,
        'gbr_n': len(gbr_pp),
        'ita_n': len(ita_pp)
    }


def create_visualization(ends_df):
    """
    Create a bar chart showing Power Play effectiveness by end number.
    
    This visualization helps us see the pattern: Power Plays are more effective
    in later ends (especially End 8).
    
    Args:
        ends_df: DataFrame with end-level data
    """
    print("\n" + "="*70)
    print("7. VISUALIZATION: Power Play Success by End")
    print("="*70)
    
    # Filter to Power Play ends
    pp_ends = ends_df[ends_df['PowerPlay'].notna() & (ends_df['PowerPlay'] > 0)].copy()
    
    # Group by end and calculate statistics
    by_end = pp_ends.groupby('EndID').agg({
        'Result': ['mean', 'count', 'std']
    }).reset_index()
    by_end.columns = ['EndID', 'AvgPoints', 'Count', 'StdDev']
    
    # Create the bar chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(by_end['EndID'], by_end['AvgPoints'], 
                   yerr=by_end['StdDev'].fillna(0),
                   capsize=5, alpha=0.7, color='steelblue', edgecolor='black')
    
    # Add labels and title
    plt.xlabel('End Number', fontsize=12, fontweight='bold')
    plt.ylabel('Average Points Scored', fontsize=12, fontweight='bold')
    plt.title('Power Play Effectiveness by End Number', fontsize=14, fontweight='bold')
    plt.xticks(range(1, 9))
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add sample size labels on bars
    for i, (end, count, avg) in enumerate(zip(by_end['EndID'], by_end['Count'], by_end['AvgPoints'])):
        plt.text(end, avg + by_end['StdDev'].iloc[i] + 0.05, 
                f'n={count}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    # Save the figure
    output_path = os.path.join(DATA_DIR, 'power_play_by_end.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nVisualization saved to: {output_path}")
    plt.close()


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Main function that runs all the analyses.
    
    This is the entry point of the script. It:
    1. Loads the data
    2. Runs all analysis functions
    3. Prints a summary of key findings
    """
    print("="*70)
    print("CSAS 2026 CURLING DATA CHALLENGE - STRATEGIC ANALYSIS")
    print("Power Play Deployment Analysis")
    print("="*70)
    
    # Step 1: Load the data
    print("\nLoading data...")
    stones, ends = load_data()
    print(f"Loaded {len(stones):,} stone records and {len(ends):,} end records")
    
    # Step 2: Calculate Traffic (house congestion)
    stones_with_traffic = calculate_traffic(stones)
    
    # Step 3: Calculate Power Play Readiness Score for early ends
    early_ends_pprs = calculate_power_play_readiness_score(stones, ends)
    
    # Step 4: Analyze Power Play deployment patterns
    pp_analysis = analyze_power_play_deployment(ends)
    
    # Step 5: Compare shot accuracy (Draws vs Wicks)
    draws, wicks = analyze_shot_accuracy(stones)
    
    # Step 6: Analyze how Traffic affects Power Play scoring
    traffic_analysis = analyze_traffic_impact(stones_with_traffic, ends)
    
    # Step 7: Compare team performance (GBR vs Italy)
    team_comparison = analyze_team_comparison(ends, stones)
    
    # Step 8: Create visualization
    create_visualization(ends)
    
    # Print final summary
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\nKey Metrics Summary:")
    print(f"  - Average Traffic: {stones_with_traffic['Traffic'].mean():.2f} stones in house")
    print(f"  - Average PPRS (Ends 1-2): {early_ends_pprs['PPRS'].mean():.2f} center corridor stones")
    print(f"  - Total Power Plays analyzed: {len(pp_analysis)}")
    print(f"  - Draw accuracy: {draws['Points'].mean():.2f}/4.0")
    print(f"  - Wick accuracy: {wicks['Points'].mean():.2f}/4.0")
    
    # Calculate execution gap
    execution_gap = draws['Points'].mean() - wicks['Points'].mean()
    execution_gap_pct = (execution_gap / wicks['Points'].mean()) * 100
    print(f"  - Execution Gap: {execution_gap:.2f} points ({execution_gap_pct:.1f}%)")


# ============================================================================
# RUN THE SCRIPT
# ============================================================================

if __name__ == "__main__":
    main()
