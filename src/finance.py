import yfinance as yf
import pandas as pd
import tkinter as tk
import os
from tkinter import ttk
import sqlite3
import sv_ttk

#  INFO: CREATES AN EXCEL FILE CONTAINING SP500 TICKERS ON FIRST CALL THEN REFS IT FOR FOLLOWING CALLS
def get_tickers():
    try:
        with open('tickers.csv', 'rb') as file :
            tickers = pd.read_csv(file, index_col=0)
            file.close()

    except FileNotFoundError:
        tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        tickers['Symbol'].to_csv('tickers.csv')

    return tickers['Symbol'].convert_dtypes(convert_string=True).tolist()


#  INFO: GENERAL GUI FUNCTIONS

def filter_list(input_list, input_filter) :
    drop_calc_list = [x for x in input_list if x.startswith(input_filter)] #  FIX: DROP CALC LIST HARD CODED
    update_listbox(drop_calc_list, tickers_search_tree)

def add_tickers() :
    for each in tickers_search_tree.selection() :
        selected_tickers.add(str(tickers_search_tree.item(each)['text']))
    update_listbox(selected_tickers, tickers_selected_tree)
    tickers_search_tree.selection_remove(*tickers_search_tree.selection())

def sub_tickers() :
    for each in tickers_selected_tree.selection() :
        selected_tickers.remove(str(tickers_selected_tree.item(each)['text']))
    update_listbox(selected_tickers, tickers_selected_tree)

def update_listbox(input_list, input_listbox) :     #  FIX: NO LONGER USING LIST BOXES 
    input_listbox.delete(*input_listbox.get_children())
    for i in sorted(input_list) :
        input_listbox.insert('', 'end', text=i)
    input_listbox.update()

def entry_default_text(input_strvar, input_text) :
    if (input_strvar.get() == '') :
        input_strvar.set(input_text)
    elif (input_strvar.get() == input_text) :
        input_strvar.set('')

def toggle_recovery() :         #  FIX: Probably unnecessary 
    if (recovery_check.get() == True) :
        recovery_spinbox.config(state=tk.NORMAL)
    else :
        recovery_spinbox.config(state=tk.DISABLED)

def filter_periodbox() :        #  FIX: Should utilize filter function
    if (interval_combobox.get() == '1m') :
        period_combobox.set('')
        period_combobox['values'] = ['1d']
    elif (interval_combobox.get() == '1h') :
        period_combobox.set('')
        period_combobox['values'] = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y']
    elif (interval_combobox.get() in ['2m', '5m', '15m', '30m', '90m']) :
        period_combobox.set('')
        period_combobox['values'] = ['1d', '5d', '1mo']
    else :
        period_combobox['values'] = period_values

#  INFO: CALCULATION CONTROLLER
def run_calculations(input_dataframe) :
    calc_choice = calculation_combobox.get()        #  HACK: Currently only accepts 1 calculation selection
    if (calc_choice == 'Consecutive Drop %') :
        cumulative_drop_calc(input_dataframe)

def find_drops(input_dataframe, input_min_drop = 0) -> dict :
    try :
        drop_check = pd.Series(input_dataframe['Close'].diff().lt(input_min_drop).to_list())
        drop_length = pd.Series(drop_check.groupby((~drop_check).cumsum()).cumsum().to_list())
        drop_list = drop_length.diff().le(-3)
        output_dict = dict()
        for i in range(len(drop_list)) :
            if drop_list[i] == True :
                output_dict.update({i : int(drop_length[i-1])})
        return output_dict
   except KeyError :
        print('Error getting data from ticker info during drop calculation')

