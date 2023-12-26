import os
import json
import logging
from tkinter import messagebox
import tkinter as tk


logger = logging.getLogger("MonitorLogger")


def txt_to_json_converter(txtfilename):
    try:
        print("Here1")
        with open(fr"{txtfilename}") as file:
            lines = file.readlines()
            print("Here2")
    

    except (FileNotFoundError, OSError) as e:
        print(f"Here3\nError is {e}")
        logger.error("File(s) missing. json_file_reader or tutor_shift.txt missing from path")
        root = tk.Tk()
        root.title("File(s) Missing")
        label = tk.Label(root, text="json_file_reader or tutor_shift.txt missing from path")
        label.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        button = tk.Button(root, text="OK", command=lambda: root.destroy())
        button.pack(side="bottom", fill="none", expand=True)
        root.mainloop()
        #messagebox.showerror("File(s) missing", "json_file_reader or tutor_shift.txt missing from path")
        
        
        os._exit(0)

    with open(fr"{txtfilename[:-4]}.json", "w") as json_file:
        print(fr"Opening {txtfilename[:-4]}.json")
        lines_json= json.dump(lines, json_file)
        json_file.close()


#txt_to_json_converter("tutor_shifts.txt")
