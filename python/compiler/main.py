import re

# Define token types for lexical analysis
TOKENS = [
    ("COMMENT", r"//.*"),  # Single-line comments
    ("KEYWORD", r"\b(int|float|bool|string|pen|func|void|if|else|elseif|repeat|while|wait|skip|leave|break|return|cursor|walk|goTo|circle|fillColor|compareSDLColors|approxPosX|approxPosY|approxPos|float2Rad|pixelColor|circleWrite|clearMatrix|rotateArea|copyPaste|copy|paste|cut|translation|waitKey|closeEventSDL|renderMatrix|initSDL)\b"),  # Recognized keywords
    ("NUMBER", r"-?\b\d+(\.\d+)?\b"),  # Handles negative and positive, integer and decimal numbers
    ("OPERATOR", r"[=+\-*/><!&|]{1,2}"),  # Operators include arithmetic, logical, and comparison
    ("SYMBOL", r"[{}();,.]"),  # Punctuation symbols used for syntax
    ("BOOL", r"\b(true|false)\b"),  # Boolean values
    ("STRING", r"\".*?\""),  # String literals enclosed in double quotes
    ("PEN_ATTRIBUTE", r"\b(color|thickness|positionX|positionY|rotation|penDown)\b"),  # Attributes specific to 'pen' objects
    ("IDENTIFIER", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),  # Identifiers (variable/function names)
    ("WHITESPACE", r"[ \t\n]+"),  # Whitespace characters (space, tab, newline)
]
# Pattern pour identifier
identifier_pattern = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b")

# Pattern pour identifier une expression :
expression_pattern = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b|[-+]?\b\d*\.?\d+\b|[+\-*/()]")
# Pattern pour number
number_pattern = re.compile(r"-?\b\d+(\.\d+)?\b")
def tokenize(code):
    tokens = []
    line_number = 1  # Starting line number
    current_index = 0  # Starting index in the code string

    # Tokenization process
    while current_index < len(code):
        match = None
        for token_type, pattern in TOKENS:
            regex = re.compile(pattern)
            match = regex.match(code, current_index)
            if match:
                value = match.group(0)
                newlines = value.count('\n')
                if token_type not in ["WHITESPACE", "COMMENT"]:
                    tokens.append((token_type, value, line_number))
                line_number += newlines
                current_index += len(value)
                break
        if not match:
            raise SyntaxError(f"Unexpected character '{code[current_index]}' at line {line_number}")

    return tokens

# Custom exception for syntax errors that includes line number
class SyntaxErrorWithLine(Exception):
    def __init__(self, line, message):
        super().__init__(message)
        self.line = line
        self.message = message

    def __str__(self):
        return f"Line {self.line}: {self.message}"

