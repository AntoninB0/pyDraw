import re

# Lexical analysis: Token definitions
TOKENS = [
    #("FUNC", r"func\s+(int|float|bool|string|pen|void)\s+(\w+)\s*\(\s*((?:\s*(int|float|bool|string|pen)\s+\w+\s*,?\s*)*)\)\s*{"),
    
    ("COMMENT", r"//.*"),  # Single-line comments : take everything after .*
    ("KEYWORD", r"\b(int|float|bool|string|pen|func|void|if|else|elseif|repeat|while|skip|leave|return|cursor|down|up|walk|goTo|jumpTo|func)\b"), #\b...\b check if there is the word ...  
    ("OPERATOR", r"[=+\-*/><!&|]{1,2}"),  # Includes =, ==, !=, &, |, ++, -- because of the 2 in {1,2}, [...] list of element and combination with max 2 charactere
    ("SYMBOL", r"[{}();,]"),  # Specific symbols
    ("NUMBER", r"\b\d+(\.\d+)?\b"),  # Integers and floats
    ("BOOL", r"\b(true|false)\b"),  # Boolean values
    ("STRING", r"\".*?\""),  # String literals
    ("IDENTIFIER", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),  # Variable/function names
    ("WHITESPACE", r"[ \t\n]+"),  # Whitespace (to be ignored)
    ("UNKNOWN", r"."),  # Catch-all for unexpected characters
]

# Function for lexical analysis, read all the code and transform it into tokens
def tokenize(code):
    tokens = [] #empty token list
    while code: #until there is nothing
        match = None
        for token_type, pattern in TOKENS: #Loop over all token patterns (keywords, numbers, operators, etc.) and try to match
            regex = re.compile(pattern)
            match = regex.match(code)
            if match:
                value = match.group(0) # Extract the matched value
                if token_type not in ["WHITESPACE", "COMMENT"]:  # Ignore whitespace and comments
                    tokens.append((token_type, value))
                code = code[len(value):]  # Move forward in the input code
                break
        if not match:
            raise SyntaxError(f"Unexpected character: {code[0]}")
    return tokens

