import yfinance as yf
import pandas as pd
import tkinter as tk
from tkinter import ttk
import sqlite3
import sv_ttk

def get_tickers():
    tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    return tickers['Symbol'].convert_dtypes(convert_string=True).tolist()

def table_exists(db, name):
    query = "SELECT 1 FROM sqlite_master WHERE type='table' and name=?"
    return db.execute(query, (name,)).fetchone() is not None

def create_tables(db, input_tickers):
    for i in input_tickers['Symbol'].tolist() :
        data = yf.Ticker(i.replace('.','-')).history(period="1yr", interval="1d", actions=False, rounding=True)
        data.drop(columns='Volume', inplace=True)
        data.reset_index(inplace=True)
        data['Date'] = data['Date'].dt.date
        data.to_sql(i, conn, schema=None, if_exists='replace', index=False)

def get_output_types() :
    output = [outputList.get(i) for i in outputList.curselection()]
    return output

def add_ticker() :

def sub_ticker() :

selected_tickers = []
export_values = ['Excel', 'Database', 'Text']
interval_values = ['1m', '2m', '5m', '15m', '30m', '1h', '90m', '1d', '5d', '1wk', '1mo', '3mo']
period_values = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'YTD', 'MAX']
tickers = get_tickers()
tickers.sort()

root = tk.Tk()
root.title('Stock Database')

excel_check = tk.BooleanVar()
xml_check = tk.BooleanVar()
text_check = tk.BooleanVar()

searchWindow = tk.PanedWindow(root)
searchWindow.grid(row=0, column=0, padx=10)
# searchWindow.configure(bg='white')
selectWindow = tk.PanedWindow(root)
selectWindow.grid(row=0, column=1, padx=10)
optionsWindow = tk.PanedWindow(root)
optionsWindow.grid(row=1, column=0, columnspan=2, pady=(10, 0))
exportWindow = tk.PanedWindow(root)
exportWindow.grid(row=2, column=0, columnspan=2, pady=20)

tickersSearch = tk.Entry(searchWindow, width=14)
tickersSearch.grid(row=0, column=0, padx=15, pady=(15, 0), ipady=5, sticky='W')
tickersAdd = ttk.Button(searchWindow, text='+', width=2, command=add_ticker)
tickersAdd.grid(row=0, column=0, padx=(120, 0), pady=(15, 0))
tickersSearchList = tk.Listbox(searchWindow)
for i in tickers :
    tickersSearchList.insert(tickers.index(i), i)
tickersSearchList.grid(row=1, column=0, padx=15, pady=(2, 15))
tickersSelectedList = tk.Listbox(selectWindow)
tickersSelectedList.grid(row=1, column=1, padx=15, pady=(2, 15))
selectedText = tk.Label(selectWindow, text='Selected')
selectedText.grid(row=0, column=1, padx=(25, 25), pady=(15, 2), sticky='W')
tickersRemove = ttk.Button(selectWindow, text='-', width=2, command=sub_ticker)
tickersRemove.grid(row=0, column=1, padx=(120, 0), pady=(15, 0))

intervalLabel = tk.Label(optionsWindow, text='Interval')
periodLabel = tk.Label(optionsWindow, text='Period')
startLabel = tk.Label(optionsWindow, text='Start')
endLabel = tk.Label(optionsWindow, text='End')
intervalLabel.grid(row=0, column=0, padx=(20, 30))
periodLabel.grid(row=0, column=1, padx=(10, 50))
startLabel.grid(row=0, column=2, padx=(20, 20))
endLabel.grid(row=0, column=3, padx=(20, 30))
intervalBox = ttk.Combobox(optionsWindow, value=interval_values, state='readonly', width=5)
periodBox = ttk.Combobox(optionsWindow, value=period_values, state='readonly', width=5)
intervalBox.bind('<<ComboboxSelected>>', lambda e: intervalBox.selection_clear())
periodBox.bind('<<ComboboxSelected>>', lambda e: periodBox.selection_clear())
startEntry = tk.Entry(optionsWindow, width=10)
endEntry = tk.Entry(optionsWindow, width=10)
intervalBox.grid(row=1, column=0)
periodBox.grid(row=1, column=1)
startEntry.grid(row=1, column=2)
endEntry.grid(row=1, column=3)


exportCheck = ttk.Checkbutton(exportWindow, text='Excel', variable=excel_check)
xmlCheck = ttk.Checkbutton(exportWindow, text='XML', variable=xml_check)
textCheck = ttk.Checkbutton(exportWindow, text='Text', variable=text_check)
exportButton = ttk.Button(exportWindow, text='Export', command=root.destroy)
progressBar = ttk.Progressbar(exportWindow, length=400)
exportCheck.grid(row=0, column=0)
xmlCheck.grid(row=0, column=1)
textCheck.grid(row=0, column=2)
exportButton.grid(row=0, column=3)
progressBar.grid(row=1, column=0, columnspan=4, pady=(20, 10))

sv_ttk.set_theme('dark')
root.mainloop()


# tickersCombo = tk.(root, value=get_tickers())
# outputButton = tk.Button(root, text='Select Outputs', width=15, command=get_output_types)
# outputList = tk.Listbox(root, listvariable=output_types, selectmode='multiple')
# for i in output_types :
#     outputList.insert(output_types.index(i), i)
# tickersCombo.grid(row=0, column=0)
# outputButton.grid(row=1, column=1)
# outputList.grid(row=0, column=1)

# conn = sqlite3.connect('tickers.db')
# c = conn.cursor()
#
# print(get_tickers())
# create_tables(conn, tickers[1])

# UNSAFE INPUT METHOD IF ACCEPTING USER INPUT (SEE : SQL INJECTION ATTACK) HOWEVER, SAFE FOR THIS PURPOSE
# for i in tickers['Symbol'].tolist() :
#     if (i.find('.') != -1) :
#         i = i.replace('.', '_')

    # data = yf.Ticker(i.replace('_','-')).history(period="1mo", interval="1d", actions=False, rounding=True)
    # data.drop(columns='Volume', inplace=True)
    # data.reset_index(inplace=True)
    # data['Date'] = data['Date'].dt.date
    # data.to_sql(i, conn, schema=None, if_exists='append', index=False)


