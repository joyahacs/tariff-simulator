import pandas as pd

print("Creating sec122_exemptions.csv...")

# Create a direct database of the most common exemptions
data = {
    "HTSUS": [
        "2901.10.40", # The one from your screenshot!
        "2804.29.00",
        "0811.90.80", 
        "3917.23.00", 
        "4403.91.00"
    ],
    "Description": [
        "Saturated acyclic hydrocarbon derived from petroleum", 
        "Rare gases, other than argon", 
        "Tropical fruit, nesoi", 
        "Tubes, rigid, vinyl chloride", 
        "Oak wood in the rough"
    ],
    "Scope Limitations": [
        "Pharma", 
        "Pharma", 
        "Ex", 
        "Aircraft", 
        ""
    ]
}

df = pd.DataFrame(data)
df.to_csv(r"D:\tariff_project\sec122_exemptions.csv", index=False)

print("✅ SUCCESS! The file sec122_exemptions.csv has been created in your folder.")