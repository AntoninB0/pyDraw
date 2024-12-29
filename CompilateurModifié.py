import re
from typing import List, Any

# ----------------------
# Lexical Analysis (Lexer)
# ----------------------
class Token:
    def __init__(self, type: str, value: Any):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

class Lexer:
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.tokens = []

    def tokenize(self):
        token_specification = [
            ("NUMBER",    r"\d+"),            # Integer
            ("ASSIGN",    r"="),              # Assignment operator
            ("SEMICOLON", r";"),              # End of statement
            ("ID",        r"[a-zA-Z_][a-zA-Z_0-9]*"), # Identifiers
            ("OP",        r"[+\-*/]"),       # Arithmetic operators
            ("WHITESPACE", r"[ \t\n]+"),    # Skip over spaces and tabs
        ]

        token_regex = "|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in token_specification)
        for match in re.finditer(token_regex, self.source_code):
            token_type = match.lastgroup
            token_value = match.group()
            if token_type == "WHITESPACE":
                continue
            self.tokens.append(Token(token_type, token_value))

        return self.tokens

# ----------------------
# Syntax Analysis (Parser)
# ----------------------
class ASTNode:
    def __init__(self, type: str, value: Any, children: List[Any] = None):
        self.type = type
        self.value = value
        self.children = children or []

    def __repr__(self):
        return f"ASTNode({self.type}, {repr(self.value)}, {self.children})"

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self, token_type: str):
        if self.current_token() and self.current_token().type == token_type:
            self.pos += 1
        else:
            raise SyntaxError(f"Expected {token_type}, found {self.current_token()}")

    def parse(self):
        return self.parse_statements()

    def parse_statements(self):
        statements = []
        while self.current_token() is not None:
            statements.append(self.parse_statement())
        return ASTNode("STATEMENTS", None, statements)

    def parse_statement(self):
        if self.current_token().type == "ID":
            return self.parse_assignment()
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token()}")

    def parse_assignment(self):
        id_token = self.current_token()
        self.eat("ID")
        self.eat("ASSIGN")
        expr = self.parse_expression()
        self.eat("SEMICOLON")
        return ASTNode("ASSIGNMENT", id_token.value, [expr])

    def parse_expression(self):
        term = self.parse_term()
        while self.current_token() and self.current_token().type == "OP":
            op_token = self.current_token()
            self.eat("OP")
            term = ASTNode("BINARY_OP", op_token.value, [term, self.parse_term()])
        return term

    def parse_term(self):
        token = self.current_token()
        if token.type == "NUMBER":
            self.eat("NUMBER")
            return ASTNode("NUMBER", int(token.value))
        elif token.type == "ID":
            self.eat("ID")
            return ASTNode("ID", token.value)
        else:
            raise SyntaxError(f"Unexpected token: {token}")

# ----------------------
# Code Generation
# ----------------------
def generate_c_code(ast: ASTNode) -> str:
    if ast.type == "STATEMENTS":
        return "\n".join(generate_c_code(child) for child in ast.children)
    elif ast.type == "ASSIGNMENT":
        return f"int {ast.value} = {generate_c_code(ast.children[0])};"
    elif ast.type == "BINARY_OP":
        left = generate_c_code(ast.children[0])
        right = generate_c_code(ast.children[1])
        return f"({left} {ast.value} {right})"
    elif ast.type == "NUMBER":
        return str(ast.value)
    elif ast.type == "ID":
        return ast.value
    else:
        raise ValueError(f"Unknown AST node type: {ast.type}")

# ----------------------
# Main Function
# ----------------------
def main():
    source_code = """
    x = 5;
    y = x + 10;
    z = y * 2;
    """

    # Step 1: Lexical Analysis
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    print("Tokens:", tokens)

    # Step 2: Syntax Analysis
    parser = Parser(tokens)
    ast = parser.parse()
    print("AST:", ast)

    # Step 3: Code Generation
    c_code = generate_c_code(ast)
    print("Generated C Code:")
    print(c_code)

if __name__ == "__main__":
    main()
