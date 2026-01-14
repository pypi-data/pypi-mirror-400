Write-Host "Creating virtual environment..."
python -m venv pythonLib

Write-Host "Activating virtual environment..."
.\pythonLib\Scripts\Activate.ps1

Write-Host "Installing requirements..."
python -m pip install --upgrade pip
pip install -r requirement.txt

Write-Host "Setup completed successfully!"
