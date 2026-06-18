import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
import pdfplumber
import os
from PIL import Image
# LOAD MERCHANT CATEGORY FILE
merchant_map = {}

if os.path.exists("merchant_categories.csv"):

    df_map = pd.read_csv("merchant_categories.csv", header=None)

    for i,row in df_map.iterrows():
        merchant = str(row[0]).lower()
        category = str(row[1])

        merchant_map[merchant] = category

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1000x600")
app.title("Finance Tracker")

file_path = ""
dataframe = None


# -------------------------------
# FUNCTION TO SWITCH PAGES
# -------------------------------

def show_frame(frame):
    frame.tkraise()


# -------------------------------
# FUNCTION TO READ PDF
# -------------------------------

def read_pdf_statement(path):

    rows = []

    with pdfplumber.open(path) as pdf:

        for page in pdf.pages:

            table = page.extract_table()

            if table is None:
                continue

            for row in table[1:]:

                if len(row) >= 3:
                    rows.append([row[0], row[1], row[2]])

    df = pd.DataFrame(rows, columns=["Date","Description","Amount"])

    return df


# -------------------------------
# HOME PAGE
# -------------------------------

home_frame = ctk.CTkFrame(app)
home_frame.grid(row=0,column=0,sticky="nsew")

logo_image = ctk.CTkImage(
    light_image=Image.open("FT_logo.png"),
    dark_image=Image.open("FT_logo.png"),
    size=(120,120)
)

logo_label = ctk.CTkLabel(home_frame,image=logo_image,text="")
logo_label.pack(pady=20)

title = ctk.CTkLabel(home_frame,text="Finance Tracker (FT)",font=("Arial",40))
title.pack(pady=20)

start_btn = ctk.CTkButton(home_frame,text="Start",
                          command=lambda:show_frame(upload_frame))
start_btn.pack()


# -------------------------------
# UPLOAD PAGE
# -------------------------------

upload_frame = ctk.CTkFrame(app)
upload_frame.grid(row=0,column=0,sticky="nsew")

upload_title = ctk.CTkLabel(upload_frame,
                            text="Upload Bank Statement",
                            font=("Arial",28))
upload_title.pack(pady=40)

file_label = ctk.CTkLabel(upload_frame,text="No file selected")
file_label.pack(pady=10)


def upload_file():

    global file_path

    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Excel files","*.xlsx"),
            ("PDF files","*.pdf"),
            ("All files","*.*")
        ])

    file_label.configure(text=file_path)


upload_btn = ctk.CTkButton(upload_frame,
                           text="Choose File",
                           command=upload_file)
upload_btn.pack(pady=10)


# -------------------------------
# ANALYZE FILE
# -------------------------------

def analyze_file():

    global dataframe

    if file_path == "":
        file_label.configure(text="Please choose a file first")
        return

    if file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)

    elif file_path.endswith(".pdf"):
        df = read_pdf_statement(file_path)

    else:
        file_label.configure(text="Unsupported file type")
        return


    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    df = df.dropna(subset=["Date","Amount"])

    df["Month"] = df["Date"].dt.strftime("%B")
    df["Year"] = df["Date"].dt.year

    categories = {
        "Food":["biryani","pizza","burger","restaurant","swiggy","zomato","Cafe Latte","Starbucks Coffe","Tea Stall","Burger Restaurant"],
        "Shopping":["amazon","flipkart","myntra","meesho","nykaa", "Zudio","Ajio"],
        "Entertainment":["movie","cinema","netflix","spotify","prime",'Tataplay',"Hotstar Subscription","BookMyShow Movie","Internet Broadband","PVR Cinema Ticket"],
        "Study":["book","stationery","pen","notebook"],
        "Transport":["uber","ola","metro","bus","petrol",'Parking fee',''],
        "Bills":["electricity","wifi","recharge","airtel","jio"]
    }

    def detect_category(text):

        text = str(text).lower()

        for cat,words in categories.items():
            for w in words:
                if w in text:
                    return cat

        return "Other"

    df["Category"] = df["Description"].apply(detect_category)

    dataframe = df


    for widget in month_buttons_frame.winfo_children():
        widget.destroy()


    month_order = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
    ]

    for m in month_order:

        btn = ctk.CTkButton(
            month_buttons_frame,
            text=m,
            width=160,
            command=lambda x=m:show_month(x)
        )

        btn.pack(pady=5)

    show_frame(dashboard_frame)


