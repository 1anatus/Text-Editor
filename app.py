import tkinter as tk

from tkinter import ttk
import sv_ttk

from tkinter.filedialog import askopenfilename, asksaveasfilename
import ujson
from pathlib import Path

import threading
import time

#set up basic gui parts including text field, rows, and columns
window = tk.Tk()
window.title("Notebook")
window.rowconfigure(0, minsize=10,weight=1)
window.columnconfigure(0, minsize=800, weight=1)
window.columnconfigure(1, minsize=50, weight=1)
editor = tk.Text(window)

#set page number to 1 and word count to 0 by default
pageNum = 1
wordCount = 0

currentFilePath = None
currentText = None

#class for media controls like save, open, and clear
class MediaBar:
    #function to open file explorer to select a file to open
    def open_file():
        #set file path to chosen file and currently open file path to the file path
        filepath = askopenfilename(filetypes=[("Notebook Files", "*.notebook"), ("All Files", "*.*")])
        if not filepath:
            return
        global currentFilePath
        currentFilePath = filepath

        #replace current text in editor with text from the file
        editor.delete("1.0", tk.END)
        with open(filepath, "r") as inputFile:
            global currentText 
            currentText = ujson.loads(inputFile.read())
            editor.insert(tk.END, currentText["pages"][pageNum - 1]["text"])

        #update word counter
        ControlBar.update_word_counter()

        #update window title
        window.title("Notebook: " + currentText["title"])

    #function to either save to the currently opened file or save as a new file if no file is open
    def save_file():
        if not currentFilePath == None:
            #save the current text in the editor formatted in json
            text = editor.get("1.0", tk.END).strip()
            if pageNum > len(currentText["pages"]) and not text == "": #if the selected page number is greater than the number of pages in the open file and is not blank, add a new page to the notebook
                currentText["pages"].append({
                    "text": text
                })
            else:
                currentText["pages"][pageNum - 1]["text"] = text
            with open(currentFilePath, "w") as outputFile: #save the formatted text to the notebook file, either as a new page or as an edit to an existing page
                ujson.dump(currentText, outputFile, indent=4)

            #update the window title
            window.title("Notebook: " + currentText["title"])
        else: #if no file is selected, proceed to the save as new file function
            MediaBar.saveas_file()

    #function for saving the text in the editor to a new file
    def saveas_file():
        #set the file path to the selected location for creating a new file
        filepath = asksaveasfilename(defaultextension=".notebook", filetypes=[("Notebook Files", "*.notebook"), ("All Files", "*.*")],)
        if not filepath:
            return

        #open the file path and write the contents of the current text editor formatted as json to the new notebook file
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

        #update the window title
        window.title(f"Notebook: - {filepath}")

    #function for clearing the contents of the text editor
    def clear():
        global currentFilePath
        global currentText
        editor.delete("1.0", tk.END) #clear the editor
        ControlBar.update_word_counter() #update the word counter
        currentFilePath = None #clear the currently open file path
        currentText = None #clear the currently open text

    #create gui elements and the gui frame on which they sit
    frame = ttk.Frame(window, relief=tk.RAISED)
    openButton = ttk.Button(frame, text="Open", command=open_file)
    saveButton = ttk.Button(frame, text="Save", command=save_file)
    clearButton = ttk.Button(frame, text="Clear", command=clear)

    #position the gui elements
    openButton.grid(row=0, column=0, sticky="ew")
    saveButton.grid(row=0, column=1, sticky="ew")
    clearButton.grid(row=0, column=2, sticky="ew")

#code for page controls and content
class ControlBar:
    #function for updating the page number counter and its position
    def update_page_number():
        pageNumber = tk.Label(text=f"Page {pageNum}", fg="white")
        pageNumber.grid(row=0, column=1, sticky="s")
    update_page_number() #call the above function

    #function for moving the current page back by one
    def previous_page():
        global pageNum
        if pageNum > 1: #as long as the current page number is greater than one, allow the user to go back a page
            if not editor.get("1.0", tk.END).strip() == "": #if the current page has text on it, save the text before moving the page
                MediaBar.save_file()
            pageNum -= 1
            ControlBar.update_page_number() #call the update page number function
            editor.delete("1.0", tk.END) #delete the contents of the editor
            editor.insert(tk.END, currentText["pages"][pageNum - 1]["text"]) #load the contents of the previous page
            ControlBar.update_word_counter() #update the word counter to the number of words on the previous page

    #function for moving the current page forward by one
    def next_page():
        global pageNum
        if pageNum <= len(currentText["pages"]): #as long as the current page number is less than or equal to the total number of pages in the notebook, allow the user to go forwars a page
            if not editor.get("1.0", tk.END).strip() == "": #if the current page has text on it, save the text before moving the page
                MediaBar.save_file()
            pageNum += 1
            ControlBar.update_page_number() #call the update page number function
            editor.delete("1.0", tk.END) #delete the contents of the editor
            if pageNum <= len(currentText["pages"]): #if the next page number is less thaan or equal to the total number of pages in the notebook, load the contents of the next page
                editor.insert(tk.END, currentText["pages"][pageNum - 1]["text"]) #load the contents of the next page
            ControlBar.update_word_counter() #update the word counter to the number of words on the next page

    #create gui elements and the gui frame on which they sit
    frame = ttk.Frame(window, relief=tk.RAISED)
    backButton = ttk.Button(frame, text="Back", command=previous_page)
    nextButton = ttk.Button(frame, text="Next", command=next_page)
    wordCounter = tk.Label(frame, text=f"{wordCount} words", fg="white")

    #position the gui elements
    backButton.grid(row=0, column=1, sticky="sw")
    nextButton.grid(row=0, column=2, sticky="sw")
    wordCounter.grid(row=0, column=0, sticky="w")

    #function for updating the word counter
    def update_word_counter():
        global wordCount
        text = editor.get("1.0", tk.END).strip()
        wordCount = len(text.split())
        ControlBar.wordCounter.config(text=f"{wordCount} words", fg="white") #edit the word counter label widget's text field
    #function for abstracting the event bound to this function so it can be called as normal
    def run_update(event):
        ControlBar.update_word_counter()
    editor.bind("<KeyRelease>", run_update) #bind the run_update function to trigger when a keyboard key is released

#set the positions of the main gui containers in the window
MediaBar.frame.grid(row=0, column=0, sticky="w")
ControlBar.frame.grid(column=1, sticky="sew")
editor.grid(row=1, column=0, sticky="nsew")


#set the environment theme to dark
sv_ttk.set_theme("dark")

#run the environment
window.mainloop()