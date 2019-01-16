import json, os, sys
import requests
import csv
from queue import Queue
from threading import Thread
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import filedialog

API_KEY = ""

URLS = []

c_seo = ""
c_best_practices = ""
c_performance = ""
s_mobile = ""
s_desktop = ""

all_url_csv_headers = ["URL", "Field Data: FCP", "Field Data: FID", "Field Data: Overall", "Lighthouse FCP (s)", "Lighthouse Meaningful Paint (s)", "Lighthouse Time to Interactive (s)"]
d_all_url_data = {}
d_all_url_csv_name = "desktop-all-urls-loading-experience.csv"
m_all_url_data = {}
m_all_url_csv_name = "mobile-all-urls-loading-experience.csv"

opps_csv_headers = ["Title", "Description", "Average Est. Time Saved Sitewide", "# of Pages"]
d_opps_csv_name = "desktop-all-opps.csv"
d_opps_data = {}
m_opps_csv_name = "mobile-all-opps.csv"
m_opps_data = {}

perf_csv_headers = []
d_perf_csv_name = "desktop-performance-audits.csv"
d_perf_data = {}
d_perf_urls = {"render-blocking-resources": [], "uses-responsive-images": [], "offscreen-images": [], "unminified-css": [], "unminified-javascript": [], "unused-css-rules": [], "uses-optimized-images": [], "uses-webp-images": [], "uses-text-compression": [], "uses-rel-preconnect": [], "time-to-first-byte": [], "redirects": [], "uses-rel-preload": [], "efficient-animated-content": [], "total-byte-weight": [], "uses-long-cache-ttl": [], "dom-size": [], "critical-request-chains": [], "network-requests": [], "bootup-time": [], "mainthread-work-breakdown": [], "font-display": []}
m_perf_csv_name = "mobile-performance-audits.csv"
m_perf_data = {}
m_perf_urls = {"render-blocking-resources": [], "uses-responsive-images": [], "offscreen-images": [], "unminified-css": [], "unminified-javascript": [], "unused-css-rules": [], "uses-optimized-images": [], "uses-webp-images": [], "uses-text-compression": [], "uses-rel-preconnect": [], "time-to-first-byte": [], "redirects": [], "uses-rel-preload": [], "efficient-animated-content": [], "total-byte-weight": [], "uses-long-cache-ttl": [], "dom-size": [], "critical-request-chains": [], "network-requests": [], "bootup-time": [], "mainthread-work-breakdown": [], "font-display": []}

bestpractice_csv_headers = []
d_bestpractice_csv_name = "desktop-best-practices-audits.csv"
d_bestpractice_data = {}
d_bestpractice_urls = {"appcache-manifest": [], "is-on-https": [], "uses-passive-event-listeners": [], "no-document-write": [], "external-anchors-use-rel-noopener": [], "geolocation-on-start": [], "doctype": [], "no-vulnerable-libraries": [], "js-libraries": [], "notification-on-start": [], "deprecations": [], "password-inputs-can-be-pasted-into": [], "errors-in-console": [], "image-aspect-ratio": []}
m_bestpractice_csv_name = "mobile-best-practices-audits.csv"
m_bestpractice_data = {}
m_bestpractice_urls = {"appcache-manifest": [], "is-on-https": [], "uses-passive-event-listeners": [], "no-document-write": [], "external-anchors-use-rel-noopener": [], "geolocation-on-start": [], "doctype": [], "no-vulnerable-libraries": [], "js-libraries": [], "notification-on-start": [], "deprecations": [], "password-inputs-can-be-pasted-into": [], "errors-in-console": [], "image-aspect-ratio": []}

