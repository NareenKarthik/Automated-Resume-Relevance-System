import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import PyPDF2
import docx
import re
import datetime
import os
import shutil
import json
import atexit

# ---------------- Global Variables ----------------
UPLOAD_FOLDER = "C:/Users/naree/Downloads/ATS_Uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DATA_FILE = os.path.join(UPLOAD_FOLDER, "uploaded_files.json")

# Load previously saved uploaded files
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        uploaded_files = json.load(f)
else:
    uploaded_files = []

selected_candidates = []
targeted_skills = []
targeted_exp = 0
SUBWINDOW_BG = "#7B68EE"  # Purple-ish background
password = "admin123"      # Default password

# ---------------- Save on Exit ----------------
def save_uploaded_files():
    with open(DATA_FILE, "w") as f:
        json.dump(uploaded_files, f, indent=4)
atexit.register(save_uploaded_files)

# ---------------- Password Functions ----------------
def verify_password():
    pwd = simpledialog.askstring("Password", "Enter password:", show="*")
    return pwd == password

def change_password():
    if not verify_password():
        messagebox.showerror("Access Denied", "Incorrect password!")
        return
    
    def save_new_password():
        global password
        new_pwd = new_pwd_entry.get().strip()
        confirm_pwd = confirm_pwd_entry.get().strip()
        if new_pwd and new_pwd == confirm_pwd:
            password = new_pwd
            messagebox.showinfo("Settings", "Password changed successfully!")
            settings_window.destroy()
        else:
            messagebox.showerror("Settings", "Passwords do not match or empty!")
    
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings - Change Password")
    settings_window.geometry("400x200")
    settings_window.configure(bg=SUBWINDOW_BG)
    
    tk.Label(settings_window, text="New Password:", font=("Helvetica", 12, "bold"), bg=SUBWINDOW_BG, fg="white").pack(pady=5)
    new_pwd_entry = tk.Entry(settings_window, show="*")
    new_pwd_entry.pack(pady=5)
    
    tk.Label(settings_window, text="Confirm Password:", font=("Helvetica", 12, "bold"), bg=SUBWINDOW_BG, fg="white").pack(pady=5)
    confirm_pwd_entry = tk.Entry(settings_window, show="*")
    confirm_pwd_entry.pack(pady=5)
    
    tk.Button(settings_window, text="Save", bg="#4CAF50", fg="white", command=save_new_password).pack(pady=10)

# ---------------- Upload Functions ----------------
def upload_document():
    file_path = filedialog.askopenfilename(
        title="Select Document File",
        filetypes=[("Word Documents", "*.docx *.doc"), ("All Files", "*.*")]
    )
    if file_path:
        filename = os.path.basename(file_path)
        target_path = os.path.join(UPLOAD_FOLDER, filename)
        shutil.copy(file_path, target_path)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uploaded_files.append((target_path, timestamp))
        messagebox.showinfo("File Uploaded", f"Document saved to:\n{target_path}\nTime: {timestamp}")

