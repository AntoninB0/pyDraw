import re

# Lexical analysis: Token definitions
TOKENS = [
    ("COMMENT", r"//.*"), 
    ("KEYWORD", r"\b(int|float|bool|string|pen|func|void|if|else|elseif|repeat|while|skip|leave|break|return|cursor|down|up|walk|goTo|jumpTo|rectangle|circle|triangleIso|rotateCW|rotateCCW|fillColor|initMatrix|clearMatrix|compareSDLColors|defineColor|approxPosX|approxPosY|approxPos|float2Rad|pixelColor|circleWrite|rotateArea|copyPaste|copy|paste|cut|translation|waitKey|closeEventSDL|renderMatrix|initSDL)\b"),
    ("OPERATOR", r"[=+\-*/><!&|]{1,2}"), 
    ("SYMBOL", r"[{}();,.]"),  
    ("NUMBER", r"\b\d+(\.\d+)?\b"),
    ("BOOL", r"\b(true|false)\b"),  
    ("STRING", r"\".*?\""),  
    ("PEN_ATTRIBUTE", r"\b(color|thickness|positionX|positionY|rotation|speed)\b"),
    ("IDENTIFIER", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),  
    ("WHITESPACE", r"[ \t\n]+"),  
]

def tokenize(code):
    tokens = []
    line_number = 1  # on commence à la ligne 1
    current_index = 0

    while current_index < len(code):
        match = None

        for token_type, pattern in TOKENS:
            regex = re.compile(pattern)
            match = regex.match(code, current_index)
            if match:
                value = match.group(0)
                # Comptage des sauts de ligne dans 'value'
                newlines = value.count('\n')

                if token_type not in ["WHITESPACE", "COMMENT"]:
                    tokens.append((token_type, value, line_number))

                line_number += newlines
                current_index += len(value)
                break
        if not match:
            # Caractère inattendu
            raise SyntaxError(f"Unexpected character '{code[current_index]}' at line {line_number}")

    return tokens
