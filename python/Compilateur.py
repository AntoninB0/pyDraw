import re
class Pen:
    def __init__(self, name, x, y, color="000000", thickness=3, rotation=0, speed=5):
        self.name = name
        self.positionX = x
        self.positionY = y
        self.color = color
        self.thickness = thickness
        self.rotation = rotation % 360
        self.speed = speed


# Function to read and analyse the file
def compile_pydraw_to_python(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    python_code = []

    # Reading line by line using the right separator
    for line in lines:
        line = line.strip()
        
        # There is no line or no separtor => No code
        if not line or line == ";":
            continue
        
        # From PyDraw to Python

        #Function
        if line.startswith("func"):
            match = re.match(r"func void (\w+)\((.*)\)\s*{", line)
            if match:
                func_name = match.group(1)
                params = match.group(2)
                python_code.append(f"def {func_name}({params}):")
            continue

        # Declaration and variable type
        if re.match(r"(int|float|pen|bool|string) \w+ = .*;", line):
            var_line = re.sub(r";$", "", line)  # Delete separator
            var_line = re.sub(r"int|float|pen|bool|string", "", var_line)  # Delete type declaration (no need in python)
            python_code.append(var_line.strip())
            continue

        # Affectation
        if "=" in line:
            assign_line = line.replace(";", "")
            python_code.append(assign_line)
            continue

        # Increment and decrement
        if "++" in line:
            var_name = line.split("++")[0].strip()
            python_code.append(f"{var_name} += 1")
            continue

        if "--" in line:
            var_name = line.split("--")[0].strip()
            python_code.append(f"{var_name} -= 1")
            continue

        # Conditions
        if line.startswith("if("):
            condition = re.search(r"if\((.*)\)\s*{", line).group(1)
            python_code.append(f"if {condition}:")
            continue
        if line.startswith("elseif("):
            condition = re.search(r"elseif\((.*)\)\s*{", line).group(1)
            python_code.append(f"elif {condition}:")
            continue
        if line.startswith("else"):
            python_code.append("else:")
            continue

        # Loops
        if line.startswith("repeat("):
            match = re.search(r"repeat\((.*)\)", line)
            if match:
                repeat_params = match.group(1).split(",")
                var, condition, increment = repeat_params
                python_code.append(f"while {condition.strip()}:")
                python_code.append(f"    {increment.strip()}")
            continue
        if line.startswith("while("):
            condition = re.search(r"while\((.*)\)\s*{", line).group(1)
            python_code.append(f"while {condition}:")
            continue

        # Loop's Instructions
        if line == "skip;":
            python_code.append("continue")
            continue
        if line == "leave;":
            python_code.append("break")
            continue

        # Add indentation for blocks
        if "{" in line:
            python_code.append("    " + line.replace("{", "").strip())
        elif "}" in line:
            python_code.append("")  # Ligne vide pour séparer les blocs

    # Typing the python code that matchs
    with open(output_file, 'w') as file:
        file.write("\n".join(python_code))

    print(f"Compilation succeeded: the Python code is saved in {output_file}")

        
