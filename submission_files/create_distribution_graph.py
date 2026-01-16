"""
Create Power Play distribution graph
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"
ends = pd.read_csv(os.path.join(DATA_DIR, "Ends.csv"))

# Get Power Play ends
pp = ends[ends['PowerPlay'].notna() & (ends['PowerPlay'] > 0)].copy()

# Count by end
end_counts = []
for end in range(1, 9):
    count = len(pp[pp['EndID'] == end])
    end_counts.append(count)

# Create figure
fig, ax = plt.subplots(figsize=(9, 6))

# Make bars - simple blue color
bars = ax.bar(range(1, 9), end_counts, color='#4472C4', edgecolor='black', linewidth=1.0)

# Labels
ax.set_xlabel('End Number', fontsize=11)
ax.set_ylabel('Number of Power Plays', fontsize=11)
ax.set_title('Power Play Deployment Distribution by End', fontsize=12, fontweight='bold')
ax.set_xticks(range(1, 9))

# Grid
ax.grid(axis='y', alpha=0.3)

# Add value labels
for i, (bar, count) in enumerate(zip(bars, end_counts)):
    if count > 0:
        height = bar.get_height()
        pct = (count / len(pp)) * 100
        ax.text(bar.get_x() + bar.get_width()/2., height + 3,
                f'{count}\n({pct:.1f}%)',
                ha='center', va='bottom', fontsize=8)

plt.tight_layout()

# Save
output_path = os.path.join(DATA_DIR, 'submission_files', 'power_play_distribution.png')
plt.savefig(output_path, dpi=200, bbox_inches='tight')
print(f"Graph saved to: {output_path}")
plt.close()
