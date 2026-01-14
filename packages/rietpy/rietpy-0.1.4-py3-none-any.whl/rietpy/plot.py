import pandas as pd
import matplotlib.pyplot as plt
import os

class Plotter:
    def load_data(self, gpd_path: str) -> pd.DataFrame:
        """
        Loads diffraction data from a .gpd file.
        
        Args:
            gpd_path (str): Path to the .gpd file.
            
        Returns:
            pd.DataFrame: DataFrame containing the data.
        """
        if not os.path.exists(gpd_path):
            raise FileNotFoundError(f"File not found: {gpd_path}")

        try:
            # Read file line by line to handle the reflection list at the end
            with open(gpd_path, 'r') as f:
                lines = f.readlines()
            
            data_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#'):
                    # Stop if we reach the reflection list
                    if "h, k, l" in line:
                        break
                    # Skip other comments (header)
                    continue
                
                data_lines.append(line)
            
            from io import StringIO
            data_str = "".join(data_lines)
            
            df = pd.read_csv(
                StringIO(data_str), 
                sep=r'\s+', 
                header=None,
                names=['2theta', 'I_obs', 'I_calc', 'Residual', 'Background']
            )
            return df
        except Exception as e:
            raise ValueError(f"Failed to read .gpd file: {e}")

    def plot_pattern(self, gpd_path: str, output_path: str = None, title: str = "Rietveld Refinement Result"):
        """
        Plots the observed and calculated diffraction patterns.
        
        Args:
            gpd_path (str): Path to the .gpd file.
            output_path (str, optional): Path to save the plot image. If None, shows the plot.
            title (str): Plot title.
        """
        df = self.load_data(gpd_path)
        
        plt.figure(figsize=(10, 6))
        
        # Plot Observed (dots)
        plt.plot(df['2theta'], df['I_obs'], 'r+', label='Observed', markersize=4, markeredgewidth=0.5)
        
        # Plot Calculated (line)
        plt.plot(df['2theta'], df['I_calc'], 'g-', label='Calculated', linewidth=1)
        
        # Plot Difference (line at bottom)
        # Usually difference is plotted shifted down
        # We want to shift it so it doesn't overlap too much with the pattern
        # A common way is to put it below zero
        min_obs = df['I_obs'].min()
        max_obs = df['I_obs'].max()
        range_obs = max_obs - min_obs
        
        # Shift residual down by 10% of range
        offset = range_obs * 0.1
        
        plt.plot(df['2theta'], df['Residual'] - offset, 'b-', label='Difference', linewidth=1)
        
        # Plot Background (optional, dashed)
        plt.plot(df['2theta'], df['Background'], 'k--', label='Background', linewidth=0.5)
        
        plt.xlabel('2-Theta (degrees)')
        plt.ylabel('Intensity (a.u.)')
        plt.title(title)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300)
            plt.close()
        else:
            plt.show()
