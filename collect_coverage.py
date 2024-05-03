#!/usr/bin/env python3
from pathlib import Path
import re
import sys

# This script goes through all *.c files in this directory (and recursively through subdirectories)
# and finds the following pattern
# ```
# // [[openmac-coverage:implemented]]
# void ic_mac_init_openmac() {
#     // taken from libpp/hal_mac.o hal_mac_init
#     IC_MAC_INIT_REGISTER &= 0xffffe800;
# }
# ```
# and then outputs
# ic_mac_init_openmac:implementend
# on stdout


# Regex to find C function declarations
# I know you can't really parse C source code with a regex, but it seems to work for this limited usecase
FUNCTION_REGEX = r'^\s*(?:(?:inline|static)\s+){0,2}(?!else|typedef|return)\w+\**\s+\*?\s*(\w+)\s*\([^0;\)]*?\)\s*[;{]$'

OPENMAC_COVERAGE_REGEX = r'\[\[openmac-coverage:(\w+)\]\]'

def find_opensource_functions(path):
    with open(path) as infile:
        next_line_attribute = None
        for idx, line in enumerate(infile):
            line = line.strip()
            if (match := re.search(OPENMAC_COVERAGE_REGEX, line)) is not None:
                next_line_attribute = match[1]
            elif next_line_attribute is not None:
                match = re.match(FUNCTION_REGEX, line)
                if match is None:
                    print(f'no function match found in {path}:{idx+1} "{line}"', file=sys.stderr)
                else:
                    print(f'{match[1]}:{next_line_attribute}')
                next_line_attribute = None

file_list = [f for f in Path('.').glob('**/*.c') if f.is_file()]
for filename in file_list:
    find_opensource_functions(filename)