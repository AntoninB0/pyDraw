import re

# Tokens definition
TOKENS = {
    "FUNC": r"func void (\w+)\((.*)\)\s*{",
    "VAR_DECL": r"(int|float|pen|bool|string) (\w+) = (.*);",
    "ASSIGNMENT": r"(\w+) = (.*);",
    "INCREMENT": r"(\w+)\+\+;",
    "DECREMENT": r"(\w+)\-\-;",
    "IF": r"if\((.*)\)\s*{",
    "ELSEIF": r"elseif\((.*)\)\s*{",
    "ELSE": r"else\s*{",
    "REPEAT": r"repeat\((.*)\);",
    "WHILE": r"while\((.*)\)\s*{",
    "SKIP": r"skip;",
    "LEAVE": r"leave;"
}

def tokenize_line(line):
    """Identify tokens in a line"""
    for token_name, pattern in TOKENS.items():
        match = re.match(pattern, line)
        if match:
            return token_name, match.groups()
    return None, None

def compile_pydraw_to_python(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    python_code = []

    for line in lines:
        line = line.strip()
        
        # Ignore empty lines or separators
        if not line or line == ";":
            continue

        # Tokenize the line
        token_type, groups = tokenize_line(line)

        # Process each token type
        if token_type == "FUNC":
            func_name, params = groups
            python_code.append(f"def {func_name}({params}):")
        elif token_type == "VAR_DECL":
            _, var_name, value = groups
            python_code.append(f"{var_name.strip()} = {value.strip()}")
        elif token_type == "ASSIGNMENT":
            var_name, value = groups
            python_code.append(f"{var_name.strip()} = {value.strip()}")
        elif token_type == "INCREMENT":
            var_name, = groups
            python_code.append(f"{var_name.strip()} += 1")
        elif token_type == "DECREMENT":
            var_name, = groups
            python_code.append(f"{var_name.strip()} -= 1")
        elif token_type == "IF":
            condition, = groups
            python_code.append(f"if {condition.strip()}:")
        elif token_type == "ELSEIF":
            condition, = groups
            python_code.append(f"elif {condition.strip()}:")
        elif token_type == "ELSE":
            python_code.append("else:")
        elif token_type == "REPEAT":
            params, = groups
            var, condition, increment = map(str.strip, params.split(","))
            python_code.append(f"while {condition}:")
            python_code.append(f"    {increment}")
        elif token_type == "WHILE":
            condition, = groups
            python_code.append(f"while {condition.strip()}:")
        elif token_type == "SKIP":
            python_code.append("continue")
        elif token_type == "LEAVE":
            python_code.append("break")
        elif "{" in line or "}" in line:
            # Add indentation or handle end of blocks
            pass
        else:
            # Unrecognized syntax
            raise ValueError(f"Unrecognized syntax: {line}")

    # Write the Python code to the output file
    with open(output_file, 'w') as file:
        file.write("\n".join(python_code))

    print(f"Compilation succeeded: the Python code is saved in {output_file}")



compile_pydraw_to_python("test.txt", "final.txt")
