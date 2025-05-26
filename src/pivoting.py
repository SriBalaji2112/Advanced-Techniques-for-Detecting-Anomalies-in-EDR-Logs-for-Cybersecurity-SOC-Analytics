from src.importing import *
from widgets.Dialogs import MergeDialog
from widgets.Tables import update_table, create_table #, anomaly_table_creation
from src.query_filter import build
from widgets.Messages import MessageBox
from widgets.ContinueProgressBar import ContinousProgressBar

def save_draft(parent):
    new_pivoted_data = {}
    current_index = parent.tabs.currentIndex()
    current_sheet_name = parent.tabs.tabText(current_index)
    parent.pivoting_count += 1
    new_pivoted_data["pivoting"+str(parent.pivoting_count)] = {"df": parent.data[current_sheet_name]['df'],
                                                               "query": ''}

    # parent.update_table(current_sheet_name, parent.data[current_sheet_name])
    parent.data.update(new_pivoted_data.copy())
    parent.original_data.update(new_pivoted_data.copy())
    # parent.display_data(parent.data)

    create_table(parent, "pivoting"+str(parent.pivoting_count), parent.data[current_sheet_name]['df'], progress_lable="Saving Draft. This may take a moment, please wait...")

def open_merge_dialog(parent):
    current_sheet_names = list(parent.data.keys())
    dialog = MergeDialog(current_sheet_names, parent)
    dialog.exec_()

def remove_duplicates(parent):
    current_index = parent.tabs.currentIndex()
    current_sheet_name = parent.tabs.tabText(current_index)

    parent.data[current_sheet_name]['df'] = parent.data[current_sheet_name]['df'].drop_duplicates()
    update_table(parent, current_index, current_sheet_name, parent.data[current_sheet_name]['df'], progress_lable="Removing Duplicates. This may take a moment, please wait...")

def reset_filter(parent):
    current_index = parent.tabs.currentIndex()
    current_sheet_name = parent.tabs.tabText(current_index)
    # Reload the original data
    print(parent.original_data[current_sheet_name]['df'])
    print(parent.data[current_sheet_name]['df'])
    
    parent.data[current_sheet_name]['df'] = parent.original_data[current_sheet_name]['df'].copy()
    update_table(parent, current_index, current_sheet_name, parent.data[current_sheet_name]['df'], progress_lable="Resetting data. This may take a moment, please wait...")

def filter_text_input_on_change(parent, text):
    current_index = parent.tabs.currentIndex()
    current_sheet_name = parent.tabs.tabText(current_index)
    parent.data[current_sheet_name]['query'] = text

def apply_query(parent):
    
    filter_text = parent.filter_textbox.text()
    new_pivoted_data = {}

    current_index = parent.tabs.currentIndex()
    current_sheet_name = parent.tabs.tabText(current_index)

    if filter_text and parent.data:
        new_pivoted_data[current_sheet_name] = {}
        new_pivoted_data[current_sheet_name]['query'] = parent.data[current_sheet_name]['query']
        # parent.data[current_sheet_name]['df']['ProcessId'] = parent.data[current_sheet_name]['df']['ProcessId'].astype(str)
        # parent.data[current_sheet_name]['df']['ParentProcessId'] = parent.data[current_sheet_name]['df']['ParentProcessId'].astype(str)
        new_pivoted_data[current_sheet_name]['df'] = build(parent.data[current_sheet_name]['df'], parent.filter_textbox.text())
        # print()
        # print(new_pivoted_data[current_sheet_name]['df'])
        # print(type(new_pivoted_data[current_sheet_name]['df']))
        # if "Anomaly" in new_pivoted_data[current_sheet_name]['df'].columns:
        #     anomaly_table_creation(parent, current_sheet_name, new_pivoted_data[current_sheet_name]['df'])
        print(type(new_pivoted_data[current_sheet_name]['df']))
        print(new_pivoted_data[current_sheet_name]['df'])
        update_table(parent, current_index, current_sheet_name, data_dict=new_pivoted_data[current_sheet_name]['df'], progress_lable="Running your query. Just a moment...")
        parent.data.update(new_pivoted_data.copy())
    else:
        MessageBox.show_warning(parent, message="No filter text provided or no data available.")
    