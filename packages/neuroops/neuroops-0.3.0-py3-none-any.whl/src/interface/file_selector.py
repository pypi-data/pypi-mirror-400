import tkinter as tk
from tkinter import filedialog
import os

def open_file_dialog(initial_dir="."):
    """
    Opens a native OS file dialog to select a file.
    Returns the absolute path of the selected file, or None if cancelled.
    """
    try:
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw() # Hide the main window
        
        # Ensure the dialog appears on top of other windows
        root.wm_attributes('-topmost', 1)

        # Open dialog
        file_path = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Select Neuroimaging Data",
            filetypes=[
                ("Neuroimaging Data", "*.nii *.nii.gz *.fif *.edf *.vhdr *.set *.mat"), 
                ("All Files", "*.*")
            ]
        )
        
        root.destroy()
        return file_path if file_path else None
    except Exception as e:
        print(f"Error opening file dialog: {e}")
        return None
