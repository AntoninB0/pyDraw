import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import platform  # Pour détecter le système d'exploitation
from compiler import main
       
class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Éditeur de Texte")
       
        # Suivi de l'état du thème
        self.is_dark_theme = True
       
        self.menu = tk.Menu(root)
        root.config(menu=self.menu)
       
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Fichier", menu=self.file_menu)
        self.file_menu.add_command(label="Nouveau", command=self.new_file)
        self.file_menu.add_command(label="Ouvrir", command=self.open_file)
        self.file_menu.add_command(label="Enregistrer", command=self.save_file)
        self.file_menu.add_command(label="Enregistrer sous", command=self.save_file_as)
        self.file_menu.add_command(label="Changer de thème", command=self.toggle_theme)  # Changer de thème
        self.file_menu.add_separator()
        # Barre de boutons pour le debug
        self.toolbar = tk.Frame(root)
        self.toolbar.pack(side='top', fill='x')
       
        self.debug_button = tk.Button(self.toolbar, text="Debug", command=self.debug)
        self.debug_button.pack(side='left')
        # Créer un canvas pour dessiner un triangle vert
        self.triangle_canvas = tk.Canvas(self.toolbar, width=30, height=30)
        self.triangle_canvas.pack(side='left')
        # Dessiner le triangle vert
        self.triangle_canvas.create_polygon(5, 25, 25, 25, 15, 5, fill='green', outline='black')
       
        # Lier l'action de clic sur le triangle à extra_action
        self.triangle_canvas.bind("<Button-1>", lambda event: self.run_action())
               
        # Ajouter le bouton Fermer
        self.close_button = tk.Button(self.toolbar, text="Fermer l'onglet", command=self.close_tab)
        self.close_button.pack(side='right')
               
               
       
        self.clear_button = tk.Button(self.toolbar, text="Clear", command=self.clear_terminal)
        self.clear_button.pack(side='right')
       
        # PanedWindow pour gérer le redimensionnement
        self.paned_window = tk.PanedWindow(root, orient=tk.VERTICAL)
        self.paned_window.pack(fill='both', expand=True)
       
        # Frame pour l'éditeur de texte
        self.text_frame = tk.Frame(self.paned_window)
        self.notebook = ttk.Notebook(self.text_frame)
        self.notebook.pack(fill='both', expand=True)
        self.paned_window.add(self.text_frame, minsize=100)  # Taille minimale
               
       
        self.current_file = None
        self.open_files = []
        self.line_states = {}
        self.line_underlignes = {}
       
        # Frame pour le terminal
        self.terminal_frame = tk.Frame(self.paned_window)
        self.terminal = tk.Text(self.terminal_frame, height=5, state='normal', bg='#252539', fg='white')
        self.terminal.pack(fill='both', expand=True)
       
        # Ajoutez le terminal_frame au paned_window
        self.paned_window.add(self.terminal_frame, minsize=50)
       
        self.open_default_file()
               
    def close_tab(self):
        # Récupérer l'index de l'onglet actif
        current_tab_index = self.notebook.index(self.notebook.select())
        current_tab = self.open_files[current_tab_index]
               
        # Vérifier si l'onglet est fermable
        if current_tab['closable']:
            # Supprimer l'onglet du Notebook et de la liste
            self.notebook.forget(current_tab['frame'])
            self.open_files.pop(current_tab_index)
        else:
            messagebox.showwarning("Action interdite", "Cet onglet ne peut pas être fermé.")
               
    def save_file(self):
        current_tab = self.notebook.index(self.notebook.select())
        if self.open_files[current_tab]['file_path']:
            with open(self.open_files[current_tab]['file_path'], 'w') as file:
                file.write(self.open_files[current_tab]['text_widget'].get(1.0, tk.END))
        else:
            self.save_file_as()
           
    def save_file_as(self):
        # Obtenir l'index de l'onglet actuel
        current_tab_index = self.notebook.index(self.notebook.select())
        current_tab = self.open_files[current_tab_index]
           
        # Demander à l'utilisateur de choisir où sauvegarder le fichier
        file_path = filedialog.asksaveasfilename(defaultextension=".pd", filetypes=[("Text files", "*.pd"), ("All files", "*.*")])
        if file_path:
            # Sauvegarder le contenu dans le nouveau fichier
            with open(file_path, 'w') as file:
                file.write(current_tab['text_widget'].get(1.0, tk.END))
           
            # Fermer l'onglet actuel
            self.close_tab()
           
       
    def toggle_theme(self):
        """Alterner entre thème clair et sombre."""
        if self.is_dark_theme:
            # Passer au thème clair
            self.root.configure(bg="white")
            self.terminal.configure(bg="white", fg="black")
            for tab in self.open_files:
                tab['text_widget'].configure(bg="white", fg="black")
            self.is_dark_theme = False
        else:
            # Passer au thème sombre
            self.root.configure(bg='#252539')
            self.terminal.configure(bg='#252539', fg="white")
            for tab in self.open_files:
                tab['text_widget'].configure(bg='#252539', fg="white")
            self.is_dark_theme = True
       
    def open_default_file(self):
        file_path = "doc.txt"
        text_frame = tk.Frame(self.notebook)
        text_widget = tk.Text(text_frame, wrap='word', state='disabled', bg='#252539', fg='white')  # Couleurs du thème
        text_widget.pack(side='right', fill='both', expand=True)
       
        line_numbers = tk.Canvas(text_frame, width=50)
        line_numbers.pack(side='left', fill='y')
       
        text_widget.bind('<KeyRelease>', lambda event: self.update_line_numbers(text_widget, line_numbers))
        text_widget.bind('<Configure>', lambda event: self.update_line_numbers(text_widget, line_numbers))
        text_widget.bind('<MouseWheel>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
        text_widget.bind('<Button-4>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
        text_widget.bind('<Button-5>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
        line_numbers.bind('<MouseWheel>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
        try:
            with open(file_path, 'r') as file:
                text_widget.config(state='normal')
                text_widget.insert(tk.END, file.read())
                text_widget.config(state='disabled')
       
                # Forcer la mise à jour des numéros de ligne après le chargement du fichier
                self.update_line_numbers(text_widget, line_numbers)
       
        except FileNotFoundError:
            messagebox.showerror("Erreur", f"Le fichier {file_path} n'a pas été trouvé.")
       
        self.notebook.add(text_frame, text=file_path)
        self.open_files.append({'text_widget': text_widget, 'line_numbers': line_numbers, 'file_path': file_path, 'frame': text_frame, 'closable': False})
       
        # Initialiser l'état des lignes pour ce fichier
        self.line_states[file_path] = {}
        self.line_underlignes[file_path] = {}



    def open_file(self, file_path='None'):
            # Si file_path n'est pas spécifié, ouvrir la boîte de dialogue pour sélectionner un fichier
            if file_path == 'None':
                file_paths = filedialog.askopenfilenames(defaultextension=".pd", filetypes=[("Text files", "*.pd"), ("All files", "*.*")])
            if not file_paths:
                return  # Si aucun fichier n'est sélectionné, quitter la fonction
                   
            # Initialiser l'état des lignes pour ce fichier
            self.line_states[file_path] = {}
            self.line_underlignes[file_path] = {}
           
            # Créer un nouveau cadre pour l'onglet
            text_frame = tk.Frame(self.notebook)
            text_widget = tk.Text(text_frame, wrap='word', bg='#252539', fg='white')  # Couleurs du thème
            text_widget.pack(side='right', fill='both', expand=True)
           
            # Canvas pour les numéros de ligne
            line_numbers = tk.Canvas(text_frame, width=50)
            line_numbers.pack(side='left', fill='y')
           
            # Liens d'événements pour la mise à jour des numéros de ligne
            text_widget.bind('<KeyRelease>', lambda event: self.update_line_numbers(text_widget, line_numbers))
            text_widget.bind('<Configure>', lambda event: self.update_line_numbers(text_widget, line_numbers))
            line_numbers.bind('<Button-1>', lambda event: self.on_line_number_click(text_widget, line_numbers, event, None))
            text_widget.bind('<MouseWheel>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
            line_numbers.bind('<MouseWheel>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
           
            # Ouvrir le fichier et insérer son contenu dans le Text widget
            with open(file_path, 'r') as file:
                text_widget.insert(tk.END, file.read())
                text_widget.insert(tk.END, "\n")  # Ajoute un retour à la ligne
           
            # Mettre à jour les numéros de ligne immédiatement après l'ouverture du fichier
            self.update_line_numbers(text_widget, line_numbers)
           
            # Ajouter l'onglet au notebook
            self.notebook.add(text_frame, text=file_path)




    def new_file(self):
        # Générer un nom temporaire unique pour le fichier
        new_file_index = len(self.open_files) + 1
        new_file_name = f"Nouveau {new_file_index}"
               
        # Créer un nouveau cadre pour l'onglet
        text_frame = tk.Frame(self.notebook)
        text_widget = tk.Text(text_frame, wrap='word', bg='#252539', fg='white')  # Couleurs du thème
        text_widget.pack(side='right', fill='both', expand=True)
           
        # Canvas pour les numéros de ligne
        line_numbers = tk.Canvas(text_frame, width=50)
        line_numbers.pack(side='left', fill='y')
           
        text_widget.bind('<KeyRelease>', lambda event: self.update_line_numbers(text_widget, line_numbers))
        text_widget.bind('<Configure>', lambda event: self.update_line_numbers(text_widget, line_numbers))
        text_widget.bind('<MouseWheel>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
        text_widget.bind('<Button-4>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
        text_widget.bind('<Button-5>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
        line_numbers.bind('<MouseWheel>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
           
        # Ajouter l'onglet au notebook
        self.notebook.add(text_frame, text=new_file_name)
        self.open_files.append({'text_widget': text_widget, 'line_numbers': line_numbers, 'file_path': None, 'frame': text_frame, 'closable': True})
           
        # Initialiser l'état des lignes pour ce fichier
        self.line_states[new_file_name] = {}
        self.line_underlignes[new_file_name] = {}
               
        # Forcer la mise à jour des numéros de ligne dans le nouvel onglet
        self.update_line_numbers(text_widget, line_numbers)



       
    def open_file(self,file_path = None):
        if file_path == None:
            file_paths = filedialog.askopenfilenames(defaultextension=".pd", filetypes=[("Text files", "*.pd"), ("All files", "*.*")])
        print(file_path)
        if file_paths:
            for file_path in file_paths:
                # Initialiser l'état des lignes pour ce fichier
                self.line_states[file_path] = {}
                self.line_underlignes[file_path] = {}
                text_frame = tk.Frame(self.notebook)
                text_widget = tk.Text(text_frame, wrap='word', bg='#252539', fg='white')  # Couleurs du thème
                text_widget.pack(side='right', fill='both', expand=True)
           
                line_numbers = tk.Canvas(text_frame, width=50)
                line_numbers.pack(side='left', fill='y')
                text_widget.bind('<KeyRelease>', lambda event: self.update_line_numbers(text_widget, line_numbers))
                text_widget.bind('<Configure>', lambda event: self.update_line_numbers(text_widget, line_numbers))
                line_numbers.bind('<Button-1>', lambda event: self.on_line_number_click(text_widget, line_numbers, event, None))
                text_widget.bind('<MouseWheel>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
                text_widget.bind('<Button-4>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
                text_widget.bind('<Button-5>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
                line_numbers.bind('<MouseWheel>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
                with open(file_path, 'r') as file:
                    text_widget.insert(tk.END, file.read())
                    text_widget.insert(tk.END, "\n")  # Ajoute un retour à la ligne
           
                # Mettre à jour les numéros de ligne immédiatement après l'ouverture du fichier
                self.update_line_numbers(text_widget, line_numbers)
           
           
                self.notebook.add(text_frame, text=file_path)
                self.open_files.append({'text_widget': text_widget, 'line_numbers': line_numbers, 'file_path': file_path, 'frame': text_frame, 'closable': True})
           
                       
       
       
    def update_line_numbers(self, text_widget, line_numbers):
        # Récupérer l'index de l'onglet sélectionné
        selected_tab = self.notebook.select()
        if not selected_tab:
            return
           
        current_tab_index = self.notebook.index(selected_tab)
        file_path = self.open_files[current_tab_index]['file_path'] or f"Tab_{current_tab_index}"
        if file_path not in self.line_states:
            self.line_states[file_path] = {}
        # Supprimer les anciens numéros de ligne
        line_numbers.delete('all')
           
        # Mise à jour des numéros avec gestion des états
        i = text_widget.index("@0,0")
        while True:
            dline = text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            line_num = str(i).split(".")[0]
           
            # Déterminer la couleur en fonction de l'état
            state = self.line_states[file_path].get(line_num, False)
            color = "green" if state else "black"
           
            # Ajouter le texte du numéro de ligne
            line_numbers.create_text(2, y, anchor="nw", text=line_num, fill=color, font=("Helvetica", 10))
           
            i = text_widget.index(f"{i}+1line")
                   

               
               
    def update_underlignes(self, text_widget,file_path):
        # Récupérer l'index de l'onglet sélectionné
        selected_tab = self.notebook.select()
        if not selected_tab:
            return
           
        current_tab_index = self.notebook.index(selected_tab)
        file_path = self.open_files[current_tab_index]['file_path'] or f"Tab_{current_tab_index}"
           
        # Effacer toutes les balises existantes pour éviter les duplications
        text_widget.tag_remove("underline", "1.0", "end")
           
        # Ajouter les soulignements aux lignes spécifiées
        for line_num, underline in self.line_underlignes[file_path].items():
            if underline:
                text_widget.tag_add("underline", f"{line_num}.0", f"{line_num}.end")
           
        # Configurer la balise de soulignement
        text_widget.tag_configure("underline", underline=True)

  
    def on_line_number_click(self, text_widget, line_numbers, event, file_path):
        # Identifier l'onglet actif
        current_tab_index = self.notebook.index(self.notebook.select())
        file_path = file_path or self.open_files[current_tab_index]['file_path'] or f"Tab_{current_tab_index}"
               
        # Identifier la ligne cliquée
        i = text_widget.index("@0,0")
        while True:
            dline = text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            if y <= event.y <= y + dline[3]:
                line_num = str(i).split(".")[0]
                current_state = self.line_states[file_path].get(line_num, False)
                self.line_states[file_path][line_num] = not current_state
                self.update_line_numbers(text_widget, line_numbers)
                break
            i = text_widget.index(f"{i}+1line")
   
       
       
    def on_mouse_wheel(self, event, text_widget, line_numbers):
        if platform.system() == "Linux":
            # Gestion spécifique pour Linux
            if event.num == 4:  # Molette haut
                text_widget.yview_scroll(-1, 'units')
            elif event.num == 5:  # Molette bas
                text_widget.yview_scroll(1, 'units')
        else:
            # Pour Windows et autres plateformes
            text_widget.yview_scroll(int(-1 * (event.delta / 120)), 'units')
           
        # Synchroniser les numéros de ligne
        line_numbers.yview_moveto(text_widget.yview()[0])
        self.update_line_numbers(text_widget, line_numbers)
   
   
       
    def debug(self):
        # Récupère l'onglet courant et le fichier associé
        current_tab = self.notebook.index(self.notebook.select())
        current_file = self.open_files[current_tab]['file_path']
        if current_file :
            if current_file != "doc.txt":
                # Trouve toutes les lignes en état "on"
                on_lines = [line_num for line_num, state in self.line_states[current_file].items() if state]
                underlined_lines = [line_num for line_num, underline in self.line_underlignes[current_file].items() if underline]
                    
                # Affiche les lignes "on" et soulignées dans le terminal
                if on_lines:
                    self.terminal.insert(tk.END, f"Lignes en état 'on': {', '.join(on_lines)}\n")
                else:
                    self.terminal.insert(tk.END, "Aucune ligne en état 'on'.\n")
                    
                if underlined_lines:
                    self.terminal.insert(tk.END, f"Lignes soulignées : {', '.join(underlined_lines)}\n")
                else:
                    self.terminal.insert(tk.END, "Aucune ligne soulignée.\n")

       
    def run_action(self):
        # Identifier l'onglet actif
        current_tab_index = self.notebook.index(self.notebook.select())
        current_tab = self.open_files[current_tab_index]
        # Récupérer le fichier et le widget texte de l'onglet actif
        file_path = current_tab['file_path']
        result = main.main(file_path,"output.c")   
        text_widget = current_tab['text_widget']
        if file_path :
            if file_path != "doc.txt":
                if result != None :
                    for key in result:
                        # Ajouter des lignes à souligner
                        self.line_underlignes[file_path][key] = True
                        # Appeler update_underlignes pour mettre à jour les soulignements
                        self.update_underlignes(text_widget, file_path)
                        # Insérer un message dans le terminal
                        self.terminal.insert(tk.END, f"LIGNE : {key}, ERROR : {result[key]}\n")
                        
                else : 
                    self.terminal.insert(tk.END, "Compilation successful! C code has been generated in output.c")

       
    def clear_terminal(self):
        self.terminal.delete('1.0', tk.END)
       
if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()