def recovery_calc() :               #  FIX: THIS DOES NOT WORK AT ALL
    recovery_list = list()
    for i in [x for x in calc['drop_list_index'] if x == x] :     #  NOTE: (if x==x) : removes NaN values
        start_value = input_dataframe.iat[int(i) - 3, 4]    #  WARN: input_dataframe[column 4] hardcoded and assumed to be 'CLOSE'
        recovery_goal = start_value * (float(recovery_spinbox.get()) / 100.0)

        if (int(i) != len(input_dataframe.index) - 1) :         #  NOTE: Catch edge case of drop index being at last index
            recovery_index = input_dataframe.iloc[int(i)+1:, 4].cummax().ge(recovery_goal).idxmax()  
        else :
            recovery_index = int(i - 1)

        if (input_dataframe.iat[recovery_index, 4] >= recovery_goal) :  #  WARN: input_dataframe[column 4] hardcoded and assumed to be 'CLOSE'
            recovery_list.append(str(input_dataframe.iat[recovery_index, 0]))
        else :
            recovery_list.append('NO RECOVERY FOUND')

    input_dataframe['Recovery'] = pd.Series(recovery_list)

#  INFO: CUMULATIVE DROP CALCULATION
def cumulative_drop_calc(input_dataframe) :         #  FIX: WAY TOO MANY THINGS IN ONE FUNCTION

    find_drops(input_dataframe)
    # calc = pd.DataFrame(columns=['is_lt', 'cumul_sum', 'drop_list_index', 'diff'])
    # calc['is_lt'] = input_dataframe['Close'].diff().lt(0)           #  WARN: .lt(0) : detects any downward change in price with no minimum req
    # dif_check = calc['is_lt'].cumsum().where(calc['is_lt'], 0).eq(0)
    # calc['cumul_sum'] = dif_check.groupby(dif_check.cumsum()).cumcount()
    # calc['drop_list_index'] = pd.Series(calc.loc[calc['cumul_sum'] == 3].index)  #  FIX: 3 is hard coded for third consecutive drop, also ignores further drops
    #
    # diff_list = list()
    # for i in [x for x in calc['drop_list_index'] if x == x] :         #  NOTE: (if x==x) : removes NaN values
    #     diff_list.append(1 - (1 / pow(input_dataframe.at[i-3, 'Close'] / input_dataframe.at[i, 'Close'], 1/3)))
    # calc['diff'] = pd.Series(data=diff_list)
    #
    # drop_calc_list = list()
    # for i in range(len(diff_list)) :
    #     drop_datetime = str(input_dataframe.loc[calc.at[i, 'drop_list_index']].iat[0])
    #     if interval_combobox.get() in ['1d', '5d', '1wk', '1mo', '3mo'] :
    #         drop_datetime = drop_datetime[:drop_datetime.rfind(' 00:00:00')]        #  NOTE: strips unnecessary time info if [period >= 1d]
    #     drop_amount = calc.at[i, 'diff'].round(5)
    #     drop_calc_list.append(str(drop_datetime) + ' / ' + str(drop_amount))
    #
    # input_dataframe['Cumulative Drop %'] = pd.Series(drop_calc_list)
    #
    # #  INFO: OPTIONAL RECOVERY CALCULATION
    # if (recovery_check.get() == True) :
    #     recovery_calc(

def get_ticker(input_ticker_name) :
    try :
        if (start_entry.get() == 'YYYY-MM-DD' and end_entry.get() == 'YYYY-MM-DD') :
            data = yf.Ticker(input_ticker_name.replace('.','-')).history(  #  NOTE: input_name.replace('.','-') : YFinance uses - instead of . in ticker name
                         interval=interval_combobox.get(), period=period_combobox.get(), actions=False, rounding=True)
        elif (start_entry.get() != '' and end_entry.get() != '') :
            data = yf.Ticker(input_ticker_name.replace('.','-')).history(
                        interval=interval_combobox.get(), start=start_entry.get(), end=end_entry.get(), actions=False, rounding=True)
        data.drop(columns='Volume', inplace=True)
        data.reset_index(inplace=True)
        data[data.columns[0]] = data[data.columns[0]].dt.tz_localize(None)  #  NOTE: tz_localize(None) : removes unnecessary timezone information
    except AttributeError : 
        print(i + " did'nt work!")

    return data

def export_database(input_ticker) :
    #  INFO: SQLite INIT
    conn = sqlite3.connect('output.db')
    cursor = conn.cursor()

    input_ticker.to_sql(i, conn, schema=None, if_exists='replace', index=False)

def export_excel(input_ticker) :
    excel_writer = pd.ExcelWriter('output.xlsx')
    input_ticker.to_excel(excel_writer, sheet_name=i, index=False)
    excel_writer.close()

