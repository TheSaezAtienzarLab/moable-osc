import requests
import pandas as pd
from pathlib import Path
import pickle
import time
from typing import Dict, List, Optional

class DrugsFDARetriever:
    def __init__(self):
        self.base_url = "https://api.fda.gov/drug/drugsfda.json"
        self.api_key = None  # Optional: Add your API key here for higher rate limits
        self.output_dir = Path("data")

    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        try:
            if self.api_key:
                params = params or {}
                params['api_key'] = self.api_key

            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Response content: {e.response.text[:500]}")
            return None

    def get_all_approved_drugs(self, limit: int = 100) -> List[Dict]:
        """Retrieve approved drugs from DRUGS@FDA"""
        print(f"Retrieving approved drugs (limit: {limit})...")
        
        # Search for prescription drugs that are currently approved
        params = {
            'search': 'products.marketing_status:"Prescription" AND products.route:"ORAL"',
            'limit': limit
        }
        
        response_data = self._make_request(self.base_url, params)
        if not response_data or 'results' not in response_data:
            print("Failed to retrieve drug data")
            return []

        return response_data['results']

    def process_drug_data(self, raw_data: List[Dict]) -> pd.DataFrame:
        """Process raw drug data into a structured format"""
        processed_data = []
        
        for record in raw_data:
            # Get basic application info
            application_info = {
                'application_number': record.get('application_number', ''),
                'sponsor_name': record.get('sponsor_name', ''),
                'submission_type': ''
            }
            
            # Get submission information
            if 'submissions' in record and record['submissions']:
                latest_submission = record['submissions'][0]  # Most recent submission
                application_info['submission_type'] = latest_submission.get('submission_type', '')
                
            # Process products
            if 'products' in record:
                for product in record['products']:
                    product_info = application_info.copy()
                    product_info.update({
                        'product_number': product.get('product_number', ''),
                        'brand_name': '',  # Will be filled from openfda if available
                        'generic_name': '', # Will be filled from openfda if available
                        'dosage_form': product.get('dosage_form', ''),
                        'route': '; '.join(product.get('route', [])),
                        'marketing_status': product.get('marketing_status', ''),
                        'active_ingredients': []
                    })
                    
                    # Get active ingredients
                    if 'active_ingredients' in product:
                        ingredients = []
                        for ingredient in product['active_ingredients']:
                            ingredients.append(f"{ingredient.get('name', '')} {ingredient.get('strength', '')}")
                        product_info['active_ingredients'] = '; '.join(ingredients)
                    
                    # Get additional info from openfda section if available
                    if 'openfda' in record:
                        openfda = record['openfda']
                        product_info['brand_name'] = '; '.join(openfda.get('brand_name', []))
                        product_info['generic_name'] = '; '.join(openfda.get('generic_name', []))
                    
                    processed_data.append(product_info)
        
        return pd.DataFrame(processed_data)

    def save_data(self, df: pd.DataFrame):
        """Save processed data to files"""
        if df.empty:
            print("No data to save")
            return

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save complete dataset as CSV
        csv_path = self.output_dir / "fda_approved_drugs.csv"
        df.to_csv(csv_path, index=False)
        print(f"Saved complete drug data to {csv_path}")
        
        # Create and save dictionary for MoAble
        # Using generic_name as key and active_ingredients as value
        drug_dict = dict(zip(
            df['generic_name'].dropna(),
            df['active_ingredients'].dropna()
        ))
        
        # Remove empty entries
        drug_dict = {k: v for k, v in drug_dict.items() if k and v}
        
        # Save as pickle
        pickle_path = self.output_dir / "input"
        pickle_path.mkdir(parents=True, exist_ok=True)
        pickle_file = pickle_path / "example_input_smiles.pkl"
        
        with open(pickle_file, 'wb') as f:
            pickle.dump(drug_dict, f)
        print(f"Saved drug dictionary to {pickle_file}")
        
        # Print summary statistics
        print("\nDataset Summary:")
        print(f"Total number of drug products: {len(df)}")
        print(f"Unique generic names: {df['generic_name'].nunique()}")
        print(f"Unique dosage forms: {df['dosage_form'].nunique()}")
        print("\nMost common routes of administration:")
        print(df['route'].value_counts().head())

def main():
    try:
        retriever = DrugsFDARetriever()
        
        # Get drug data
        raw_data = retriever.get_all_approved_drugs(limit=100)  # Adjust limit as needed
        
        if raw_data:
            # Process the data
            df = retriever.process_drug_data(raw_data)
            
            # Save the results
            retriever.save_data(df)
        else:
            print("No data retrieved from DRUGS@FDA")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()