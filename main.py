import json, os, sys
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import filedialog


class PageSpeedApp():
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Bulk PSI v5 Hookup Utility")
        self.check_performance = tk.IntVar()
        self.check_seo = tk.IntVar()
        self.check_best_practices = tk.IntVar()
        self.check_desktop = tk.IntVar()
        self.check_mobile = tk.IntVar()
        self.max_threads = ""
        self.api_key = ""
        self.path_to_urls = ""
        self.file_label_var = tk.StringVar()
        self.path_to_save_directory = ""

        self.filetypes = [('All File Types', '.*'), ('Text Files', '.txt'), ('CSV Files', '.csv')]

        self.create_widgets()

    def create_widgets(self):
        self.window['padx'] = 5
        self.window['pady'] = 5

        # Load a custom config JSON file that will save the user's API key.
        cfg = ""

        with open("config.json") as f:
            cfg = json.load(f)

        # These are set prior to user input for default values.
        self.check_mobile.set(1)
        self.check_performance.set(1)

        # API Key
        api_frame = ttk.LabelFrame(self.window, text="API Key", padding=5, relief=tk.RIDGE)
        api_frame.grid(row=1, column=1, sticky=tk.E + tk.W + tk.N + tk.S)

        api_text_label = ttk.Label(api_frame, text="Note: You MUST enter an API key for the application to work.")
        api_text_label.grid(row=2, column=1, columnspan=1, sticky=tk.W)
        self.api_entry = ttk.Entry(api_frame, width=60)
        self.api_entry.grid(row=1, column=1, sticky=tk.W)

        if cfg["api_key"] != "":
            self.api_entry.insert(0, cfg["api_key"])

        # File Chooser
        file_frame = ttk.LabelFrame(self.window, text="Select a File w/ URLs", padding=5, relief=tk.RIDGE)
        file_frame.grid(row=2, column=1, sticky=tk.E + tk.W + tk.N + tk.S)

        file_btn = ttk.Button(file_frame, text="Select File", command=self.get_file_path)
        file_btn.grid(row=1, column=1, sticky=tk.W)

        file_label = ttk.Label(file_frame, textvariable=self.file_label_var)
        file_label.grid(row=2, column=1, sticky=tk.W)

        # Threads
        thread_frame = ttk.LabelFrame(self.window, text="Max Threads", padding=5, relief=tk.RIDGE)
        thread_frame.grid(row=3, column=1, sticky=tk.E + tk.W + tk.N + tk.S)
        
        thread_text_label = ttk.Label(thread_frame, text="Please enter the max # of threads you'd like to use.\nWe suggest 4, or half of your CPU cores.")
        thread_text_label.grid(row=1, column=1, columnspan=1, sticky=tk.W)
        self.thread_combo = ttk.Combobox(thread_frame, height=4)
        self.thread_combo.grid(row=2, column=1, sticky=tk.W)
        self.thread_combo['values'] = ("0", "1", "2", "3", "4", "5", "6", "7", "8")
        self.thread_combo.current(4)

        # Desktop // Mobile
        device_frame = ttk.LabelFrame(self.window, text="Choose Device(s)", padding=5, relief=tk.RIDGE)
        device_frame.grid(row=1, column=2, sticky=tk.E + tk.W + tk.N + tk.S)

        chk_desktop_btn = ttk.Checkbutton(device_frame, variable=self.check_desktop, text="Check Desktop")
        chk_mobile_btn = ttk.Checkbutton(device_frame, variable=self.check_mobile, text="Check Mobile")

        chk_desktop_btn.grid(row=1, column=1, sticky=tk.W)
        chk_mobile_btn.grid(row=2, column=1, sticky=tk.W)

        # Categories
        cat_frame = ttk.LabelFrame(self.window, text="Choose Test Categories(s)", padding=5, relief=tk.RIDGE)
        cat_frame.grid(row=2, column=2, sticky=tk.E + tk.W + tk.N + tk.S)

        chk_best_btn = ttk.Checkbutton(cat_frame, variable=self.check_best_practices, text="Best Practices")
        chk_perf_btn = ttk.Checkbutton(cat_frame, variable=self.check_performance, text="Performance")
        chk_seo_btn = ttk.Checkbutton(cat_frame, variable=self.check_seo, text="SEO")

        chk_best_btn.grid(row=1, column=1, sticky=tk.W)
        chk_perf_btn.grid(row=2, column=1, sticky=tk.W)
        chk_seo_btn.grid(row=3, column=1, sticky=tk.W)


        # Buttons
        btns_frame = ttk.Frame(self.window, padding=5)
        btns_frame.grid(row=1, column=3)
        start_btn = ttk.Button(btns_frame, text="Run Tests", command=self.start_tests)
        quit_btn = ttk.Button(btns_frame, text="Quit App", command=self.window.destroy)

        start_btn.grid(row=1, column=1)
        quit_btn.grid(row=2, column=1)

    def start_tests(self):
        self.max_threads = self.thread_combo.current()
        self.api_key = self.api_entry.get()

        if self.api_key == "":
            messagebox.showerror("No API Key - ERROR", "You MUST enter an API key for the system to work. Please retry.")
        elif self.path_to_urls == "":
            messagebox.showerror("No URL File - ERROR", "You MUST select a URL file for the system to work. Please retry.")
        else:
            if self.check_desktop.get() == 1:
                self.check_desktop = True
            else:
                self.check_desktop = False

            if self.check_mobile.get() == 1:
                self.check_mobile = True
            else:
                self.check_mobile = False

            if self.check_performance.get() == 1:
                self.check_performance = True
            else:
                self.check_performance = False

            if self.check_best_practices.get() == 1:
                self.check_best_practices = True
            else:
                self.check_best_practices = False

            if self.check_seo.get() == 1:
                self.check_seo = True
            else:
                self.check_seo = False


            print("Max Threads: " + str(self.max_threads))
            print("Best Practices: " + str(self.check_best_practices))
            print("SEO: " + str(self.check_seo))
            print("Performance: " + str(self.check_performance))
            print("Desktop: " + str(self.check_desktop))
            print("Mobile: " + str(self.check_mobile))
            print("File Path: " + self.path_to_urls)
            print("API Key: " + self.api_key)

            #save api key to cfg
            #self.window.quit()
            # RUN PROGRAM
            # DISPLAY COMPLETE
            #self.is_complete()

    def get_file_path(self):
        url_file_location = filedialog.askopenfilename(parent=self.window, initialdir=os.getcwd(), title="Please select a valid file with your URLs:", filetypes=self.filetypes)

        while url_file_location == "":
            msg = messagebox.askyesno("You must select a valid file with a list of URLs in either a CSV or TXT file.", "Do you want to try again?")
            if msg == False:
                sys.exit()
        self.path_to_urls = url_file_location
        self.file_label_var.set("File: " + url_file_location)

    def is_complete(self):
        pass

if __name__ == "__main__":   
    p = PageSpeedApp()
    p.window.mainloop()