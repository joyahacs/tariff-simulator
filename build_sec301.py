import pandas as pd
import re

# 👉 CHANGE THIS to the exact location of your Excel file!
excel_path = r"C:\Users\joyah\Downloads\China_Tariffs.xlsx"
output_csv = "section301_rates.csv"

# The engine that translates the government codes into actual duty percentages
rate_map = {
    "9903.88.01": 25.0, "9903.88.02": 25.0, "9903.88.03": 25.0,
    "9903.88.04": 25.0, "9903.88.15": 7.5,  "9903.91.01": 25.0,
    "9903.91.02": 50.0, "9903.91.03": 100.0,"9903.91.04": 25.0,
    "9903.91.05": 50.0, "9903.91.06": 25.0, "9903.91.07": 50.0,
    "9903.91.08": 25.0,
}

print(f"Reading Excel file from {excel_path}...")
try:
    # Read the Excel file. (Assumes HTS is the 1st column, Chapter 99 Heading is the 2nd column)
    df_excel = pd.read_excel(excel_path)
    
    data = []
    for index, row in df_excel.iterrows():
        hts_raw = str(row.iloc[0]).strip()
        heading_raw = str(row.iloc[1]).strip()
        
        # Clean the HTS code (remove dots)
        clean_hts = hts_raw.replace('.', '')
        rate = rate_map.get(heading_raw, 25.0)
        
        # Only keep rows that start with numbers
        if re.match(r'^\d+', clean_hts):
            data.append({
                "HTS": hts_raw,
                "clean_hts": clean_hts,
                "Heading": heading_raw,
                "s301_rate": rate
            })

    # Save cleanly to your app's database format
    df_new = pd.DataFrame(data).drop_duplicates(subset=['clean_hts'])
    df_new.to_csv(output_csv, index=False)
    print(f"✅ SUCCESS! Converted Excel to database. Added {len(df_new)} codes to {output_csv}.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Tip: You might need to install openpyxl. Run: pip install openpyxl")