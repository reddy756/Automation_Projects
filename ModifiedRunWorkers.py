import os
import subprocess
import time
import traceback
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

class RunThreads:
    def __init__(self, folderpath: str, prefixes: list, threads=4, timeout=600):
        self.threads = threads
        self.folderpath = os.path.normpath(folderpath)
        self.lock = threading.Lock()
        self.timeout = timeout  # Timeout in seconds
        self.prefixes = prefixes  # List of prefixes to filter files

    def triggerCompaniesByFilePath(self, filepath):
        """Function to execute a Python file."""
        try:
            start_time = time.time()
            result = subprocess.run(
                ['python', filepath],
                capture_output=False,
                text=True,
                check=True,
                shell=False
            )
            end_time = time.time()
            elapsed_time = (end_time - start_time) / 60
            return True, {f"Subprocess Success for file {os.path.basename(filepath)}"}
        except Exception as e:
            return False, {str(e) or 'No error message captured'}

    def run(self):
        execution_summary = []
        processed_files = set()
        missing_files = []  # To track files not found
        folderpath = self.folderpath
        files = [os.path.join(folderpath, file) for file in os.listdir(folderpath) 
                 if file.endswith(".py") and any(file.startswith(prefix) for prefix in self.prefixes)]
        
        # Collect missing files
        for prefix in self.prefixes:
            matching_files = [file for file in os.listdir(folderpath) if file.startswith(prefix) and file.endswith(".py")]
            if not matching_files:
                missing_files.append(f"No files found starting with '{prefix}'")

        if files:
            with ThreadPoolExecutor(max_workers=self.threads) as pool:
                futures = {pool.submit(self.triggerCompaniesByFilePath, file): file for file in files}
            for future in futures:
                file = futures[future]
                try:
                    file_summary = {}
                    with self.lock:
                        if file in processed_files:
                            continue
                    time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    file_summary["FileName"] = os.path.basename(file)
                    file_summary["StartTime"] = time_stamp
                    try:
                        success, output = future.result(timeout=self.timeout)
                    except Exception as e:
                        success, output = False, f"Future Exception: {str(e)}"
                    if not success:
                        file_summary["Status"] = "Failed"
                        file_summary["SubprocessError"] = output
                        execution_summary.append(file_summary)
                        continue

                    file_summary["Status"] = "Success"
                    end_time = time.time()
                    execution_time = (end_time - time.time()) / 60
                    with self.lock:
                        processed_files.add(file)
                    execution_summary.append(file_summary)
                except Exception as e:
                    error_details = {
                        "Thread Status": "Thread Failed",
                        "ErrorType": type(e).__name__,
                        "ErrorMessage": str(e),
                        "FileName": os.path.basename(file),
                        "StackTrace": traceback.format_exc()
                    }
                    file_summary.update(error_details)
                    execution_summary.append(file_summary)

        failed_files = [(status["FileName"], status) for status in execution_summary if status["Status"] != "Success"]
        for file, error in failed_files:
            print(f"Execution Failed for {file}, {error}")

        # Print missing files
        for missing in missing_files:
            print(missing)
        print('Missing Files-------->',missing_files)
        return execution_summary

# Example usage
prefixes = ['1420422','1450368','1485329','1652375','2272555_1448437','2272555_1448438','3195776','3297900','4560223','5348304','5429405','5500315']  # Replace with your actual prefixes
A = RunThreads('C:\\Users\\Abdullah.Habeeb\\OneDrive - GlobalData PLC\\Desktop\\jobsgenericwebcrawlerapp\\09_04_2025', prefixes)
exec_summary = A.run()
success_files = [status["FileName"] for status in exec_summary if status["Status"] == "Success"]
failed_files = [(status["FileName"], status) for status in exec_summary if status["Status"] != "Success"]

print(success_files, failed_files)
