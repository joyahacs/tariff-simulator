import pandas as pd
import pdfplumber
import re
import os

# --- PATHS (Update these if your PDFs are named differently) ---
PDF_DIR = r"D:\OneDrive\Trump Tariff"
SEC301_PDF = os.path.join(PDF_DIR, "2024-05-28 - Section 301 Exclusion Extension FRN.pdf")
COPPER_PDF = os.path.join(PDF_DIR, "2025-07-31 - copper.pdf")
AUTO_PDF = os.path.join(PDF_DIR, "2025-05-01 - CSMS # 64916652 - GUIDANCE_ Import Duties on Certain Automobile Parts.pdf")
STEEL_PDF = os.path.join(PDF_DIR, "2025-08-15 - Section 232 Steel Derivative.pdf")
ALUM_PDF = os.path.join(PDF_DIR, "2025-08-15 - Section 232 Aluminum Derivative.pdf")
SEMI_PDF = os.path.join(PDF_DIR, "2026-01-15 - SemiConductor.prc_.rel-ANNEX.pdf")
MHDV_PDF = os.path.join(PDF_DIR, "2025-10-17 - MediumandHeavyDutyVehicles.Parts_.Buses_.section232.prc_.rel-ANNEX.pdf")
TIMBER_PDF = os.path.join(PDF_DIR, "2025-09-29 - Adjusting Imports of Timber, Lumber, and their Derivative Products into the United States – The White House.pdf")

OUTPUT_DIR = r"D:\tariff_project"

def extract_hts_from_pdf(pdf_path):
    codes = set()
    if not os.path.exists(pdf_path): return list(codes)
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # 1. Check Tables
            table = page.extract_table()
            if table:
                for row in table:
                    for cell in row:
                        if cell:
                            for word in str(cell).split():
                                word_clean = re.sub(r'[^\d\.]', '', word)
                                if re.match(r'^\d{4}(\.\d{2}(\.\d{2,4})?)?$', word_clean):
                                    if len(word_clean) == 4 and word_clean.startswith(('19', '20')): continue
                                    codes.add(word_clean)
            
            # 2. Check Raw Text (Catches the 4-digit headers)
            text = page.extract_text()
            if text:
                matches = re.findall(r'\b\d{4}(?:\.\d{2}(?:\.\d{2,4})?)?\b', text)
                for m in matches:
                    if len(m) == 4 and m.startswith(('19', '20')): continue
                    codes.add(m)
    return list(codes)

print("🔨 Building Modular Databases...")

# 1. Sec 301 Exemptions
print("Scanning Sec 301 Exemptions for Exact Descriptions...")
sec301_data = []
if os.path.exists(SEC301_PDF):
    with pdfplumber.open(SEC301_PDF) as pdf:
        for page in pdf.pages[6:]:
            table = page.extract_table()
            if table:
                for row in table:
                    if len(row) >= 3:
                        desc_cell = str(row[-1]).replace('\n', ' ')
                        hts_match = re.search(r'([0-9]{4}\.[0-9]{2}\.[0-9]{4})', desc_cell)
                        if hts_match:
                            hts = hts_match.group(1)
                            clean_desc = re.sub(r'\(described in statistical reporting number.*?\)', '', desc_cell).strip()
                            sec301_data.append({"HTSUS": hts, "Description": clean_desc})
                        elif re.match(r'^[0-9]{4}\.[0-9]{2}\.[0-9]{4}$', desc_cell.strip()):
                            sec301_data.append({"HTSUS": desc_cell.strip(), "Description": "Official USTR Exemption"})
            
            text = page.extract_text()
            if text:
                text = text.replace('\n', ' ')
                matches = re.finditer(r'\b\d+\)\s+(.*?)\(described in statistical reporting numbers?\s+([0-9]{4}\.[0-9]{2}\.[0-9]{4})\)', text, re.IGNORECASE)
                for m in matches:
                    desc = m.group(1).strip()
                    hts = m.group(2).strip()
                    if hts not in [x['HTSUS'] for x in sec301_data]:
                        sec301_data.append({"HTSUS": hts, "Description": desc})
                        
                bare_matches = re.finditer(r'\b\d+\)\s+([0-9]{4}\.[0-9]{2}\.[0-9]{4})\b', text)
                for m in bare_matches:
                    if m.group(1) not in [x['HTSUS'] for x in sec301_data]:
                        sec301_data.append({"HTSUS": m.group(1), "Description": "Official USTR Exemption"})

df_301 = pd.DataFrame(sec301_data).drop_duplicates(subset=["HTSUS"])
df_301.to_csv(os.path.join(OUTPUT_DIR, "sec301_exemptions.csv"), index=False)

# 2. Section 232 Databases
databases_to_build = [
    ("Copper", COPPER_PDF, 50.0, "sec232_copper.csv"),
    ("Auto Parts", AUTO_PDF, 25.0, "sec232_auto.csv"),
    ("Steel", STEEL_PDF, 25.0, "sec232_steel.csv"),
    ("Aluminum", ALUM_PDF, 10.0, "sec232_aluminum.csv"),
    ("Semiconductors", SEMI_PDF, 25.0, "sec232_semi.csv")
]

for name, pdf_path, rate, filename in databases_to_build:
    print(f"Scanning {name}...")
    codes = extract_hts_from_pdf(pdf_path)
    df = pd.DataFrame({"HTSUS": codes, "Rate": [rate]*len(codes)})
    df.to_csv(os.path.join(OUTPUT_DIR, filename), index=False)

# 3. Special Case: MHDV
print("Scanning MHDV & Buses...")
mhdv_codes = extract_hts_from_pdf(MHDV_PDF)
mhdv_data = [{"HTSUS": code, "Rate": 10.0 if code.startswith('8702') else 25.0} for code in mhdv_codes]
pd.DataFrame(mhdv_data).to_csv(os.path.join(OUTPUT_DIR, "sec232_mhdv.csv"), index=False)

# 4. Special Case: Timber
print("Scanning Timber & Lumber...")
timber_codes = extract_hts_from_pdf(TIMBER_PDF)
timber_data = []
for code in timber_codes:
    rate = 25.0 if code.startswith('9401') or code.startswith('9403') else 10.0
    timber_data.append({"HTSUS": code, "Rate": rate})
pd.DataFrame(timber_data).to_csv(os.path.join(OUTPUT_DIR, "sec232_timber.csv"), index=False)

print("✅ SUCCESS! All databases generated with 4-digit codes included.")