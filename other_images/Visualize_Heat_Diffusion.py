import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

output_path = "output"

def run_visualization():
    # --- Parameter settings ---
    rows, cols = 100, 100
    iterations = 200
    alpha = 0.1  # Heat diffusion coefficient < 0.25
    seed_value = 100.0

    # Initialize grid
    grid = np.zeros((rows, cols))
    # Place heat source in the center
    grid[rows // 2, cols // 2] = seed_value

    # Set up canvas
    fig, ax = plt.subplots(figsize=(8, 6))
    # Fixed scale range: vmin=0, vmax set to 10% of initial heat source to make the diffusion process clearer
    im = ax.imshow(grid, cmap='hot', interpolation='nearest', animated=True, vmin=0, vmax=seed_value * 0.1)
    ax.set_title(f"Heat Diffusion Simulation - Iteration 0")
    plt.colorbar(im, label='Temperature')

    def update(frame):
        """Update function for each iteration cycle"""
        nonlocal grid
        
        # Implement periodic boundary conditions using numpy.roll
        # np.roll(grid, 1, axis=0) shifts all rows down by one, with the last row wrapping to the first (up)
        # np.roll(grid, -1, axis=0) shifts all rows up by one, with the first row wrapping to the last (down)
        
        up    = np.roll(grid,  1, axis=0)
        down  = np.roll(grid, -1, axis=0)
        left  = np.roll(grid,  1, axis=1)
        right = np.roll(grid, -1, axis=1)

        # Calculate Laplacian operator (5-point convolution)
        # next = current + alpha * (up + down + left + right - 4 * current)
        laplacian = up + down + left + right - 4 * grid
        grid = grid + alpha * laplacian

        # Update image data
        im.set_array(grid)
        
        # Update title to show current iteration step
        ax.set_title(f"Heat Diffusion Simulation - Iteration {frame}")
        
        if frame % 20 == 0:
            print(f"Processing frame {frame}/{iterations}...")
            
        return [im, ax.title]

    # Create animation
    # interval: time interval between frames (ms)
    ani = animation.FuncAnimation(fig, update, frames=iterations, interval=50, blit=True)

    # Save as GIF (requires pillow library: pip install pillow)
    print("Saving animation to heat_diffusion.gif...")
    try:
        ani.save(os.path.join(output_path, "heat_diffusion_periodic.gif"), writer='pillow')
        print("Success! File saved as heat_diffusion_periodic.gif")
    except Exception as e:
        print(f"Error saving GIF: {e}")
        print("Showing plot instead...")
        plt.show()

    # Uncomment the line below if you want to see the window demo directly
    # plt.show()

if __name__ == "__main__":
    run_visualization()