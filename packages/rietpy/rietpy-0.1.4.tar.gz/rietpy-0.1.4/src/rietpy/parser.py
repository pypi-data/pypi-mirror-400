import re
import os


class InsParser:
    def __init__(self, file_path=None):
        self.lines = []
        self.params = {}
        if file_path:
            self.read(file_path)

    def save(self, file_path):
        """Saves the current lines to a file."""
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(self.lines)

    def read(self, file_path):
        """Reads an .ins file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Try reading with different encodings
        encodings = ["utf-8", "cp932", "latin-1"]
        content = None

        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    self.lines = f.readlines()
                content = True
                break
            except UnicodeDecodeError:
                continue

        if not content:
            # Fallback with errors='ignore'
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                self.lines = f.readlines()

        self._parse_params()

    def _parse_params(self):
        """Parses parameters from the .ins file."""
        self.params = {}

        # Keywords to ignore (Control structures, etc.)
        ignored_keywords = {
            "Select",
            "case",
            "end",
            "If",
            "else",
            "endif",
            "return",
            "stop",
        }

        i = 0
        while i < len(self.lines):
            line = self.lines[i]
            stripped = line.strip()

            if not stripped:
                i += 1
                continue

            # Rule: Lines starting with # or ! are comments
            if stripped.startswith("#") or stripped.startswith("!"):
                i += 1
                continue

            # Rule: Lines of form "Variable = Value! Comment" are comment lines as a whole
            # If '!' appears before any '#', the line is a comment
            if "!" in line:
                idx_bang = line.find("!")
                idx_hash = line.find("#")
                if idx_hash == -1 or idx_bang < idx_hash:
                    i += 1
                    continue

            # Parse Key = Value
            if "=" in line:
                parts = line.split("=", 1)
                key = parts[0].strip()

                # Check if key is valid (alphanumeric)
                if not key.isalnum():
                    i += 1
                    continue

                remainder = parts[1]

                # Handle inline comments with # or :
                if "#" in remainder:
                    remainder = remainder.split("#")[0]
                if ":" in remainder:
                    remainder = remainder.split(":")[0]

                value = remainder.strip()

                if key and value:
                    self.params[key] = {"value": value, "line_idx": i}

                i += 1
                continue

            # Parse Space-Separated Parameters (e.g., SCALE, SHIFT0, BKGD)
            # Split by whitespace
            parts = stripped.split()
            if not parts:
                i += 1
                continue

            key = parts[0]

            # Check if key is valid identifier and not in ignored list
            if key.isalnum() and key not in ignored_keywords:
                # Remove comments from the line content
                content = stripped
                if "#" in content:
                    content = content.split("#")[0]
                if ":" in content:
                    content = content.split(":")[0]

                # Re-split after comment stripping
                parts = content.split()
                if len(parts) < 2:
                    # Just a keyword? Unlikely to be a parameter we want to parse, or maybe a flag.
                    i += 1
                    continue

                # Special handling for BKGD (Multi-line)
                if key == "BKGD":
                    # Start with current line's values (excluding key)
                    # Actually, let's store the whole value string including continuation
                    value_str = content[len(key) :].strip()

                    # Check next lines for continuation
                    # Continuation lines for BKGD usually start with indentation
                    j = i + 1
                    while j < len(self.lines):
                        next_line = self.lines[j]
                        next_stripped = next_line.strip()
                        if not next_stripped:
                            j += 1
                            continue

                        # If it starts with # or !, it's a comment, maybe break or skip?
                        # Usually parameters are contiguous.
                        if next_stripped.startswith("#") or next_stripped.startswith(
                            "!"
                        ):
                            break

                        # If it looks like a new keyword (start of line, no indent), break
                        # But how to distinguish indent?
                        # In Fapatite.ins: "      23.2694 ..." (6 spaces)
                        # "BKGD ..." (0 spaces)
                        if not next_line.startswith(" ") and not next_line.startswith(
                            "\t"
                        ):
                            break

                        # It is a continuation line
                        # Remove comments
                        next_content = next_stripped
                        if "#" in next_content:
                            next_content = next_content.split("#")[0]

                        value_str += " " + next_content
                        j += 1

                    self.params[key] = {
                        "value": value_str,
                        "line_idx": i,
                    }  # line_idx points to start
                    i = j  # Skip processed lines
                    continue

                else:
                    # Single line parameter
                    # Value is everything after the key
                    # We want to preserve the format if possible, but for parsing value, we just need the string
                    value = content[len(key) :].strip()
                    self.params[key] = {"value": value, "line_idx": i}

            i += 1

    def read_linear_constraints(self):
        """
        Reads linear constraints from the .ins file.
        Returns a list of constraint strings.
        """
        constraints = []
        in_constraints_block = False

        # Find the block
        # Start: "! Linear constraints"
        # End: "}" (usually "} End of linear constraints.")

        # Note: The block is usually inside "If NMODE <> 1 then"

        for line in self.lines:
            stripped = line.strip()

            if "! Linear constraints" in line:
                in_constraints_block = True
                continue

            if in_constraints_block:
                if stripped.startswith("}"):
                    in_constraints_block = False
                    break

                # Skip control structures and comments
                if stripped.lower().startswith("if ") or stripped.lower().startswith(
                    "end if"
                ):
                    continue
                if stripped.startswith("#") or stripped.startswith("!"):
                    continue
                if not stripped:
                    continue

                # Assume it's a constraint
                # Remove inline comments
                content = stripped
                if "#" in content:
                    content = content.split("#")[0].strip()
                if "!" in content:
                    content = content.split("!")[0].strip()

                if content:
                    constraints.append(content)

        return constraints

    def set_linear_constraints(self, constraints):
        """
        Overwrites linear constraints in the .ins file.

        Args:
            constraints (list): List of constraint strings.
        """
        new_lines = []
        in_constraints_block = False
        constraints_written = False

        i = 0
        while i < len(self.lines):
            line = self.lines[i]
            stripped = line.strip()

            if "! Linear constraints" in line:
                new_lines.append(line)
                in_constraints_block = True
                i += 1
                continue

            if in_constraints_block:
                # Check for end of block
                if stripped.startswith("}"):
                    # Write new constraints before closing brace
                    if not constraints_written:
                        for c in constraints:
                            new_lines.append(f"{c}\n")
                        constraints_written = True

                    new_lines.append(line)
                    in_constraints_block = False
                    i += 1
                    continue

                # Keep control structures (If/End If) but discard other content (old constraints/comments)
                # Wait, we should probably keep the "If NMODE <> 1 then" line if it exists immediately after header
                # But "If" might be anywhere.

                # Heuristic: Keep lines starting with "If " or "End If" (case insensitive)
                # Discard everything else (old constraints and comments inside the block)

                if stripped.lower().startswith("if ") or stripped.lower().startswith(
                    "end if"
                ):
                    new_lines.append(line)

                # Skip old constraints and comments
                i += 1
                continue

            new_lines.append(line)
            i += 1

        self.lines = new_lines

    def set_param(self, name, value):
        """
        Updates a parameter value.

        Args:
            name (str): Parameter name (e.g., 'NBEAM', 'SCALE', 'a').
            value (str or int or float): New value.
        """
        # Handle lattice parameters
        if name in ["a", "b", "c", "alpha", "beta", "gamma"]:
            self.set_lattice_params({name: value})
            return

        # Handle SCALE
        if name == "SCALE":
            self.set_scale(value)
            return

        if name in self.params:
            idx = self.params[name]["line_idx"]
            original_line = self.lines[idx]

            # We need to preserve the comment part
            # Split by comment markers
            comment_part = ""
            match = re.search(r"([:!#].*)", original_line)
            if match:
                comment_part = match.group(1)

            # Determine separator
            # Check if '=' exists in the non-comment part
            content_part = original_line
            if match:
                content_part = original_line[: match.start()]

            if "=" in content_part:
                separator = " = "
            else:
                separator = "  "

            # Construct new line
            # Format value: ensure uppercase E for scientific notation
            val_str = str(value)
            if "e" in val_str:
                val_str = val_str.upper()

            new_line = f"{name}{separator}{val_str}"
            if comment_part:
                # Ensure there is a space before the comment if it's not starting with a space
                if not comment_part.startswith(" "):
                    new_line += " " + comment_part
                else:
                    new_line += comment_part
            else:
                new_line += "\n"

            if not new_line.endswith("\n"):
                new_line += "\n"

            self.lines[idx] = new_line
            self.params[name]["value"] = val_str
        else:
            print(
                f"Warning: Parameter '{name}' not found in the file. Adding it is not yet supported."
            )

    def set_scale(self, value):
        """Updates the SCALE parameter."""
        for i, line in enumerate(self.lines):
            stripped = line.strip()
            if stripped.startswith("SCALE"):
                # Check if it uses '='
                if "=" in line:
                    # Use standard set_param logic for '=' lines
                    # But we need to call the internal logic or duplicate it
                    # Let's just update the line manually here

                    # Preserve comments
                    comment_part = ""
                    match = re.search(r"([:!#].*)", line)
                    if match:
                        comment_part = match.group(1)

                    val_str = str(value)
                    if "e" in val_str:
                        val_str = val_str.upper()

                    new_line = f"SCALE = {val_str}"
                    if comment_part:
                        if not comment_part.startswith(" "):
                            new_line += " " + comment_part
                        else:
                            new_line += comment_part
                    else:
                        new_line += "\n"

                    if not new_line.endswith("\n"):
                        new_line += "\n"

                    self.lines[i] = new_line
                    return

                parts = line.split()
                # SCALE value flag
                if len(parts) >= 2:
                    # We assume the second part is the value, and the third is the flag
                    # But wait, parts[0] is 'SCALE', parts[1] is value, parts[2] is flag

                    # Preserve flag if it exists
                    flag = parts[2] if len(parts) > 2 else "1"

                    # Format value
                    val_str = str(value)
                    if "e" in val_str:
                        val_str = val_str.upper()

                    # Reconstruct
                    new_line = f"SCALE  {val_str}  {flag}"

                    # Preserve comments
                    comment_match = re.search(r"([:!#].*)", line)
                    if comment_match:
                        new_line += "  " + comment_match.group(1)

                    new_line += "\n"
                    self.lines[i] = new_line
                    return
        print("Warning: SCALE line not found.")

    def set_lattice_params(self, params):
        """
        Updates lattice parameters in the CELLQ line.

        Args:
            params (dict): Dictionary with keys 'a', 'b', 'c', 'alpha', 'beta', 'gamma'.
        """
        for i, line in enumerate(self.lines):
            if line.strip().startswith("CELLQ"):
                parts = line.split()
                # CELLQ a b c alpha beta gamma Q ID
                # We expect at least 8 parts (CELLQ + 7 values)
                if len(parts) >= 8:
                    # Preserve Q and ID
                    q_val = parts[7]
                    id_val = parts[8] if len(parts) > 8 else ""

                    # Update values if present in params
                    a = params.get("a", parts[1])
                    b = params.get("b", parts[2])
                    c = params.get("c", parts[3])
                    alpha = params.get("alpha", parts[4])
                    beta = params.get("beta", parts[5])
                    gamma = params.get("gamma", parts[6])

                    # Reconstruct line
                    # Use standard formatting
                    new_line = (
                        f"CELLQ  {a}  {b}  {c}  {alpha}  {beta}  {gamma}  {q_val}"
                    )
                    if id_val:
                        new_line += f"  {id_val}"

                    # Preserve comments if any
                    comment_match = re.search(r"([:!#].*)", line)
                    if comment_match:
                        new_line += "  " + comment_match.group(1)

                    new_line += "\n"
                    self.lines[i] = new_line
                    return
        print("Warning: CELLQ line not found.")

    def write(self, file_path):
        """Writes the content to an .ins file."""
        # Use cp932 (Shift-JIS) for Windows compatibility with legacy tools like RIETAN
        # Try LF line endings as RIETAN might be sensitive or expecting Unix style
        with open(file_path, "w", encoding="cp932", newline="\n", errors="ignore") as f:
            f.writelines(self.lines)


class ResultParser:
    @staticmethod
    def parse_lst(lst_file):
        """
        Parses the .lst file to extract R-factors (Rwp, Rp, S, Re) and all refined parameters.

        Args:
            lst_file (str): Path to the .lst output file.

        Returns:
            dict: Dictionary containing Rwp, Rp, S, Re, and other refined parameters, or None if parsing failed.
        """
        if not os.path.exists(lst_file):
            print(f"Error: List file '{lst_file}' not found.")
            return None

        results = {}
        # Regex pattern to match the R-factor line
        # Example: Rwp =  4.724    Rp =  3.888    RR = 20.154    Re =  4.570    S = 1.0336
        r_pattern = re.compile(
            r"Rwp\s*=\s*([\d\.]+)\s+Rp\s*=\s*([\d\.]+).*?Re\s*=\s*([\d\.]+).*?S\s*=\s*([\d\.]+)"
        )

        # Regex for refined parameters table
        # Format: No. Name Value ... Name
        # Example: 58    9.36903       0.00000       9.36903        0   Lattice parameter, a
        # We capture the refined value (3rd column) and the parameter description/name
        param_pattern = re.compile(
            r"^\s*\d+\s+[\d\.E\+\-]+\s+[\d\.E\+\-]+\s+([\d\.E\+\-]+)\s+\d+\s+(.+)$"
        )

        try:
            with open(lst_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            # 1. Parse R-factors (search from end)
            for line in reversed(lines):
                match = r_pattern.search(line)
                if match:
                    results["Rwp"] = float(match.group(1))
                    results["Rp"] = float(match.group(2))
                    results["Re"] = float(match.group(3))
                    results["S"] = float(match.group(4))
                    break

            if not results:
                print("Warning: R-factors not found in the .lst file.")

            # 2. Parse Refined Parameters
            # We scan the whole file. Later values overwrite earlier ones (final cycle).
            # We need to map descriptions to parameter names if possible, or store raw descriptions.

            # Common parameter mapping based on description suffix
            # "Lattice parameter, a" -> "a"
            # "Fractional coordinate, x, Mn" -> "Mn_x" (Need to handle this carefully)
            # "Isotropic atomic displacement parameter, B, Mn" -> "Mn_B"
            # "Background parameter, b 0" -> "BKGD_0"
            # "Scale factor, s, Phase #1" -> "SCALE_1" (or just SCALE if single phase)

            current_atom = None
            cycle_lattice_counts = {}

            for line in lines:
                # Reset lattice parameter counts at the start of each cycle or new result table
                if ("Cycle" in line and "Cycle #" in line) or (
                    "A(old)" in line and "refined" in line.lower()
                ):
                    cycle_lattice_counts = {}

                match = param_pattern.search(line)
                if match:
                    val_str = match.group(1)
                    desc = match.group(2).strip()

                    try:
                        value = float(val_str)
                    except ValueError:
                        continue

                    # Map description to key
                    key = None

                    # 1. Atom Parameters
                    if "Occupancy," in desc:
                        parts = desc.split("Occupancy,")
                        pre_text = parts[0].strip()
                        if pre_text:
                            current_atom = pre_text

                        if current_atom:
                            key = f"{current_atom}_g"

                    elif "Fractional coordinate," in desc:
                        parts = desc.split("Fractional coordinate,")
                        pre_text = parts[0].strip()
                        if pre_text:
                            current_atom = pre_text

                        if len(parts) > 1:
                            axis = parts[1].strip()
                            if current_atom:
                                key = f"{current_atom}_{axis}"

                    elif "Isotropic atomic displacement parameter," in desc:
                        parts = desc.split("Isotropic atomic displacement parameter,")
                        pre_text = parts[0].strip()
                        if pre_text:
                            current_atom = pre_text

                        if len(parts) > 1:
                            param = parts[1].strip()
                            if current_atom:
                                key = f"{current_atom}_{param}"

                    # 2. Global Parameters
                    elif "Lattice parameter," in desc:
                        raw_key = desc.split(",")[-1].strip()

                        # Track occurrences of this parameter in the current cycle
                        cycle_lattice_counts[raw_key] = (
                            cycle_lattice_counts.get(raw_key, 0) + 1
                        )
                        curr_count = cycle_lattice_counts[raw_key]

                        if raw_key == "a":
                            base_key = "A"
                        elif raw_key == "b":
                            base_key = "B"
                        elif raw_key == "c":
                            base_key = "C"
                        elif raw_key == "alpha":
                            base_key = "AL"
                        elif raw_key == "beta":
                            base_key = "BE"
                        elif raw_key == "gamma":
                            base_key = "GA"
                        else:
                            base_key = raw_key

                        if curr_count > 1:
                            key = f"{base_key}_{curr_count}"
                        else:
                            key = base_key

                    elif "Background parameter," in desc:
                        m = re.search(r"b\s*(\d+)", desc)
                        if m:
                            key = f"BKGD_{m.group(1)}"

                    elif "Scale factor," in desc:
                        key = "SCALE"

                    elif "Peak-shift parameter," in desc:
                        raw_key = desc.split(",")[-1].strip()
                        if raw_key == "t0":
                            key = "SHIFT0"
                        else:
                            key = raw_key

                    elif "Shift parameter," in desc:
                        key = desc.split(",")[-1].strip()

                    elif "Surface-roughness parameter," in desc:
                        key = desc.split(",")[-1].strip()

                    elif "Asymmetry parameter," in desc:
                        key = desc.split(",")[-1].strip()

                    elif "Mixing parameter," in desc:
                        key = desc.split(",")[-1].strip()

                    elif "FWHM parameter," in desc:
                        raw_key = desc.split(",")[-1].strip()
                        if raw_key == "u":
                            key = "U"
                        elif raw_key == "v":
                            key = "V"
                        elif raw_key == "w":
                            key = "W"
                        else:
                            key = raw_key

                    elif "Preferred-orientation parameter," in desc:
                        key = desc.split(",")[-1].strip()

                    elif "Anisotropic strain broadening," in desc:
                        key = desc.split(",")[-1].strip()

                    elif "Anisotropic Scherrer broadening," in desc:
                        key = desc.split(",")[-1].strip()

                    elif "Profile parameter," in desc:
                        parts = desc.split(",")
                        if len(parts) >= 2:
                            key = parts[1].strip()

                    if key:
                        results[key] = value

            return results
        except Exception as e:
            print(f"Error parsing .lst file: {e}")
            return None

    @staticmethod
    def parse_lattice_params(lst_file):
        """
        Parses the .lst file to extract refined lattice parameters.

        Args:
            lst_file (str): Path to the .lst output file.

        Returns:
            dict: Dictionary containing a, b, c, alpha, beta, gamma, or None if not found.
        """
        if not os.path.exists(lst_file):
            return None

        params = {}
        # Regex to match lines like:
        # 58    9.36903       0.00000       9.36903        0   Lattice parameter, a
        # We want the 3rd number (Refined value) and the parameter name at the end
        pattern = re.compile(
            r"^\s*\d+\s+[\d\.E\+\-]+\s+[\d\.E\+\-]+\s+([\d\.E\+\-]+)\s+\d+\s+Lattice parameter,\s+(\w+)"
        )

        try:
            with open(lst_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            # Iterate through all lines. Since the file contains multiple cycles,
            # later values will overwrite earlier ones, leaving us with the final refined values.
            for line in lines:
                match = pattern.search(line)
                if match:
                    value = float(match.group(1))
                    name = match.group(2)
                    params[name] = value

            if params:
                return params
            else:
                # Fallback to old method if the new pattern doesn't match
                # (e.g. for different versions of RIETAN)
                target_header = (
                    "a         b         c       alpha      beta      gamma        V"
                )
                for i in range(len(lines) - 1, -1, -1):
                    if target_header in lines[i]:
                        if i + 1 < len(lines):
                            val_line = lines[i + 1].strip()
                            parts = val_line.split()
                            if len(parts) >= 6:
                                params = {
                                    "a": float(parts[0]),
                                    "b": float(parts[1]),
                                    "c": float(parts[2]),
                                    "alpha": float(parts[3]),
                                    "beta": float(parts[4]),
                                    "gamma": float(parts[5]),
                                }
                                if len(parts) >= 7:
                                    params["Volume"] = float(parts[6])
                                return params
                return None

        except Exception as e:
            print(f"Error parsing lattice parameters: {e}")
            return None

    @staticmethod
    def parse_sequential_results(output_dir, parameters=None):
        """
        Parses sequential refinement results from a directory.
        Reads .lst files from subdirectories to extract refined parameters.

        Args:
            output_dir (str): Path to the sequential results directory.
            parameters (list, optional): List of parameter names to extract.
                                         If None, extracts all available parameters found in .lst files.

        Returns:
            dict: Dictionary where keys are parameter names and values are lists of values.
                  Includes 'Filename' as a key.
        """
        if not os.path.exists(output_dir):
            print(f"Error: Directory '{output_dir}' not found.")
            return {}

        results_list = []

        # Iterate over subdirectories in sorted order
        try:
            entries = sorted(os.listdir(output_dir))
        except OSError as e:
            print(f"Error listing directory: {e}")
            return {}

        for entry in entries:
            entry_path = os.path.join(output_dir, entry)
            if os.path.isdir(entry_path):
                # Look for .lst file with same name as dir
                lst_file = os.path.join(entry_path, f"{entry}.lst")
                if os.path.exists(lst_file):
                    res = ResultParser.parse_lst(lst_file)
                    if res:
                        res["Filename"] = entry
                        results_list.append(res)

        if not results_list:
            return {}

        # Determine all keys
        all_keys = set()
        if parameters:
            all_keys.update(parameters)
            all_keys.add("Filename")
        else:
            for r in results_list:
                all_keys.update(r.keys())

        # Convert to dict of lists
        final_dict = {k: [] for k in all_keys}

        for r in results_list:
            for k in all_keys:
                final_dict[k].append(r.get(k, None))

        return final_dict
