import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import platform  
import compiler.main as main
import subprocess
import os
       

class TextEditor:
    def __init__(self, root,isdark = True ) :
        self.root = root
        self.root.title("Éditeur de Texte")
       
        #set dark theme at the begening
        self.is_dark_theme = isdark
        #open tkinter windows
        self.menu = tk.Menu(root)
        root.config(menu=self.menu)
       
        #untils set for save, create file ect ... 
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Fichier", menu=self.file_menu)
        self.file_menu.add_command(label="Nouveau", command=self.new_file)
        self.file_menu.add_command(label="Ouvrir", command=self.open_file)
        self.file_menu.add_command(label="Enregistrer", command=self.save_file)
        self.file_menu.add_command(label="Enregistrer sous", command=self.save_file_as)
        self.file_menu.add_command(label="Changer de thème", command=self.toggle_theme)  # Changer de thème
        self.file_menu.add_separator()
        
        #until set 
        self.toolbar = tk.Frame(root)
        self.toolbar.pack(side='top', fill='x')
       
        #debug button
        self.debug_button = tk.Button(self.toolbar, text="Debug", command=self.debug)
        self.debug_button.pack(side='left')
        
        # run button
        self.triangle_canvas = tk.Canvas(self.toolbar, width=30, height=30)
        self.triangle_canvas.pack(side='left')
        
        # Draw green triangle
        self.triangle_canvas.create_polygon(5, 15, 25, 5, 25, 25, fill='green', outline='black')
       
        self.triangle_canvas.bind("<Button-1>", lambda event: self.run_action())
               
        #Close feneter
        self.close_button = tk.Button(self.toolbar, text="Fermer l'onglet", command=self.close_tab)
        self.close_button.pack(side='right')
               
        #clear terminal
        self.clear_button = tk.Button(self.toolbar, text="Nettoyer terminal", command=self.clear_terminal)
        self.clear_button.pack(side='right')
       
        #for choose a width of the feneter
        self.paned_window = tk.PanedWindow(root, orient=tk.VERTICAL)
        self.paned_window.pack(fill='both', expand=True)
       
        #text editor
        self.text_frame = tk.Frame(self.paned_window)
        self.notebook = ttk.Notebook(self.text_frame)
        self.notebook.pack(fill='both', expand=True)
        self.paned_window.add(self.text_frame, minsize=100)  # Taille minimale
        on_lines_str = []
        # initialise for each fenester many constant
        self.current_file = None
        self.open_files = []
        self.line_states = {}
        self.line_underlignes = {}
       
        #terminal 
        self.terminal_frame = tk.Frame(self.paned_window)
        self.terminal = tk.Text(self.terminal_frame, height=5, state='normal', bg='#252539', fg='white')
        self.terminal.pack(fill='both', expand=True)
        self.paned_window.add(self.terminal_frame, minsize=50)
        #start the ide
        self.open_default_file()
               
    def close_tab(self):
        # take current fenester
        current_tab_index = self.notebook.index(self.notebook.select())
        current_tab = self.open_files[current_tab_index]
               
        # Verify if the fenester is not a documentation
        if current_tab['closable']:
            # close fenester
            self.notebook.forget(current_tab['frame'])
            self.open_files.pop(current_tab_index)
        else:
            messagebox.showwarning("Action interdite", "Cet onglet ne peut pas être fermé.")
               
    def save_file(self):
        # take current fenester
        current_tab = self.notebook.index(self.notebook.select())
        if self.open_files[current_tab]['file_path']:
            with open(self.open_files[current_tab]['file_path'], 'w') as file:
                #save the file
                file.write(self.open_files[current_tab]['text_widget'].get(1.0, tk.END))
        #if that a new file save as it's better that save
        else:
            self.save_file_as()
           
    def save_file_as(self):
        # take current fenester
        current_tab_index = self.notebook.index(self.notebook.select())
        current_tab = self.open_files[current_tab_index]
           
        # ask the name and the file path 
        file_path = filedialog.asksaveasfilename(defaultextension=".pd", filetypes=[("Text files", "*.pd"), ("All files", "*.*")])
        if file_path:
            # save in the new file
            with open(file_path, 'w') as file:
                file.write(current_tab['text_widget'].get(1.0, tk.END))
           
            # close a fenester because if you don't close the current tab doesn't exist
            self.close_tab()
           
       
    def toggle_theme(self):
        #switch theme colors
        if self.is_dark_theme:
            # white theme
            self.root.configure(bg="white")
            self.text_frame.configure(bg="white")
            self.terminal.configure(bg="white", fg="black")
            for tab in self.open_files:
                tab['text_widget'].configure(bg="white", fg="black")
            self.is_dark_theme = False
        else:
            # black theme
            self.root.configure(bg='#252539')
            self.terminal.configure(bg='#252539', fg="white")
            for tab in self.open_files:
                tab['text_widget'].configure(bg='#252539', fg="white")
            self.is_dark_theme = True
       
    def open_default_file(self):
        #documentation file
        file_path = "doc.txt"
        text_frame = tk.Frame(self.notebook)
        text_widget = tk.Text(text_frame, wrap='word', state='disabled', bg='#252539', fg='white')  # Couleurs du thème
        text_widget.pack(side='right', fill='both', expand=True)
       
        line_numbers = tk.Canvas(text_frame, width=50)
        line_numbers.pack(side='left', fill='y')
    
    
        # collect all interactive action and react   
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
       
                # after loading the file / update line number
                self.update_line_numbers(text_widget, line_numbers)
       
        except FileNotFoundError:
            messagebox.showerror("Erreur", f"Le fichier {file_path} n'a pas été trouvé.")
       
        self.notebook.add(text_frame, text=file_path)
        self.open_files.append({'text_widget': text_widget, 'line_numbers': line_numbers, 'file_path': file_path, 'frame': text_frame, 'closable': False})
       
        # initialisation of constant for this file
        self.line_states[file_path] = {}
        self.line_underlignes[file_path] = {}




    def new_file(self):
        # Generate a new file
        new_file_index = len(self.open_files) + 1
        new_file_name = f"Nouveau {new_file_index}"
               
        # add fenester
        text_frame = tk.Frame(self.notebook)
        text_widget = tk.Text(text_frame, wrap='word', bg='#252539', fg='white')  # Couleurs du thème
        text_widget.pack(side='right', fill='both', expand=True)
           
        # add line numbers
        line_numbers = tk.Canvas(text_frame, width=50)
        line_numbers.pack(side='left', fill='y')
           
        # collect all interactive action and react
        text_widget.bind('<KeyRelease>', lambda event: self.update_line_numbers(text_widget, line_nurrent_filumbers))
        text_widget.bind('<Configure>', lambda event: self.update_line_numbers(text_widget, line_numbers))
        text_widget.bind('<MouseWheel>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
        text_widget.bind('<Button-4>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
        text_widget.bind('<Button-5>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
        line_numbers.bind('<MouseWheel>', lambda event: self.on_mouse_wheel(event, text_widget, line_numbers))
           
        self.notebook.add(text_frame, text=new_file_name)
        self.open_files.append({'text_widget': text_widget, 'line_numbers': line_numbers, 'file_path': None, 'frame': text_frame, 'closable': True})
           
        # Initialize constent for this file
        self.line_states[new_file_name] = {}
        self.line_underlignes[new_file_name] = {}
               
        ## after loading the file / update line number
        self.update_line_numbers(text_widget, line_numbers)



       
    def open_file(self,file_path = None):
        #verify if file exist
        if file_path == None:
            file_paths = filedialog.askopenfilenames(defaultextension=".pd", filetypes=[("Text files", "*.pd"), ("All files", "*.*")])
        print(file_path)
        if file_paths:
            for file_path in file_paths:
                
                # Initialise a constent for this 
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
           
                # after loading the file / update line number
                self.update_line_numbers(text_widget, line_numbers)
           
           
                self.notebook.add(text_frame, text=file_path)
                self.open_files.append({'text_widget': text_widget, 'line_numbers': line_numbers, 'file_path': file_path, 'frame': text_frame, 'closable': True})
           
                       
       
       
    def update_line_numbers(self, text_widget, line_numbers):
        # take a current fenester
        selected_tab = self.notebook.select()
        if not selected_tab:
            return
           
        current_tab_index = self.notebook.index(selected_tab)
        file_path = self.open_files[current_tab_index]['file_path'] or f"Tab_{current_tab_index}"
        if file_path not in self.line_states:
            self.line_states[file_path] = {}
        # clear a line number
        line_numbers.delete('all')
           
        #update of line numbers
        i = text_widget.index("@0,0")
        while True:
            dline = text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            line_num = str(i).split(".")[0]
           
            #Watch state of the line
            state = self.line_states[file_path].get(line_num, False)
            color = "red" if state else "black"
           
            # add a widget for see a line number on the ide
            line_numbers.create_text(2, y, anchor="nw", text=line_num, fill=color, font=("Helvetica", 10))
            i = text_widget.index(f"{i}+1line")
                   

               
               
    def update_underlignes(self, text_widget,file_path):
        # take current fenester
        selected_tab = self.notebook.select()
        if not selected_tab:
            return
           
        current_tab_index = self.notebook.index(selected_tab)
        file_path = self.open_files[current_tab_index]['file_path'] or f"Tab_{current_tab_index}"
           
        # delete all underline on the ide
        text_widget.tag_remove("underline", "1.0", "end")
           
        # underlines 
        for line_num, underline in self.line_underlignes[file_path].items():
            if underline:
                text_widget.tag_add("underline", f"{line_num}.0", f"{line_num}.end")
        text_widget.tag_configure("underline", underline=True)

  
    def on_line_number_click(self, text_widget, line_numbers, event, file_path):
        #  take current fenster
        current_tab_index = self.notebook.index(self.notebook.select())
        file_path = file_path or self.open_files[current_tab_index]['file_path'] or f"Tab_{current_tab_index}"
               
        # identify line on click
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
            # specifique gestion for linux
            if event.num == 4:  
                text_widget.yview_scroll(-1, 'units')
            elif event.num == 5: 
                text_widget.yview_scroll(1, 'units')
        else:
            # for windows or other OS
            text_widget.yview_scroll(int(-1 * (event.delta / 120)), 'units')
           
        # Syncrhonize line scroll with mouse
        line_numbers.yview_moveto(text_widget.yview()[0])
        self.update_line_numbers(text_widget, line_numbers)
   
   
       
    def debug(self):
        # take current tab
        current_tab = self.notebook.index(self.notebook.select())
        current_file = self.open_files[current_tab]['file_path']
        if current_file :
            if current_file != "doc.txt":
                # find all lines with on click
                underlined_lines = [line_num for line_num, underline in self.line_underlignes[current_file].items() if underline]
                self.run_action(1)


    def c_compiling(self):

        start_dir = os.getcwd()+"/c"
        
        commands = [
            ["make", "cleaning"],
            ["make"],
            ["./pyDrawExec"]
        ]

        for command in commands:
            result = subprocess.run(command, text=True, capture_output=True, cwd=start_dir)
            if result.returncode != 0:
                print(f"Erreur avec la commande : {' '.join(command)}")
                print(f"Sortie d'erreur : {result.stderr}")
                break
            print(f"Résultat : {result.stdout}")

    def run_action(self,debug = 0):
        # take a current tab
        self.save_file()
        current_tab_index = self.notebook.index(self.notebook.select())
        current_tab = self.open_files[current_tab_index]
        file_path = current_tab['file_path']
        text_widget = current_tab['text_widget']
        liste_key = []
        on_lines = []
        if debug != 0:
            on_lines_str = [line_num for line_num, state in self.line_states[file_path].items() if state]
            on_lines = [int(x) for x in on_lines_str]
        if file_path :
            if file_path != "doc.txt":
                result = main.main(file_path,on_lines)  
                if result != None :
                    for key in result:
                        liste_key.append(key)
                        # underlignes
                        self.line_underlignes[file_path][key] = True
                        self.update_underlignes(text_widget, file_path)
                        # print in the termiunal
                        if key !=0 :
                            self.terminal.insert(tk.END, f"LIGNE : {key}, ERROR : {result[key]}\n")
                        else : 
                            self.terminal.insert(tk.END, "Compilation successful! C code has been generated \n")
                            self.c_compiling()
                    for i in liste_key :
                        self.line_underlignes[file_path][key] = False
                else : 
                    self.terminal.insert(tk.END, "Compilation successful! C code has been generated \n")
                    self.c_compiling()
                    for i in liste_key :
                        self.line_underlignes[file_path][key] = False
                    self.update_underlignes(text_widget, file_path)

    
       
    def clear_terminal(self):
        self.terminal.delete('1.0', tk.END)
       
if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root,True)
    root.mainloop()
