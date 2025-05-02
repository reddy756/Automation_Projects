
import pandas as pd
import requests


def check_url_status(excel_file, sheet_name, url_column):
    # Load the Excel file and sheet
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    # Check if the URL column exists in the sheet
    if url_column not in df.columns:
        print(f"Error: Column '{url_column}' not found in the sheet.")
        return

    # Create a new column for status codes (or update if already exists)
    status_column = url_column + '_Status_Code'
    if status_column not in df.columns:
        df[status_column] = None  # Add the new column if it doesn't exist

    # Loop through each URL in the given column
    for index, row in df.iterrows():
        url = row[url_column]

        # Check if the URL is not empty
        if pd.notna(url):
            try:
                # Make the GET request with a timeout of 10 seconds
                print('Running URL Checker for ---->', url)
                response = requests.get(url, timeout=15)

                # Store the status code
                df.at[index, status_column] = response.status_code
            except requests.Timeout:
                # If the request times out, update with "Too long time"
                df.at[index, status_column] = "Timeout"
            except requests.RequestException as e:
                # For other exceptions, store the error message
                df.at[index, status_column] = f"Error: {str(e)}"

    # Save the updated DataFrame back to the same Excel file
    df.to_excel(excel_file, index=False)
    print(f"Excel file updated with status codes saved in the same file: {excel_file}")


# Example usage
excel_file = 'C:\\Users\\Abdullah.Habeeb\\Documents\\URLNotWorking_Nexgile.xlsx'  # Path to your Excel file
sheet_name = 'Merged'  # Name of the sheet to process
url_column = 'jobUrl'  # The column name containing URLs


check_url_status(excel_file, sheet_name, url_column)