# Parser class to handle syntax analysis
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.variables = {}
        self.functions = {}  
        self.functions_vars = {}  
        self.func_vars = 0
        self.func_use = ""

    def find_variable_type(self, name):
        
        if self.func_vars :
            if name in self.functions_vars:
                if self.functions_vars[name] == "pen":
                    return "int"
                return self.functions_vars[name]
            raise Exception(f"Variable '{name}' not declared.")
        else :
            if name in self.variables:
                
                if self.variables[name] == "pen":
                    return "int"
                return self.variables[name]
            raise Exception(f"Variable '{name}' not declared.")
        
    def find_variable(self, name):
        if self.func_vars :
            if name in self.functions_vars:
                return name
            raise Exception(f"Variable '{name}' not declared.")
        else :
            if name in self.variables:
                return name
            raise Exception(f"Variable '{name}' not declared.")
    
    def is_variable_declared(self, name):
        """Check if a variable is declared in the current or any outer scope."""
        
        if self.func_vars :
            
            if name in self.functions_vars:
                
                return True
            else :
                return False
        else :
            if name in self.variables:
                return True
            else :
                return False
    
    def is_function_declared(self, name):
        """Check if a function is declared in the current or any outer scope."""

        if name in self.functions:
            
            return True
        else :
            return False

    def declare_variable(self, name, var_type):
        """Declare a new variable in the current scope."""
        if self.func_vars :
            if name in self.functions_vars:
                raise SyntaxErrorWithLine(self.get_line(), f"Variable '{name}' already declared in this scope.")
            self.functions_vars[name] = var_type
        else :
            if name in self.variables:
                raise SyntaxErrorWithLine(self.get_line(), f"Variable '{name}' already declared in this scope.")
            self.variables[name] = var_type

    def get_expression_type(self, expr, expected_type):
        code = tokenize(expr)
        i = 0  # Utilisez un index pour parcourir la liste de tokens
        while i < len(code):
            token = code[i]
            if token[0] == "IDENTIFIER":
                # Vérifiez si le token suivant est une parenthèse ouvrante, indiquant un appel de fonction
                if i + 1 < len(code) and code[i + 1][1] == "|":
                    i += 1  # Avancez à la parenthèse ouvrante
                    # Avancez dans les tokens jusqu'à trouver la parenthèse fermante correspondante
                    while i < len(code) and code[i][1] != "|":
                        i += 1
                    func = self.find_function(token)
                    var_type = func["return_type"]
                    
                elif i + 1 < len(code) and code[i + 1][1] == ".":
                    
                    i += 2  # Sautez le point et l'attribut/méthode suivant
                    var_type = self.find_variable_type(token[1])
                else:
                    # C'est un identifiant qui n'est pas suivi par '(' ou '.', donc c'est une variable
                    var_type = self.find_variable_type(token[1])
            elif token[0] == "NUMBER":
                if "." in token[1]:
                    var_type = "float"
                else:
                    var_type = "int"
            if var_type != expected_type:
                raise SyntaxErrorWithLine(self.get_line(), f"Expected expression with only {expected_type} variable but got {token[1]} which type is {var_type}")

            i += 1  # Avancez à chaque itération de la boucle
        return expected_type

        
    def get_line(self):
        """Get the current line number from the tokens."""
        _, _, line = self.tokens[self.current]
        return line

    def declare_function(self, name, return_type, params):
        if name in self.functions:
            raise Exception(f"Function '{name}' is already declared.")
        self.functions[name] = (return_type, params)
        for param_type, param_name in params:
            self.declare_variable(param_name, param_type)

    def find_function(self, name):
        if name not in self.functions:
            raise Exception(f"Function '{name}' not declared.")
        return self.functions[name]

    # Function to consume a token and ensure it is of the expected type
    def consume(self, expected_type):
        token_type, token_value, token_line = self.tokens[self.current]
        if self.current >= len(self.tokens):
            raise SyntaxErrorWithLine(token_line, f"Unexpected end of tokens, expected {expected_type}")

        token_type, token_value, token_line = self.tokens[self.current]
        if token_type == expected_type:
            self.current += 1
            return token_value
        else:
            raise SyntaxErrorWithLine(token_line,
                f"Expected {expected_type} but got {token_type} ('{token_value}')"
            )

    def parse_variable_declaration(self):
        var_type = self.consume("KEYWORD")  # Expect a type keyword like 'int'
        name = self.consume("IDENTIFIER")   # Expect the variable name
        # Check if next token is a semicolon or an equals sign (for potential initialization)
        next_token_type, next_token_value, _ = self.tokens[self.current]
        
        if next_token_value == ";":
            self.consume("SYMBOL")  # Consume the semicolon, ending the declaration
            self.declare_variable(name, var_type)  # Declare without initializing
            return {"type": "var_decl", "var_type": var_type, "name": name, "value": None}
        
        elif next_token_value == "=":
            self.consume("OPERATOR")  # Consume the equals sign
            value, type = self.parse_term(var_type)
            self.consume("SYMBOL")  # Consume the semicolon
            self.declare_variable(name, var_type)  # Declare and initialize
            return {"type": "var_decl", "var_type": var_type, "name": name, "value": value}
        else:
            raise SyntaxErrorWithLine(self.get_line(), "Expected ';' or '=' after variable declaration")

    # Parses declarations of 'pen' type, including position initialization
    def parse_pen_declaration(self):
        token_type, token_value, token_line = self.tokens[self.current]
        self.consume("KEYWORD")  # 'pen'
        name = self.consume("IDENTIFIER")
        if name in self.variables:
            raise SyntaxErrorWithLine(token_line, f"Variable '{name}' already declared")

        self.consume("OPERATOR")  # '='
        self.consume("KEYWORD")   # 'cursor'
        self.consume("SYMBOL")    # '('
        # Parse x value, which can be a NUMBER or an IDENTIFIER referring to a variable
        x, type = self.parse_number_or_variable()
        
        
        self.consume("SYMBOL")    # ','
        
        # Parse y value, which can be a NUMBER or an IDENTIFIER referring to a variable
        y, type = self.parse_number_or_variable()
        self.consume("SYMBOL")    # ')'
        self.consume("SYMBOL")    # ';'

        self.variables[name] = "pen"
        return {"type": "pen_decl", "name": name, "x": x, "y": y}

    def parse_number_or_variable(self):
        token_type, token_value, token_line = self.tokens[self.current]
        
        if token_type == "NUMBER":
            self.consume("NUMBER")
            if "." in token_value :
                return token_value, "float"
            else :
                return token_value, "int"  # Return the number as is
        elif token_type == "IDENTIFIER":
            # Verify the variable is declared and is of a type that can be treated as a number
            var_name = self.consume("IDENTIFIER")
            if var_name not in self.variables or self.variables[var_name] not in ["int", "float","pen"]:
                raise SyntaxErrorWithLine(token_line, f"Variable '{var_name}' is not declared as a numeric type")
            return var_name, self.variables[var_name] # Return the variable name
        else:
            raise SyntaxErrorWithLine(token_line, f"Expected a number or variable, got '{token_value}'")
    
    # Parses method calls on 'pen' objects, ensuring that the pen has been declared
    def parse_pen_method(self, pen_name):
        token_type, token_value, token_line = self.tokens[self.current]
        if pen_name not in self.variables:
            raise SyntaxErrorWithLine(token_line, f"Variable '{pen_name}' is not declared")
        if self.variables[pen_name] != "pen":
            raise SyntaxErrorWithLine(token_line, f"Variable '{pen_name}' is not a pen")

        self.consume("SYMBOL")  # '.'
        method = self.consume("KEYWORD")
        self.consume("SYMBOL")  # '('
        params = []
        if self.tokens[self.current][1] != ")":
            lst1 = self.parse_expression_condition()
            params.append(lst1)
            while self.tokens[self.current][1] == ",":
                self.consume("SYMBOL")
                lst = self.parse_expression_condition()
                params.append(lst)
        if method in ["walk","goTo"]:
            for e in params :
                if not expression_pattern.match(e):
                    if int(e) < 0 :
                        raise SyntaxErrorWithLine(token_line, f"Expected argument >= 0 but got {e}")

        self.consume("SYMBOL")  # ')'
        self.consume("SYMBOL")  # ';'
        return {"type": "method_call", "name": pen_name, "method": method, "params": params}
    
    def parse_pen_call(self, pen_name) :
        token_type, token_value, token_line = self.tokens[self.current]
        if pen_name not in self.variables:
            raise SyntaxErrorWithLine(token_line, f"Variable '{pen_name}' is not declared")
        if self.variables[pen_name] != "pen":
            raise SyntaxErrorWithLine(token_line, f"Variable '{pen_name}' is not a pen")

        self.consume("SYMBOL")  # '.'
        attribute = self.consume("PEN_ATTRIBUTE")
        return {
            "type": "pen_attribute",
            "name": pen_name,
            "attribute": attribute
        }
    # Parses attribute assignments for 'pen' objects
    def parse_pen_attribute(self, pen_name):
        
        token_type, token_value, token_line = self.tokens[self.current]
        if pen_name not in self.variables:
            raise SyntaxErrorWithLine(token_line, f"Variable '{pen_name}' is not declared")
        if self.variables[pen_name] != "pen":
            raise SyntaxErrorWithLine(token_line, f"Variable '{pen_name}' is not a pen")

        self.consume("SYMBOL")  # '.'
        attribute = self.consume("PEN_ATTRIBUTE")
        
        self.consume("OPERATOR")
        
        next_token_type, next_token_value, next_token_line = self.tokens[self.current+1]
        next3_token_type, next3_token_value, next3_token_line = self.tokens[self.current+3]
        if attribute in ["rotation","penDown","positionY", "positionX","thickness"]:
            
            if next_token_type == "OPERATOR" or next3_token_type == "OPERATOR" :
                value, type = self.parse_expression("int")
            else :
                value, type = self.parse_number_or_variable()
                if not expression_pattern.match(value):
                    if attribute in ["positionY", "positionX", "penDown"] :
                        if int(value) < 0 :
                            raise SyntaxErrorWithLine(token_line, f"The value of {attribute} must be >= 0, but got {value} ")
                    elif attribute == "thickness":
                        if int(value) < 1 :
                            raise SyntaxErrorWithLine(token_line, f"The value of {attribute} must be >= 1, but got {value} ")
                    elif attribute == "rotation":
                        if int(value) > 90 or int(value) < 0:
                            raise SyntaxErrorWithLine(token_line, f"The value of {attribute} must be between 0 and 90, but got {value} ")
                
        elif attribute == "color":
            value = self.parse_function_call("defineColor")
        else:
            raise SyntaxErrorWithLine(token_line, f"Variable '{attribute}' is not a valid pen attribute")
        
        self.consume("SYMBOL")  # ';'
        
        return {
            "type": "pen_attribute",
            "name": pen_name,
            "attribute": attribute,
            "value": value
        }

    def parse_function_call(self, name=None):
        # Récupérer le nom de la fonction et vérifier qu'elle est bien déclarée
        if name is not None:
            func_name = name
            self.consume("IDENTIFIER")
        else:
            func_name = self.consume("IDENTIFIER")
        
        if func_name not in self.functions:
            raise SyntaxErrorWithLine(self.get_line(), f"Function '{func_name}' is not declared.")
        
        self.consume("SYMBOL")  # Consommer '('
        # Récupérer les types et noms des paramètres attendus pour la fonction
        param_defs = self.functions[func_name][1]
        
        actual_args = []
        if self.tokens[self.current][1] != ")":
            while True:
                arg_value = self.parse_expression_condition()  # Assurez-vous que cette méthode renvoie (valeur, type)
                actual_args.append(arg_value)
                if self.tokens[self.current][1] == ",":
                    self.consume("SYMBOL")
                elif self.tokens[self.current][1] == ")":
                    break
                else:
                    raise SyntaxErrorWithLine(self.get_line(), "Expected ',' or ')' in function call")
                
        
        self.consume("SYMBOL")  # Consommer ')'
        
        # Vérifier le nombre d'arguments
        if len(param_defs) != len(actual_args):
            raise SyntaxErrorWithLine(self.get_line(), f"Function '{func_name}' expects {len(param_defs)} arguments, got {len(actual_args)}.")
        
        # Type checking
        for (expected_type, _), arg_expr in zip(param_defs, actual_args):
            if expression_pattern.match(arg_expr):
                actual_type = self.get_expression_type(arg_expr,expected_type)
            elif identifier_pattern.match(arg_expr) is not None:
                actual_type = self.find_variable_type(arg_expr)
            elif number_pattern.match(arg_expr) is not None :
                
                if "." in arg_expr :
                    actual_type = "float"
                else :
                    actual_type = "int"
            elif '"' in arg_expr :
                actual_type = "string"
            else:
                raise SyntaxErrorWithLine(self.get_line(), f"Type mismatch for function '{func_name}': unknown type : {expected_type}, got {arg_expr}")
            if expected_type != actual_type:
                raise SyntaxErrorWithLine(self.get_line(), f"Type mismatch for function '{func_name}': expected {expected_type}, got {arg_expr}")
        return {"type": "function_call", "name": func_name, "args": [arg for arg in actual_args]}  # retourne seulement les valeurs des arguments

        

        # Here you should add code to check the types of actual_args against params

    # Parses function definitions, checking for duplicate declarations and parsing the function body
    def parse_function(self):
        token_type, token_value, token_line = self.tokens[self.current]
        self.consume("KEYWORD")  # 'func'
        return_type = self.consume("KEYWORD")
        name = self.consume("IDENTIFIER")
        if name in self.functions:
            raise SyntaxErrorWithLine(token_line, f"Function '{name}' already declared")
        self.consume("SYMBOL")  # '('
        
        params = []

        self.func_vars = 1
        
        while self.tokens[self.current][1] != ")":
            param_type = self.consume("KEYWORD")
            
            param_name = self.consume("IDENTIFIER")
            params.append((param_type, param_name))
            if self.tokens[self.current][1] == ",":
                self.consume("SYMBOL")
        
        self.consume("SYMBOL")  # ')'
        self.consume("SYMBOL")  # '{'
        self.declare_function(name, return_type, params)

        body = [] 

        self.func_use = name
        while self.tokens[self.current][1] != "}":
            body.append(self.parse_statement())  
        self.functions_vars = {}
        self.func_vars = 0
        self.func_use = ""
        self.consume("SYMBOL")  # '}'
        self.functions[name] = (return_type, params)
        return {
            "type": "function",
            "return_type": return_type,
            "name": name,
            "params": params,
            "body": body
        }

    # Parses repeat loops, including initialization, condition, increment, and loop body
    def parse_repeat(self):
        self.consume("KEYWORD")  
        self.consume("SYMBOL")  
        init = self.parse_expression_condition()
        self.consume("SYMBOL")  
        condition = self.parse_expression_condition()
        self.consume("SYMBOL")  
        increment = self.parse_increment()
        self.consume("SYMBOL")  

        self.consume("SYMBOL")  
        body = []
        
        while self.tokens[self.current][1] != "}":
            body.append(self.parse_statement())
        self.consume("SYMBOL")
        
        return {
            "type": "repeat",
            "init": init,
            "condition": condition,
            "increment_var": increment["name"],
            "increment_op": increment["operation"],
            "body": body
        }

    # Parses conditional structures (if, else if, else), including conditions and branches
    def parse_condition(self):
        if self.consume("KEYWORD") == "if":
            self.consume("SYMBOL")  # '('
            condition = self.parse_expression_condition()
            self.consume("SYMBOL")  # ')'
            self.consume("SYMBOL")  # '{'

            body = []
            while self.tokens[self.current][1] != "}":
                body.append(self.parse_statement())
            self.consume("SYMBOL")  # '}'

            node = {
                "type": "if",
                "condition": condition,
                "body": body,
                "elseif": [],
                "else": None
            }

            while self.current < len(self.tokens) and self.tokens[self.current][1] == "elseif":
                self.consume("KEYWORD")  
                self.consume("SYMBOL")  
                elseif_condition = self.parse_expression_condition()
                self.consume("SYMBOL")  
                self.consume("SYMBOL")  
                elseif_body = []
                while self.tokens[self.current][1] != "}":
                    elseif_body.append(self.parse_statement())
                self.consume("SYMBOL")  
                node["elseif"].append({
                    "condition": elseif_condition,
                    "body": elseif_body
                })

            if self.current < len(self.tokens) and self.tokens[self.current][1] == "else":
                self.consume("KEYWORD")  
                self.consume("SYMBOL")  
                else_body = []
                while self.tokens[self.current][1] != "}":
                    else_body.append(self.parse_statement())
                self.consume("SYMBOL")
                node["else"] = else_body

            return node

    # Parses statements related to control flow methods (break, continue, etc.)
    def parse_condition_methode(self):
        token_type, token_value, token_line = self.tokens[self.current]
        if token_type == "KEYWORD":
            methode = self.consume("KEYWORD")
            self.consume("SYMBOL")  
            return {"type": "methode", "methode": methode}

    # Parses increment operations, ensuring that variables have been declared
    def parse_increment(self):
        name, var_line = self._consume_identifier_checked()
        operation_type, operation_val, operation_line = self.tokens[self.current]
        if operation_type != "OPERATOR" or operation_val not in ["++","--"]:
            raise SyntaxErrorWithLine(operation_line, f"Unexpected increment operation : '{operation_val}'")
        self.current += 1

        return {"type": "short_operation", "name": name, "operation": operation_val}

    # Parses simple short operations (increment/decrement)
    def parse_short_operation(self):
        name, var_line = self._consume_identifier_checked()
        operation_type, operation_val, operation_line = self.tokens[self.current]
        if operation_type != "OPERATOR" or operation_val not in ["++","--"]:
            raise SyntaxErrorWithLine(operation_line, f"Unexpected operation '{operation_val}'")

        self.current += 1
        # Consume the semicolon
        if self.current < len(self.tokens) and self.tokens[self.current][1] == ";":
            self.consume("SYMBOL")

        return {"type": "short_operation", "name": name, "operation": operation_val}

    # Parses assignment operations, ensuring that variables have been declared and optionally checking types
    def parse_assignment(self):
        
        var_name = self.consume("IDENTIFIER")
        self.consume("OPERATOR")  # Consume the '=' symbol
        var_type = self.find_variable_type(var_name)
        value = self.parse_expression(var_type)  # Parse the expression to assign
        self.consume("SYMBOL")  # Consume the semicolon

        # Check if variable is declared
        if not self.is_variable_declared(var_name):
            raise SyntaxErrorWithLine(self.get_line(), f"Variable '{var_name}' not declared.")

        return {"type": "assignment", "left": var_name, "right": value}


    def parse_expression_condition(self):
        """
        Parse an expression, including binary operations (e.g., 'num * num').
        """
        left = self.parse_term_condition()  # Parse the first operand or term
        
        while self.current < len(self.tokens):
            token_type, token_value, token_line = self.tokens[self.current]
            

            # Check for an operator
            if token_type == "OPERATOR":
                operator = self.consume("OPERATOR")
                
                right = self.parse_term_condition()

                if operator == "&" :
                    operator = " and "
                elif operator == "|" :
                    operator = " or "
                    
                left = f"{left} {operator} {right}"  # Combine into a valid expression
            
            else:
                break
        return left

    def parse_term_condition(self):
        """
        Parse a single term, such as a variable, number, or parenthesized expression.
        """
        token_type, token_value, token_line = self._current_token()
        if token_type == "IDENTIFIER" or token_type == "NUMBER" or token_type == "STRING" or token_type == "PEN_ATTRIBUTE":
            self.current += 1
            return token_value
        else:
            raise SyntaxErrorWithLine(token_line, f"Unexpected token in term: {token_value}")


    def parse_expression(self, expected_type=None):
        right_value, right_type = self.parse_term(expected_type)
        return right_value, right_type

    # Parses terms within expressions, handling variables, numbers, and parenthesized expressions
    def parse_term(self, expected_type):
        token_type, token_value, token_line = self._current_token()
        next_token_type, next_token_value, next_token_line = self.tokens[self.current+1] if (self.current+1) < len(self.tokens) else (None,None,None)

        if (token_type == "IDENTIFIER" or token_type == "NUMBER") and next_token_value == ";":
            #self.parse_number_or_variable()
            if token_type == "IDENTIFIER":
                if self.is_variable_declared(token_value):
                    var_type = self.find_variable_type(token_value)
                    if var_type != expected_type :
                        raise SyntaxErrorWithLine(token_line, f"Wrong variable type '{token_value}'")
                    self.consume("IDENTIFIER")
                    return token_value, var_type
                else :
                    raise SyntaxErrorWithLine(token_line, f"Undefined variable '{token_value}'")
            elif token_type == "NUMBER":
                if '.' in token_value:
                    name, type = self.parse_number_or_variable()
                    if expected_type != "float" :
                        raise SyntaxErrorWithLine(token_line, f"Wrong variable type '{token_value}'")
                    return name, "float"
                else:
                    name, type = self.parse_number_or_variable()
                    if expected_type != "int" :
                        raise SyntaxErrorWithLine(token_line, f"Wrong variable type '{token_value}'")
                    return name, "int"
        elif (token_type == "IDENTIFIER" or token_type == "NUMBER") and (next_token_type == "OPERATOR" or next_token_value == "(" or next_token_value == "."):
            expr_value = ""
            while self.tokens[self.current][1] != ";":
                
                token_type, token_value, token_line = self._current_token()
                
                next_token_type, next_token_value, next_token_line = self.tokens[self.current+1] if (self.current+1) < len(self.tokens) else (None,None,None)
                
                if token_type == "IDENTIFIER":
                    if next_token_value == "(":
                        if self.is_function_declared(token_value) :
                            
                            func = self.parse_function_call(token_value)
                            token_type, token_value, token_line = self._current_token()
                            
                            return_type, params =self.functions[func["name"]]
                            
                            if return_type != expected_type :
                                raise SyntaxErrorWithLine(token_line, f"Wrong return function type '{func["name"]}'")
                            
                            if self.tokens[self.current][1] == ";": 
                                func_call = func["name"] + "(" + ", ".join(map(str, (func["args"]))) + ")"
                                expr_value += func_call
                                
                                return expr_value, return_type
                            else :
                                func_call = func["name"] + "(" + ", ".join(map(str, (func["args"]))) + ")"
                                expr_value += func_call
                        else :
                            raise SyntaxErrorWithLine(token_line, f"Undefined function '{token_value}'")
                    elif next_token_value == ".":
                        pen = self.consume("IDENTIFIER")
                        value = self.parse_pen_call(pen)
                        expr_value += value["name"] + "." + value["attribute"]
                        token_type, token_value, token_line = self._current_token()
                    elif next_token_type == "OPERATOR" or next_token_type == "SYMBOL":
                        if not self.is_variable_declared(token_value) :
                            raise SyntaxErrorWithLine(token_line, f"Undefined variable '{token_value}'")
                        elif self.find_variable_type(token_value) != expected_type and expected_type is not None:
                            raise SyntaxErrorWithLine(token_line, f"Wrong variable type '{token_value}'")
                        else :
                            
                            txt = self.consume("IDENTIFIER")
                            expr_value += txt
                    
                elif token_type == "NUMBER": # and expected_type is not None: 
                    if '.' in token_value:
                        
                        name, type = self.parse_number_or_variable()
                        if expected_type != "float" :
                            raise SyntaxErrorWithLine(token_line, f"Wrong variable type '{token_value}'")
                        expr_value += name
                    else:
                        name, type = self.parse_number_or_variable()
                        if expected_type != "int" :
                            raise SyntaxErrorWithLine(token_line, f"Wrong variable type '{token_value}'")
                        expr_value += name
                else :
                    raise SyntaxErrorWithLine(token_line, f"Incorrect variable type '{token_value}'")
                
                token_type, token_value, token_line = self._current_token()
                if self.tokens[self.current][1] == ";":
                    break
                else :
                    txt = self.consume("OPERATOR")
                
                expr_value += txt
            return expr_value, expected_type
        else:
            raise SyntaxErrorWithLine(token_line, f"Unexpected token in term: {token_value}")
    
    # Parses SDL function calls, treating them like any other function but ensuring proper argument handling
    def parse_sdl_function(self):
        func_name_type, func_name_val, func_line = self.tokens[self.current]
        if func_name_type != "KEYWORD":
            raise SyntaxErrorWithLine(func_line, f"Expected SDL function name, got '{func_name_val}'")

        self.current += 1  # consume the function name

        # Consume '('
        self.consume("SYMBOL")
        args = []
        while self.tokens[self.current][1] != ")":
            args.append(self.parse_expression_condition())
            if self.tokens[self.current][1] == ",":
                self.consume("SYMBOL")
        self.consume("SYMBOL")  # ')'
        # Consume ';'
        if self.tokens[self.current][1] == ";":
            self.consume("SYMBOL")

        return {
            "type": "sdl_function_call",
            "name": func_name_val,
            "args": args
        }

    # Parses any single statement within the code, dispatching to specific parsing functions based on the statement type
    
    def parse_statement(self):
        token_type, token_value, token_line = self._current_token()
        next_token_type, next_token_value, next_token_line = self.tokens[self.current+1] if (self.current+1) < len(self.tokens) else (None,None,None)
       
        # Handle SDL functions
        if token_type == "KEYWORD" and token_value in [
            "fillColor","initMatrix","clearMatrix","compareSDLColors","defineColor",
            "approxPosX","approxPosY","approxPos","float2Rad","pixelColor",
            "circleWrite","rotateArea","copyPaste","copy","paste","cut","translation",
            "waitKey","closeEventSDL","renderMatrix","initSDL"
        ]:
            return self.parse_sdl_function()
        elif token_type == "KEYWORD" and token_value == "pen":
            return self.parse_pen_declaration()
        
        elif token_type == "IDENTIFIER" and next_token_type == "SYMBOL" and next_token_value == ".":
            pen_name_t, pen_name_val, pen_name_line = self.tokens[self.current]
            self.current += 1  # consume the identifier
            
            if pen_name_val not in self.variables:
                raise SyntaxErrorWithLine(pen_name_line, f"PEN '{pen_name_val}' not declared.")
            # Peek at the next token
            next_next_type, next_next_val, next_next_line = self.tokens[self.current+1]
            if next_next_type == "PEN_ATTRIBUTE":
                return self.parse_pen_attribute(pen_name_val)
            else:
                return self.parse_pen_method(pen_name_val)

        elif token_type == "KEYWORD" and token_value == "func":
            
            return self.parse_function()
            
        
        elif token_type == "KEYWORD" and token_value in ["int","float","bool","string"]:
            
            return self.parse_variable_declaration()
        
        elif token_type == "KEYWORD" and token_value == "return":
            self.consume("KEYWORD")
            if self.func_vars :
                return_type, params = self.functions[self.func_use]
                value, type = self.parse_expression(return_type)#ajout expected type a lire depuis la fonction
            else :
                value, type = self.parse_expression()
            self.consume("SYMBOL")
            if self.current < len(self.tokens) and self.tokens[self.current][1] == ";":
                self.consume("SYMBOL")  
            return {"type": "return", "value": value}
        
        elif token_type == "KEYWORD" and token_value == "repeat":
            return self.parse_repeat()
        
        elif token_type == "KEYWORD" and token_value == "if":
            return self.parse_condition()
        
        elif token_type == "KEYWORD" and token_value in ["skip","leave","break","wait"]:
            return self.parse_condition_methode()
        
        # Short operations
        elif token_type == "IDENTIFIER":
            # x++ / x--
            if next_token_value in ["++","--"]:
                return self.parse_short_operation()
            else:
                return self.parse_assignment()
        else:
            raise SyntaxErrorWithLine(token_line, f"Unexpected token in statement: {token_value}")

    # Utility function to retrieve the current token or default if at the end of the list
    def _current_token(self):
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        else:
            return (None, None, None)

    # Utility function to check an identifier for declaration before use
    def _consume_identifier_checked(self):
        token_type, token_value, token_line = self.tokens[self.current]
        if token_type != "IDENTIFIER":
            raise SyntaxErrorWithLine(token_line, f"Expected identifier, got '{token_value}'")
        if token_value not in self.variables:
            raise SyntaxErrorWithLine(token_line, f"Variable '{token_value}' is not declared.")
        self.current += 1
        return token_value, token_line

    # Main parse function that processes all tokens into an abstract syntax tree (AST)
    def parse(self):
        ast = []
        self.variables = {} # Save declared variables
        self.functions = {} # Save declared func
        func_name = "defineColor"
        return_type = "int"  # Assumant que defineColor ne retourne rien
        params = [("string", "colorCode")]  # Le paramètre attend un code couleur en string

        if func_name not in self.functions:
            self.functions[func_name] = (return_type, params)
            for param_type, param_name in params:
                self.declare_variable(param_name, param_type)  # Déclare les paramètres comme variables locales si nécessaire
        while self.current < len(self.tokens):
            statement = self.parse_statement()
            ast.append(statement)
        return ast

