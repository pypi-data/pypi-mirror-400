import smart_open
import json
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
import pandas as pd


def google_sheet_to_pandas_df(url, tab_name, google_credentials_json_file):
    with smart_open.open(google_credentials_json_file, 'r') as f:
        credentials = json.load(f)
    creds = Credentials.from_service_account_info(
        credentials,
        scopes=[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_url(url)

    worksheet = spreadsheet.worksheet(tab_name)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    n_rows = df.shape[0]
    print(f'Read in {n_rows} rows from url: {url}, tab: {tab_name}.')
    return df


def save_pandas_df_to_google_sheet(url, tab_name, google_credentials_json_file, df):
    # --- Load credentials from S3 ---
    with smart_open.open(s3_creds_path, 'r') as f:
        credentials = json.load(f)

    # --- Authenticate ---
    creds = Credentials.from_service_account_info(
        credentials,
        scopes=[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_url(url)
    worksheet = spreadsheet.worksheet(tab_name)
    worksheet.clear()
    set_with_dataframe(worksheet, df)
    print(f"Successfully wrote {len(df)} rows to '{tab_name}' in {url}.")