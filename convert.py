import pdfplumber
import pandas as pd

# The exact path where your PDF is downloaded
pdf_path = r"C:\Users\joyah\Downloads\China Tariffs_2026HTSRev3 (2).pdf"
output_csv = "section301_rates.csv"

print("Opening PDF and extracting tables. This will take about 1 to 2 minutes...")

# The USTR PDF maps 8-digit codes to "Chapter 99" headings. 
# We translate those headings into the actual percentage rates.
rate_mapping = {
    "9903.88.15": 7.5,   # List 4A is currently 7.5%
    "9903.88.01": 25.0,  # List 1
    "9903.88.02": 25.0,  # List 2
    "9903.88.03": 25.0,  # List 3
    "9903.88.04": 25.0,  # List 3
}

data = []

try:
    # Open the PDF
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            
            if table:
                for row in table:
                    # Clean the text to prevent errors
                    hts_raw = str(row[0]).strip()
                    ch99_raw = str(row[1]).strip()
                    
                    # Remove the dots so "3924.10.40" becomes "39241040"
                    hts_clean = hts_raw.replace('.', '')
                    
                    # If it is a valid 8-digit code (skips the table headers)
                    if hts_clean.isdigit() and len(hts_clean) == 8:
                        # Find the rate, defaulting to 25.0% for new 2026 tariffs if unknown
                        rate = rate_mapping.get(ch99_raw, 25.0) 
                        data.append({"hts8": hts_clean, "s301_rate": rate})
                        
    # Save the massive list into your CSV file!
    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)
    print(f"✅ SUCCESS! Created '{output_csv}' with {len(df):,} Section 301 rules.")

except Exception as e:
    print(f"Error reading PDF: {e}")