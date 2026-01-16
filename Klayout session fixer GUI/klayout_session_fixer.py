
import os
import re
import tkinter as tk
from tkinter import messagebox, Listbox, MULTIPLE, END, Scrollbar


def fix_paths_in_file(file_path, base_dir):
    """
    Modifica un file .lys:
    - aggiorna il percorso del file .gds (estratto dal tag <name>)
    - aggiorna tutti i percorsi delle immagini mantenendo 'images/...'
    """

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    modified = content

    # --- 1. Trova nome GDS dal tag <name>
    gds_match = re.search(r"<name>(.*?)</name>", content)
    if gds_match:
        gds_name = gds_match.group(1).strip()
        new_gds_path = os.path.join(base_dir, gds_name)
        new_gds_path = new_gds_path.replace("\\", "/")

        # Sostituisci tag <file-path>...</file-path>
        modified = re.sub(
            r"<file-path>.*?</file-path>",
            f"<file-path>{new_gds_path}</file-path>",
            modified
        )

    # --- 2. Aggiorna i percorsi immagine dentro <value>...file='...'>
    # pattern che cattura file='QUALCOSA\images\FILE'
    img_pattern = r"file='([^']*?images[\\/][^']*)'"

    def replace_image_path(match):
        old_full_path = match.group(1)
        # prendi solo la parte "images/.../file.ext"
        idx = old_full_path.lower().find("images")
        relative_path = old_full_path[idx:].replace("\\", "/")
        new_full_path = os.path.join(base_dir, relative_path).replace("\\", "/")
        return f"file='{new_full_path}'"

    modified = re.sub(img_pattern, replace_image_path, modified)

    # scrivi file aggiornato
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(modified)


def build_gui():
    root = tk.Tk()
    root.title("KLayout session fixer")
    # root.iconbitmap(os.path.join(base_dir, "icon.ico"))
    root.geometry("650x400")

    # cartella in cui risiede l'exe o il file .py
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Label percorso corrente
    label_dir = tk.Label(root, text=f"Cartella corrente:\n{base_dir}", fg="blue")
    label_dir.pack(pady=10)

    # Raccogli tutti i file .lys
    lys_files = [f for f in os.listdir(base_dir) if f.lower().endswith(".lys")]

    # Lista con selezione multipla
    frame_list = tk.Frame(root)
    frame_list.pack(pady=5)

    scrollbar = Scrollbar(frame_list)
    scrollbar.pack(side="right", fill="y")

    listbox = Listbox(frame_list, selectmode=MULTIPLE, width=80, height=12, yscrollcommand=scrollbar.set)
    listbox.pack(side="left")

    scrollbar.config(command=listbox.yview)

    for lys in lys_files:
        listbox.insert(END, lys)

    # Funzione eseguita quando si clicca "Fix selected files"
    def fix_selected():
        selected_indices = listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Attenzione", "Seleziona almeno un file .lys.")
            return

        for idx in selected_indices:
            filename = lys_files[idx]
            full_path = os.path.join(base_dir, filename)
            try:
                fix_paths_in_file(full_path, base_dir)
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel file {filename}:\n{e}")
                return

        messagebox.showinfo("Completato", "Percorsi aggiornati correttamente!")

    # Bottone principale
    btn_fix = tk.Button(root, text="Fix selected files", command=fix_selected, bg="#4CAF50", fg="white", padx=10, pady=5)
    btn_fix.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    build_gui()
