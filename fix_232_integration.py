import os

file_path = r'c:\Users\jiafe\.gemini\antigravity\scratch\us-tariffs-simulator\app.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_marker = "# --- SECTION 232 METAL ARTICLES (MASTER REBUILD) ---"
end_marker = "        has_s232 = any(res[\"is_subject\"] for res in s232_results)"

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if start_marker in line:
        start_idx = i
    if end_marker in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_logic = """        # --- SECTION 232 (FULL SUITE) ---
        s232_results = []
        if clean_input:
            # 1. SPECIAL CATEGORY PRE-CHECKS (Auto, Semi, Timber, MHDV)
            def get_232_rate_precheck(db, default_rate, category_name, ch99_code):
                m = check_db_match(db, clean_input)
                if not m.empty:
                    r = default_rate
                    if 'Rate' in m.columns:
                        try: r = float(m.iloc[0]['Rate'])
                        except: pass
                    return r, f"Sec 232 ({category_name})", ch99_code
                return 0.0, "", ""
            
            check_list = [
                get_232_rate_precheck(df_232_auto, 25.0, "Auto Parts", "9903.94.05"),
                get_232_rate_precheck(df_232_semi, 25.0, "Semiconductors", "9903.79.01")
            ]
            
            m_timber = check_db_match(df_232_timber, clean_input)
            if not m_timber.empty:
                r_timber = float(m_timber.iloc[0].get('Rate', 10.0))
                c_timber = "9903.76.02" if clean_input.startswith("9401") else ("9903.76.03" if clean_input.startswith("9403") else "9903.76.01")
                check_list.append((r_timber, "Sec 232 (Timber/Lumber)", c_timber))

            m_mhdv = check_db_match(df_232_mhdv, clean_input)
            if not m_mhdv.empty:
                r_mhdv = float(m_mhdv.iloc[0].get('Rate', 25.0))
                c_mhdv = "9903.74.02" if clean_input.startswith("8702") else ("9903.74.01" if clean_input.startswith(("8701", "8704", "8705", "8706", "8709")) else "9903.74.08")
                check_list.append((r_mhdv, "Sec 232 (MHDV/Buses)", c_mhdv))

            for idx, (res_r, res_lb, res_cd) in enumerate(check_list):
                if res_r > 0:
                    ans_sp = st.radio(f"Is this subject to {res_lb} ({res_r}%)?", ["No", "Yes"], index=0, horizontal=True, key=f"s232_sp_{idx}")
                    if ans_sp == "Yes":
                        s232_results.append({"label": res_lb, "rate": res_r, "code": res_cd, "is_subject": True})
                        st.warning(f"⚠️ **Sec 232:** {res_lb} logic applied ({res_r}%).")

            # 2. METAL ARTICLES (MASTER REBUILD)
            subdivs = get_hts_subdivisions(clean_input)
            if subdivs:
                st.markdown("<div class='questionnaire-header'>🏗️ Section 232 Metal Assessment</div>", unsafe_allow_html=True)
                
                is_article = any(s in ['i', 'iii', 'v'] for s in subdivs)
                is_derivative = any(s in ['ii', 'iv', 'vi', 'vii', 'viii', 'ix', 'x'] for s in subdivs)
                is_aluminum = any(s in ['i', 'ii', 'vi', 'ix'] for s in subdivs) or clean_input.startswith("76")
                is_steel = any(s in ['iii', 'iv', 'vii', 'x'] for s in subdivs) or clean_input.startswith(("72", "73"))
                is_copper = any(s in ['v', 'viii'] for s in subdivs) or clean_input.startswith("74")
                
                can_use_deminimis = not clean_input.startswith(("72", "73", "74", "76"))
                if iso_code == "RU" and is_aluminum: can_use_deminimis = False
                
                ans_wt = "Yes"
                if can_use_deminimis:
                    ans_wt = st.radio("Is aggregate steel/aluminum/copper weight at least 15%?", ["No", "Yes"], index=1, horizontal=True, key="s232_wt")
                
                if ans_wt == "No":
                    s232_results.append({"label": "Sec 232 De Minimis", "rate": 0.0, "code": "9903.82.03", "is_subject": True})
                    st.success("✅ **Sec 232:** Exempt (9903.82.03) - Metal < 15%.")
                else:
                    is_moto_hts = clean_input.startswith(("84", "85", "87"))
                    proceed_to_cores = True
                    if is_moto_hts and any(s in ['vi', 'vii', 'viii'] for s in subdivs):
                        ans_moto = st.radio("For US motorcycle manufacturing?", ["No", "Yes"], index=0, horizontal=True, key="s232_moto")
                        if ans_moto == "Yes":
                            s232_results.append({"label": "Sec 232 (Motorcycle)", "rate": 0.0, "code": "9903.82.13", "is_subject": True})
                            proceed_to_cores = False
                    
                    if proceed_to_cores:
                        rate_val, code_val = 0.0, ""
                        label = f"Sec 232 ({'Article' if is_article else 'Derivative'})"

                        if iso_code == "RU":
                            if is_aluminum:
                                code_val = "9903.85.68" if is_derivative else "9903.85.67"
                                rate_val = 200.0
                            else:
                                ru_opts = []
                                if any(s in ['iii', 'iv', 'v'] for s in subdivs): ru_opts.append("9903.82.14 - Articles (50%)")
                                if any(s in ['iv', 'vii', 'viii'] for s in subdivs): 
                                    ru_opts.append("9903.82.15 - Copper/Deriv Steel (10%)")
                                    ru_opts.append("9903.82.16 - Copper/Deriv Steel (25%)")
                                if 'x' in subdivs: ru_opts.append("9903.82.17 - Russian Deriv Steel (25%)")
                                
                                code_val, rate_val = "9903.82.14", 50.0
                                if ru_opts:
                                    ru_choice = st.selectbox("Select Russia Provision", ru_opts)
                                    code_val = ru_choice.split(" - ")[0]
                                    rate_val = float(ru_choice.split("(")[1].replace("%)", ""))
                        else:
                            metal_opts = ["None / Other Metal Origin", "95% US Metal"]
                            if iso_code == "GB": metal_opts.append("95% UK Metal")
                            metal_src = st.radio("Qualifying Metal Processing", metal_opts, index=0, horizontal=True)

                            if metal_src == "95% UK Metal":
                                if any(s in ['i', 'ii', 'iii', 'iv'] for s in subdivs): code_val, rate_val = "9903.82.04", 25.0
                                elif any(s in ['vi', 'vii'] for s in subdivs): code_val, rate_val = "9903.82.05", 15.0
                                else: code_val, rate_val = "9903.82.04", 25.0
                            elif metal_src == "95% US Metal":
                                if any(s in ['ix', 'x'] for s in subdivs):
                                    if parsed_rate < 10.0: code_val, rate_val = "9903.82.07", max(10.0 - parsed_rate, 0.0)
                                    else: code_val, rate_val = "9903.82.08", 0.0
                                else: code_val, rate_val = "9903.82.06", 10.0
                            else:
                                if is_article: code_val, rate_val = "9903.82.02", 50.0
                                elif any(s in ['ix', 'x'] for s in subdivs):
                                    if parsed_rate < 15.0: code_val, rate_val = "9903.82.10", max(15.0 - parsed_rate, 0.0)
                                    else: code_val, rate_val = "9903.82.11", 0.0
                                else: code_val, rate_val = "9903.82.09", 25.0

                        s232_results.append({"label": label, "rate": rate_val, "code": code_val, "is_subject": True})
                        st.warning(f"⚠️ **Sec 232:** Subject to {code_val} {rate_val:.2f}% Tariff!")
"""
    lines[start_idx:end_idx] = [new_logic + "\n"]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Successfully re-integrated 232 sub-checks.")
else:
    print(f"Markers not found. Start: {start_idx}, End: {end_idx}")
