import streamlit as st
import pandas as pd
import json
import os
import re
import io

# --- PAGE SETUP & CUSTOM CSS ---
st.set_page_config(page_title="Tariff Simulator PRO", page_icon="🏛️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important; 
}

.block-container { padding-top: 1.2rem; padding-bottom: 1.2rem; max-width: 98%; } 

/* FIXED TITLE CLIPPING (P, G, Y descenders) */
.main-title { 
    font-size: 2rem; 
    font-weight: 800; 
    background: linear-gradient(90deg, #1e3a8a, #0ea5e9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0px; 
    letter-spacing: -0.5px;
    padding-bottom: 10px; /* Stronger padding */
    line-height: 1.5; /* Increased line height to give the descenders room */
}
            
.sub-title {
    font-size: 0.9rem;
    color: #64748b;
    font-weight: 600;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: -10px; /* Pull it slightly up to offset the title padding */
}

/* COMPACT FLEXPORT RESULTS LAYOUT */
.results-cards-container {
    display: flex;
    gap: 12px;
    margin-bottom: 10px;
    align-items: stretch;
}
.flexport-card {
    flex: 1;
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* Duty Rate Card */
.duty-split-top {
    flex: 1;
    padding: 12px 15px; 
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.duty-rate-title { font-size: 11.5px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
.duty-rate-value { font-size: 2.6rem; font-weight: 700; color: #6366f1; line-height: 1; margin: 0; }
.duty-total-value { font-size: 2.2rem; font-weight: 700; color: #0f172a; line-height: 1; margin: 0; }

/* Line Items (4-Column Form 7501 Grid) */
.line-item-box { background: #f8fafc; padding: 12px 15px; border-radius: 6px; margin-bottom: 8px; border: 1px solid #e2e8f0; }
.line-item-header { display: flex; justify-content: space-between; font-weight: 600; color: #1e293b; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid #cbd5e1; font-size: 13px;}

.line-item-grid {
    display: grid;
    grid-template-columns: 100px 1fr 75px 95px; 
    gap: 10px;
    align-items: center;
    font-size: 13px;
    color: #475569;
    margin-bottom: 5px;
}
.col-code { font-weight: 600; color: #334155; text-decoration: underline; font-family: 'Courier New', Courier, monospace; font-size: 12.5px; }
.col-desc { display: flex; align-items: center; }
.col-rate { text-align: right; font-weight: 500; }
.col-val { font-weight: 600; color: #0f172a; text-align: right; }

.line-item-tag { padding: 3px 8px; border-radius: 4px; font-size: 10.5px; font-weight: 700; display: inline-block;}

/* ULTRA-COMPACT BANNERS */
.questionnaire-header {
    background: linear-gradient(90deg, #1e293b, #334155);
    color: #f8fafc;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-left: 3px solid #3b82f6;
}
.fta-alert {
    background-color: #f0fdf4;
    border: 1px solid #22c55e;
    color: #166534;
    padding: 6px 10px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 12px;
    margin-top: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* COMPACT COMPLIANCE ALERTS */
.compact-alert {
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 12.5px;
    margin-bottom: 6px;
    border: 1px solid transparent;
    line-height: 1.3;
}
.alert-danger { background-color: #fef2f2; border-color: #fecaca; color: #991b1b; }
.alert-warning { background-color: #fffbeb; border-color: #fde68a; color: #92400e; }
.alert-info { background-color: #eff6ff; border-color: #bfdbfe; color: #1e40af; }

/* Streamlit Overrides for Density */
div[data-testid="stExpander"] div[role="button"] p { font-size: 13.5px; font-weight: 600; }
.stAlert { padding: 8px 12px !important; margin-bottom: 8px !important; font-size: 13px !important; }
div.row-widget.stRadio > div { flex-direction: row; gap: 15px; } 
</style>
""", unsafe_allow_html=True)

# Special Header
st.markdown('<div class="main-title">🌐 TradePro Tariff Simulator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Advanced Customs Duty & Compliance Engine</div>', unsafe_allow_html=True)

# SECTION 122 GLOBAL ALERT
st.error("🚨 **EXECUTIVE ORDER:** A **15% global tariff** under **Section 122** applies to all origins unless exempted in Annex II.")

COUNTRIES = [
    "AF - Afghanistan", "AL - Albania", "DZ - Algeria", "AD - Andorra", "AO - Angola", 
    "AR - Argentina", "AU - Australia", "AT - Austria", "BH - Bahrain", "BD - Bangladesh", 
    "BE - Belgium", "BR - Brazil", "CA - Canada", "CL - Chile", "CN - China", 
    "CO - Colombia", "CR - Costa Rica", "CU - Cuba", "DK - Denmark", "DO - Dominican Republic", 
    "EG - Egypt", "SV - El Salvador", "FI - Finland", "FR - France", "DE - Germany", 
    "GR - Greece", "GT - Guatemala", "HN - Honduras", "HK - Hong Kong", "IN - India", 
    "ID - Indonesia", "IE - Ireland", "IL - Israel", "IT - Italy", "JP - Japan", 
    "JO - Jordan", "KP - North Korea", "KR - South Korea", "MY - Malaysia", "MX - Mexico", 
    "MA - Morocco", "NL - Netherlands", "NZ - New Zealand", "NI - Nicaragua", "NG - Nigeria", 
    "NO - Norway", "OM - Oman", "PK - Pakistan", "PA - Panama", "PE - Peru", 
    "PH - Philippines", "PL - Poland", "PT - Portugal", "QA - Qatar", "RU - Russia", 
    "SA - Saudi Arabia", "SG - Singapore", "ZA - South Africa", "ES - Spain", "SE - Sweden", 
    "CH - Switzerland", "TW - Taiwan", "TH - Thailand", "TR - Turkey", "AE - United Arab Emirates", 
    "GB - United Kingdom", "US - United States", "VN - Vietnam"
]

FTA_MAPPING = {
    "AU": ["AU"], "BH": ["BH"], "CL": ["CL"], "CO": ["CO"], "IL": ["IL"], 
    "JO": ["JO"], "JP": ["JP"], "KR": ["KR"], "MA": ["MA"], "OM": ["OM"], 
    "PA": ["PA"], "PE": ["PE"], "SG": ["SG"], "CA": ["S", "S+"], "MX": ["S", "S+"], 
    "CR": ["P", "P+"], "DO": ["P", "P+"], "SV": ["P", "P+"], "GT": ["P", "P+"], 
    "HN": ["P", "P+"], "NI": ["P", "P+"], "ZA": ["D"], "NG": ["D"]
}
COL2_COUNTRIES = ["CU", "KP", "RU", "BY"]

ANNEX_I_CODES = {
    "02011005": "", "02011010": "", "02011050": "", "02012002": "", "02012004": "", "02012006": "", "02012010": "", "02012030": "", "02012050": "", "02012080": "", "02013002": "", "02013004": "", "02013006": "", "02013010": "", "02013030": "", "02013050": "", "02013080": "", "02021005": "", "02021010": "", "02021050": "", "02022002": "", "02022004": "", "02022006": "", "02022010": "", "02022030": "", "02022050": "", "02022080": "", "02023002": "", "02023004": "", "02023006": "", "02023010": "", "02023030": "", "02023050": "", "02023080": "", "02061000": "", "02062100": "", "02062200": "", "02062900": "", "02102000": "", "07020020": "", "07020040": "", "07020060": "", "07099905": "", "07099910": "", "07108015": "", "07119030": "", "07123200": "", "07123410": "", "07123420": "", "07133420": "", "07133440": "", "07141010": "", "07141020": "", "07144010": "", "07144020": "", "07144050": "", "07144060": "", "07145010": "", "07145020": "", "07145060": "", "07149042": "", "07149044": "", "07149046": "", "07149048": "", "07149061": "", "08011100": "", "08011200": "", "08011901": "", "08012100": "", "08012200": "", "08013100": "", "08013200": "", "08024100": "", "08024200": "", "08026100": "", "08026200": "", "08027010": "", "08027020": "", "08028010": "", "08028020": "", "08029110": "", "08029190": "", "08029210": "", "08029290": "", "08031010": "", "08031020": "", "08039000": "", "08043020": "", "08043040": "", "08043060": "", "08044000": "", "08045040": "", "08045060": "", "08045080": "", "08051000": "", "08055030": "", "08055040": "", "08072000": "", "08084020": "", "08084040": "", "08105000": "", "08106000": "", "08109027": "", "08109046": "", "08119010": "", "08119025": "", "08119030": "", "08119040": "", "08119050": "", "08119052": "", "08129040": "", "09011100": "", "09011200": "", "09012100": "", "09012200": "", "09019010": "", "09019020": "", "09021010": "", "09021090": "", "09022010": "", "09022090": "", "09023000": "", "09024000": "", "09030000": "", "09041100": "", "09041200": "", "09042120": "", "09042140": "", "09042160": "", "09042180": "", "09042220": "", "09042240": "", "09042273": "", "09042276": "", "09042280": "", "09051000": "", "09052000": "", "09061100": "", "09061900": "", "09062000": "", "09071000": "", "09072000": "", "09081100": "", "09081200": "", "09082100": "", "09082220": "", "09082240": "", "09083100": "", "09083200": "", "09092100": "", "09092200": "", "09093100": "", "09093200": "", "09096100": "", "09096200": "", "09101100": "", "09101200": "", "09102000": "", "09103000": "", "09109100": "", "09109907": "", "09109910": "", "09109920": "", "09109940": "", "09109950": "", "09109960": "", "10039040": "", "10083000": "", "10084000": "", "10086000": "", "11062090": "", "11063020": "", "11081400": "", "11081900": "", "12030000": "", "12079100": "", "15131100": "", "15131900": "", "15211000": "", "15219020": "", "16025005": "", "16025007": "", "16025008": "", "16025021": "", "16025060": "", "16025090": "", "18010000": "", "18020000": "", "18031000": "", "18032000": "", "18040000": "", "18050000": "", "19030020": "", "19030040": "", "20019045": "", "20059160": "", "20060040": "", "20079940": "", "20079950": "", "20081915": "", "20082000": "", "20089100": "", "20089913": "", "20089915": "", "20089940": "", "20089945": "", "20089991": "", "20091100": "", "20091225": "", "20091245": "", "20091900": "", "20093920": "", "20094940": "", "21011129": "", "21011290": "", "21012020": "", "21069048": "", "22029930": "", "22029935": "", "31010000": "", "31021000": "", "31022100": "", "31022900": "", "31023000": "", "31024000": "", "31025000": "", "31026000": "", "31028000": "", "31029001": "", "31031100": "", "31031900": "", "31039001": "", "31053000": "", "31054000": "", "31055100": "", "31055900": "", "31059000": "",
    "08059001": "for religious purposes only",
    "08119080": "if tropical fruit",
    "14049090": "for religious purposes only",
    "19059010": "for religious purposes only",
    "19059090": "for religious purposes only",
    "20089921": "if Acai",
    "20093160": "if citrus juice (other than orange, grapefruit, lime)",
    "20098970": "if Coconut water or juice of acai",
    "20099040": "if Coconut water juice blends",
    "21069099": "if Acai preparations",
    "33012951": "for religious purposes only"
}

EXEMPT_CODES_232 = {
    "Sec 232 (Auto Parts)": "9903.94.06",
    "Sec 232 (MHDV/Buses)": "9903.74.11",
    "Sec 232 (Timber/Lumber)": "9903.76.04",
    "Sec 232 (Copper)": "9903.78.02",
    "Sec 232 (Semiconductors)": "9903.79.02",
    "Sec 232 (Steel)": "9903.81.92",
    "Sec 232 (Aluminum)": "9903.85.09"
}

PGA_DICTIONARY = {
    "EP1": ("EPA", "Ozone Depleting Substances", "May be Required"), "EP2": ("EPA", "Ozone Depleting Substances", "Required"),
    "EP3": ("EPA", "Vehicle and Engines", "May be Required"), "EP4": ("EPA", "Vehicle and Engines", "Required"),
    "EP5": ("EPA", "Pesticides", "May be Required"), "EP6": ("EPA", "Pesticides", "Required"),
    "EP7": ("EPA", "Toxic Substances Control Act", "May be Required"), "EP8": ("EPA", "Toxic Substances Control Act", "Required"),
    "EH1": ("EPA", "Hydrofluorocarbons", "May be Required"), "EH2": ("EPA", "Hydrofluorocarbons", "Required"),
    "FS3": ("FSIS", "Meat/Poultry/Egg Data", "May be Required"), "FS4": ("FSIS", "Meat/Poultry/Egg Data", "Required"),
    "NM1": ("NMF", "NOAA 370 Specific Data", "May be Required"), "NM2": ("NMF", "NOAA 370 Specific Data", "Required"),
    "NM3": ("NMF", "Antarctic Marine Living Resources", "May be Required"), "NM4": ("NMF", "Antarctic Marine Living Resources", "Required"),
    "NM5": ("NMF", "Highly Migratory Species", "May be Required"), "NM6": ("NMF", "Highly Migratory Species", "Required"),
    "NM8": ("NMF", "Seafood Import Monitoring Program", "Required"),
    "DT1": ("NHTSA", "DOT/NHTSA HS-7 Data", "May be Required"), "DT2": ("NHTSA", "DOT/NHTSA HS-7 Data", "Required"),
    "AL1": ("APHIS", "Lacey Act", "May be Required"), "AL2": ("APHIS", "Lacey Act", "Required"),
    "FD1": ("FDA", "FDA Data 801(a)", "May be Required"), "FD2": ("FDA", "FDA Data 801(a)", "Required"),
    "FD3": ("FDA", "FDA Prior Notice 801(m)", "May be Required"), "FD4": ("FDA", "FDA Prior Notice 801(m)", "Required"),
    "AM1": ("AMS", "Egg Products", "May be Required"), "AM2": ("AMS", "Shell Eggs", "Required"),
    "AM3": ("AMS", "Marketing Orders", "May be Required"), "AM4": ("AMS", "Marketing Orders", "Required"),
    "AM6": ("AMS", "Peanuts", "Required"), "AM7": ("AMS", "Organics", "May be Required"), "AM8": ("AMS", "Organics", "Required"),
    "TB1": ("TTB", "Alcohol/Tobacco", "May be Required"), "TB2": ("TTB", "Alcohol/Tobacco", "Required"), "TB3": ("TTB", "Alcohol/Tobacco", "May be Required"),
    "AQ1": ("APHIS", "Animal/Plant Health", "May be Required"), "AQ2": ("APHIS", "Animal/Plant Health", "Required"), "AQX": ("APHIS", "Animal/Plant Health (No Disclaim)", "May be Required"),
    "OM1": ("OMC", "Office of Marine Conservation", "May be Required"), "OM2": ("OMC", "Office of Marine Conservation", "Required"),
    "FW1": ("FWS", "Fish and Wildlife Service", "May be Required"), "FW2": ("FWS", "Fish and Wildlife Service", "Required"), "FW3": ("FWS", "Fish and Wildlife Service", "May be Required"),
    "DE1": ("DEA", "Drug Enforcement Administration", "May be Required")
}

# --- STEP 1: LOAD DATABASES ---
@st.cache_data
def load_csv(filename):
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename, dtype=str)
            df.columns = df.columns.str.strip()
            col_name = next((col for col in df.columns if 'HTS' in col.upper() or 'TARIFF' in col.upper()), df.columns[0])
            df['clean_hts'] = df[col_name].astype(str).str.replace('.', '', regex=False).str.strip()
            return df
        except: return None
    return None

@st.cache_data
def load_pga_data():
    if os.path.exists('hts_pga_report.csv'):
        try:
            df = pd.read_csv('hts_pga_report.csv', dtype=str)
            df.columns = df.columns.str.strip()
            col_name = next((col for col in df.columns if 'TARIFF' in col.upper() or 'HTS' in col.upper()), df.columns[0])
            df['clean_hts10'] = df[col_name].astype(str).str.replace(r'\.0$', '', regex=True).str.replace('.', '', regex=False).str.strip()
            df['clean_hts10'] = df['clean_hts10'].apply(lambda x: x.zfill(10) if x.isdigit() else x)
            return df
        except: return None
    return None

df = load_csv('htsdata.json')
if os.path.exists('htsdata.json'):
    with open('htsdata.json', 'r', encoding='utf-8') as f:
        df = pd.DataFrame(json.load(f))
        df['clean_htsno'] = df['htsno'].astype(str).str.replace('.', '', regex=False).str.strip()
        desc_clean = df['description'].astype(str).str.replace('\n', ' ').str.title()
        df['display_name'] = df['htsno'].astype(str) + " - " + desc_clean

df_301 = load_csv('section301_rates.csv')
df_301_exempt = load_csv('sec301_exemptions.csv')
df_232_steel = load_csv('sec232_steel.csv')
df_232_alum = load_csv('sec232_aluminum.csv')
df_232_copper = load_csv('sec232_copper.csv')
df_232_auto = load_csv('sec232_auto.csv')
df_232_timber = load_csv('sec232_timber.csv')
df_232_mhdv = load_csv('sec232_mhdv.csv')
df_232_semi = load_csv('sec232_semi.csv')
df_122 = load_csv('sec122_exemptions.csv')
df_adcvd = load_csv('adcvd_warnings.csv')
df_pga = load_pga_data()

def check_db_match(df_db, target_codes):
    if df_db is None or df_db.empty: return pd.DataFrame()
    match_mask = df_db['clean_hts'].apply(lambda x: any(t in re.findall(r'\d+', str(x).replace('.', '')) for t in target_codes if t))
    return df_db[match_mask]

# --- LAYOUT ---
left_col, right_col = st.columns([4, 6], gap="medium")

with left_col:
    st.subheader("Calculator", anchor=False)
    with st.container(border=True):
        
        # --- SINGLE BOX SEARCH ENGINE (CLEAN LEAF CODES ONLY) ---
        if df is not None and not df.empty:
            search_df = df[
                (~df['clean_htsno'].str.startswith(('98', '99'))) & 
                (~df['display_name'].str.contains('Goods Provided For', case=False, na=False)) &
                (~df['display_name'].str.contains('Articles Classifiable', case=False, na=False)) &
                (df['clean_htsno'].str.len() >= 8) # Filter out all the messy 4-digit headers
            ]
            
            selected_item = st.selectbox(
                "Product or HTS Code", 
                options=search_df['display_name'].tolist(), 
                index=None, 
                placeholder="Enter HTS Code (e.g. 3924.10.30.00)"
            )
            hts_input = selected_item.split(" - ")[0].strip() if selected_item else ""
        else:
            hts_input = st.text_input("Product or HTS Code", placeholder="Enter HTS Code (e.g. 3924.10.30.00)")
            
        c1, c2 = st.columns(2)
        value = c1.number_input("Cargo Value (USD)", min_value=0.0, value=10000.0, step=100.0)
        mode = c2.selectbox("Transport", ["Ocean", "Air", "Train", "Truck"])
        origin = st.selectbox("Country of Origin", COUNTRIES, index=14)

        clean_input = hts_input.replace('.', '').replace(' ', '').strip()
        target_codes = [clean_input[:10], clean_input[:8], clean_input[:6], clean_input[:4]]
        iso_code = origin.split(" - ")[0].strip()

        # --- SECTION 301 ---
        s301_rate = 0.0
        s301_code = "9903.88.03"
        claim_301 = "No"
        
        if iso_code == "CN" and clean_input:
            match_301_ex = check_db_match(df_301_exempt, target_codes)
            if not match_301_ex.empty:
                s301_desc = str(match_301_ex.iloc[0].get('Description', 'See USTR exclusions list')).strip()
                st.markdown("<div class='questionnaire-header'>🚨 Section 301 Exemption Check</div>", unsafe_allow_html=True)
                claim_301 = st.radio(f"**Exemption Found:** Is this product specifically: *{s301_desc}*?", ["No", "Yes"], index=0, horizontal=True)
                if claim_301 == "Yes": s301_code = "9903.88.69"

        # --- SECTION 232 ---
        s232_results = []
        if clean_input:
            def get_232_rate_precheck(db, default_rate, category_name, ch99_code):
                m = check_db_match(db, target_codes)
                if not m.empty:
                    r = default_rate
                    if category_name in ["Steel", "Aluminum", "Copper"]: r = 50.0
                    elif 'Rate' in m.columns:
                        try: r = float(m.iloc[0]['Rate'])
                        except: pass
                    return r, f"Sec 232 ({category_name})", ch99_code
                return 0.0, "", ""
            
            r_steel, l_steel, c_steel = get_232_rate_precheck(df_232_steel, 50.0, "Steel", "9903.81.90")
            r_alum, l_alum, c_alum = get_232_rate_precheck(df_232_alum, 50.0, "Aluminum", "9903.85.07")
            r_copper, l_copper, c_copper = get_232_rate_precheck(df_232_copper, 50.0, "Copper", "9903.78.01")
            r_auto, l_auto, c_auto = get_232_rate_precheck(df_232_auto, 25.0, "Auto Parts", "9903.94.05")
            r_semi, l_semi, c_semi = get_232_rate_precheck(df_232_semi, 25.0, "Semiconductors", "9903.79.01")
            
            m_timber = check_db_match(df_232_timber, target_codes)
            r_timber, l_timber, c_timber = 0.0, "", ""
            if not m_timber.empty:
                r_timber = float(m_timber.iloc[0].get('Rate', 10.0))
                c_timber = "9903.76.02" if clean_input.startswith("9401") else ("9903.76.03" if clean_input.startswith("9403") else "9903.76.01")
                l_timber = "Sec 232 (Timber/Lumber)"

            m_mhdv = check_db_match(df_232_mhdv, target_codes)
            r_mhdv, l_mhdv, c_mhdv = 0.0, "", ""
            if not m_mhdv.empty:
                r_mhdv = float(m_mhdv.iloc[0].get('Rate', 25.0))
                if clean_input.startswith("8702"): c_mhdv = "9903.74.02"
                elif clean_input.startswith(("8701", "8704", "8705", "8706", "8709")): c_mhdv = "9903.74.01"
                else: c_mhdv = "9903.74.08"
                l_mhdv = "Sec 232 (MHDV/Buses)"

            sec232_matches = []
            for r, l, c in [(r_copper, l_copper, c_copper), (r_steel, l_steel, c_steel), (r_auto, l_auto, c_auto), 
                            (r_mhdv, l_mhdv, c_mhdv), (r_semi, l_semi, c_semi), (r_alum, l_alum, c_alum), (r_timber, l_timber, c_timber)]:
                if r > 0: sec232_matches.append((r, l, c))

            if sec232_matches:
                st.markdown("<div class='questionnaire-header'>🏗️ Section 232 Applicability Check</div>", unsafe_allow_html=True)
                
                for idx, (r, l, c) in enumerate(sec232_matches):
                    ans = st.radio(f"Subject to {l} ({r}%)?", ["No", "Yes"], index=0, horizontal=True, key=f"s232_{idx}")
                    
                    is_split = False
                    metal_pct = 100.0
                    metal_type = ""
                    
                    if ans == "Yes" and any(m in l for m in ["Steel", "Aluminum", "Copper"]):
                        is_split = True
                        if "Steel" in l: metal_type = "Steel"
                        elif "Aluminum" in l: metal_type = "Aluminum"
                        elif "Copper" in l: metal_type = "Copper"
                        metal_pct = st.number_input(f"% of {metal_type} Content by Value", min_value=0.0, max_value=100.0, value=100.0, step=1.0, key=f"pct_{idx}")
                        
                    s232_results.append({
                        "label": l, "rate": r if ans == "Yes" else 0.0, "base_rate": r, 
                        "code": c if ans == "Yes" else EXEMPT_CODES_232.get(l, "EXEMPT"),
                        "is_subject": ans == "Yes", "is_split": is_split, "metal_pct": metal_pct, "metal_type": metal_type
                    })

        split_res = next((res for res in s232_results if res.get("is_split") and res.get("metal_pct", 100) < 100.0), None)
        do_split = split_res is not None
        has_s232 = any(res["is_subject"] for res in s232_results)

        # --- SECTION 122 ---
        claim_122 = "No"
        if clean_input:
            st.markdown("<div class='questionnaire-header'>🛡️ Section 122 Exemption Check</div>", unsafe_allow_html=True)
            if has_s232 and not do_split:
                st.success("✅ **Sec 122:** Automatically exempt due to Section 232 penalty.")
                claim_122 = "Yes"
            else:
                s122_eligible = False
                s122_scope, s122_desc = "", ""

                if clean_input[:10] in ANNEX_I_CODES or clean_input[:8] in ANNEX_I_CODES:
                    s122_eligible = True
                    s122_scope = "Annex I General Exemption"
                else:
                    match_122 = check_db_match(df_122, target_codes)
                    if not match_122.empty:
                        s122_eligible = True
                        s122_scope = str(match_122.iloc[0].get('Scope Limitations', match_122.iloc[0].get('Notes', ''))).strip()
                        s122_desc = str(match_122.iloc[0].get('Description', '')).strip()

                if s122_eligible:
                    if s122_scope.lower() in ['nan', '', 'none', 'annex i general exemption']:
                        st.success("✅ **Sec 122:** Unconditionally exempt per Annex I/II.")
                        claim_122 = "Yes"
                    else:
                        claim_122 = st.radio(f"**Sec 122:** Conditionally exempt IF: {s122_scope} / {s122_desc}. Do you meet this?", ["No", "Yes"], index=0, horizontal=True)
                else:
                    if do_split:
                        st.warning("⚠️ **Sec 122:** Non-metal portion subject to 15% Global Tariff.")
                    else:
                        st.info("No exemption found. Subject to 15% Global Tariff.")

    st.write("") 
    run_btn = st.button("🚀 Calculate Duties", type="primary", use_container_width=True)

with right_col:
    res_header1, res_header2 = st.columns([3, 1])
    res_header1.subheader("Results", anchor=False)
    
    if run_btn:
        if df is None: st.error("Database not found.")
        elif not hts_input: st.warning("Please search for an HTS code.")
        else:
            match = df[df['clean_htsno'] == clean_input]
            if not match.empty:
                row = match.iloc[0]
                country_name_only = origin.split(" - ")[1].strip() if " - " in origin else origin

                gen_rate_text = str(row.get('general', '')).replace('nan', '').strip()
                spl_rate_text = str(row.get('special', '')).replace('nan', '').strip()
                col2_rate_text = str(row.get('other', '')).replace('nan', '').strip()
                
                if not gen_rate_text and len(clean_input) == 10:
                    parent_match = df[df['clean_htsno'] == clean_input[:8]]
                    if not parent_match.empty:
                        parent_row = parent_match.iloc[0]
                        gen_rate_text = str(parent_row.get('general', '')).replace('nan', '').strip()
                        spl_rate_text = str(parent_row.get('special', '')).replace('nan', '').strip()
                        col2_rate_text = str(parent_row.get('other', '')).replace('nan', '').strip()

                gen_rate_text = gen_rate_text or "Free"
                spl_rate_text = spl_rate_text or "None"
                col2_rate_text = col2_rate_text or "None"
                
                active_rate_text = gen_rate_text
                duty_label = "Col 1 Duty"
                fta_applied = False
                
                if iso_code in COL2_COUNTRIES:
                    active_rate_text = col2_rate_text
                    duty_label = f"Col 2 Duty"
                else:
                    if spl_rate_text != "None" and "(" in spl_rate_text and ")" in spl_rate_text:
                        rate_part = spl_rate_text.split("(")[0].strip()
                        spi_part = spl_rate_text.split("(")[1].split(")")[0].strip()
                        indicators_in_hts = [s.strip() for s in spi_part.split(',')]
                        country_indicators = FTA_MAPPING.get(iso_code, [])
                        if any(indicator in indicators_in_hts for indicator in country_indicators):
                            active_rate_text = rate_part
                            duty_label = f"FTA Duty"
                            fta_applied = True
                
                duty_rate_display = str(active_rate_text).replace(' 1/', '').strip()
                parsed_rate = 0.0
                has_specific_duty = False

                if "Free" in duty_rate_display or duty_rate_display == "None" or duty_rate_display == "":
                    duty_rate_display = "Free"
                    parsed_rate = 0.0
                else:
                    if "¢" in duty_rate_display or "/" in duty_rate_display or "cents" in duty_rate_display.lower() or "+" in duty_rate_display:
                        has_specific_duty = True
                        
                    pct_match = re.search(r'(\d+(\.\d+)?)%', duty_rate_display)
                    if pct_match: parsed_rate = float(pct_match.group(1))
                    else:
                        if not has_specific_duty:
                            numbers = re.findall(r"[-+]?\d*\.\d+|\d+", duty_rate_display)
                            if numbers: parsed_rate = float(numbers[0])

                if parsed_rate == 0.0 and not has_specific_duty: duty_rate_display = "Free"

                if iso_code == "CN" and claim_301 == "No":
                    match_301 = check_db_match(df_301, target_codes)
                    if not match_301.empty:
                        if 's301_rate' in match_301.columns:
                            try: s301_rate = float(match_301.iloc[0]['s301_rate'])
                            except: s301_rate = 25.0
                        else: s301_rate = 25.0
                        if 'Heading' in match_301.columns: s301_code = str(match_301.iloc[0]['Heading'])
                    elif clean_input[:4] in ['9401', '9403']: s301_rate = 25.0

                for res in s232_results:
                    if res["is_subject"]:
                        if iso_code in ["GB", "JP", "AT", "BE", "FR", "DE", "IT", "ES", "NL", "SE"] and "Timber" in res["label"]:
                            if iso_code == "GB":
                                res["rate"] = min(res["rate"], 10.0)
                                res["base_rate"] = min(res["base_rate"], 10.0)
                            else:
                                res["rate"] = min(res["rate"], 15.0)
                                res["base_rate"] = min(res["base_rate"], 15.0)
                        elif iso_code == "GB" and any(m in res["label"] for m in ["Steel", "Aluminum", "Copper"]):
                            res["rate"] = 25.0
                            res["base_rate"] = 25.0
                            if "Steel" in res["label"]: res["code"] = "9903.81.97"
                            if "Aluminum" in res["label"]: res["code"] = "9903.85.14"

                base_s122_rate = 0.0 if claim_122 == "Yes" else 15.0

                if do_split:
                    metal_pct = split_res["metal_pct"]
                    metal_type = split_res["metal_type"]
                    metal_val = value * (metal_pct / 100.0)
                    non_metal_val = value - metal_val
                    
                    duty_metal = metal_val * (parsed_rate / 100.0)
                    duty_non_metal = non_metal_val * (parsed_rate / 100.0)
                    
                    s301_metal = metal_val * (s301_rate / 100.0) if claim_301 == "No" else 0.0
                    s301_non_metal = non_metal_val * (s301_rate / 100.0) if claim_301 == "No" else 0.0
                    
                    s122_non_metal_rate = base_s122_rate
                    s122_non_metal = non_metal_val * (s122_non_metal_rate / 100.0)
                    s122_metal_rate = 0.0
                    s122_metal = 0.0
                    
                    s232_metal = 0.0
                    s232_non_metal = 0.0
                    for r in s232_results:
                        if r["is_subject"]:
                            if r == split_res: s232_metal += metal_val * (r["rate"] / 100.0)
                            else:
                                s232_metal += metal_val * (r["rate"] / 100.0)
                                s232_non_metal += non_metal_val * (r["rate"] / 100.0)
                                
                    s232_total = s232_metal + s232_non_metal
                    
                    mpf_base = value * 0.003464
                    mpf = max(33.58, min(mpf_base, 651.50))
                    mpf_metal = mpf * (metal_val / value)
                    mpf_non_metal = mpf * (non_metal_val / value)
                    
                    hmf = (value * 0.00125) if mode == "Ocean" else 0.0
                    hmf_metal = hmf * (metal_val / value)
                    hmf_non_metal = hmf * (non_metal_val / value)
                    
                    s122_total = s122_metal + s122_non_metal
                    total_duties = duty_metal + duty_non_metal + s301_metal + s301_non_metal + s232_total + s122_total
                    total_duties_and_fees = total_duties + mpf + hmf
                    effective_rate = (total_duties_and_fees / value) * 100 if value > 0 else 0
                else:
                    duty = value * (parsed_rate / 100.0)
                    s301 = value * (s301_rate / 100.0) if claim_301 == "No" else 0.0
                    s232 = sum(value * (res["rate"] / 100.0) for res in s232_results)
                    s122_rate = 0.0 if has_s232 else base_s122_rate
                    s122_total = value * (s122_rate / 100.0)
                        
                    mpf_base = value * 0.003464
                    mpf = max(33.58, min(mpf_base, 651.50))
                    hmf = (value * 0.00125) if mode == "Ocean" else 0.0
                    total_duties = duty + s301 + s232 + s122_total
                    total_duties_and_fees = total_duties + mpf + hmf
                    effective_rate = (total_duties_and_fees / value) * 100 if value > 0 else 0

                dashboard_html = f"""
                <div class="results-cards-container">
                    <div class="flexport-card"><div class="duty-split-top" style="background-color: #f8faff;">
                        <div class="duty-rate-title">Effective Duty Rate</div><div class="duty-rate-value">{effective_rate:,.2f}<span style="font-size: 1.5rem;">%</span></div>
                    </div></div>
                    <div class="flexport-card"><div class="duty-split-top">
                        <div class="duty-rate-title">Total Duties & Fees</div><div class="duty-total-value">${total_duties_and_fees:,.2f}</div>
                    </div></div>
                </div>
                """
                st.markdown(dashboard_html.replace('\n', '').strip(), unsafe_allow_html=True)
                
                if has_specific_duty:
                    st.markdown("<div class='compact-alert alert-info'>ℹ️ <b>Specific Duty Detected:</b> Excludes weight-based portion (e.g., ¢/kg). Evaluate manually.</div>", unsafe_allow_html=True)

                def render_7501_line(line_num, line_label, line_val, duty_val, s301_val, s122_val, mpf_val, hmf_val, is_metal_line=False, split_res_ref=None):
                    html = f'<div class="line-item-box"><div class="line-item-header"><span>Line {line_num} {line_label}</span><span>Value: ${line_val:,.2f}</span></div>'
                    
                    if s301_rate > 0.0 or iso_code == "CN":
                        if claim_301 == "Yes": html += f'<div class="line-item-grid"><div class="col-code">{s301_code}</div><div class="col-desc"><span class="line-item-tag" style="background-color: #dcfce7; color: #166534;">Sec 301 (EXEMPT)</span></div><div class="col-rate">Free</div><div class="col-val">$0.00</div></div>'
                        elif s301_rate > 0.0: html += f'<div class="line-item-grid"><div class="col-code">{s301_code}</div><div class="col-desc"><span class="line-item-tag" style="background-color: #e0e7ff; color: #4f46e5;">Sec 301 China</span></div><div class="col-rate">{s301_rate}%</div><div class="col-val">${s301_val:,.2f}</div></div>'
                    
                    for res in s232_results:
                        if res == split_res_ref and not is_metal_line: continue
                        is_active_penalty = res["is_subject"]
                        if is_active_penalty:
                            penalty_amt = line_val * (res["base_rate"] / 100.0)
                            html += f'<div class="line-item-grid"><div class="col-code">{res["code"]}</div><div class="col-desc"><span class="line-item-tag" style="background-color: #e0e7ff; color: #4f46e5;">{res["label"]}</span></div><div class="col-rate">{res["base_rate"]}%</div><div class="col-val">${penalty_amt:,.2f}</div></div>'
                        else:
                            exempt_code = EXEMPT_CODES_232.get(res["label"], "EXEMPT")
                            html += f'<div class="line-item-grid"><div class="col-code">{exempt_code}</div><div class="col-desc"><span class="line-item-tag" style="background-color: #dcfce7; color: #166534;">{res["label"]} (EXEMPT)</span></div><div class="col-rate">Free</div><div class="col-val">$0.00</div></div>'
                    
                    if is_metal_line or (has_s232 and not do_split):
                        line_s122_rate = 0.0
                        line_s122_tag = "Sec 122 (EXEMPT via Sec 232)"
                        line_s122_color = "background-color: #dcfce7; color: #166534;"
                        line_s122_code = "9903.01.33"
                    else:
                        line_s122_rate = 0.0 if claim_122 == "Yes" else 15.0
                        line_s122_tag = "Sec 122 (EXEMPT)" if claim_122 == "Yes" else "Sec 122 Global Tariff"
                        line_s122_color = "background-color: #dcfce7; color: #166534;" if claim_122 == "Yes" else "background-color: #fee2e2; color: #e11d48;"
                        line_s122_code = "Sec 122"

                    s122_rate_display = "Free" if line_s122_rate == 0.0 else f"{line_s122_rate}%"
                    html += f'<div class="line-item-grid"><div class="col-code">{line_s122_code}</div><div class="col-desc"><span class="line-item-tag" style="{line_s122_color}">{line_s122_tag}</span></div><div class="col-rate">{s122_rate_display}</div><div class="col-val">${s122_val:,.2f}</div></div>'
                    
                    html += f'<div class="line-item-grid" style="margin-top: 8px; padding-top: 8px; border-top: 1px dashed #cbd5e1;"><div class="col-code">{clean_input}</div><div class="col-desc"><span class="line-item-tag" style="background-color: #f1f5f9; color: #475569;">Base Duty</span></div><div class="col-rate">{duty_rate_display}</div><div class="col-val">${duty_val:,.2f}</div></div>'
                    
                    mpf_rate_str = "0.3464%"
                    if mpf_base < 33.58: mpf_rate_str = "MIN"
                    elif mpf_base > 651.50: mpf_rate_str = "MAX"
                    html += f'<div class="line-item-grid"><div class="col-code">499</div><div class="col-desc"><span class="line-item-tag" style="background-color: #f8fafc; border: 1px solid #e2e8f0; color: #64748b;">Merchandise Processing</span></div><div class="col-rate">{mpf_rate_str}</div><div class="col-val">${mpf_val:,.2f}</div></div>'
                    
                    if hmf > 0: html += f'<div class="line-item-grid"><div class="col-code">501</div><div class="col-desc"><span class="line-item-tag" style="background-color: #f8fafc; border: 1px solid #e2e8f0; color: #64748b;">Harbor Maintenance</span></div><div class="col-rate">0.1250%</div><div class="col-val">${hmf_val:,.2f}</div></div>'
                    
                    html += "</div>"
                    return html

                with st.expander("Line Item Details", expanded=True):
                    final_html = ""
                    if do_split:
                        final_html += render_7501_line(1, f"(Non-{metal_type})", non_metal_val, duty_non_metal, s301_non_metal, s122_non_metal, mpf_non_metal, hmf_non_metal, False, split_res)
                        final_html += render_7501_line(2, f"({metal_type})", metal_val, duty_metal, s301_metal, s122_metal, mpf_metal, hmf_metal, True, split_res)
                    else:
                        final_html += render_7501_line(1, "", value, duty, s301, s122_total, mpf, hmf, False, None)
                        
                    st.markdown(final_html.replace('\n', '').strip(), unsafe_allow_html=True)
                    
                if fta_applied: 
                    st.markdown(f"<div class='fta-alert'><span>✅</span> <span><span style='text-transform: uppercase;'>FTA APPLIED:</span> {country_name_only} qualifies for special duties.</span></div>", unsafe_allow_html=True)

                compliance_alerts = []
                if df_adcvd is not None and not df_adcvd.empty:
                    risk_check = df_adcvd[(df_adcvd['hts_prefix'] == clean_input[:6]) & (df_adcvd['country'] == iso_code)]
                    if not risk_check.empty:
                        case_name = risk_check.iloc[0].get('case_desc', 'subject merchandise')
                        compliance_alerts.append(f"🚨 <b>AD/CVD RISK:</b> Imports of <b>{case_name}</b> from <b>{country_name_only}</b> are subject to punitive duties.")

                if df_pga is not None and not df_pga.empty:
                    pga_match = df_pga[df_pga['clean_hts10'] == clean_input[:10]]
                    if not pga_match.empty:
                        pga_row = pga_match.iloc[0]
                        for col_name_in_df in pga_row.index:
                            if 'tariff' in str(col_name_in_df).lower() or 'clean' in str(col_name_in_df).lower() or 'desc' in str(col_name_in_df).lower(): continue
                            val = str(pga_row[col_name_in_df]).strip().upper()
                            for code in re.split(r'[,\s]+', val):
                                code = code.strip()
                                if code in PGA_DICTIONARY:
                                    agency, desc, status = PGA_DICTIONARY[code]
                                    alert = f"📋 <b>{agency}</b> ({code}): {desc} - <b>{status.upper()}</b>"
                                    if alert not in compliance_alerts: compliance_alerts.append(alert)
                                elif re.match(r'^[A-Z]{2}[A-Z0-9]$', code) and code not in ['NAN', 'NON']:
                                    alert = f"📋 <b>{code}</b>: PGA Requirement Detected"
                                    if alert not in compliance_alerts: compliance_alerts.append(alert)

                if compliance_alerts:
                    st.markdown("<div style='font-weight: 600; color: #1e293b; margin-top: 15px; margin-bottom: 8px; font-size: 13.5px;'>⚖️ Compliance & Regulatory Checks</div>", unsafe_allow_html=True)
                    for alert in compliance_alerts:
                        if "🚨" in alert: 
                            st.markdown(f"<div class='compact-alert alert-danger'>{alert}</div>", unsafe_allow_html=True)
                        else: 
                            st.markdown(f"<div class='compact-alert alert-warning'>{alert}</div>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<div style='font-size: 13.5px;'>", unsafe_allow_html=True)
    st.subheader("System Databases")
    if df is not None: st.markdown("✅ **HTS Master:** loaded")
    st.markdown("---")
    st.caption("🚨 Section 301")
    if df_301 is not None: st.markdown(f"✅ Rules: {len(df_301):,}")
    if df_301_exempt is not None: st.markdown(f"✅ Exemptions: {len(df_301_exempt):,}")
    st.markdown("---")
    st.caption("🏗️ Section 232 Subsystems")
    if df_232_steel is not None: st.markdown(f"✅ Steel: {len(df_232_steel):,}")
    if df_232_alum is not None: st.markdown(f"✅ Aluminum: {len(df_232_alum):,}")
    if df_232_copper is not None: st.markdown(f"✅ Copper: {len(df_232_copper):,}")
    if df_232_auto is not None: st.markdown(f"✅ Auto Parts: {len(df_232_auto):,}")
    if df_232_timber is not None: st.markdown(f"✅ Timber/Lumber: {len(df_232_timber):,}")
    if df_232_mhdv is not None: st.markdown(f"✅ MHDV/Buses: {len(df_232_mhdv):,}")
    if df_232_semi is not None: st.markdown(f"✅ Semiconductors: {len(df_232_semi):,}")
    st.markdown("---")
    st.caption("⚖️ Compliance Databases")
    if df_pga is not None: st.markdown(f"✅ PGA Index: {len(df_pga):,}")
    if df_adcvd is not None: st.markdown(f"✅ AD/CVD Alerts: {len(df_adcvd):,}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    if st.button("🔄 Clear System Cache", use_container_width=True):
        st.cache_data.clear()
        st.rerun()