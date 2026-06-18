
import pandas as pd
import matplotlib.pyplot as plt
import os
import pdfplumber
import csv

# --------------------------------
# ENTER FILE NAME HERE
# --------------------------------

file_path = file_path

# --------------------------------
# CREATE CHART FOLDER
# --------------------------------

if not os.path.exists("charts"):
    os.makedirs("charts")

# --------------------------------
# LOAD LEARNED MERCHANT DATABASE
# --------------------------------

merchant_db = {}

if os.path.exists("merchant_categories.csv"):

    merchant_df = pd.read_csv("merchant_categories.csv")

    for i,row in merchant_df.iterrows():
        merchant_db[row["merchant"]] = row["category"]


# --------------------------------
# FUNCTION TO READ PDF
# --------------------------------

def read_pdf_statement(file):

    rows = []

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            table = page.extract_table()

            if table:

                for row in table[1:]:
                    rows.append(row)

    df = pd.DataFrame(rows, columns=["Date","Description","Amount"])

    return df


# --------------------------------
# READ FILE
# --------------------------------

if file_path.endswith(".xlsx"):

    df = pd.read_excel(file_path)

elif file_path.endswith(".pdf"):

    df = read_pdf_statement(file_path)

else:

    print("Unsupported file format")
    exit()


# --------------------------------
# CLEAN DATA
# --------------------------------

df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

df.dropna(inplace=True)

df["Month"] = df["Date"].dt.strftime("%B")

df["Year"] = df["Date"].dt.year


# --------------------------------
# CATEGORY KEYWORDS
# --------------------------------

categories = {

"Food":[
"biryani","pizza","burger","restaurant","hotel","cafe",
"swiggy","zomato","dominos","kfc","mcdonald"
],

"Shopping":[
"amazon","flipkart","myntra","meesho","nykaa","ajio"
],

"Groceries":[
"supermarket","mart","grocery","bigbasket","jiomart"
],

"Entertainment":[
"netflix","spotify","prime","hotstar","movie","cinema"
],

"Transport":[
"uber","ola","rapido","metro","petrol","fuel"
],

"Bills":[
"electricity","wifi","internet","recharge","airtel","jio"
],

"Education":[
"book","course","udemy","coursera","college"
],

"Health":[
"hospital","pharmacy","apollo","clinic"
],

"Subscriptions":[
"youtube","spotify","netflix","prime","icloud"
],

"Cash":[
"atm","withdrawal"
]

}


# --------------------------------
# AI STYLE CATEGORY DETECTION
# --------------------------------

'''def detect_category(text):

    text = str(text).lower()

    # STEP 1 → CHECK LEARNED MERCHANTS

    for merchant in merchant_db:

        if merchant in text:

            return merchant_db[merchant]


    # STEP 2 → KEYWORD MATCH

    for cat,words in categories.items():

        for w in words:

            if w in text:

                return cat


    # STEP 3 → LEARN NEW MERCHANT

    merchant_name = text.split()[0]

    merchant_db[merchant_name] = "Other"

    with open("merchant_categories.csv","a",newline="") as f:

        writer = csv.writer(f)

        writer.writerow([merchant_name,"Other"])


    print("Unknown merchant learned:",merchant_name)

    return "Other"'''
def detect_category(text):

    text = str(text).lower()

    for merchant,category in merchant_map.items():
        if merchant in text:
            return category

    return "Other"


# --------------------------------
# APPLY CATEGORY
# --------------------------------

df["Category"] = df["Description"].apply(detect_category)

print(df)


# --------------------------------
# CATEGORY SUMMARY
# --------------------------------

summary = df.groupby("Category")["Amount"].sum()

print(summary)


# --------------------------------
# YEARLY TOTAL
# --------------------------------

year_total = df["Amount"].sum()

print("\nTotal Spending This Year:",year_total)


# --------------------------------
# SAVE DATA
# --------------------------------

df.to_excel("categorized_transactions.xlsx",index=False)


# --------------------------------
# YEARLY REPORT
# --------------------------------

report = pd.DataFrame({

"Category":summary.index,

"Amount":summary.values

})

report.to_excel("yearly_financial_report.xlsx",index=False)


# --------------------------------
# PIE CHART YEARLY
# --------------------------------

summary.plot(kind="pie",autopct="%1.1f%%")

plt.title("Overall Spending Distribution")

plt.ylabel("")

plt.savefig("charts/yearly_spending.png")

plt.show()


# --------------------------------
# MONTH CHARTS
# --------------------------------

months = df["Month"].unique()

for month in months:

    mdata = df[df["Month"]==month]

    msum = mdata.groupby("Category")["Amount"].sum()

    if len(msum)>0:

        msum.plot(kind="pie",autopct="%1.1f%%")

        plt.title(f"{month} Spending")

        plt.ylabel("")

        plt.savefig(f"charts/{month}_spending.png")

        plt.show()