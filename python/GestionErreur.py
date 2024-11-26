class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.symbol_table = {}  # Table des symboles {variable: type}

    def consume(self, expected_type):
        if self.current >= len(self.tokens):
            raise CompilationError(self.tokens[-1][0], "", f"Unexpected end of tokens, expected {expected_type}")

        token_type, token_value = self.tokens[self.current][1], self.tokens[self.current][2]
        if token_type == expected_type:
            self.current += 1
            return token_value
        else:
            raise CompilationError(self.tokens[self.current][0], token_value, f"Expected {expected_type} but got {token_type}")

    def parse_variable_declaration(self):
        """
        Parse a variable declaration and check types during parsing.
        """
        var_type = self.consume("KEYWORD")  # Get the type (e.g., int, float)
        name = self.consume("IDENTIFIER")  # Get the variable name

        # Add variable to symbol table with its declared type
        if name in self.symbol_table:
            raise CompilationError(self.tokens[self.current - 1][0], name, f"Variable '{name}' already declared")
        self.symbol_table[name] = var_type

        # Handle initialization
        self.consume("OPERATOR")  # Assignment operator '='
        value = self.parse_expression()

        # Type checking
        if var_type == "int" and "." in value:
            raise CompilationError(self.tokens[self.current - 1][0], value, f"Type mismatch: expected 'int' but got 'float'")
        elif var_type == "float" and not ("." in value or value.isdigit()):
            raise CompilationError(self.tokens[self.current - 1][0], value, f"Type mismatch: expected 'float' but got '{value}'")

        self.consume("SYMBOL")  # Semicolon ';'
        return {"type": "var_decl", "var_type": var_type, "name": name, "value": value}

    def parse_assignment(self):
        """
        Parse an assignment operation and check types.
        """
        name = self.consume("IDENTIFIER")
        if name not in self.symbol_table:
            raise CompilationError(self.tokens[self.current - 1][0], name, f"Variable '{name}' not declared")

        self.consume("OPERATOR")  # Assignment operator '='
        value = self.parse_expression()

        # Type checking
        declared_type = self.symbol_table[name]
        if declared_type == "int" and "." in value:
            raise CompilationError(self.tokens[self.current - 1][0], value, f"Type mismatch: variable '{name}' is 'int', cannot assign 'float'")
        elif declared_type == "float" and not ("." in value or value.isdigit()):
            raise CompilationError(self.tokens[self.current - 1][0], value, f"Type mismatch: variable '{name}' is 'float', incompatible value")

        self.consume("SYMBOL")  # Semicolon ';'
        return {"type": "assignment", "name": name, "value": value}

    def parse_expression(self):
        """
        Parse a basic expression.
        """
        token_type, token_value = self.tokens[self.current][1], self.tokens[self.current][2]
        if token_type in ["NUMBER", "IDENTIFIER"]:
            self.current += 1
            return token_value
        else:
            raise CompilationError(self.tokens[self.current][0], token_value, "Invalid expression")
def parse_statement(self):
    token_type, token_value = self.tokens[self.current][1], self.tokens[self.current][2]

    # Handle variable declarations
    if token_type == "KEYWORD" and token_value in ["int", "float"]:
        return self.parse_variable_declaration()

    # Handle variable assignments
    elif token_type == "IDENTIFIER":
        return self.parse_assignment()

    else:
        raise CompilationError(self.tokens[self.current][0], token_value, "Unexpected statement")