def export_text(input_ticker) :
    try :
        os.remove('output.txt')
    except OSError :
        pass

    with open('output.txt', 'a') as f:
        print(i + '\n' + input_ticker.to_string() + '\n', file=f)

#  INFO: FILE EXPORTING
def export_output() :
    export_progressbar.configure(maximum=(len(selected_tickers) + 0.01))
    export_progressbar['value'] = 0

    #  INFO: TICKER INFO REQUEST
    for i in sorted(selected_tickers) :
        ticker_info = get_ticker(i)
        print(ticker_info)
        run_calculations(ticker_info)

        export_progressbar.step(1)
        root.update_idletasks()

        #  INFO: EXPORT FILE TYPE CHECKS
        if (db_check.get() == True) :
            export_database(ticker_info)

        if(xlsx_check.get() == True) :
            export_excel(ticker_info)

        if (text_check.get() == True) :
            export_text(ticker_info)


#  INFO: YFINANCE PREDEFINED VALUES
selected_tickers = set()
interval_values = ['1m', '2m', '5m', '15m', '30m', '1h', '90m', '1d', '5d', '1wk', '1mo', '3mo']
period_values = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'YTD', 'MAX']
calculation_values = ['Consecutive Drop %']

#  INFO: TICKER INFO REQUEST
tickers = get_tickers()
tickers.sort()

#  INFO: GUI ROOT INIT
root = tk.Tk()
root.title('Stock Database')
root.geometry('600x650')
sv_ttk.set_theme('dark')

#  INFO: GUI Variable INIT
search_text = tk.StringVar()
start_value = tk.StringVar()
end_value = tk.StringVar()
recovery_value = tk.IntVar()
db_check = tk.BooleanVar()
xlsx_check = tk.BooleanVar()
text_check = tk.BooleanVar()
recovery_check = tk.BooleanVar()
search_text.set('Search tickers')
start_value.set('YYYY-MM-DD')
end_value.set('YYYY-MM-DD')
recovery_value.set(100.0)

#  INFO: GUI : Frames
selection_frame = ttk.Frame(root)
options_frame = ttk.Frame(root)
calculation_frame = ttk.Frame(root)
export_frame = ttk.Frame(root)
selection_frame.grid(row=0, column=0, padx=10, pady=(15,0))
options_frame.grid(row=1, column=0, pady=(30, 0))
calculation_frame.grid(row=2, column=0, pady=30)
export_frame.grid(row=3, column=0, pady=30)

#  INFO: GUI : Ticker search and selection
tickers_search_entry = ttk.Entry(selection_frame, textvariable=search_text, width=15)
tickers_add_button = ttk.Button(selection_frame, text='->', width=2, command=add_tickers)
tickers_remove_button = ttk.Button(selection_frame, text='<-', width=2, command=sub_tickers)
selected_text_label = ttk.Label(selection_frame, text='Selected')
tickers_search_tree = ttk.Treeview(selection_frame, selectmode='extended', show='tree')
tickers_selected_tree = ttk.Treeview(selection_frame, selectmode='extended', show='tree')
tickers_scrollbar = ttk.Scrollbar(selection_frame, orient='vertical')
tickers_search_entry.grid(row=0, column=0, padx=(35,0), pady=5)
tickers_search_tree.grid(row=1, column=0, columnspan=2, padx=(15, 45))
tickers_scrollbar.grid(row=1, column=1, sticky='ns', padx=(20, 0))
tickers_selected_tree.grid(row=1, column=2, columnspan=2, padx=(15, 15))
selected_text_label.grid(row=0, column=2, rowspan=2, sticky='wn', padx=(30,0), pady=(32,0))
selected_text_label.lift()
tickers_add_button.grid(row=1, column=1, padx=(100, 0), pady=(0,90))
tickers_remove_button.grid(row=1, column=1, padx=(100, 0), pady=(90,0))
tickers_search_entry.bind('<FocusIn>', lambda f: entry_default_text(search_text, 'Search tickers'))
tickers_search_entry.bind('<FocusOut>', lambda f: entry_default_text(search_text, 'Search tickers'))
tickers_search_entry.bind('<KeyRelease>', lambda f: filter_list(tickers, tickers_search_entry.get().upper()))
for i in tickers :      #  NOTE: Ticker search list insertion
    tickers_search_tree.insert('', 'end', text=i)
