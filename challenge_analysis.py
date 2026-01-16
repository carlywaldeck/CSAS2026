"""
CSAS 2026 Curling Data Challenge - Strategic Analysis
Elite Mixed Doubles Analytics: Power Play Optimization

This script calculates key metrics for power play strategy:
1. Chaos State Index (CSI) - Stones in house at each shot
2. Power Play Readiness Score (PPRS) - Center corridor congestion
3. First Strike Validation - Early vs Late power play effectiveness
4. Shot Accuracy - Draw vs Wick execution comparison
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Constants from challenge description
BUTTON_X = 750
BUTTON_Y = 800
HOUSE_RADIUS = 600  # Distance threshold for "in house"
CENTER_CORRIDOR_WIDTH = 200  # |X - 750| < 200
CENTER_LINE_X = 750
SENTINEL_VALUE = 4095  # Stones knocked off sheet
NOT_THROWN = 0  # Stones not yet thrown

DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"


def load_data():
    """Load Stones.csv and Ends.csv from the data directory."""
    stones = pd.read_csv(os.path.join(DATA_DIR, "Stones.csv"))
    ends = pd.read_csv(os.path.join(DATA_DIR, "Ends.csv"))
    return stones, ends


def calculate_distance_to_button(x, y):
    """Calculate Euclidean distance from stone position to button (750, 800)."""
    return np.sqrt((x - BUTTON_X)**2 + (y - BUTTON_Y)**2)


def calculate_chaos_state_index(stones_df):
    """
    Calculate Traffic: Number of stones in house at each shot.
    
    Previously called "Chaos State Index" but renamed to "Traffic" to align
    with the baseball analogy (traffic on the bases).
    
    A stone is 'in the house' if its distance to the button (750, 800) <= 600 units.
    Only counts stones that are in play (not sentinel value 4095, not 0/not thrown).
    
    Returns:
        DataFrame with Traffic column added (also kept as CSI/HTI for compatibility)
    """
    print("\n" + "="*70)
    print("1. TRAFFIC CALCULATION")
    print("="*70)
    
    # Create a copy to avoid modifying original
    stones = stones_df.copy()
    
    # Get all stone positions (stones 1-12, both x and y)
    stone_cols_x = [f'stone_{i}_x' for i in range(1, 13)]
    stone_cols_y = [f'stone_{i}_y' for i in range(1, 13)]
    
    csi_values = []
    
    for idx, row in stones.iterrows():
        stones_in_house = 0
        
        # Check each stone position
        for i in range(1, 13):
            x_col = f'stone_{i}_x'
            y_col = f'stone_{i}_y'
            
            x_val = row[x_col]
            y_val = row[y_col]
            
            # Skip if stone not thrown (0) or knocked off sheet (4095)
            if pd.isna(x_val) or pd.isna(y_val) or x_val == NOT_THROWN or y_val == NOT_THROWN:
                continue
            if x_val == SENTINEL_VALUE or y_val == SENTINEL_VALUE:
                continue
            
            # Calculate distance to button
            distance = calculate_distance_to_button(x_val, y_val)
            
            if distance <= HOUSE_RADIUS:
                stones_in_house += 1
        
        csi_values.append(stones_in_house)
    
    stones['CSI'] = csi_values
    stones['HTI'] = csi_values  # Keep for compatibility
    stones['Traffic'] = csi_values  # Primary metric name
    
    # Summary statistics
    summary = stones.groupby(['CompetitionID', 'SessionID', 'GameID', 'EndID'])['Traffic'].agg([
        'mean', 'max', 'std'
    ]).reset_index()
    
    print(f"\nTotal shots analyzed: {len(stones):,}")
    print(f"Average Traffic (stones in house per shot): {stones['Traffic'].mean():.2f}")
    print(f"Maximum Traffic (most congested state): {stones['Traffic'].max()}")
    print(f"Standard deviation: {stones['Traffic'].std():.2f}")
    
    print("\nTraffic Statistics by End:")
    print(stones.groupby('EndID')['Traffic'].agg(['mean', 'max']).round(2))
    
    return stones


def calculate_power_play_readiness_score(stones_df, ends_df):
    """
    Calculate Power Play Readiness Score (PPRS): Center corridor congestion.
    
    For the first two ends, counts stones in the "Center Corridor" defined as |X - 750| < 200.
    This measures how clogged the center is early in the game, which affects power play viability.
    
    Returns:
        DataFrame with PPRS column added for ends 1-2
    """
    print("\n" + "="*70)
    print("2. POWER PLAY READINESS SCORE (PPRS) CALCULATION")
    print("="*70)
    
    stones = stones_df.copy()
    
    # Filter to first two ends only
    early_ends = stones[stones['EndID'].isin([1, 2])].copy()
    
    # Get all stone positions
    pprs_values = []
    
    for idx, row in early_ends.iterrows():
        center_stones = 0
        
        # Check each stone position
        for i in range(1, 13):
            x_col = f'stone_{i}_x'
            y_col = f'stone_{i}_y'
            
            x_val = row[x_col]
            y_val = row[y_col]
            
            # Skip if stone not thrown or knocked off sheet
            if pd.isna(x_val) or pd.isna(y_val) or x_val == NOT_THROWN or y_val == NOT_THROWN:
                continue
            if x_val == SENTINEL_VALUE or y_val == SENTINEL_VALUE:
                continue
            
            # Check if in center corridor: |X - 750| < 200
            if abs(x_val - CENTER_LINE_X) < CENTER_CORRIDOR_WIDTH:
                center_stones += 1
        
        pprs_values.append(center_stones)
    
    early_ends['PPRS'] = pprs_values
    
    print(f"\nTotal shots in Ends 1-2: {len(early_ends):,}")
    print(f"Average PPRS (center corridor stones): {early_ends['PPRS'].mean():.2f}")
    print(f"Maximum PPRS: {early_ends['PPRS'].max()}")
    
    print("\nPPRS by End:")
    print(early_ends.groupby('EndID')['PPRS'].agg(['mean', 'max']).round(2))
    
    return early_ends


def first_strike_validation(ends_df):
    """
    Power Play Deployment Analysis: Compare power play distribution and effectiveness.
    
    Groups by EndID and PowerPlay flag, calculating:
    - Average Points Scored
    - 'Big End' rate (ends where Result >= 3)
    - Deployment distribution
    
    Analyzes Power Play timing across all ends.
    
    Returns:
        Summary statistics and distribution table
    """
    print("\n" + "="*70)
    print("3. POWER PLAY DEPLOYMENT ANALYSIS - Timing Distribution")
    print("="*70)
    
    # Filter to power play ends only
    pp_ends = ends_df[ends_df['PowerPlay'].notna() & (ends_df['PowerPlay'] > 0)].copy()
    
    # Overall PP statistics
    print(f"\nTotal Power Play Ends: {len(pp_ends)}")
    print(f"Overall Average Points: {pp_ends['Result'].mean():.2f}")
    print(f"Overall Big End Rate (3+ pts): {(pp_ends['Result'] >= 3).sum() / len(pp_ends) * 100:.1f}%")
    
    # Distribution by end
    print("\n" + "-" * 70)
    print("DEPLOYMENT DISTRIBUTION BY END:")
    print("-" * 70)
    end_dist = pp_ends.groupby('EndID').agg({
        'Result': ['count', 'mean'],
    }).round(2)
    end_dist.columns = ['Count', 'AvgPoints']
    end_dist['Percentage'] = (end_dist['Count'] / len(pp_ends) * 100).round(1)
    print(end_dist)
    
    # Categorize ends
    pp_ends['EndCategory'] = pp_ends['EndID'].apply(
        lambda x: 'Early (1-2)' if x <= 2 else ('Late (7-8)' if x >= 7 else 'Middle (3-6)')
    )
    
    # Calculate metrics by category
    summary = pp_ends.groupby('EndCategory').agg({
        'Result': ['mean', 'count'],
    }).round(2)
    
    # Calculate Big End rate (Result >= 3)
    big_end_rates = pp_ends.groupby('EndCategory').apply(
        lambda x: (x['Result'] >= 3).sum() / len(x) * 100
    ).round(2)
    
    print("\n" + "-" * 70)
    print("PERFORMANCE BY CATEGORY:")
    print("-" * 70)
    print("\nAverage Points Scored:")
    print(summary[('Result', 'mean')])
    print("\nNumber of Power Plays:")
    print(summary[('Result', 'count')])
    print("\nBig End Rate (% with Result >= 3):")
    print(big_end_rates)
    
    # Check for early PPs (the scarcity fact)
    early = pp_ends[pp_ends['EndCategory'] == 'Early (1-2)']
    print("\n" + "-" * 70)
    print("EARLY POWER PLAY ANALYSIS (Ends 1-2):")
    print("-" * 70)
    print(f"Count: {len(early)}")
    if len(early) > 0:
        print(f"Average Points: {early['Result'].mean():.2f}")
        print(f"Percentage of Total PPs: {len(early) / len(pp_ends) * 100:.2f}%")
    else:
        print("No early power plays found in dataset.")
    
    return pp_ends


def shot_accuracy_analysis(stones_df):
    """
    Shot Accuracy: Compare execution quality between Draws and Wicks.
    
    Task 0 = Draw
    Task 4 = Wick/Soft Peeling
    
    Calculates average 'Points' (execution score 0-4) for each shot type.
    
    Returns:
        Comparison statistics
    """
    print("\n" + "="*70)
    print("4. SHOT ACCURACY ANALYSIS - Draw vs Wick")
    print("="*70)
    
    # Filter to Draws (Task 0) and Wicks (Task 4)
    draws = stones_df[stones_df['Task'] == 0].copy()
    wicks = stones_df[stones_df['Task'] == 4].copy()
    
    draw_avg = draws['Points'].mean()
    wick_avg = wicks['Points'].mean()
    
    print(f"\nDraws (Task 0):")
    print(f"  Total shots: {len(draws):,}")
    print(f"  Average execution score: {draw_avg:.2f}")
    print(f"  Standard deviation: {draws['Points'].std():.2f}")
    
    print(f"\nWicks/Ticks (Task 4):")
    print(f"  Total shots: {len(wicks):,}")
    print(f"  Average execution score: {wick_avg:.2f}")
    print(f"  Standard deviation: {wicks['Points'].std():.2f}")
    
    if len(draws) > 0 and len(wicks) > 0:
        diff = draw_avg - wick_avg
        pct_diff = (diff / wick_avg) * 100 if wick_avg > 0 else 0
        print(f"\nDifference (Draw - Wick): {diff:+.2f} points")
        print(f"Percentage difference: {pct_diff:+.1f}%")
        
        # Statistical comparison (using basic calculations)
        draw_points = draws['Points'].dropna()
        wick_points = wicks['Points'].dropna()
        if len(draw_points) > 1 and len(wick_points) > 1:
            print(f"\nComparison:")
            print(f"  Draws range: {draw_points.min():.0f}-{draw_points.max():.0f}")
            print(f"  Wicks range: {wick_points.min():.0f}-{wick_points.max():.0f}")
            print(f"  Execution advantage (Draw): {pct_diff:+.1f}%")
    
    return draws, wicks


def calculate_ev_comparison(ends_df):
    """
    Calculate Expected Value (EV) comparison: End 1 PP vs End 8 PP.
    
    Returns:
        Dictionary with EV metrics for End 1 and End 8 power plays
    """
    print("\n" + "="*70)
    print("EXPECTED VALUE (EV) COMPARISON: End 1 vs End 8 Power Play")
    print("="*70)
    
    pp_ends = ends_df[ends_df['PowerPlay'].notna() & (ends_df['PowerPlay'] > 0)].copy()
    
    # Filter to End 1 and End 8 specifically
    end_1_pp = pp_ends[pp_ends['EndID'] == 1]
    end_8_pp = pp_ends[pp_ends['EndID'] == 8]
    
    # Also get standard (non-PP) ends for baseline comparison
    standard_end_1 = ends_df[(ends_df['EndID'] == 1) & (ends_df['PowerPlay'].isna() | (ends_df['PowerPlay'] == 0))]
    standard_end_8 = ends_df[(ends_df['EndID'] == 8) & (ends_df['PowerPlay'].isna() | (ends_df['PowerPlay'] == 0))]
    
    # Calculate EVs
    ev_end_1_pp = end_1_pp['Result'].mean() if len(end_1_pp) > 0 else 0
    ev_end_8_pp = end_8_pp['Result'].mean() if len(end_8_pp) > 0 else 0
    ev_standard_1 = standard_end_1['Result'].mean() if len(standard_end_1) > 0 else 0
    ev_standard_8 = standard_end_8['Result'].mean() if len(standard_end_8) > 0 else 0
    
    leverage_end_1 = ev_end_1_pp - ev_standard_1
    leverage_end_8 = ev_end_8_pp - ev_standard_8
    
    print(f"\nEnd 1 Power Play:")
    print(f"  Sample size: {len(end_1_pp)}")
    print(f"  PP EV: {ev_end_1_pp:.2f} points")
    print(f"  Standard End 1 EV: {ev_standard_1:.2f} points")
    print(f"  Leverage (PP - Standard): {leverage_end_1:+.2f} points")
    
    print(f"\nEnd 8 Power Play:")
    print(f"  Sample size: {len(end_8_pp)}")
    print(f"  PP EV: {ev_end_8_pp:.2f} points")
    print(f"  Standard End 8 EV: {ev_standard_8:.2f} points")
    print(f"  Leverage (PP - Standard): {leverage_end_8:+.2f} points")
    
    if ev_end_1_pp > 0 and ev_end_8_pp > 0:
        diff = ev_end_1_pp - ev_end_8_pp
        print(f"\nEV Difference (End 1 PP - End 8 PP): {diff:+.2f} points")
        print(f"Leverage Difference (End 1 - End 8): {leverage_end_1 - leverage_end_8:+.2f} points")
    
    return {
        'end_1_pp': ev_end_1_pp,
        'end_8_pp': ev_end_8_pp,
        'leverage_1': leverage_end_1,
        'leverage_8': leverage_end_8,
        'n_end_1': len(end_1_pp),
        'n_end_8': len(end_8_pp)
    }


def calculate_csi_big_end_relationship(stones_with_csi, ends_df):
    """
    Analyze the relationship between Traffic and Power Play scoring efficiency.
    
    This function tests whether high traffic helps or hurts Power Play scoring.
    Reports the "Traffic Tax" - the efficiency penalty from congestion.
    
    Args:
        stones_with_csi: DataFrame with Traffic/CSI/HTI already calculated
    
    Returns:
        Statistics showing relationship between Traffic and scoring efficiency
    """
    print("\n" + "="*70)
    print("TRAFFIC vs POWER PLAY SCORING EFFICIENCY")
    print("="*70)
    
    # Merge with ends to get results
    stones_merged = pd.merge(
        stones_with_csi,
        ends_df[['CompetitionID', 'SessionID', 'GameID', 'EndID', 'Result', 'PowerPlay']],
        on=['CompetitionID', 'SessionID', 'GameID', 'EndID'],
        how='inner'
    )
    
    # Filter to power play ends only
    pp_stones = stones_merged[stones_merged['PowerPlay'].notna() & (stones_merged['PowerPlay'] > 0)].copy()
    
    # Use Traffic if available, otherwise fall back to HTI or CSI
    traffic_col = 'Traffic' if 'Traffic' in pp_stones.columns else ('HTI' if 'HTI' in pp_stones.columns else 'CSI')
    
    # Categorize by Traffic levels (low, medium, high)
    pp_stones['Traffic_Category'] = pd.cut(
        pp_stones[traffic_col],
        bins=[-1, 2, 4, 20],
        labels=['Low Traffic (0-2)', 'Medium Traffic (3-4)', 'High Traffic (5+)']
    )
    
    # Calculate average points by Traffic category
    scoring_by_traffic = pp_stones.groupby('Traffic_Category').agg({
        'Result': ['mean', 'count'],
    }).round(2)
    
    # Calculate Big End probability (Result >= 3)
    big_end_prob = pp_stones.groupby('Traffic_Category').apply(
        lambda x: (x['Result'] >= 3).sum() / len(x) * 100
    ).round(2)
    
    print("\nScoring Efficiency by Traffic Level:")
    print("-" * 70)
    print(f"Total PP shots analyzed: {len(pp_stones):,}")
    print("\nAverage Points Scored by Traffic:")
    print(scoring_by_traffic[('Result', 'mean')])
    print("\nSample Size by Traffic:")
    print(scoring_by_traffic[('Result', 'count')])
    print("\nBig End Rate (% with Result >= 3) by Traffic:")
    print(big_end_prob)
    
    # Calculate Traffic Tax (efficiency change from low to high Traffic)
    low_traffic = pp_stones[pp_stones['Traffic_Category'] == 'Low Traffic (0-2)']
    high_traffic = pp_stones[pp_stones['Traffic_Category'] == 'High Traffic (5+)']
    
    if len(low_traffic) > 0 and len(high_traffic) > 0:
        avg_low = low_traffic['Result'].mean()
        avg_high = high_traffic['Result'].mean()
        traffic_tax = ((avg_high - avg_low) / avg_low) * 100 if avg_low > 0 else 0
        
        print(f"\n" + "-" * 70)
        print(f"TRAFFIC TAX ANALYSIS:")
        print(f"Low Traffic (0-2 stones): {avg_low:.2f} points")
        print(f"High Traffic (5+ stones): {avg_high:.2f} points")
        print(f"Traffic Tax: {traffic_tax:+.1f}%")
        
        if traffic_tax < 0:
            print(f"\nFINDING: High traffic REDUCES scoring efficiency by {abs(traffic_tax):.1f}%")
            print(f"This quantifies the geometric penalty of house congestion.")
        else:
            print(f"\nFINDING: High traffic INCREASES scoring efficiency by {traffic_tax:.1f}%")
    
    return pp_stones


def calculate_high_congestion_failure_rates(stones_with_csi):
    """
    Identify failure rate of Task 0 (Draws) vs Task 4 (Wicks) in high-congestion scenarios.
    
    Args:
        stones_with_csi: DataFrame with CSI already calculated
    
    Uses CSI to define high-congestion (CSI >= 5).
    
    Returns:
        Failure rate statistics for both shot types
    """
    print("\n" + "="*70)
    print("FAILURE RATE ANALYSIS: Draws vs Wicks in High Congestion")
    print("="*70)
    
    # Filter to high congestion (CSI >= 5)
    high_congestion = stones_with_csi[stones_with_csi['CSI'] >= 5].copy()
    
    # Get Draws (Task 0) and Wicks (Task 4) in high congestion
    draws_high = high_congestion[high_congestion['Task'] == 0]
    wicks_high = high_congestion[high_congestion['Task'] == 4]
    
    # Failure rate = shots with Points == 0 (or very low, < 1)
    draw_failure_rate = (draws_high['Points'] < 1).sum() / len(draws_high) * 100 if len(draws_high) > 0 else 0
    wick_failure_rate = (wicks_high['Points'] < 1).sum() / len(wicks_high) * 100 if len(wicks_high) > 0 else 0
    
    print(f"\nHigh Congestion Scenarios (CSI >= 5):")
    print(f"  Total shots: {len(high_congestion):,}")
    print(f"  Draws (Task 0): {len(draws_high):,}")
    print(f"  Wicks (Task 4): {len(wicks_high):,}")
    
    print(f"\nFailure Rates (Points < 1):")
    print(f"  Draws failure rate: {draw_failure_rate:.1f}%")
    print(f"  Wicks failure rate: {wick_failure_rate:.1f}%")
    
    if len(draws_high) > 0 and len(wicks_high) > 0:
        print(f"\nAverage Execution Score (0-4 scale):")
        print(f"  Draws: {draws_high['Points'].mean():.2f}")
        print(f"  Wicks: {wicks_high['Points'].mean():.2f}")
        print(f"  Difference: {draws_high['Points'].mean() - wicks_high['Points'].mean():+.2f}")
    
    return {
        'draw_failure_rate': draw_failure_rate,
        'wick_failure_rate': wick_failure_rate,
        'n_draws': len(draws_high),
        'n_wicks': len(wicks_high)
    }


def visualize_power_play_success_by_end(ends_df):
    """
    Create visualization of Power Play success by end number.
    
    Shows average points scored on power plays for each end (1-8).
    """
    print("\n" + "="*70)
    print("5. VISUALIZATION: Power Play Success by End")
    print("="*70)
    
    # Filter to power play ends
    pp_ends = ends_df[ends_df['PowerPlay'].notna() & (ends_df['PowerPlay'] > 0)].copy()
    
    # Group by end
    by_end = pp_ends.groupby('EndID').agg({
        'Result': ['mean', 'count', 'std']
    }).reset_index()
    by_end.columns = ['EndID', 'AvgPoints', 'Count', 'StdDev']
    
    # Create visualization
    plt.figure(figsize=(10, 6))
    bars = plt.bar(by_end['EndID'], by_end['AvgPoints'], 
                   yerr=by_end['StdDev'].fillna(0),
                   capsize=5, alpha=0.7, color='steelblue', edgecolor='black')
    
    plt.xlabel('End Number', fontsize=12, fontweight='bold')
    plt.ylabel('Average Points Scored', fontsize=12, fontweight='bold')
    plt.title('Power Play Effectiveness by End Number', fontsize=14, fontweight='bold')
    plt.xticks(range(1, 9))
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add count labels on bars
    for i, (end, count, avg) in enumerate(zip(by_end['EndID'], by_end['Count'], by_end['AvgPoints'])):
        plt.text(end, avg + by_end['StdDev'].iloc[i] + 0.05, 
                f'n={count}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    output_path = os.path.join(DATA_DIR, 'power_play_by_end.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nVisualization saved to: {output_path}")
    plt.close()


def main():
    """Main execution function."""
    print("="*70)
    print("CSAS 2026 CURLING DATA CHALLENGE - STRATEGIC ANALYSIS")
    print("Elite Mixed Doubles Analytics")
    print("="*70)
    
    # Load data
    print("\nLoading data...")
    stones, ends = load_data()
    print(f"Loaded {len(stones):,} stone records and {len(ends):,} end records")
    
    # Run all analyses
    stones_with_csi = calculate_chaos_state_index(stones)
    early_ends_pprs = calculate_power_play_readiness_score(stones, ends)
    pp_validation = first_strike_validation(ends)
    draws, wicks = shot_accuracy_analysis(stones)
    ev_comparison = calculate_ev_comparison(ends)
    csi_big_end = calculate_csi_big_end_relationship(stones_with_csi, ends)
    failure_rates = calculate_high_congestion_failure_rates(stones_with_csi)
    visualize_power_play_success_by_end(ends)
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\nKey Metrics Summary:")
    traffic_col = 'Traffic' if 'Traffic' in stones_with_csi.columns else ('HTI' if 'HTI' in stones_with_csi.columns else 'CSI')
    print(f"  - Average Traffic: {stones_with_csi[traffic_col].mean():.2f} stones in house")
    print(f"  - Average PPRS (Ends 1-2): {early_ends_pprs['PPRS'].mean():.2f} center corridor stones")
    print(f"  - Total Power Plays analyzed: {len(pp_validation)}")
    print(f"  - Draw accuracy: {draws['Points'].mean():.2f}/4.0")
    print(f"  - Wick accuracy: {wicks['Points'].mean():.2f}/4.0")
    print(f"  - Execution gap: {draws['Points'].mean() - wicks['Points'].mean():.2f} points ({((draws['Points'].mean() - wicks['Points'].mean()) / wicks['Points'].mean() * 100):.1f}%)")


if __name__ == "__main__":
    main()
