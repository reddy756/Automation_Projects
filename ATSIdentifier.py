import sys

import pandas as pd
import pyodbc

# === CONFIGURATION ===

input_path = ''      # 📥 Input Excel file
output_path = './CDMSID_Output.xlsx'    # 📤 Output Excel file
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=;"
    "DATABASE="
    "UID="
    "PWD="
)
# === LOAD INPUT EXCEL ===
df_input = pd.read_excel(input_path)

# Add empty columns for output
df_input['FileName'] = None
df_input['jobUrl'] = None

# Collect missing/error records
missing_records = []

def get_table_from_file_location(file_location: str) -> str:
    """Extract the actual date string from 'File Location'."""
    if '/' in file_location:
        return file_location.split('/')[-1].strip()
    return file_location.strip()

try:
    print("🔌 Connecting to database...")
    conn = pyodbc.connect(
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=;'  # <<-- Replace with your SQL Server name
        r'DATABASE='  # <<-- Replace with your DB name
        r'UID='  # <<-- Replace with your SQL Server username
        r'PWD='
    )
    print('Connected to DB')

    for index, row in df_input.iterrows():
        raw_date = str(row['File Location'])
        cdmsid = row['CDMSID']

        date_str = get_table_from_file_location(raw_date)
        table_name = f"LUTemp_{date_str.replace('_', '')}"

        query = f"""
            SELECT COALESCE(FileName, CAST(CDMSID AS VARCHAR)) AS FileName, jobUrl
            FROM {table_name}
            WHERE CDMSID = ?
        """

        try:
            result = pd.read_sql(query, conn, params=[cdmsid])

            if not result.empty:
                df_input.at[index, 'FileName'] = result.loc[0, 'FileName']
                df_input.at[index, 'jobUrl'] = result.loc[0, 'jobUrl']
                print(f"✅ Found: CDMSID {cdmsid} in {table_name}")
            else:
                print(f"⚠️ Not found: CDMSID {cdmsid} in {table_name}")
                df_input.at[index, 'FileName'] = "NOT_FOUND"
                df_input.at[index, 'jobUrl'] = "NOT_FOUND"
                missing_records.append({'CDMSID': cdmsid, 'Table': table_name})

        except Exception as query_err:
            print(f"❌ Query error for CDMSID {cdmsid} in {table_name}: {query_err}")
            df_input.at[index, 'FileName'] = "ERROR"
            df_input.at[index, 'jobUrl'] = "ERROR"
            missing_records.append({
                'CDMSID': cdmsid,
                'Table': table_name,
                'Error': str(query_err)
            })

    conn.close()
    print("🔒 Connection closed.")

    # === SAVE TO EXCEL ===
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_input.to_excel(writer, sheet_name='Results', index=False)

        if missing_records:
            pd.DataFrame(missing_records).to_excel(writer, sheet_name='Not_Found', index=False)

    print(f"\n✅ Final output saved to: {output_path}")

except Exception as conn_err:
    print("❌ Failed to connect to the database:", conn_err)
