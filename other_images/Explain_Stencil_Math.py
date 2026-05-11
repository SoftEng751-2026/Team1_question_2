import matplotlib.pyplot as plt
import numpy as np
import os

output_path = "output"

def draw_stencil_explanation():
    fig, ax = plt.subplots(figsize=(10, 9))
    
    # Define grid size
    grid_size = 3
    ax.set_xlim(-0.5, grid_size - 0.5)
    ax.set_ylim(-0.5, grid_size - 0.5)
    
    # Draw background grid lines
    for x in range(grid_size + 1):
        ax.axhline(x - 0.5, color='gray', lw=1, alpha=0.5)
        ax.axvline(x - 0.5, color='gray', lw=1, alpha=0.5)

    # Define position and attributes of 5-point Stencil
    # (row, col, label, color, weight)
    points = [
        (1, 1, 'Center\n(i, j)', '#ffcc00', '-4'),   # Center point
        (2, 1, 'Up\n(i-1, j)', '#99ff99', '+1'),    # Up
        (0, 1, 'Down\n(i+1, j)', '#99ff99', '+1'),  # Down
        (1, 0, 'Left\n(i, j-1)', '#99ff99', '+1'),  # Left
        (1, 2, 'Right\n(i, j+1)', '#99ff99', '+1')  # Right
    ]

    for r, c, label, color, weight in points:
        # Draw squares
        rect = plt.Rectangle((c - 0.5, r - 0.5), 1, 1, color=color, alpha=0.8)
        ax.add_patch(rect)
        
        # Add coordinate labels
        ax.text(c, r + 0.2, label, ha='center', va='center', fontsize=12, fontweight='bold')
        # Add weight labels
        ax.text(c, r - 0.2, f"Weight: {weight}", ha='center', va='center', fontsize=10, fontstyle='italic')

    # Draw arrows pointing to the center, representing heat flow (increase shrink to avoid blocking text)
    arrow_props = dict(facecolor='black', shrink=0.35, width=1.5, headwidth=6)
    ax.annotate('', xy=(1, 1), xytext=(1, 2), arrowprops=arrow_props) # From Up
    ax.annotate('', xy=(1, 1), xytext=(1, 0), arrowprops=arrow_props) # From Down
    ax.annotate('', xy=(1, 1), xytext=(0, 1), arrowprops=arrow_props) # From Left
    ax.annotate('', xy=(1, 1), xytext=(2, 1), arrowprops=arrow_props) # From Right

    # Add formula explanation
    formula = (
        r"$T_{i,j}^{next} = T_{i,j} + \alpha \cdot \Delta T$" + "\n\n" +
        r"$\Delta T = (T_{up} + T_{down} + T_{left} + T_{right} - 4 \cdot T_{center})$"
    )
    plt.figtext(0.5, 0.1, formula, ha='center', fontsize=13, 
                bbox={"facecolor":"orange", "alpha":0.2, "pad":10})

    # Chart decoration
    ax.set_title("5-Point Stencil: Heat Diffusion Logic", fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks([0, 1, 2])
    ax.set_yticks([0, 1, 2])
    ax.set_xticklabels(['j-1', 'j', 'j+1'])
    ax.set_yticklabels(['i+1', 'i', 'i-1']) # Matrix coordinates are opposite to plotting coordinates on the y-axis
    
    plt.gca().set_aspect('equal', adjustable='box')
    plt.subplots_adjust(bottom=0.25) # Leave bottom space for the formula
    
    # 保存图片
    output_file = os.path.join(output_path, "stencil_math_explanation.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Explanation diagram saved as {output_file}")
    plt.show()

if __name__ == "__main__":
    draw_stencil_explanation()