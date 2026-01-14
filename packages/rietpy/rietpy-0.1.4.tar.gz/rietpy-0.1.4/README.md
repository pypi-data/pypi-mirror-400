# RIETPY

**RIETPY** is a Python library designed to automate Rietveld analysis using the [RIETAN-FP](http://fujioizumi.verse.jp/download/download.html) engine. It streamlines the refinement process by providing tools to programmatically manipulate input files, execute the refinement engine, parse results, and visualize outputs.

## Features

*   **Automated Execution**: Run RIETAN-FP (`rietan`) and `cif2ins` directly from Python.
*   **Input Manipulation**: Read, parse, and modify `.ins` files programmatically.
*   **Result Parsing**: Extract R-factors ($R_{wp}$, $R_p$, $S$, etc.) and refined lattice parameters from output files.
*   **Batch Analysis**:
    *   **CSV-based**: Run analysis on multiple samples with parameters defined in a CSV file.
    *   **Sequential Refinement**: Automatically refine a series of datasets (e.g., temperature dependence), passing refined lattice parameters from one run to the next.
*   **Visualization**: Plot observed vs. calculated diffraction patterns (`.gpd` files).

## Prerequisites

*   **OS**: Windows
*   **Python**: >= 3.13
*   **RIETAN-FP**: The latest version of RIETAN-FP must be installed. It should be located at `C:\Program Files\RIETAN_VENUS` (default) or the executables (`rietan`, `cif2ins`) must be accessible in your system's PATH.

## Installation

You can install RIETPY directly from PyPI:

```bash
pip install rietpy
```

## Usage

### 1. Basic Execution

```python
from rietpy.engine import RietanEngine

# Initialize engine (assumes 'rietan' is in PATH)
engine = RietanEngine()

# Run cif2ins (Create .ins from .cif)
engine.run_cif2ins("sample.cif", "template.ins")

# Run refinement
engine.run("sample.ins")
```

### 2. Parsing Results

```python
from rietpy.parser import ResultParser

# Parse R-factors
results = ResultParser.parse_lst("path/to/sample.lst")
print(f"Rwp: {results['Rwp']}, S: {results['S']}")

# Parse Lattice Parameters
lattice = ResultParser.parse_lattice_params("path/to/sample.lst")
print(f"Refined a: {lattice['a']}, c: {lattice['c']}")
```

### 3. Modifying Input Files

```python
from rietpy.parser import InsParser

parser = InsParser()
parser.read("sample.ins")

# Change a parameter
parser.set_param("NBEAM", "1")  # Set to Conventional X-ray

# Update lattice parameters
parser.set_lattice_params({'a': 5.123, 'c': 13.45})

parser.write("modified.ins")
```

### 4. Multi-step Refinement (Single Sample)

Run a multi-step refinement on a single dataset by defining a strategy in a CSV file. This allows you to gradually turn on parameters (e.g., Scale -> Background -> Lattice -> Profile -> Structure).

```python
from rietpy.analysis import BatchAnalyzer

analyzer = BatchAnalyzer()

# 1. Generate a template CSV from an .ins file
# This creates a CSV with columns for all parameters found in the .ins file
analyzer.generate_template_csv("sample.ins", "strategy.csv")

# 2. Edit the CSV file to define steps (rows)
# Set '1' to refine a parameter, '0' to fix it.
# Each row represents one run of RIETAN.

# 3. Run the multi-step refinement
# Set real_time_plot=True to visualize Rwp and profile fitting progress in Jupyter Notebook
analyzer.run_single_refinement("sample.ins", "strategy.csv", real_time_plot=True)
```

### 5. Sequential Refinement

Perform sequential refinement on a series of data files (e.g., temperature dependence). The refined parameters from one run are automatically propagated to the next.

**Features:**
*   **Anchor Points**: Specify a list of `.ins` files in `anchor_ins_files`. If a file matches the current data file name, it resets the model (e.g., at a phase transition).
*   **Background Propagation**: Support for `.bkg` files via `anchor_bkg_files`. Backgrounds are propagated or reset similar to `.ins` files.
*   **Multi-step Refinement**: Use `parameter_csv_files` to define a multi-step refinement strategy (e.g., Step 1: Scale/Bkg, Step 2: +Lattice, Step 3: +Atomic Coords) for each anchor.
*   **Resume Capability**: Resume analysis from a specific sample using `resume_from`.

```python
from rietpy.analysis import BatchAnalyzer

analyzer = BatchAnalyzer()

# 1. Generate a template CSV for multi-step refinement (optional)
# analyzer.generate_template_csv("temp_100K.ins", "refinement_strategy.csv")

data_files = ["data/temp_100K.int", "data/temp_200K.int", "data/temp_300K.int"]

# List of available anchor .ins files.
# The analyzer matches them to data files by filename.
# e.g. "temp_100K.ins" is used for "temp_100K.int".
# If no anchor is found, the result from the previous run is used.
anchor_ins_files = ["anchors/temp_100K.ins", "anchors/temp_300K.ins"]

# Optional: CSV files for multi-step refinement strategies
parameter_csv_files = ["anchors/strategy_A.csv"]

# Optional: Background files (.bkg) can also be anchored/propagated
anchor_bkg_files = ["anchors/temp_100K.bkg"]

analyzer.run_sequential(
    data_files=data_files,
    anchor_ins_files=anchor_ins_files,
    parameter_csv_files=parameter_csv_files,
    anchor_bkg_files=anchor_bkg_files,
    output_dir="results_sequential",
    resume_from="temp_200K"  # Optional: Resume from a specific sample
)
```

### 5. Multi-phase Model Creation

Combine multiple single-phase `.ins` files into a single multi-phase `.ins` file.

```python
from rietpy.engine import RietanEngine

engine = RietanEngine()

# Base file (Phase 1) + List of other phases
engine.combine_ins_files(
    base_ins="phase1.ins", 
    other_ins_list=["phase2.ins", "phase3.ins"], 
    output_ins="multiphase.ins"
)
```

### 6. Visualization

```python
from rietpy.plot import Plotter

plotter = Plotter()
plotter.plot_pattern("sample.gpd", title="Refinement Result")
```

### 7. Parsing Sequential Results

```python
from rietpy.parser import ResultParser

# Parse results from a sequential run directory
# Returns a dict: {'Filename': [...], 'Rwp': [...], 'a': [...], ...}
seq_results = ResultParser.parse_sequential_results("results_sequential")
```

## Project Structure

```
src/rietpy/
├── engine.py       # Wrappers for RIETAN-FP executables
├── parser.py       # Parsers for .ins (input) and .lst (output) files
├── analysis.py     # High-level automation (Batch, Sequential)
└── plot.py         # Visualization tools
```

## License

MIT License
