import pandas as pd

OUTPUT_CSV = 'adcvd_warnings.csv'

print("Building AD/CVD Risk Database...")

adcvd_data = []

# --- 1. WOODEN CABINETS & VANITIES ---
for h in ['940340', '940360', '940391']: 
    adcvd_data.append({'hts_prefix': h, 'country': 'CN', 'case_desc': 'Wooden Cabinets and Vanities'})

# --- 2. MATTRESSES ---
for h in ['940421', '940429']: 
    for c in ['CN', 'VN', 'ID', 'RS', 'KH', 'MY', 'TH', 'TR', 'BG']: # China, Vietnam, Indonesia, etc.
        adcvd_data.append({'hts_prefix': h, 'country': c, 'case_desc': 'Mattresses (Various Cases)'})

# --- 3. QUARTZ SURFACE PRODUCTS ---
for h in ['681099']: 
    for c in ['CN', 'IN', 'TR']:
        adcvd_data.append({'hts_prefix': h, 'country': c, 'case_desc': 'Quartz Surface Products'})

# --- 4. SOLAR PANELS / CELLS ---
for h in ['854142', '854143']: 
    for c in ['CN', 'MY', 'TH', 'VN', 'KH']: # Heavily targeted right now
        adcvd_data.append({'hts_prefix': h, 'country': c, 'case_desc': 'Crystalline Silicon Photovoltaic Cells/Modules'})

# --- 5. HARDWOOD PLYWOOD ---
for h in ['441231', '441233', '441234', '441299']: 
    for c in ['CN', 'RS']:
        adcvd_data.append({'hts_prefix': h, 'country': c, 'case_desc': 'Hardwood Plywood Products'})

# --- 6. ALUMINUM EXTRUSIONS ---
for h in ['760421', '760429', '760820']: 
    for c in ['CN', 'CO', 'EC', 'IN', 'ID', 'IT', 'MY', 'MX', 'KR', 'TW', 'TH', 'TR', 'AE', 'VN']: 
        adcvd_data.append({'hts_prefix': h, 'country': c, 'case_desc': 'Aluminum Extrusions'})

# --- 7. STEEL NAILS ---
for h in ['731700']: 
    for c in ['CN', 'IN', 'KR', 'MY', 'OM', 'TW', 'TR', 'VN', 'AE']:
        adcvd_data.append({'hts_prefix': h, 'country': c, 'case_desc': 'Certain Steel Nails'})

# Create DataFrame and save to CSV
df = pd.DataFrame(adcvd_data)
df.to_csv(OUTPUT_CSV, index=False)

print(f"✅ SUCCESS! Created '{OUTPUT_CSV}' with {len(df)} AD/CVD warning triggers.")