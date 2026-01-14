import shutil
from pathlib import Path

def generate_project(project_name):
    src = Path(__file__).parent / "skeleton"
    dest = Path.cwd() / project_name
    shutil.copytree(src, dest)
    print(f"Project {project_name} created")
