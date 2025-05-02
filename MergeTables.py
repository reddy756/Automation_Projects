import pyodbc
import pandas as pd

# Connection string
conn_str = (

)

# List of dates (excluding multi-date entries)
date_list_raw = [
    "28_02_2025", "11_03_2025", "20_12_2024", "26_12_2024", "18_02_2025", "24_12_2024", "27_12_2024",
    "16_12_2024", "10_03_2025", "13_12_2024", "10_12_2024", "26_02_2025", "27_02_2025",
    "18_12_2024", "23_12_2024", "19_12_2024", "03_03_2025", "11_03_2025", "11_12_2024", "04_03_2025",
    "13_03_2025", "12_12_2024", "11_03_2025", "12_03_2025", "25_02_2025", "30_12_2024", "07_03_2025",
    "12_03_2025", "31_12_2024", "09_01_2025", "06_01_2025", "02_01_2025", "03_01_2025", "08_01_2025",
    "07_01_2025", "10_01_2025", "22_01_2025", "23_01_2025", "18_03_2025", "21_01_2025", "17_01_2025",
    "20_01_2025", "16_01_2025", "12_01_2025", "11_01_2025", "24_01_2025", "27_01_2025", "28_01_2025",
    "29_01_2025", "04_02_2025", "30_01_2025", "31_01_2025", "03_02_2025", "05_02_2025", "10_02_2025",
    "17_02_2025", "13_02_2025", "11_02_2025", "07_02_2025", "06_02_2025", "05_02_2025", "18_02_2025",
    "14_02_2025", "12_02_2025", "27_02_2025", "21_03_2025", "19_02_2025", "19_03_2025", "24_03_2025",
    "24_02_2025", "21_02_2025", "20_02_2025", "05_03_2025", "06_03_2025", "20_03_2025", "17_03_2025",
    "25_03_2025", "26_03_2025", "27_03_2025", "28_03_2025", "03_04_2025", "02_04_2025", "01_04_2025",
    "07_04_2025", "09_04_2025", "10_04_2025", "04_04_2025", "15_04_2025", "14_04_2025", "11_04_2025",
    "08_04_2025"
]
# date_list_raw=['09_04_2025','10_04_2025']
# Remove entries with "/"
date_list = [d for d in date_list_raw if '/' not in d]

# Function to check table existence
def table_exists(cursor, table_name):
    cursor.execute("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = ?
    """, (table_name,))
    return cursor.fetchone()[0] == 1

# Build dynamic SQL query
def build_union_query(cursor, table_dates):
    select_statements = []

    for date_str in table_dates:
        date_compact = date_str.replace("_", "")
        table_name = f"LUTemp_{date_compact}"
        if table_exists(cursor, table_name):
            stmt = f"""
                SELECT 
                    CDMSID, 
                    joburl, 
                    COALESCE(CAST(FileName AS VARCHAR), CAST(CDMSID AS VARCHAR)) AS FileName,
                    '{date_str}' AS SourceDate,
                    '{table_name}' AS SourceTable
                FROM {table_name}
            """
            select_statements.append(stmt)
        else:
            print(f"Skipping missing table: {table_name}")

    if not select_statements:
        raise Exception("No valid tables found!")

    union_query = "\nUNION ALL\n".join(select_statements)

    final_query = f"""
    WITH TempTable AS (
        {union_query}
    )
    SELECT * FROM TempTable;
    """
    return final_query

# Execute and fetch into DataFrame
try:
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        sql_query = build_union_query(cursor, date_list)
        df = pd.read_sql(sql_query, conn)
        print(df.head())  # Show first few records
        output_path = "./output_data.xlsx"
        df.to_excel(output_path, index=False)
except Exception as e:
    print("Error:", e)
