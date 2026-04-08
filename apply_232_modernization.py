import os

file_path = r'c:\Users\jiafe\.gemini\antigravity\scratch\us-tariffs-simulator\app.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_marker = "# --- SECTION 232 ---"
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
    new_logic = """        # --- SECTION 232 METAL ARTICLES (MASTER REBUILD) ---
        s232_results = []
        if clean_input:
            subdivs = get_hts_subdivisions(clean_input)
            
            if subdivs:
                st.markdown("<div class='questionnaire-header'>🏗️ Section 232 Precision Assessment</div>", unsafe_allow_html=True)
                
                # Identify Class
                is_article = any(s in ['i', 'iii', 'v'] for s in subdivs)
                is_derivative = any(s in ['ii', 'iv', 'vi', 'vii', 'viii', 'ix', 'x'] for s in subdivs)
                
                # Determine metal type for Russian rules
                is_aluminum = any(s in ['i', 'ii', 'vi', 'ix'] for s in subdivs) or clean_input.startswith("76")
                is_steel = any(s in ['iii', 'iv', 'vii', 'x'] for s in subdivs) or clean_input.startswith(("72", "73"))
                is_copper = any(s in ['v', 'viii'] for s in subdivs) or clean_input.startswith("74")
                
                # 1. 15% WEIGHT RULE (De Minimis 9903.82.03)
                can_use_deminimis = not clean_input.startswith(("72", "73", "74", "76"))
                if iso_code == "RU" and is_aluminum: can_use_deminimis = False
                
                ans_wt = "Yes"
                if can_use_deminimis:
                    ans_wt = st.radio("Is the aggregate weight of ALL steel, aluminum, and copper at least 15% of the total article weight?", ["No", "Yes"], index=1, horizontal=True, key="s232_wt")
                
                if ans_wt == "No":
                    s232_results.append({"label": "Sec 232 De Minimis", "rate": 0.0, "code": "9903.82.03", "is_subject": True})
                    st.success("✅ **Sec 232:** Exempted (9903.82.03) because metal content < 15%.")
                else:
                    # 2. MOTORCYCLE EXEMPTION (9903.82.13)
                    is_moto_hts = clean_input.startswith(("84", "85", "87"))
                    proceed_to_cores = True
                    if is_moto_hts and any(s in ['vi', 'vii', 'viii'] for s in subdivs):
                        ans_moto = st.radio("Is this for US motorcycle manufacturing?", ["No", "Yes"], index=0, horizontal=True, key="s232_moto")
                        if ans_moto == "Yes":
                            s232_results.append({"label": "Sec 232 (Motorcycle)", "rate": 0.0, "code": "9903.82.13", "is_subject": True})
                            st.success("✅ **Sec 232:** Exempted (9903.82.13) for US motorcycle manufacturing.")
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
    print("Successfully replaced Section 232 block.")
else:
    print(f"Markers not found. Start: {start_idx}, End: {end_idx}")
