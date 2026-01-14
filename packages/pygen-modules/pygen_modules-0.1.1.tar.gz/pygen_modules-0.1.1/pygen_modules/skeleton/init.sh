echo "🔹 Creating virtual environment..."
py -m venv pythonLib

echo "🔹 Activating virtual environment..."
source pythonLib/Scripts/activate

echo "🔹 Installing requirements..."
python -m pip install --upgrade pip
pip install -r requirement.txt

echo "✅ Setup completed successfully!"
