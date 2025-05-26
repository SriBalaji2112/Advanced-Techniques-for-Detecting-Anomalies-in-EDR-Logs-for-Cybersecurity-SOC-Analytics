"""
System Process and Network Monitor Script

This script monitors running processes and their network activities on a Windows system.
It collects detailed information like CPU usage, memory usage, file hashes, connections, and more.
The information is logged periodically into a CSV file stored under the user's Documents/logs folder.
Administrator privileges are required to access full process details.
"""

import os
import sys
import csv
import time
import ctypes
import hashlib
import psutil
from datetime import datetime
from plyer import notification

count = 0
logs = []

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def hash_file(file_path):
    try:
        sha1 = hashlib.sha1()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha1.update(chunk)
        return sha1.hexdigest()
    except:
        return None

def collect_logs():
    global count
    log_data = []

    for proc in psutil.process_iter(['pid', 'ppid', 'name']):
        try:
            p = psutil.Process(proc.info['pid'])
            parent = psutil.Process(proc.info['ppid']) if proc.info['ppid'] else None

            exe_path = None
            try: exe_path = p.exe()
            except: pass

            io_counters = p.io_counters() if hasattr(p, "io_counters") else None
            memory_info = p.memory_info() if hasattr(p, "memory_info") else None
            cpu_percent = p.cpu_percent(interval=0.1)

            proc_info = {
                "Event Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Process Id": p.pid,
                "Process Name": p.name(),
                "Command Line": ' '.join(p.cmdline()) if p.cmdline() else None,
                "Creation Time": datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M:%S"),
                "Account Name": p.username(),
                "Parent Process Id": p.ppid(),
                "Parent Process Name": parent.name() if parent else None,
                "Parent Command Line": ' '.join(parent.cmdline()) if parent else None,
                "Process Status": p.status(),
                "Process Integrity Level": "Normal" if p.status() in ['running', 'sleeping'] else "Critical",
                "Executable Path": exe_path,
                "SHA1": hash_file(exe_path) if exe_path else None,
                "Read Count": io_counters.read_count if io_counters else 0,
                "Write Count": io_counters.write_count if io_counters else 0,
                "CPU Usage (%)": cpu_percent,
                "Memory Usage (MB)": memory_info.rss / (1024 * 1024) if memory_info else 0,
                "Network Sent (MB)": io_counters.write_bytes / (1024 * 1024) if io_counters else 0,
                "Network Received (MB)": io_counters.read_bytes / (1024 * 1024) if io_counters else 0
            }

            # Add connection info
            connections = p.net_connections(kind='inet')
            if connections:
                for conn in connections:
                    log_entry = proc_info.copy()
                    log_entry.update({
                        "Remote IP": conn.raddr.ip if conn.raddr else None,
                        "Remote Port": conn.raddr.port if conn.raddr else None,
                        "Local IP": conn.laddr.ip if conn.laddr else None,
                        "Local Port": conn.laddr.port if conn.laddr else None
                    })
                    log_data.append(log_entry)
                    count += 1
            else:
                proc_info.update({
                    "Remote IP": None,
                    "Remote Port": None,
                    "Local IP": None,
                    "Local Port": None
                })
                log_data.append(proc_info)
                count += 1

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return log_data

def monitor_system_logs(output_file, interval=5):
    global logs
    fieldnames = [
        "Event Time", "Process Id", "Process Name", "Command Line", "Creation Time", "Account Name",
        "Parent Process Id", "Parent Process Name", "Parent Command Line", "Remote IP", "Remote Port",
        "Local IP", "Local Port", "Process Status", "Process Integrity Level", "Executable Path",
        "SHA1", "Read Count", "Write Count", "CPU Usage (%)", "Memory Usage (MB)",
        "Network Sent (MB)", "Network Received (MB)"
    ]
    try:
        if not os.path.exists(output_file):
            with open(output_file, mode='w', newline='', encoding='utf-8', errors='replace') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
        while True:
            logs = collect_logs()
            if logs:
                with open(output_file, mode='a', newline='', encoding='utf-8', errors='replace') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerows(logs)
                print(f"✅ Logs saved to: {output_file} — [{datetime.now().strftime('%H:%M:%S')}]")
                logs = []
            time.sleep(interval)
    except KeyboardInterrupt:
        print("🛑 Monitoring stopped by user.")
    except Exception as E:
        notification.notify(
            title="Error in Log Monitor",
            message=str(E),
            app_name="Cyrus",
            timeout=5
        )

def run_as_admin():
    if not is_admin():
        script = sys.executable
        params = ' '.join([f'"{arg}"' for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", script, params, None, 1)
        sys.exit()

if __name__ == "__main__":
    run_as_admin()
    print("🚀 Script running with admin privileges.")
    notification.notify(
        title="Log Monitor Started",
        message="System monitoring has started.",
        app_name="Cyrus",
        timeout=5
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    documents_dir = os.path.join(os.environ["USERPROFILE"], "Documents")
    logs_dir = os.path.join(documents_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    output_file = f"{logs_dir}/logs_{timestamp}.csv"

    monitor_system_logs(output_file, interval=5)
