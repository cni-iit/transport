import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

def plot_resistance_vs_voltage(
    file_path, 
    output_file='resistance_vs_voltage.png', 
    figsize=(6,6),
    grid_on=False,
    dpi=300,
    fontsize=15
    ):
    """
    Plot a resistance vs voltage curve from a tab-separated text file and export as image.
    
    Parameters:
    -----------
    file_path : str
        Path to tab-separated file with Raman data
    output_file : str, optional
        Name of output file (default: 'resistance_vs_voltage.png')
    figsize : tuple, optional
        Figure dimensions (width, height) in inches
    grid_on : bool, optional
        Whether to show grid lines on the plot
    dpi : int, optional
        Resolution of output image
    fontsize : int, optional
        Value to adjust the font throughout the picture
    """
    # Read the data from the tab-separated file
    data = np.loadtxt(file_path, delimiter='\t')
    
    # Extract gate voltage (V) and resistance (Ohm)
    gate_voltage = data[:, 0]
    resistance = data[:, 1]
    
    # Convert resistance from Ohm to kOhm
    resistance_kohm = resistance / 1000
    
    # Set font sizes
    rcParams['font.size'] = fontsize
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(gate_voltage, resistance_kohm, linewidth=1.5)
    
    # Add labels and title
    ax.set_xlabel(r'$V_{bg}$ (V)')
    ax.set_ylabel(r'$R_{xx}$ (kΩ)')
    # plt.title('Resistance vs. Gate Voltage', fontsize=fontsize+2)
    
    ax.set_xlim([-10,10])
    
    # Add grid
    if grid_on:
        plt.grid(True, linestyle='--', alpha=0.7)
    
    # Adjust layout
    fig.tight_layout()
    
    # Save the plot
    plt.savefig(output_file, dpi=dpi, bbox_inches='tight')
    
    # Show and close the plot
    plt.show()
    plt.close()
    
    print(f"Plot saved as {output_file}")

if __name__ == "__main__":
    
    # Create the plot
    plot_resistance_vs_voltage(
        file_path='example.txt',
        output_file='resistance_vs_voltage.png',
        # figsize=(8,6),  # Defaults to (6,6)
        # grid_on=True,   # Activate to display grid lines
        # dpi=600,        # Defaults to 300
        # fontsize=20     # Defaults to 15
        )