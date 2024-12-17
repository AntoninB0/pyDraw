# Gestion des erreurs
class ErrorManager:
    def __init__(self):
        self.errors = []

    def add_error(self, error_message):
        self.errors.append(error_message)

    def display_errors(self):
        if not self.errors:
            print("✅ Aucune erreur détectée.")
        else:
            print("\n=== 🚩 Erreurs détectées ===")
            for error in self.errors:
                print(f"- {error}")
            print("===========================\n")

    def clear_errors(self):
        self.errors = []


# Compilateur intégré
class Compiler:
    def __init__(self):
        self.error_manager = ErrorManager()
        self.valid_tokens = ["int", "float", "=", ";", "pen", "curseurStylo"]  # Ajout de commandes
        self.variables = {}  # Stockage des variables déclarées

    def analyze_lexical(self, tokens):
        for token in tokens:
            if not (token.isidentifier() or token.isnumeric() or token in self.valid_tokens):
                self.error_manager.add_error(f"Erreur lexicale : Token invalide '{token}'")

    def analyze_syntax(self, tokens):
        if tokens[0] == "pen" or tokens[0] == "curseurStylo":
            return  # Commande spéciale : on l'ignore pour le moment

        if "=" in tokens:  # Vérification pour les déclarations ou réaffectations
            if tokens[-1] != ";":
                self.error_manager.add_error("Erreur syntaxique : Il manque un ';' à la fin de la ligne.")
        else:
            self.error_manager.add_error("Erreur syntaxique : Ligne non reconnue.")

    def analyze_semantic(self, tokens):
        try:
            if tokens[0] == "pen" or tokens[0] == "curseurStylo":
                print(f"✏️ Commande '{tokens[0]}' exécutée.")
                return

            if tokens[1] == "=":  # Réaffectation de variable
                var_name = tokens[0]
                value = tokens[2]

                if var_name not in self.variables:
                    self.error_manager.add_error(f"Erreur sémantique : La variable '{var_name}' n'a pas été déclarée.")
                else:
                    var_type = self.variables[var_name]["type"]
                    if var_type == "int" and not value.isdigit():
                        self.error_manager.add_error(f"Erreur sémantique : '{value}' n'est pas un entier valide.")
                    elif var_type == "float" and not self.is_float(value):
                        self.error_manager.add_error(f"Erreur sémantique : '{value}' n'est pas un flottant valide.")
                    else:
                        self.variables[var_name]["value"] = value  # Mise à jour de la valeur

            elif tokens[0] in ["int", "float"]:  # Déclaration de variable
                var_type = tokens[0]
                var_name = tokens[1]
                value = tokens[3]

                if var_name in self.variables:
                    self.error_manager.add_error(f"Erreur sémantique : La variable '{var_name}' est déjà déclarée.")
                else:
                    if var_type == "int" and not value.isdigit():
                        self.error_manager.add_error(f"Erreur sémantique : La valeur de '{var_name}' n'est pas un entier valide.")
                    elif var_type == "float" and not self.is_float(value):
                        self.error_manager.add_error(f"Erreur sémantique : La valeur de '{var_name}' n'est pas un flottant valide.")
                    else:
                        self.variables[var_name] = {"type": var_type, "value": value}
        except Exception as e:
            self.error_manager.add_error(f"Erreur inconnue : {str(e)}")

    @staticmethod
    def is_float(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def compile(self, code_source):
        self.error_manager.clear_errors()

        # Diviser le code en lignes
        lines = code_source.split("\n")

        # Analyser chaque ligne
        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue  # Ignore les lignes vides
            print(f"🔍 Analyse de la ligne {line_number} : {line.strip()}")

            tokens = line.strip().split()
            self.analyze_lexical(tokens)
            self.analyze_syntax(tokens)
            self.analyze_semantic(tokens)

        # Affichage des erreurs
        self.error_manager.display_errors()

        if not self.error_manager.errors:
            print("🎉 Compilation réussie !")


# Interface principale (IDE simplifié)
def main():
    print("=== Bienvenue dans votre IDE avec Compilateur Intégré ===")
    compiler = Compiler()

    while True:
        print("\n1. Compiler un code source")
        print("2. Quitter")
        choice = input("Entrez votre choix : ")

        if choice == "1":
            print("\n--- Entrez votre code source ligne par ligne ---")
            print("(Tapez 'FIN' pour terminer l'entrée du code)")
            code_source = ""
            while True:
                line = input("> ")
                if line.strip().upper() == "FIN":
                    break
                code_source += line + "\n"

            # Compiler le code source
            compiler.compile(code_source)
        elif choice == "2":
            print("👋 Au revoir !")
            break
        else:
            print("Choix invalide. Veuillez réessayer.")


if __name__ == "__main__":
    main()
