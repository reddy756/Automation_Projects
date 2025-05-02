import pyodbc
import pandas as pd

# Connection string (fill in your credentials)
conn_str = (
  
)

# Filtered dates (>= 19_02_2025)
# filtered_dates=['10_03_2025']
filtered_dates = [
    "19_02_2025", "21_03_2025", "19_03_2025", "24_03_2025", "24_02_2025", "21_02_2025", "20_02_2025",
    "25_02_2025", "26_02_2025", "27_02_2025", "28_02_2025", "03_03_2025", "04_03_2025", "05_03_2025",
    "06_03_2025", "07_03_2025", "10_03_2025", "11_03_2025", "12_03_2025", "13_03_2025", "17_03_2025",
    "18_03_2025", "19_03_2025", "20_03_2025", "21_03_2025", "24_03_2025", "25_03_2025", "26_03_2025",
    "27_03_2025", "28_03_2025", "31_03_2025", "01_04_2025", "02_04_2025", "03_04_2025", "04_04_2025",
    "07_04_2025", "08_04_2025", "09_04_2025", "10_04_2025", "11_04_2025", "14_04_2025", "15_04_2025"
]

# Initialize empty DataFrame
combined_df = pd.DataFrame()

# Connect and execute
try:
    with pyodbc.connect(conn_str) as conn:
        for date_str in filtered_dates:
            table_suffix = date_str.replace("_", "")
            table_name = f"LUTemp_{table_suffix}"

            query = f"""
                select a.CDMSID,b.sno,  b.dailyspider, b.cdmsid as ActualCDMSID, b.jobUrl, b.active, b.PyResource, b.patternid, b.ScheduleNo,
                COALESCE(a.FileName, CAST(a.CDMSID AS VARCHAR)) AS FileName,
                '{date_str}' AS SourceDate
                FROM {table_name} a
                INNER JOIN CP_Companies b
                ON a.jobUrl = b.jobUrl AND a.CDMSID != b.CDMSID
                
            """

            try:
                df_temp = pd.read_sql(query, conn)
                combined_df = pd.concat([combined_df, df_temp], ignore_index=True)
                print(f"✅ Fetched data for table: {table_name}")
            except Exception as inner_e:
                print(f"⚠️ Skipping {table_name} due to error: {inner_e}")

    # Save to Excel
    output_path = "./CDMSIDMisMatch.xlsx"
    combined_df.to_excel(output_path, index=False)
    print(f"✅ Final Excel saved to: {output_path}")

except Exception as e:
    print("❌ Error during DB operation:", e)
