from PyQt5.QtGui import QColor
# from importing import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QProgressDialog
from PyQt5.QtCore import Qt
from widgets.Tables import update_table, create_table #, anomaly_table_creation
from widgets.ContinueProgressBar import ContinousProgressBar

def start_anomaly_detection(parent):
    # progress = QProgressDialog("Processing anomaly detection...", None, 0, 0, parent)
    # progress.setWindowModality(Qt.WindowModal)
    # progress.setMinimumDuration(0)
    progress = ContinousProgressBar("Take some time, Anomaly Detecting...", parent=parent)
    progress.show()

    current_index = parent.tabs.currentIndex()
    current_sheet_name = parent.tabs.tabText(current_index)

    if current_sheet_name:
        data = parent.data[current_sheet_name]["df"].copy()
    else:
        print("No log data found, please open a log file.")

    parent.thread = AnomalyDetectionThread(data)
    parent.thread.finished.connect(progress.close)
    parent.thread.finished.connect(lambda: print("Anomaly detection complete!"))
    parent.thread.anomaly_detected.connect(lambda data: display_anomalies(parent, data, current_sheet_name))
    parent.thread.start()

def display_anomalies(parent, data, current_sheet_name):
    anomaly_new_data = {}
    parent.pivoting_count += 1
    anomaly_new_data["Anomaly_"+current_sheet_name] = {"df": data,
                                                               "query": ''}

    # parent.update_table(current_sheet_name, parent.data[current_sheet_name])
    parent.data.update(anomaly_new_data.copy())
    parent.original_data.update(anomaly_new_data.copy())
    print(data)

    # anomaly_table = AnomalyTableCreation(parent, "Anomaly_"+current_sheet_name, parent.data["Anomaly_"+current_sheet_name]['df'])
    # anomaly_table_creation(parent, "Anomaly_"+current_sheet_name, parent.data["Anomaly_"+current_sheet_name]['df'])
    create_table(parent, "Anomaly_"+current_sheet_name, parent.data["Anomaly_"+current_sheet_name]['df'])
    # anomaly_table.start()

