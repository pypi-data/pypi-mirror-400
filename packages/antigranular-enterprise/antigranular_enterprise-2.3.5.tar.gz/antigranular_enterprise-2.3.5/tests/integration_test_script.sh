#!/bin/bash

# Create a virtual environment
python3.8 -m venv myenv

# Activate the virtual environment
. myenv/bin/activate

pip3 install matplotlib numpy seaborn pandas nbformat nbconvert nbclient

# Clone the repo
git clone -b dev_config https://github.com/ObliviousAI/AntigranularClient.git

# Change directory to the cloned repo
cd AntigranularClient

# Install Poetry
pip3 install poetry

# Install dependencies in the current environment
poetry install

# Install ipykernel and register the venv as a kernel
pip3 install ipykernel
python3 -m ipykernel install --user --name=myenv_kernel

cd tests/
# Execute the Python script (this script should now be able to find and use the kernel named 'myenv_kernel' when executing notebooks)
python3 full_integration_test.py
cd ..
# Cleanup: Unregister the kernel and delete the venv and cloned repo
jupyter kernelspec uninstall myenv_kernel -f

# Deactivate and remove the virtual environment
deactivate
cd ..
rm -rf myenv AntigranularClient
