import tkinter as tk
from tkinter import filedialog, messagebox, Text
from tkinter import ttk
import subprocess
import platform

# Fonction pour exécuter le programme C (dessin progressif d'une ligne)
def execute_c_program():
    # Le chemin du fichier C
    c_file_path = filedialog.askopenfilename(defaultextension=".c", 
                                             filetypes=[("C Files", "*.c"), ("All Files", "*.*")])
    if not c_file_path:
        return
    
    # Nom de l'exécutable à générer
    output_file = "draw_line"
    if platform.system() == "Windows":
        output_file += ".exe"  # Extension pour Windows
    
    # Commande de compilation
    compile_command = []
    if platform.system() == "Linux":
        compile_command = ["gcc", c_file_path, "-o", output_file, "-lSDL2"]
    elif platform.system() == "Windows":
        compile_command = ["gcc", c_file_path, "-o", output_file, "-lmingw32", "-lSDL2main", "-lSDL2"]
    
    # Compilation
    try:
        subprocess.run(compile_command, check=True)
        messagebox.showinfo("Succès", f"Compilation réussie ! Exécutable : {output_file}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erreur", f"Erreur lors de la compilation : {e}")
        return

    # Exécution du programme C compilé
    try:
        if platform.system() == "Linux":
            subprocess.Popen(["./" + output_file])
        elif platform.system() == "Windows":
            subprocess.Popen([output_file])
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'exécution : {e}")

# Fonction pour créer un fichier vide
def create_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                             filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, 'w') as new_file:
            new_file.write('')  # Créer un fichier vide
        messagebox.showinfo("Succès", f"Le fichier a été créé: {file_path}")
