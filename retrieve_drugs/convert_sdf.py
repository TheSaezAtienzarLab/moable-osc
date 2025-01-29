from rdkit import Chem
import pandas as pd

def sdf_to_csv(sdf_text):
    """
    Convert SDF format text to a pandas DataFrame and save as CSV
    
    Args:
        sdf_text (str): Content of the SDF file
        
    Returns:
        pd.DataFrame: DataFrame containing the extracted information
    """
    # Split the SDF into individual molecule blocks
    mol_blocks = sdf_text.split("$$$$\n")
    
    # Initialize lists to store data
    data = []
    
    for block in mol_blocks:
        if not block.strip():
            continue
            
        # Create RDKit molecule object
        mol = Chem.MolFromMolBlock(block.split(">")[0])
        
        if mol is None:
            continue
            
        # Extract properties from the SDF
        props = {}
        
        # Get all the data fields
        lines = block.split("\n")
        current_field = None
        field_content = []
        
        for line in lines:
            if line.startswith("> <"):
                if current_field and field_content:
                    props[current_field] = "\n".join(field_content)
                    field_content = []
                current_field = line[3:-1]  # Remove "> <" and ">"
            elif current_field and line.strip():
                field_content.append(line.strip())
        
        # Add the last field
        if current_field and field_content:
            props[current_field] = "\n".join(field_content)
        
        # Add SMILES
        if mol is not None:
            props['SMILES'] = Chem.MolToSmiles(mol)
            
        data.append(props)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    return df

# Process the input text and convert to CSV
def process_sdf(sdf_text, output_file="output.csv"):
    """
    Process SDF text and save to CSV file
    
    Args:
        sdf_text (str): Content of the SDF file
        output_file (str): Name of the output CSV file
    """
    df = sdf_to_csv(sdf_text)
    df.to_csv(output_file, index=False)
    print(f"Converted {len(df)} molecules to {output_file}")
    return df

# Example usage:
with open('/users/PAS2598/duarte63/GitHub/moable-osc/data/structures.sdf', 'r') as f:
     sdf_text = f.read()
 df = process_sdf(sdf_text, '/users/PAS2598/duarte63/GitHub/moable-osc/data/drugs.csv')