# Parser class for syntactic analysis
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def consume(self, expected_type):
        if self.current >= len(self.tokens):  # Fin des jetons
            raise SyntaxError(f"Unexpected end of tokens, expected {expected_type}")

        token_type, token_value = self.tokens[self.current]
        if token_type == expected_type:
            self.current += 1
            
            print(token_value)

            return token_value
        else:
            print("une fois")
            print(self.tokens)
            print(token_value)
            raise SyntaxError(f"Expected {expected_type} but got {token_type}: {token_value}")


    def parse_variable_declaration(self):
        var_type = self.consume("KEYWORD")  # Type (int, float, pen, etc.)
        name = self.consume("IDENTIFIER")  # Variable name
        if var_type == "pen":  # Special case for pen
            self.consume("OPERATOR")  # Assignment operator '='
            self.consume("KEYWORD")  # 'cursor'
            self.consume("SYMBOL")  # '('
            x = self.consume("NUMBER")  # x position
            self.consume("SYMBOL")  # ','
            y = self.consume("NUMBER")  # y position
            self.consume("SYMBOL")  # ')'
            self.consume("SYMBOL")  # Semicolon ';'
            return {"type": "pen_decl", "name": name, "x": x, "y": y}
        else:
            self.consume("OPERATOR")  # Assignment operator '='
            value = self.parse_expression()  # Parse the expression
            self.consume("SYMBOL")  # Semicolon ';'
            return {"type": "var_decl", "var_type": var_type, "name": name, "value": value}

    def parse_pen_method(self, pen_name):
        method = self.consume("KEYWORD")  # Method name (e.g., up, down, walk, etc.)
        if method in ["up", "down"]:
            self.consume("SYMBOL")  # '('
            self.consume("SYMBOL")  # ')'
            self.consume("SYMBOL")  # ';'
            return {"type": "pen_method", "name": pen_name,  "method": method}
        elif method in ["walk", "goTo", "jumpTo"]:
            self.consume("SYMBOL")  # '('
            if method == "walk":
                distance = self.consume("NUMBER")
                self.consume("SYMBOL")  # ')'
                self.consume("SYMBOL")  # ';'
                return {"type": "pen_method", "name": pen_name, "method": method, "params": [distance]}
            else:
                x = self.consume("NUMBER")
                self.consume("SYMBOL")  # ','
                y = self.consume("NUMBER")
                self.consume("SYMBOL")  # ')'
                self.consume("SYMBOL")  # ';'
                return {"type": "pen_method", "name": pen_name, "method": method, "params": [x, y]}
            
            
    def parse_function_call(self, func_name):
        self.consume("SYMBOL")  # '('
        args = []
        while self.tokens[self.current][1] != ")":
            args.append(self.parse_expression())
            if self.tokens[self.current][1] == "," :    #or self.tokens[self.current][1] == ";":
                self.consume("SYMBOL")  # Consume ','      or ';'
        self.consume("SYMBOL")  # ')'
        return {"type": "function_call", "name": func_name, "args": args}

    def parse_function(self):
        self.consume("KEYWORD")  # 'func'
        return_type = self.consume("KEYWORD")
        name = self.consume("IDENTIFIER")
        self.consume("SYMBOL")  # '('

        params = []
        while self.tokens[self.current][1] != ")":
            param_type = self.consume("KEYWORD")
            param_name = self.consume("IDENTIFIER")
            params.append((param_type, param_name))
            if self.tokens[self.current][1] == ",":
                self.consume("SYMBOL")  # Consume ','

        self.consume("SYMBOL")  # ')'
        self.consume("SYMBOL")  # '{'

        body = []
        while self.tokens[self.current][1] != "}":
            body.append(self.parse_statement())
        
        self.consume("SYMBOL")  # '}'

        return {
            "type": "function",
            "return_type": return_type,
            "name": name,
            "params": params,
            "body": body
        }

    def parse_repeat(self):
        self.consume("KEYWORD")  # 'repeat'
        self.consume("SYMBOL")  # '('
        init = self.parse_expression()
        self.consume("SYMBOL")  # ','
        condition = self.parse_expression()
        self.consume("SYMBOL")  # ','
        increment = self.parse_expression()
        self.consume("SYMBOL")  # ')'
        self.consume("SYMBOL")  # '{'

        body = []
        while self.tokens[self.current][1] != "}":
            body.append(self.parse_statement())
        
        self.consume("SYMBOL")  # '}'

        return {
            "type": "repeat",
            "init": init,
            "condition": condition,
            "increment": increment,
            "body": body
        }


    
    def parse_statement(self):
        """
        Parse a single statement in the code. Handles variable declarations, method calls, and return statements.
        """
        token_type, token_value = self.tokens[self.current]

        # Handle variable declarations like `int x = 5;`
        if token_type == "KEYWORD" and token_value in ["int", "float", "pen"]:
            return self.parse_variable_declaration()

        # Handle method calls like `pen_name.move(10, 20);`
        elif token_type == "IDENTIFIER":
            pen_name = self.consume("IDENTIFIER")
            return self.parse_pen_method(pen_name)

        # Handle return statements like `return x;`
        elif token_type == "KEYWORD" and token_value == "return":
            self.consume("KEYWORD")  # Consume 'return'
            value = self.parse_expression()  # Parse the returned expression
            self.consume("SYMBOL")  # Consume the ';'
            return {"type": "return", "value": value}
        
        elif token_type == "KEYWORD" and token_value in ["repeat"]:
            return self.parse_repeat()

        elif token_type == "KEYWORD" and token_value in ["if", "else","elseif"]:
            print('ici')
            value = self.parse_expression()  # Parse the returned expression
            self.consume("SYMBOL")  # Consume the ';'
            return {"type": "return", "value": value}
        



        elif token_type == "IDENTIFIER":  # Could be a variable or function call
            name = self.consume("IDENTIFIER")
            if self.tokens[self.current][1] == "(":
                return self.parse_function_call(name)
            else:
                raise SyntaxError(f"Unexpected identifier usage: {name}")
        

        # If no valid statement type is found, raise an error
        else:
            raise SyntaxError(f"Unexpected token in statement: {token_value}")

    def parse_expression(self):
        """
        Parse an expression (e.g., 'a + b', '5', etc.).
        """
        token_type, token_value = self.tokens[self.current]
        
        # Basic example: Parse an identifier or number
        if token_type in ["IDENTIFIER", "NUMBER"]:
            self.current += 1
            left = token_value

            # Check for an operator (e.g., '+', '-', etc.)
            if self.current < len(self.tokens):
                token_type, token_value = self.tokens[self.current]
                if token_type == "OPERATOR":
                    self.current += 1
                    operator = token_value
                    right = self.parse_expression()  # Recursively parse the right-hand side
                    return f"{left} {operator} {right}"
            return left
        else:
            raise SyntaxError(f"Unexpected token in expression: {token_value}")


    def parse(self):
        ast = []
        while self.current < len(self.tokens):
            token_type, token_value = self.tokens[self.current]
            
            if token_type == "KEYWORD" and token_value == "func":
                
                ast.append(self.parse_function())
                print("iciiiiii")
            else:
                raise SyntaxError(f"Unexpected token: {self.tokens[self.current]}")
        return ast

# Code generation for C
def generate_c_code(ast):
    """
    Generate C code from the given Abstract Syntax Tree (AST).
    """
    
    c_code = []
    for node in ast:
        if node["type"] == "var_decl":
            c_code.append(f"{node['var_type']} {node['name']} = {node['value']};")
        elif node["type"] == "pen_decl":
            c_code.append(f"Pen {node['name']} = createPen({node['x']}, {node['y']});")
        elif node["type"] == "pen_method":
            params = ", ".join(node.get("params", []))
            c_code.append(f"{node['name']}.{node['method']}({params});")
        elif node["type"] == "function":
            params = ", ".join([f"{ptype} {pname}" for ptype, pname in node.get("params", [])])
            body = "\n".join([f"    {line}" for line in generate_c_code(node.get("body", [])).split("\n")])
            c_code.append(f"{node['return_type']} {node['name']}({params}) {{\n{body}\n}}")
        elif node["type"] == "return":
            c_code.append(f"return {node['value']};")
        else:
            raise ValueError(f"Unknown AST node type: {node['type']}")

    return "\n".join(c_code)

# Main function to run the compiler
def main(input_file, output_file):
    try:
        pydraw_code = read_file(input_file)
        tokens = tokenize(pydraw_code)
        parser = Parser(tokens)
        
        ast = parser.parse()
        c_code = generate_c_code(ast)

        # ajout de c_codeINIT = ["#include <stdio.h>","#include <stdlib.h>"] à c_code


        write_file(output_file, c_code)
        print(f"Compilation successful! C code has been generated in {output_file}.")
    except Exception as e:
        print(f"Error: {e}")

# Utility functions
def read_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def write_file(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main("test.txt", "output.c")