# Fonction pour ouvrir et éditer un fichier existant (y compris les fichiers .c)
def open_file():
    file_path = filedialog.askopenfilename(defaultextension=".txt", 
                                           filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if not file_path:
        return

    # Créer un nouvel onglet
    tab = ttk.Frame(notebook)
    
    # Ajouter un onglet avec un titre
    tab_title = file_path.split("/")[-1] + "   "  # Espace ajouté pour le bouton
    notebook.add(tab, text=tab_title)
    
    # Cadre pour le contenu du fichier et le bouton de fermeture
    content_frame = tk.Frame(tab)
    content_frame.pack(expand=True, fill='both', padx=10, pady=10)

    # Barre de défilement
    scrollbar = tk.Scrollbar(content_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Zone de texte avec numéros de ligne
    listbox = tk.Listbox(content_frame, width=4, height=15, font=("Arial", 12),)  # Taille de la police réduite
    listbox.pack(side=tk.LEFT, fill=tk.Y)

    text_area = Text(content_frame, wrap=tk.WORD, font=("Arial", 12), bg="#e0e0e0", fg="#333333", padx=10, pady=20, spacing1=1, yscrollcommand=scrollbar.set)
    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Lier la scrollbar à la zone de texte et à la listbox
    scrollbar.config(command=lambda *args: (text_area.yview(*args), listbox.yview(*args)))

    # Synchroniser le défilement entre la zone de texte et la listbox
    def on_text_scroll(*args):
        listbox.yview_moveto(args[0])

    def on_listbox_scroll(*args):
        text_area.yview_moveto(args[0])

    # Lier les événements de défilement
    text_area.config(yscrollcommand=on_text_scroll)
    listbox.config(yscrollcommand=on_listbox_scroll)

    # Charger le contenu du fichier dans la zone de texte
    with open(file_path, 'r') as file:
        content = file.read()
        text_area.insert(tk.END, content)
    
    # Liste pour garder la trace des lignes cliquées
    clicked_lines = []

    # Fonction pour mettre à jour les numéros de ligne
    def mettre_a_jour_numeros_lignes(event=None):
        contenu = text_area.get("1.0", tk.END)
        lignes = contenu.count("\n") + 1  # Compter les lignes
        listbox.delete(0, tk.END)  # Supprimer les anciens numéros
        for i in range(0, lignes + 1):
            if i == 0:
                listbox.insert(tk.END, " ")
            else:
                listbox.insert(tk.END, str(i))  # Ajouter chaque numéro de ligne

        # Appliquer la couleur verte aux lignes cliquées
        for ligne in clicked_lines:
            listbox.itemconfig(ligne, {'bg': 'green', 'fg': 'white'})

    # Fonction appelée lorsqu'un numéro de ligne est cliqué
    def afficher_numero_ligne(event):
        selection = listbox.curselection()
        if selection:
            ligne = selection[0]  # Les indices commencent à 0
            if ligne > 0:  # Ignorer la ligne 0 (vide)
                if ligne in clicked_lines:
                    clicked_lines.remove(ligne)
                    print(f"Ligne désactivée : {ligne}")
                else:
                    clicked_lines.append(ligne)
                    print(f"Ligne activée : {ligne}")
                mettre_a_jour_numeros_lignes()  # Mettre à jour l'affichage

    # Lier l'événement du clic sur un numéro de ligne
    listbox.bind("<ButtonRelease-1>", afficher_numero_ligne)

    # Mettre à jour les numéros de ligne à chaque modification du texte
    text_area.bind("<KeyRelease>", mettre_a_jour_numeros_lignes)

    # Initialiser les numéros de ligne
    mettre_a_jour_numeros_lignes()

    # Ajouter un bouton de fermeture en haut à droite
    close_button = tk.Button(content_frame, text="✕", command=lambda: close_tab(tab), 
                             bg="#F44336", fg="white", font=("Arial", 12, "bold"), bd=0, width=3)
    close_button.place(relx=0.95, rely=0.05)  # Positionnement en haut à droite du cadre

    # Bouton d'enregistrement sous la zone de texte
    save_button = tk.Button(content_frame, text="Enregistrer", bg="#4CAF50", fg="white", width=15,
                        command=lambda: save_changes(file_path, text_area))
    save_button.place(relx=0.5, rely=1.0, anchor="s", y=-10)  # Placer le bouton en bas au centre

# Fonction pour fermer un onglet
def close_tab(tab):
    index = notebook.index(tab)
    notebook.forget(index)

# Fonction pour enregistrer les modifications du fichier
def save_changes(file_path, text_area):
    with open(file_path, 'w') as file:
        file.write(text_area.get("1.0", tk.END))
    messagebox.showinfo("Succès", f"Modifications enregistrées dans: {file_path}")

# Fonction pour quitter l'application
def quit_application():
    root.destroy()

# Fenêtre principale
root = tk.Tk()
root.title("Gestionnaire de fichiers")

# Récupérer la largeur et la hauteur de l'écran
largeur_ecran = root.winfo_screenwidth()
hauteur_ecran = root.winfo_screenheight()

# Définir la taille de la fenêtre en fonction de la résolution de l'écran
root.geometry(f"{largeur_ecran}x{hauteur_ecran}")

root.configure(bg='#d0e1f9')

# Création d'un Notebook pour les onglets
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", padx=10, pady=10)

# Cadre pour les boutons principaux
button_frame = tk.Frame(root, bg='#d0e1f9')
button_frame.pack(pady=5)  # Réduire le padding ici

# Bouton pour créer un fichier
create_button = tk.Button(button_frame, text="Créer un fichier", command=create_file, bg="#2196F3", fg="white", width=20, height=2)
create_button.grid(row=0, column=0, padx=5, pady=2)  # Réduire le padding ici

# Bouton pour ouvrir un fichier
open_button = tk.Button(button_frame, text="Ouvrir un fichier", command=open_file, bg="#FF9800", fg="white", width=20, height=2)
open_button.grid(row=1, column=0, padx=5, pady=2)  # Réduire le padding ici

# Bouton pour exécuter un programme C
execute_button = tk.Button(button_frame, text="Exécuter programme C", command=execute_c_program, bg="#9C27B0", fg="white", width=20, height=2)
execute_button.grid(row=2, column=0, padx=5, pady=2)  # Réduire le padding ici

# Bouton pour quitter l'application
quit_button = tk.Button(button_frame, text="Quitter", command=quit_application, bg="#F44336", fg="white", width=20, height=2)
quit_button.grid(row=3, column=0, padx=5, pady=2)  # Réduire le padding ici

# Lancer la boucle principale
root.mainloop()
print("test")
