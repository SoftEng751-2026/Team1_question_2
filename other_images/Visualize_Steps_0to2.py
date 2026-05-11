import numpy as np
import matplotlib.pyplot as plt
import os

output_path = "output"

def visualize_first_steps():
    # Parameter settings
    size = 5
    alpha = 0.1
    steps = 2
    
    # Initialize grid
    grid = np.zeros((size, size))
    grid[size // 2, size // 2] = 100.0
    
    # Record history of each step
    history = [grid.copy()]
    
    # Calculate iterations (using periodic boundaries)
    for t in range(steps):
        prev = history[-1]
        next_grid = np.zeros_like(prev)
        for i in range(size):
            for j in range(size):
                up = prev[(i - 1) % size, j]
                down = prev[(i + 1) % size, j]
                left = prev[i, (j - 1) % size]
                right = prev[i, (j + 1) % size]
                
                # 5-point Stencil formula
                delta = up + down + left + right - 4 * prev[i, j]
                next_grid[i, j] = prev[i, j] + alpha * delta
        history.append(next_grid)

    # Plotting
    fig, axes = plt.subplots(1, 3, figsize=(20, 5))
    fig.suptitle(f"Heat Diffusion: First {steps} Steps (Alpha={alpha})", fontsize=16, fontweight='bold')

    for t, ax in enumerate(axes):
        data = history[t]
        # Display using heatmap, fixed scale 0-100
        im = ax.imshow(data, cmap='YlOrRd', vmin=0, vmax=100)
        ax.set_title(f"Iteration {t}")
        
        # Display values on each cell
        for i in range(size):
            for j in range(size):
                val = data[i, j]
                color = "white" if val > 50 else "black"
                ax.text(j, i, f"{val:.1f}", ha='center', va='center', color=color, fontsize=10)

        # Set axes
        ax.set_xticks(np.arange(size))
        ax.set_yticks(np.arange(size))
        ax.set_xticklabels([f"j={k}" for k in range(size)])
        ax.set_yticklabels([f"i={k}" for k in range(size)])

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    output_file = os.path.join(output_path, "heat_diffusion_first_steps.png")
    plt.savefig(output_file, dpi=300)
    print(f"Visualization saved as {output_file}")
    plt.show()

if __name__ == "__main__":
    visualize_first_steps()