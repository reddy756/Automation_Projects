import pandas as pd
import pyodbc  # Or use sqlalchemy, psycopg2, etc., based on your DB
from openpyxl import load_workbook

# 1. Load Excel Sheet

# 2. Connect to your Database
conn = pyodbc.connect(
      
)
print('Connected to DB')
cursor = conn.cursor()

# 3. Function to run query and return Sno and ScheduleNo
def get_schedule_data(job_url: str):
    query = """
        SELECT Sno, ScheduleNo
        FROM CP_Companies
        WHERE jobURL = ?
    """
    cursor.execute(query, (job_url,))
    result = cursor.fetchone()
    return result if result else (None, None)

# === Main Execution ===

input_file = ''       # Path to the Excel file
sheet_name = 'Sheet1'              # Replace with your actual sheet name

# 1. Read the specified sheet from Excel file
df = pd.read_excel(input_file, sheet_name=sheet_name)

# 2. Add empty columns
df['Sno'] = None
df['ScheduleNo'] = None

# 3. Populate Sno and ScheduleNo
for index, row in df.iterrows():
    job_url = str(row['jobUrl'])
    sno, sched_no = get_schedule_data(job_url)
    df.at[index, 'Sno'] = sno
    df.at[index, 'ScheduleNo'] = sched_no

# 4. Write back to the same Excel file and same sheet
with pd.ExcelWriter(input_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df.to_excel(writer, sheet_name=sheet_name, index=False)

# 5. Clean up
cursor.close()
conn.close()