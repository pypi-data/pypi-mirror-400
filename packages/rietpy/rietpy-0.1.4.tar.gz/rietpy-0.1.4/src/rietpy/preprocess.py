import pandas as pd
import os
import re
from pathlib import Path
import numpy as np


def xy_to_general(input_file, output_file):
    """
    Convert an xy format file to RIETAN GENERAL format.

    The RIETAN GENERAL format consists of:
    Line 1: "GENERAL"
    Line 2: Number of data points (integer)
    Line 3+: 2theta Intensity (space separated)

    Parameters
    ----------
    input_file : str
        Path to the input xy file.
    output_file : str
        Path to the output GENERAL format file.
    """
    try:
        # Read the xy file. Assuming whitespace delimiter.
        # header=None assumes the file starts with data.
        # If the file has a header, we might need to adjust, but simple xy usually doesn't.
        # We'll try to read it. If the first row is strings, we'll reload with header=0.
        df = pd.read_csv(input_file, sep=r"\s+", header=None, engine="python")

        # Check if the first row contains non-numeric data (likely a header)
        is_header = False
        try:
            float(df.iloc[0, 0])
        except ValueError:
            is_header = True

        if is_header:
            df = pd.read_csv(input_file, sep=r"\s+", header=0, engine="python")

        # Ensure we have at least 2 columns
        if df.shape[1] < 2:
            raise ValueError(
                f"Input file {input_file} must have at least 2 columns (2theta, Intensity)."
            )

        # Extract 2theta and Intensity (first two columns)
        data = df.iloc[:, :2]
        num_points = len(data)

        with open(output_file, "w") as f:
            f.write("GENERAL\n")
            f.write(f"{num_points}\n")
            # Write data points
            for _, row in data.iterrows():
                f.write(f"{row.iloc[0]:.6f} {row.iloc[1]:.6f}\n")

        print(f"Successfully converted {input_file} to {output_file}")

    except Exception as e:
        print(f"Failed to convert {input_file}: {e}")
        raise


def get_sequential_dataset(data_dir, base_name_pattern, reverse=False):
    """
    Search for sequential data files recursively and return them sorted by the numeric part.

    Parameters
    ----------
    data_dir : str or Path
        Directory to search in.
    base_name_pattern : str
        Filename pattern where '?' represents the numeric sequence.
        Example: "data_?.int" matches "data_0.int", "data_01.int", etc.
    reverse : bool, optional
        If True, sort in descending order. Default is False (ascending).

    Returns
    -------
    tuple of Path
        Sorted tuple of file paths.
    """
    data_dir = Path(data_dir)
    if not data_dir.exists():
        raise FileNotFoundError(f"Directory not found: {data_dir}")

    # Create regex from pattern
    if "?" not in base_name_pattern:
        raise ValueError("Pattern must contain '?' placeholder.")

    # Split by '?'
    parts = base_name_pattern.split("?")
    if len(parts) > 2:
        raise ValueError("Pattern must contain only one '?' placeholder.")

    prefix = parts[0]
    suffix = parts[1]

    # Regex to capture the number.
    # We use re.escape for the fixed parts to handle dots etc safely.
    pattern_re = re.compile(f"^{re.escape(prefix)}(\\d+){re.escape(suffix)}$")

    matched_files = []

    # Recursive search.
    for file_path in data_dir.rglob("*"):
        if not file_path.is_file():
            continue

        match = pattern_re.match(file_path.name)
        if match:
            number = int(match.group(1))
            matched_files.append((number, file_path))

    # Sort by the extracted number
    matched_files.sort(key=lambda x: x[0], reverse=reverse)

    return tuple(f[1] for f in matched_files)


def create_minimum_background_profile(input_files, output_file):
    """
    Create a background profile using the Minimum Profile Method.
    Calculates the minimum intensity at each 2-theta step across all input files.

    Parameters
    ----------
    input_files : list of str or Path
        List of input data files.
    output_file : str or Path
        Path to save the output background file.
    """
    if not input_files:
        print("No input files provided.")
        return

    # Helper to read file
    def _read_data(fpath):
        try:
            with open(fpath, "r") as f:
                header = f.readline().strip()

            skip = 0
            if header == "GENERAL":
                skip = 2

            df = pd.read_csv(
                fpath, sep=r"\s+", skiprows=skip, header=None, engine="python"
            )

            # Check if first row is header (non-numeric) if not GENERAL
            if header != "GENERAL":
                try:
                    float(df.iloc[0, 0])
                except (ValueError, TypeError):
                    # Reload with header
                    df = pd.read_csv(fpath, sep=r"\s+", header=0, engine="python")

            return df.iloc[:, :2].values  # Return numpy array of 2theta, Intensity
        except Exception as e:
            print(f"Error reading {fpath}: {e}")
            return None

    # Process first file
    base_data = _read_data(input_files[0])
    if base_data is None:
        raise ValueError(f"Could not read first file: {input_files[0]}")

    two_theta = base_data[:, 0]
    min_intensity = base_data[:, 1]

    for fpath in input_files[1:]:
        data = _read_data(fpath)
        if data is None:
            continue

        # Check length
        if len(data) != len(two_theta):
            print(f"Warning: {fpath} length {len(data)} != {len(two_theta)}. Skipping.")
            continue

        # Check 2theta (optional, maybe just assume same grid for speed/simplicity or warn)
        if not np.allclose(data[:, 0], two_theta, atol=1e-3):
            print(f"Warning: {fpath} 2theta mismatch. Skipping.")
            continue

        min_intensity = np.minimum(min_intensity, data[:, 1])

    # Save
    with open(output_file, "w") as f:
        # Usually background files are just X Y.
        for x, y in zip(two_theta, min_intensity):
            f.write(f"{x:.6f}  {y:.6f}\n")

    print(f"Background profile saved to {output_file}")