analyze_btn = ctk.CTkButton(upload_frame,
                            text="Analyze",
                            command=analyze_file)
analyze_btn.pack(pady=20)


# -------------------------------
# DASHBOARD PAGE
# -------------------------------

dashboard_frame = ctk.CTkFrame(app)
dashboard_frame.grid(row=0,column=0,sticky="nsew")

sidebar = ctk.CTkFrame(dashboard_frame,width=200)
sidebar.pack(side="left",fill="y")

home_btn = ctk.CTkButton(sidebar,text="Home",
                         command=lambda:show_frame(home_frame))
home_btn.pack(pady=10)

upload_btn2 = ctk.CTkButton(sidebar,text="Upload",
                            command=lambda:show_frame(upload_frame))
upload_btn2.pack(pady=10)

# ⭐ NEW BUTTON (OVERALL EXPENSE)

overall_btn = ctk.CTkButton(
    sidebar,
    text="Overall Expense",
    command=lambda:show_year()
)

overall_btn.pack(pady=10)

month_buttons_frame = ctk.CTkFrame(sidebar)
month_buttons_frame.pack(pady=20)


main_area = ctk.CTkFrame(dashboard_frame)
main_area.pack(side="right",expand=True,fill="both")

report_box = ctk.CTkTextbox(main_area,width=300)
report_box.pack(pady=10)

chart_area = ctk.CTkFrame(main_area)
chart_area.pack(expand=True,fill="both")

chart_button = ctk.CTkButton(main_area,text="Show Pie Chart")


# -------------------------------
# SHOW MONTH REPORT
# -------------------------------

def show_month(month):

    global dataframe

    for widget in chart_area.winfo_children():
        widget.destroy()

    report_box.delete("1.0","end")

    month_data = dataframe[dataframe["Month"] == month]

    if month_data.empty:

        report_box.insert("end",f"\nMonth : {month}\n\n")
        report_box.insert("end","No transactions found.")

        chart_button.pack_forget()

        return

    summary = month_data.groupby("Category")["Amount"].sum()

    report_box.insert("end",f"\nMonth : {month}\n\n")

    for cat,amt in summary.items():
        report_box.insert("end",f"{cat:<15}{amt}\n")

    total = month_data["Amount"].sum()

    report_box.insert("end",f"\nTotal : {total}")


    def draw_chart():

        for widget in chart_area.winfo_children():
            widget.destroy()

        fig = plt.Figure(figsize=(4,4))
        ax = fig.add_subplot(111)

        summary.plot(kind="pie",ax=ax,autopct="%1.1f%%")
        ax.set_ylabel("")

        canvas = FigureCanvasTkAgg(fig,chart_area)
        canvas.draw()
        canvas.get_tk_widget().pack()

    chart_button.configure(command=draw_chart)
    chart_button.pack(pady=10)


# -------------------------------
# SHOW YEARLY REPORT
# -------------------------------

def show_year():

    global dataframe

    report_box.delete("1.0","end")

    for widget in chart_area.winfo_children():
        widget.destroy()

    summary = dataframe.groupby("Category")["Amount"].sum()

    year = dataframe["Year"].iloc[0]

    report_box.insert("end",f"\nYear : {year}\n\n")

    for cat,amt in summary.items():
        report_box.insert("end",f"{cat:<15}{amt}\n")

    total = dataframe["Amount"].sum()

    report_box.insert("end",f"\nTotal : {total}")


    def draw_chart():

        for widget in chart_area.winfo_children():
            widget.destroy()

        fig = plt.Figure(figsize=(4,4))
        ax = fig.add_subplot(111)

        summary.plot(kind="pie",ax=ax,autopct="%1.1f%%")

        ax.set_ylabel("")

        canvas = FigureCanvasTkAgg(fig,chart_area)

        canvas.draw()

        canvas.get_tk_widget().pack()

    chart_button.configure(command=draw_chart)
    chart_button.pack(pady=10)


# -------------------------------

home_frame.tkraise()

app.mainloop()