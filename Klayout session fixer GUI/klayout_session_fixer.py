
import os
import re
import tkinter as tk
from tkinter import messagebox, Listbox, MULTIPLE, END, Scrollbar, filedialog


def fix_paths_in_file(file_path, base_dir):
    """
    Modifica un file .lys:
    - aggiorna il percorso del file .gds (estratto dal tag <name>)
    - aggiorna tutti i percorsi delle immagini mantenendo 'images/...'
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    modified = content

    # 1) Nome GDS dal tag <name>
    gds_match = re.search(r"<name>(.*?)</name>", content)
    if gds_match:
        gds_name = gds_match.group(1).strip()
        new_gds_path = os.path.join(base_dir, gds_name).replace("\\", "/")

        # sostituisci il contenuto del tag <file-path>...</file-path>
        modified = re.sub(
            r"<file-path>.*?</file-path>",
            f"<file-path>{new_gds_path}</file-path>",
            modified
        )

    # 2) Aggiorna i percorsi immagine in file='...images/...'
    img_pattern = r"file='([^']*?images[\\/][^']*)'"

    def replace_image_path(match):
        old_full_path = match.group(1)
        idx = old_full_path.lower().find("images")
        if idx == -1:
            return match.group(0)  # sicurezza
        relative_path = old_full_path[idx:].replace("\\", "/")
        new_full_path = os.path.join(base_dir, relative_path).replace("\\", "/")
        return f"file='{new_full_path}'"

    modified = re.sub(img_pattern, replace_image_path, modified)

    # Scrivi il file aggiornato
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(modified)


def build_gui():
    root = tk.Tk()
    root.title("KLayout session fixer")

    # --- Icona personalizzata, se presente accanto allo script/exe
    try:
        base_here = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_here, "icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception:
        pass

    root.geometry("700x560")

    # Cartella di default = cartella dello script/exe
    current_base_dir = tk.StringVar()
    current_base_dir.set(os.path.dirname(os.path.abspath(__file__)))

    # Header: percorso corrente + bottone "Scegli cartella…"
    frm_top = tk.Frame(root)
    frm_top.pack(fill="x", padx=12, pady=(12, 6))

    lbl_dir_title = tk.Label(frm_top, text="Cartella di lavoro:", font=("Segoe UI", 10, "bold"))
    lbl_dir_title.pack(anchor="w")

    lbl_dir = tk.Label(frm_top, textvariable=current_base_dir, fg="blue", wraplength=740, justify="left")
    lbl_dir.pack(anchor="w", pady=(2, 6))

    def browse_dir():
        new_dir = filedialog.askdirectory(title="Scegli la cartella di lavoro")
        if new_dir:
            current_base_dir.set(new_dir)
            refresh_lys_list()

    btn_browse = tk.Button(frm_top, text="Scegli cartella…", command=browse_dir)
    btn_browse.pack(anchor="w")

    # Lista dei .lys con scrollbar
    frm_list = tk.LabelFrame(root, text="File .lys nella cartella selezionata", padx=10, pady=10)
    frm_list.pack(fill="both", expand=True, padx=12, pady=6)

    scrollbar = Scrollbar(frm_list)
    scrollbar.pack(side="right", fill="y")

    listbox = Listbox(frm_list, selectmode=MULTIPLE, width=95, height=18, yscrollcommand=scrollbar.set)
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=listbox.yview)

    # Barra comandi (seleziona tutto / deseleziona tutto / fix)
    frm_bottom = tk.Frame(root)
    frm_bottom.pack(fill="x", padx=12, pady=(6, 12))

    def select_all():
        listbox.selection_set(0, END)

    def deselect_all():
        listbox.selection_clear(0, END)

    def refresh_lys_list():
        base_dir = current_base_dir.get()
        listbox.delete(0, END)
        if not os.path.isdir(base_dir):
            return
        lys_files = [f for f in os.listdir(base_dir) if f.lower().endswith(".lys")]
        lys_files.sort()
        for f in lys_files:
            listbox.insert(END, f)
        # seleziona il primo file di default (se presente)
        if lys_files:
            listbox.selection_set(0)

    def fix_selected():
        base_dir = current_base_dir.get()
        if not os.path.isdir(base_dir):
            messagebox.showerror("Errore", "La cartella di lavoro selezionata non esiste.")
            return

        selected_indices = listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Attenzione", "Seleziona almeno un file .lys.")
            return

        errors = []
        successes = 0
        # snapshot dei nomi nella listbox
        items = [listbox.get(i) for i in range(listbox.size())]

        for idx in selected_indices:
            filename = items[idx]
            full_path = os.path.join(base_dir, filename)
            try:
                fix_paths_in_file(full_path, base_dir)
                successes += 1
            except Exception as e:
                errors.append(f"{filename}: {e}")

        if errors:
            messagebox.showwarning(
                "Completato con avvisi",
                f"Modifiche completate: {successes}\n"
                f"File con errori: {len(errors)}\n\n" + "\n".join(errors[:10]) +
                ("\n\n(Altri errori omessi…)" if len(errors) > 10 else "")
            )
        else:
            messagebox.showinfo("Completato", f"Percorsi aggiornati correttamente in {successes} file.")

    # Pulsanti a sinistra: selezione
    btn_select_all = tk.Button(frm_bottom, text="Seleziona tutto", command=select_all)
    btn_select_all.pack(side="left", padx=(0, 8))

    btn_deselect_all = tk.Button(frm_bottom, text="Deseleziona tutto", command=deselect_all)
    btn_deselect_all.pack(side="left")

    # Pulsante principale a destra
    btn_fix = tk.Button(frm_bottom, text="Fix selected files", command=fix_selected,
                        bg="#4CAF50", fg="white", padx=12, pady=6)
    btn_fix.pack(side="right")

    # popolamento iniziale
    refresh_lys_list()
    root.mainloop()


if __name__ == "__main__":
    build_gui()