seo_csv_headers = []
d_seo_csv_name = "desktop-seo-audits.csv"
d_seo_data = {}
d_seo_urls = {"canonical": [], "is-crawlable": [], "hreflang": [], "font-size": [], "document-title": [], "robots-txt": [], "http-status-code": [], "link-text": [], "plugins": [], "meta-description": [], "viewport": [], "structured-data": [], "mobile-friendly": []}
m_seo_csv_name = "mobile-seo-audits.csv"
m_seo_data = {}
m_seo_urls = {"canonical": [], "is-crawlable": [], "hreflang": [], "font-size": [], "document-title": [], "robots-txt": [], "http-status-code": [], "link-text": [], "plugins": [], "meta-description": [], "viewport": [], "structured-data": [], "mobile-friendly": []}



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
        global API_KEY
        API_KEY = self.api_entry.get()

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

            global c_seo, c_performance, c_best_practices, s_mobile, s_desktop
            c_seo = self.check_seo
            c_performance = self.check_performance
            c_best_practices = self.check_best_practices
            s_mobile = self.check_mobile
            s_desktop = self.check_desktop

            with open("config.json", "w") as f:
                json.dump({"api_key": self.api_key}, f, indent=4)
            
            self.window.destroy()

            with open(self.path_to_urls, "r") as f:
                for line in f.readlines():
                    URLS.append(line.strip())
            
            queue = Queue()

            for _ in range(self.max_threads):
                w = PageSpeedThread(queue)
                w.daemon = True
                w.start()
                    
            for url in URLS:
                queue.put(url)

            queue.join()
            
            self.save_csv()
            self.is_complete()

    def get_file_path(self):
        url_file_location = filedialog.askopenfilename(parent=self.window, initialdir=os.getcwd(), title="Please select a valid file with your URLs:", filetypes=self.filetypes)

        while url_file_location == "":
            msg = messagebox.askyesno("You must select a valid file with a list of URLs in either a CSV or TXT file.", "Do you want to try again?")
            if msg == False:
                sys.exit()
        self.path_to_urls = url_file_location
        self.file_label_var.set("File: " + url_file_location)

    def save_csv(self):
        desktop_loc = os.path.expanduser("~/Desktop")

        if os.path.isdir(desktop_loc + "/pagespeedtests") == False:
            os.mkdir(desktop_loc + "/pagespeedtests")

        save_loc = desktop_loc + "/pagespeedtests/"

        if s_mobile is True:
            with open(save_loc + m_all_url_csv_name, "w", newline='') as f:
                w = csv.writer(f)
                w.writerow(all_url_csv_headers)
                for key, value in m_all_url_data.items():
                    x = [key]
                    for item in value:
                        x.append(item)
                    w.writerow(x)

            with open(save_loc + m_opps_csv_name, "w", newline='') as f:
                w = csv.writer(f)
                w.writerow(opps_csv_headers)
                for key, value in m_opps_data.items():
                    x = []
                    for item in value:
                        if item == "Average Time Saved":
                            temp = ((value[item] / value["Count"]) / 1000) * 10
                            x.append(temp)
                        else:
                            x.append(value[item])
                    w.writerow(x)

            with open(save_loc + "mobile-all-urls.csv", "w", newline='') as f:
                w = csv.writer(f)
                w.writerow(["Audit Name", "URL Tested", "Pass/Fail", "Returned Value", "# of Issues on Page"])
                for key, values in m_perf_urls.items():
                    for value in values:
                        x = []
                        x.append(key)
                        for item in value:
                            x.append(item)
                        w.writerow(x)
                
                for key, value in m_seo_urls.items():
                    for value in values:
                        x = []
                        x.append(key)
                        for item in value:
                            x.append(item)
                        w.writerow(x)
                
                for key, value in m_bestpractice_urls.items():
                    for value in values:
                        x = []
                        x.append(key)
                        for item in value:
                            x.append(item)
                        w.writerow(x)

        if s_desktop is True:
            with open(save_loc + d_all_url_csv_name, "w", newline='') as f:
                w = csv.writer(f)
                w.writerow(all_url_csv_headers)
                for key, value in d_all_url_data.items():
                    x = [key]
                    for item in value:
                        x.append(item)
                    w.writerow(x)

            with open(save_loc + d_opps_csv_name, "w", newline='') as f:
                w = csv.writer(f)
                w.writerow(opps_csv_headers)
                for key, value in d_opps_data.items():
                    x = []
                    for item in value:
                        if item == "Average Time Saved":
                            temp = ((value[item] / value["Count"]) / 1000) * 10
                            x.append(temp)
                        else:
                            x.append(value[item])
                    w.writerow(x)

            with open(save_loc + "desktop-all-urls.csv", "w", newline='') as f:
                w = csv.writer(f)
                w.writerow(["Audit Name", "URL Tested", "Pass/Fail", "Returned Value", "# of Issues on Page"])
                for key, values in m_perf_urls.items():
                    for value in values:
                        x = []
                        x.append(key)
                        for item in value:
                            x.append(item)
                        w.writerow(x)
                
                for key, value in m_seo_urls.items():
                    for value in values:
                        x = []
                        x.append(key)
                        for item in value:
                            x.append(item)
                        w.writerow(x)
                
                for key, value in m_bestpractice_urls.items():
                    for value in values:
                        x = []
                        x.append(key)
                        for item in value:
                            x.append(item)
                        w.writerow(x)

    def is_complete(self):
        messagebox.showinfo(title="Page Speed Audit - Complete", message="Your page speed audit has been completed and the files have been saved. Thanks.")
        sys.exit()

