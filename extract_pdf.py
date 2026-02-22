import pdfplumber
import pandas as pd
import re

pdf_path = r"D:\OneDrive\Trump Tariff\2025-11-13 - ANNEX II.pdf"
csv_path = r"D:\tariff_project\sec122_exemptions.csv"

all_data = []
print("📖 Reading PDF (Scanning Annex I text and Annex II tables)...")

with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        # Pages 1 & 2 contain Annex I (which is a raw text paragraph, NOT a table!)
        if i < 2:
            text = page.extract_text()
            if text:
                codes = re.findall(r'\b\d{4}\.\d{2}\.\d{2}\b', text)
                for c in codes:
                    all_data.append([c, "Annex I General Exemption", "Addition"])
        
        # Pages 3+ contain Annex II (formatted as Tables)
        table = page.extract_table()
        if table:
            for row in table:
                # Flatten row to ignore broken PDF columns
                row_str = " ".join([str(cell).replace('\n', ' ') for cell in row if cell])
                hts_matches = re.findall(r'\b\d{4}(?:\.\d{2})?(?:\.\d{2})?\b', row_str)
                
                if hts_matches:
                    note = ""
                    if re.search(r'\b(Pharma|Aircraft|Addition|Ex)\b', row_str, re.IGNORECASE):
                        note = re.search(r'\b(Pharma|Aircraft|Addition|Ex)\b', row_str, re.IGNORECASE).group(1)
                    
                    hts_col = " ".join(hts_matches)
                    all_data.append([hts_col, row_str, note])

df = pd.DataFrame(all_data, columns=["HTSUS", "Description", "Scope Limitations"])
df.drop_duplicates(subset=["HTSUS"], inplace=True)
df.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"🎉 Success! Extracted {len(df)} rules!")