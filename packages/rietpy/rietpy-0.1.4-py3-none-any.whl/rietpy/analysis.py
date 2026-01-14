import pandas as pd
import os
import shutil
import re
import csv
import matplotlib.pyplot as plt
from IPython.display import display, clear_output
from .engine import RietanEngine
from .parser import InsParser, ResultParser
from .plot import Plotter
from .constants import KEYWORD_PATTERN, BKGD_PATTERN, STRUCTURE_PATTERN


class BatchAnalyzer:
    def __init__(self, engine=None):
        self.engine = engine if engine else RietanEngine()

    def _evaluate_condition(self, condition_str, variables):
        """
        Evaluates a RIETAN condition string (e.g., "NMODE <> 1").
        Supports operators: =, <>, >=, <=, >, <
        Supports logical operators: AND, OR
        """
        cond = condition_str.lower()

        # Split by OR
        or_parts = cond.split(" or ")
        for or_part in or_parts:
            # Split by AND
            and_parts = or_part.split(" and ")
            and_result = True
            for atom in and_parts:
                atom = atom.strip()
                # Find operator
                op = None
                # Check multi-char ops first
                for check_op in ["<>", ">=", "<=", "=", ">", "<"]:
                    if check_op in atom:
                        op = check_op
                        break

                if not op:
                    # Invalid atom? assume False
                    and_result = False
                    break

                left, right = atom.split(op, 1)
                var_name = left.strip()
                val_str = right.strip()

                # Get variable value
                # Try exact match first
                var_val = variables.get(var_name)
                if var_val is None:
                    # Try case-insensitive match
                    for k, v in variables.items():
                        if k.lower() == var_name.lower():
                            var_val = v
                            break

                if var_val is None:
                    # Variable not defined, condition fails
                    and_result = False
                    break

                # Parse right side value
                try:
                    if "." in val_str:
                        target_val = float(val_str)
                    else:
                        target_val = int(val_str)
                except ValueError:
                    # Maybe comparing strings?
                    target_val = val_str.strip("'").strip('"')

                # Compare
                res = False
                if op == "=":
                    res = var_val == target_val
                elif op == "<>":
                    res = var_val != target_val
                elif op == ">=":
                    res = var_val >= target_val
                elif op == "<=":
                    res = var_val <= target_val
                elif op == ">":
                    res = var_val > target_val
                elif op == "<":
                    res = var_val < target_val

                if not res:
                    and_result = False
                    break

            if and_result:
                return True

        return False

    def _split_constraints(self, constraints_str):
        """
        Splits a string of constraints by semicolon.
        e.g. "A(Ca1,x)=...; A(Ca2,y)=..." -> ["A(Ca1,x)=...", "A(Ca2,y)=..."]
        """
        if not constraints_str:
            return []
        return [c.strip() for c in constraints_str.split(";") if c.strip()]

    def generate_template_csv(self, ins_file, csv_file):
        """
        Parses the .ins file and generates a template CSV for automatic analysis.
        The CSV header contains 'Run number' and analysis parameters (refinement flags).
        The first row is initialized with Run number = 1 and 0 for all parameters.

        Args:
            ins_file (str): Path to the input .ins file.
            csv_file (str): Path to the output .csv file.
        """
        if not os.path.exists(ins_file):
            print(f"Error: Input file '{ins_file}' not found.")
            return False

        parameters = []
        in_structure_block = False

        # Variables for Select Case logic
        variables = {}
        active_stack = [True]  # Global scope is active
        select_stack = []  # Stack of {variable, value, has_matched}
        if_stack = []  # Stack of {has_matched} for If/ElseIf/Else

        with open(ins_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i]  # Keep original line for regex matching
            line_strip = line.strip()

            # --- Select Case Logic ---

            # 1. Variable Assignment (e.g., NBEAM = 0)
            # Only process assignments if we are in an active block
            if all(active_stack):
                # Simple heuristic for assignment: VAR = VAL
                # Ignore lines starting with '!' or '#'
                if (
                    not line_strip.startswith("!")
                    and not line_strip.startswith("#")
                    and "=" in line_strip
                ):
                    # If line contains '!', it is a comment line (inactive assignment)
                    if "!" in line_strip:
                        pass
                    else:
                        # Remove comments (only ':' is valid for active assignment)
                        clean_line = line_strip.split(":")[0]
                        if "=" in clean_line:
                            parts = clean_line.split("=")
                            if len(parts) == 2:
                                var_name = parts[0].strip()
                                var_val_str = parts[1].strip()
                                # Try to parse as int or float
                                try:
                                    if "." in var_val_str:
                                        var_val = float(var_val_str)
                                    else:
                                        var_val = int(var_val_str)
                                    variables[var_name] = var_val
                                except ValueError:
                                    pass

            # --- If/Else Logic ---

            # If Statement
            if line_strip.lower().startswith("if ") and "then" in line_strip.lower():
                # Only evaluate if parent scope is active
                parent_active = all(active_stack)

                # Parse condition
                clean_line = line_strip.split("!")[0].split(":")[0].strip()
                lower_line = clean_line.lower()
                then_idx = lower_line.rfind("then")

                if then_idx > 3:
                    condition = clean_line[3:then_idx].strip()

                    is_match = False
                    if parent_active:
                        is_match = self._evaluate_condition(condition, variables)

                    # Push new scope
                    active_stack.append(is_match)
                    if_stack.append({"has_matched": is_match})

                i += 1
                continue

            # Else If Statement
            if line_strip.lower().startswith(
                "else if"
            ) or line_strip.lower().startswith("elseif"):
                if if_stack:
                    # Check if parent (excluding current If scope) is active
                    parent_active = all(active_stack[:-1])
                    current_if = if_stack[-1]

                    # If a previous branch already matched, this branch is inactive
                    if current_if["has_matched"]:
                        active_stack[-1] = False
                    else:
                        # Evaluate condition
                        clean_line = line_strip.split("!")[0].split(":")[0].strip()
                        lower_line = clean_line.lower()

                        if lower_line.startswith("else if"):
                            cond_start = 7
                        else:
                            cond_start = 6

                        then_idx = lower_line.rfind("then")
                        if then_idx > cond_start:
                            condition = clean_line[cond_start:then_idx].strip()

                            is_match = False
                            if parent_active:
                                is_match = self._evaluate_condition(
                                    condition, variables
                                )

                            active_stack[-1] = is_match
                            if is_match:
                                current_if["has_matched"] = True
                i += 1
                continue

            # Else Statement
            if line_strip.lower().startswith("else") and not (
                line_strip.lower().startswith("else if")
                or line_strip.lower().startswith("elseif")
            ):
                if if_stack:
                    parent_active = all(active_stack[:-1])
                    current_if = if_stack[-1]

                    if current_if["has_matched"]:
                        active_stack[-1] = False
                    else:
                        active_stack[-1] = parent_active
                        current_if["has_matched"] = True
                i += 1
                continue

            # End If Statement
            if line_strip.lower().startswith("end if") or line_strip.lower().startswith(
                "endif"
            ):
                if if_stack:
                    if_stack.pop()
                    active_stack.pop()
                i += 1
                continue

            # 2. Select Case Start
            if line_strip.lower().startswith("select case"):
                # Remove comments first
                clean_line = line_strip.split("!")[0].split(":")[0].strip()
                parts = clean_line.split()
                if len(parts) >= 3:
                    var_name = parts[2]
                    var_value = variables.get(var_name)
                    select_stack.append(
                        {"variable": var_name, "value": var_value, "has_matched": False}
                    )
                    # Enter new scope, initially inactive until a case matches
                    active_stack.append(False)
                i += 1
                continue

            # 3. Case Statement
            if line_strip.lower().startswith("case"):
                if select_stack:
                    current_select = select_stack[-1]
                    case_val_str = line_strip[4:].strip()

                    is_match = False
                    if case_val_str.lower().startswith("default"):
                        # Default matches if nothing else has matched
                        is_match = not current_select["has_matched"]
                    else:
                        # Parse values: case 0, 1, 2
                        case_val_str = case_val_str.split("!")[0].split(":")[0]
                        possible_values = [v.strip() for v in case_val_str.split(",")]

                        for val_str in possible_values:
                            # Handle range syntax 'min-max' (e.g. 1-3)
                            # Simple logic: assume positive integers usually
                            range_match = re.match(r"^(\d+)-(\d+)$", val_str)
                            if range_match:
                                low = float(range_match.group(1))
                                high = float(range_match.group(2))
                                if (
                                    current_select["value"] is not None
                                    and low <= current_select["value"] <= high
                                ):
                                    is_match = True
                                    break

                            try:
                                if "." in val_str:
                                    val = float(val_str)
                                else:
                                    val = int(val_str)
                                # Compare with variable value
                                if (
                                    current_select["value"] is not None
                                    and val == current_select["value"]
                                ):
                                    is_match = True
                                    break
                            except ValueError:
                                pass

                    # Update active state for this level
                    # Only activate if it's a match AND we haven't matched a previous case (exclusive)
                    if is_match and not current_select["has_matched"]:
                        active_stack[-1] = True
                        current_select["has_matched"] = True
                    else:
                        active_stack[-1] = False
                i += 1
                continue

            # 4. End Select
            if line_strip.lower().startswith("end select"):
                if select_stack:
                    select_stack.pop()
                    active_stack.pop()
                i += 1
                continue

            # --- End Select Case Logic ---

            # If not active, skip parameter extraction
            if not all(active_stack):
                i += 1
                continue

            # Check for Structure Parameter block
            if "! Structure parameters" in lines[i]:
                in_structure_block = True
                i += 1
                continue
            if in_structure_block and "End of lines" in lines[i]:
                in_structure_block = False
                i += 1
                continue

            if in_structure_block:
                match = STRUCTURE_PATTERN.match(lines[i])
                if match:
                    label_part = match.group(2)  # e.g. Ti1/Ti
                    label = label_part.split("/")[0]
                    ids = match.group(4)

                    suffixes = ["g", "x", "y", "z", "B"]
                    if len(ids) > 5:
                        for k in range(5, len(ids)):
                            suffixes.append(f"p{k}")

                    for k, suffix in enumerate(suffixes):
                        if k < len(ids):
                            parameters.append(f"{label}_{suffix}")
                    i += 1
                    continue
                # If not a structure line, fall through to check for keywords/BKGD
                # This handles cases where profile parameters are interleaved or block isn't strictly closed

            # Check for BKGD
            if line.startswith("BKGD"):
                # Check if IDs are on the same line
                match = BKGD_PATTERN.search(lines[i])
                if match:
                    for k in range(12):
                        parameters.append(f"BKGD_{k}")
                    i += 1
                    continue

                # Look ahead for IDs
                found_ids = False
                for offset in range(1, 4):
                    if i + offset < len(lines):
                        next_line = lines[i + offset]
                        if BKGD_PATTERN.search(next_line):
                            for k in range(12):
                                parameters.append(f"BKGD_{k}")
                            found_ids = True
                            i += offset + 1
                            break
                if found_ids:
                    continue

            # Check for other keywords
            match = KEYWORD_PATTERN.match(lines[i])
            if match:
                name = match.group(2)
                ids = match.group(4)
                count = len(ids)
                for k in range(count):
                    parameters.append(f"{name}_{k}")
                i += 1
                continue

            i += 1

        # Generate CSV
        header = parameters + ["Linear_constraints"]
        row1 = [0] * len(parameters) + [
            "# Use semicolon as a separator for multiple constraints"
        ]

        try:
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerow(row1)
            print(f"Template CSV generated: {csv_file}")
            return True
        except Exception as e:
            print(f"Error generating CSV: {e}")
            return False

    def _update_ins_with_flags(self, lines, flags_dict):
        """
        Updates the refinement flags (IDs) in the .ins file lines based on the dictionary.

        Args:
            lines (list): List of strings representing the .ins file content.
            flags_dict (dict): Dictionary mapping parameter names to '0' or '1'.

        Returns:
            list: Updated list of strings.
        """
        updated_lines = lines.copy()
        in_structure_block = False

        i = 0
        while i < len(updated_lines):
            line = updated_lines[i]

            # Check for Structure Parameter block
            if "! Structure parameters" in line:
                in_structure_block = True
                i += 1
                continue
            if in_structure_block and "End of lines" in line:
                in_structure_block = False
                i += 1
                continue

            if in_structure_block:
                match = STRUCTURE_PATTERN.match(line)
                if match:
                    label_part = match.group(2)  # Ti1/Ti
                    label = label_part.split("/")[0]  # Ti1
                    current_ids = match.group(4)

                    new_ids_list = list(current_ids)
                    suffixes = ["g", "x", "y", "z", "B"]
                    if len(current_ids) > 5:
                        for k in range(5, len(current_ids)):
                            suffixes.append(f"p{k}")

                    for k, s in enumerate(suffixes):
                        if k < len(current_ids):
                            key = f"{label}_{s}"
                            if key in flags_dict:
                                val = flags_dict[key]
                                if val in ["0", "1", "2"]:
                                    new_ids_list[k] = val

                    new_ids = "".join(new_ids_list)

                    # Reconstruct line
                    updated_lines[i] = (
                        match.group(1)
                        + match.group(2)
                        + match.group(3)
                        + new_ids
                        + match.group(5).rstrip("\n\r")
                        + "\n"
                    )
                i += 1
                continue

            # Check for BKGD
            if line.strip().startswith("BKGD"):

                def get_new_bkgd_ids(current_ids_str):
                    new_ids_list = list(current_ids_str)
                    for k in range(12):
                        key = f"BKGD_{k}"
                        if key in flags_dict:
                            val = flags_dict[key]
                            if val in ["0", "1", "2"]:
                                new_ids_list[k] = val
                    return "".join(new_ids_list)

                match = BKGD_PATTERN.search(line)
                if match:
                    current_ids = match.group(2)
                    new_ids = get_new_bkgd_ids(current_ids)
                    updated_lines[i] = BKGD_PATTERN.sub(
                        lambda m: m.group(1) + new_ids + m.group(3), line
                    )
                    i += 1
                    continue

                # Look ahead
                found_ids = False
                for offset in range(1, 4):
                    if i + offset < len(updated_lines):
                        next_line = updated_lines[i + offset]
                        match = BKGD_PATTERN.search(next_line)
                        if match:
                            current_ids = match.group(2)
                            new_ids = get_new_bkgd_ids(current_ids)
                            updated_lines[i + offset] = BKGD_PATTERN.sub(
                                lambda m: m.group(1) + new_ids + m.group(3), next_line
                            )
                            found_ids = True
                            i += offset + 1
                            break
                if found_ids:
                    continue

            # Check for other keywords
            match = KEYWORD_PATTERN.match(line)
            if match:
                name = match.group(2)
                current_ids = match.group(4)

                new_ids_list = list(current_ids)
                for k in range(len(current_ids)):
                    key = f"{name}_{k}"
                    if key in flags_dict:
                        val = flags_dict[key]
                        if val in ["0", "1", "2"]:
                            new_ids_list[k] = val
                new_ids = "".join(new_ids_list)

                updated_lines[i] = (
                    match.group(1)
                    + match.group(2)
                    + match.group(3)
                    + new_ids
                    + match.group(5).rstrip("\n\r")
                    + "\n"
                )

                i += 1
                continue

            i += 1

        return updated_lines

    def _save_summary(self, results_summary, ins_file, column_order=None):
        """Helper to save results summary to CSV."""
        if results_summary:
            working_dir = os.path.dirname(os.path.abspath(ins_file))
            summary_path = os.path.join(working_dir, "summary.csv")
            try:
                df = pd.DataFrame(results_summary)

                # Reorder columns
                cols = list(df.columns)
                ordered_cols = []

                # 1. Run_number must be first
                if "Run_number" in cols:
                    ordered_cols.append("Run_number")
                    cols.remove("Run_number")

                # 2. R-factors
                r_factors = ["Rwp", "Rp", "Re", "S"]
                for r in r_factors:
                    if r in cols:
                        ordered_cols.append(r)
                        cols.remove(r)

                # 3. Follow column_order for parameters (if provided)
                if column_order:
                    for col in column_order:
                        if col in cols:
                            ordered_cols.append(col)
                            cols.remove(col)

                # 4. Append remaining columns
                ordered_cols.extend(cols)

                df = df[ordered_cols]
                df.to_csv(summary_path, index=False)
                print(f"Run summary saved to {summary_path}")
            except Exception as e:
                print(f"Error saving summary CSV: {e}")

    def run_single_refinement(
        self, ins_file, csv_file, resume_from_run=None, real_time_plot=False
    ):
        """
        Executes a single refinement run (or sequence of runs on the SAME data) based on the CSV file.
        This was previously named 'run_sequential' in engine.py.

        Args:
            ins_file (str): Path to the initial .ins file.
            csv_file (str): Path to the CSV file containing refinement flags.
            resume_from_run (int or str, optional): Run number to resume from.
                                                    If specified, the .ins file is restored from
                                                    results/Run{resume_from_run}.ins, and runs
                                                    up to and including this number are skipped.

        Returns:
            bool: True if all runs completed successfully, False otherwise.
        """
        if not os.path.exists(csv_file):
            print(f"Error: CSV file '{csv_file}' not found.")
            return False

        fieldnames = []
        try:
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                runs = list(reader)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return False

        # Handle Resume
        if resume_from_run is not None:
            working_dir = os.path.dirname(os.path.abspath(ins_file))
            results_dir = os.path.join(working_dir, "results")
            backup_ins = os.path.join(results_dir, f"Run{resume_from_run}.ins")

            if os.path.exists(backup_ins):
                try:
                    shutil.copy(backup_ins, ins_file)
                    print(f"Resuming analysis. Restored .ins file from: {backup_ins}")
                except Exception as e:
                    print(f"Error restoring backup file: {e}")
                    return False
            else:
                print(
                    f"Error: Backup file for Run {resume_from_run} not found at {backup_ins}"
                )
                return False
        elif not os.path.exists(ins_file):
            print(f"Error: Input file '{ins_file}' not found.")
            return False

        # Read initial .ins content
        try:
            with open(ins_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading .ins file: {e}")
            return False

        results_summary = []

        # Lists for real-time plotting
        plot_x = []
        plot_y = []

        for idx, run_data in enumerate(runs):
            run_number = idx + 1

            # Skip if resuming
            if resume_from_run is not None:
                try:
                    if run_number <= int(resume_from_run):
                        continue
                except ValueError:
                    print(
                        f"Warning: Invalid resume_from_run value '{resume_from_run}'. Ignoring."
                    )

            if not real_time_plot:
                print(f"Starting Run {run_number}...")

            # Update lines with flags from CSV
            updated_lines = self._update_ins_with_flags(lines, run_data)

            # Write updated .ins file
            try:
                with open(ins_file, "w", encoding="utf-8") as f:
                    f.writelines(updated_lines)
            except Exception as e:
                print(f"Error writing .ins file for Run {run_number}: {e}")
                self._save_summary(results_summary, ins_file, fieldnames)
                return False

            # Update Linear Constraints if present
            linear_constraints_str = run_data.get("Linear_constraints", "").strip()
            if linear_constraints_str:
                try:
                    constraints_list = self._split_constraints(linear_constraints_str)
                    parser = InsParser(ins_file)
                    parser.set_linear_constraints(constraints_list)
                    parser.save(ins_file)
                except Exception as e:
                    print(f"Error updating linear constraints: {e}")
                    self._save_summary(results_summary, ins_file, fieldnames)
                    return False

            # Backup the .ins file before running RIETAN
            working_dir = os.path.dirname(os.path.abspath(ins_file))
            results_dir = os.path.join(working_dir, "results")
            os.makedirs(results_dir, exist_ok=True)

            backup_ins = os.path.join(results_dir, f"Run{run_number}.ins")
            try:
                shutil.copy(ins_file, backup_ins)
                if not real_time_plot:
                    print(f"Backed up .ins file to: {backup_ins}")
            except Exception as e:
                print(f"Warning: Failed to backup .ins file: {e}")

            # Run RIETAN
            success = self.engine.run(ins_file)
            if not success:
                print(f"Run {run_number} failed.")
                self._save_summary(results_summary, ins_file, fieldnames)
                return False

            # Parse and print Rwp
            lst_file = os.path.splitext(ins_file)[0] + ".lst"

            # Backup .lst file
            backup_lst = os.path.join(results_dir, f"Run{run_number}.lst")
            try:
                shutil.copy(lst_file, backup_lst)
            except Exception as e:
                print(f"Warning: Failed to backup .lst file: {e}")

            res = ResultParser.parse_lst(lst_file)
            if res and "Rwp" in res:
                res["Run_number"] = run_number
                results_summary.append(res)

                if real_time_plot:
                    try:
                        plot_x.append(run_number)
                        plot_y.append(float(res["Rwp"]))

                        clear_output(wait=True)

                        # Create figure with 2 subplots
                        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

                        # Plot 1: Rwp
                        ax1.plot(plot_x, plot_y, marker="o", linestyle="-", color="b")
                        ax1.set_xlabel("Run Number")
                        ax1.set_ylabel("Rwp")
                        ax1.set_title(
                            f"Refinement Progress: {os.path.basename(ins_file)}\nCurrent Run: {run_number}, Rwp: {res['Rwp']}"
                        )
                        ax1.grid(True)
                        ax1.annotate(
                            f"{res['Rwp']}",
                            (run_number, float(res["Rwp"])),
                            textcoords="offset points",
                            xytext=(0, 10),
                            ha="center",
                        )

                        # Plot 2: Profile
                        gpd_file = os.path.splitext(ins_file)[0] + ".gpd"
                        if os.path.exists(gpd_file):
                            try:
                                plotter = Plotter()
                                df = plotter.load_data(gpd_file)

                                ax2.plot(
                                    df["2theta"],
                                    df["I_obs"],
                                    label="Observed",
                                    color="black",
                                    marker="+",
                                    linestyle="None",
                                    markersize=2,
                                )
                                ax2.plot(
                                    df["2theta"],
                                    df["I_calc"],
                                    label="Calculated",
                                    color="red",
                                    linewidth=1,
                                )
                                ax2.plot(
                                    df["2theta"],
                                    df["Residual"],
                                    label="Diff",
                                    color="blue",
                                    linewidth=0.5,
                                )
                                ax2.set_xlabel("2-theta (deg)")
                                ax2.set_ylabel("Intensity")
                                ax2.legend()
                                ax2.set_title("Fitted Profile")
                            except Exception as e:
                                ax2.text(
                                    0.5,
                                    0.5,
                                    f"Error plotting profile: {e}",
                                    ha="center",
                                )
                        else:
                            ax2.text(0.5, 0.5, "GPD file not found", ha="center")

                        plt.tight_layout()
                        plt.show()
                    except Exception as e:
                        print(f"Plotting error: {e}")
                        print(f"Run {run_number} successful. Rwp = {res['Rwp']}")
                else:
                    print(f"Run {run_number} successful. Rwp = {res['Rwp']}")
            else:
                print(f"Run {run_number} failed. R-factors not found in {lst_file}.")
                self._save_summary(results_summary, ins_file, fieldnames)
                return False

            # Reload lines
            try:
                with open(ins_file, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"Error reloading .ins file after Run {run_number}: {e}")
                self._save_summary(results_summary, ins_file, fieldnames)
                return False

        # Save summary
        self._save_summary(results_summary, ins_file, fieldnames)

        if not real_time_plot:
            print("Sequential analysis completed successfully.")
        return True

    def _restore_resume_state(self, output_dir, resume_from, data_files):
        """
        Finds the resume target index and restores the state (.ins, .csv, and .bkg).
        """
        start_index = 0
        previous_ins = None
        current_csv = None
        previous_bkg = None

        # 1. Find the index
        found = False
        for i, data_file in enumerate(data_files):
            base_name = os.path.splitext(os.path.basename(data_file))[0]
            if base_name == resume_from or os.path.basename(data_file) == resume_from:
                start_index = i
                found = True
                break

        if not found:
            print(f"Error: resume_from '{resume_from}' not found in data files.")
            return None, None, None, None

        # 2. Restore state
        resume_base = os.path.splitext(os.path.basename(data_files[start_index]))[0]
        resume_dir = os.path.join(output_dir, resume_base)
        resume_ins = os.path.join(resume_dir, f"{resume_base}.ins")
        resume_csv = os.path.join(resume_dir, f"{resume_base}.csv")
        resume_bkg = os.path.join(resume_dir, f"{resume_base}.bkg")

        if os.path.exists(resume_ins):
            previous_ins = resume_ins
            print(f"Resuming analysis from {resume_base}. Using {resume_ins} as input.")
        else:
            print(
                f"Error: .ins file for resume_from '{resume_base}' not found at {resume_ins}"
            )
            return None, None, None, None

        if os.path.exists(resume_csv):
            current_csv = resume_csv
            print(f"Restored parameter CSV: {current_csv}")

        if os.path.exists(resume_bkg):
            previous_bkg = resume_bkg
            print(f"Restored background file: {previous_bkg}")

        return start_index, previous_ins, current_csv, previous_bkg

    def _prepare_sample_files(
        self,
        sample_dir,
        base_name,
        current_ins_source,
        data_file,
        current_csv,
        current_bkg_source=None,
    ):
        """
        Copies necessary files to the sample directory.
        """
        os.makedirs(sample_dir, exist_ok=True)
        target_ins = os.path.join(sample_dir, f"{base_name}.ins")
        target_int = os.path.join(sample_dir, f"{base_name}.int")
        target_csv = None

        try:
            # Copy .ins if different
            if os.path.abspath(current_ins_source) != os.path.abspath(target_ins):
                shutil.copy(current_ins_source, target_ins)

            # Copy .int
            shutil.copy(data_file, target_int)

            # Copy .csv if exists
            if current_csv and os.path.exists(current_csv):
                target_csv = os.path.join(sample_dir, f"{base_name}.csv")
                if os.path.abspath(current_csv) != os.path.abspath(target_csv):
                    shutil.copy(current_csv, target_csv)

            # Copy .bkg if exists
            if current_bkg_source and os.path.exists(current_bkg_source):
                target_bkg = os.path.join(sample_dir, f"{base_name}.bkg")
                if os.path.abspath(current_bkg_source) != os.path.abspath(target_bkg):
                    shutil.copy(current_bkg_source, target_bkg)
                    print(f"  Copied background file: {current_bkg_source}")

            return target_ins, target_csv
        except Exception as e:
            print(f"  Error copying files: {e}")
            return None, None

    def run_sequential(
        self,
        data_files,
        anchor_ins_files,
        parameter_csv_files=None,
        anchor_bkg_files=None,
        output_dir="sequential_results",
        resume_from=None,
    ):
        """
        Runs sequential refinement on a list of data files.

        Args:
            data_files (list): List of paths to data files (e.g., .int files).
            anchor_ins_files (list): List of paths to available anchor .ins files.
                                     If a file with the same name as the data file exists, it is used.
                                     Otherwise, the result of the previous analysis is used.
            parameter_csv_files (list, optional): List of paths to available parameter CSV files.
                                                  Matching logic is the same as for anchor files.
            anchor_bkg_files (list, optional): List of paths to available anchor .bkg files.
                                               Matching logic is the same as for anchor files.
            output_dir (str): Directory to save results.
            resume_from (str, optional): Filename (with or without extension) to resume analysis from.
        """
        os.makedirs(output_dir, exist_ok=True)
        results_summary = []

        # Create lookup dictionaries
        anchor_map = {
            os.path.splitext(os.path.basename(f))[0]: f for f in anchor_ins_files
        }
        csv_map = {}
        if parameter_csv_files:
            csv_map = {
                os.path.splitext(os.path.basename(f))[0]: f for f in parameter_csv_files
            }
        bkg_map = {}
        if anchor_bkg_files:
            bkg_map = {
                os.path.splitext(os.path.basename(f))[0]: f for f in anchor_bkg_files
            }

        # Previous successful ins file path
        previous_ins = None
        # Previous successful bkg file path
        previous_bkg = None
        # Current CSV file path (stateful)
        current_csv = None
        start_index = 0

        # Determine start index and restore state
        if resume_from:
            (
                start_index,
                previous_ins,
                current_csv,
                previous_bkg,
            ) = self._restore_resume_state(output_dir, resume_from, data_files)
            if start_index is None:
                return

        # Main Processing Loop
        for i in range(start_index, len(data_files)):
            data_file = data_files[i]
            base_name = os.path.splitext(os.path.basename(data_file))[0]

            # Update CSV state
            # If resuming and this is the first step (the resume target itself),
            # we prefer the restored CSV (current_csv) over the one in csv_map
            # to ensure we reproduce/continue the exact state.
            is_resuming_step = resume_from is not None and i == start_index

            if not (is_resuming_step and current_csv):
                if base_name in csv_map:
                    current_csv = csv_map[base_name]

            print(f"Processing {base_name} ({i+1}/{len(data_files)})...")

            # Step 1: Determine Initial .ins and .bkg
            current_ins_source = None
            current_bkg_source = None

            if is_resuming_step:
                # Force use of the restored file
                current_ins_source = previous_ins
                current_bkg_source = previous_bkg
            else:
                # Standard logic: Check Anchor -> Check Previous Result
                if base_name in anchor_map:
                    current_ins_source = anchor_map[base_name]
                    print(f"  Using anchor .ins file: {current_ins_source}")
                elif previous_ins and os.path.exists(previous_ins):
                    current_ins_source = previous_ins
                    print(f"  Using previous result .ins file: {current_ins_source}")

                # Background file logic
                if base_name in bkg_map:
                    current_bkg_source = bkg_map[base_name]
                    print(f"  Using anchor .bkg file: {current_bkg_source}")
                elif previous_bkg and os.path.exists(previous_bkg):
                    current_bkg_source = previous_bkg
                    print(f"  Using previous result .bkg file: {current_bkg_source}")

            if not current_ins_source:
                msg = f"No suitable .ins file found for {base_name}."
                print(f"  Error: {msg}")
                if i == 0:
                    raise FileNotFoundError(
                        f"Anchor file for the first data file '{base_name}' is missing in anchor_ins_files."
                    )
                else:
                    print("  Skipping.")
                    continue

            if not os.path.exists(current_ins_source):
                print(
                    f"  Error: Source .ins file '{current_ins_source}' not found. Skipping."
                )
                continue

            # Determine CSV
            if current_csv:
                print(f"  Using parameter CSV: {current_csv}")

            # Step 2: Prepare Files
            sample_dir = os.path.join(output_dir, base_name)
            target_ins, target_csv = self._prepare_sample_files(
                sample_dir,
                base_name,
                current_ins_source,
                data_file,
                current_csv,
                current_bkg_source,
            )

            if not target_ins:
                continue

            # Step 4: Run Analysis
            if target_csv and os.path.exists(target_csv):
                print(f"  Running multi-step refinement using CSV: {target_csv}")
                success = self.run_single_refinement(target_ins, target_csv)
            else:
                success = self.engine.run(target_ins)

            if success:
                # Step 5: Result Handling
                lst_file = os.path.join(sample_dir, f"{base_name}.lst")
                res = ResultParser.parse_lst(lst_file)
                refined_lattice = ResultParser.parse_lattice_params(lst_file)

                if res:
                    res["Filename"] = base_name
                    if refined_lattice:
                        res.update(refined_lattice)
                    results_summary.append(res)

                # Keep this ins as previous_ins for next iteration
                # RIETAN updates the input .ins file if NUPDT=1.
                # So target_ins should now contain refined parameters.
                previous_ins = target_ins

                # Check for updated .bkg file
                target_bkg = os.path.join(sample_dir, f"{base_name}.bkg")
                if os.path.exists(target_bkg):
                    previous_bkg = target_bkg
                else:
                    # If no bkg file output, maybe we should keep using the old one?
                    # Or maybe RIETAN didn't use it?
                    # If we copied one there, it should still be there.
                    # If we didn't copy one, and RIETAN didn't create one, then previous_bkg becomes None?
                    # Usually if we provide a bkg file, we want to propagate it.
                    # If we copied it, it exists.
                    pass

                # Save intermediate summary
                if results_summary:
                    summary_df = pd.DataFrame(results_summary)
                    summary_path = os.path.join(output_dir, "summary.csv")
                    try:
                        summary_df.to_csv(summary_path, index=False)
                    except Exception as e:
                        print(f"  Warning: Failed to save intermediate summary: {e}")

            else:
                print(f"  Refinement failed for {base_name}.")
                print(
                    f"  Error: Analysis failed for sample '{base_name}'. Aborting sequential process."
                )
                break

        # Save Summary (Final)
        if results_summary:
            summary_df = pd.DataFrame(results_summary)
            summary_path = os.path.join(output_dir, "summary.csv")
            summary_df.to_csv(summary_path, index=False)
            print(f"Sequential analysis completed. Summary saved to {summary_path}")
