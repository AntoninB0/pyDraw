import re

# Lexical analysis: Token definitions
TOKENS = [
    #("FUNC", r"func\s+(int|float|bool|string|pen|void)\s+(\w+)\s*\(\s*((?:\s*(int|float|bool|string|pen)\s+\w+\s*,?\s*)*)\)\s*{"),
    
    ("COMMENT", r"//.*"),  # Single-line comments : take everything after .*
    ("KEYWORD", r"\b(int|float|bool|string|pen|func|void|if|else|elseif|repeat|while|skip|leave|break|return|cursor|down|up|walk|goTo|jumpTo|rectangle|circle|triangleIso|rotateCW|rotateCCW|func)\b"), #\b...\b check if there is the word ...  
    ("OPERATOR", r"[=+\-*/><!&|]{1,2}"),  # Includes =, ==, !=, &, |, ++, -- because of the 2 in {1,2}, [...] list of element and combination with max 2 charactere
    ("SYMBOL", r"[{}();,.]"),  # Specific symbols
    ("NUMBER", r"\b\d+(\.\d+)?\b"),  # Integers and floats
    ("BOOL", r"\b(true|false)\b"),  # Boolean values
    ("STRING", r"\".*?\""),  # String literals
    ("PEN_ATTRIBUTE",r"\b(color|thickness|positionX|positionY|rotation|speed)\b"),
    ("IDENTIFIER", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),  # Variable/function names
    ("WHITESPACE", r"[ \t\n]+"),  # Whitespace (to be ignored)
    
    #("UNKNOWN", r"."),  # Catch-all for unexpected characters
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
            raise SyntaxError(f"Expected {expected_type} but got {token_type}: {token_value}")

    def parse_variable_declaration(self):
        var_type = self.consume("KEYWORD")  # Type (int, float, pen, etc.)
        name = self.consume("IDENTIFIER")  # Variable name
        self.consume("OPERATOR")  # Assignment operator '='
        
        # Gestion des appels de fonction ou d'expressions
        if self.tokens[self.current][0] == "IDENTIFIER" and self.tokens[self.current + 1][1] == "(":
            value = self.parse_function_call(self.consume("IDENTIFIER"))
        else:
            value = self.parse_expression()  # Parse an expression

        self.consume("SYMBOL")  # Semicolon ';'
        
        # Retourne un AST cohérent
        return {"type": "var_decl", "var_type": var_type, "name": name, "value": value}
    
    def parse_pen_declaration(self):
        print("ici")
        self.consume("KEYWORD")  # Consume the type pen
        print("2")
        name = self.consume("IDENTIFIER")  # name of the pen
        print("3")
        self.consume("OPERATOR")  # Consume "="
        self.consume("KEYWORD")  # Consume "cursor"
        self.consume("SYMBOL")  # Consume "("
        x = self.consume("NUMBER")  # Position X
        self.consume("SYMBOL")  # Consume ","
        y = self.consume("NUMBER")  # Position Y
        self.consume("SYMBOL")  # Consume ")"
        self.consume("SYMBOL")  # Consume ";"
        
        return {"type": "pen_decl", "name": name, "x": x, "y": y}

    def parse_pen_method(self, pen_name):
        self.consume("SYMBOL")  # Consomme le "."
        method = self.consume("KEYWORD")  # Nom de la méthode
        self.consume("SYMBOL")  # Consomme "("
        
        params = []
        if self.tokens[self.current][1] != ")":  # Si la méthode a des paramètres
            params.append(self.parse_expression())  # Analyse le premier paramètre
            while self.tokens[self.current][1] == ",":
                self.consume("SYMBOL")  # Consomme ","
                params.append(self.parse_expression())
        
        self.consume("SYMBOL")  # Consomme ")"

        self.consume("SYMBOL")
        
        return {"type": "method_call", "name": pen_name, "method": method, "params": params}

    """def parse_pen_method(self, pen_name):
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
                return {"type": "pen_method", "name": pen_name, "method": method, "params": [x, y]}    """
            
    def parse_pen_attribute(self, pen_name):
        self.consume("SYMBOL")  # Consume the "."
        attribute = self.consume("PEN_ATTRIBUTE")  # Attribute's name
        self.consume("OPERATOR")
        if attribute in ["rotation","speed","positionY", "positionX","thickness"] :
            value = self.consume("NUMBER")
        elif attribute == "color" :
            value = self.consume("STRING")
        else :
            print("erreur, not an attribute")

        self.consume("SYMBOL")
        return {"type": "pen_attribute", "name": pen_name, "attribute": attribute,"value":value}

    def parse_function_call(self, func_name):
        self.consume("SYMBOL")  # '('
        args = []
        while self.tokens[self.current][1] != ")":
            args.append(self.parse_expression())
            if self.tokens[self.current][1] == ",":
                self.consume("SYMBOL")  # Consume ','
        self.consume("SYMBOL")  # ')'
        if self.tokens[self.current+1][1] == ";":
            self.consume("SYMBOL") # ";"""
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
            body.append(self.parse_statement())  # Correctly parse statements

        self.consume("SYMBOL")  # '}'

        return {
            "type": "function",
            "return_type": return_type,
            "name": name,
            "params": params,
            "body": body
        }

    def parse_repeat(self):
        """
        Parse a 'repeat' loop with the syntax:
        repeat (init_expr, condition_expr, increment_expr) { body }
        """
        self.consume("KEYWORD")  # 'repeat'
        self.consume("SYMBOL")  # '('
        
        # Parse the initialization, condition, and increment
        init = self.parse_expression()
        self.consume("SYMBOL")  # ','
        condition = self.parse_expression()
        self.consume("SYMBOL")  # ','
        increment = self.parse_increment()
        self.consume("SYMBOL")  # ')'
        
        # Parse the loop body
        self.consume("SYMBOL")  # '{'
        body = []
        while self.tokens[self.current][1] != "}":
            body.append(self.parse_statement())
        self.consume("SYMBOL")  # '}'

        # Return the 'repeat' node
        return {
            "type": "repeat",
            "init": init,
            "condition": condition,
            "increment_var": increment["name"],
            "increment_op" : increment["operation"],
            "body": body
        }

    def parse_condition(self):
        if self.consume("KEYWORD") == "if":
            self.consume("SYMBOL")  # '('
            condition = self.parse_expression()
            self.consume("SYMBOL")  # ')'
            self.consume("SYMBOL")  # '{'

            body = []
            while self.tokens[self.current][1] != "}":
                body.append(self.parse_statement())

            self.consume("SYMBOL")  # '}'

            # Initial node for the 'if' statement
            node = {
                "type": "if",
                "condition": condition,
                "body": body,
                "elseif": [],
                "else": None,
            }

            # Handle 'elseif' block if exists
            while self.current < len(self.tokens) and self.tokens[self.current][1] == "elseif":
                self.consume("KEYWORD")  # 'elseif'
                self.consume("SYMBOL")  # '('
                elseif_condition = self.parse_expression()
                self.consume("SYMBOL")  # ')'
                self.consume("SYMBOL")  # '{'

                elseif_body = []
                while self.tokens[self.current][1] != "}":
                    elseif_body.append(self.parse_statement())

                self.consume("SYMBOL")  # '}'
                node["elseif"].append({
                    "condition": elseif_condition,
                    "body": elseif_body
                })

            # Handle 'else' block if exists
            if self.current < len(self.tokens) and self.tokens[self.current][1] == "else":
                self.consume("KEYWORD")  # 'else'
                self.consume("SYMBOL")  # '{'

                else_body = []
                while self.tokens[self.current][1] != "}":
                    else_body.append(self.parse_statement())

                self.consume("SYMBOL")  # '}'
                node["else"] = else_body

            return node

    def parse_condition_methode(self):
        """
        Parse methode like break, leave or skip
        """
        token_type, token_value = self.tokens[self.current]

        if token_type == "KEYWORD":
            methode = self.consume("KEYWORD")  # Consume the methode
            self.consume("SYMBOL")  # Consume the ';' symbol
            return {"type": "methode", "methode": methode}
    
    def parse_increment(self):
        """
        Parse short operations like x++ or x--.
        """
        name = self.consume("IDENTIFIER")  # Get the variable name (e.g., `x`)
        operation = self.consume("OPERATOR")  # Get the operator (e.g., `++` or `--`)
        
        if operation not in ["++", "--"]:
            raise SyntaxError(f"Unexpected increment operation: {operation}")
        
        return {"type": "short_operation", "name": name, "operation": operation}

    def parse_short_operation(self):
        """
        Parse short operations like x++ or x--.
        """
        name = self.consume("IDENTIFIER")  # Get the variable name (e.g., `x`)
        operation = self.consume("OPERATOR")  # Get the operator (e.g., `++` or `--`)
        
        if operation not in ["++", "--"]:
            raise SyntaxError(f"Unexpected operation: {operation}")

        # Ensure a ';' is present after the operation
        self.consume("SYMBOL")  # Consume the `;`

        return {"type": "short_operation", "name": name, "operation": operation}

    def parse_assignment(self):
        """
        Parse an assignment statement like `a = b;`.
        """
        token_type, token_value = self.tokens[self.current]
        next_token_type, next_token_value = self.tokens[self.current + 1]

        if token_type == "IDENTIFIER":
            left = token_value
            self.consume("IDENTIFIER")  # Consume the identifier (variable)

            self.consume("OPERATOR")  # Consume the '=' symbol

            right = self.parse_expression()  # Parse the right-hand side expression

            self.consume("SYMBOL")  # Consume the ';' symbol

            return {"type": "assignment", "left": left, "right": right}

    def parse_expression(self):
        """
        Parse an expression, including binary operations (e.g., 'num * num').
        """
        left = self.parse_term()  # Parse the first operand or term

        while self.current < len(self.tokens):
            token_type, token_value = self.tokens[self.current]

            # Check for an operator
            if token_type == "OPERATOR":
                operator = self.consume("OPERATOR")
                
                right = self.parse_term()

                if operator == "&" :
                    operator = " and "
                elif operator == "|" :
                    operator = " or "
                    
                left = f"{left} {operator} {right}"  # Combine into a valid expression
            else:
                break

        return left

    def parse_term(self):
        """
        Parse a single term, such as a variable, number, or parenthesized expression.
        """
        token_type, token_value = self.tokens[self.current]

        if token_type == "IDENTIFIER" or token_type == "NUMBER":
            self.current += 1
            return token_value
        elif token_value == "(":  # Handle parenthesized expressions
            self.consume("SYMBOL")  # Consume '('
            expr = self.parse_expression()
            self.consume("SYMBOL")  # Consume ')'
            return f"({expr})"
        else:
            raise SyntaxError(f"Unexpected token in term: {token_value}")
    
    def parse_statement(self):
        """
        Parse a single statement in the code. Handles variable declarations, method calls, 
        return statements, loops, and now function definitions.
        """
        token_type, token_value = self.tokens[self.current]
        next_token_type, next_token_value = self.tokens[self.current + 1]

        # Handle function definitions
        if token_type == "KEYWORD" and token_value == "func":
            return self.parse_function()
        # Handle pen declarations
        elif token_type == "KEYWORD" and token_value == "pen":
            return self.parse_pen_declaration()

        # Handle pen methods (e.g., pen1.walk(50);)
        elif token_type == "IDENTIFIER" and next_token_type == "SYMBOL" and next_token_value == ".":  # Check for `pen1.<something>`
            pen_name = self.consume("IDENTIFIER")
            next_next_token_type, next_next_token_value = self.tokens[self.current + 1]
            if next_next_token_type == "PEN_ATTRIBUTE" :
                return self.parse_pen_attribute(pen_name)
            else :
                return self.parse_pen_method(pen_name)
        

        # Handle variable declarations like `int x = 5;`
        elif token_type == "KEYWORD" and token_value in ["int", "float", "bool", "string"]:
            return self.parse_variable_declaration()

        # Handle return statements like `return x;`
        elif token_type == "KEYWORD" and token_value == "return":
            self.consume("KEYWORD")  # Consume 'return'
            value = self.parse_expression()  # Parse the returned expression
            self.consume("SYMBOL")  # Consume the ';'
            return {"type": "return", "value": value}

        # Handle repeat loops
        elif token_type == "KEYWORD" and token_value == "repeat":
            return self.parse_repeat()

        # Handle conditons : if, else, elseif
        elif token_type == "KEYWORD" and token_value == "if" :
            return self.parse_condition()
        
        # Handle leave, skip and break
        elif token_type == "KEYWORD" and (token_value == "skip" or token_value == "leave" or token_value == "break"):
            return self.parse_condition_methode()


        # Handle short operation with ++ or --
        elif token_type == "IDENTIFIER":
            # Peek at the next token to check for ++ or --
            if self.tokens[self.current + 1][1] in ["++", "--"]:
                return self.parse_short_operation()
            else:
                return self.parse_assignment()
        # If no valid statement type is found, raise an error
        else:
            raise SyntaxError(f"Unexpected token in statement: {token_type} {token_value}")
    
    def parse(self):
        ast = []
        print(ast)
        while self.current < len(self.tokens):
            print(f"Parsing statement starting at token {self.current}")  # Debug log
            try:
                statement = self.parse_statement()
                ast.append(statement)
                #print(ast)
                
            except SyntaxError as e:
                
                raise SyntaxError(f"Error parsing statement at token {self.current}: {e}")

        #print("AST generated:", ast)  # Debug log for the final AST
        return ast






# Code generation for C
def generate_c_code(ast):
    """
    Generate C code from the given Abstract Syntax Tree (AST).
    """
    c_code = []
    print(ast)
    for node in ast:
        if node["type"] == "var_decl":
            value = generate_c_code([node["value"]]) if isinstance(node["value"], dict) else node["value"]
            c_code.append(f"{node['var_type']} {node['name']} = {value};")
        elif node["type"] == "pen_decl":
            c_code.append(f"Pen {node['name']} = createPen({node['x']}, {node['y']});")
        elif node["type"] == "pen_method":
            params = ", ".join(map(str, node.get("params", [])))
            c_code.append(f"{node['name']}.{node['method']}({params});")
        elif node["type"] == "function_call":
            args = ", ".join(node["args"])
            c_code.append(f"{node['name']}({args})")
        elif node["type"] == "function":
            params = ", ".join([f"{ptype} {pname}" for ptype, pname in node.get("params", [])])
            body = "".join([f"{line}" for line in generate_c_code(node.get("body", [])).split("\n")])
            c_code.append(f"{node['return_type']} {node['name']}({params}) {{\n{body}\n}}")
        elif node["type"] == "return":
            c_code.append(f"return {node['value']};")
            # Handle assignments
        elif node["type"] == "assignment":
            left = node["left"]
            right = node["right"]
            c_code.append(f"{left} = {right};")
        #handle methode
        elif node["type"] == "methode":
            methode = node["methode"]
            c_code.append(f"{methode};")
        # handle short operator
        elif node["type"] == "short_operation":
            operation = node["operation"]
            name = node["name"]
            c_code.append(f"{name} {operation};")
        # Handle repeat
        elif node["type"] == "repeat":
            init = node["init"]
            condition = node["condition"]
            increment_var = node["increment_var"]
            increment_op = node["increment_op"]
            body = "".join([f"{line}" for line in generate_c_code(node["body"])])
            c_code.append(f"for ({init},{condition}, {increment_var} {increment_op}) {{\n{body}\n}}")
        # Handle conditions (if, else, elseif)
        elif node["type"] == "if":
            condition = node["condition"]
            body = "".join([f"{line}" for line in generate_c_code(node["body"])])
            c_code.append(f"if ({condition}) {{\n{body}\n}}")
            
            # Handle else if
            if node.get("elseif"):
                for elif_block in node["elseif"]:
                    elif_condition = elif_block["condition"]
                    elif_body = "".join([f"{line}" for line in generate_c_code(elif_block["body"])])
                    c_code.append(f"else if ({elif_condition}) {{\n{elif_body}\n}}")
            
            # Handle else block
            if node.get("else"):
                else_body = "".join([f"{line}" for line in generate_c_code(node["else"])])
                c_code.append(f"else {{\n{else_body}\n}}")
        #Handle pen's creation
        elif node["type"] == "pen_decl":
            c_code.append(f"Pen {node['name']} = createPen({node['x']}, {node['y']});")
        # Handle pen's attribute
        elif node["type"] == "pen_attribute":
            c_code.append(f"{node['name']}.{node['attribute']} = {node['value']};")
        # Handle pen's method
        elif node["type"] == "method_call":
            if len(node["params"])>1:
                params = ", ".join(map(str, node["params"]))  # Liste des paramètres
            else :
                params = "".join(map(str, node["params"]))
            c_code.append(f"{node['method']}({node['name']},{params});")


        else:
            raise ValueError(f"Unknown AST node type: {node['type']};")

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




