import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

OUTPUT_DIR = "benchmark_results/benchmark_plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)
plt.rcParams.update({'font.size': 11})

# ============================================================
# Data Loading & Aggregation
# ============================================================
def load_and_agg(path):
    df = pd.read_csv(path)
    if 'run' not in df.columns:
        df['run'] = 1
    group_cols = ['implementation', 'rows', 'cols', 'iterations', 'seed', 'threads']
    agg = df.groupby(group_cols)['time_ms'].agg(['mean', 'std', 'min', 'max']).reset_index()
    agg.columns = list(group_cols) + ['mean_ms', 'std_ms', 'min_ms', 'max_ms']
    return agg

gol = load_and_agg("benchmark_results/perf_raw/all_results.csv")
heat = load_and_agg("benchmark_results/perf_raw/heat_diffusion_results.csv")

def config_label(row):
    return f"{int(row['rows'])}x{int(row['cols'])}"

def size_key(row):
    return int(row['rows']) * int(row['cols'])

# ============================================================
# Speedup Plots
# ============================================================
def plot_speedup(stats, sequential_name, parallel_name, lang_label, title, filename):
    sizes = stats[['rows', 'cols']].drop_duplicates().sort_values(['rows', 'cols']).values
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.tab10(np.linspace(0, 1, len(sizes)))
    for (rows, cols), color in zip(sizes, colors):
        t_seq = stats[(stats['implementation'] == sequential_name) &
                      (stats['rows'] == rows) & (stats['cols'] == cols) &
                      (stats['threads'] == 1)]
        if t_seq.empty:
            continue
        t_seq_val = t_seq['mean_ms'].values[0]

        par = stats[(stats['implementation'] == parallel_name) &
                    (stats['rows'] == rows) & (stats['cols'] == cols)]
        threads = sorted(par['threads'].unique())
        speedups = []
        err = []
        for t in threads:
            row = par[par['threads'] == t]
            s = t_seq_val / row['mean_ms'].values[0]
            speedups.append(s)
            s_std = s * row['std_ms'].values[0] / row['mean_ms'].values[0]
            err.append(s_std)
        ax.errorbar(threads, speedups, yerr=err, marker='o', capsize=4,
                     color=color, label=f'{rows}x{cols}')

    max_t = int(stats['threads'].max())
    ax.plot([1, max_t], [1, max_t], 'k--', alpha=0.5, label='Ideal')
    ax.set_xlabel('Threads')
    ax.set_ylabel('Speedup')
    ax.set_title(f'{title} — {lang_label}')
    ax.set_xticks([1, 2, 4, 8])
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

# Game of Life
plot_speedup(gol, 'cpp_sequential', 'cpp_optimized', 'C++ (OpenMP)',
             'Game of Life — Total Speedup', 'speedup_gol_cpp.png')
plot_speedup(gol, 'java_sequential', 'java_optimized', 'Java (ForkJoin)',
             'Game of Life — Total Speedup', 'speedup_gol_java.png')

# Heat Diffusion
plot_speedup(heat, 'HeatDiffusion_Cpp_Serial', 'HeatDiffusion_Cpp_OMP', 'C++ (OpenMP)',
             'Heat Diffusion — Parallel Speedup', 'speedup_heat_cpp.png')
plot_speedup(heat, 'HeatDiffusion_Java_Serial', 'HeatDiffusion_Java_ForkJoin', 'Java (ForkJoin)',
             'Heat Diffusion — Parallel Speedup', 'speedup_heat_java.png')

# ============================================================
# Efficiency Plots
# ============================================================
def plot_efficiency(stats, sequential_name, parallel_name, lang_label, title, filename):
    sizes = stats[['rows', 'cols']].drop_duplicates().sort_values(['rows', 'cols']).values
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.tab10(np.linspace(0, 1, len(sizes)))
    for (rows, cols), color in zip(sizes, colors):
        t_seq = stats[(stats['implementation'] == sequential_name) &
                      (stats['rows'] == rows) & (stats['cols'] == cols) &
                      (stats['threads'] == 1)]
        if t_seq.empty:
            continue
        t_seq_val = t_seq['mean_ms'].values[0]

        par = stats[(stats['implementation'] == parallel_name) &
                    (stats['rows'] == rows) & (stats['cols'] == cols)]
        threads = sorted(par['threads'].unique())
        effs = []
        err = []
        for t in threads:
            row = par[par['threads'] == t]
            s = t_seq_val / row['mean_ms'].values[0]
            e = s / t
            effs.append(e)
            e_std = e * row['std_ms'].values[0] / row['mean_ms'].values[0]
            err.append(e_std)
        ax.errorbar(threads, effs, yerr=err, marker='o', capsize=4,
                     color=color, label=f'{rows}x{cols}')

    ax.axhline(y=1.0, color='k', linestyle='--', alpha=0.3)
    ax.set_xlabel('Threads')
    ax.set_ylabel('Parallel Efficiency')
    ax.set_title(f'{title} — {lang_label}')
    ax.set_xticks([1, 2, 4, 8])
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