class SyntaxErrorWithLine(Exception):
    def __init__(self, line, message):
        super().__init__(message)
        self.line = line
        self.message = message

    def __str__(self):
        return f"Line {self.line}: {self.message}"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.variables = {}  # nom_variable -> type
        self.functions = {}  # nom_fonction -> type_retour

    def consume(self, expected_type):
        token_type, token_value, token_line = self.tokens[self.current]
        if self.current >= len(self.tokens):
            raise SyntaxError(f"Line {token_line}: Unexpected end of tokens, expected {expected_type}")

        token_type, token_value, token_line = self.tokens[self.current]
        if token_type == expected_type:
            self.current += 1
            return token_value
        else:
            raise SyntaxError(
                f"Line {token_line}: Expected {expected_type} but got {token_type} ('{token_value}')"
            )

    def parse_variable_declaration(self):
        token_type, token_value, token_line = self.tokens[self.current]
        var_type = self.consume("KEYWORD")  
        name = self.consume("IDENTIFIER")  
        self.consume("OPERATOR")  # '='

        # Vérifie si la variable existe déjà
        if name in self.variables:
            raise SyntaxErrorWithLine(token_line, f"Variable '{name}' already declared")

        # Vérifie si c'est un appel de fonction
        # On doit accéder à self.tokens[self.current] et self.tokens[self.current+1], chacun ayant 3 valeurs
        if (
            (self.tokens[self.current][0] in ["IDENTIFIER", "KEYWORD"])
            and self.tokens[self.current + 1][1] == "("
        ):
            # Appel de fonction
            next_token_type, next_token_val, next_token_line = self.tokens[self.current]
            if next_token_type == "IDENTIFIER":
                func_id = self.consume("IDENTIFIER")
                value = self.parse_function_call(func_id)
            else:
                func_kw = self.consume("KEYWORD")
                value = self.parse_function_call(func_kw)
        else:
            value = self.parse_expression()

        # S'il y a un ';'
        if self.current < len(self.tokens) and self.tokens[self.current][1] == ";":
            self.consume("SYMBOL")

        self.variables[name] = var_type

        return {
            "type": "var_decl",
            "var_type": var_type,
            "name": name,
            "value": value
        }

    def parse_pen_declaration(self):
        token_type, token_value, token_line = self.tokens[self.current]
        self.consume("KEYWORD")  # 'pen'
        name = self.consume("IDENTIFIER")
        if name in self.variables:
            raise SyntaxErrorWithLine(token_line, f"Variable '{name}' already declared")

        self.consume("OPERATOR")  # '='
        self.consume("KEYWORD")   # 'cursor'
        self.consume("SYMBOL")    # '('
        x = self.consume("NUMBER")  
        self.consume("SYMBOL")    # ','
        y = self.consume("NUMBER") 
        self.consume("SYMBOL")    # ')'
        self.consume("SYMBOL")    # ';'

        self.variables[name] = "pen"
        return {"type": "pen_decl", "name": name, "x": x, "y": y}

    def parse_pen_method(self, pen_name):
        token_type, token_value, token_line = self.tokens[self.current]
        # Vérifie la déclaration
        if pen_name not in self.variables:
            raise SyntaxErrorWithLine(token_line, f"Variable '{pen_name}' is not declared")
        if self.variables[pen_name] != "pen":
            raise SyntaxErrorWithLine(token_line, f"Variable '{pen_name}' is not a pen")

        self.consume("SYMBOL")  # '.'
        method = self.consume("KEYWORD")
        self.consume("SYMBOL")  # '('

        params = []
        if self.tokens[self.current][1] != ")":
            params.append(self.parse_expression())
            while self.tokens[self.current][1] == ",":
                self.consume("SYMBOL")
                params.append(self.parse_expression())

        self.consume("SYMBOL")  # ')'
        self.consume("SYMBOL")  # ';'

        return {"type": "method_call", "name": pen_name, "method": method, "params": params}

    def parse_pen_attribute(self, pen_name):
        token_type, token_value, token_line = self.tokens[self.current]
        if pen_name not in self.variables:
            raise SyntaxErrorWithLine(token_line, f"Variable '{pen_name}' is not declared")
        if self.variables[pen_name] != "pen":
            raise SyntaxErrorWithLine(token_line, f"Variable '{pen_name}' is not a pen")

        self.consume("SYMBOL")  # '.'
        attribute = self.consume("PEN_ATTRIBUTE")
        self.consume("OPERATOR")

        if attribute in ["rotation","speed","positionY","positionX","thickness"]:
            value = self.consume("NUMBER")
        elif attribute == "color":
            value = self.consume("STRING")
        else:
            raise SyntaxErrorWithLine(token_line, f"Variable '{attribute}' is not a valid pen attribute")

        self.consume("SYMBOL")  # ';'
        return {
            "type": "pen_attribute",
            "name": pen_name,
            "attribute": attribute,
            "value": value
        }

    def parse_function_call(self, func_name):
        token_type, token_value, token_line = self.tokens[self.current]
        if func_name not in self.functions:
            raise SyntaxErrorWithLine(token_line, f"Variable '{func_name}' is not declared")

        self.consume("SYMBOL")  # '('
        args = []
        while self.tokens[self.current][1] != ")":
            args.append(self.parse_expression())
            if self.tokens[self.current][1] == ",":
                self.consume("SYMBOL")
        self.consume("SYMBOL")  # ')'

        # Gère le ';' si présent
        if self.current < len(self.tokens) and self.tokens[self.current][1] == ";":
            self.consume("SYMBOL")
        return {"type": "function_call", "name": func_name, "args": args}

    def parse_function(self):
        token_type, token_value, token_line = self.tokens[self.current]
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
                self.consume("SYMBOL")

        self.consume("SYMBOL")  # ')'
        self.consume("SYMBOL")  # '{'

        body = []
        while self.tokens[self.current][1] != "}":
            body.append(self.parse_statement())

        self.consume("SYMBOL")  # '}'

        if name in self.functions:
            raise SyntaxErrorWithLine(token_line, f"Function '{name}' already declared")
        self.functions[name] = return_type

        return {
            "type": "function",
            "return_type": return_type,
            "name": name,
            "params": params,
            "body": body
        }

    def parse_repeat(self):
        self.consume("KEYWORD")  
        self.consume("SYMBOL")  
        init = self.parse_expression()
        self.consume("SYMBOL")  
        condition = self.parse_expression()
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
                elseif_condition = self.parse_expression()
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

    def parse_condition_methode(self):
        token_type, token_value, token_line = self.tokens[self.current]
        if token_type == "KEYWORD":
            methode = self.consume("KEYWORD")
            self.consume("SYMBOL")  
            return {"type": "methode", "methode": methode}

    def parse_increment(self):
        name, var_line = self._consume_identifier_checked()
        operation_type, operation_val, operation_line = self.tokens[self.current]
        if operation_type != "OPERATOR" or operation_val not in ["++","--"]:
            raise SyntaxErrorWithLine(operation_line, f"Unexpected increment operation : '{operation_val}'")
        self.current += 1

        return {"type": "short_operation", "name": name, "operation": operation_val}

    def parse_short_operation(self):
        name, var_line = self._consume_identifier_checked()
        operation_type, operation_val, operation_line = self.tokens[self.current]
        if operation_type != "OPERATOR" or operation_val not in ["++","--"]:
            raise SyntaxErrorWithLine(operation_line, f"Unexpected operation '{operation_val}'")

        self.current += 1
        # consomme le ';'
        if self.current < len(self.tokens) and self.tokens[self.current][1] == ";":
            self.consume("SYMBOL")

        return {"type": "short_operation", "name": name, "operation": operation_val}

    def parse_assignment(self):
        token_type, left, token_line = self.tokens[self.current]
        if token_type != "IDENTIFIER":
            raise SyntaxErrorWithLine(token_line, f"Expected variable name, got {left}")

        # Vérifier la variable
        if left not in self.variables:
            raise SyntaxErrorWithLine(token_line, f"Variable '{left}' is not declared before use (assignment)")

        self.current += 1  # consomme l'identifiant

        op_type, op_val, op_line = self.tokens[self.current]
        if op_type != "OPERATOR" or op_val != "=":
            raise SyntaxErrorWithLine(op_line, f"Expected '=' for assignment, got {op_val}")
        self.current += 1

        right = self.parse_expression()

        # on consomme éventuellement le ';'
        if self.current < len(self.tokens) and self.tokens[self.current][1] == ";":
            self.consume("SYMBOL")

        return {"type": "assignment", "left": left, "right": right}

    def parse_expression(self):
        left = self.parse_term()
        while self.current < len(self.tokens):
            token_type, token_value, token_line = self._current_token()
            if token_type == "OPERATOR":
                op_val = self.consume("OPERATOR")
                right = self.parse_term()
                if op_val == "&":
                    op_val = " and "
                elif op_val == "|":
                    op_val = " or "
                left = f"{left}{op_val}{right}"
            else:
                break
        return left

    def parse_term(self):
        token_type, token_value, token_line = self._current_token()
        if token_type in ["IDENTIFIER","NUMBER"]:
            # Vérification pour IDENTIFIER
            # si c'est un identifiant non déclaré, potentiellement lever une erreur
            self.current += 1
            return token_value
        elif token_value == "(":
            self.consume("SYMBOL")
            expr = self.parse_expression()
            self.consume("SYMBOL")
            return f"({expr})"
        else:
            raise SyntaxErrorWithLine(token_line, f"Unexpected token in term: {token_value}")

    def parse_sdl_function(self):
        func_name_type, func_name_val, func_line = self.tokens[self.current]
        if func_name_type != "KEYWORD":
            raise SyntaxErrorWithLine(func_line, f"Expected SDL function name, got '{func_name_val}'")
        

        self.current += 1  # consomme le nom de la fonction

        # '('
        self.consume("SYMBOL")
        args = []
        while self.tokens[self.current][1] != ")":
            args.append(self.parse_expression())
            if self.tokens[self.current][1] == ",":
                self.consume("SYMBOL")
        self.consume("SYMBOL")  # ')'
        # ';'
        if self.tokens[self.current][1] == ";":
            self.consume("SYMBOL")

        return {
            "type": "sdl_function_call",
            "name": func_name_val,
            "args": args
        }

    def parse_statement(self):
        token_type, token_value, token_line = self._current_token()
        next_token_type, next_token_value, next_token_line = self.tokens[self.current+1] if (self.current+1) < len(self.tokens) else (None,None,None)

        # Fonctions SDL
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
            self.current += 1  # consomme l'identifiant
            if pen_name_val not in self.variables:
                raise SyntaxErrorWithLine(pen_name_line, f"Pen '{pen_name_val}' not declared.")
            # peek sur la suite
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
            value = self.parse_expression()
            if self.current < len(self.tokens) and self.tokens[self.current][1] == ";":
                self.consume("SYMBOL")  
            return {"type": "return", "value": value}
        elif token_type == "KEYWORD" and token_value == "repeat":
            return self.parse_repeat()
        elif token_type == "KEYWORD" and token_value == "if":
            return self.parse_condition()
        elif token_type == "KEYWORD" and token_value in ["skip","leave","break"]:
            return self.parse_condition_methode()

        # short op
        elif token_type == "IDENTIFIER":
            # x++ / x--
            if next_token_value in ["++","--"]:
                return self.parse_short_operation()
            else:
                return self.parse_assignment()
        else:
            raise SyntaxErrorWithLine(token_line, f"Unexpected token in statement: {token_value}")

    def _current_token(self):
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        else:
            return (None, None, None)

    def _consume_identifier_checked(self):
        token_type, token_value, token_line = self.tokens[self.current]
        if token_type != "IDENTIFIER":
            raise SyntaxErrorWithLine(token_line, f"Expected identifier, got '{token_value}'")
        if token_value not in self.variables:
            raise SyntaxErrorWithLine(token_line, f"Variable '{token_value}' is not declared.")
        self.current += 1
        return token_value, token_line

    def parse(self):
        ast = []
        self.variables = {}
        self.functions = {}

        while self.current < len(self.tokens):
            statement = self.parse_statement()
            ast.append(statement)
        return ast

