import json
import os
import pandas as pd
from pathlib import Path

def parse_claims_from_fhir(raw_dir):
    all_claims = []
    
    # Path to your JSON files
    json_files = list(Path(raw_dir).glob("*.json"))
    print(f"Scanning {len(json_files)} FHIR bundles for financial data...")

    for file_path in json_files:
        with open(file_path, 'r') as f:
            bundle = json.load(f)
            
            for entry in bundle.get('entry', []):
                res = entry.get('resource', {})
                
                # We are specifically looking for EOB resources
                if res.get('resourceType') == 'ExplanationOfBenefit':
                    claim_data = {
                        'claim_id': res.get('id'),
                        'patient_id': res.get('patient', {}).get('reference', '').replace('Patient/', ''),
                        'encounter_id': res.get('item', [{}])[0].get('encounter', [{}])[0].get('reference', '').replace('Encounter/', ''),
                        'total_cost': float(res.get('total', [{}])[0].get('amount', {}).get('value', 0)),
                        'payment_amount': float(res.get('payment', {}).get('amount', {}).get('value', 0)),
                        'status': res.get('status'),
                        'created': res.get('created')
                    }
                    all_claims.append(claim_data)

    df = pd.DataFrame(all_claims)
    return df

# Main execution
raw_fhir_path = "data/raw/fhir" # Adjust this to your actual path!
output_path = "data/processed/fhir_parsed/claims_fhir.parquet"

df_claims = parse_claims_from_fhir(raw_fhir_path)
df_claims.to_parquet(output_path, index=False)
print(f"✅ Successfully extracted {len(df_claims):,} claims to Parquet!")