plot_efficiency(gol, 'cpp_sequential', 'cpp_optimized', 'C++ (OpenMP)',
                'Game of Life — Efficiency', 'efficiency_gol_cpp.png')
plot_efficiency(gol, 'java_sequential', 'java_optimized', 'Java (ForkJoin)',
                'Game of Life — Efficiency', 'efficiency_gol_java.png')
plot_efficiency(heat, 'HeatDiffusion_Cpp_Serial', 'HeatDiffusion_Cpp_OMP', 'C++ (OpenMP)',
                'Heat Diffusion — Efficiency', 'efficiency_heat_cpp.png')
plot_efficiency(heat, 'HeatDiffusion_Java_Serial', 'HeatDiffusion_Java_ForkJoin', 'Java (ForkJoin)',
                'Heat Diffusion — Efficiency', 'efficiency_heat_java.png')

# ============================================================
# C++ vs Java Ratio
# ============================================================
def plot_ratio(stats, sequential_pair, parallel_pair, title, filename):
    configs = stats[['rows', 'cols', 'threads']].drop_duplicates().sort_values(
        ['rows', 'cols', 'threads']).values
    sizes_list = stats[['rows', 'cols']].drop_duplicates().sort_values(['rows', 'cols']).values
    n_configs = len(configs)
    fig, axes = plt.subplots(1, 2, figsize=(max(14, n_configs * 0.6), 5), sharey=True)
    grid_colors = plt.cm.tab10(np.linspace(0, 1, len(sizes_list)))
    for ax, (cpp_name, java_name, mode_label) in zip(axes, [
            (sequential_pair[0], sequential_pair[1], 'Sequential'),
            (parallel_pair[0], parallel_pair[1], 'Parallel')]):
        labels = []
        ratios = []
        errs = []
        bar_colors = []
        for rows, cols, threads in configs:
            cpp = stats[(stats['implementation'] == cpp_name) &
                        (stats['rows'] == rows) & (stats['cols'] == cols) &
                        (stats['threads'] == threads)]
            java = stats[(stats['implementation'] == java_name) &
                         (stats['rows'] == rows) & (stats['cols'] == cols) &
                         (stats['threads'] == threads)]
            if cpp.empty or java.empty or cpp['mean_ms'].values[0] == 0:
                continue
            r = java['mean_ms'].values[0] / cpp['mean_ms'].values[0]
            ratios.append(r)
            r_err = r * np.sqrt(
                (java['std_ms'].values[0] / java['mean_ms'].values[0])**2 +
                (cpp['std_ms'].values[0] / cpp['mean_ms'].values[0])**2
            )
            errs.append(r_err)
            labels.append(f"{rows}x{cols}\n{int(threads)}T")
            idx = [i for i, (r, c) in enumerate(sizes_list) if r == rows and c == cols][0]
            bar_colors.append(grid_colors[idx])

        x = np.arange(len(labels))
        ax.bar(x, ratios, yerr=errs, capsize=4, color=bar_colors, alpha=0.85)
        ax.axhline(y=1.0, color='k', linestyle='--', alpha=0.5)
        ax.set_xticks(x)
        tick_font = max(5, min(8, 8 - len(labels) // 10))
        ax.set_xticklabels(labels, fontsize=tick_font, rotation=45)
        ax.set_title(mode_label)
        ax.set_ylabel('Java Time / C++ Time')
        ax.grid(axis='y', alpha=0.3)

        for i, r in enumerate(ratios):
            ax.annotate(f'{r:.2f}x', (i, r), textcoords="offset points",
                        xytext=(0, 6), ha='center', fontsize=5,
                        color='#d62728' if r > 2 else '#2ca02c')

        sep = 0
        for (rows, cols) in sizes_list[:-1]:
            sep += len([l for l in labels if l.startswith(f'{rows}x{cols}')])
            ax.axvline(x=sep - 0.5, color='gray', linestyle=':', alpha=0.5)

        for idx, (rows, cols) in enumerate(sizes_list):
            cx = len([l for l in labels if l.startswith(f'{rows}x{cols}')]) // 2
            prev = sum(len([l for l in labels if l.startswith(f'{r}x{c}')]) for r, c in sizes_list[:idx])
            ax.text(prev + cx, ax.get_ylim()[1] * 0.95, f'{rows}x{cols}',
                    ha='center', fontsize=7, fontweight='bold', color=grid_colors[idx])

    fig.suptitle(title, fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

plot_ratio(gol,
           ('cpp_sequential', 'java_sequential'),
           ('cpp_optimized', 'java_optimized'),
           'Game of Life — C++ vs Java Performance Ratio',
           'ratio_gol.png')
plot_ratio(heat,
           ('HeatDiffusion_Cpp_Serial', 'HeatDiffusion_Java_Serial'),
           ('HeatDiffusion_Cpp_OMP', 'HeatDiffusion_Java_ForkJoin'),
           'Heat Diffusion — C++ vs Java Performance Ratio',
           'ratio_heat.png')

# ============================================================
# Throughput (Million Cells / Second)
# ============================================================
def plot_throughput(stats, title, filename):
    n_configs = len(stats[['rows', 'cols', 'threads']].drop_duplicates())
    fig, ax = plt.subplots(figsize=(max(12, n_configs * 0.8), 6))
    df = stats.copy()
    df['total_cells'] = (df['rows'] * df['cols'] * df['iterations']).astype(int)
    df['throughput'] = df['total_cells'] / (df['mean_ms'] / 1000.0) / 1e6
    df['throughput_std'] = df['throughput'] * df['std_ms'] / df['mean_ms']

    df['config'] = df.apply(lambda r: f"{int(r['rows'])}x{int(r['cols'])}\n{int(r['threads'])}T", axis=1)
    df['sort_key'] = df.apply(lambda r: (size_key(r), int(r['threads'])), axis=1)
    df = df.sort_values('sort_key')

    impls = df['implementation'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(impls)))
    x = np.arange(len(df['config'].unique()))
    width = 0.8 / len(impls)

    for idx, impl in enumerate(impls):
        impl_df = df[df['implementation'] == impl]
        offsets = x + (idx - len(impls) / 2 + 0.5) * width
        ax.bar(offsets, impl_df['throughput'].values, width, yerr=impl_df['throughput_std'].values,
               capsize=3, label=impl, color=colors[idx], alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(df['config'].unique(), fontsize=8, rotation=45)
    ax.set_ylabel('Million Cells / Second')
    ax.set_title(title)
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

plot_throughput(gol, 'Game of Life — Throughput', 'throughput_gol.png')
plot_throughput(heat, 'Heat Diffusion — Throughput', 'throughput_heat.png')

# ============================================================
# Combined Speedup (C++ and Java on same plot)
# ============================================================
def plot_speedup_combined(stats, cpp_ser, cpp_par, java_ser, java_par, title, filename):
    sizes = stats[['rows', 'cols']].drop_duplicates().sort_values(['rows', 'cols']).values
    n = len(sizes)
    ncols = 3
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows), sharey=True)
    axes = axes.flatten()
    for ax, (rows, cols) in zip(axes, sizes):
        t_cpp_seq = stats[(stats['implementation'] == cpp_ser) &
                          (stats['rows'] == rows) & (stats['cols'] == cols) &
                          (stats['threads'] == 1)]
        t_java_seq = stats[(stats['implementation'] == java_ser) &
                           (stats['rows'] == rows) & (stats['cols'] == cols) &
                           (stats['threads'] == 1)]
        if t_cpp_seq.empty or t_java_seq.empty:
            ax.set_title(f'{rows}x{cols} (no data)')
            continue
        t_cpp = t_cpp_seq['mean_ms'].values[0]
        t_java = t_java_seq['mean_ms'].values[0]

        par_cpp = stats[(stats['implementation'] == cpp_par) &
                        (stats['rows'] == rows) & (stats['cols'] == cols)]
        par_java = stats[(stats['implementation'] == java_par) &
                         (stats['rows'] == rows) & (stats['cols'] == cols)]

        threads = sorted(par_cpp['threads'].unique())
        sp_cpp = [t_cpp / par_cpp[par_cpp['threads'] == t]['mean_ms'].values[0] for t in threads]
        sp_java = [t_java / par_java[par_java['threads'] == t]['mean_ms'].values[0] for t in threads]

        ax.plot(threads, sp_cpp, 'o-', color='#2ca02c', label='C++')
        ax.plot(threads, sp_java, 's-', color='#1f77b4', label='Java')
        max_t = max(threads)
        ax.plot([1, max_t], [1, max_t], 'k--', alpha=0.4, label='Ideal')
        ax.set_xlabel('Threads')
        ax.set_title(f'{rows}x{cols}')
        ax.set_xticks([1, 2, 4, 8])
        ax.grid(alpha=0.3)
        col_idx = list(axes).index(ax) % ncols
        if col_idx == 0:
            ax.set_ylabel('Speedup')
        ax.legend(fontsize=9)

    for ax in axes[n:]:
        ax.set_visible(False)

    fig.suptitle(title, fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

plot_speedup_combined(gol, 'cpp_sequential', 'cpp_optimized',
                      'java_sequential', 'java_optimized',
                      'Game of Life — Speedup by Problem Size', 'speedup_combined_gol.png')
plot_speedup_combined(heat, 'HeatDiffusion_Cpp_Serial', 'HeatDiffusion_Cpp_OMP',
                      'HeatDiffusion_Java_Serial', 'HeatDiffusion_Java_ForkJoin',
                      'Heat Diffusion — Speedup by Problem Size', 'speedup_combined_heat.png')

print(f"Analysis plots saved to {OUTPUT_DIR}/")
print(f"  speedup_gol_cpp.png, speedup_gol_java.png, speedup_combined_gol.png")
print(f"  speedup_heat_cpp.png, speedup_heat_java.png, speedup_combined_heat.png")
print(f"  efficiency_gol_cpp.png, efficiency_gol_java.png")
print(f"  efficiency_heat_cpp.png, efficiency_heat_java.png")
print(f"  ratio_gol.png, ratio_heat.png")
print(f"  throughput_gol.png, throughput_heat.png")
