import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
import numpy as np
import os

def create_boundary_comparison_plot():
    """
    Visualizes the differences in 5-point stencil calculations for 
    Fixed, Periodic, and Reflective boundary conditions.
    """
    output_path = "output"
    os.makedirs(output_path, exist_ok=True)

    rows, cols = 4, 4
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    titles = ["Fixed (Dirichlet)", "Periodic (Toroidal)", "Reflective (Neumann)"]

    for idx, ax in enumerate(axes):
        # In Dirichlet, the boundary (0 and 3) doesn't move. Target must be interior.
        # In others, we target the edge to show the wrap/reflect logic.
        target_r, target_c = (1, 2) if idx == 0 else (0, 2)

        # Draw main grid
        ax.set_xlim(-1.5, cols + 0.5)
        ax.set_ylim(rows + 0.5, -1.5)
        ax.set_aspect('equal')
        ax.set_title(titles[idx], fontsize=14, fontweight='bold', pad=20)

        # Draw internal grid lines
        for r in range(rows + 1):
            ax.axhline(r - 0.5, color='gray', lw=1, alpha=0.3)
        for c in range(cols + 1):
            ax.axvline(c - 0.5, color='gray', lw=1, alpha=0.3)

        # Mark the actual Grid Range with a thick border
        domain_border = patches.Rectangle((-0.5, -0.5), cols, rows, linewidth=2.5, 
                                          edgecolor='black', facecolor='none', zorder=5)
        ax.add_patch(domain_border)

        # For Dirichlet, shade the non-calculating boundary rows/cols
        if idx == 0:
            for r in range(rows):
                for c in range(cols):
                    if r == 0 or r == rows-1 or c == 0 or c == cols-1:
                        ax.add_patch(patches.Rectangle((c - 0.5, r - 0.5), 1, 1, 
                                                       color='lightgray', alpha=0.5, zorder=2))
            ax.text(cols//2, -1.0, "Boundary Rows/Cols are Fixed", ha='center', color='red', fontsize=9)

        # Highlight the Target Cell
        ax.add_patch(patches.Rectangle((target_c - 0.5, target_r - 0.5), 1, 1, 
                                       color='yellow', alpha=0.8, label='Target Cell'))
        ax.text(target_c, target_r, "T", ha='center', va='center', fontweight='bold')

        # Neighbor Logic
        # Neighbors: (Up, Down, Left, Right)
        raw_neighbors = [(target_r - 1, target_c), (target_r + 1, target_c), 
                         (target_r, target_c - 1), (target_r, target_c + 1)]
        
        resolved_neighbors = []
        ghost_cells = []

        for r, c in raw_neighbors:
            is_out = r < 0 or r >= rows or c < 0 or c >= cols
            
            if titles[idx].startswith("Fixed"):
                # Neighbors are always inside the grid or the immediate fixed boundary
                color = 'red' if (r == 0 or r == rows-1 or c == 0 or c == cols-1) else 'green'
                resolved_neighbors.append((r, c, color))
            
            elif titles[idx].startswith("Periodic"):
                rr, cc = r % rows, c % cols
                if is_out:
                    ghost_cells.append((r, c, f"({rr},{cc})"))
                    resolved_neighbors.append((rr, cc, 'blue'))
                    # Draw wrap-around arrow
                    ax.annotate("", xy=(target_c, target_r), xytext=(cc, rr),
                                arrowprops=dict(arrowstyle="->", color="blue", lw=1.5, alpha=0.6, connectionstyle="arc3,rad=-0.3"))
                else:
                    resolved_neighbors.append((r, c, 'green'))

            elif titles[idx].startswith("Reflective"):
                if is_out:
                    # Mirroring logic: if out of bounds, read from itself or nearest neighbor
                    rr, cc = max(0, min(rows-1, r)), max(0, min(cols-1, c))
                    resolved_neighbors.append((rr, cc, 'purple'))
                    ax.annotate("", xy=(target_c, target_r), xytext=(cc, rr),
                                arrowprops=dict(arrowstyle="->", color="purple", lw=2, alpha=0.6))
                else:
                    resolved_neighbors.append((r, c, 'green'))

        # Draw Neighbors
        for r, c, color in resolved_neighbors:
            ax.add_patch(patches.Circle((c, r), 0.2, color=color, alpha=0.6))
        
        # Draw Ghost Cells (conceptual area outside grid)
        for r, c, label in ghost_cells:
            ax.add_patch(patches.Rectangle((c - 0.5, r - 0.5), 1, 1, 
                                           fill=False, linestyle='--', edgecolor='gray'))
            ax.text(c, r, label, ha='center', va='center', fontsize=8, color='gray')

        # Clean up axes
        ax.set_xticks(range(cols))
        ax.set_yticks(range(rows))
        if idx == 0:
            # Legend only on first plot
            legend_elements = [
                patches.Patch(color='yellow', label='Target Cell'),
                patches.Patch(color='lightgray', alpha=0.5, label='Fixed/Constant Area'),
                Line2D([0], [0], color='black', lw=2, label='Grid Boundary'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='green', label='Interior Neighbor'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='red', label='Fixed Boundary Value'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', label='Wrap-around'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='purple', label='Mirror/Reflective'),
            ]
            ax.legend(handles=legend_elements, loc='lower left', fontsize=8)

    plt.tight_layout()
    file_name = "boundary_comparison.png"
    plt.savefig(os.path.join(output_path, file_name), dpi=300)
    print(f"Comparison plot saved to {output_path}/{file_name}")
    plt.show()

if __name__ == "__main__":
    create_boundary_comparison_plot()