import re
import os

# Default installation directory for RIETAN-FP on Windows
DEFAULT_RIETAN_DIR_WIN = r"C:\Program Files\RIETAN_VENUS"

# List of parameter keywords supported for flag toggling
# Includes regex patterns for indexed parameters
SUPPORTED_KEYWORDS = [
    "SHIFT0",
    "SHIFTN",
    "ROUGH",
    "SCALE",
    "GAUSS[0-9]+",
    "LORENTZ[0-9]+",
    "ASYM[0-9]+",
    "ANISTR[0-9]+",
    "FWHM[0-9]+",
    "ETA[0-9]+",
    "DECAY[0-9]+",
    "ANISOBR[0-9]+",
    "M[0-9]+",
    "PREF",
    "CELLQ",
]

# Regex pattern to identify parameter lines in .ins files
# Captures:
# Group 1: Leading whitespace
# Group 2: Keyword (Parameter Name) including optional @Suffix
# Group 3: Middle content (values)
# Group 4: Flags (0s and 1s)
# Group 5: Trailing whitespace (if any, usually captured in group 4 or separate)
KEYWORD_PATTERN = re.compile(
    r"^(\s*)((?:"
    + "|".join(SUPPORTED_KEYWORDS)
    + r")(?:@[A-Za-z0-9]+)?)(\s+.*?\s)([012]+)(\s*)$"
)

# Regex pattern to identify BKGD flags (12 digits of 0 or 1)
# Captures:
# Group 1: Leading whitespace
# Group 2: The 12 flags
# Group 3: Trailing whitespace
BKGD_PATTERN = re.compile(r"(\s)([01]{12})(\s*)$")

# Regex pattern for structure parameters
# Captures:
# Group 1: Leading whitespace
# Group 2: Label/Species (e.g. Ti1/Ti or M1@N/Fe3+)
# Group 3: Middle content (coords etc)
# Group 4: IDs (5 or 6 digits)
# Group 5: Trailing whitespace
STRUCTURE_PATTERN = re.compile(
    r"^(\s*)([A-Za-z0-9]+(?:@[A-Za-z0-9]+)?/[A-Za-z0-9+\-]+)(\s+.*?\s)([012]{5,6})(\s*)$"
)
