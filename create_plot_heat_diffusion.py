import pandas as pd
import matplotlib.pyplot as plt
import os

# Path to the specific Heat Diffusion benchmark results
Path = "benchmark_results/perf_raw/heat_diffusion_results.csv"
output_path = "benchmark_results/benchmark_plots"
df = pd.read_csv(Path)

# Pivot the data to group by configuration and compare Java vs C++ implementations
pivot_df = df.pivot_table(
    index=['rows', 'cols', 'threads'], 
    columns='implementation', 
    values='time_ms', 
    aggfunc='mean'
)

# Define a color map to distinguish between Language and Parallelism
# Java: Blue tones, C++: Green tones
# Parallel: Darker, Serial: Lighter
color_map = {
    'HeatDiffusion_Java_ForkJoin': '#1f77b4',  # Dark Blue
    'HeatDiffusion_Java_Serial': '#aec7e8',    # Light Blue
    'HeatDiffusion_Cpp_OMP': '#2ca02c',        # Dark Green
    'HeatDiffusion_Cpp_Serial': '#98df8a'      # Light Green
}

# Get colors in the order of the pivot table columns
colors = [color_map.get(col, '#333333') for col in pivot_df.columns]

# Generate the bar chart
plot = pivot_df.plot(kind='bar', figsize=(10, 6), rot=45, color=colors)
plt.title('Heat Diffusion: Serial vs Parallel (Java & C++)')
plt.ylabel('Execution Time (ms)')
plt.xlabel('Configuration (Rows, Cols, Threads)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(title='Implementation')
plt.tight_layout()

# Save the plot as a separate file to avoid overwriting Game of Life results
file_path = os.path.join(output_path, 'heat_diffusion_performance.png')
plt.savefig(file_path, bbox_inches='tight', dpi=300)