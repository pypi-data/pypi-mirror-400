import subprocess
import sys
import os
from packaging.requirements import Requirement
from importlib.metadata import distributions

REQUIREMENTS_FILE = "requirements.txt"


def read_requirements():
    """Read requirements.txt and return a clean list of packages."""
    if not os.path.exists(REQUIREMENTS_FILE):
        print("⚠️ requirements.txt not found. Creating new one...")
        update_requirements()

    # Try utf-8-sig first, fallback to utf-16
    try:
        with open(REQUIREMENTS_FILE, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
    except UnicodeError:
        with open(REQUIREMENTS_FILE, "r", encoding="utf-16") as f:
            lines = f.readlines()

    packages = []
    for line in lines:
        clean_line = line.strip().replace("\x00", "")
        if clean_line and not clean_line.startswith("#"):
            packages.append(clean_line)
    return packages


def normalize_package_name(name: str) -> str:
    """Normalize package name according to PEP 503."""
    return name.lower().replace("_", "-").replace(".", "-")


def get_installed_packages() -> set:
    """Return a set of normalized installed package names."""
    return {normalize_package_name(dist.metadata["Name"]) for dist in distributions()}


def install_missing_packages():
    """Install only missing packages based on requirements.txt."""
    required_packages = read_requirements()
    installed = get_installed_packages()
    missing = []

    for req_line in required_packages:
        try:
            req = Requirement(req_line)
            pkg_name = normalize_package_name(req.name)
        except Exception:
            pkg_name = normalize_package_name(
                req_line.split("==")[0].split(">=")[0].split("<=")[0]
            )

        if pkg_name not in installed:
            missing.append(req_line)

    if missing:
        print(f"📦 Installing missing packages: {', '.join(missing)}")
        subprocess.run([sys.executable, "-m", "pip", "install", *missing], check=True)
        print("[OK] Missing packages installed successfully!")
    else:
        print("[OK] All required packages are already installed.")


def update_requirements():
    """Regenerate requirements.txt from current environment."""
    print("📄 Updating requirements.txt from current environment...")
    with open(REQUIREMENTS_FILE, "w", encoding="utf-8") as f:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        )
        f.write(result.stdout)
    print("[OK] requirements.txt updated successfully!")


def pip_install(package_name: str):
    """Install a single package & update requirements.txt."""
    subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=True)
    update_requirements()


def pip_uninstall(package_name: str):
    """Uninstall a single package & update requirements.txt."""
    subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "-y", package_name], check=True
    )
    update_requirements()


# -------------------- Command-line Interface -------------------- #
if __name__ == "__main__":
    if len(sys.argv) >= 3:
        command = sys.argv[1].lower()
        package = sys.argv[2]
        if command == "install":
            pip_install(package)
        elif command == "uninstall":
            pip_uninstall(package)
        else:
            print("❌ Invalid command! Use 'install' or 'uninstall'.")
        sys.exit(0)
    else:
        print(
            "ℹ️ Usage: python auto_requirements.py install <package> | uninstall <package>"
        )
        install_missing_packages()