class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processing Anomalies")
        self.setModal(True)
        layout = QVBoxLayout()

        self.label = QLabel("Detecting anomalies, please wait...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)

        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

from PyQt5.QtCore import QThread, pyqtSignal
from sklearn.ensemble import IsolationForest
import pandas as pd

def IsolationForestAlgorithm(data):
    import numpy as np
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.ensemble import IsolationForest
    from sklearn.feature_selection import SelectKBest, f_classif
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import confusion_matrix, classification_report

    # print(data)

    data.fillna(value=0, inplace=True)

    # Copy original data for reference
    original_data = data.copy()

    # Encode categorical features
    categorical_columns = ['Process Name', 'Command Line', 'Account Name', 'Parent Process Name', 'Executable Path', 
                            'Parent Command Line', 'Process Status', 'SHA1', 'Process Integrity Level']
    encoder_mappings = {}

    for col in categorical_columns:
        if col in data.columns:
            encoder = LabelEncoder()
            data[col] = encoder.fit_transform(data[col].astype(str))
            encoder_mappings[col] = dict(zip(encoder.classes_, range(len(encoder.classes_))))  # Store mapping

    # Convert timestamps to UNIX format (seconds since epoch)
    timestamp_columns = ['Event Time', 'Creation Time']
    for col in timestamp_columns:
        if col in data.columns:
            data[col] = pd.to_datetime(data[col], errors='coerce').astype('int64') // 10**9
            data[col] = data[col].fillna(0)

    # Convert IP addresses to numeric representation
    def ip_to_numeric(ip):
        try:
            if isinstance(ip, str):
                if ':' in ip:  # IPv6
                    return int(ip.replace(':', ''), 16)
                elif '.' in ip:  # IPv4
                    return sum(int(octet) * (256 ** i) for i, octet in enumerate(reversed(ip.split('.'))))
        except:
            return 0
        return 0

    data['Remote IP'] = data['Remote IP'].astype(str).apply(ip_to_numeric)
    data['Local IP'] = data['Local IP'].astype(str).apply(ip_to_numeric)

    # Scale numerical features
    scaler = StandardScaler()
    numerical_columns = ['Event Time', 'Creation Time', 'Remote IP', 'Remote Port', 'Local IP', 'Local Port',
                        'Read Count', 'Write Count', 'Process Integrity Level']

    for col in numerical_columns:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)

    # Ensure only valid columns are scaled
    valid_numerical_columns = [col for col in numerical_columns if col in data.columns]
    data[valid_numerical_columns] = scaler.fit_transform(data[valid_numerical_columns])

    # data[numerical_columns] = scaler.fit_transform(data[numerical_columns])

    # Feature Selection
    X = data.copy()
    X_numerical = X.select_dtypes(include=[np.number])

    # Select top features
    selector = SelectKBest(score_func=f_classif, k=min(10, X_numerical.shape[1]))
    X_selected = selector.fit_transform(X_numerical.replace([np.inf, -np.inf], np.nan).dropna(), np.ones(X_numerical.shape[0]))
    selected_feature_names = np.array(X_numerical.columns)[selector.get_support()]

    # Split dataset into training & testing sets (80% train, 20% test)
    X_train, X_test = train_test_split(X_numerical[selected_feature_names], test_size=0.2, random_state=42)

    # Isolation Forest Model
    # model = IsolationForest(
    #     n_estimators=100, 
    #     contamination=0.05, 
    #     max_samples=0.8, 
    #     max_features=0.8, 
    #     random_state=42
    # )
    model = IsolationForest(n_estimators=100, contamination=0.08, max_samples=0.8, max_features=0.8, random_state=42)

    model.fit(X_train)

    # Predict anomalies
    data['Anomaly'] = model.predict(X_selected)
    data['Anomaly Score'] = model.decision_function(X_selected)

    # threshold = np.percentile(data['Anomaly Score'], 95)  # Reduce from 98 to 95
    # data['Anomaly'] = data['Anomaly Score'].apply(lambda x: -1 if x < threshold else 1)

    # Identify anomaly reasons
    def get_anomaly_reason(row, normal_mean, normal_std):
        reasons = []
        for feature in selected_feature_names:
            value = row[feature]
            mean = normal_mean[feature]
            std_dev = normal_std[feature]
            if abs(value - mean) > 2 * std_dev:  # Significant deviation
                reasons.append(f"{feature} unusual (Value: {value:.2f}, Mean: {mean:.2f})")
        return "; ".join(reasons) if reasons else "Normal behavior"

    # Calculate normal feature statistics
    normal_data = data[data['Anomaly'] == 1]
    normal_mean = normal_data[selected_feature_names].mean()
    normal_std = normal_data[selected_feature_names].std()

    # Apply function to identify anomaly reasons
    data['AnomalyReason'] = data.apply(lambda row: get_anomaly_reason(row, normal_mean, normal_std), axis=1)

    # ✅ Fix: Align Anomaly Labels with Detected Anomaly Reasons
    data['Anomaly'] = data.apply(lambda row: -1 if row['AnomalyReason'] != "Normal behavior" else row['Anomaly'], axis=1)

    for col, mapping in encoder_mappings.items():
        inverse_mapping = {v: k for k, v in mapping.items()}
        data[col] = data[col].map(inverse_mapping)
        
    return data

class AnomalyDetectionThread(QThread):
    progress = pyqtSignal(int)
    anomaly_detected = pyqtSignal(pd.DataFrame)
    finished = pyqtSignal(int)

    def __init__(self, data):
        super().__init__()
        self.df = data

    def run(self):
        self.progress.emit(100)
        self.df = IsolationForestAlgorithm(self.df)
        self.anomaly_detected.emit(self.df)
        self.finished.emit(1)
