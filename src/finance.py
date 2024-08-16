import yfinance as yf
import pandas as pd
import tkinter as tk
from tkinter import ttk
import sqlite3
import sv_ttk

# MAKE THIS INTO A XML FILE ON FIRST CALL AND THEN REF IT AFTER
def get_tickers():
    tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    return tickers['Symbol'].convert_dtypes(convert_string=True).tolist()

def create_tables(db, input_tickers):
    for i in input_tickers['Symbol'].tolist() :
        data = yf.Ticker(i.replace('.','-')).history(
            period="1yr", interval="1d", actions=False, rounding=True)
        data.drop(columns='Volume', inplace=True)
        data.reset_index(inplace=True)
        data['Date'] = data['Date'].dt.date
        data.to_sql(i, conn, schema=None, if_exists='replace', index=False)

def get_output_types() :
    output = [outputList.get(i) for i in outputList.curselection()]
    return output

def filter_list(input_list, input_filter) :
    output_list = [x for x in input_list if x.startswith(input_filter)]
    update_listbox(output_list, tickersSearchList)

def add_tickers() :
    for i in tickersSearchList.curselection() :
        selected_tickers.add(tickersSearchList.get(i))
    update_listbox(selected_tickers, tickersSelectedList)
    tickersSearchList.selection_clear(0, tk.END)

def sub_tickers() :
    for i in tickersSelectedList.curselection() :
        selected_tickers.remove(tickersSelectedList.get(i))
    update_listbox(selected_tickers, tickersSelectedList)

def update_listbox(input_list, input_listbox) :
    input_listbox.delete(0, tk.END)
    for i in sorted(input_list) :
        input_listbox.insert(tk.END, i)

selected_tickers = set()
export_values = ['Excel', 'Database', 'Text']
interval_values = ['1m', '2m', '5m', '15m', '30m', '1h', '90m', '1d', '5d', '1wk', '1mo', '3mo']
period_values = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'YTD', 'MAX']

tickers = get_tickers()
tickers.sort()

root = tk.Tk()
root.title('Stock Database')

db_check = tk.BooleanVar()
xml_check = tk.BooleanVar()
text_check = tk.BooleanVar()

searchWindow = tk.PanedWindow(root)
selectWindow = tk.PanedWindow(root)
optionsWindow = tk.PanedWindow(root)
exportWindow = tk.PanedWindow(root)
searchWindow.grid(row=0, column=0, padx=10)
selectWindow.grid(row=0, column=1, padx=10)
optionsWindow.grid(row=1, column=0, columnspan=2, pady=(10, 0))
exportWindow.grid(row=2, column=0, columnspan=2, pady=20)

tickersSearch = ttk.Entry(searchWindow, width=14)
tickersAdd = ttk.Button(searchWindow, text='+', width=2, command=add_tickers)
tickersRemove = ttk.Button(selectWindow, text='-', width=2, command=sub_tickers)
selectedText = tk.Label(selectWindow, text='Selected')
tickersSearchList = tk.Listbox(searchWindow, selectmode='multiple')
tickersSelectedList = tk.Listbox(selectWindow, selectmode=tk.MULTIPLE)
tickersSearch.grid(row=0, column=0, padx=5, pady=(15, 0), sticky='W')
tickersAdd.grid(row=0, column=1, padx=(5, 0), pady=(15, 0))
tickersSearchList.grid(row=1, column=0, columnspan=2, padx=15, pady=(2, 15))
tickersSelectedList.grid(row=1, column=1, padx=15, pady=(2, 15))
selectedText.grid(row=0, column=1, padx=(25, 25), pady=(15, 2), sticky='W')
tickersRemove.grid(row=0, column=1, padx=(120, 0), pady=(15, 0))
tickersSearch.bind('<KeyRelease>', lambda f: filter_list(tickers, tickersSearch.get().upper()))
# tickersSearch.bind('<KeyRelease>', lambda f: print('TESTING'))
for i in tickers :
    tickersSearchList.insert(tickers.index(i), i)

intervalLabel = ttk.Label(optionsWindow, text='Interval')
periodLabel = ttk.Label(optionsWindow, text='Period')
startLabel = ttk.Label(optionsWindow, text='Start')
endLabel = ttk.Label(optionsWindow, text='End')
intervalBox = ttk.Combobox(optionsWindow, value=interval_values, state='readonly', width=5)
periodBox = ttk.Combobox(optionsWindow, value=period_values, state='readonly', width=5)
startEntry = tk.Entry(optionsWindow, width=10, text='YYYY-MM-DD')
endEntry = tk.Entry(optionsWindow, width=10, text='YYYY-MM-DD')
intervalLabel.grid(row=0, column=0, padx=(20, 30))
periodLabel.grid(row=0, column=1, padx=(10, 50))
startLabel.grid(row=0, column=2, padx=(20, 20))
endLabel.grid(row=0, column=3, padx=(20, 30))
intervalBox.grid(row=1, column=0)
periodBox.grid(row=1, column=1)
startEntry.grid(row=1, column=2)
endEntry.grid(row=1, column=3)
intervalBox.bind('<<ComboboxSelected>>', lambda e: intervalBox.selection_clear())
periodBox.bind('<<ComboboxSelected>>', lambda e: periodBox.selection_clear())
startEntry.bind('<KeyRelease>', )
endEntry.bind('<KeyRelease>', )


exportCheck = ttk.Checkbutton(exportWindow, text='DataBase', variable=db_check)
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


