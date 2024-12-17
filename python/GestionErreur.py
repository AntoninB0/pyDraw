class CompilationError(Exception):
    def __init__(self, line, value, message):
        super().__init__(f"Error at line {line}: '{value}' - {message}")
        self.line = line
        self.value = value
        self.message = message

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.symbol_table = {}  # Table des symboles : {variable: type}

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
        var_type = self.consume("KEYWORD")  # int, float, bool, string, pen
        name = self.consume("IDENTIFIER")

        if name in self.symbol_table:
            raise CompilationError(self.tokens[self.current - 1][0], name, "Variable already declared")
        self.symbol_table[name] = var_type

        if self.tokens[self.current][2] == "=":
            self.consume("OPERATOR")  # Consume '='
            value = self.parse_expression()

            # Type checking
            self.check_type(var_type, value)
        else:
            value = None

        self.consume("SYMBOL")  # Consume ';'
        return {"type": "var_decl", "var_type": var_type, "name": name, "value": value}

    def parse_expression(self):
        token_type, token_value = self.tokens[self.current][1], self.tokens[self.current][2]
        if token_type in ["NUMBER", "IDENTIFIER", "STRING", "BOOL"]:
            self.current += 1
            return token_value
        else:
            raise CompilationError(self.tokens[self.current][0], token_value, "Invalid expression")

    def parse_pen_method_call(self):
        pen_name = self.consume("IDENTIFIER")
        if pen_name not in self.symbol_table or self.symbol_table[pen_name] != "pen":
            raise CompilationError(self.tokens[self.current - 1][0], pen_name, "Pen not declared")

        self.consume("SYMBOL")  # '.'
        method = self.consume("IDENTIFIER")
        self.consume("SYMBOL")  # '('
        args = []
        while self.tokens[self.current][2] != ")":
            args.append(self.parse_expression())
            if self.tokens[self.current][2] == ",":
                self.current += 1  # Consume ','

        self.consume("SYMBOL")  # ')'
        self.consume("SYMBOL")  # ';'
        return {"type": "pen_method_call", "pen": pen_name, "method": method, "args": args}

    def check_type(self, var_type, value):
        if var_type == "int" and "." in value:
            raise CompilationError(self.tokens[self.current - 1][0], value, "Type mismatch: expected 'int'")
        elif var_type == "float" and not any(c in value for c in "0123456789."):
            raise CompilationError(self.tokens[self.current - 1][0], value, "Type mismatch: expected 'float'")
        elif var_type == "bool" and value not in ["true", "false"]:
            raise CompilationError(self.tokens[self.current - 1][0], value, "Type mismatch: expected 'bool'")
        elif var_type == "string" and not (value.startswith('"') and value.endswith('"')):
            raise CompilationError(self.tokens[self.current - 1][0], value, "Type mismatch: expected 'string'")

    def parse_if_statement(self):
        self.consume("KEYWORD")  # 'if'
        self.consume("SYMBOL")  # '('
        condition = self.parse_expression()
        self.consume("SYMBOL")  # ')'
        self.consume("SYMBOL")  # '{'

        statements = []
        while self.tokens[self.current][2] != "}":
            statements.append(self.parse_statement())

        self.consume("SYMBOL")  # '}'
        return {"type": "if_statement", "condition": condition, "statements": statements}

    def parse_statement(self):
        token_type, token_value = self.tokens[self.current][1], self.tokens[self.current][2]

        if token_type == "KEYWORD" and token_value in ["int", "float", "bool", "string", "pen"]:
            return self.parse_variable_declaration()
        elif token_type == "IDENTIFIER":
            if self.tokens[self.current + 1][2] == ".":  # Pen method
                return self.parse_pen_method_call()
            else:  # Assignment
                name = self.consume("IDENTIFIER")
                self.consume("OPERATOR")  # '='
                value = self.parse_expression()
                self.consume("SYMBOL")  # ';'
                return {"type": "assignment", "name": name, "value": value}
        elif token_value == "if":
            return self.parse_if_statement()
        else:
            raise CompilationError(self.tokens[self.current][0], token_value, "Unexpected statement")

    def parse(self):
        program = []
        while self.current < len(self.tokens):
            program.append(self.parse_statement())
        return program