def upload_pdf():
    file_path = filedialog.askopenfilename(
        title="Select PDF File",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if file_path:
        filename = os.path.basename(file_path)
        target_path = os.path.join(UPLOAD_FOLDER, filename)
        shutil.copy(file_path, target_path)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uploaded_files.append((target_path, timestamp))
        messagebox.showinfo("File Uploaded", f"PDF saved to:\n{target_path}\nTime: {timestamp}")

# ---------------- Job Info ----------------
def targeted_job_info():
    def save_job_info():
        global targeted_skills, targeted_exp
        text = skills_text.get("1.0", tk.END).strip()
        targeted_skills = [skill.strip().lower() for skill in text.split(",")]
        try:
            targeted_exp = int(exp_entry.get())
        except:
            targeted_exp = 0
        messagebox.showinfo("Saved", "Job info saved")
        job_window.destroy()
    
    job_window = tk.Toplevel(root)
    job_window.title("Targeted Job Info")
    job_window.geometry("400x350")
    job_window.configure(bg=SUBWINDOW_BG)
    
    tk.Label(job_window, text="Enter required skills (comma separated):", font=("Helvetica", 12, "bold"), bg=SUBWINDOW_BG, fg="white").pack(pady=5)
    skills_text = tk.Text(job_window, height=5, width=40)
    skills_text.pack(pady=5)
    
    tk.Label(job_window, text="Minimum Experience (years):", font=("Helvetica", 12, "bold"), bg=SUBWINDOW_BG, fg="white").pack(pady=5)
    exp_entry = tk.Entry(job_window)
    exp_entry.pack(pady=5)
    
    tk.Button(job_window, text="Save", bg="#4CAF50", fg="white", command=save_job_info).pack(pady=10)

# ---------------- View Uploaded Files ----------------
def view_uploaded_files():
    if not verify_password():
        messagebox.showerror("Access Denied", "Incorrect password!")
        return
    
    if not uploaded_files:
        messagebox.showinfo("Uploaded Files", "No files uploaded yet.")
        return
    
    files_window = tk.Toplevel(root)
    files_window.title("Uploaded Files")
    files_window.geometry("500x350")
    files_window.configure(bg=SUBWINDOW_BG)
    
    tk.Label(files_window, text="Uploaded Files (with time):", font=("Helvetica", 12, "bold"), bg=SUBWINDOW_BG, fg="white").pack(pady=10)
    
    listbox = tk.Listbox(files_window, width=70, height=15)
    listbox.pack(pady=10)
    
    for f, t in uploaded_files:
        listbox.insert(tk.END, f"{f} | Uploaded at: {t}")

# ---------------- Resume Parsing ----------------
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
    except:
        pass
    return text.lower()

def extract_text_from_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except:
        pass
    return text.lower()

def extract_candidate_info(text):
    info = {}
    name_match = re.search(r"(Name|Full Name)\s*[:\-]\s*(.*)", text, re.IGNORECASE)
    info['Name'] = name_match.group(2).strip() if name_match else "Unknown"
    
    skills_match = re.search(r"(Skills?)\s*[:\-]\s*(.*)", text, re.IGNORECASE)
    if skills_match:
        skills_text = skills_match.group(2).strip().lower()
        info['Skills'] = [s.strip() for s in re.split(r",|;", skills_text)]
    else:
        info['Skills'] = []
    
    exp_match = re.search(r"(Experience|Exp)\s*[:\-]?\s*(\d+)", text, re.IGNORECASE)
    info['Experience'] = int(exp_match.group(2)) if exp_match else 0
    
    sal_match = re.search(r"(Salary|CTC|Expected Salary)\s*[:\-]?\s*(\d+)", text, re.IGNORECASE)
    info['Salary'] = int(sal_match.group(2)) if sal_match else 0
    
    return info

# ---------------- ATS Logic with Checkboxes ----------------
def select_candidates():
    if not verify_password():
        messagebox.showerror("Access Denied", "Incorrect password!")
        return
    
    if not uploaded_files:
        messagebox.showinfo("Select Candidates", "No uploaded files to check.")
        return
    if not targeted_skills:
        messagebox.showinfo("Select Candidates", "Please enter targeted job skills first.")
        return
    
    selected_candidates.clear()
    
    for file, _ in uploaded_files:
        if file.lower().endswith(".pdf"):
            text = extract_text_from_pdf(file)
        else:
            text = extract_text_from_docx(file)
        
        candidate_info = extract_candidate_info(text)
        matched_skills = set(candidate_info['Skills']).intersection(set(targeted_skills))
        score = len(matched_skills)
        if candidate_info['Experience'] >= targeted_exp:
            score += 1
        if score > 0:
            selected_candidates.append((candidate_info['Name'], file, score, matched_skills, candidate_info['Experience']))
    
    if selected_candidates:
        result_window = tk.Toplevel(root)
        result_window.title("Selected Candidates")
        result_window.geometry("650x450")
        result_window.configure(bg=SUBWINDOW_BG)
        
        tk.Label(result_window, text="Select Candidates:", font=("Helvetica", 12, "bold"), bg=SUBWINDOW_BG, fg="white").pack(pady=10)
        
        # Scrollable frame
        canvas_frame = tk.Canvas(result_window, bg=SUBWINDOW_BG)
        scrollbar = tk.Scrollbar(result_window, orient="vertical", command=canvas_frame.yview)
        scrollable_frame = tk.Frame(canvas_frame, bg=SUBWINDOW_BG)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_frame.configure(scrollregion=canvas_frame.bbox("all"))
        )
        canvas_frame.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_frame.configure(yscrollcommand=scrollbar.set)
        canvas_frame.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store checkbutton variables
        check_vars = []

        for idx, c in enumerate(selected_candidates):
            name, file, score, skills, exp = c
            var = tk.IntVar(value=1)  # Pre-ticked
            check_vars.append((var, c))
            text_display = f"{name} | Exp: {exp} | Score: {score} | Skills: {', '.join(skills)}"
            cb = tk.Checkbutton(scrollable_frame, text=text_display, variable=var, bg=SUBWINDOW_BG, fg="white",
                                selectcolor="green", anchor="w", justify="left", font=("Helvetica", 10, "bold"))
            cb.pack(fill="x", pady=2)
        
        def show_selected():
            selected = [c[1] for v, c in check_vars if v.get() == 1]
            messagebox.showinfo("Selected Candidates", f"{len(selected)} candidate(s) selected:\n" + "\n".join(selected))
        
        tk.Button(result_window, text="Confirm Selection", bg="#4CAF50", fg="white", command=show_selected).pack(pady=10)
    
    else:
        messagebox.showinfo("Selected Candidates", "No candidates matched the targeted skills.")

