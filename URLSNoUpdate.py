import pandas as pd
import os
import re


def update_script_from_excel(excel_file, script_folder):
    # Load the Excel file
    xls = pd.ExcelFile(excel_file)
    FilesNotFoundList=[]
    Successful=[]

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)

        # Ensure the necessary columns exist
        if 'FileName' not in df.columns or 'URLSNoList' not in df.columns:
            print(f"Skipping sheet '{sheet_name}' as it does not contain required columns.")
            continue

        for index, row in df.iterrows():
            script_filename = row['FileName']
            new_urlsno = row['URLSNoList']
            script_path = os.path.join(script_folder, f"{script_filename}.py")

            if os.path.exists(script_path):
                with open(script_path, 'r', encoding='utf-8') as file:
                    script_content = file.read()

                # Replace only the first occurrence of URLSNoList
                updated_content = re.sub(r'URLSNoList\s*=\s*\[.*?\]', f'URLSNoList = [{new_urlsno}]', script_content,
                                         count=1)

                with open(script_path, 'w', encoding='utf-8') as file:
                    file.write(updated_content)

                print(f"Updated {script_filename} in sheet '{sheet_name}' with URLSNo {new_urlsno}")
                Successful.append(str(script_filename))
            else:
                print(f"File {script_filename} not found in {script_folder}")
                FilesNotFoundList.append(str(script_filename))
    print(FilesNotFoundList)
    print(len(FilesNotFoundList))
    print(Successful)


# Example usage
excel_file = "C:\\Users\\Abdullah.Habeeb\\Documents\\250325PendingATS.xlsx"  # Update with your actual Excel file path
script_folder = ("")  # Folder where Python scripts are stored
update_script_from_excel(excel_file, script_folder)
