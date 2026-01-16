"""
Create graph showing average points scored by end
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"
ends = pd.read_csv(os.path.join(DATA_DIR, "Ends.csv"))

# Get Power Play ends
pp = ends[ends['PowerPlay'].notna() & (ends['PowerPlay'] > 0)].copy()

# Calculate averages by end
end_avgs = []
end_counts = []
end_nums = []

for end in range(1, 9):
    end_data = pp[pp['EndID'] == end]
    if len(end_data) > 0:
        avg = end_data['Result'].mean()
        end_avgs.append(avg)
        end_counts.append(len(end_data))
        end_nums.append(end)
    else:
        end_avgs.append(0)
        end_counts.append(0)
        end_nums.append(end)

# Create figure
fig, ax = plt.subplots(figsize=(9, 6))

# Make bars
colors = ['#4472C4' if count > 0 else '#CCCCCC' for count in end_counts]
bars = ax.bar(end_nums, end_avgs, color=colors, edgecolor='black', linewidth=1.0)

# Labels
ax.set_xlabel('End Number', fontsize=11)
ax.set_ylabel('Average Points Scored', fontsize=11)
ax.set_title('Power Play Average Points by End Number', fontsize=12, fontweight='bold')
ax.set_xticks(range(1, 9))

# Grid
ax.grid(axis='y', alpha=0.3)

# Add value labels on bars
for i, (bar, avg, count) in enumerate(zip(bars, end_avgs, end_counts)):
    if count > 0:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{avg:.2f}\n(n={count})',
                ha='center', va='bottom', fontsize=8)
    else:
        ax.text(bar.get_x() + bar.get_width()/2., 0.1,
                'n=0',
                ha='center', va='bottom', fontsize=8, style='italic')

plt.tight_layout()

# Save
output_path = os.path.join(DATA_DIR, 'submission_files', 'power_play_avg_points.png')
plt.savefig(output_path, dpi=200, bbox_inches='tight')
print(f"Graph saved to: {output_path}")
plt.close()
