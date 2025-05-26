from src.importing import *

def init_tab():
    tabs = QTabWidget()
    tabs.setTabsClosable(True)
    tabs.setMovable(True)

    return tabs

def close_tab(parent, index):
    sheet_name = parent.tabs.tabText(index)  # Get the tab name
    parent.tabs.removeTab(index)  # Remove the tab
    if sheet_name in parent.data:
        del parent.data[sheet_name]  # Remove associated data
    # print(f"Closed sheet: {sheet_name}")

def on_tab_switched(parent, index):
    # Perform an action when the tab is switched
    sheet_name = parent.tabs.tabText(index)
    try:
        filter_text_box_text = parent.data[sheet_name]['query']
        parent.filter_textbox.setText(filter_text_box_text)
    except:
        pass
    # # You can access the widget of the current tab
    # current_widget = parent.tabs.currentWidget()
    # if current_widget:
    #     print(f"Current widget: {current_widget.text()}")