class JSONParser():
    def __init__(self):
        pass
    
    def parse_performance(self, j, device):
        p_audits = ["render-blocking-resources", "uses-responsive-images", "offscreen-images", "unminified-css", "unminified-javascript", "unused-css-rules", "uses-optimized-images", "uses-webp-images", "uses-text-compression", "uses-rel-preconnect", "time-to-first-byte", "redirects", "uses-rel-preload", "efficient-animated-content", "total-byte-weight", "uses-long-cache-ttl", "dom-size", "critical-request-chains", "network-requests", "bootup-time", "mainthread-work-breakdown", "font-display"]

        for audit in j["lighthouseResult"]["audits"]:
            
            if audit not in p_audits:
                continue

            audit_id = j["lighthouseResult"]["audits"][audit]["id"]
            audit_score = j["lighthouseResult"]["audits"][audit]["score"]
            audit_url = j["id"]
            dv = "No Returned Value"
            items = 0

            if "displayValue" in j["lighthouseResult"]["audits"][audit]:
                dv = j["lighthouseResult"]["audits"][audit]["displayValue"].replace(u'\xa0', '')

            if "items" in j["lighthouseResult"]["audits"][audit]["details"]:
                items = len(j["lighthouseResult"]["audits"][audit]["details"]["items"])

            if audit_id == "render-blocking-resources":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["render-blocking-resources"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["render-blocking-resources"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["render-blocking-resources"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["render-blocking-resources"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["render-blocking-resources"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["render-blocking-resources"].append([audit_url, "Failed", dv, items])
            elif audit_id == "uses-responsive-images":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["uses-responsive-images"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-responsive-images"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["uses-responsive-images"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-responsive-images"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["uses-responsive-images"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-responsive-images"].append([audit_url, "Failed", dv, items])
            elif audit_id == "offscreen-images":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["offscreen-images"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["offscreen-images"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["offscreen-images"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["offscreen-images"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["offscreen-images"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["offscreen-images"].append([audit_url, "Failed", dv, items])
            elif audit_id == "unminified-css":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["unminified-css"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["unminified-css"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["unminified-css"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["unminified-css"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["unminified-css"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["unminified-css"].append([audit_url, "Failed", dv, items])
            elif audit_id == "unminified-javascript":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["unminified-javascript"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["unminified-javascript"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["unminified-javascript"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["unminified-javascript"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["unminified-javascript"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["unminified-javascript"].append([audit_url, "Failed", dv, items])
            elif audit_id == "unused-css-rules":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["unused-css-rules"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["unused-css-rules"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["unused-css-rules"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["unused-css-rules"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["unused-css-rules"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["unused-css-rules"].append([audit_url, "Failed", dv, items])
            elif audit_id == "uses-optimized-images":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["uses-optimized-images"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-optimized-images"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["uses-optimized-images"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-optimized-images"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["uses-optimized-images"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-optimized-images"].append([audit_url, "Failed", dv, items])
            elif audit_id == "uses-webp-images":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["uses-webp-images"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-webp-images"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["uses-webp-images"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-webp-images"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["uses-webp-images"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-webp-images"].append([audit_url, "Failed", dv, items])
            elif audit_id == "uses-text-compression":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["uses-text-compression"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-text-compression"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["uses-text-compression"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-text-compression"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["uses-text-compression"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-text-compression"].append([audit_url, "Failed", dv, items])
            elif audit_id == "uses-rel-preconnect":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["uses-rel-preconnect"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-rel-preconnect"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["uses-rel-preconnect"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-rel-preconnect"].append([audit_url, "Passed", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["uses-rel-preconnect"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-rel-preconnect"].append([audit_url, "Passed", dv, items])
            elif audit_id == "time-to-first-byte":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["time-to-first-byte"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["time-to-first-byte"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["time-to-first-byte"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["time-to-first-byte"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["time-to-first-byte"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["time-to-first-byte"].append([audit_url, "Failed", dv, items])
            elif audit_id == "redirects":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["redirects"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["redirects"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["redirects"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["redirects"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["redirects"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["redirects"].append([audit_url, "Failed", dv, items])
            elif audit_id == "uses-rel-preload":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["uses-rel-preload"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-rel-preload"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["uses-rel-preload"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-rel-preload"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["uses-rel-preload"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-rel-preload"].append([audit_url, "Failed", dv, items])
            elif audit_id == "efficient-animated-content":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["efficient-animated-content"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["efficient-animated-content"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["efficient-animated-content"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["efficient-animated-content"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["efficient-animated-content"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["efficient-animated-content"].append([audit_url, "Failed", dv, items])
            elif audit_id == "total-byte-weight":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["total-byte-weight"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["total-byte-weight"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["total-byte-weight"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["total-byte-weight"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["total-byte-weight"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["total-byte-weight"].append([audit_url, "Failed", dv, items])
            elif audit_id == "uses-long-cache-ttl":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["uses-long-cache-ttl"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-long-cache-ttl"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["uses-long-cache-ttl"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-long-cache-ttl"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["uses-long-cache-ttl"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["uses-long-cache-ttl"].append([audit_url, "Failed", dv, items])
            elif audit_id == "dom-size":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["dom-size"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["dom-size"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["dom-size"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["dom-size"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["dom-size"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["dom-size"].append([audit_url, "Failed", dv, items])
            elif audit_id == "critical-request-chains":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["critical-request-chains"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["critical-request-chains"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["critical-request-chains"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["critical-request-chains"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["critical-request-chains"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["critical-request-chains"].append([audit_url, "Failed", dv, items])
            elif audit_id == "network-requests":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["network-requests"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["network-requests"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["network-requests"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["network-requests"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["network-requests"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["network-requests"].append([audit_url, "Failed", dv, items])
            elif audit_id == "bootup-time":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["bootup-time"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["bootup-time"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["bootup-time"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["bootup-time"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["bootup-time"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["bootup-time"].append([audit_url, "Failed", dv, items])
            elif audit_id == "mainthread-work-breakdown":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["mainthread-work-breakdown"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["mainthread-work-breakdown"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["mainthread-work-breakdown"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["mainthread-work-breakdown"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["mainthread-work-breakdown"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["mainthread-work-breakdown"].append([audit_url, "Failed", dv, items])
            elif audit_id == "font-display":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_perf_urls["font-display"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["font-display"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_perf_urls["font-display"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_perf_urls["font-display"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_perf_urls["font-display"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_perf_urls["font-display"].append([audit_url, "Failed", dv, items])

    def parse_seo(self, j, device):
        s_audits = ["canonical", "is-crawlable", "hreflang", "font-size", "document-title", "robots-txt", "http-status-code", "link-text", "plugins", "meta-description", "viewport", "structured-data", "mobile-friendly"]

        for audit in j["lighthouseResult"]["audits"]:

            if audit not in s_audits:
                continue

            audit_id = j["lighthouseResult"]["audits"][audit]["id"]
            audit_score = j["lighthouseResult"]["audits"][audit]["score"]
            audit_url = j["id"]
            dv = "No Returned Value"
            items = 0

            if "displayValue" in j["lighthouseResult"]["audits"][audit]:
                dv = j["lighthouseResult"]["audits"][audit]["displayValue"].replace(u'\xa0', '')
            else:
                dv = j["lighthouseResult"]["audits"][audit]["title"]

            if "details" in j["lighthouseResult"]["audits"][audit]:
                if "items" in j["lighthouseResult"]["audits"][audit]["details"]:
                    items = len(j["lighthouseResult"]["audits"][audit]["details"]["items"])

            if audit_id == "canonical":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_seo_urls["canonical"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["canonical"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_seo_urls["canonical"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_seo_urls["canonical"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_seo_urls["canonical"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["canonical"].append([audit_url, "Failed", dv, items])
            elif audit_id == "is-crawlable":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_seo_urls["is-crawlable"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["is-crawlable"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_seo_urls["is-crawlable"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_seo_urls["is-crawlable"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_seo_urls["is-crawlable"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["is-crawlable"].append([audit_url, "Failed", dv, items])
            elif audit_id == "hreflang":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_seo_urls["hreflang"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["hreflang"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_seo_urls["hreflang"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_seo_urls["hreflang"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_seo_urls["hreflang"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["hreflang"].append([audit_url, "Failed", dv, items])
            elif audit_id == "font-size":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_seo_urls["font-size"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["font-size"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_seo_urls["font-size"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_seo_urls["font-size"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_seo_urls["font-size"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["font-size"].append([audit_url, "Failed", dv, items])
            elif audit_id == "document-title":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_seo_urls["document-title"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["document-title"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_seo_urls["document-title"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_seo_urls["document-title"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_seo_urls["document-title"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["document-title"].append([audit_url, "Failed", dv, items])
            elif audit_id == "robots-txt":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_seo_urls["robots-txt"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["robots-txt"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_seo_urls["robots-txt"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_seo_urls["robots-txt"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_seo_urls["robots-txt"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["robots-txt"].append([audit_url, "Failed", dv, items])
            elif audit_id == "http-status-code":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_seo_urls["http-status-code"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["http-status-code"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_seo_urls["http-status-code"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_seo_urls["http-status-code"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_seo_urls["http-status-code"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["http-status-code"].append([audit_url, "Failed", dv, items])
            elif audit_id == "link-text":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_seo_urls["link-text"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["link-text"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_seo_urls["link-text"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_seo_urls["link-text"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_seo_urls["link-text"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["link-text"].append([audit_url, "Failed", dv, items])
            elif audit_id == "plugins":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_seo_urls["plugins"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["plugins"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_seo_urls["plugins"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_seo_urls["plugins"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_seo_urls["plugins"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["plugins"].append([audit_url, "Failed", dv, items])
            elif audit_id == "meta-description":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_seo_urls["meta-description"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["meta-description"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_seo_urls["meta-description"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_seo_urls["meta-description"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_seo_urls["meta-description"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["meta-description"].append([audit_url, "Failed", dv, items])
            elif audit_id == "viewport":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_seo_urls["viewport"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["viewport"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_seo_urls["viewport"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_seo_urls["viewport"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_seo_urls["viewport"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["viewport"].append([audit_url, "Failed", dv, items])
            elif audit_id == "structured-data":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_seo_urls["structured-data"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["structured-data"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_seo_urls["structured-data"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_seo_urls["structured-data"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_seo_urls["structured-data"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["structured-data"].append([audit_url, "Failed", dv, items])
            elif audit_id == "mobile-friendly":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_seo_urls["mobile-friendly"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["mobile-friendly"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_seo_urls["mobile-friendly"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_seo_urls["mobile-friendly"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_seo_urls["mobile-friendly"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_seo_urls["mobile-friendly"].append([audit_url, "Failed", dv, items])

    def parse_best_practices(self, j, device):
        bp_audits = ["appcache-manifest", "is-on-https", "uses-passive-event-listeners", "no-document-write", "external-anchors-use-rel-noopener", "geolocation-on-start", "doctype", "no-vulnerable-libraries", "js-libraries", "notification-on-start", "deprecations", "password-inputs-can-be-pasted-into", "errors-in-console", "image-aspect-ratio"]

        for audit in j["lighthouseResult"]["audits"]:

            if audit not in bp_audits:
                continue

            audit_id = j["lighthouseResult"]["audits"][audit]["id"]
            audit_score = j["lighthouseResult"]["audits"][audit]["score"]
            audit_url = j["id"]
            dv = "No Returned Value"
            items = 0

            if "displayValue" in j["lighthouseResult"]["audits"][audit]:
                dv = j["lighthouseResult"]["audits"][audit]["displayValue"].replace(u'\xa0', '')
            else:
                dv = j["lighthouseResult"]["audits"][audit]["title"]

            if "details" in j["lighthouseResult"]["audits"][audit]:
                if "items" in j["lighthouseResult"]["audits"][audit]["details"]:
                    items = len(j["lighthouseResult"]["audits"][audit]["details"]["items"])

            if audit_id == "appcache-manifest":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_bestpractice_urls["appcache-manifest"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["appcache-manifest"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_bestpractice_urls["appcache-manifest"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["appcache-manifest"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_bestpractice_urls["appcache-manifest"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["appcache-manifest"].append([audit_url, "Failed", dv, items])
            elif audit_id == "is-on-https":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_bestpractice_urls["is-on-https"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["is-on-https"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_bestpractice_urls["is-on-https"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["is-on-https"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_bestpractice_urls["is-on-https"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["is-on-https"].append([audit_url, "Failed", dv, items])
            elif audit_id == "uses-passive-event-listeners":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_bestpractice_urls["uses-passive-event-listeners"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["uses-passive-event-listeners"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_bestpractice_urls["uses-passive-event-listeners"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["uses-passive-event-listeners"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_bestpractice_urls["uses-passive-event-listeners"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["uses-passive-event-listeners"].append([audit_url, "Failed", dv, items])
            elif audit_id == "no-document-write":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_bestpractice_urls["no-document-write"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["no-document-write"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_bestpractice_urls["no-document-write"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["no-document-write"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_bestpractice_urls["no-document-write"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["no-document-write"].append([audit_url, "Failed", dv, items])
            elif audit_id == "external-anchors-use-rel-noopener":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_bestpractice_urls["external-anchors-use-rel-noopener"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["external-anchors-use-rel-noopener"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_bestpractice_urls["external-anchors-use-rel-noopener"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["external-anchors-use-rel-noopener"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_bestpractice_urls["external-anchors-use-rel-noopener"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["external-anchors-use-rel-noopener"].append([audit_url, "Failed", dv, items])
            elif audit_id == "geolocation-on-start":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_bestpractice_urls["geolocation-on-start"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["geolocation-on-start"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_bestpractice_urls["geolocation-on-start"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["geolocation-on-start"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_bestpractice_urls["geolocation-on-start"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["geolocation-on-start"].append([audit_url, "Failed", dv, items])
            elif audit_id == "doctype":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_bestpractice_urls["doctype"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["doctype"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_bestpractice_urls["doctype"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["doctype"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_bestpractice_urls["doctype"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["doctype"].append([audit_url, "Failed", dv, items])
            elif audit_id == "no-vulnerable-libraries":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_bestpractice_urls["no-vulnerable-libraries"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["no-vulnerable-libraries"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_bestpractice_urls["no-vulnerable-libraries"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["no-vulnerable-libraries"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_bestpractice_urls["no-vulnerable-libraries"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["no-vulnerable-libraries"].append([audit_url, "Failed", dv, items])
            elif audit_id == "js-libraries":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_bestpractice_urls["js-libraries"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["js-libraries"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_bestpractice_urls["js-libraries"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["js-libraries"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_bestpractice_urls["js-libraries"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["js-libraries"].append([audit_url, "Failed", dv, items])
            elif audit_id == "notification-on-start":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_bestpractice_urls["notification-on-start"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["notification-on-start"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_bestpractice_urls["notification-on-start"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["notification-on-start"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_bestpractice_urls["notification-on-start"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["notification-on-start"].append([audit_url, "Failed", dv, items])
            elif audit_id == "deprecations":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_bestpractice_urls["deprecations"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["deprecations"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_bestpractice_urls["deprecations"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["deprecations"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_bestpractice_urls["deprecations"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["deprecations"].append([audit_url, "Failed", dv, items])
            elif audit_id == "password-inputs-can-be-pasted-into":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_bestpractice_urls["password-inputs-can-be-pasted-into"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["password-inputs-can-be-pasted-into"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_bestpractice_urls["password-inputs-can-be-pasted-into"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["password-inputs-can-be-pasted-into"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_bestpractice_urls["password-inputs-can-be-pasted-into"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["password-inputs-can-be-pasted-into"].append([audit_url, "Failed", dv, items])
            elif audit_id == "errors-in-console":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_bestpractice_urls["errors-in-console"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["errors-in-console"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_bestpractice_urls["errors-in-console"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["errors-in-console"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_bestpractice_urls["errors-in-console"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["errors-in-console"].append([audit_url, "Failed", dv, items])
            elif audit_id == "image-aspect-ratio":
                if audit_score == 1.0:
                    if device == "mobile":
                        m_bestpractice_urls["image-aspect-ratio"].append([audit_url, "Passed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["image-aspect-ratio"].append([audit_url, "Passed", dv, items])
                elif audit_score is None:
                    if device == "mobile":
                        m_bestpractice_urls["image-aspect-ratio"].append([audit_url, "No Pass/Fail", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["image-aspect-ratio"].append([audit_url, "No Pass/Fail", dv, items])
                else:
                    if device == "mobile":
                        m_bestpractice_urls["image-aspect-ratio"].append([audit_url, "Failed", dv, items])
                    elif device == "desktop":
                        d_bestpractice_urls["image-aspect-ratio"].append([audit_url, "Failed", dv, items])

    def parse_loading_experience(self, j):
        try:
            fcp = j["loadingExperience"]["metrics"]["FIRST_CONTENTFUL_PAINT_MS"]["category"]
        except:
            fcp = "N/A"

        try:
            fid = j["loadingExperience"]["metrics"]["FIRST_CONTENTFUL_PAINT_MS"]["category"]
        except:
            fid = "N/A"
        
        try:
            overall = j["loadingExperience"]["overall_category"]
        except:
            overall = "N/A"
        
        try:
            contentful = j["lighthouseResult"]["audits"]["first-contentful-paint"]["displayValue"]
        except:
            contentful = "N/A"

        try:
            meaningful = j["lighthouseResult"]["audits"]["first-meaningful-paint"]["displayValue"]
        except:
            meaningful = "N/A"

        try:
            interactive = j["lighthouseResult"]["audits"]["interactive"]["displayValue"]
        except:
            interactive = "N/A" 

        return [fcp.strip(), fid.strip(), overall.strip(), contentful.replace(u'\xa0s', '').strip(), meaningful.replace(u'\xa0s', '').strip(), interactive.replace(u'\xa0s', '').strip()]
    
    def parse_opportunities(self, j, device):
        try:
            lighthouse = j["lighthouseResult"]["audits"]
            if device == "mobile":
                for value in lighthouse:
                    try:
                        if lighthouse[value]["details"]["type"] == "opportunity":
                            if lighthouse[value]["score"] < 1:
                                if value in m_opps_data:
                                    m_opps_data[value]["Count"] = m_opps_data[value]["Count"] + 1
                                    m_opps_data[value]["Average Time Saved"] = m_opps_data[value]["Average Time Saved"] + lighthouse[value]["details"]["overallSavingsMs"]
                                else:
                                    m_opps_data[value] = {"Title": lighthouse[value]["title"], "Description":lighthouse[value]["description"], "Average Time Saved": lighthouse[value]["details"]["overallSavingsMs"], "Count": 1}
                    except:
                        continue
            else:
                for value in lighthouse:
                    try:
                        if lighthouse[value]["details"]["type"] == "opportunity":
                            if lighthouse[value]["score"] < 1:
                                if value in d_opps_data:
                                    d_opps_data[value]["Count"] = d_opps_data[value]["Count"] + 1
                                    d_opps_data[value]["Average Time Saved"] = d_opps_data[value]["Average Time Saved"] + lighthouse[value]["details"]["overallSavingsMs"]
                                else:
                                    d_opps_data[value] = {"Title": lighthouse[value]["title"], "Description":lighthouse[value]["description"], "Average Time Saved": lighthouse[value]["details"]["overallSavingsMs"], "Count": 1}
                    except:
                        continue
        except:
            print("No Opps")

class PageSpeedThread(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            url = self.queue.get()
            try:
                s = ""
                if c_seo is True:
                    s += "&category=seo"
                if c_best_practices is True:
                    s += "&category=best-practices"
                if c_performance is True:
                    s += "&category=performance"

                if s_mobile is True:
                    r = requests.get("https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=" + url + "&key=" + API_KEY + "&strategy=mobile" + s)

                    j = r.json()

                    m_all_url_data[j["id"]] = JSONParser().parse_loading_experience(j)
                    JSONParser().parse_opportunities(j, "mobile")

                    if c_best_practices is True:
                        JSONParser().parse_best_practices(j, "mobile")
                    if c_performance is True:
                        JSONParser().parse_performance(j, "mobile")
                    if c_seo is True:
                        JSONParser().parse_seo(j, "mobile")
                    

                if s_desktop is True:
                    r = requests.get("https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=" + url + "&key=" + API_KEY + "&strategy=desktop" + s)
                    j = r.json()
                    d_all_url_data[j["id"]] = JSONParser().parse_loading_experience(j)
                    JSONParser().parse_opportunities(j, "desktop")

                    if c_best_practices is True:
                        JSONParser().parse_best_practices(j, "desktop")
                    if c_performance is True:
                        JSONParser().parse_performance(j, "desktop")
                    if c_seo is True:
                        JSONParser().parse_seo(j, "desktop")
                    
            except:
                self._stop()
                messagebox.showerror(title="Error Processing Threads", message="There was an issue running the system, please try again or consult the developer.")
                sys.exit()
            finally:
                self.queue.task_done()


if __name__ == "__main__":   
    p = PageSpeedApp()
    p.window.mainloop()