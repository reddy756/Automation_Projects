import pandas as pd
from urllib.parse import urlparse

# Input file path
input_file = "" #Excel file input
sheet_name = "Sheet3"  # Change if your sheet is named differently

# Load the Excel sheet into DataFrame
df = pd.read_excel(input_file, sheet_name=sheet_name)

# Function to extract domain, now handles None or empty string for URLs
def extract_domain(url):
    if pd.isna(url) or url == "":
        return None  # Return None if URL is missing or empty
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None  # In case of any error, return None

# Check if the 'joburl' column exists
if 'joburl' not in df.columns:
    raise Exception("Column 'joburl' not found!")

# Apply domain extraction to 'joburl' column
df['domain'] = df['joburl'].apply(extract_domain)

# Write back to the **same sheet**, overwriting it
with pd.ExcelWriter(input_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"Domain column added to sheet '{sheet_name}' in '{input_file}'")
