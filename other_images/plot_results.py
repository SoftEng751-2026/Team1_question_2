import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_results():
    if not os.path.exists('results.csv'):
        print("Error: results.csv not found.")
        return

    df = pd.read_csv('results.csv')
    
    # Create figure with two subplots: one for CPP, one for Java
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

    languages = ['CPP', 'Java']
    axes = [ax1, ax2]

    for lang, ax in zip(languages, axes):
        lang_df = df[df['Language'] == lang]
        for layout in ['1D', '2D']:
            data = lang_df[lang_df['Type'] == layout]
            ax.plot(data['Size'], data['Time'], marker='o', label=f'{layout} Layout')
        
        ax.set_title(f'{lang} Performance Comparison')
        ax.set_xlabel('Grid Size (N x N)')
        ax.set_ylabel('Execution Time (ms)')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    output_file = 'benchmark_comparison.png'
    plt.savefig(output_file)
    print(f"Plot saved as {output_file}")
    plt.show()

if __name__ == "__main__":
    # Required libraries: pandas, matplotlib
    plot_results()