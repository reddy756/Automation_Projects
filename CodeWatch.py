import os
import pandas as pd
import pyodbc
from datetime import datetime, timedelta
# from main.mailspy import sendMail
import glob
import ast

# === Email Map ===
EMailMap = {
   ''' Dict containing all the emails of the users mapped to their names based on the format stored in the database'''
}

conn = pyodbc.connect('''
SERVER = 'your_server_name_or_ip'  # e.g., 'localhost' or '192.168.1.100'
DATABASE = 'your_database_name'    # e.g., 'TestDB'
USERNAME = 'your_username'         # e.g., 'sa'
PASSWORD = 'your_password'         # e.g., 'your_password'

'''

)

TierPrevPhase = conn.execute('SELECT MAX(TPhase) FROM CP_Tier1_Phase WITH(nolock)').fetchone()[0] - 1
NonTierPrevPhase = conn.execute('SELECT MAX(TPhase) FROM CP_NonTier1_Phase WITH(nolock)').fetchone()[0] - 1

query = f"""
SELECT a.CDMSID, a.PyResource, a.ScheduleNo, a.Sno, a.DailySpider, b.CrawlStatus, b.ErrorLog, b.RecordDate, b.JobCounts 
FROM CP_Companies a 
INNER JOIN CP_Tier1_CrawlStatus b ON a.Sno = b.URLSNo 
WHERE b.Phase = {TierPrevPhase} AND a.PatternID > 999 AND a.ScheduleNo IS NOT NULL AND a.Active > 0 AND a.PyResource = 'BhaskarD'
UNION
SELECT a.CDMSID, a.PyResource, a.ScheduleNo, a.Sno, a.DailySpider, b.CrawlStatus, b.ErrorLog, b.RecordDate, b.JobCounts 
FROM CP_Companies a 
INNER JOIN CP_NonTier1_CrawlStatus b ON a.Sno = b.URLSNo 
WHERE b.Phase = {NonTierPrevPhase} AND a.PatternID > 999 AND a.ScheduleNo IS NOT NULL AND a.Active > 0 AND a.PyResource = 'BhaskarD'
"""

df = pd.read_sql(query, conn)

# === File Checks ===
base_dir = r""  #path of the folder to perform checks
now = datetime.now()
three_days_ago = now - timedelta(days=3)

def has_spidercode_function(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            tree = ast.parse(file.read(), filename=filepath)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "spiderCode":
                return True
    except Exception:
        return False
    return False

def check_file(row):
    folder_name = f"ScheduleNo-{row['ScheduleNo']}"
    folder_path = os.path.join(base_dir, folder_name)
    cdmsid = row['CDMSID']

    pattern = os.path.join(folder_path, f"{cdmsid}*.py")
    matching_files = glob.glob(pattern)

    file_exists = len(matching_files) > 0
    file_path = matching_files[0] if file_exists else None

    last_modified = pd.to_datetime(os.path.getmtime(file_path), unit='s') if file_exists else None
    stale = file_exists and last_modified < three_days_ago

    file_size_ok = False
    has_spidercode = False

    if file_exists:
        size_kb = os.path.getsize(file_path) / 1024
        file_size_ok = size_kb > 3
        has_spidercode = has_spidercode_function(file_path)

    return pd.Series([
        file_exists,
        file_exists,
        file_path,
        last_modified,
        stale,
        file_size_ok,
        has_spidercode
    ])

df[['FilePathPresent', 'InCorrectFolder', 'ActualPath', 'LastModified', 'IsStale', 'SizeOK', 'HasSpiderCode']] = df.apply(check_file, axis=1)

# === Enhanced Summary with SizeOK and HasSpiderCode ===
summary = df.groupby('PyResource').agg(
    Total_Files=('CDMSID', 'count'),
    Files_Uploaded=('FilePathPresent', 'sum'),
    Files_Stale=('IsStale', 'sum'),
    Files_Small=('SizeOK', lambda x: (~x).sum()),
    Missing_spiderCode=('HasSpiderCode', lambda x: (~x).sum())
)

summary['Upload Completion %'] = round((summary['Files_Uploaded'] / summary['Total_Files']) * 100, 2)
summary['Update Completion %'] = round(((summary['Files_Uploaded'] - summary['Files_Stale']) / summary['Files_Uploaded']) * 100, 2)
missing_df = df[df['FilePathPresent'] == False]
notify_df = df[(df['FilePathPresent'] == False) | (df['CrawlStatus'] != 1)]
stale_df = df[df['IsStale'] == True]
small_files_df = df[df['SizeOK'] == False]
missing_spidercode_df = df[df['HasSpiderCode'] == False]


output_file = ""  #Output file Name
with pd.ExcelWriter(output_file) as writer:
    df.to_excel(writer, sheet_name="FileStatus", index=False)
    summary.reset_index().to_excel(writer, sheet_name="Summary", index=False)
    missing_df.to_excel(writer, sheet_name="MissingFiles", index=False)
    notify_df.to_excel(writer, sheet_name="NotifyList", index=False)
    stale_df.to_excel(writer, sheet_name="StaleFiles", index=False)
    small_files_df.to_excel(writer, sheet_name="Files<3KB", index=False)
    missing_spidercode_df.to_excel(writer, sheet_name="Missing_spiderCode", index=False)

print(f"✅ Report generated: {output_file}")

# === Email Generation ===
messages = {}
for name, group in df.groupby('PyResource'):
    user_issues = group[
        (group['FilePathPresent'] == False) |
        (group['CrawlStatus'] != 1)
    ]
    if user_issues.empty:
        continue

    user_issues = user_issues.sort_values(by=['ScheduleNo', 'CDMSID'])
    message = f"""
    <html>
    <body>
        <p>Hi {name},</p>
        <p>The following issues were found in your Companies:</p>
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; font-family: Arial, sans-serif;">
            <thead style="background-color: #f2f2f2;">
                <tr>
                    <th>Sno</th>
                    <th>CDMSID</th>
                    <th>Schedule No</th>
                    <th>Issues</th>
                </tr>
            </thead>
            <tbody>
    """
    for i, row in enumerate(user_issues.itertuples(), start=1):
        issues = []
        if not row.FilePathPresent:
            issues.append("🚫 Missing .py file")
        if row.CrawlStatus != 1:
            issues.append(f"⚠️ CrawlStatus = {row.CrawlStatus}")
        message += f"""
            <tr>
                <td>{i}</td>
                <td>{row.CDMSID}</td>
                <td>{row.ScheduleNo}</td>
                <td>{" | ".join(issues)}</td>
            </tr>
        """
    message += """
            </tbody>
        </table>
        <p>Please resolve these at your earliest convenience.</p>
        <p>Thanks!</p>
    </body>
    </html>
    """
    messages[name] = message

# === Send Email ===
print("\n📬 Email Summaries (Missing / Crawl / Stale):\n")
for name, msg in messages.items():
    print(f"--- Email to: {name} ---")
    print(msg)
    sendMail(EMailMap[name], MailBody=msg) # function to send the mails
    print(msg)
    print("-" * 50)