# Function to generate C code from the parsed AST, handling various statement and expression types
def generate_c_code(ast, lst, current_line):
    c_code = []
    #print(f"Starting generation at line {type(current_line)}")
    for node in ast:
        #print(f"Processing node at line {current_line}: {node['type']}")
        if current_line in lst:
            c_code.append("WAIT")
        if node["type"] == "var_decl":
            value,current_line = generate_c_code([node["value"]],lst,current_line) if isinstance(node["value"], dict) else node["value"], current_line
            if value is None or value == "None":
                c_code.append(f"{node['var_type']} {node['name']};")
            else:
                c_code.append(f"{node['var_type']} {node['name']} = {value};")
        elif node["type"] == "pen_decl":

            c_code.append(f"PEN {node['name']} = createPen({node['x']}, {node['y']});")
        elif node["type"] == "pen_method":
            
            params = ", ".join(map(str, node.get("params", [])))
            c_code.append(f"{node['name']}.{node['method']}({params});")
        elif node["type"] == "function_call":
            args = ", ".join(node["args"])
            c_code.append(f"{node['name']}({args});")
        elif node["type"] == "sdl_function_call":
            func_name = node["name"]
            args = ", ".join(node["args"])
            c_code.append(f"{func_name}({args});")
        elif node["type"] == "function":
            params = ", ".join([f"{ptype} {pname}" for ptype, pname in node.get("params", [])])
            body_str, current_line = generate_c_code(node.get("body", []),lst,current_line)
            c_code.append(f"{node['return_type']} {node['name']}({params}) {{\n{body_str}\n}}")
        elif node["type"] == "return":
            c_code.append(f"return {node['value']};")
        elif node["type"] == "assignment":
            left = node["left"]
            right = node["right"]
            c_code.append(f"{left} = {right[0]};")
        elif node["type"] == "methode":
            methode = node["methode"]
            if methode == "wait":
                c_code.append("WAIT;")
            else :
                c_code.append(f"{methode};")
        elif node["type"] == "short_operation":
            operation = node["operation"]
            name = node["name"]
            c_code.append(f"{name}{operation};")
        elif node["type"] == "repeat":
            init = node["init"]
            condition = node["condition"]
            incr_var = node["increment_var"]
            incr_op = node["increment_op"]
            body_str, current_line = generate_c_code(node["body"],lst,current_line)
            c_code.append(f"for ({init}; {condition}; {incr_var}{incr_op}) {{\n{body_str}\n}}")
        elif node["type"] == "if":
            condition = node["condition"]
            body_str, current_line = generate_c_code(node["body"],lst,current_line)
            c_code.append(f"if ({condition}) {{\n{body_str}\n}}")
            if node.get("elseif"):
                for elif_block in node["elseif"]:
                    elif_cond = elif_block["condition"]
                    elif_body, current_line = generate_c_code(elif_block["body"],lst,current_line)
                    c_code.append(f"else if ({elif_cond}) {{\n{elif_body}\n}}")
            if node.get("else"):
                else_body, current_line = generate_c_code(node["else"],lst,current_line)
                c_code.append(f"else {{\n{else_body}\n}}")
        elif node["type"] == "pen_attribute":
            if node['attribute'] == "color":
                c_code.append(f"{node['name']}.{node['attribute']} = {node['value']["name"]}({node['value']["args"][0]});")
            else :
                c_code.append(f"{node['name']}.{node['attribute']} = {node['value']};")
        elif node["type"] == "method_call":
            params = ", ".join(map(str, node["params"]))
            
            if len(node["params"]) > 0:
                if node['method'] == "goTo" or node['method'] == "walk":
                    c_code.append(f"{node['name']} = {node['method']}({node['name']},{params});")
                else :
                    c_code.append(f"{node['method']}({node['name']},{params});")
            else:
                c_code.append(f"{node['method']}({node['name']});")
        else:
            raise ValueError(f"Unknown AST node type: {node['type']}.")
        current_line += 1
        
    return "\n".join(c_code), current_line

