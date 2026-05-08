import pandas as pd
import matplotlib.pyplot as plt
import os

Path = "benchmark_results/perf_raw/all_results.csv"
output_path = "benchmark_results/benchmark_plots"
df = pd.read_csv(Path)


pivot_df = df.pivot_table(
    index=['rows', 'cols', 'threads'], 
    columns='implementation', 
    values='time_ms', 
    aggfunc='mean'
)


plot = pivot_df.plot(kind='bar', figsize=(10, 6), rot=45)
plt.title('Most Recent Performance Comparison: Java vs C++')
plt.ylabel('Time (ms)')
plt.xlabel('Configuration (Rows, Cols, Threads)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(title='Implementation')
plt.tight_layout()

file_path = os.path.join(output_path, 'most_recent.png')
plt.savefig(file_path, bbox_inches='tight', dpi=300)