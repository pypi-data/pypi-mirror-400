import subprocess
import os
import shutil
import re
from .constants import DEFAULT_RIETAN_DIR_WIN


class RietanEngine:
    def __init__(self, rietan_path="RIETAN", cif2ins_path="cif2ins"):
        """
        Initialize the Rietan engine.

        Args:
            rietan_path (str): Path to the RIETAN executable.
            cif2ins_path (str): Path to the cif2ins executable.
        """
        self.rietan_path = self._resolve_executable(rietan_path)
        self.cif2ins_path = self._resolve_executable(cif2ins_path)

    def _resolve_executable(self, exe_name):
        """
        Resolves the executable path, checking common locations if not found in PATH.
        """
        resolved = shutil.which(exe_name)
        if resolved:
            return resolved

        # Check common Windows location
        if os.name == "nt":
            candidate = os.path.join(DEFAULT_RIETAN_DIR_WIN, exe_name)
            if not candidate.lower().endswith(".exe"):
                candidate += ".exe"

            if os.path.exists(candidate):
                return candidate

        return exe_name

    def run(self, ins_file):
        """
        Runs RIETAN-FP with the given .ins file.

        Args:
            ins_file (str): Path to the .ins input file.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not os.path.exists(ins_file):
            print(f"Error: Input file '{ins_file}' not found.")
            return False

        ins_file = os.path.abspath(ins_file)
        working_dir = os.path.dirname(ins_file)
        file_name = os.path.basename(ins_file)

        # Ensure 'asfdc' file is present in the working directory
        # RIETAN requires this file for atomic scattering factors
        self._ensure_asfdc(working_dir)

        # Set environment variable for RIETAN if needed
        # Some versions might look for auxiliary files based on this
        env = os.environ.copy()
        rietan_exe = shutil.which(self.rietan_path)
        if rietan_exe:
            rietan_dir = os.path.dirname(os.path.abspath(rietan_exe))
            env["RIETAN"] = rietan_dir
            # Also add to PATH just in case
            env["PATH"] = rietan_dir + os.pathsep + env.get("PATH", "")

        # RIETAN typically expects the filename without extension
        # or handles it. To be safe and standard, we pass the base name without extension.
        # But we must ensure we are passing what it expects.
        # If file_name is "sample.ins", we pass "sample".
        base_name_no_ext = os.path.splitext(file_name)[0]

        # Construct arguments list based on RIETAN.command
        # "$RIETAN/rietan" $sample.ins $sample.int $sample.bkg $sample.itx $sample.hkl $sample.xyz $sample.fos $sample.ffe $sample.fba $sample.ffi $sample.ffo $sample.vesta $sample.plt $sample.gpd $sample.alb $sample.prf $sample.inflip $sample.exp
        extensions = [
            ".ins",
            ".int",
            ".bkg",
            ".itx",
            ".hkl",
            ".xyz",
            ".fos",
            ".ffe",
            ".fba",
            ".ffi",
            ".ffo",
            ".vesta",
            ".plt",
            ".gpd",
            ".alb",
            ".prf",
            ".inflip",
            ".exp",
        ]

        args = [base_name_no_ext + ext for ext in extensions]
        cmd = [self.rietan_path] + args

        print(f"Running RIETAN in {working_dir}...")

        try:
            result = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=True,
                text=True,
                check=True,
                env=env,
            )

            # Write stdout to .lst file
            lst_file = os.path.join(working_dir, base_name_no_ext + ".lst")
            with open(lst_file, "w", encoding="utf-8") as f:
                f.write(result.stdout)

            print("RIETAN execution completed.")
            # print("Standard Output:\n", result.stdout)
            # print("Standard Error:\n", result.stderr)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error running RIETAN: {e}")
            print("Standard Output:\n", e.stdout)
            print("Standard Error:\n", e.stderr)
            return False
        except FileNotFoundError:
            print(f"Error: Executable '{self.rietan_path}' not found.")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

    def _ensure_asfdc(self, target_dir):
        """
        Ensures that the 'asfdc' file exists in the target directory.
        It tries to find it in the directory where the RIETAN executable resides.
        """
        target_path = os.path.join(target_dir, "asfdc")
        if os.path.exists(target_path):
            return

        # Find RIETAN executable path
        rietan_exe = shutil.which(self.rietan_path)
        if not rietan_exe:
            # If not in PATH, maybe it's a direct path
            if os.path.exists(self.rietan_path):
                rietan_exe = self.rietan_path
            else:
                print("Warning: Could not locate RIETAN executable to find 'asfdc'.")
                return

        rietan_dir = os.path.dirname(os.path.abspath(rietan_exe))
        source_path = os.path.join(rietan_dir, "asfdc")

        if os.path.exists(source_path):
            try:
                print(f"Copying 'asfdc' from {source_path} to {target_dir}...")
                shutil.copy(source_path, target_path)
            except Exception as e:
                print(f"Warning: Failed to copy 'asfdc': {e}")
        else:
            print(
                f"Warning: 'asfdc' file not found in {rietan_dir}. RIETAN might fail."
            )

    def run_cif2ins(self, cif_file, template_ins="template.ins"):
        """
        Runs cif2ins to generate .ins file from .cif and template.

        Args:
            cif_file (str): Path to the .cif input file.
            template_ins (str): Path to the template .ins file.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not os.path.exists(cif_file):
            print(f"Error: CIF file '{cif_file}' not found.")
            return False

        cif_file = os.path.abspath(cif_file)
        working_dir = os.path.dirname(cif_file)
        sample_name = os.path.splitext(os.path.basename(cif_file))[0]

        # Check template
        # If template_ins is just a filename, look in working_dir
        # If it's a path, use it.
        if os.path.dirname(template_ins):
            template_path = template_ins
        else:
            template_path = os.path.join(working_dir, template_ins)

        if not os.path.exists(template_path):
            print(f"Error: Template file '{template_path}' not found.")
            return False

        # Check for #std in cif file
        standardize = "0"
        try:
            with open(cif_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                if re.search(r"^\s*#\s*std\s*$", content, re.MULTILINE):
                    standardize = "1"
        except Exception:
            pass

        # Construct command
        # cif2ins [0|1] ${sample}.cif template.ins ${sample}.ins ...

        output_ins = f"{sample_name}.ins"

        # Output filenames
        args = [
            standardize,
            os.path.basename(cif_file),
            os.path.basename(template_path),
            output_ins,
            f"{sample_name}-report.tex",
            f"{sample_name}.pdf",
            f"{sample_name}-struct.pdf",
            f"{sample_name}.lst",
            f"{sample_name}-mscs.pdf",
            f"{sample_name}-density.pdf",
        ]

        cmd = [self.cif2ins_path] + args

        # Set environment variable CIF2INS
        env = os.environ.copy()
        cif2ins_exe = shutil.which(self.cif2ins_path)
        if cif2ins_exe:
            cif2ins_dir = os.path.dirname(os.path.abspath(cif2ins_exe))
            env["CIF2INS"] = cif2ins_dir
            env["PATH"] = cif2ins_dir + os.pathsep + env.get("PATH", "")

        print(f"Running cif2ins in {working_dir}...")

        try:
            # Run without check=True to handle non-zero exit codes
            result = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )

            # Check if output file exists
            output_path = os.path.join(working_dir, output_ins)

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                if result.returncode != 0:
                    print(
                        f"Warning: cif2ins exited with code {result.returncode}, but output file was created."
                    )
                return True
            else:
                print(f"Error: cif2ins failed. Exit code: {result.returncode}")
                print("Standard Output:\n", result.stdout)
                print("Standard Error:\n", result.stderr)
                return False

        except FileNotFoundError:
            print(f"Error: Executable '{self.cif2ins_path}' not found.")
            return False

    def combine_ins_files(self, base_ins, other_ins_list, output_ins):
        """
        Combines multiple .ins files into a single multi-phase .ins file.
        References logic from Combins.command but adapted for standard .ins files.

        Args:
            base_ins (str): Path to the first .ins file (Phase 1).
            other_ins_list (list): List of paths to other .ins files (Phase 2, 3, ...).
            output_ins (str): Path to the output .ins file.
        """
        if not os.path.exists(base_ins):
            print(f"Error: Base file '{base_ins}' not found.")
            return False

        # Read base file
        with open(base_ins, "r", encoding="utf-8", errors="ignore") as f:
            base_lines = f.readlines()

        # Capture Constraint Template (before replacement)
        constr_start = -1
        constr_end = -1
        for i, line in enumerate(base_lines):
            if "! Constraints @N" in line:
                constr_start = i
            if "# End Constraints @N" in line:
                constr_end = i

        constraint_template = []
        if constr_start != -1 and constr_end != -1:
            constraint_template = base_lines[constr_start : constr_end + 1]

        # Replace @N with @1 in base lines
        base_lines = [line.replace("@N", "@1") for line in base_lines]

        # Initialize elements set
        all_elements = set()

        def extract_elements_from_line(line):
            # Extract element symbols (letters), ignoring / and whitespace
            # Standard RIETAN format: Ca P O F /
            return re.findall(r"\b[A-Za-z]+\b", line)

        # Extract from Base
        for i, line in enumerate(base_lines):
            if "! Elements @" in line:
                if i + 1 < len(base_lines):
                    all_elements.update(extract_elements_from_line(base_lines[i + 1]))

        # 1. Extract Global Sections from Base
        # We keep everything up to the end of Phase 1 info, and then append other phases.
        # Actually, we need to insert other phases BEFORE "} End of information about phases."
        # And insert other parameters BEFORE "} End of lines for label/species"

        # Find insertion points
        phase_end_idx = -1
        param_end_idx = -1

        for i, line in enumerate(base_lines):
            if "} End of information about phases" in line:
                phase_end_idx = i
            if "} End of lines for label/species" in line:
                param_end_idx = i

        if phase_end_idx == -1 or param_end_idx == -1:
            print("Error: Could not find block end markers in base .ins file.")
            return False

        # 1. Handle Phase Blocks (Header)
        # Extract blocks from Base
        base_blocks = self._extract_phase_blocks(base_lines)
        if not base_blocks:
            print("Error: No phase blocks found in base file.")
            return False

        # Find start of blocks in base_lines to construct header
        blocks_start_idx = -1
        for i, line in enumerate(base_lines):
            if "Data concerning crystalline phases" in line:
                blocks_start_idx = i + 1
                break

        # Start with Base Header
        final_lines = base_lines[:blocks_start_idx]

        # Add Phase 1 Block (from Base)
        # If multiple blocks, take the 1st one (Phase 1)
        p1_block = self._rename_phase_block(base_blocks[0], 1)
        final_lines.extend(p1_block)
        final_lines.append("\n")

        # Add Other Phase Blocks
        param_blocks = []

        for idx, other_ins in enumerate(other_ins_list):
            phase_num = idx + 2  # Phase 2, 3, ...

            if not os.path.exists(other_ins):
                print(f"Warning: File '{other_ins}' not found. Skipping.")
                continue

            with open(other_ins, "r", encoding="utf-8", errors="ignore") as f:
                other_lines = f.readlines()

            # Replace @N with @{phase_num}
            other_lines = [line.replace("@N", f"@{phase_num}") for line in other_lines]

            # Extract elements
            for i, line in enumerate(other_lines):
                if "! Elements @" in line:
                    if i + 1 < len(other_lines):
                        all_elements.update(
                            extract_elements_from_line(other_lines[i + 1])
                        )

            # Extract Phase Blocks
            other_blocks = self._extract_phase_blocks(other_lines)

            target_block = []
            if len(other_blocks) == 1:
                target_block = other_blocks[0]
            elif len(other_blocks) >= phase_num:
                target_block = other_blocks[phase_num - 1]
            elif len(other_blocks) > 0:
                print(
                    f"Warning: Could not find block for Phase {phase_num} in '{other_ins}'. Using 1st block."
                )
                target_block = other_blocks[0]
            else:
                print(f"Warning: No phase blocks found in '{other_ins}'.")

            if target_block:
                renamed_block = self._rename_phase_block(target_block, phase_num)
                final_lines.extend(renamed_block)
                final_lines.append("\n")

            # Extract Parameter Block
            # Look for SCALE to start phase-dependent params?
            # Or better, look for "Label, A(I)..." block
            par_start = -1
            par_end = -1
            for i, line in enumerate(other_lines):
                if "Label, A(I), and ID(I) now starts here" in line:
                    par_start = i
                if "} End of lines for label/species" in line:
                    par_end = i

            if par_start != -1 and par_end != -1:
                # We need to skip phase-independent data (SHIFT, BKGD)
                # Scan for SCALE to start
                scale_idx = -1
                for k in range(par_start, par_end):
                    if "SCALE" in other_lines[k]:
                        scale_idx = k
                        break

                if scale_idx != -1:
                    # Take from just before SCALE (maybe comment "! Phase #1")
                    # Let's take from scale_idx - 2 (heuristic)
                    # Or just take from scale_idx and prepend a comment
                    raw_params = other_lines[scale_idx:par_end]
                    renamed_params = self._rename_param_block(raw_params, phase_num)

                    # Add a header comment
                    param_blocks.append(f"\n  ! Phase #{phase_num}\n")
                    param_blocks.extend(renamed_params)
                else:
                    print(
                        f"Warning: Could not find SCALE in parameter block of '{other_ins}'."
                    )

        # Close Phase Block Section
        final_lines.append(base_lines[phase_end_idx])  # } End of information...

        # Add Middle Section (from phase_end_idx + 1 to param_end_idx)
        final_lines.extend(base_lines[phase_end_idx + 1 : param_end_idx])

        # Add Param Blocks (Phase 2, 3...)
        final_lines.extend(param_blocks)

        # Add Footer (from param_end_idx to end)
        # Handle Constraints
        if constr_start != -1 and constr_end != -1:
            # Part before constraints (but after params)
            final_lines.extend(base_lines[param_end_idx:constr_start])

            # Add constraints for Phase 1 (from base_lines, which has @N replaced by @1)
            final_lines.extend(base_lines[constr_start : constr_end + 1])

            # Add constraints for Phase 2..N
            total_phases = len(other_ins_list) + 1
            for p in range(2, total_phases + 1):
                # Replace @N with @p in template
                block = [line.replace("@N", f"@{p}") for line in constraint_template]
                final_lines.extend(block)

            # Part after constraints
            final_lines.extend(base_lines[constr_end + 1 :])
        else:
            final_lines.extend(base_lines[param_end_idx:])

        # Update Elements in final_lines
        if all_elements:
            sorted_elements = sorted(list(all_elements))
            # Wrap elements in single quotes
            quoted_elements = [f"'{el}'" for el in sorted_elements]
            new_element_line = "  " + "  ".join(quoted_elements) + " /\n"
            for i, line in enumerate(final_lines):
                if "! Elements @" in line:
                    if i + 1 < len(final_lines):
                        final_lines[i + 1] = new_element_line
                    break

        # Update NPHASE
        total_phases = len(other_ins_list) + 1
        for i, line in enumerate(final_lines):
            if "NPHASE@ =" in line:
                # Replace NPHASE@ = 1 with NPHASE@ = {total_phases}
                final_lines[i] = re.sub(
                    r"(NPHASE@\s*=\s*)1", f"\\g<1>{total_phases}", line
                )
                break

        # Write output
        try:
            with open(output_ins, "w", encoding="utf-8") as f:
                f.writelines(final_lines)
            print(f"Successfully created multi-phase .ins file: {output_ins}")
            return True
        except Exception as e:
            print(f"Error writing output file: {e}")
            return False

    def _extract_phase_blocks(self, lines):
        """
        Extracts individual phase blocks from the header section.
        Returns a list of lists of strings (blocks).
        """
        blocks = []
        current_block = []
        in_block = False

        start_idx = -1
        end_idx = -1
        for i, line in enumerate(lines):
            if "Data concerning crystalline phases" in line:
                start_idx = i
            if "} End of information about phases" in line:
                end_idx = i

        if start_idx == -1 or end_idx == -1:
            return []

        for i in range(start_idx + 1, end_idx):
            line = lines[i]
            # Check for start of block
            # Usually "! Phase @" or "PHNAME"
            if "! Phase @" in line:
                if in_block:
                    # End previous block
                    blocks.append(current_block)
                    current_block = []
                in_block = True
                current_block.append(line)
            elif in_block:
                current_block.append(line)
                # Check for end of block
                if "# End Phase" in line:
                    in_block = False
                    blocks.append(current_block)
                    current_block = []

        # Handle case where last block doesn't have explicit end marker or we are inside one
        if in_block and current_block:
            blocks.append(current_block)

        return blocks

    def _rename_phase_block(self, lines, phase_num):
        """Renames variables in the phase block for the new phase number."""
        new_lines = []
        for line in lines:
            # Skip empty lines or lines that are just comments if desired? No, keep them.

            # Rename PHNAME1 -> PHNAME{n}
            # Regex for variables ending in 1
            # PHNAME, HKLM, LPAIR, INDIV, IHA, IKA, ILA
            # IHP, IKP, ILP are special (vectors)

            # General rule: VAR1 = ... -> VAR{n} = ...
            # But be careful not to match values.

            # Specific replacements
            line = re.sub(r"(PHNAME)1", f"\\g<1>{phase_num}", line)
            line = re.sub(r"(VNS)1", f"\\g<1>{phase_num}", line)
            line = re.sub(r"(HKLM)1", f"\\g<1>{phase_num}", line)
            line = re.sub(r"(LPAIR)1", f"\\g<1>{phase_num}", line)
            line = re.sub(r"(INDIV)1", f"\\g<1>{phase_num}", line)
            line = re.sub(r"(IHA)1", f"\\g<1>{phase_num}", line)
            line = re.sub(r"(IKA)1", f"\\g<1>{phase_num}", line)
            line = re.sub(r"(ILA)1", f"\\g<1>{phase_num}", line)

            # Vectors: IHP1 -> IHP{n}1 (Phase n, Vector 1)
            # Assuming source is Phase 1
            line = re.sub(r"(IHP)([0-9]+)", f"\\g<1>{phase_num}\\g<2>", line)
            line = re.sub(r"(IKP)([0-9]+)", f"\\g<1>{phase_num}\\g<2>", line)
            line = re.sub(r"(ILP)([0-9]+)", f"\\g<1>{phase_num}\\g<2>", line)

            new_lines.append(line)
        return new_lines

    def _rename_param_block(self, lines, phase_num):
        """Renames labels in the parameter block for the new phase number."""
        new_lines = []
        for line in lines:
            # SCALE -> SCALE{n}
            # PREF -> PREF{n}
            # CELLQ -> CELLQ{n}

            # If source is Phase 1, SCALE might be SCALE or SCALE1?
            # In Fapatite.ins, it is SCALE.
            # In Cu3Fe4P6.ins, it is SCALE1.
            # We should handle both.

            # Replace SCALE followed by space or 1
            line = re.sub(r"^(\s*)SCALE1?(\s+)", f"\\g<1>SCALE{phase_num}\\g<2>", line)
            line = re.sub(r"^(\s*)PREF1?(\s+)", f"\\g<1>PREF{phase_num}\\g<2>", line)
            line = re.sub(r"^(\s*)CELLQ1?(\s+)", f"\\g<1>CELLQ{phase_num}\\g<2>", line)

            # Profile parameters: GAUSS01 -> GAUSS01{n}
            # List: GAUSS, LORENTZ, ASYM, ANISTR, FWHM, ETA, ANISOBR, DUMMY, M
            # We match Keyword + Digits
            # If digits end in 1 (Phase 1), replace 1 with n?
            # Or just append n?
            # Cu3Fe4P6: GAUSS01 -> GAUSS012.
            # So we append n.

            keywords = [
                "GAUSS",
                "LORENTZ",
                "ASYM",
                "ANISTR",
                "FWHM",
                "ETA",
                "ANISOBR",
                "DUMMY",
                "M",
            ]
            pattern = r"^(\s*)(" + "|".join(keywords) + r")([0-9]+)(\s+)"

            def repl(m):
                return f"{m.group(1)}{m.group(2)}{m.group(3)}{phase_num}{m.group(4)}"

            line = re.sub(pattern, repl, line)

            # Structure parameters: Label/Species
            # O1/O- -> O1_{n}/O-
            # Regex: ^(\s*)([A-Za-z0-9]+)(/[A-Za-z0-9+\-]+)
            # Exclude keywords

            # Check if it looks like a structure line
            if "/" in line and not line.strip().startswith("!"):
                # Avoid matching comments
                match = re.match(r"^(\s*)([A-Za-z0-9]+)(/[A-Za-z0-9+\-]+)", line)
                if match:
                    label = match.group(2)
                    # Don't rename if it's a keyword (unlikely with /)
                    # Rename label
                    new_label = f"{label}_{phase_num}"
                    line = line.replace(f"{label}/", f"{new_label}/", 1)

            new_lines.append(line)
        return new_lines