tickers_scrollbar.config(command=tickers_search_tree.yview)
tickers_search_tree.config(yscrollcommand=tickers_scrollbar.set)

#  INFO: GUI : YFinance Interval and Period selection
interval_label = ttk.Label(options_frame, text='Interval')
period_label = ttk.Label(options_frame, text='Period')
start_label = ttk.Label(options_frame, text='Start')
end_label = ttk.Label(options_frame, text='End')
interval_combobox = ttk.Combobox(options_frame, value=interval_values, state='readonly', width=5)
period_combobox = ttk.Combobox(options_frame, value=period_values, state='readonly', width=5)
start_entry = ttk.Entry(options_frame, width=12, textvariable=start_value)
end_entry = ttk.Entry(options_frame, width=12, textvariable=end_value)
interval_label.grid(row=0, column=0, padx=(5, 20))
period_label.grid(row=0, column=1, padx=(0, 60))
start_label.grid(row=0, column=2, padx=(35, 20))
end_label.grid(row=1, column=2, padx=(35, 20))
interval_combobox.grid(row=1, column=0, padx=(5,20))
period_combobox.grid(row=1, column=1, padx=(0,60))
start_entry.grid(row=0, column=3)
end_entry.grid(row=1, column=3)
interval_combobox.bind('<<ComboboxSelected>>', lambda e: (interval_combobox.selection_clear(), filter_periodbox()))
period_combobox.bind('<<ComboboxSelected>>', lambda e: period_combobox.selection_clear())
start_entry.bind('<FocusIn>', lambda f: entry_default_text(start_value, 'YYYY-MM-DD'))
end_entry.bind('<FocusIn>', lambda f: entry_default_text(end_value, 'YYYY-MM-DD'))
start_entry.bind('<FocusOut>', lambda f: entry_default_text(start_value, 'YYYY-MM-DD'))
end_entry.bind('<FocusOut>', lambda f: entry_default_text(end_value, 'YYYY-MM-DD'))

#  INFO: GUI : Calculation selection and options
calculation_label = ttk.Label(calculation_frame, text='Calculation')
calculation_combobox = ttk.Combobox(calculation_frame, value=calculation_values, state='readonly', width=18)
recovery_checkbutton = ttk.Checkbutton(calculation_frame, text='Recovery', variable=recovery_check, command=toggle_recovery)
recovery_spinbox = ttk.Spinbox(calculation_frame, from_=1.0, to=200.0, state='readonly', textvariable=recovery_value, width=10,
                                command= lambda : recovery_spinbox.selection_clear())
calculation_label.grid(row=0, column=0, padx=(5,45))
calculation_combobox.grid(row=1, column=0, padx=(5,45))
recovery_checkbutton.grid(row=0, column=1, padx=(65,0))
recovery_spinbox.grid(row=1, column=1, padx=(65,0))
calculation_combobox.bind('<<ComboboxSelected>>', lambda e: calculation_combobox.selection_clear())

#  INFO: GUI : Export selection
database_checkbutton = ttk.Checkbutton(export_frame, text='DATABASE', variable=db_check)
xlsx_checkbutton = ttk.Checkbutton(export_frame, text='EXCEL', variable=xlsx_check)
text_checkbutton = ttk.Checkbutton(export_frame, text='TEXT', variable=text_check)
export_button = ttk.Button(export_frame, text='Export', command=export_output)
export_progressbar = ttk.Progressbar(export_frame, length=400, mode='determinate')
database_checkbutton.grid(row=0, column=0)
xlsx_checkbutton.grid(row=0, column=1)
text_checkbutton.grid(row=0, column=2)
export_button.grid(row=0, column=3)
export_progressbar.grid(row=1, column=0, columnspan=4, pady=(20, 10))


#  INFO: GUI : MAIN EVENT LOOP
root.mainloop()
