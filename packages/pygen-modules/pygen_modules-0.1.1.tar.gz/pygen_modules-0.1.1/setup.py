from setuptools import setup, find_packages

setup(
    name="pygen_modules",
    version="0.1.1",
    packages=find_packages(),
    entry_points={"console_scripts": ["pygen=pygen_modules.cli:main"]},
    include_package_data=True,

    # Author details
    author="Manikandan",
    author_email="manianuram2312@gmail.com",
    description="Project skeleton generator CLI tool",
    long_description_content_type="text/markdown",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
