import pdfplumber
import pandas as pd
import os

# Your specific file paths
pdf_path = r"D:\OneDrive\Trump Tariff\2025-11-13 - ANNEX II.pdf"
csv_path = r"D:\tariff_project\sec122_exemptions.csv"

all_data = []

print("📖 Opening PDF and extracting tables (this will take a minute for 98 pages)...")

try:
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            # Extract the table from the current page
            table = page.extract_table()
            
            if table:
                for row in table:
                    # We only want rows that have exactly 3 columns (HTSUS, Description, Scope Limitations)
                    if len(row) == 3:
                        all_data.append(row)
    
    print("✅ Extraction complete! Cleaning up data...")
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(all_data, columns=["HTSUS", "Description", "Scope Limitations"])
    
    # Remove repeated header rows from the PDF
    df = df[~df["HTSUS"].astype(str).str.contains("HTSUS", case=False, na=False)]
    
    # Remove empty rows
    df = df.dropna(how='all')
    
    # Clean up PDF line breaks
    df = df.map(lambda x: str(x).replace('\n', ' ').strip() if pd.notnull(x) and x is not None else "")
    
    # Save to CSV in your project folder
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print(f"🎉 Success! Saved {len(df)} exemptions to {csv_path}")

except Exception as e:
    print(f"❌ Error: {e}")