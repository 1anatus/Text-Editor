import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import ujson

window = tk.Tk()
window.title("Notebook")
window.rowconfigure(0, minsize=10,weight=1)
window.columnconfigure(0, minsize=800, weight=1)
window.columnconfigure(1, minsize=50, weight=1)
editor = tk.Text(window)

pageNum = 1

currentFilePath = None

class MediaBar():
    def open_file():
        filepath = askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if not filepath:
            return
        global currentFilePath
        currentFilePath = filepath

        editor.delete("1.0", tk.END)
        with open(filepath, mode="r") as inputFile:
            global currentText 
            currentText = ujson.loads(inputFile.read())
            editor.insert(tk.END, currentText["pages"][pageNum - 1]["text"])

        window.title("Notebook: " + currentText["title"])

    def save_file():
        if not currentFilePath == None:
            text = editor.get("1.0", tk.END).strip()
            if pageNum > len(currentText["pages"]) and not text == "":
                currentText["pages"].append({"text": text})
            else:
                currentText["pages"][pageNum - 1]["text"] = text
            with open(currentFilePath, mode='w') as outputFile:
                ujson.dump(currentText, outputFile, indent=4)

            window.title("Notebook: " + currentText["title"])

    def saveas_file():
        filepath = asksaveasfilename(defaultextension=".txt", filetypes=[("Notebook Files", "*.notebook"), ("All Files", "*.*")],)
        if not filepath:
            return

        with open(filepath, mode="w") as outputFile:
            text = editor.get("1.0", tk.END)
            outputFile.write(text)

        window.title(f"Notebook: - {filepath}")

    frame = tk.Frame(window, relief=tk.RAISED)
    openButton = tk.Button(frame, text="Open", command=open_file)
    saveButton = tk.Button(frame, text="Save", command=save_file)
    saveasButton = tk.Button(frame, text="Save As", command=saveas_file)

    openButton.grid(row=0, column=0, sticky="ew")
    saveButton.grid(row=0, column=1, sticky="ew")
    saveasButton.grid(row=0, column=2, sticky="ew")

class ControlBar():
    def update_page_number():
        pageNumber = tk.Label(text=f"Page {pageNum}", fg="black")
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

    frame = tk.Frame(window, relief=tk.RAISED)
    backButton = tk.Button(frame, text="Back", command=previous_page)
    nextButton = tk.Button(frame, text="Next", command=next_page)

    backButton.grid(row=0, column=0, sticky="sw")
    nextButton.grid(row=0, column=1, sticky="sw")

MediaBar.frame.grid(row=0, column=0, sticky="w")
ControlBar.frame.grid(column=1, sticky="sew")
editor.grid(row=1, column=0, sticky="nsew")

window.mainloop()