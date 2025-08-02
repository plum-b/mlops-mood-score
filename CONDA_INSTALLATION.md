# Conda Installation and Environment Setup Guide

## Installing Miniconda on Ubuntu/WSL2

### Step 1: Download Miniconda
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
```

### Step 2: Install Miniconda
```bash
bash miniconda.sh -b -p $HOME/miniconda3
```

### Step 3: Initialize Conda
```bash
$HOME/miniconda3/bin/conda init bash
```

### Step 4: Restart Terminal or Source Conda
After installation, either:
- **Restart your terminal/shell**, or
- **Source conda in current session**:
```bash
source $HOME/miniconda3/etc/profile.d/conda.sh
```

### Step 5: Verify Installation
```bash
conda --version
```

## Creating Environment for This Project

### Create Conda Environment
```bash
conda create -n wine-score python=3.10 -y
```

### Activate Environment
```bash
conda activate wine-score
```

### Install Requirements
```bash
pip install -r requirements.txt
```

### Install Jupyter Kernel (Optional)
To make the environment available as a kernel in Jupyter notebooks:
```bash
python -m ipykernel install --user --name=mood-score --display-name "Python (mood-score)"
```

## Alternative: Using Python venv (if conda not available)

If conda is not available, you can use Python's built-in virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

## Project Requirements

The project requires the following packages (from `requirements.txt`):
- pandas
- mlflow
- notebook
- numpy
- scikit-learn
- matplotlib
- python-box
- pyYAML
- tqdm
- ensure
- joblib
- types-PyYAML
- Flask
- Flask-Cors

## Environment Management Commands

### Conda Commands
```bash
# List environments
conda env list

# Activate environment
conda activate wine-score

# Deactivate environment
conda deactivate

# Remove environment
conda env remove -n wine-score

# Export environment
conda env export > environment.yml

# Create from environment file
conda env create -f environment.yml
```

### Python venv Commands
```bash
# Activate environment
source venv/bin/activate

# Deactivate environment
deactivate

# Remove environment
rm -rf venv
```

## Troubleshooting

### Conda Command Not Found
If you get "conda: command not found" after installation:
1. Restart your terminal
2. Or source conda manually: `source $HOME/miniconda3/etc/profile.d/conda.sh`

### Permission Issues
If you encounter permission issues during installation, ensure you have write permissions to your home directory.

### WSL2 Specific Notes
- Conda works well in WSL2
- Make sure you're using a recent version of WSL2
- If you have issues, consider using Python venv as an alternative 