# ---------------- GUI Setup ----------------
root = tk.Tk()
root.title("ATS File Upload Portal")
root.geometry("500x650")

# Main Window Background Image (JPEG)
try:
    bg_image = Image.open("C:/Users/naree/Downloads/download (8).jpeg")
    bg_image = bg_image.resize((500, 650))
    bg_photo = ImageTk.PhotoImage(bg_image)
    canvas = tk.Canvas(root, width=500, height=650)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    canvas.image = bg_photo
except:
    canvas = tk.Canvas(root, width=500, height=650, bg="gray")
    canvas.pack(fill="both", expand=True)

# Main window widgets on canvas
title_label = tk.Label(root, text="Welcome to ATS File Upload", font=("Helvetica", 16, "bold"), bg="#000000", fg="white")
canvas.create_window(250, 30, window=title_label)

btn_doc = tk.Button(root, text="Upload Document", command=upload_document, bg="#00FFFF", fg="purple", font=("Helvetica", 14, "bold"), width=30, height=2)
canvas.create_window(250, 100, window=btn_doc)

btn_pdf = tk.Button(root, text="Upload PDF", command=upload_pdf, bg="#FF6A6A", fg="purple", font=("Helvetica", 14, "bold"), width=30, height=2)
canvas.create_window(250, 170, window=btn_pdf)

btn_job = tk.Button(root, text="Targeted Job Info", command=targeted_job_info, bg="#FFD700", fg="black", font=("Helvetica", 14, "bold"), width=30, height=2)
canvas.create_window(250, 240, window=btn_job)

btn_uploaded = tk.Button(root, text="Uploaded Files", command=view_uploaded_files, bg="#32CD32", fg="white", font=("Helvetica", 14, "bold"), width=30, height=2)
canvas.create_window(250, 310, window=btn_uploaded)

btn_select = tk.Button(root, text="Select Candidates", command=select_candidates, bg="#FF8C00", fg="white", font=("Helvetica", 14, "bold"), width=30, height=2)
canvas.create_window(250, 380, window=btn_select)

btn_settings = tk.Button(root, text="Settings", command=change_password, bg="#1E90FF", fg="white", font=("Helvetica", 14, "bold"), width=30, height=2)
canvas.create_window(250, 450, window=btn_settings)

root.mainloop()
