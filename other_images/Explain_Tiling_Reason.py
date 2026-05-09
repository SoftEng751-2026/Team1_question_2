import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
import os

def create_tiling_reason_plot():
    """
    Visualizes why Tiling is used: Cache Locality vs Memory Wall.
    """
    output_path = "output"
    os.makedirs(output_path, exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    grid_size = 12
    tile_size = 4

    def draw_grid(ax, title):
        ax.set_xlim(-0.5, grid_size - 0.5)
        ax.set_ylim(grid_size - 0.5, -0.5)
        ax.set_aspect('equal')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        for i in range(grid_size + 1):
            ax.axhline(i - 0.5, color='gray', lw=0.5, alpha=0.5)
            ax.axvline(i - 0.5, color='gray', lw=0.5, alpha=0.5)
        ax.set_xticks([])
        ax.set_yticks([])

    # --- Scenario 1: Row-Major (No Tiling) ---
    draw_grid(ax1, "Standard Row-Major Access\n(Poor Temporal Locality)")
    
    # Highlight current row being processed
    curr_row = 5
    ax1.add_patch(patches.Rectangle((-0.5, curr_row - 0.5), grid_size, 1, color='blue', alpha=0.2, label='Current Row'))
    
    # Highlight a specific stencil operation
    target_x, target_y = 6, curr_row
    ax1.add_patch(patches.Rectangle((target_x - 0.5, target_y - 0.5), 1, 1, color='yellow', alpha=0.8))
    
    # Show the "Top" neighbor being far away in time
    ax1.add_patch(patches.Rectangle((target_x - 0.5, target_y - 1.5), 1, 1, edgecolor='red', facecolor='none', lw=2, hatch='///'))
    ax1.annotate("Top neighbor was loaded\nlong ago. Likely EVICTED\nfrom Cache!", 
                 xy=(target_x, target_y - 1), xytext=(target_x - 4, target_y - 3),
                 arrowprops=dict(arrowstyle="->", color='red'), fontsize=10, color='red', fontweight='bold', ha='center')

    # Show scanning arrow
    ax1.annotate("", xy=(grid_size-1, curr_row), xytext=(0, curr_row),
                 arrowprops=dict(arrowstyle="->", lw=2, color='blue'))
    ax1.text(grid_size/2, curr_row + 0.8, "Scanning long rows...", ha='center', color='blue', fontsize=10)


    # --- Scenario 2: Tiled Access ---
    draw_grid(ax2, "Tiled Access (Blocking)\n(High Cache Reuse)")
    
    # Highlight the Tile
    tile_x, tile_y = 4, 4
    ax2.add_patch(patches.Rectangle((tile_x - 0.5, tile_y - 0.5), tile_size, tile_size, 
                                   edgecolor='green', facecolor='green', alpha=0.2, lw=3, label='Working Set (Tile)'))
    
    # Highlight a specific stencil inside the tile
    target_x, target_y = 5, 5
    ax2.add_patch(patches.Rectangle((target_x - 0.5, target_y - 0.5), 1, 1, color='yellow', alpha=0.8))
    
    # Show neighbors - all inside the "Hot" tile
    neighbors = [(target_x, target_y-1), (target_x, target_y+1), (target_x-1, target_y), (target_x+1, target_y)]
    for nx, ny in neighbors:
        ax2.add_patch(patches.Rectangle((nx - 0.5, ny - 0.5), 1, 1, edgecolor='green', facecolor='none', lw=2))

    ax2.annotate("Entire block fits in L1/L2 Cache.\nAll 5 neighbors are 'HOT'\nand reused immediately!", 
                 xy=(target_x + 0.5, target_y), xytext=(target_x + 4, target_y + 2),
                 arrowprops=dict(arrowstyle="->", color='green'), fontsize=10, color='green', fontweight='bold', ha='center')

    # Show scanning arrow inside tile
    ax2.annotate("", xy=(tile_x + tile_size - 1, tile_y), xytext=(tile_x, tile_y),
                 arrowprops=dict(arrowstyle="->", lw=2, color='green'))

    # --- Global Labels & Legend ---
    legend_elements = [
        patches.Patch(color='yellow', label='Current Pixel being calculated'),
        patches.Patch(color='blue', alpha=0.2, label='Memory Scan Path'),
        patches.Patch(color='green', alpha=0.2, label='Data currently in Cache'),
        Line2D([0], [0], color='red', linestyle='--', lw=2, label='Cache Miss / DRAM Access'),
        Line2D([0], [0], color='green', lw=2, label='Cache Hit / Fast Access')
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3, bbox_to_anchor=(0.5, 0.05))

    plt.suptitle("Why use Tiling? Cache Locality vs. Memory Latency", fontsize=20, y=0.98)
    plt.subplots_adjust(bottom=0.2)
    
    file_name = "explain_tiling_reason.png"
    plt.savefig(os.path.join(output_path, file_name), dpi=300)
    print(f"Explanation plot saved to {output_path}/{file_name}")
    plt.show()

if __name__ == "__main__":
    create_tiling_reason_plot()