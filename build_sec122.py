import pdfplumber
import pandas as pd
import re
import os

# Update this path to exactly match your downloaded PDF
PDF_PATH = r"D:\OneDrive\Trump Tariff\2026-02-20 - Imposing a Temporary Import Surcharge to Address Fundamental International Payments Problems – The White House.pdf"
OUTPUT_CSV = r"D:\tariff_project\sec122_exemptions.csv"

print("Scanning White House Proclamation for Section 122 Annex II...")

data = []
if os.path.exists(PDF_PATH):
    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # Look for rows with at least 3 columns (HTSUS, Description, Scope Limitations)
                    if len(row) >= 3:
                        hts_raw = str(row[0]).replace('\n', ' ')
                        desc = str(row[1]).replace('\n', ' ').strip()
                        scope = str(row[2]).replace('\n', ' ').replace('None', '').strip()
                        
                        # Ignore table headers
                        if "HTSUS" in hts_raw:
                            continue
                            
                        # Extract all valid 8-digit codes from the cell (e.g., 0201.10.05)
                        hts_matches = re.findall(r'\d{4}\.\d{2}\.\d{2}', hts_raw)
                        for hts in hts_matches:
                            data.append({
                                "HTSUS": hts,
                                "Description": desc,
                                "Scope Limitations": scope
                            })

    df = pd.DataFrame(data).drop_duplicates(subset=['HTSUS'])
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ SUCCESS! Extracted {len(df)} exemptions and saved to {OUTPUT_CSV}")
else:
    print("❌ ERROR: PDF not found at specified path.")