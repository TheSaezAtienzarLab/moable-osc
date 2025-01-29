#SBATCH --account=PAS2598
#SBATCH --time=2:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=drug_retrieve_process
#SBATCH --output=drugretrieve%j.log
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=duarte63@osu.edu

# Load latest miniconda version
module load miniconda3/24.1.2-py310

# Define conda environment path explicitly
export CONDA_ENV_PATH="/users/PAS2598/duarte63/.conda/envs/drug_pred"
export PATH="$CONDA_ENV_PATH/bin:$PATH"
export PYTHONPATH="$CONDA_ENV_PATH/lib/python3.10/site-packages:$PYTHONPATH"

# Activate conda environment
source activate drug_pred

# Run the script
python convert_sdf.py
