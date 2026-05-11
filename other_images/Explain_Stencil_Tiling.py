import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import os

output_path = "output"

def run_explanation_animation():
    # Set up a smaller grid for observation
    rows, cols = 4, 4
    tile_size = 2
    alpha = 0.1
    num_iterations = 3
    
    # Create a dedicated directory for individual step images
    # steps_dir = os.path.join(output_path, "explanation_steps")
    # os.makedirs(steps_dir, exist_ok=True)
    
    # Set up two subplots side-by-side to show Double Buffering
    fig, (ax_src, ax_dst) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Initialize two separate buffers
    grid_a = np.zeros((rows, cols))
    grid_a[rows // 2, cols // 2] = 100.0 # Heat in Grid A
    grid_b = np.zeros((rows, cols))      # Empty Grid B
    
    # Plot initial state
    im_a = ax_src.imshow(grid_a, cmap='YlOrRd', vmin=0, vmax=100)
    im_b = ax_dst.imshow(grid_b, cmap='YlOrRd', vmin=0, vmax=100)
    
    # Initialize text labels
    texts_a = [[ax_src.text(j, i, f"{grid_a[i, j]:.1f}", ha='center', va='center', fontsize=10) for j in range(cols)] for i in range(rows)]
    texts_b = [[ax_dst.text(j, i, f"{grid_b[i, j]:.1f}", ha='center', va='center', fontsize=10) for j in range(cols)] for i in range(rows)]

    # Create highlighting patches for both axes (will toggle visibility)
    def add_highlights(ax):
        return {
            'tile': ax.add_patch(Rectangle((0, 0), tile_size, tile_size, linewidth=3, edgecolor='red', facecolor='none', visible=False)),
            'pixel': ax.add_patch(Rectangle((0, 0), 1, 1, linewidth=2, edgecolor='yellow', facecolor='orange', visible=False)),
            'center': ax.add_patch(Rectangle((0, 0), 1, 1, linewidth=2, edgecolor='yellow', facecolor='none', linestyle='--', visible=False)),
            'neighbors': [ax.add_patch(Rectangle((0, 0), 1, 1, linewidth=1, edgecolor='green', facecolor='lime', alpha=0.5, visible=False)) for _ in range(4)]
        }

    patches_a = add_highlights(ax_src)
    patches_b = add_highlights(ax_dst)

    # Add arrows to represent data flow from Src to Dst
    arrow_text = fig.text(0.5, 0.5, '→', fontsize=40, ha='center', va='center', fontweight='bold')

    # Generate steps for multiple iterations
    steps = []
    for t in range(num_iterations):
        for ii in range(0, rows, tile_size):
            for jj in range(0, cols, tile_size):
                for i in range(ii, min(ii + tile_size, rows)):
                    for j in range(jj, min(jj + tile_size, cols)):
                        steps.append((t, ii, jj, i, j))

    steps_per_iter = len(steps) // num_iterations

    def update(frame):
        t, ii, jj, i, j = steps[frame]
        step_in_iter = (frame % steps_per_iter) + 1

        # Determine roles based on iteration (Double Buffering)
        if t % 2 == 0:  # Even: A -> B
            src_grid, dst_grid = grid_a, grid_b
            im_src, im_dst = im_a, im_b
            texts_src, texts_dst = texts_a, texts_b
            src_p, dst_p = patches_a, patches_b
            ax_src.set_title("Source (Grid A)", color='blue')
            ax_dst.set_title("Destination (Grid B)", color='darkred')
            arrow_text.set_text('→')
        else:           # Odd: B -> A
            src_grid, dst_grid = grid_b, grid_a
            im_src, im_dst = im_b, im_a
            texts_src, texts_dst = texts_b, texts_a
            src_p, dst_p = patches_b, patches_a
            ax_src.set_title("Destination (Grid A)", color='darkred')
            ax_dst.set_title("Source (Grid B)", color='blue')
            arrow_text.set_text('←')

        # If starting new iteration, clear the destination grid visually
        if step_in_iter == 1:
            dst_grid.fill(0.0)
            im_dst.set_array(dst_grid)
            for r in range(rows):
                for c in range(cols): 
                    texts_dst[r][c].set_text("0.0")
                    texts_dst[r][c].set_color("black")

        # 1. Stencil Logic
        up, down = src_grid[(i - 1) % rows, j], src_grid[(i + 1) % rows, j]
        left, right = src_grid[i, (j - 1) % cols], src_grid[i, (j + 1) % cols]
        delta = up + down + left + right - 4 * src_grid[i, j]
        dst_grid[i, j] = src_grid[i, j] + alpha * delta

        # 2. Update destination display
        im_dst.set_array(dst_grid)
        val = dst_grid[i, j]
        texts_dst[i][j].set_text(f"{val:.1f}")
        texts_dst[i][j].set_color("white" if val > 50 else "black")
        
        # 3. Handle Visibility and Movement of Patches
        for p_set in [patches_a, patches_b]:
            p_set['tile'].set_visible(False)
            p_set['pixel'].set_visible(False)
            p_set['center'].set_visible(False)
            for n in p_set['neighbors']: n.set_visible(False)

        dst_p['tile'].set_visible(True)
        dst_p['pixel'].set_visible(True)
        src_p['center'].set_visible(True)
        for n in src_p['neighbors']: n.set_visible(True)

        # Update Destination boxes
        dst_p['tile'].set_xy((jj - 0.5, ii - 0.5))
        # For periodic, tiles cover the entire range up to rows/cols
        dst_p['tile'].set_width(min(jj + tile_size, cols) - jj)
        dst_p['tile'].set_height(min(ii + tile_size, rows) - ii)
        dst_p['pixel'].set_xy((j - 0.5, i - 0.5))

        # Update Source boxes
        src_p['center'].set_xy((j - 0.5, i - 0.5))
        neighbor_coords = [((i - 1) % rows, j), ((i + 1) % rows, j), (i, (j - 1) % cols), (i, (j + 1) % cols)]
        for idx, (ni, nj) in enumerate(neighbor_coords):
            src_p['neighbors'][idx].set_xy((nj - 0.5, ni - 0.5))

        # 4. Global Title Update
        fig.suptitle(f"Double Buffering Stencil: Iteration {t+1}/{num_iterations} | Step {step_in_iter}/{steps_per_iter}", fontsize=16, y=0.95)

        # Save the current frame as an individual image file
        # fig.savefig(os.path.join(steps_dir, f"step_{frame:04d}.png"))

        return []

    ani = animation.FuncAnimation(fig, update, frames=len(steps), interval=800, blit=False)

    for ax in [ax_src, ax_dst]:
        ax.set_xticks(np.arange(cols))
        ax.set_yticks(np.arange(rows))
        ax.set_xticks(np.arange(cols + 1) - 0.5, minor=True)
        ax.set_yticks(np.arange(rows + 1) - 0.5, minor=True)
        ax.set_aspect('equal')
        ax.grid(True, which='minor', color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
        ax.tick_params(which='minor', length=0, labelbottom=False, labelleft=False)

    plt.tight_layout(rect=[0, 0, 1, 0.9])
    
    print("Saving explanation animation...")
    # Set fps to 1 to match the 1000ms interval for the saved GIF
    ani.save(os.path.join(output_path, "stencil_tiling_explanation.gif"), writer='pillow', fps=1)
    print("Done! Saved as stencil_tiling_explanation.gif")
    plt.show()

if __name__ == "__main__":
    run_explanation_animation()