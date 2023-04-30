import tkinter as tk

from tkinter import ttk
import sv_ttk

from tkinter.filedialog import askopenfilename, asksaveasfilename
import ujson
from pathlib import Path

import threading
import time

window = tk.Tk()
window.title("Notebook")
window.rowconfigure(0, minsize=10,weight=1)
window.columnconfigure(0, minsize=800, weight=1)
window.columnconfigure(1, minsize=50, weight=1)
editor = tk.Text(window)

pageNum = 1
wordCount = 0

currentFilePath = None
currentText = None

class MediaBar:
    def open_file():
        filepath = askopenfilename(filetypes=[("Notebook Files", "*.notebook"), ("All Files", "*.*")])
        if not filepath:
            return
        global currentFilePath
        currentFilePath = filepath

        editor.delete("1.0", tk.END)
        with open(filepath, "r") as inputFile:
            global currentText 
            currentText = ujson.loads(inputFile.read())
            editor.insert(tk.END, currentText["pages"][pageNum - 1]["text"])

        ControlBar.update_word_counter()

        window.title("Notebook: " + currentText["title"])

    def save_file():
        if not currentFilePath == None:
            text = editor.get("1.0", tk.END).strip()
            if pageNum > len(currentText["pages"]) and not text == "":
                currentText["pages"].append({
                    "text": text
                })
            else:
                currentText["pages"][pageNum - 1]["text"] = text
            with open(currentFilePath, "w") as outputFile:
                ujson.dump(currentText, outputFile, indent=4)

            window.title("Notebook: " + currentText["title"])
        else:
            MediaBar.saveas_file()

    def saveas_file():
        filepath = asksaveasfilename(defaultextension=".notebook", filetypes=[("Notebook Files", "*.notebook"), ("All Files", "*.*")],)
        if not filepath:
            return

        with open(filepath, "w") as outputFile:
            newJson = {
                "title": Path(filepath).stem.title(),
                "pages": [
                    {
                        "text": editor.get("1.0", tk.END).strip()
                    }
                ]
            }
            ujson.dump(newJson, outputFile, indent=4)

        window.title(f"Notebook: - {filepath}")

    def clear():
        global currentFilePath
        global currentText
        editor.delete("1.0", tk.END)
        ControlBar.update_word_counter()
        currentFilePath = None
        currentText = None        

    frame = ttk.Frame(window, relief=tk.RAISED)
    openButton = ttk.Button(frame, text="Open", command=open_file)
    saveButton = ttk.Button(frame, text="Save", command=save_file)
    clearButton = ttk.Button(frame, text="Clear", command=clear)

    openButton.grid(row=0, column=0, sticky="ew")
    saveButton.grid(row=0, column=1, sticky="ew")
    clearButton.grid(row=0, column=2, sticky="ew")

class ControlBar:
    def update_page_number():
        pageNumber = tk.Label(text=f"Page {pageNum}", fg="white")
        pageNumber.grid(row=0, column=1, sticky="s")
    update_page_number()

    def previous_page():
        global pageNum
        if pageNum > 1:
            if not editor.get("1.0", tk.END).strip() == "":
                MediaBar.save_file()
            pageNum -= 1
            ControlBar.update_page_number()
            editor.delete("1.0", tk.END)
            editor.insert(tk.END, currentText["pages"][pageNum - 1]["text"])
            ControlBar.update_word_counter()

    def next_page():
        global pageNum
        if pageNum <= len(currentText["pages"]):
            if not editor.get("1.0", tk.END).strip() == "":
                MediaBar.save_file()
            pageNum += 1
            ControlBar.update_page_number()
            editor.delete("1.0", tk.END)
            if pageNum <= len(currentText["pages"]):
                editor.insert(tk.END, currentText["pages"][pageNum - 1]["text"])
            ControlBar.update_word_counter()

    frame = ttk.Frame(window, relief=tk.RAISED)
    backButton = ttk.Button(frame, text="Back", command=previous_page)
    nextButton = ttk.Button(frame, text="Next", command=next_page)
    wordCounter = tk.Label(frame, text=f"{wordCount} words", fg="white")

    backButton.grid(row=0, column=1, sticky="sw")
    nextButton.grid(row=0, column=2, sticky="sw")
    wordCounter.grid(row=0, column=0, sticky="w")

    def update_word_counter():
        global wordCount
        text = editor.get("1.0", tk.END).strip()
        wordCount = len(text.split())
        ControlBar.wordCounter.config(text=f"{wordCount} words", fg="white")
    def run_update(event):
        ControlBar.update_word_counter()

    editor.bind("<KeyRelease>", run_update)


MediaBar.frame.grid(row=0, column=0, sticky="w")
ControlBar.frame.grid(column=1, sticky="sew")
editor.grid(row=1, column=0, sticky="nsew")


sv_ttk.set_theme("dark")

window.mainloop()