# Functions to read from and write to files
def read_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def write_file(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
import sys, ast as at
# Main function to execute the compiler process
def main(input_file, line_numbers=None):
    output_file = "./c/src/main.c"  # Chemin du fichier de sortie défini dans le code
    lst = line_numbers if line_numbers else []  # Utiliser les numéros de ligne fournis ou une liste vide
    try:
        pydraw_code = read_file(input_file)
        tokens = tokenize(pydraw_code)
        parser = Parser(tokens)
        ast = parser.parse()
        header ='#include "../libs/pyDraw.h"\nint main(int argc, char* argv[]) {\ninitMatrix();\ninitSDL();\n'
        footer ='\ncloseEventSDL();\nreturn 0;\n}'
        c_code, line = generate_c_code(ast, lst, 1)
        c_code = header + c_code + footer
        write_file(output_file, c_code)
        print(f"Compilation successful! C code has been generated in {output_file}.")
    except SyntaxErrorWithLine as e:
        # If a syntax error is caught, it is printed and returned as a dictionary
        return {e.line: e.message}
    
    except Exception as e:
        # Other exceptions are logged as errors
        return {"General error":e}


# L'utilisation typique en dehors de ce fichier pourrait ressembler à ceci:
if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        line_nums = at.literal_eval(sys.argv[2]) if len(sys.argv) > 2 else None
        main(file_path, line_nums)
    else:
        print("Usage: python main.py <input_file> [line_numbers]")


"""# other_script.py
import main

# Appel de la fonction main avec le chemin du fichier et éventuellement des numéros de ligne
input_file = "test.txt"
line_numbers = [1, 2, 3]  # Les lignes où vous voulez que quelque chose de spécifique soit effectué

main.main(input_file, line_numbers)"""


# L'utilisation typique en dehors de ce fichier pourrait ressembler à ceci:
if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        line_nums = at.literal_eval(sys.argv[2]) if len(sys.argv) > 2 else None
        main(file_path, line_nums)
    else:
        print("Usage: python main.py <input_file> [line_numbers]")

