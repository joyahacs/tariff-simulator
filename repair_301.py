import csv
import re
import os

input_file = r'C:\Users\jiafe\.gemini\antigravity\scratch\us-tariffs-simulator\section301_rates.csv'
output_file = r'C:\Users\jiafe\.gemini\antigravity\scratch\us-tariffs-simulator\section301_rates_repaired.csv'

# Standard rate mapping
RATE_MAP = {
    '9903.88.15': 7.5,
}

def repair_hts(val):
    # Regex to catch YYYY-MM-DD HH:MM:SS or variations
    # E.g. "7116-10-25 00:00:00" -> "7116.10.25"
    if '00:00:00' in val or '-' in val:
        # Extract all numeric parts
        parts = re.findall(r'\d+', val)
        if len(parts) >= 3:
            # If parts[2] is a year (e.g. "2026"), it might be flipped. 
            # But in the user's data, the first part is the HTS (e.g. "7116").
            # HTS codes are usually 4.2.2 or 4.4.2 format.
            hts = ".".join(parts[:3])
            return hts
    return val

with open(input_file, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

repaired_rows = []
for row in rows:
    original_hts = row['HTS']
    repaired_hts = repair_hts(original_hts)
    
    # Recalculate clean_hts
    clean_hts = re.sub(r'\D', '', repaired_hts)
    
    # Assign rate based on heading
    heading = row['Heading']
    rate = RATE_MAP.get(heading, 25.0)
    
    repaired_rows.append({
        'HTS': repaired_hts,
        'clean_hts': clean_hts,
        'Heading': heading,
        's301_rate': rate
    })

# Deduplicate
unique_rows = {}
for r in repaired_rows:
    key = (r['clean_hts'], r['Heading'])
    if key not in unique_rows:
        unique_rows[key] = r

with open(output_file, mode='w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['HTS', 'clean_hts', 'Heading', 's301_rate'])
    writer.writeheader()
    for row in sorted(unique_rows.values(), key=lambda x: x['clean_hts']):
        writer.writerow(row)

print(f"Repaired {len(rows)} rows into {len(unique_rows)} unique mappings.")
