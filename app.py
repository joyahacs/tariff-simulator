import streamlit as st
import pandas as pd
import json
import os
import re
import io

# --- PAGE SETUP & CUSTOM CSS ---
st.set_page_config(page_title="Tariff Simulator PRO", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important; 
}

.block-container { padding-top: 2rem; padding-bottom: 2rem; }

.main-title { 
    font-size: 2.8rem; 
    font-weight: 800; 
    background: linear-gradient(90deg, #1e3a8a, #0ea5e9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 2px; 
    letter-spacing: -1px;
}
.sub-title {
    font-size: 1.05rem;
    color: #64748b;
    font-weight: 500;
    margin-bottom: 20px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* FLEXPORT RESULTS LAYOUT */
.results-cards-container {
    display: flex;
    gap: 20px;
    margin-bottom: 15px;
    align-items: stretch;
}
.flexport-card {
    flex: 1;
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* Duty Rate Card */
.duty-split-top {
    flex: 1;
    padding: 25px 20px;
    background-color: #f8faff;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.duty-split-bottom {
    flex: 1;
    padding: 25px 20px;
    background-color: #ffffff;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.duty-rate-title { font-size: 13px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
.duty-rate-value { font-size: 4rem; font-weight: 700; color: #6366f1; line-height: 1; margin: 0; }
.duty-total-value { font-size: 2.8rem; font-weight: 700; color: #0f172a; line-height: 1; margin: 0; }

/* Cost Breakdown Card */
.breakdown-inner { padding: 24px; display: flex; flex-direction: column; height: 100%; }
.breakdown-title { font-size: 13px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; }
.breakdown-row { display: flex; justify-content: space-between; font-size: 15px; color: #475569; margin-bottom: 15px; }
.breakdown-row:last-child { margin-bottom: 0; }
.breakdown-row-value { font-weight: 600; color: #1e293b; }

/* Line Items */
.line-item-box { background: #f8fafc; padding: 18px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #e2e8f0; }
.line-item-header { display: flex; justify-content: space-between; font-weight: 600; color: #1e293b; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0;}
.line-item-row { display: flex; justify-content: space-between; font-size: 14px; color: #475569; margin-bottom: 10px; align-items: center;}
.line-item-tag { padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 600; display: inline-block;}
.line-hts { text-decoration: underline; font-weight: 500; color: #334155; }
.line-val { font-weight: 600; color: #0f172a; }
</style>
""", unsafe_allow_html=True)

# Special Header
st.markdown('<div class="main-title">🌐 TradePro Tariff Simulator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Advanced Customs Duty & Compliance Engine</div>', unsafe_allow_html=True)

# SECTION 122 GLOBAL ALERT
st.error("🚨 **EXECUTIVE ORDER:** A **15% global tariff** under **Section 122** has been implemented for 150 days. This applies to all origins unless specifically exempted in Annex II.")
st.markdown("---")

# --- LIST OF ALL COUNTRIES (WITH ISO CODES) ---
COUNTRIES = [
    "AF - Afghanistan", "AL - Albania", "DZ - Algeria", "AD - Andorra", "AO - Angola", 
    "AG - Antigua and Barbuda", "AR - Argentina", "AM - Armenia", "AT - Austria", 
    "AU - Australia", "AZ - Azerbaijan", "BS - Bahamas", "BH - Bahrain", "BD - Bangladesh", 
    "BB - Barbados", "BY - Belarus", "BE - Belgium", "BZ - Belize", "BJ - Benin", 
    "BT - Bhutan", "BO - Bolivia", "BA - Bosnia and Herzegovina", "BW - Botswana", 
    "BR - Brazil", "BN - Brunei", "BG - Bulgaria", "BF - Burkina Faso", "BI - Burundi", 
    "CV - Cabo Verde", "KH - Cambodia", "CM - Cameroon", "CA - Canada", 
    "CF - Central African Republic", "TD - Chad", "CL - Chile", "CN - China", 
    "CO - Colombia", "KM - Comoros", "CR - Costa Rica", "HR - Croatia", "CU - Cuba", 
    "CY - Cyprus", "CZ - Czechia", "CD - Democratic Republic of the Congo", 
    "DK - Denmark", "DJ - Djibouti", "DM - Dominica", "DO - Dominican Republic", 
    "EC - Ecuador", "EG - Egypt", "SV - El Salvador", "GQ - Equatorial Guinea", 
    "ER - Eritrea", "EE - Estonia", "SZ - Eswatini", "ET - Ethiopia", "FJ - Fiji", 
    "FI - Finland", "FR - France", "GA - Gabon", "GM - Gambia", "GE - Georgia", 
    "DE - Germany", "GH - Ghana", "GR - Greece", "GD - Grenada", "GT - Guatemala", 
    "GN - Guinea", "GW - Guinea-Bissau", "GY - Guyana", "HT - Haiti", "HN - Honduras", 
    "HU - Hungary", "IS - Iceland", "IN - India", "ID - Indonesia", "IR - Iran", 
    "IQ - Iraq", "IE - Ireland", "IL - Israel", "IT - Italy", "JM - Jamaica", 
    "JP - Japan", "JO - Jordan", "KP - North Korea", "KR - South Korea", "KZ - Kazakhstan", 
    "KE - Kenya", "KI - Kiribati", "KW - Kuwait", "KG - Kyrgyzstan", "LA - Laos", 
    "LV - Latvia", "LB - Lebanon", "LS - Lesotho", "LR - Liberia", "LY - Libya", 
    "LI - Liechtenstein", "LT - Lithuania", "LU - Luxembourg", "MG - Madagascar", 
    "MW - Malawi", "MY - Malaysia", "MV - Maldives", "ML - Mali", "MT - Malta", 
    "MH - Marshall Islands", "MR - Mauritania", "MU - Mauritius", "MX - Mexico", 
    "FM - Micronesia", "MD - Moldova", "MC - Monaco", "MN - Mongolia", "ME - Montenegro", 
    "MA - Morocco", "MZ - Mozambique", "MM - Myanmar", "NA - Namibia", "NR - Nauru", 
    "NP - Nepal", "NL - Netherlands", "NZ - New Zealand", "NI - Nicaragua", "NE - Niger", 
    "NG - Nigeria", "MK - North Macedonia", "NO - Norway", "OM - Oman", "PK - Pakistan", 
    "PW - Palau", "PA - Panama", "PG - Papua New Guinea", "PY - Paraguay", "PE - Peru", 
    "PH - Philippines", "PL - Poland", "PT - Portugal", "QA - Qatar", "RO - Romania", 
    "RU - Russia", "RW - Rwanda", "KN - Saint Kitts and Nevis", "LC - Saint Lucia", 
    "VC - Saint Vincent and the Grenadines", "WS - Samoa", "SM - San Marino", 
    "ST - Sao Tome and Principe", "SA - Saudi Arabia", "SN - Senegal", "RS - Serbia", 
    "SC - Seychelles", "SL - Sierra Leone", "SG - Singapore", "SK - Slovakia", 
    "SI - Slovenia", "SB - Solomon Islands", "SO - Somalia", "ZA - South Africa", 
    "SS - South Sudan", "ES - Spain", "LK - Sri Lanka", "SD - Sudan", "SR - Suriname", 
    "SE - Sweden", "CH - Switzerland", "SY - Syria", "TW - Taiwan", "TJ - Tajikistan", 
    "TZ - Tanzania", "TH - Thailand", "TL - Timor-Leste", "TG - Togo", "TO - Tonga", 
    "TT - Trinidad and Tobago", "TN - Tunisia", "TR - Turkey", "TM - Turkmenistan", 
    "TV - Tuvalu", "UG - Uganda", "UA - Ukraine", "AE - United Arab Emirates", 
    "GB - United Kingdom", "US - United States", "UY - Uruguay", "UZ - Uzbekistan", 
    "VU - Vanuatu", "VE - Venezuela", "VN - Vietnam", "YE - Yemen", "ZM - Zambia", "ZW - Zimbabwe"
]

# --- HARDCODED ANNEX I MASTER LIST (Never breaks) ---
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

# --- HTS SPECIAL PROGRAM INDICATORS (FTA MAPPING) ---
FTA_MAPPING = {
    "AU": ["AU"], "BH": ["BH"], "CL": ["CL"], "CO": ["CO"], "IL": ["IL"], 
    "JO": ["JO"], "JP": ["JP"], "KR": ["KR"], "MA": ["MA"], "OM": ["OM"], 
    "PA": ["PA"], "PE": ["PE"], "SG": ["SG"], "CA": ["S", "S+"], "MX": ["S", "S+"], 
    "CR": ["P", "P+"], "DO": ["P", "P+"], "SV": ["P", "P+"], "GT": ["P", "P+"], 
    "HN": ["P", "P+"], "NI": ["P", "P+"], "ZA": ["D"], "NG": ["D"], "KE": ["D"], 
    "GH": ["D"]
}
COL2_COUNTRIES = ["CU", "KP", "RU", "BY"]

# --- SECTION 232 RULES ---
S232_EXEMPTIONS = {
    "Steel": ["CA", "MX", "BR", "AR", "KR", "UA"], "Steel-Derivative": ["CA", "MX"], 
    "Aluminum": ["CA", "MX", "AR"], "Aluminum-Derivative": ["CA", "MX"], 
    "Auto-MHDV": ["CA", "MX"], "Buses": ["CA", "MX"], "Copper": [], 
    "Semiconductors": [], "Wood-Lumber": [], "Wood-Furniture/Cabinets": []
}

EU_COUNTRIES = ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"]
S232_RULES = {
    "Wood-Furniture/Cabinets": { "DEFAULT": (25.0, "9903.76.02"), "GB": (10.0, "9903.76.20"), "JP": (15.0, "9903.76.21"), "EU": (15.0, "9903.76.22") },
    "Wood-Lumber": { "DEFAULT": (10.0, "9903.76.01"), "GB": (10.0, "9903.76.20"), "JP": (15.0, "9903.76.21"), "EU": (15.0, "9903.76.22") },
    "Auto-MHDV": { "DEFAULT": (25.0, "9903.94.07"), "GB": (10.0, "9903.94.33"), "JP": (15.0, "9903.94.54"), "EU": (15.0, "9903.94.44") },
    "Buses": { "DEFAULT": (10.0, "9903.74.02") },
    "Steel": { "DEFAULT": (25.0, "9903.81.87"), "GB": (25.0, "9903.81.94") },
    "Steel-Derivative": { "DEFAULT": (50.0, "9903.81.90"), "GB": (25.0, "9903.81.97") },
    "Aluminum": { "DEFAULT": (10.0, "9903.85.02"), "GB": (10.0, "9903.85.12") },
    "Aluminum-Derivative": { "DEFAULT": (50.0, "9903.85.07"), "GB": (25.0, "9903.85.14") },
    "Copper": { "DEFAULT": (50.0, "9903.78.01") },
    "Semiconductors": { "DEFAULT": (25.0, "9903.79.01") }
}

# --- PGA DICTIONARY MAP ---
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

# --- STEP 1: LOAD DATA ---
JSON_FILENAME = 'htsdata.json' 
S301_FILENAME = 'section301_rates.csv'
S232_FILENAME = 'section232_rates.csv'
ADCVD_FILENAME = 'adcvd_warnings.csv'
PGA_FILENAME = 'hts_pga_report.csv'
S122_FILENAME = 'sec122_exemptions.csv'

@st.cache_data
def load_hts_data():
    if os.path.exists(JSON_FILENAME):
        try:
            with open(JSON_FILENAME, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            df['clean_htsno'] = df['htsno'].astype(str).str.replace('.', '', regex=False).str.strip()
            desc_clean = df['description'].astype(str).str.replace('\n', ' ').str.title()
            df['display_name'] = df['htsno'].astype(str) + " - " + desc_clean
            return df
        except:
            return None
    return None

@st.cache_data
def load_301_data():
    if os.path.exists(S301_FILENAME): return pd.read_csv(S301_FILENAME, dtype={'hts8': str})
    return pd.DataFrame({'hts8': [], 's301_rate': []})

@st.cache_data
def load_232_data():
    if os.path.exists(S232_FILENAME): return pd.read_csv(S232_FILENAME, dtype={'hts8': str})
    return pd.DataFrame({'hts8': [], 's232_rate': [], 'category': []})

@st.cache_data
def load_adcvd_data():
    if os.path.exists(ADCVD_FILENAME): return pd.read_csv(ADCVD_FILENAME, dtype={'hts_prefix': str, 'country': str})
    return pd.DataFrame({'hts_prefix': [], 'country': [], 'case_desc': []})

@st.cache_data
def load_pga_data():
    if os.path.exists(PGA_FILENAME):
        df = pd.read_csv(PGA_FILENAME)
        df.columns = df.columns.str.strip()
        col_name = 'Tariff Number' if 'Tariff Number' in df.columns else df.columns[0]
        df['clean_hts10'] = df[col_name].astype(str).str.replace(r'\.0$', '', regex=True).str.replace('.', '', regex=False).str.strip()
        df['clean_hts10'] = df['clean_hts10'].apply(lambda x: x.zfill(10) if x.isdigit() else x)
        return df
    return None

@st.cache_data
def load_122_data():
    if os.path.exists(S122_FILENAME):
        try:
            df = pd.read_csv(S122_FILENAME)
            df.columns = df.columns.str.strip()
            col_name = 'HTSUS' if 'HTSUS' in df.columns else df.columns[0]
            df['clean_hts'] = df[col_name].astype(str).str.replace('.', '', regex=False).str.strip()
            return df
        except:
            return None
    return None

df = load_hts_data()
df_301 = load_301_data()
df_232 = load_232_data()
df_adcvd = load_adcvd_data()
df_pga = load_pga_data()
df_122 = load_122_data()

# --- LAYOUT (LEFT 40%, RIGHT 60%) ---
left_col, right_col = st.columns([4, 6], gap="large")

with left_col:
    st.subheader("Calculator")
    with st.container(border=True):
        if df is not None and not df.empty:
            # Filter out Chapter 98/99 AND hide those long conditional descriptions
            search_df = df[
                (~df['clean_htsno'].str.startswith(('98', '99'))) & 
                (~df['display_name'].str.contains('Goods Provided For In Subheading', case=False, na=False)) &
                (~df['display_name'].str.contains('Articles Classifiable In Subheadings', case=False, na=False)) &
                (~df['display_name'].str.contains('Articles Containing Over', case=False, na=False))
            ]
            
            selected_item = st.selectbox(
                "Product or HTS Code", 
                options=search_df['display_name'].tolist(),
                index=None,
                placeholder="Search by product name or HTS code..."
            )
            hts_input = selected_item.split(" - ")[0].strip() if selected_item else ""
        else:
            hts_input = st.text_input("Product or HTS Code", placeholder="e.g. 8712.00.3500")
            
        value = st.number_input("Cargo Value (USD)", min_value=0.0, value=10000.0, step=100.0)

        try:
            default_country_index = COUNTRIES.index("CN - China")
        except ValueError:
            default_country_index = 0
            
        origin = st.selectbox("Country of Origin", COUNTRIES, index=default_country_index)
        mode = st.selectbox("Mode of Transport", ["Ocean", "Air", "Train", "Truck"])

        clean_input = hts_input.replace('.', '').replace(' ', '').strip()
        hts10_input = clean_input[:10]
        hts8_input = clean_input[:8] 
        hts6_input = clean_input[:6]
        hts4_input = clean_input[:4]

        # --- SECTION 232 SPLIT LOGIC ---
        is_split_tariff = False
        tariff_cat = ""
        metal_type = ""

        if clean_input and df_232 is not None and not df_232.empty:
            match_232 = df_232[df_232['hts8'] == hts10_input]
            if match_232.empty: match_232 = df_232[df_232['hts8'] == hts8_input]
            if match_232.empty: match_232 = df_232[df_232['hts8'] == hts6_input]
            if match_232.empty: match_232 = df_232[df_232['hts8'] == hts4_input]

            if not match_232.empty:
                cat = str(match_232.iloc[0]['category'])
                if "Derivative" in cat or cat == "Copper":
                    is_split_tariff = True
                    tariff_cat = cat
                    if "Steel" in cat: metal_type = "Steel"
                    elif "Aluminum" in cat: metal_type = "Aluminum"
                    elif "Copper" in cat: metal_type = "Copper"

        subject_to_232 = "No"
        metal_pct = 100.0

        if is_split_tariff:
            st.markdown("---")
            st.caption(f"**Section 232 Value Split Required ({tariff_cat})**")
            dq_col1, dq_col2 = st.columns(2)
            with dq_col1:
                subject_to_232 = st.selectbox(f"Subject to Sec 232 {metal_type} tariffs?", ["Yes", "No"], index=0)
            with dq_col2:
                if subject_to_232 == "Yes":
                    metal_pct = st.number_input(f"% of {metal_type} Content by Value", min_value=0.0, max_value=100.0, value=100.0, step=1.0)
                else:
                    metal_pct = 100.0

        # --- SECTION 122 EXEMPTION QUESTIONNAIRE (BULLETPROOF) ---
        s122_eligible = False
        s122_scope = ""
        s122_desc = ""

        if clean_input:
            # 1. Check Hardcoded Annex I list first (Bypasses missing CSV data completely)
            if hts10_input in ANNEX_I_CODES:
                s122_eligible = True
                s122_scope = ANNEX_I_CODES[hts10_input]
                s122_desc = "Annex I General Exemption"
            elif hts8_input in ANNEX_I_CODES:
                s122_eligible = True
                s122_scope = ANNEX_I_CODES[hts8_input]
                s122_desc = "Annex I General Exemption"
            elif hts6_input in ANNEX_I_CODES:
                s122_eligible = True
                s122_scope = ANNEX_I_CODES[hts6_input]
                s122_desc = "Annex I General Exemption"
            
            # 2. Check Annex II CSV
            elif df_122 is not None and not df_122.empty:
                target_codes = [c for c in [hts10_input, hts8_input, hts6_input, hts4_input] if c]
                
                def check_s122_match(val):
                    v_str = str(val)
                    if v_str.endswith('.0'): v_str = v_str[:-2]
                    csv_codes = re.findall(r'\d+', v_str.replace('.', ''))
                    return any(t in csv_codes for t in target_codes)
                    
                match_mask = df_122['clean_hts'].apply(check_s122_match)
                match_122 = df_122[match_mask]
                
                if not match_122.empty:
                    s122_eligible = True
                    if 'Scope Limitations' in match_122.columns:
                        s122_scope = str(match_122.iloc[0]['Scope Limitations']).strip()
                    elif 'Notes' in match_122.columns:
                        s122_scope = str(match_122.iloc[0]['Notes']).strip()
                    
                    if 'Description' in match_122.columns:
                        s122_desc = str(match_122.iloc[0]['Description']).strip()

        claim_122 = "No"
        if s122_eligible:
            st.markdown("---")
            st.caption("**🛡️ Section 122 Global Tariff Exemption**")
            
            if s122_scope.lower() == 'pharma':
                st.info("This item is conditionally exempt from Sec 122 IF used for non-patented pharmaceutical applications.")
                claim_122 = st.selectbox("Claim Pharma Exemption?", ["No", "Yes"], index=0)
            elif s122_scope.lower() == 'aircraft':
                st.info("This item is conditionally exempt from Sec 122 IF used for civil aircraft parts/components.")
                claim_122 = st.selectbox("Claim Civil Aircraft Exemption?", ["No", "Yes"], index=0)
            elif s122_scope.lower() == 'ex' or 'ex ' in s122_scope.lower() or 'addition' in s122_scope.lower():
                st.info(f"This item is conditionally exempt from Sec 122 IF it exactly matches: {s122_desc}")
                claim_122 = st.selectbox("Claim Specific Product Exemption?", ["No", "Yes"], index=0)
            elif s122_scope.lower() == 'nan' or s122_scope == '' or s122_scope.lower() == 'none':
                st.success("This HTS code is unconditionally exempt from the Section 122 Global Tariff per Annex I/II.")
                claim_122 = "Yes"
            else:
                st.info(f"This item is conditionally exempt from Sec 122 under limitation: {s122_scope}")
                claim_122 = st.selectbox("Do you meet this condition?", ["No", "Yes"], index=0)

    st.write("") 
    run_btn = st.button("🚀 Calculate Duties", type="primary", use_container_width=True)

with right_col:
    res_header1, res_header2 = st.columns([3, 1])
    res_header1.subheader("Results")
    
    if run_btn:
        if df is None:
            st.error("HTS Database not found.")
        elif not hts_input:
            st.warning("Please search for an HTS code to begin.")
        else:
            match = df[df['clean_htsno'] == clean_input]
            
            if not match.empty:
                row = match.iloc[0]
                iso_code = origin.split(" - ")[0].strip()
                country_name_only = origin.split(" - ")[1].strip() if " - " in origin else origin

                # --- 1. BASE RATE ---
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
                    if pct_match:
                        parsed_rate = float(pct_match.group(1))
                    else:
                        if not has_specific_duty:
                            numbers = re.findall(r"[-+]?\d*\.\d+|\d+", duty_rate_display)
                            if numbers: parsed_rate = float(numbers[0])

                # --- 2. SEC 301 ---
                s301_rate = 0.0
                if iso_code == "CN":
                    match_301 = df_301[df_301['hts8'] == hts10_input]
                    if match_301.empty: match_301 = df_301[df_301['hts8'] == hts8_input]
                    if match_301.empty: match_301 = df_301[df_301['hts8'] == hts6_input]

                    if not match_301.empty: s301_rate = float(match_301.iloc[0]['s301_rate'])
                    elif hts4_input in ['9401', '9403']: s301_rate = 25.0

                # --- 3. SEC 232 ---
                s232_rate = 0.0
                s232_heading = ""
                s232_label = f"Section 232 ({country_name_only})"
                if not match_232.empty:
                    s232_category = str(match_232.iloc[0]['category'])
                    exempt_list = S232_EXEMPTIONS.get(s232_category, [])
                    if iso_code not in exempt_list and not (is_split_tariff and subject_to_232 == "No"):
                        cat_rules = S232_RULES.get(s232_category, {"DEFAULT": (25.0, "9903.XX.XX")})
                        if iso_code in cat_rules: s232_rate, s232_heading = cat_rules[iso_code]
                        elif iso_code in EU_COUNTRIES and "EU" in cat_rules: s232_rate, s232_heading = cat_rules["EU"]
                        else: s232_rate, s232_heading = cat_rules["DEFAULT"]

                # --- 4. SEC 122 (Global Temporary Tariff) ---
                s122_rate = 15.0
                s122_tag_label = "Sec 122 Global Tariff"
                s122_tag_color = "background-color: #fee2e2; color: #e11d48;" # Red
                
                if claim_122 == "Yes":
                    s122_rate = 0.0
                    s122_tag_label = "Sec 122 (EXEMPT)"
                    s122_tag_color = "background-color: #dcfce7; color: #166534;" # Green

                # --- 5. MATH ---
                duty, s301, s232, s122 = 0.0, 0.0, 0.0, 0.0
                do_split = is_split_tariff and subject_to_232 == "Yes" and s232_rate > 0.0 and metal_pct < 100.0
                
                if do_split:
                    metal_value = value * (metal_pct / 100.0)
                    non_metal_value = value - metal_value
                    
                    duty_non_metal = non_metal_value * (parsed_rate / 100.0)
                    s301_non_metal = non_metal_value * (s301_rate / 100.0)
                    s122_non_metal = non_metal_value * (s122_rate / 100.0)
                    
                    duty_metal = metal_value * (parsed_rate / 100.0)
                    s301_metal = metal_value * (s301_rate / 100.0)
                    s232_metal = metal_value * (s232_rate / 100.0)
                    s122_metal = metal_value * (s122_rate / 100.0)
                    
                    duty = duty_non_metal + duty_metal
                    s301 = s301_non_metal + s301_metal
                    s232 = s232_metal
                    s122 = s122_non_metal + s122_metal
                else:
                    duty = value * (parsed_rate / 100.0)
                    s301 = value * (s301_rate / 100.0)
                    s232 = value * (s232_rate / 100.0)
                    s122 = value * (s122_rate / 100.0)
                    
                mpf = max(33.58, min(value * 0.003464, 651.50))
                hmf = (value * 0.00125) if mode == "Ocean" else 0.0
                total_duties = duty + s301 + s232 + s122
                total_duties_and_fees = total_duties + mpf + hmf
                effective_rate = (total_duties_and_fees / value) * 100 if value > 0 else 0

                # Export Button Integration
                csv_buffer = io.StringIO()
                csv_buffer.write(f"Tariff Simulation\nHTS:,{clean_input}\nOrigin:,{origin}\nValue:,${value:,.2f}\nLanded:,${total_duties_and_fees + value:,.2f}\n")
                with res_header2:
                    st.download_button("📩 Export CSV", data=csv_buffer.getvalue(), file_name=f"Tariff_{clean_input}_{iso_code}.csv", mime="text/csv", use_container_width=True)

                # --- 40/60 UI DASHBOARD ---
                dashboard_html = f"""
                <div class="results-cards-container">
                    <div class="flexport-card">
                        <div class="duty-split-top">
                            <div class="duty-rate-title">Effective Duty Rate</div>
                            <div class="duty-rate-value">{effective_rate:,.2f}<span style="font-size: 2rem;">%</span></div>
                        </div>
                        <div class="duty-split-bottom">
                            <div class="duty-rate-title">Total Duties & Fees</div>
                            <div class="duty-total-value">${total_duties_and_fees:,.2f}</div>
                        </div>
                    </div>
                    <div class="flexport-card">
                        <div class="breakdown-inner">
                            <div class="breakdown-title">Cost Breakdown</div>
                            <div class="breakdown-row"><span>Cargo Value</span><span class="breakdown-row-value">${value:,.2f}</span></div>
                            <div class="breakdown-row"><span>Total Duties</span><span class="breakdown-row-value">${total_duties:,.2f}</span></div>
                            <div class="breakdown-row"><span style="font-weight: 600;">Sec 122 Global (15%)</span><span class="breakdown-row-value">${s122:,.2f}</span></div>
                            <div class="breakdown-row"><span>Harbor Maintenance (HMF)</span><span class="breakdown-row-value">${hmf:,.2f}</span></div>
                            <div class="breakdown-row"><span>Merchandise Proc. (MPF)</span><span class="breakdown-row-value">${mpf:,.2f}</span></div>
                        </div>
                    </div>
                </div>
                """
                st.markdown(dashboard_html.replace('\n', '').strip(), unsafe_allow_html=True)
                
                # Compound Rate Warning
                if has_specific_duty:
                    st.info("ℹ️ **Specific Duty Detected:** This HTS code contains a quantity/weight-based duty rate (e.g., ¢/kg) in addition to a percentage. Because this simulator evaluates by *value*, the specific portion is excluded from the automated total. Please factor weight-based duties manually.")

                # --- LINE ITEMS ACCORDION ---
                with st.expander("Line Item Details", expanded=True):
                    line_html = ""
                    if do_split:
                        line_html += f"""
                        <div class="line-item-box">
                            <div class="line-item-header"><span>Line 1 (Non-{metal_type})</span><span>Value: ${non_metal_value:,.2f}</span></div>
                            <div class="line-item-row"><span class="line-hts">{clean_input}</span><span>{duty_rate_display}</span><span class="line-val">${duty_non_metal:,.2f}</span></div>
                        """
                        if iso_code == "CN":
                            line_html += f'<div class="line-item-row"><span><span class="line-hts">9903.88.03</span><span class="line-item-tag" style="margin-left: 10px; background-color: #e0e7ff; color: #4f46e5;">Sec 301 China</span></span><span>{s301_rate}%</span><span class="line-val">${s301_non_metal:,.2f}</span></div>'
                        line_html += f'<div class="line-item-row"><span><span class="line-hts">Sec 122</span><span class="line-item-tag" style="margin-left: 10px; {s122_tag_color}">{s122_tag_label}</span></span><span>{s122_rate}%</span><span class="line-val">${s122_non_metal:,.2f}</span></div>'
                        line_html += "</div>"
                        
                        line_html += f"""
                        <div class="line-item-box">
                            <div class="line-item-header"><span>Line 2 ({metal_type})</span><span>Value: ${metal_value:,.2f}</span></div>
                            <div class="line-item-row"><span class="line-hts">{clean_input}</span><span>{duty_rate_display}</span><span class="line-val">${duty_metal:,.2f}</span></div>
                        """
                        if iso_code == "CN":
                            line_html += f'<div class="line-item-row"><span><span class="line-hts">9903.88.03</span><span class="line-item-tag" style="margin-left: 10px; background-color: #e0e7ff; color: #4f46e5;">Sec 301 China</span></span><span>{s301_rate}%</span><span class="line-val">${s301_metal:,.2f}</span></div>'
                        line_html += f'<div class="line-item-row"><span><span class="line-hts">{s232_heading}</span><span class="line-item-tag" style="margin-left: 10px; background-color: #e0e7ff; color: #4f46e5;">Sec 232 Penalty</span></span><span>{s232_rate}%</span><span class="line-val">${s232_metal:,.2f}</span></div>'
                        line_html += f'<div class="line-item-row"><span><span class="line-hts">Sec 122</span><span class="line-item-tag" style="margin-left: 10px; {s122_tag_color}">{s122_tag_label}</span></span><span>{s122_rate}%</span><span class="line-val">${s122_metal:,.2f}</span></div>'
                        line_html += "</div>"
                    else:
                        line_html += f"""
                        <div class="line-item-box">
                            <div class="line-item-header"><span>Line 1</span><span>Value: ${value:,.2f}</span></div>
                            <div class="line-item-row"><span class="line-hts">{clean_input}</span><span>{duty_rate_display}</span><span class="line-val">${duty:,.2f}</span></div>
                        """
                        if iso_code == "CN":
                            line_html += f'<div class="line-item-row"><span><span class="line-hts">9903.88.03</span><span class="line-item-tag" style="margin-left: 10px; background-color: #e0e7ff; color: #4f46e5;">Sec 301 China</span></span><span>{s301_rate}%</span><span class="line-val">${s301:,.2f}</span></div>'
                        if s232_rate > 0.0:
                            line_html += f'<div class="line-item-row"><span><span class="line-hts">{s232_heading}</span><span class="line-item-tag" style="margin-left: 10px; background-color: #e0e7ff; color: #4f46e5;">Sec 232 Penalty</span></span><span>{s232_rate}%</span><span class="line-val">${s232:,.2f}</span></div>'
                        
                        # Add Section 122 Line Item
                        line_html += f'<div class="line-item-row"><span><span class="line-hts">Sec 122</span><span class="line-item-tag" style="margin-left: 10px; {s122_tag_color}">{s122_tag_label}</span></span><span>{s122_rate}%</span><span class="line-val">${s122:,.2f}</span></div>'
                        line_html += "</div>"

                    st.markdown(line_html.replace('\n', '').strip(), unsafe_allow_html=True)
                    if fta_applied: st.caption(f"✅ **FTA Applied:** {country_name_only} qualifies for special duties.")

                # --- COMPLIANCE BLOCK ---
                compliance_alerts = []
                if df_adcvd is not None and not df_adcvd.empty:
                    risk_check = df_adcvd[(df_adcvd['hts_prefix'] == hts6_input) & (df_adcvd['country'] == iso_code)]
                    if not risk_check.empty:
                        case_name = risk_check.iloc[0]['case_desc']
                        compliance_alerts.append(f"🚨 **CRITICAL AD/CVD RISK:** Imports of **{case_name}** from **{country_name_only}** are subject to punitive duties.")

                if df_pga is not None and not df_pga.empty:
                    pga_match = df_pga[df_pga['clean_hts10'] == hts10_input]
                    if not pga_match.empty:
                        pga_row = pga_match.iloc[0]
                        for col_name_in_df in pga_row.index:
                            if 'tariff' in str(col_name_in_df).lower() or 'clean' in str(col_name_in_df).lower() or 'desc' in str(col_name_in_df).lower(): continue
                            val = str(pga_row[col_name_in_df]).strip().upper()
                            for code in re.split(r'[,\s]+', val):
                                code = code.strip()
                                if code in PGA_DICTIONARY:
                                    agency, desc, status = PGA_DICTIONARY[code]
                                    alert = f"📋 **{agency}** ({code}): {desc} - **{status.upper()}**"
                                    if alert not in compliance_alerts: compliance_alerts.append(alert)
                                elif re.match(r'^[A-Z]{2}[A-Z0-9]$', code) and code not in ['NAN', 'NON']:
                                    alert = f"📋 **{code}**: PGA Requirement Detected"
                                    if alert not in compliance_alerts: compliance_alerts.append(alert)

                if compliance_alerts:
                    st.write("")
                    with st.container(border=True):
                        st.markdown("<div style='font-weight: 600; color: #1e293b; margin-bottom: 10px;'>⚖️ Compliance & Regulatory Checks</div>", unsafe_allow_html=True)
                        for alert in compliance_alerts:
                            if "🚨" in alert: st.error(alert)
                            else: st.warning(alert)
            else:
                st.error(f"❌ HTS Code '{clean_input}' not found in the official database.")
    else:
        with st.container(border=True):
            st.markdown("<div style='text-align: center; color: #718096; padding: 40px 0;'>🔍 Enter shipment details on the left and click Calculate to see results.</div>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("System Databases")
    if df is not None: st.markdown("✅ **HTS Master:** loaded")
    if not df_301.empty: st.markdown(f"✅ **Sec 301:** {len(df_301):,} rules")
    if not df_232.empty: st.markdown(f"✅ **Sec 232:** {len(df_232):,} rules")
    if not df_adcvd.empty: st.markdown(f"✅ **AD/CVD:** {len(df_adcvd):,} alerts")
    
    if df_pga is not None: st.markdown(f"✅ **PGA Index:** {len(df_pga):,} items")
    else: st.markdown("❌ **PGA Index:** Missing CSV")
        
    if df_122 is not None: st.markdown(f"✅ **Sec 122 Exemptions:** 135 (Annex I) + {len(df_122):,} (Annex II)")
    else: st.markdown("⚠️ **Sec 122 Exemptions:** Missing sec122_exemptions.csv")
        
    st.divider()
    if st.button("🔄 Clear System Cache", use_container_width=True):
        st.cache_data.clear()
        st.rerun()