def generate_c_code(ast):
    c_code = []
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
            c_code.append(f"{node['name']}({args});")
        elif node["type"] == "sdl_function_call":
            func_name = node["name"]
            args = ", ".join(node["args"])
            c_code.append(f"{func_name}({args});")
        elif node["type"] == "function":
            params = ", ".join([f"{ptype} {pname}" for ptype, pname in node.get("params", [])])
            body_str = generate_c_code(node.get("body", []))
            c_code.append(f"{node['return_type']} {node['name']}({params}) {{\n{body_str}\n}}")
        elif node["type"] == "return":
            c_code.append(f"return {node['value']};")
        elif node["type"] == "assignment":
            left = node["left"]
            right = node["right"]
            c_code.append(f"{left} = {right};")
        elif node["type"] == "methode":
            methode = node["methode"]
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
            body_str = generate_c_code(node["body"])
            c_code.append(f"for ({init}; {condition}; {incr_var}{incr_op}) {{\n{body_str}\n}}")
        elif node["type"] == "if":
            condition = node["condition"]
            body_str = generate_c_code(node["body"])
            c_code.append(f"if ({condition}) {{\n{body_str}\n}}")
            if node.get("elseif"):
                for elif_block in node["elseif"]:
                    elif_cond = elif_block["condition"]
                    elif_body = generate_c_code(elif_block["body"])
                    c_code.append(f"else if ({elif_cond}) {{\n{elif_body}\n}}")
            if node.get("else"):
                else_body = generate_c_code(node["else"])
                c_code.append(f"else {{\n{else_body}\n}}")
        elif node["type"] == "pen_attribute":
            c_code.append(f"{node['name']}.{node['attribute']} = {node['value']};")
        elif node["type"] == "method_call":
            params = ", ".join(map(str, node["params"]))  
            if len(node["params"]) > 0:
                c_code.append(f"{node['method']}({node['name']},{params});")
            else:
                c_code.append(f"{node['method']}({node['name']});")
        else:
            raise ValueError(f"Unknown AST node type: {node['type']};")

    return "\n".join(c_code)

def read_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def write_file(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def main(input_file, output_file):
    try:
        pydraw_code = read_file(input_file)
        tokens = tokenize(pydraw_code)
        parser = Parser(tokens)
        
        ast = parser.parse()
        c_code = generate_c_code(ast)
        write_file(output_file, c_code)
        print(f"Compilation successful! C code has been generated in {output_file}.")
    except SyntaxErrorWithLine as e:
        print(e.line)
        print(e.message)
        return {e.line: e.message}
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main("test.txt", "output.c")
