
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
import shutil
import hashlib

# File categories
FILE_TYPES = {
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx", ".csv"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi"],
    "Audio": [".mp3", ".wav", ".aac", ".flac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Programs": [".py", ".java", ".cpp", ".exe", ".html", ".css", ".js"]
}

selected_folder = None


# Select folder
def select_folder():
    global selected_folder

    folder = filedialog.askdirectory(
        title="Select a folder to organize"
    )

    if folder:
        selected_folder = Path(folder)
        folder_label.config(text=str(selected_folder))
        log("Selected folder: " + str(selected_folder))


# Generate a unique filename if one already exists
def get_unique_path(destination):
    if not destination.exists():
        return destination

    counter = 1

    while True:
        new_path = destination.with_name(
            f"{destination.stem}_{counter}{destination.suffix}"
        )

        if not new_path.exists():
            return new_path

        counter += 1


# Organize files
def organize_files():
    if selected_folder is None:
        messagebox.showwarning(
            "Warning", "Please select a folder first!"
        )
        return

    moved = 0
    skipped = 0
    errors = 0

    try:
        for file in list(selected_folder.iterdir()):

            # Ignore folders and symbolic links
            if not file.is_file() or file.is_symlink():
                continue

            category = "Others"

            for folder_name, extensions in FILE_TYPES.items():
                if file.suffix.lower() in extensions:
                    category = folder_name
                    break

            # Create destination folder automatically
            destination_folder = selected_folder / category
            destination_folder.mkdir(exist_ok=True)

            # Avoid overwriting existing files
            destination = get_unique_path(
                destination_folder / file.name
            )

            try:
                shutil.move(str(file), str(destination))
                moved += 1
                log(f"Moved: {file.name} -> {category}")

            except OSError as error:
                errors += 1
                log(f"Error moving {file.name}: {error}")

        log(f"Organization completed. Moved: {moved}")

        messagebox.showinfo(
            "Completed",
            f"Files moved: {moved}\nErrors: {errors}"
        )

    except OSError as error:
        messagebox.showerror("Error", str(error))


# Calculate SHA-256 hash
def calculate_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


# Find duplicate files
def find_duplicates():
    if selected_folder is None:
        messagebox.showwarning(
            "Warning", "Please select a folder first!"
        )
        return

    hashes = {}
    duplicates = []

    try:
        for file in selected_folder.rglob("*"):

            if not file.is_file() or file.is_symlink():
                continue

            try:
                file_hash = calculate_hash(file)

                if file_hash in hashes:
                    duplicates.append((file, hashes[file_hash]))
                else:
                    hashes[file_hash] = file

            except OSError as error:
                log(f"Could not read {file}: {error}")

        log("----- DUPLICATE SCAN RESULTS -----")

        if duplicates:
            for duplicate, original in duplicates:
                log(f"Duplicate: {duplicate}")
                log(f"Original:  {original}")
                log("--------------------------------")

        else:
            log("No duplicate files found.")

        messagebox.showinfo(
            "Duplicate Scan",
            f"Duplicate files found: {len(duplicates)}\n\n"
            "No files have been deleted."
        )

    except OSError as error:
        messagebox.showerror("Error", str(error))


# Display activity logs
def log(message):
    output_box.insert(tk.END, message + "\n")
    output_box.see(tk.END)


# Clear logs
def clear_logs():
    output_box.delete("1.0", tk.END)


# Main GUI window
root = tk.Tk()
root.title("File Automation Tool")
root.geometry("750x600")
root.minsize(650, 500)
root.configure(bg="#1e1e2e")

# Heading
title = tk.Label(
    root,
    text="FILE AUTOMATION TOOL",
    font=("Arial", 20, "bold"),
    bg="#1e1e2e",
    fg="white"
)
title.pack(pady=20)

subtitle = tk.Label(
    root,
    text="Organize files | Find duplicates | Manage folders",
    font=("Arial", 10),
    bg="#1e1e2e",
    fg="#b0b0c0"
)
subtitle.pack(pady=5)

# Folder selection
folder_frame = tk.Frame(root, bg="#1e1e2e")
folder_frame.pack(pady=20, padx=20, fill="x")

select_button = tk.Button(
    folder_frame,
    text="Select Folder",
    command=select_folder,
    bg="#3b82f6",
    fg="white",
    font=("Arial", 11, "bold"),
    padx=15,
    pady=8
)
select_button.pack(side="left", padx=5)

folder_label = tk.Label(
    folder_frame,
    text="No folder selected",
    bg="#1e1e2e",
    fg="#cccccc",
    wraplength=450
)
folder_label.pack(side="left", padx=10)

# Action buttons
button_frame = tk.Frame(root, bg="#1e1e2e")
button_frame.pack(pady=15)

organize_button = tk.Button(
    button_frame,
    text="Organize Files",
    command=organize_files,
    bg="#16a34a",
    fg="white",
    font=("Arial", 11, "bold"),
    padx=15,
    pady=10
)
organize_button.grid(row=0, column=0, padx=10)

duplicate_button = tk.Button(
    button_frame,
    text="Find Duplicates",
    command=find_duplicates,
    bg="#9333ea",
    fg="white",
    font=("Arial", 11, "bold"),
    padx=15,
    pady=10
)
duplicate_button.grid(row=0, column=1, padx=10)

clear_button = tk.Button(
    button_frame,
    text="Clear Logs",
    command=clear_logs,
    bg="#475569",
    fg="white",
    font=("Arial", 11),
    padx=15,
    pady=10
)
clear_button.grid(row=0, column=2, padx=10)

# Activity log heading
log_title = tk.Label(
    root,
    text="ACTIVITY LOG",
    font=("Arial", 12, "bold"),
    bg="#1e1e2e",
    fg="white"
)
log_title.pack(pady=10)

# Activity log area
output_box = scrolledtext.ScrolledText(
    root,
    width=85,
    height=17,
    bg="#11111b",
    fg="#a6e3a1",
    font=("Consolas", 9),
    wrap=tk.WORD
)
output_box.pack(padx=20, pady=10, fill="both", expand=True)

# Footer
footer = tk.Label(
    root,
    text="Python File Automation Project",
    bg="#1e1e2e",
    fg="#888899"
)
footer.pack(pady=10)

# Start application
root.mainloop()
